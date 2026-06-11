"""Schema Validator for prd2proto pipeline.

加载 kernel/contracts/artifacts/ 下的真实 JSON Schema，验证 LLM 产出的 artifact。

核心能力：
1. 加载 schema 文件（支持 pipeline.yaml 里声明的相对路径）
2. 解析 $ref（schema 用 allOf + $ref 引用 artifact-base.schema.json）
3. 验证 artifact，返回错误列表

设计原则：
- 与 gate 解耦：本模块只做"加载+验证"，gate 负责判定 block/warning
- 容错：schema 文件不存在时返回明确错误，不崩溃
- 复用现有 schema：不创建新 schema（kernel/contracts 是 source of truth）
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

# 项目根目录（本文件在 skills/prd2proto/runtime/）
PROJECT_ROOT = Path(__file__).resolve().parents[3]
SCHEMA_DIR = PROJECT_ROOT / "kernel" / "contracts" / "artifacts"


class SchemaValidator:
    """加载真实 JSON Schema 并验证 artifact。"""

    def __init__(self, schema_dir: Path | str | None = None):
        """
        Args:
            schema_dir: schema 目录（默认 kernel/contracts/artifacts/）
        """
        self.schema_dir = Path(schema_dir) if schema_dir else SCHEMA_DIR
        self._registry = None  # 延迟构建（含所有 schema，供 $ref 解析）
        self._schema_cache: dict[str, dict] = {}

    def _build_registry(self):
        """构建 referencing Registry，加载所有 schema 供 $ref 解析。"""
        if self._registry is not None:
            return self._registry

        from referencing import Registry, Resource

        registry = Registry()
        if self.schema_dir.exists():
            for schema_file in self.schema_dir.glob("*.schema.json"):
                try:
                    doc = json.loads(schema_file.read_text(encoding="utf-8"))
                except json.JSONDecodeError:
                    continue
                resource = Resource.from_contents(doc)
                # 注册多种 URI 形式以兼容不同 $ref 写法
                registry = registry.with_resource(
                    uri=f"./{schema_file.name}", resource=resource
                )
                registry = registry.with_resource(
                    uri=schema_file.name, resource=resource
                )

        self._registry = registry
        return registry

    def load_schema(self, schema_ref: str) -> dict[str, Any] | None:
        """加载 schema 文件。

        Args:
            schema_ref: schema 引用，支持：
                - "kernel/contracts/artifacts/design-objectives.schema.json"（pipeline.yaml格式）
                - "design-objectives.schema.json"（仅文件名）
                - 绝对路径

        Returns:
            schema dict，加载失败返回 None
        """
        if schema_ref in self._schema_cache:
            return self._schema_cache[schema_ref]

        # 解析路径
        path = Path(schema_ref)
        if not path.is_absolute():
            if schema_ref.startswith("kernel/"):
                path = PROJECT_ROOT / schema_ref
            elif "/" not in schema_ref:
                path = self.schema_dir / schema_ref
            else:
                path = PROJECT_ROOT / schema_ref

        if not path.exists():
            return None

        try:
            schema = json.loads(path.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            return None

        self._schema_cache[schema_ref] = schema
        return schema

    def validate(
        self,
        artifact: dict[str, Any],
        schema_ref: str,
    ) -> tuple[bool, list[dict[str, Any]]]:
        """验证 artifact 是否符合 schema。

        Args:
            artifact: 要验证的 artifact dict
            schema_ref: schema 引用

        Returns:
            (是否通过, 错误列表)
            错误列表元素: {field, message, validator, critical}
        """
        schema = self.load_schema(schema_ref)
        if schema is None:
            return False, [{
                "field": "",
                "message": f"schema 文件加载失败: {schema_ref}",
                "validator": "schema_load",
                "critical": True,
            }]

        from jsonschema import Draft7Validator

        registry = self._build_registry()
        validator = Draft7Validator(schema, registry=registry)

        errors = sorted(
            validator.iter_errors(artifact),
            key=lambda e: list(e.path),
        )

        if not errors:
            return True, []

        # 格式化错误，判定 critical（required 字段缺失=critical）
        formatted = []
        for err in errors:
            field_path = ".".join(str(p) for p in err.path) or "(root)"
            is_critical = self._is_critical_error(err)
            formatted.append({
                "field": field_path,
                "message": err.message[:200],
                "validator": err.validator,
                "critical": is_critical,
            })

        return False, formatted

    @staticmethod
    def _is_critical_error(error) -> bool:
        """判定错误是否 critical。

        critical: required 字段缺失、类型错误（核心结构问题）
        non-critical: 格式/枚举/长度等（可修复的质量问题）
        """
        # required 字段缺失 → critical
        if error.validator == "required":
            return True
        # 顶层类型错误 → critical
        if error.validator == "type" and len(list(error.path)) == 0:
            return True
        # 其他（enum/pattern/minLength/format等）→ non-critical
        return False

    def get_schema_ref_from_stage(self, stage_config: dict) -> str | None:
        """从 pipeline stage 配置提取 schema 引用。"""
        return stage_config.get("schema")


def main():
    """CLI 测试：验证某个 artifact 文件对某 schema。"""
    import argparse

    parser = argparse.ArgumentParser(description="测试 SchemaValidator")
    parser.add_argument(
        "--schema",
        default="design-objectives.schema.json",
        help="schema 文件名或路径",
    )
    parser.add_argument("--artifact", help="artifact JSON 文件路径")
    args = parser.parse_args()

    validator = SchemaValidator()

    print(f"=== 加载 schema: {args.schema} ===")
    schema = validator.load_schema(args.schema)
    if schema is None:
        print(f"❌ schema 加载失败")
        return
    print(f"✅ schema 加载成功: {schema.get('title', 'untitled')}")

    if args.artifact:
        artifact = json.loads(Path(args.artifact).read_text(encoding="utf-8"))
        print(f"\n=== 验证 artifact: {args.artifact} ===")
        passed, errors = validator.validate(artifact, args.schema)
        if passed:
            print("✅ 验证通过")
        else:
            critical = [e for e in errors if e["critical"]]
            print(f"❌ {len(errors)} 个错误（{len(critical)} 个 critical）")
            for e in errors[:10]:
                mark = "🔴" if e["critical"] else "🟡"
                print(f"   {mark} {e['field']}: {e['message'][:80]}")
    else:
        # 用一个空 artifact 测试 required 检查
        print(f"\n=== 用空对象测试 required 检查 ===")
        passed, errors = validator.validate({}, args.schema)
        critical = [e for e in errors if e["critical"]]
        print(f"{'✅' if not passed else '❌'} 空对象应该失败: {len(errors)} 个错误（{len(critical)} critical）")
        for e in errors[:8]:
            mark = "🔴" if e["critical"] else "🟡"
            print(f"   {mark} {e['field']}: {e['message'][:60]}")


if __name__ == "__main__":
    main()
