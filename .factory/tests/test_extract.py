"""Tests for tools.extract — reverse-extracting archetype specs from skills.

Per CONTRACT §5.2, Agent A must deliver:
1. extract.py that produces valid ArchetypeSpec instances
2. Round-trip test: extract(uxeval) matches hand-written evaluation.yaml >= 90%
3. Auto-detection test: archetype is inferred from outputs when --archetype omitted
4. YAML serialization test: output can be written to a file
5. Warning test: heuristic fields emit warnings to stderr
6. Error test: invalid skill directories produce actionable error messages
"""

from __future__ import annotations

import sys
from io import StringIO
from pathlib import Path

import pytest


def _add_factory_to_path() -> None:
    factory_dir = Path(__file__).resolve().parents[1]
    if str(factory_dir) not in sys.path:
        sys.path.insert(0, str(factory_dir))


def test_extract_uxeval_produces_valid_archetype_spec() -> None:
    """Extract uxeval and validate the result through ArchetypeSpec."""
    _add_factory_to_path()
    from archetypes.archetype_schema import ArchetypeSpec
    from tools.extract import extract

    repo_root = Path(__file__).resolve().parents[2]
    uxeval_dir = repo_root / "skills" / "uxeval"

    spec = extract(uxeval_dir, archetype="evaluation")
    assert isinstance(spec, ArchetypeSpec)
    assert spec.name == "evaluation"
    assert spec.representative_skill == "uxeval"


def test_extract_uxeval_matches_handwritten_evaluation_yaml() -> None:
    """Extract uxeval and compare to the hand-written evaluation.yaml.

    Per CONTRACT §4 Gate 1, the extracted spec must be >= 90% consistent
    with the hand-written archetype on key fields:
    - name = evaluation
    - mode_semantics.semantic_type = evidence_collection
    - at least 6 stage_slots
    - at least 3 checkpoint_slots
    """
    _add_factory_to_path()
    from archetypes import load_archetype
    from tools.extract import extract

    repo_root = Path(__file__).resolve().parents[2]
    uxeval_dir = repo_root / "skills" / "uxeval"

    extracted = extract(uxeval_dir, archetype="evaluation")
    reference = load_archetype("evaluation")

    # Must-match fields
    assert extracted.name == reference.name == "evaluation"
    assert extracted.mode_semantics.semantic_type == reference.mode_semantics.semantic_type
    assert extracted.mode_semantics.semantic_type == "evidence_collection"

    # Topology consistency
    assert len(extracted.stage_slots) >= 6, "evaluation archetype requires >= 6 stage slots"
    assert len(extracted.checkpoint_slots) >= 3, "evaluation archetype requires >= 3 checkpoints"

    # Checkpoint IDs must match
    extracted_cp_ids = {c.checkpoint_id for c in extracted.checkpoint_slots}
    reference_cp_ids = {c.checkpoint_id for c in reference.checkpoint_slots if c.required}
    assert extracted_cp_ids >= reference_cp_ids, (
        f"extracted checkpoints {extracted_cp_ids} missing required {reference_cp_ids}"
    )

    # Required outputs must be present
    extracted_outputs = {o.value for o in extracted.outputs.required}
    reference_outputs = {o.value for o in reference.outputs.required}
    assert extracted_outputs >= reference_outputs, (
        f"extracted outputs {extracted_outputs} missing required {reference_outputs}"
    )

    # Evidence contract must exist for evaluation
    assert extracted.evidence_contract is not None
    assert reference.evidence_contract is not None

    # Delivery contract must exist for evaluation
    assert extracted.delivery_contract is not None
    assert reference.delivery_contract is not None

    # Constitution required
    assert extracted.constitution_required is True


def test_extract_auto_detects_evaluation_archetype() -> None:
    """When --archetype is omitted, extract infers 'evaluation' from outputs."""
    _add_factory_to_path()
    from tools.extract import extract

    repo_root = Path(__file__).resolve().parents[2]
    uxeval_dir = repo_root / "skills" / "uxeval"

    # Do NOT pass archetype= — let it auto-detect.
    spec = extract(uxeval_dir)
    assert spec.name == "evaluation"


def test_extract_writes_yaml_when_output_specified(tmp_path: Path) -> None:
    """Extract can serialize to a file via --output."""
    _add_factory_to_path()
    from tools.extract import extract, spec_to_yaml

    repo_root = Path(__file__).resolve().parents[2]
    uxeval_dir = repo_root / "skills" / "uxeval"

    spec = extract(uxeval_dir, archetype="evaluation")
    yaml_text = spec_to_yaml(spec)

    out_file = tmp_path / "extracted.yaml"
    out_file.write_text(yaml_text, encoding="utf-8")

    assert out_file.exists()
    assert "name: evaluation" in out_file.read_text(encoding="utf-8")


def test_extract_warns_on_guessed_fields() -> None:
    """Heuristic fields (mode_semantics, unmapped stages) emit warnings."""
    _add_factory_to_path()
    from tools.extract import extract

    repo_root = Path(__file__).resolve().parents[2]
    uxeval_dir = repo_root / "skills" / "uxeval"

    warn_stream = StringIO()
    spec = extract(uxeval_dir, archetype="evaluation", warn_stream=warn_stream)
    assert spec.name == "evaluation"

    warnings = warn_stream.getvalue()
    # uxeval has stages that don't map to the canonical 9 slots (e.g.
    # prd-screenshot-conflict, task-script-generation). Extract should warn.
    assert "[warn]" in warnings or len(warnings) > 0, (
        "expected at least one warning for unmapped stages or heuristic fields"
    )


