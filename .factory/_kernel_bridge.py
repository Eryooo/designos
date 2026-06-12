"""DesignOS Skills Factory — Kernel Bridge.

Single import point for the kernel schemas the factory relies on.

Why this module exists:
    The factory must NOT redefine ``SkillConfig`` / ``StageConfig`` /
    ``CheckpointConfig`` / ``OutputType`` etc. The kernel already owns those as
    the single source of truth (``kernel.contracts.schemas``). The factory
    re-exports them through this bridge so:

    1. Every factory tool reads from one place.
    2. If the kernel renames or extends a schema, the factory breaks loudly
       at this single import boundary instead of in 4-5 scattered files.
    3. Tests can mock or substitute schemas via this module.

Per CONTRACT §6, factory code must import schemas via this bridge only.
"""

from __future__ import annotations

# CRITICAL: Ensure local repo's kernel is loaded, not any installed version
# in site-packages. The factory must always use the kernel that lives next to
# it in this repo, so extract/validate/scaffold see the same schemas the
# user is developing against.
import sys
from pathlib import Path as _Path

_REPO_ROOT: _Path = _Path(__file__).resolve().parent.parent
_repo_root_str: str = str(_REPO_ROOT)
if _repo_root_str in sys.path:
    sys.path.remove(_repo_root_str)
sys.path.insert(0, _repo_root_str)

# Drop any previously-imported kernel module from a different location so we
# re-import from the repo. This handles the case where some other code
# imported `kernel` from site-packages before the bridge loaded.
for _mod_name in list(sys.modules):
    if _mod_name == "kernel" or _mod_name.startswith("kernel."):
        _mod = sys.modules[_mod_name]
        _mod_file = getattr(_mod, "__file__", None)
        if _mod_file and not _mod_file.startswith(_repo_root_str):
            del sys.modules[_mod_name]

from kernel.contracts.enums import (  # noqa: E402
    CheckpointAction,
    ErrorCode,
    MCPTransport,
    Mode,
    OutputType,
    RunStatus,
    SeverityLevel,
    SkillType,
    StageStatus,
    StageType,
)
from kernel.contracts.schemas import (  # noqa: E402
    CheckpointConfig,
    ExternalRequirementConfig,
    MCPServerConfig,
    RetryConfig,
    SkillConfig,
    SkillOutputConfig,
    StageConfig,
    StageGateConfig,
)
from kernel.skill_loader import load_pipeline_skill, parse_frontmatter  # noqa: E402

__all__ = [
    "CheckpointAction",
    "CheckpointConfig",
    "ErrorCode",
    "ExternalRequirementConfig",
    "MCPServerConfig",
    "MCPTransport",
    "Mode",
    "OutputType",
    "RetryConfig",
    "RunStatus",
    "SeverityLevel",
    "SkillConfig",
    "SkillOutputConfig",
    "SkillType",
    "StageConfig",
    "StageGateConfig",
    "StageStatus",
    "StageType",
    "load_pipeline_skill",
    "parse_frontmatter",
]
