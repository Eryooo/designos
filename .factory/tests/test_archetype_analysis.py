"""Tests for the analysis archetype yaml + loader.

F1.1 regression lock: after de-provisionalizing analysis.yaml from ai-analytics A1,
these tests ensure the archetype's pilot-reality constraints stay locked:
- version is 0.1.0-pilot (not provisional)
- data_collection.stage_type == llm (not tool)
- report_generation.stage_type == llm (not tool)

This prevents silent regression where YAML duplicate keys cause the parser to
revert to tool-type assumptions that don't match pilot reality.
"""

from __future__ import annotations

import sys
from pathlib import Path


def _add_factory_to_path() -> None:
    factory_dir = Path(__file__).resolve().parents[1]
    if str(factory_dir) not in sys.path:
        sys.path.insert(0, str(factory_dir))


def test_analysis_archetype_loads() -> None:
    _add_factory_to_path()
    from archetypes import load_archetype

    spec = load_archetype("analysis")
    assert spec.name == "analysis"
    assert spec.representative_skill == "ai-analytics"
    assert spec.version == "0.1.0-pilot", (
        "analysis archetype must be 0.1.0-pilot (de-provisionalized from ai-analytics A1)"
    )


def test_analysis_stage_slots_reflect_pilot_llm_synthesis() -> None:
    """data_collection / report_generation must be stage_type: llm in pilot.

    F1.1 regression lock: YAML duplicate keys caused report_generation to parse
    as tool despite the earlier llm declaration. This test ensures the real
    parsed result matches pilot reality (no real scraping/rendering tools).
    """
    _add_factory_to_path()
    from archetypes import load_archetype
    from kernel.contracts.enums import StageType

    spec = load_archetype("analysis")
    by_slot = {slot.slot_id: slot for slot in spec.stage_slots}

    # pilot reality: data_collection consumes user-provided material (LLM synthesis)
    assert by_slot["data_collection"].stage_type == StageType.LLM, (
        "data_collection must be LLM in pilot (no real scraping tool)"
    )

    # pilot reality: report_generation renders markdown (LLM synthesis)
    assert by_slot["report_generation"].stage_type == StageType.LLM, (
        "report_generation must be LLM in pilot (no real rendering tool)"
    )


def test_analysis_required_outputs_are_real_kernel_types() -> None:
    """Required outputs must be valid OutputType enum members."""
    _add_factory_to_path()
    from archetypes import load_archetype
    from kernel.contracts.enums import OutputType

    spec = load_archetype("analysis")
    expected_required = {
        OutputType.ANALYSIS_REPORT,
        OutputType.DESIGN_STRATEGY,
        OutputType.COMPARISON_MATRIX,
        OutputType.USER_PERSONA,
    }
    assert set(spec.outputs.required) == expected_required
