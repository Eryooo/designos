"""真实 LLM stage runner（prd2proto v2）。

设计目标：
- 用真实 LLM 执行单个 pipeline stage（加载 prompt + PRD → 产出 artifact JSON）
- 默认走真实 LLM；mock 必须显式 --mock，绝不静默 mock
- 每个 stage 输出经过 schema gate 校验
- 兼容 Claude Code 的 ANTHROPIC_AUTH_TOKEN（现有 provider 只读 ANTHROPIC_API_KEY）

本模块是 P0-3（真实 LLM execution）的基础，先用于 02-design-objectives 质量验证。
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
import time
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[3]
PROMPTS_DIR = Path(__file__).resolve().parent.parent / "prompts-v2"
SCHEMA_DIR = REPO_ROOT / "kernel" / "contracts" / "artifacts"


def resolve_token() -> str | None:
    """Claude Code 用 AUTH_TOKEN，官方 SDK 用 API_KEY，两者都试。"""
    return os.getenv("ANTHROPIC_AUTH_TOKEN") or os.getenv("ANTHROPIC_API_KEY")


def load_prompt(stage_prompt_file: str) -> str:
    # If absolute path or relative to current dir, use as-is
    path = Path(stage_prompt_file)
    if not path.is_absolute():
        # Try relative to PROMPTS_DIR only if it's a simple filename
        if '/' not in stage_prompt_file:
            path = PROMPTS_DIR / stage_prompt_file
    if not path.exists():
        raise FileNotFoundError(f"prompt not found: {path}")
    return path.read_text(encoding="utf-8")


def build_stage_input(prompt_text: str, prd_text: str) -> str:
    """组装发给 LLM 的完整输入：prompt(系统指令) + PRD(输入) + 输出要求。"""
    return f"""{prompt_text}

---

# 实际输入：PRD 文档

以下是需要你分解目标的真实 PRD：

```markdown
{prd_text}
```

---

# 你的任务

严格按照上述 prompt 的 Senior Designer Reasoning Model 和 Output Schema，
对这份 PRD 做设计目标分解。

