"""Archetype schema — the contract that defines what an archetype is.

An archetype is a *machine-readable specification* of a skill family
(evaluation / generation / analysis). It is the single source of truth for
both ``validate`` (does this skill conform?) and ``scaffold`` (what should
the skeleton look like?).

Key design choices (per CONTRACT §7):

- **Reuses kernel enums** for ``OutputType`` / ``StageType`` / ``CheckpointAction``
  via the kernel bridge — no parallel string enums.

- **mode_semantics is explicit** because the same word "mode" means different
  things across archetypes:
    * ``evidence_collection`` — uxeval's web/client (how evidence is captured)
    * ``fidelity``            — prd2proto's pm/designer-spec/designer-dsl
    * ``data_source``         — ai-analytics' web/client (where competitors come from)
    * ``none``                — single-mode skills (ip-design, brand-creative.*)

- **Stage / checkpoint / gate topology is declarative**: each archetype
  declares which canonical stages must exist, which checkpoints must pause,
  which gates must guard. Concrete skill implementations then map their
  stage IDs to these archetype slots.

- **All pieces are optional-with-defaults**: an archetype can omit slots
  it doesn't need (e.g. analysis archetype may skip evidence_contract).
  Validators interpret "omitted = not enforced".
"""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

# Absolute import: callers add `.factory/` to sys.path so the bridge is at top level.
from _kernel_bridge import OutputType, StageType


# ---------------------------------------------------------------------------
# Frontmatter / output requirements
# ---------------------------------------------------------------------------


class FrontmatterRequirement(BaseModel):
    """Required frontmatter fields for a skill of this archetype."""

    model_config = ConfigDict(frozen=True)

    required_keys: list[str] = Field(
        default_factory=lambda: ["name", "version", "type", "requires", "outputs"],
        description="Top-level frontmatter keys that MUST be present.",
    )
    required_kernel_range: str = Field(
        default=">=1.0.0,<2.0.0",
        description="The kernel range every skill of this archetype must declare.",
    )
    skill_type: Literal["pipeline", "group"] = Field(
        default="pipeline",
        description="Form factor expected for this archetype.",
    )


class OutputRequirement(BaseModel):
    """OutputTypes that every skill of this archetype must declare."""

    model_config = ConfigDict(frozen=True)

    required: list[OutputType] = Field(
        default_factory=list,
        description="OutputTypes that MUST appear in skill `outputs`.",
    )
    optional: list[OutputType] = Field(
        default_factory=list,
        description="OutputTypes commonly seen but not required.",
    )


# ---------------------------------------------------------------------------
# Stage / checkpoint / gate topology
# ---------------------------------------------------------------------------


class StageSlot(BaseModel):
    """One canonical stage in the archetype's pipeline topology.

    A skill maps one of its concrete stage IDs to each slot. Two stages
    of the same skill cannot fill the same slot.
    """

    model_config = ConfigDict(frozen=True)

    slot_id: str = Field(..., description="Canonical slot identifier (e.g. 'understanding').")
    purpose: str = Field(..., description="What this stage is for, in human terms.")
    stage_type: StageType = Field(..., description="Required execution shape.")
    required: bool = Field(
        default=True,
        description="True = every skill must implement this slot.",
    )
    only_when_modes: list[str] = Field(
        default_factory=list,
        description="If non-empty, slot is only required for these mode IDs.",
    )
    required_inputs: list[str] = Field(
        default_factory=list,
        description="Variable names this stage must accept as input.",
    )
    required_outputs: list[str] = Field(
        default_factory=list,
        description="Variable names this stage must produce.",
    )


class CheckpointSlot(BaseModel):
    """A canonical pause point in the archetype's pipeline topology."""

    model_config = ConfigDict(frozen=True)

    checkpoint_id: str = Field(..., description="Canonical checkpoint id (e.g. 'C1').")
    after_slot: str = Field(..., description="The stage slot this checkpoint follows.")
    purpose: str = Field(..., description="Why a human must intervene here.")
    required: bool = Field(default=True)


class GateSlot(BaseModel):
    """A canonical runtime gate in the archetype's pipeline topology."""

    model_config = ConfigDict(frozen=True)

    gate_id: str = Field(..., description="Canonical gate id (e.g. 'QG2').")
    on_slot: str = Field(..., description="The stage slot this gate guards.")
    purpose: str = Field(..., description="What runtime condition this gate enforces.")
    required: bool = Field(default=True)
    only_when_modes: list[str] = Field(default_factory=list)


