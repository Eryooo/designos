"""Loader for ``.factory/archetypes/<name>.yaml`` files."""

from __future__ import annotations

from pathlib import Path

import yaml

from .archetype_schema import ArchetypeSpec

_ARCHETYPES_DIR: Path = Path(__file__).parent


def load_archetype(name: str, *, root: Path | None = None) -> ArchetypeSpec:
    """Load and validate an archetype spec by name.

    Args:
        name: Archetype name (e.g. ``"evaluation"``).
        root: Optional override of the archetypes directory.

    Raises:
        FileNotFoundError: When the archetype yaml is missing.
        pydantic.ValidationError: When the yaml does not match the schema.
    """
    base: Path = root if root is not None else _ARCHETYPES_DIR
    yaml_path: Path = base / f"{name}.yaml"
    if not yaml_path.exists():
        raise FileNotFoundError(
            f"archetype '{name}' not found at {yaml_path}. "
            f"Available: {sorted(p.stem for p in base.glob('*.yaml'))}"
        )
    raw = yaml.safe_load(yaml_path.read_text(encoding="utf-8"))
    return ArchetypeSpec.model_validate(raw)


__all__ = ["load_archetype"]
