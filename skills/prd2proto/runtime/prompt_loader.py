"""Prompt Loader for prd2proto pipeline.

负责加载prompts-v2目录下的prompt文件，并支持以下能力：
1. 按stage_id定位对应prompt文件
2. 注入上游artifacts作为context
3. 注入PRD/scope_md等输入
4. 渲染最终发给LLM的完整prompt

设计原则：
- 单一职责：只做prompt加载与渲染
- 与LLM调用解耦：返回完整prompt字符串，由llm_client负责调用
- 与executor解耦：executor只调用load_and_render()
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


class PromptLoader:
    """加载并渲染prompts-v2/*.md，注入上游artifacts。"""

    def __init__(self, prompts_dir: Path | str):
        """
        Args:
            prompts_dir: prompts-v2目录路径
        """
        self.prompts_dir = Path(prompts_dir)
        if not self.prompts_dir.exists():
            raise FileNotFoundError(f"prompts目录不存在: {self.prompts_dir}")

    def load_prompt(self, prompt_file: str) -> str:
        """加载单个prompt文件原始内容。

        Args:
            prompt_file: prompt文件名（如 "02-design-objectives.md"）
                         或相对prompts_dir的路径
                         或绝对路径

        Returns:
            prompt原始Markdown内容
        """
        # 支持绝对路径
        path = Path(prompt_file)
        if not path.is_absolute():
            # 支持pipeline.yaml中的"prompts-v2/02-..."格式
            if prompt_file.startswith("prompts-v2/"):
                # pipeline.yaml里是相对skill根目录的，需要去掉前缀
                file_name = prompt_file.replace("prompts-v2/", "")
                path = self.prompts_dir / file_name
            elif "/" not in prompt_file:
                # 仅文件名，直接拼接
                path = self.prompts_dir / prompt_file
            else:
                # 其他相对路径，相对当前工作目录
                path = Path(prompt_file)

        if not path.exists():
            raise FileNotFoundError(f"prompt文件不存在: {path}")

        return path.read_text(encoding="utf-8")

    # 上游注入时剥离的元数据信封字段（下游不需要，省 token）
    _COMPACT_STRIP_KEYS = {
        'artifact_id', 'skill_id', 'run_id', 'created_at', 'maturity',
        'source_inputs', 'inferred_fields', 'warnings', 'validation_status',
        'traceability', '_runtime_injected', '_runtime_normalized',
        '_retry_applied', 'assumptions',
    }

    # 业务对象内的"解释性"字段（下游消费需结论，不需理由 → 省 token）
    _COMPACT_STRIP_NESTED = {
        'rationale', 'gsm_signal', 'gsm_why', 'why_this_number',
        'context_from_prd', 'evidence', 'priority_rationale', 'reason',
        'measurement_method', 'ia_rationale', 'navigation_rationale',
        'interaction_density_rationale', 'data_density_rationale',
        'custom_rationale', 'pattern_rationale',
    }

    @classmethod
    def _strip_nested(cls, obj: Any) -> Any:
        """递归剥离业务对象内的解释性字段（保留结论性字段）。"""
        if isinstance(obj, dict):
            return {
                k: cls._strip_nested(v)
                for k, v in obj.items()
                if k not in cls._COMPACT_STRIP_NESTED
            }
        if isinstance(obj, list):
            return [cls._strip_nested(x) for x in obj]
        return obj

    @classmethod
    def _compact_upstream(cls, asset: Any) -> Any:
        """注入上游 artifact 前剥离元数据信封 + 解释性字段，只留业务结论（省 token）。

        - 移除 runtime 元数据（artifact_id/run_id/...）
        - 移除解释性字段（rationale/gsm_*/evidence/... → 下游需结论非理由）
        - gaps 简化为 description 列表
        - 保留结论性业务字段（goal_id/description/target/serves_*/priority/...）
        """
        if not isinstance(asset, dict):
            return asset
        compact = {}
        for k, v in asset.items():
            if k in cls._COMPACT_STRIP_KEYS:
                continue
            if k == 'gaps' and isinstance(v, list):
                compact[k] = [
                    (g.get('description') or g.get('gap') or str(g))
                    if isinstance(g, dict) else str(g)
                    for g in v
                ][:5]
                continue
            compact[k] = cls._strip_nested(v)
        return compact

    def render_stage_prompt(
        self,
        prompt_file: str,
        upstream_artifacts: dict[str, Any] | None = None,
        runtime_inputs: dict[str, Any] | None = None,
    ) -> str:
        """加载prompt并注入上游artifacts和runtime输入，输出完整prompt。

        最终发给LLM的prompt结构：
        ```
        {prompt原始内容}

        ---

        # 实际输入：上游推理资产

        ## design_objectives
        ```json
        {...}
        ```

        ## user_task_map
        ...

        ---

        # 运行时输入

        ## prd_content
        {PRD原文}

        ---

        # 你的任务

        严格按照上述prompt的Senior Designer Reasoning Model生成输出。
        只输出一个JSON对象，不要其他文字。
        ```

        Args:
            prompt_file: prompt文件路径
            upstream_artifacts: 上游stages生成的artifacts {asset_name: dict}
            runtime_inputs: 运行时输入 {input_name: value}

        Returns:
            完整渲染后的prompt字符串
        """
        prompt_text = self.load_prompt(prompt_file)

        sections = [prompt_text, "\n---\n"]

        # 注入上游artifacts
        if upstream_artifacts:
            sections.append("# 实际输入：上游推理资产\n")
            for asset_name, asset_data in upstream_artifacts.items():
                sections.append(f"\n## {asset_name}\n")
                sections.append("```json\n")
                sections.append(
                    json.dumps(
                        self._compact_upstream(asset_data),
                        ensure_ascii=False, indent=2,
                    )
                )
                sections.append("\n```\n")
            sections.append("\n---\n")

        # 注入运行时输入
        if runtime_inputs:
            sections.append("# 运行时输入\n")
            for input_name, input_value in runtime_inputs.items():
                sections.append(f"\n## {input_name}\n")
                if isinstance(input_value, str):
                    if len(input_value) > 100 and "\n" in input_value:
                        # 长文本（如PRD全文）用代码块
                        sections.append(f"```\n{input_value}\n```\n")
                    else:
                        sections.append(f"{input_value}\n")
                elif isinstance(input_value, (dict, list)):
                    sections.append("```json\n")
                    sections.append(
                        json.dumps(input_value, ensure_ascii=False, indent=2)
                    )
                    sections.append("\n```\n")
                else:
                    sections.append(f"{input_value}\n")
            sections.append("\n---\n")

        # 任务说明
        sections.append("""# 你的任务

