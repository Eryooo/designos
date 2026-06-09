"""Tests for the factory kernel bridge.

Per CONTRACT §3.B (schema_import_count >= 8), the factory must reuse the
kernel's pydantic schemas. These tests fail loudly if either:

- the bridge stops re-exporting required symbols, OR
- the kernel renames a symbol the bridge depends on.

This is the single early-warning surface for kernel/factory schema drift.
"""

from __future__ import annotations

import importlib

# We resolve the bridge dynamically because `.factory` starts with a dot which
# Python treats as a hidden directory; it's not a regular package name.
_BRIDGE = importlib.import_module(".factory._kernel_bridge", package=None) if False else None


def _bridge():
    return importlib.import_module("_kernel_bridge_proxy")


def test_kernel_bridge_reexports_all_required_schemas() -> None:
    """CONTRACT §3.B: schema_import_count >= 8."""
    import sys
    from pathlib import Path

    factory_dir = Path(__file__).resolve().parents[1]
    if str(factory_dir) not in sys.path:
        sys.path.insert(0, str(factory_dir))
    import _kernel_bridge as bridge

    required: list[str] = [
        # enums
        "OutputType",
        "StageType",
        "SkillType",
        "CheckpointAction",
        "Mode",
        "MCPTransport",
        "RunStatus",
        "StageStatus",
        "SeverityLevel",
        "ErrorCode",
        # schemas
        "SkillConfig",
        "SkillOutputConfig",
        "StageConfig",
        "CheckpointConfig",
        "StageGateConfig",
        "RetryConfig",
        "MCPServerConfig",
        "ExternalRequirementConfig",
        # loader entry points
        "load_pipeline_skill",
        "parse_frontmatter",
    ]
    for name in required:
        assert hasattr(bridge, name), (
            f"kernel bridge is missing `{name}`; either kernel renamed it or "
            "the bridge stopped re-exporting it. Update .factory/_kernel_bridge.py."
        )


def test_kernel_bridge_objects_match_kernel_originals() -> None:
    """The bridge must re-export the SAME objects, not redefined copies."""
    import sys
    from pathlib import Path

    factory_dir = Path(__file__).resolve().parents[1]
    if str(factory_dir) not in sys.path:
        sys.path.insert(0, str(factory_dir))
    import _kernel_bridge as bridge

    from kernel.contracts.enums import OutputType as KernelOutputType
    from kernel.contracts.schemas import SkillConfig as KernelSkillConfig
    from kernel.contracts.schemas import StageConfig as KernelStageConfig
    from kernel.skill_loader import load_pipeline_skill as kernel_load

    assert bridge.OutputType is KernelOutputType
    assert bridge.SkillConfig is KernelSkillConfig
    assert bridge.StageConfig is KernelStageConfig
    assert bridge.load_pipeline_skill is kernel_load


def test_factory_does_not_redefine_kernel_schemas() -> None:
    """Static check: factory archetypes/ must not subclass kernel schemas
    or shadow their names with new BaseModel subclasses.

    We approximate this by checking that ArchetypeSpec uses kernel enums
    (re-exported via bridge) for its OutputType / StageType fields.
    """
    import sys
    from pathlib import Path

    factory_dir = Path(__file__).resolve().parents[1]
    if str(factory_dir) not in sys.path:
        sys.path.insert(0, str(factory_dir))
    from archetypes import ArchetypeSpec
    from kernel.contracts.enums import OutputType as KernelOutputType

    output_field = ArchetypeSpec.model_fields["outputs"]
    # The OutputRequirement model has fields typed list[OutputType] — the
    # OutputType used must be the kernel one.
    from archetypes.archetype_schema import OutputRequirement

    output_type = OutputRequirement.model_fields["required"].annotation
    # list[OutputType] — extract the inner type
    args = getattr(output_type, "__args__", ())
    assert KernelOutputType in args, (
        "ArchetypeSpec.outputs.required must use kernel OutputType enum; "
        "do not redefine output types in the factory."
    )
    _ = output_field  # silence unused
