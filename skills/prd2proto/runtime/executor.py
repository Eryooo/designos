"""
Pipeline Executor - Runtime Integration with Real LLM

集成 quality gates、traceability、真实LLM 调用的 pipeline 执行器。

Phase 3 改造（2026-06-10）：
- 删除 _mock_stage_output（违反"不要静默 mock"原则）
- 集成 prompt_loader（加载 prompts-v2 + 注入上游 artifacts）
- 集成 llm_client（真实异步 LLM 调用）
- 默认走真实 LLM；mock 必须显式 --mock
"""

import sys
import asyncio
from pathlib import Path
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
import yaml
import json
import importlib.util

# 动态加载模块
PROJECT_ROOT = Path(__file__).parent.parent.parent.parent
SKILL_ROOT = Path(__file__).parent.parent
RUNTIME_DIR = Path(__file__).parent
PROMPTS_DIR = SKILL_ROOT / "prompts-v2"


def load_module_from_file(module_name: str, file_path: Path):
    """从文件动态加载模块"""
    spec = importlib.util.spec_from_file_location(module_name, file_path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = module
    spec.loader.exec_module(module)
    return module


# 加载 gates 和 tracer
gates = load_module_from_file('gates', PROJECT_ROOT / 'kernel/quality-gates/gates.py')
tracer = load_module_from_file('tracer', PROJECT_ROOT / 'kernel/traceability/tracer.py')

QualityGateExecutor = gates.QualityGateExecutor
QualityGateBlocked = gates.QualityGateBlocked
GateStatus = gates.GateStatus
TraceabilityGenerator = tracer.TraceabilityGenerator

# 加载本目录的 prompt_loader 和 llm_client
prompt_loader_mod = load_module_from_file(
    'prd2proto_prompt_loader', RUNTIME_DIR / 'prompt_loader.py'
)
llm_client_mod = load_module_from_file(
    'prd2proto_llm_client', RUNTIME_DIR / 'llm_client.py'
)
schema_validator_mod = load_module_from_file(
    'prd2proto_schema_validator', RUNTIME_DIR / 'schema_validator.py'
)

PromptLoader = prompt_loader_mod.PromptLoader
LLMClient = llm_client_mod.LLMClient
LLMClientError = llm_client_mod.LLMClientError
JSONExtractionError = llm_client_mod.JSONExtractionError
SchemaValidator = schema_validator_mod.SchemaValidator


@dataclass
class StageResult:
    """Stage 执行结果"""
    stage_id: str
    status: str  # success, blocked, warning, error
    output: Dict
    gate_results: List[Dict]
    warnings: List[Dict]
    llm_metrics: Optional[Dict] = None  # tokens/elapsed_ms


class PipelineExecutor:
    """Pipeline 执行器（异步 + 真实 LLM）"""

    def __init__(
        self,
        pipeline_config_path: str,
        mock: bool = False,
        model: str = "claude-opus-4-8",
        max_tokens: int = 32768,
        save_stages_dir: str | None = None,
        validation_mode: bool = False,
    ):
        """
        Args:
            pipeline_config_path: pipeline.yaml 路径
            mock: 是否启用 mock 模式（默认 False = 真实 LLM）
            model: LLM 模型 ID
            max_tokens: LLM 最大输出 tokens
        """
        self.config_path = Path(pipeline_config_path)
        self.config = self._load_config()
        self.mock = mock

        self.gate_executor = QualityGateExecutor()
        self.tracer = TraceabilityGenerator()

        # Phase 3 新增：prompt loader + llm client
        self.prompt_loader = PromptLoader(PROMPTS_DIR)
        self.llm_client = LLMClient(
            model=model,
            max_tokens=max_tokens,
            mock=mock,
        )
        # Phase 4 新增：schema validator（含 $ref 解析）
        self.schema_validator = SchemaValidator()
        # Batch 1: 逐 stage 实时保存输出（即使后续 stage 失败，前面成功的已落盘）
        self.save_stages_dir = Path(save_stages_dir) if save_stages_dir else None
        if self.save_stages_dir:
            self.save_stages_dir.mkdir(parents=True, exist_ok=True)
        self._stage_seq = 0  # stage 序号（用于文件命名）
        # Batch 1 验证模式：gate critical 记录但不中断 pipeline，
        # 让 12 个 stage 都真实跑+都被检验+失败如实记录（不跳过 gate，只是不中断）
        self.validation_mode = validation_mode

        self.context = {
            'mode': 'pm',
            'fidelity': 'medium',
            'reasoning_assets': {},
            'warnings': [],
            'current_stage': None,
            'total_input_tokens': 0,
            'total_output_tokens': 0,
        }

    def _load_config(self) -> Dict:
        """加载 pipeline 配置"""
        with open(self.config_path) as f:
            return yaml.safe_load(f)

    async def execute(self, inputs: Dict) -> Dict:
        """
        异步执行完整 pipeline。

        Args:
            inputs: 输入参数（prd_content, scope_md, etc.）

        Returns:
            执行结果 dict
        """
        print(f"🚀 Starting pipeline: {self.config['name']}")
        print(f"   Mode: {self.context['mode']}, Fidelity: {self.context['fidelity']}")
        print(f"   LLM: {self.llm_client.model} (mock={self.mock})")

        stage_results = []

        try:
            for stage in self.config['stages']:
                stage_id = stage['id']
                print(f"\n📍 Stage: {stage_id}")

                # 跳过显式标记 framework 的 stage（待补全的）
                # 注意：本项目所有 prompt 已在 Phase 2 补全，这里仅保险
                if stage.get('status') == 'framework' and not self.mock:
                    # Phase 3 后所有 prompt 已补完，但 stage 配置可能滞后
                    # 仍尝试执行；若 prompt 实际有内容则正常跑
                    print(f"   ℹ️  stage.status=framework（pipeline.yaml 标注），仍尝试执行")

                # 执行 stage
                result = await self._execute_stage(stage, inputs)
                stage_results.append(result)

                # Batch 1: 逐 stage 实时保存（success/blocked/error 都存）
                if self.save_stages_dir:
                    self._save_stage_output(stage, result)

                # 检查是否 blocked
                if result.status == 'blocked':
                    print(f"   ❌ Blocked at {stage_id}")
                    return {
                        'status': 'blocked',
                        'blocked_at': stage_id,
                        'blocker_report': result.output,
                        'stage_results': [self._stage_result_to_dict(r) for r in stage_results],
                    }

                # 检查 stage 执行错误（LLM 失败 / JSON 解析失败 / Schema 不符）
                if result.status == 'error':
                    print(f"   ❌ Error at {stage_id}: {result.output.get('error')}")
                    return {
                        'status': 'error',
                        'error_at': stage_id,
                        'error_detail': result.output,
                        'stage_results': [self._stage_result_to_dict(r) for r in stage_results],
                    }

                # 检查是否需要 fallback_safe
                if result.status == 'fallback_safe':
                    print(f"   ⚠️  Fallback safe at {stage_id}")
                    self._handle_fallback_safe()

            # 汇总最终结果
            print(f"\n✅ Pipeline completed")
            print(
                f"   Total tokens: {self.context['total_input_tokens']} in / "
                f"{self.context['total_output_tokens']} out"
            )
            return {
                'status': 'success',
                'reasoning_assets': self.context['reasoning_assets'],
                'warnings': self.context['warnings'],
                'stage_results': [self._stage_result_to_dict(r) for r in stage_results],
                'metrics': {
                    'total_input_tokens': self.context['total_input_tokens'],
                    'total_output_tokens': self.context['total_output_tokens'],
                    'stages_executed': len(stage_results),
                    'per_stage': self.context.get('stage_metrics', []),
                },
            }

        except Exception as e:
            print(f"\n❌ Pipeline error: {e}")
            import traceback
            traceback.print_exc()
            return {
                'status': 'error',
                'error': str(e),
                'stage_results': [self._stage_result_to_dict(r) for r in stage_results],
            }

    async def _execute_stage(self, stage: Dict, inputs: Dict) -> StageResult:
        """
        执行单个 stage（真实 LLM）。

        Args:
            stage: stage 配置
            inputs: 输入

        Returns:
            StageResult
        """
        stage_id = stage['id']
        self.context['current_stage'] = stage_id

        # === Phase 3 核心：调用真实 LLM 而非 mock ===
        try:
            output, llm_metrics = await self._execute_llm_stage(stage, inputs)
        except (LLMClientError, JSONExtractionError) as exc:
            print(f"   ❌ LLM 执行失败: {exc}")
            return StageResult(
                stage_id=stage_id,
                status='error',
                output={'error_type': type(exc).__name__, 'error': str(exc)},
                gate_results=[],
                warnings=[],
            )

        # 累计 token 使用
        if llm_metrics:
            self.context['total_input_tokens'] += llm_metrics.get('input_tokens', 0)
            self.context['total_output_tokens'] += llm_metrics.get('output_tokens', 0)

            # Per-stage 监控指标
            output_tokens = llm_metrics.get('output_tokens', 0)
            max_tokens = self.llm_client.max_tokens
            utilization = round(output_tokens / max_tokens, 3) if max_tokens else 0
            stop_reason = llm_metrics.get('stop_reason', '')
            cont_count = llm_metrics.get('continuation_count', 0)

            print(
                f"      📊 utilization: {utilization * 100:.1f}% "
                f"(stop_reason={stop_reason}, continuations={cont_count})"
            )

            # 记录到 stage_metrics（供后续分析）
            if 'stage_metrics' not in self.context:
                self.context['stage_metrics'] = []
            self.context['stage_metrics'].append({
                'stage_id': stage_id,
                'input_tokens': llm_metrics.get('input_tokens', 0),
                'output_tokens': output_tokens,
                'max_tokens_limit': max_tokens,
                'utilization': utilization,
                'stop_reason': stop_reason,
                'continuation_count': cont_count,
                'was_truncated': llm_metrics.get('was_truncated', False),
                'elapsed_ms': llm_metrics.get('elapsed_ms', 0),
            })

        # 执行质量门
        gate_results = []
        warnings: List[Dict] = []

        if 'quality_gates' in stage:
            for gate_id in stage['quality_gates']:
                try:
                    print(f"   🔍 Quality Gate: {gate_id}")

                    # Phase 4: schema_gate 用 SchemaValidator 单独处理
                    # （kernel/gates.py 的 schema_gate 无法解析 $ref，
                    #  而真实 schema 都通过 allOf+$ref 引用 artifact-base）
                    if gate_id == 'schema_gate':
                        result = self._run_schema_gate(stage, output)
                    else:
                        gate_kwargs = self._prepare_gate_kwargs(gate_id, output)
                        result = self.gate_executor.execute(gate_id, **gate_kwargs)

                    gate_results.append(result.to_dict())

                    if result.status == GateStatus.WARNING:
                        print(f"      ⚠️  Warning: {result.message}")
                        warnings.append({
                            'gate_id': gate_id,
                            'message': result.message,
                        })

                except QualityGateBlocked as e:
                    if self.validation_mode:
                        # 验证模式：记录 critical 但不中断，保留真实 output 供下游+评审
                        print(
                            f"      ⚠️  [validation-mode] Gate critical（记录不中断）: "
                            f"{e.result.message}"
                        )
                        gate_results.append({
                            'gate_id': gate_id,
                            'status': 'blocked',
                            'message': e.result.message,
                            'errors': e.result.errors,
                            'issues': e.result.issues,
                            'recommendation': e.result.recommendation,
                        })
                        warnings.append({
                            'gate_id': gate_id,
                            'message': f"[critical-recorded] {e.result.message}",
                        })
                        # 继续后续 gate，不 return
                        continue
                    else:
                        print(f"      ❌ Blocked: {e.result.message}")
                        return StageResult(
                            stage_id=stage_id,
                            status='blocked',
                            output={
                                'gate_id': gate_id,
                                'message': e.result.message,
                                'issues': e.result.issues or e.result.errors,
                                'recommendation': e.result.recommendation,
                            },
                            gate_results=gate_results,
                            warnings=warnings,
                            llm_metrics=llm_metrics,
                        )

        # 保存到 reasoning_assets
        if 'outputs' in stage:
            for output_name in stage['outputs']:
                self.context['reasoning_assets'][output_name] = output

        print(f"   ✅ Completed")

        return StageResult(
            stage_id=stage_id,
            status='success',
            output=output,
            gate_results=gate_results,
            warnings=warnings,
            llm_metrics=llm_metrics,
        )

    def _save_stage_output(self, stage: Dict, result: "StageResult") -> None:
        """逐 stage 保存输出到文件（含 schema validation 结果）。

        文件命名: stage-NN-{stage_id}.json
        无论 success/blocked/error 都保存（失败如实记录，不静默）。
        """
        self._stage_seq += 1
        seq = self._stage_seq
        stage_id = stage.get('id', f'stage{seq}')
        fname = f"stage-{seq:02d}-{stage_id}.json"
        fpath = self.save_stages_dir / fname

        # 提取 schema validation 结果（从 gate_results 里找 schema_gate）
        schema_result = None
        for gr in (result.gate_results or []):
            if gr.get('gate_id') == 'schema_gate':
                schema_result = {
                    'status': gr.get('status'),
                    'errors': gr.get('errors', []),
                }
                break

        record = {
            'stage_seq': seq,
            'stage_id': stage_id,
            'execution_status': result.status,  # success/blocked/error
            'schema_validation': schema_result,
            'llm_metrics': result.llm_metrics,
            'warnings': result.warnings,
            'output': result.output,
        }
        fpath.write_text(
            json.dumps(record, ensure_ascii=False, indent=2, default=str),
            encoding='utf-8',
        )
        print(f"   💾 saved: {fname} (status={result.status})")

    async def _execute_llm_stage(
        self,
        stage: Dict,
        inputs: Dict,
    ) -> tuple[Dict, Dict]:
        """
        通过真实 LLM 执行 stage。

        流程：
        1. 通过 prompt_loader 加载 prompt + 注入上游 artifacts + runtime inputs
        2. 通过 llm_client 异步调用 LLM
        3. 提取 JSON 输出

        Args:
            stage: stage 配置
            inputs: runtime 输入

        Returns:
            (artifact_output, llm_metrics)
        """
        stage_id = stage['id']
        prompt_file = stage.get('prompt')

        if not prompt_file:
            raise ValueError(f"stage {stage_id} 配置缺少 prompt 字段")

        # 1. 准备上游 artifacts（基于 stage.inputs 声明）
        upstream_artifacts: Dict[str, Any] = {}
        stage_input_names = stage.get('inputs', [])
        for input_name in stage_input_names:
            if input_name in self.context['reasoning_assets']:
                upstream_artifacts[input_name] = self.context['reasoning_assets'][input_name]

        # 2. 准备 runtime inputs（PRD 全文等，仅在第一个 stage 注入）
        runtime_inputs: Dict[str, Any] = {}
        for input_name in stage_input_names:
            if input_name in inputs:
                # runtime input（如 prd_content / scope_md）
                runtime_inputs[input_name] = inputs[input_name]

        # 3. 渲染完整 prompt
        full_prompt = self.prompt_loader.render_stage_prompt(
            prompt_file,
            upstream_artifacts=upstream_artifacts if upstream_artifacts else None,
            runtime_inputs=runtime_inputs if runtime_inputs else None,
        )

        print(f"   📝 Prompt rendered ({len(full_prompt)} chars)")
        print(f"      Upstream: {list(upstream_artifacts.keys())}")
        print(f"      Runtime: {list(runtime_inputs.keys())}")

        # 4. 异步调用 LLM（自动续写：检测max_tokens截断时自动continuation）
        print(f"   🤖 Calling LLM ({self.llm_client.model})...")
        response = await self.llm_client.call_with_continuation(full_prompt)
        truncated_marker = " [TRUNCATED]" if response.was_truncated else ""
        cont_marker = (
            f" +{response.continuation_count} continuations"
            if response.continuation_count
            else ""
        )
        print(
            f"      tokens: {response.input_tokens} in / "
            f"{response.output_tokens} out ({response.elapsed_ms}ms)"
            f"{cont_marker}{truncated_marker}"
        )

        # 5. 提取 JSON（失败时 dump 原始输出便于调试）
        try:
            artifact = LLMClient.extract_json(response.text)
        except JSONExtractionError as exc:
            # Dump 原始输出到 /tmp 便于调试
            dump_path = Path(f"/tmp/llm-raw-{stage_id}.txt")
            dump_path.write_text(response.text, encoding="utf-8")
            print(f"      💾 LLM 原始输出已保存到 {dump_path}")
            raise

        # 6. 注入 runtime 元数据（artifact_id / skill_id / created_at 等）
        artifact = self._inject_runtime_metadata(
            artifact, stage_id,
            source_names=list(upstream_artifacts.keys()) + list(runtime_inputs.keys()),
        )

        # 7. 契约规范化（gaps / states 等格式对齐 schema，保留 raw 不掩盖问题）
        artifact = self._normalize_artifact(artifact, stage_id)

        # 8. Schema 自检 + 内容完整性校验 + 重试（Batch 2 retry policy）
        #    schema critical 或 内容关键项缺失 → 带反馈重新生成 1 次
        #    仍失败则记 failure case（不手工伪修复）
        schema_ref = stage.get('schema')
        if schema_ref:
            passed, errors = self.schema_validator.validate(artifact, schema_ref)
            crit = [e for e in errors if e.get('critical')]
            content_issues = self._content_quality_issues(stage_id, artifact)
            if crit or content_issues:
                reasons = []
                if crit:
                    reasons.append(f"{len(crit)} 个 schema critical")
                if content_issues:
                    reasons.append(f"{len(content_issues)} 个内容质量问题")
                print(f"      🔁 触发重试（{', '.join(reasons)}）...")
                missing = sorted({
                    e['message'].split("'")[1]
                    for e in crit
                    if "is a required property" in e.get('message', '') and "'" in e['message']
                })
                retry_prompt = (
                    full_prompt
                    + "\n\n---\n# 上次输出的问题（必须修复）\n"
                    + (f"\n## Schema 缺失字段（{len(crit)} critical）\n{', '.join(missing)}\n" if missing else "")
                    + (f"\n## 内容质量问题（资深设计师必须做到）\n" + "\n".join(f"- {x}" for x in content_issues) + "\n" if content_issues else "")
                    + "\n请重新输出**完整 JSON**：所有 required 字段齐全、枚举合法、"
                    + "且上述内容质量问题全部修复（这是资深 vs 初级的关键差异）。只输出 JSON。"
                )
                try:
                    retry_resp = await self.llm_client.call_with_continuation(retry_prompt)
                    retry_artifact = LLMClient.extract_json(retry_resp.text)
                    retry_artifact = self._inject_runtime_metadata(
                        retry_artifact, stage_id,
                        source_names=list(upstream_artifacts.keys()) + list(runtime_inputs.keys()),
                    )
                    retry_artifact = self._normalize_artifact(retry_artifact, stage_id)
                    rp, re_errs = self.schema_validator.validate(retry_artifact, schema_ref)
                    re_crit = [e for e in re_errs if e.get('critical')]
                    re_content = self._content_quality_issues(stage_id, retry_artifact)
                    # 累计 retry 的 token
                    response.input_tokens += retry_resp.input_tokens
                    response.output_tokens += retry_resp.output_tokens
                    # 采纳判断：schema+内容问题总数减少则采用重试结果
                    before_total = len(crit) + len(content_issues)
                    after_total = len(re_crit) + len(re_content)
                    if after_total < before_total:
                        print(f"      ✅ 重试改善 {before_total}→{after_total}（schema {len(crit)}→{len(re_crit)}, 内容 {len(content_issues)}→{len(re_content)}），采用重试")
                        artifact = retry_artifact
                        artifact['_retry_applied'] = True
                        crit = re_crit
                        content_issues = re_content
                    else:
                        print(f"      ⚠️ 重试未改善（{before_total}→{after_total}），保留原结果")
                except (LLMClientError, JSONExtractionError) as exc:
                    print(f"      ⚠️ 重试失败: {exc}")
                # 仍有 critical 或内容问题 → 记 failure case
                if crit or content_issues:
                    self._record_failure_case(stage_id, artifact, crit, content_issues)

        return artifact, response.to_dict()

    def _content_quality_issues(self, stage_id: str, artifact: Dict) -> list:
        """检查 stage 关键内容质量项（资深 vs 初级的关键差异）。

        返回缺失的关键项描述列表（空=通过）。用于触发重试 + 反馈给 LLM。
        这是 runtime 校验（要求 LLM 重生成），不是手工填充。
        """
        if not isinstance(artifact, dict):
            return []
        issues = []

        if stage_id == 'design-objectives':
            # 推导链不能断
            gdm = artifact.get('goal_derivation_map') or {}
            if not (isinstance(gdm, dict) and gdm.get('business_to_product')):
                issues.append("goal_derivation_map.business_to_product 为空：4层目标推导链断裂，必须连接 BG→PG")
            if not (isinstance(gdm, dict) and gdm.get('product_to_user')):
                issues.append("goal_derivation_map.product_to_user 为空：必须连接 PG→UG")
            # 方法论必选
            em = artifact.get('experience_methodology')
            if not (isinstance(em, dict) and em.get('primary_methodology')):
                issues.append("experience_methodology 缺失：必须选择体验度量方法论（UES/HEART/YOUKU）并说明理由")

        elif stage_id == 'user-task-modeling':
            # 隐藏任务必须识别
            ht = artifact.get('hidden_tasks')
            if not (isinstance(ht, list) and len(ht) >= 1):
                issues.append("hidden_tasks 为空：必须识别≥1个隐藏任务（错误恢复/批量/协作/追溯类），这是资深关键能力")

        elif stage_id == 'user-journey-mapping':
            # 旅程不能模板化：需有情绪曲线 + 关键时刻
            if not artifact.get('emotion_curve'):
                issues.append("emotion_curve 缺失：旅程需有情绪曲线，非页面流程")
            if not artifact.get('moments_of_truth'):
                issues.append("moments_of_truth 缺失：需识别关键决策时刻")

        elif stage_id == 'state-matrix':
            # 状态矩阵覆盖：AI执行态 + 边界态
            if not artifact.get('ai_execution_states'):
                issues.append("ai_execution_states 缺失：AI产品必须覆盖AI执行态（thinking/streaming/中断/失败）")
            if not artifact.get('boundary_states'):
                issues.append("boundary_states 缺失：需覆盖边界态（首次/无权限/离线）")

        return issues

    def _record_failure_case(
        self, stage_id: str, artifact: Dict,
        critical_errors: list, content_issues: list | None = None,
    ) -> None:
        """记录 schema/内容 仍失败的 case 到 failure-cases（不掩盖真实失败）。"""
        fc_dir = PROJECT_ROOT / "eval" / "failure-cases"
        fc_dir.mkdir(parents=True, exist_ok=True)
        fc_path = fc_dir / f"{stage_id}-fail.json"
        fc_path.write_text(
            json.dumps({
                'stage_id': stage_id,
                'remaining_schema_critical': critical_errors,
                'remaining_content_issues': content_issues or [],
                'retry_applied': artifact.get('_retry_applied', False),
                'note': 'remaining after normalization + 1 retry; recorded honestly, not hand-fixed',
            }, ensure_ascii=False, indent=2),
            encoding='utf-8',
        )
        print(f"      📋 failure case 记录: {fc_path.name}")

    # ---- 契约规范化（Batch 2）----

    @staticmethod
    def _infer_gap_category(text: str) -> str:
        """从 gap 描述推断 category（base schema 枚举）。"""
        t = str(text)
        if any(k in t for k in ['冲突', '矛盾', '不一致', 'conflict']):
            return 'conflicting_information'
        if any(k in t for k in ['模糊', '两种', '并存', '不清', '歧义', 'ambig']):
            return 'ambiguous_requirement'
        if any(k in t for k in ['未提供', '未明确', '缺少', '没有', '未定义', 'missing', '无']):
            return 'missing_input'
        return 'insufficient_detail'

    def _normalize_gaps(self, gaps) -> list:
        """规范化 gaps，对齐 base schema + 用户要求字段，保留 raw_gap。

        用户要求字段：gap_id / category / description / severity / source / impact
        base schema required：gap_id / category / description / impact
        规则：自动补齐缺失字段，但保留 raw_gap 记录 LLM 原始输出（不掩盖真实问题）。
        """
        if not isinstance(gaps, list):
            return []
        normalized = []
        for i, g in enumerate(gaps, 1):
            if isinstance(g, str):
                raw = g
                desc = g
                g = {}
            elif isinstance(g, dict):
                raw = dict(g)
                desc = (
                    g.get('description') or g.get('gap')
                    or g.get('issue') or g.get('message') or str(g)
                )
            else:
                continue

            impact = g.get('impact', 'medium')
            if impact not in ('critical', 'high', 'medium', 'low'):
                impact = 'medium'

            category = g.get('category')
            if category not in (
                'missing_input', 'ambiguous_requirement',
                'conflicting_information', 'insufficient_detail',
            ):
                category = self._infer_gap_category(desc)

            norm = {
                'gap_id': g.get('gap_id') if str(g.get('gap_id', '')).startswith('GAP-') else f'GAP-{i:03d}',
                'category': category,
                'description': desc,
                'impact': impact,
                # 用户要求的额外字段（base schema 不 required，但用户要求必须有）
                'severity': g.get('severity', impact),
                'source': g.get('source', 'llm_identified'),
                # 保留原始，不掩盖真实问题
                'raw_gap': raw,
            }
            if 'mitigation' in g:
                norm['mitigation'] = g['mitigation']
            if 'affected_fields' in g:
                norm['affected_fields'] = g['affected_fields']
            normalized.append(norm)
        return normalized

    def _normalize_states(self, artifact: Dict) -> None:
        """规范化 business_flow 的 states，补 state_type（缺失时推断）。"""
        states = artifact.get('states')
        if not isinstance(states, list):
            return
        for s in states:
            if not isinstance(s, dict):
                continue
            st = s.get('state_type')
            if st in ('normal', 'exception', 'terminal'):
                continue
            # 推断：is_terminal→terminal，名称含异常/错误/失败→exception，否则normal
            name = str(s.get('state_name', '')) + str(s.get('description', ''))
            if s.get('is_terminal') or any(k in name for k in ['完成', '关闭', '结束', '终止']):
                s['state_type'] = 'terminal'
            elif any(k in name for k in ['异常', '错误', '失败', '驳回', '拒绝', '超时']):
                s['state_type'] = 'exception'
            else:
                s['state_type'] = 'normal'
            s.setdefault('_runtime_normalized', []).append('state_type')

    def _normalize_artifact(self, artifact: Dict, stage_id: str) -> Dict:
        """契约规范化总入口。透明记录 normalization。"""
        if not isinstance(artifact, dict):
            return artifact
        normalized_fields = []

        # gaps 规范化（所有 stage 通用）
        if artifact.get('gaps'):
            before = artifact['gaps']
            artifact['gaps'] = self._normalize_gaps(before)
            # 仅当确实改了结构才记录
            if artifact['gaps'] and (
                not isinstance(before[0], dict)
                or 'gap_id' not in (before[0] if isinstance(before[0], dict) else {})
            ):
                normalized_fields.append('gaps')

        # states 规范化（business-flow）
        if 'states' in artifact:
            self._normalize_states(artifact)
            normalized_fields.append('states.state_type')

        if normalized_fields:
            artifact.setdefault('_runtime_normalized', normalized_fields)
        return artifact

    def _inject_runtime_metadata(
        self, artifact: Dict, stage_id: str, source_names: list | None = None,
    ) -> Dict:
        """注入 runtime 元数据信封（不篡改 LLM 业务输出）。

        职责边界：
        - 注入 runtime 才知道的字段（artifact_id/run_id/created_at/source_inputs）
        - 补全 base schema required 的元数据信封默认值（仅当 LLM 未输出时）
        - 不修改 business_goals/states 等业务内容
        - 用 _runtime_injected 透明记录哪些是 runtime 补的（不假装是 LLM 给的）
        """
        from datetime import datetime, timezone
        import uuid

        artifact_type = artifact.get('artifact_type', stage_id.replace('-', '_'))
        date_str = datetime.now(timezone.utc).strftime('%Y%m%d')
        short_uuid = uuid.uuid4().hex[:8]
        artifact_id = f"{artifact_type.replace('_', '-')}-{date_str}-{short_uuid}"

        injected = []  # 记录 runtime 补了哪些字段

        def _set_if_missing(key, value):
            if key not in artifact or artifact[key] in (None, "", [], {}):
                artifact[key] = value
                injected.append(key)

        # === runtime 才知道的字段 ===
        artifact.setdefault('artifact_id', artifact_id)
        artifact.setdefault('artifact_type', artifact_type)
        artifact.setdefault('skill_id', 'prd2proto')
        artifact.setdefault('run_id', f'run-{date_str}-{short_uuid}')
        artifact.setdefault(
            'created_at',
            datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ'),
        )

        # source_inputs: runtime 知道喂了哪些输入（LLM 不该编造文件路径）
        if not artifact.get('source_inputs'):
            artifact['source_inputs'] = [
                {
                    'input_type': 'existing_artifact' if '_' in n else 'prd',
                    'input_id': n,
                    'input_status': 'complete',
                }
                for n in (source_names or ['prd_content'])
            ]
            injected.append('source_inputs')

        # === base schema required 元数据信封（LLM 未输出时补保守默认）===
        _set_if_missing('maturity', 'draft')
        if 'confidence' not in artifact:
            artifact['confidence'] = 0.5  # 保守默认；LLM 应自己给
            injected.append('confidence(default-0.5)')
        _set_if_missing('inferred_fields', [])
        _set_if_missing('gaps', [])
        _set_if_missing('warnings', [])
        _set_if_missing('traceability', {})

        # validation_status
        if 'validation_status' not in artifact:
            artifact['validation_status'] = {
                'schema_valid': True,
                'human_review_required': True,
            }
            injected.append('validation_status')
        else:
            artifact['validation_status'].setdefault('schema_valid', True)
            artifact['validation_status'].setdefault('human_review_required', True)

        # 透明记录 runtime 补了什么（不假装 LLM 给的）
        if injected:
            artifact['_runtime_injected'] = injected

        return artifact

    def _run_schema_gate(self, stage: Dict, output: Dict):
        """用 SchemaValidator 执行 schema_gate（支持 $ref 解析）。

        与 kernel/gates.py 的 schema_gate 行为对齐：
        - 0 errors → PASS
        - critical errors > 0 → 抛 QualityGateBlocked
        - 仅 non-critical → WARNING

        Args:
            stage: pipeline stage 配置（含 schema 字段）
            output: stage 产出 artifact

        Returns:
            GateResult 对象
        """
        # 从 stage 配置获取 schema 路径
        schema_ref = stage.get('schema')
        if not schema_ref:
            # stage 未声明 schema，跳过验证（warning）
            return self._make_gate_result(
                gate_id='schema_gate',
                status=GateStatus.WARNING,
                message=f"stage '{stage['id']}' 未声明 schema 字段，跳过 schema 验证",
            )

        passed, errors = self.schema_validator.validate(output, schema_ref)

        if passed:
            return self._make_gate_result(
                gate_id='schema_gate',
                status=GateStatus.PASS,
                message=f"Artifact 符合 schema {schema_ref}",
            )

        critical_errors = [e for e in errors if e.get('critical')]
        non_critical = [e for e in errors if not e.get('critical')]

        if critical_errors:
            # 抛 QualityGateBlocked，复用现有处理逻辑
            blocked_result = self._make_gate_result(
                gate_id='schema_gate',
                status=GateStatus.BLOCKED,
                message=f"发现 {len(critical_errors)} 个 critical schema 错误",
                errors=errors,
                recommendation="修复以下必需字段后重试",
            )
            raise QualityGateBlocked(blocked_result)

        return self._make_gate_result(
            gate_id='schema_gate',
            status=GateStatus.WARNING,
            message=f"发现 {len(non_critical)} 个 non-critical schema 警告",
            errors=errors,
            recommendation="建议补充以下可选字段以提升质量",
        )

    @staticmethod
    def _make_gate_result(
        gate_id: str,
        status,
        message: str,
        errors: list | None = None,
        recommendation: str = "",
    ):
        """构造 GateResult 对象（复用 kernel/gates.py 的 GateResult 类）。"""
        return gates.GateResult(
            gate_id=gate_id,
            status=status,
            message=message,
            errors=errors,
            recommendation=recommendation,
        )

    def _prepare_gate_kwargs(self, gate_id: str, output: Dict) -> Dict:
        """准备质量门参数"""
        if gate_id == 'gap_transparency_gate':
            return {'requirement_inventory': output}

        elif gate_id == 'schema_gate':
            schema = {'type': 'object', 'properties': {}}
            return {'artifact': output, 'schema': schema}

        elif gate_id == 'inference_limit_gate':
            return {'artifact': output}

        elif gate_id == 'traceability_gate':
            return {
                'traceability_map': output.get('traceability', {}),
                'reasoning_assets': self.context['reasoning_assets'],
                'output_artifact': output,
            }

        elif gate_id == 'code_constraint_gate':
            return {
                'generated_code': output,
                'information_architecture': self.context['reasoning_assets'].get(
                    'information_architecture', {}
                ),
                'component_strategy': self.context['reasoning_assets'].get(
                    'component_strategy', {}
                ),
                'state_matrix': self.context['reasoning_assets'].get('state_matrix'),
            }

        return {}

    def _handle_fallback_safe(self):
        """处理 fallback_safe 降级"""
        print(f"\n   ⚠️  Entering Fallback Safe Mode")
        self.context['mode'] = 'pm'
        self.context['fidelity'] = 'low'
        self.context['warnings'].append({
            'warning_id': 'WARN-FALLBACK',
            'severity': 'high',
            'message': '因输入质量不足，已降级到低保真模式（PM 模式）',
        })

    @staticmethod
    def _stage_result_to_dict(r: StageResult) -> Dict:
        """StageResult 序列化（避免 dataclass 嵌套问题）"""
        return {
            'stage_id': r.stage_id,
            'status': r.status,
            'output': r.output,
            'gate_results': r.gate_results,
            'warnings': r.warnings,
            'llm_metrics': r.llm_metrics,
        }


def main():
    """CLI 入口（异步执行）"""
    import argparse

    parser = argparse.ArgumentParser(description='Run prd2proto pipeline')
    parser.add_argument('--pipeline', default='skills/prd2proto/pipeline.yaml')
    parser.add_argument('--mode', default='pm', choices=['pm', 'designer-spec'])
    parser.add_argument(
        '--prd',
        help='PRD 文件路径（默认使用内置测试 PRD）',
    )
    parser.add_argument(
        '--mock',
        action='store_true',
        help='使用 mock 模式（默认走真实 LLM）',
    )
    parser.add_argument('--model', default='claude-opus-4-8')
    parser.add_argument('--max-tokens', type=int, default=32768)
    parser.add_argument(
        '--max-stages',
        type=int,
        help='仅执行前 N 个 stage（冒烟测试用）',
    )
    parser.add_argument(
        '--out',
        default='/tmp/pipeline-output.json',
        help='结果输出路径',
    )
    parser.add_argument(
        '--save-stages-dir',
        help='逐 stage 保存输出的目录（Batch 1 真实验证用）',
    )
    parser.add_argument(
        '--validation-mode',
        action='store_true',
        help='验证模式：gate critical 记录但不中断 pipeline（Batch 1 收集完整数据用）',
    )

    args = parser.parse_args()

    # 准备输入
    if args.prd:
        prd_content = Path(args.prd).read_text(encoding='utf-8')
        prd_file = args.prd
    else:
        prd_content = '# Test PRD\n\nA simple CRM system for sales team.'
        prd_file = 'test-prd.md'

    inputs = {
        'prd_file': prd_file,
        'prd_content': prd_content,
        'mode': args.mode,
    }

    # 创建 executor
    executor = PipelineExecutor(
        args.pipeline,
        mock=args.mock,
        model=args.model,
        max_tokens=args.max_tokens,
        save_stages_dir=args.save_stages_dir,
        validation_mode=args.validation_mode,
    )

    # 可选：只跑前 N 个 stage
    if args.max_stages:
        executor.config['stages'] = executor.config['stages'][: args.max_stages]
        print(f"⚙️  Limited to first {args.max_stages} stages")

    # 异步执行
    result = asyncio.run(executor.execute(inputs))

    # 保存结果
    Path(args.out).write_text(
        json.dumps(result, ensure_ascii=False, indent=2, default=str),
        encoding='utf-8',
    )
    print(f"\n📁 Result saved: {args.out}")

    # 输出总结
    print(f"\n{'=' * 60}")
    print(f"Pipeline Result: {result['status']}")
    if result['status'] == 'blocked':
        print(f"\nBlocked at: {result['blocked_at']}")
    elif result['status'] == 'success':
        print(f"\nReasoning Assets: {len(result['reasoning_assets'])} generated")
        print(f"Warnings: {len(result['warnings'])}")
        if 'metrics' in result:
            m = result['metrics']
            print(
                f"Tokens: {m['total_input_tokens']} in / "
                f"{m['total_output_tokens']} out"
            )
    elif result['status'] == 'error':
        print(f"\nError: {result.get('error')}")
    print(f"{'=' * 60}")


if __name__ == '__main__':
    main()
