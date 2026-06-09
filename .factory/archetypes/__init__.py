"""Archetypes package — machine-readable specifications of skill families."""

from .archetype_schema import (
    ArchetypeSpec,
    CheckpointSlot,
    DeliveryContract,
    DirectoryRequirement,
    EvidenceContract,
    FrontmatterRequirement,
    GateSlot,
    ModeSemantics,
    OutputRequirement,
    StageSlot,
)
from .loader import load_archetype

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
    "load_archetype",
]
