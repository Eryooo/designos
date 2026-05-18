"""Tiny safe expression evaluator for ``stage.only_when``.

The DSL supports:
- ``mode == "<value>"`` / ``mode != "<value>"``
- ``mode in ["a", "b"]``
- conjunction with ``and``

Anything else is rejected. We deliberately avoid ``eval`` and stick to a
hand-rolled parser to keep the threat surface tiny.
"""

from __future__ import annotations

import ast

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


def _vars(ctx: SkillContext) -> dict[str, object]:
    return {"mode": ctx.mode}


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
    if isinstance(node, ast.List):
        return [_value(e, env) for e in node.elts]
    if isinstance(node, ast.Tuple):
        return tuple(_value(e, env) for e in node.elts)
    return None


__all__ = ["condition_satisfied"]