def test_extract_fails_with_actionable_error_when_skill_dir_invalid() -> None:
    """Invalid skill directories produce actionable error messages."""
    _add_factory_to_path()
    from tools.extract import ExtractError, extract

    repo_root = Path(__file__).resolve().parents[2]
    missing_dir = repo_root / "skills" / "does-not-exist"

    with pytest.raises(ExtractError) as exc_info:
        extract(missing_dir)

    error_text = str(exc_info.value)
    # Per CONTRACT §3.E, error messages must be actionable (>= 90%).
    # Check for fix hints (lines starting with "  ->").
    assert "->" in error_text, "error message must contain actionable hints"
    assert "not found" in error_text.lower() or "missing" in error_text.lower()


def test_extract_fails_when_skill_md_missing(tmp_path: Path) -> None:
    """Extract errors when SKILL.md is missing."""
    _add_factory_to_path()
    from tools.extract import ExtractError, extract

    empty_dir = tmp_path / "empty-skill"
    empty_dir.mkdir()

    with pytest.raises(ExtractError) as exc_info:
        extract(empty_dir)

    error_text = str(exc_info.value)
    assert "SKILL.md" in error_text
    assert "->" in error_text


def test_extract_fails_when_pipeline_yaml_missing(tmp_path: Path) -> None:
    """Extract errors when pipeline.yaml is missing."""
    _add_factory_to_path()
    from tools.extract import ExtractError, extract

    skill_dir = tmp_path / "incomplete-skill"
    skill_dir.mkdir()
    (skill_dir / "SKILL.md").write_text(
        "---\nname: test\nversion: 1.0.0\ntype: pipeline\nrequires:\n  kernel: '>=1.0.0'\noutputs: []\n---\n",
        encoding="utf-8",
    )

    with pytest.raises(ExtractError) as exc_info:
        extract(skill_dir)

    error_text = str(exc_info.value)
    assert "pipeline.yaml" in error_text
    assert "->" in error_text


def test_extract_roundtrip_through_archetype_spec() -> None:
    """Extract → serialize → deserialize → validate round-trips cleanly."""
    _add_factory_to_path()
    from archetypes.archetype_schema import ArchetypeSpec
    from tools.extract import extract, spec_to_yaml

    repo_root = Path(__file__).resolve().parents[2]
    uxeval_dir = repo_root / "skills" / "uxeval"

    spec1 = extract(uxeval_dir, archetype="evaluation")
    yaml_text = spec_to_yaml(spec1)

    import yaml

    raw = yaml.safe_load(yaml_text)
    spec2 = ArchetypeSpec.model_validate(raw)

    # Key fields must survive the round-trip.
    assert spec2.name == spec1.name
    assert spec2.representative_skill == spec1.representative_skill
    assert len(spec2.stage_slots) == len(spec1.stage_slots)
    assert len(spec2.checkpoint_slots) == len(spec1.checkpoint_slots)


def test_extract_cli_main_writes_to_stdout(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """CLI main() writes YAML to stdout when --output is omitted."""
    _add_factory_to_path()
    from tools.extract import main

    repo_root = Path(__file__).resolve().parents[2]
    uxeval_dir = repo_root / "skills" / "uxeval"

    stdout_capture = StringIO()
    monkeypatch.setattr(sys, "stdout", stdout_capture)

    exit_code = main([str(uxeval_dir), "--archetype", "evaluation"])
    assert exit_code == 0

    output = stdout_capture.getvalue()
    assert "name: evaluation" in output
    assert "representative_skill: uxeval" in output


def test_extract_cli_main_writes_to_file(tmp_path: Path) -> None:
    """CLI main() writes YAML to a file when --output is specified."""
    _add_factory_to_path()
    from tools.extract import main

    repo_root = Path(__file__).resolve().parents[2]
    uxeval_dir = repo_root / "skills" / "uxeval"
    out_file = tmp_path / "extracted.yaml"

    exit_code = main([str(uxeval_dir), "--archetype", "evaluation", "--output", str(out_file)])
    assert exit_code == 0
    assert out_file.exists()
    assert "name: evaluation" in out_file.read_text(encoding="utf-8")


def test_extract_cli_main_returns_error_code_on_failure(tmp_path: Path) -> None:
    """CLI main() returns non-zero exit code when extraction fails."""
    _add_factory_to_path()
    from tools.extract import main

    missing_dir = tmp_path / "does-not-exist"

    exit_code = main([str(missing_dir)])
    assert exit_code != 0


__all__ = [
    "test_extract_auto_detects_evaluation_archetype",
    "test_extract_cli_main_returns_error_code_on_failure",
    "test_extract_cli_main_writes_to_file",
    "test_extract_cli_main_writes_to_stdout",
    "test_extract_fails_when_pipeline_yaml_missing",
    "test_extract_fails_when_skill_md_missing",
    "test_extract_fails_with_actionable_error_when_skill_dir_invalid",
    "test_extract_roundtrip_through_archetype_spec",
    "test_extract_uxeval_matches_handwritten_evaluation_yaml",
    "test_extract_uxeval_produces_valid_archetype_spec",
    "test_extract_warns_on_guessed_fields",
    "test_extract_writes_yaml_when_output_specified",
]
