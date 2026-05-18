"""Pure helpers for serialising / deserialising pipeline state.

Pipeline state is a free-form ``dict[str, Any]`` shared across stages. We
need a stable on-disk representation, so non-JSON types are converted to
tagged sentinels:

- ``Path`` ⇒ ``{"__path__": "/abs/path"}``
- ``datetime`` ⇒ ``{"__datetime__": "<iso>"}``
- ``Enum`` ⇒ ``{"__enum__": "module.Class.NAME", "value": ...}``
- Pydantic v2 models ⇒ ``{"__pydantic__": "module.Class", "value": dump}``
"""

from __future__ import annotations

import importlib
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any

from pydantic import BaseModel


def serialize_state(state: dict[str, Any]) -> dict[str, Any]:
    """Recursively encode a state dict into JSON-safe primitives."""
    return {key: _encode(value) for key, value in state.items()}


def deserialize_state(payload: dict[str, Any]) -> dict[str, Any]:
    """Recursively decode the output of :func:`serialize_state`."""
    return {key: _decode(value) for key, value in payload.items()}


def _encode(value: Any) -> Any:
    if isinstance(value, Path):
        return {"__path__": str(value)}
    if isinstance(value, datetime):
        return {"__datetime__": value.isoformat()}
    if isinstance(value, Enum):
        return {
            "__enum__": f"{type(value).__module__}.{type(value).__qualname__}",
            "value": value.value,
        }
    if isinstance(value, BaseModel):
        return {
            "__pydantic__": f"{type(value).__module__}.{type(value).__qualname__}",
            "value": value.model_dump(mode="json"),
        }
    if isinstance(value, dict):
        return {str(k): _encode(v) for k, v in value.items()}  # type: ignore[redundant-cast]
    if isinstance(value, list):
        return [_encode(v) for v in value]  # type: ignore[arg-type]
    if isinstance(value, tuple):
        return [_encode(v) for v in value]  # type: ignore[arg-type]
    return value


def _decode(value: Any) -> Any:
    if isinstance(value, dict):
        if "__path__" in value:
            return Path(value["__path__"])
        if "__datetime__" in value:
            return datetime.fromisoformat(value["__datetime__"])
        if "__enum__" in value:
            return _resolve_enum(value["__enum__"], value["value"])
        if "__pydantic__" in value:
            return _resolve_model(value["__pydantic__"], value["value"])
        return {k: _decode(v) for k, v in value.items()}  # type: ignore[arg-type]
    if isinstance(value, list):
        return [_decode(v) for v in value]  # type: ignore[arg-type]
    return value


def _resolve_enum(qualified: str, raw: Any) -> Any:
    module_path, _, class_name = qualified.rpartition(".")
    cls: type[Enum] = getattr(importlib.import_module(module_path), class_name)
    return cls(raw)


def _resolve_model(qualified: str, raw: Any) -> Any:
    module_path, _, class_name = qualified.rpartition(".")
    cls: type[BaseModel] = getattr(importlib.import_module(module_path), class_name)
    return cls.model_validate(raw)


__all__ = ["deserialize_state", "serialize_state"]