# ---------------------------------------------------------------------------
# Mode / contract semantics
# ---------------------------------------------------------------------------


class ModeSemantics(BaseModel):
    """How modes are interpreted for this archetype.

    Per CONTRACT §7, mode language is archetype-specific. The same word
    "mode" means evidence-collection vs fidelity vs data-source. Validate
    must enforce per-archetype rules.
    """

    model_config = ConfigDict(frozen=True)

    semantic_type: Literal["evidence_collection", "fidelity", "data_source", "none"] = Field(
        ...,
        description="What 'mode' means semantically for this archetype.",
    )
    allowed_modes: list[str] = Field(
        default_factory=list,
        description="Modes a skill of this archetype MAY declare (empty = no constraint).",
    )
    must_be_single_mode: bool = Field(
        default=False,
        description="If True, skill must NOT declare multiple modes.",
    )


class EvidenceContract(BaseModel):
    """Required evidence-related fields produced somewhere in the pipeline.

    Only meaningful for evaluation archetype; analysis/generation may omit.
    """

    model_config = ConfigDict(frozen=True)

    required_fields: list[str] = Field(
        default_factory=list,
        description="Variable names that must surface in pipeline state at some stage.",
    )
    trusted_evidence_threshold: float = Field(
        default=0.99,
        description="Required trusted-evidence rate for normal-mode final delivery.",
    )
    fallback_evidence_threshold: float = Field(
        default=0.85,
        description="Required trusted-evidence rate for fallback safe delivery.",
    )


class DeliveryContract(BaseModel):
    """Required delivery-state fields produced by audit / gate stages."""

    model_config = ConfigDict(frozen=True)

    required_states: list[str] = Field(
        default_factory=lambda: [
            "final_delivery_ready",
            "fallback_safe",
            "supplement_required",
            "blocked",
        ],
        description="Delivery status enum the skill must support in its audit gate.",
    )


# ---------------------------------------------------------------------------
# Directory & file expectations
# ---------------------------------------------------------------------------


class DirectoryRequirement(BaseModel):
    """Directory layout every skill of this archetype must follow."""

    model_config = ConfigDict(frozen=True)

    required_directories: list[str] = Field(
        default_factory=list,
        description="Subdirectories that must exist (paths relative to skill root).",
    )
    required_files: list[str] = Field(
        default_factory=list,
        description="Files that must exist (paths relative to skill root).",
    )
    eval_layout: bool = Field(
        default=True,
        description="If True, requires eval/golden/ + eval/failure/ + eval/promptfoo.yaml.",
    )


# ---------------------------------------------------------------------------
# Top-level archetype spec
# ---------------------------------------------------------------------------


class ArchetypeSpec(BaseModel):
    """The complete machine-readable spec for one archetype.

    This is what gets serialized to ``.factory/archetypes/<name>.yaml`` and
    loaded back by both ``validate`` and ``scaffold``.
    """

    model_config = ConfigDict(frozen=True)

    name: Literal["evaluation", "generation", "analysis", "creative-generation"] = Field(...)
    version: str = Field(..., description="Semver of the archetype spec itself.")
    description: str = Field(...)
    representative_skill: str = Field(
        ...,
        description="Skill name this archetype was extracted from (for traceability).",
    )

    frontmatter: FrontmatterRequirement = Field(default_factory=FrontmatterRequirement)
    outputs: OutputRequirement = Field(default_factory=OutputRequirement)
    stage_slots: list[StageSlot] = Field(default_factory=list)
    checkpoint_slots: list[CheckpointSlot] = Field(default_factory=list)
    gate_slots: list[GateSlot] = Field(default_factory=list)
    mode_semantics: ModeSemantics = Field(
        default_factory=lambda: ModeSemantics(semantic_type="none"),
    )
    evidence_contract: EvidenceContract | None = Field(default=None)
    delivery_contract: DeliveryContract | None = Field(default=None)
    directory: DirectoryRequirement = Field(default_factory=DirectoryRequirement)

    constitution_required: bool = Field(
        default=True,
        description="If True, skill must ship constitution.md.",
    )


__all__ = [
    "ArchetypeSpec",
    "CheckpointSlot",
    "DeliveryContract",
    "DirectoryRequirement",
    "EvidenceContract",
    "FrontmatterRequirement",
    "GateSlot",
    "ModeSemantics",
    "OutputRequirement",
    "StageSlot",
]
