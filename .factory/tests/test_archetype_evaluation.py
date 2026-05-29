"""Tests for the evaluation archetype yaml + loader.

Per CONTRACT §4 Gate 1, the manually-authored evaluation.yaml must:
- Parse cleanly through ArchetypeSpec
- Reference real kernel enums (no string literals that don't map)
- Cover all archetype dimensions listed in CONTRACT §7
"""

from __future__ import annotations

import sys
from pathlib import Path


def _add_factory_to_path() -> None:
    factory_dir = Path(__file__).resolve().parents[1]
    if str(factory_dir) not in sys.path:
        sys.path.insert(0, str(factory_dir))


def test_evaluation_archetype_loads() -> None:
    _add_factory_to_path()
    from archetypes import load_archetype

    spec = load_archetype("evaluation")
    assert spec.name == "evaluation"
    assert spec.representative_skill == "uxeval"
    assert spec.version


def test_evaluation_archetype_required_outputs_are_real_kernel_types() -> None:
    """Required outputs must be valid OutputType enum members."""
    _add_factory_to_path()
    from archetypes import load_archetype
    from kernel.contracts.enums import OutputType

    spec = load_archetype("evaluation")
    expected_required = {
        OutputType.ISSUE_REPORT,
        OutputType.HTML_REPORT,
        OutputType.EVIDENCE_PACK,
        OutputType.DELIVERY_AUDIT_BUNDLE,
    }
    assert set(spec.outputs.required) >= expected_required


def test_evaluation_archetype_covers_all_contract_section_7_dimensions() -> None:
    """CONTRACT §7 lists 9 dimensions. Each must be populated."""
    _add_factory_to_path()
    from archetypes import load_archetype

    spec = load_archetype("evaluation")
    # 1. frontmatter
    assert spec.frontmatter.required_keys
    # 2. outputs
    assert spec.outputs.required
    # 3. stage topology
    assert len(spec.stage_slots) >= 7  # uxeval has 7 core stages minimum
    # 4. checkpoint topology
    assert len(spec.checkpoint_slots) >= 3  # C1/C2/C3
    # 5. gate topology
    assert len(spec.gate_slots) >= 2  # at least QG2/QG3 required
    # 6. directory
    assert spec.directory.required_directories
    assert spec.directory.required_files
    # 7. evidence contract
    assert spec.evidence_contract is not None
    # 8. delivery contract
    assert spec.delivery_contract is not None
    # 9. mode semantics
    assert spec.mode_semantics.semantic_type == "evidence_collection"


def test_evaluation_archetype_required_checkpoints_are_uxeval_C1_C2_C3() -> None:
    _add_factory_to_path()
    from archetypes import load_archetype

    spec = load_archetype("evaluation")
    required_ids = {c.checkpoint_id for c in spec.checkpoint_slots if c.required}
    assert required_ids == {"C1", "C2", "C3"}


def test_evaluation_archetype_mode_semantics_is_evidence_collection() -> None:
    """uxeval / design-acceptance mode means how evidence is captured —
    NOT fidelity (prd2proto) or data source (ai-analytics)."""
    _add_factory_to_path()
    from archetypes import load_archetype

    spec = load_archetype("evaluation")
    assert spec.mode_semantics.semantic_type == "evidence_collection"
    assert set(spec.mode_semantics.allowed_modes) == {"web", "client"}


def test_load_archetype_raises_when_missing() -> None:
    _add_factory_to_path()
    from archetypes import load_archetype

    try:
        load_archetype("does-not-exist")
    except FileNotFoundError as exc:
        assert "does-not-exist" in str(exc)
        return
    raise AssertionError("expected FileNotFoundError")