严格按照上述 prompt 的 Senior Designer Reasoning Model 和 Output Schema，
基于实际输入生成输出。

**输出要求**：
- 只输出一个 JSON 对象（artifact 的内容字段 + 推理元数据）
- 不要输出任何解释性文字
- 不要 markdown 代码块标记以外的内容
- 不要生成 runtime 注入字段（artifact_id / skill_id / run_id / created_at / validation_status.schema_valid）

**质量要求**：
- 严格遵守 prompt 中的 Quality Self-Check 清单
- 每个推断必须 inferred:true + 列入 inferred_fields
- confidence 必须与输入质量匹配
""")

        return "".join(sections)

    def get_stage_prompt_path(self, stage_config: dict) -> str:
        """从pipeline stage配置中提取prompt路径。

        Args:
            stage_config: pipeline.yaml中的stage配置dict

        Returns:
            prompt文件路径
        """
        if "prompt" not in stage_config:
            raise ValueError(
                f"stage {stage_config.get('id')} 配置缺少 prompt 字段"
            )
        return stage_config["prompt"]


def main():
    """CLI测试入口"""
    import argparse

    parser = argparse.ArgumentParser(description="测试 PromptLoader")
    parser.add_argument(
        "--prompts-dir",
        default="skills/prd2proto/prompts-v2",
        help="prompts目录路径",
    )
    parser.add_argument(
        "--prompt-file",
        default="02-design-objectives.md",
        help="prompt文件名",
    )
    args = parser.parse_args()

    loader = PromptLoader(args.prompts_dir)

    print(f"=== 加载 {args.prompt_file} ===")
    raw = loader.load_prompt(args.prompt_file)
    print(f"原始内容长度: {len(raw)} 字符")
    print(f"前 200 字: {raw[:200]}...")

    print("\n=== 渲染完整prompt（含上游artifacts） ===")
    rendered = loader.render_stage_prompt(
        args.prompt_file,
        upstream_artifacts={
            "requirement_inventory": {"sample": "test"},
        },
        runtime_inputs={
            "prd_content": "# 测试PRD\n\n这是测试内容。",
        },
    )
    print(f"渲染后总长度: {len(rendered)} 字符")
    print(f"末尾 500 字: ...{rendered[-500:]}")


if __name__ == "__main__":
    main()