**只输出一个 JSON 对象**（design_objectives artifact 的内容字段 + 推理元数据），
不要输出任何解释性文字、不要 markdown 代码块标记以外的内容。
不要生成 runtime 注入字段（artifact_id / skill_id / run_id / created_at / validation_status.schema_valid）。
"""


async def call_llm(full_input: str, model: str, max_tokens: int) -> dict[str, Any]:
    from anthropic import AsyncAnthropic

    token = resolve_token()
    if not token:
        raise RuntimeError(
            "未找到 LLM 凭证。请设置 ANTHROPIC_AUTH_TOKEN 或 ANTHROPIC_API_KEY。"
            "（默认运行需要真实 LLM；如需 mock 请显式加 --mock）"
        )
    base_url = os.getenv("ANTHROPIC_BASE_URL")
    client = AsyncAnthropic(api_key=token, base_url=base_url)

    t0 = time.time()
    # Use streaming to avoid 10min timeout
    full_text = ""
    async with client.messages.stream(
        model=model,
        max_tokens=max_tokens,
        temperature=0.3,
        messages=[{"role": "user", "content": full_input}],
    ) as stream:
        async for text in stream.text_stream:
            full_text += text
        # Get final message BEFORE exiting context
        final_msg = await stream.get_final_message()

    elapsed_ms = int((time.time() - t0) * 1000)
    return {
        "text": full_text,
        "input_tokens": final_msg.usage.input_tokens,
        "output_tokens": final_msg.usage.output_tokens,
        "elapsed_ms": elapsed_ms,
        "model": model,
    }


def extract_json(text: str) -> dict[str, Any]:
    """从 LLM 输出里提取 JSON（容忍 ```json 包裹或前后杂字）。"""
    fenced = re.search(r"```(?:json)?\s*(\{.*\})\s*```", text, re.DOTALL)
    raw = fenced.group(1) if fenced else text
    start = raw.find("{")
    end = raw.rfind("}")
    if start == -1 or end == -1:
        raise ValueError("LLM 输出中未找到 JSON 对象")
    return json.loads(raw[start : end + 1])


def validate_against_schema(artifact: dict[str, Any], schema_file: str) -> list[str]:
    """用 jsonschema 校验内容字段。返回错误列表（空=通过）。

    注：本 runner 只校验"内容 + 推理元数据"，runtime 注入字段在此处补桩，
    以隔离 prompt 质量问题与 runtime 集成问题。
    """
    import jsonschema
    from jsonschema import Draft7Validator
    from referencing import Registry, Resource

    schema_path = SCHEMA_DIR / schema_file
    schema = json.loads(schema_path.read_text(encoding="utf-8"))

    # 加载 base schema 供 $ref 解析
    registry = Registry()
    for sf in SCHEMA_DIR.glob("*.schema.json"):
        doc = json.loads(sf.read_text(encoding="utf-8"))
        resource = Resource.from_contents(doc)
        registry = registry.with_resource(uri=f"./{sf.name}", resource=resource)

    # 补 runtime 注入字段的桩，使其能完整过 base required
    stub = {
        "artifact_id": "design-objectives-20260610-deadbeef",
        "skill_id": "prd2proto",
        "run_id": "run-validate01",
        "created_at": "2026-06-10T10:00:00Z",
    }
    candidate = {**stub, **artifact}
    candidate.setdefault("validation_status", {})
    candidate["validation_status"].setdefault("schema_valid", True)
    candidate["validation_status"].setdefault("human_review_required", True)

    validator = Draft7Validator(schema, registry=registry)
    errors = sorted(validator.iter_errors(candidate), key=lambda e: list(e.path))
    return [f"{'/'.join(map(str, e.path))}: {e.message}" for e in errors]


async def run(args: argparse.Namespace) -> int:
    prompt_text = load_prompt(args.prompt)
    prd_text = Path(args.prd).read_text(encoding="utf-8")
    full_input = build_stage_input(prompt_text, prd_text)

    if args.mock:
        print("⚠️  MOCK 模式（显式 --mock）。真实运行请去掉 --mock。")
        return 0

    print(f"🚀 真实 LLM 执行 stage: {args.prompt}")
    print(f"   model={args.model}  prd={Path(args.prd).name}")
    result = await call_llm(full_input, args.model, args.max_tokens)
    print(f"   tokens: {result['input_tokens']} in / {result['output_tokens']} out  ({result['elapsed_ms']}ms)")

    try:
        artifact = extract_json(result["text"])
    except (ValueError, json.JSONDecodeError) as exc:
        print(f"❌ JSON 解析失败: {exc}")
        Path(args.out).write_text(result["text"], encoding="utf-8")
        print(f"   原始输出已存: {args.out}")
        return 2

    Path(args.out).write_text(json.dumps(artifact, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"✅ artifact 已存: {args.out}")

    if args.schema:
        errors = validate_against_schema(artifact, args.schema)
        if errors:
            print(f"\n⚠️  Schema Gate: {len(errors)} 处不符合")
            for e in errors[:15]:
                print(f"   - {e}")
            return 3
        print("\n✅ Schema Gate: 通过")
    return 0


def main() -> int:
    import asyncio

    parser = argparse.ArgumentParser(description="真实 LLM stage runner (prd2proto v2)")
    parser.add_argument("--prompt", default="02-design-objectives.md")
    parser.add_argument("--prd", required=True, help="PRD 文件路径")
    parser.add_argument("--schema", default="design-objectives.schema.json")
    parser.add_argument("--model", default="claude-opus-4-8")
    parser.add_argument("--max-tokens", type=int, default=8192)
    parser.add_argument("--out", default="/tmp/stage-02-output.json")
    parser.add_argument("--mock", action="store_true", help="显式 mock（默认走真实 LLM）")
    args = parser.parse_args()
    return asyncio.run(run(args))


if __name__ == "__main__":
    sys.exit(main())
