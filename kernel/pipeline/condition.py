"""Tiny safe expression evaluator for runtime stage expressions.

The DSL supports:
- ``mode == "<value>"`` / ``mode != "<value>"``
- dotted runtime references like ``evidence_assessment.verdict``
- ``mode in ["a", "b"]``
- conjunction with ``and``

Anything else is rejected. We deliberately avoid ``eval`` and stick to a
hand-rolled parser to keep the threat surface tiny.
"""

from __future__ import annotations

import ast
from typing import Any

from kernel.contracts.schemas import SkillContext


def condition_satisfied(expression: str | None, ctx: SkillContext) -> bool:
    """Return True when ``expression`` evaluates truthy against ``ctx``."""
    if not expression:
        return True
    try:
        tree: ast.Expression = ast.parse(expression, mode="eval")
    except SyntaxError:
        return False
    return _eval(tree.body, _vars(ctx))


def context_value(ctx: SkillContext, path: str | None) -> Any:
    """Resolve a dotted path against the runtime condition environment."""
    if not path:
        return None
    current: Any = _vars(ctx)
    for part in path.split("."):
        current = _member(current, part)
        if current is None:
            return None
    return current


def _vars(ctx: SkillContext) -> dict[str, object]:
    env: dict[str, object] = {"mode": ctx.mode}
    env.update(ctx.state)
    return env


def _eval(node: ast.expr, env: dict[str, object]) -> bool:
    if isinstance(node, ast.BoolOp) and isinstance(node.op, ast.And):
        return all(_eval(child, env) for child in node.values)
    if isinstance(node, ast.BoolOp) and isinstance(node.op, ast.Or):
        return any(_eval(child, env) for child in node.values)
    if isinstance(node, ast.Compare) and len(node.ops) == 1 and len(node.comparators) == 1:
        left: object = _value(node.left, env)
        right: object = _value(node.comparators[0], env)
        op: ast.cmpop = node.ops[0]
        if isinstance(op, ast.Eq):
            return left == right
        if isinstance(op, ast.NotEq):
            return left != right
        if isinstance(op, ast.In):
            return left in right  # type: ignore[operator]
        if isinstance(op, ast.NotIn):
            return left not in right  # type: ignore[operator]
    if isinstance(node, ast.Constant):
        return bool(node.value)
    return False


def _value(node: ast.expr, env: dict[str, object]) -> object:
    if isinstance(node, ast.Constant):
        return node.value
    if isinstance(node, ast.Name):
        return env.get(node.id)
    if isinstance(node, ast.Attribute):
        base = _value(node.value, env)
        return _member(base, node.attr)
    if isinstance(node, ast.List):
        return [_value(e, env) for e in node.elts]
    if isinstance(node, ast.Tuple):
        return tuple(_value(e, env) for e in node.elts)
    return None


def _member(value: object, key: str) -> object | None:
    if isinstance(value, dict):
        return value.get(key)
    return getattr(value, key, None)


__all__ = ["condition_satisfied", "context_value"]
