"""Pydantic schemas for frontend-codegen tool I/O.

These schemas define the contract between prd2proto pipeline stages and the
frontend-codegen MCP server. They are stable across the mock and real
implementations: when the real implementation lands in P3, only the *body*
of core functions changes; consumers (pipeline stages, downstream code)
keep working unchanged.
"""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

# ---------------------------------------------------------------------------
# DSL fetch
# ---------------------------------------------------------------------------


class DSLFetchRequest(BaseModel):
    """Input for fetching DSL from Figma or MasterGo."""

    model_config = ConfigDict(frozen=True)

    source: Literal["figma", "mastergo"] = Field(
        ...,
        description="Which DSL source to fetch from.",
    )
    file_id: str = Field(
        ...,
        description="Source-specific file/project identifier.",
    )
    access_token: str | None = Field(
        default=None,
        description="Optional access token. Real impl will require it.",
    )


class DSLNode(BaseModel):
    """One node in the standardized DSL tree.

    Both Figma and MasterGo flatten into this shape so downstream stages do
    not branch on source.
    """

    id: str
    type: str = Field(..., description="Node type (Frame / Text / Group / Component / etc).")
    name: str
    children: list["DSLNode"] = Field(default_factory=list)
    properties: dict[str, str | int | float | bool] = Field(
        default_factory=dict,
        description="Visual props (fill / fontSize / padding / radius...). Mock returns example data.",
    )


DSLNode.model_rebuild()


class DSLFetchResponse(BaseModel):
    """Standardized DSL tree returned by fetch_dsl."""

    source: Literal["figma", "mastergo"]
    file_id: str
    root: DSLNode
    is_mock: bool = Field(
        default=True,
        description="Mock impl always sets True. Real impl will set False.",
    )


# ---------------------------------------------------------------------------
# Token extraction
# ---------------------------------------------------------------------------


class ExtractTokensRequest(BaseModel):
    """Input for token extraction."""

    model_config = ConfigDict(frozen=True)

    dsl: DSLFetchResponse
    design_md_path: str | None = Field(
        default=None,
        description="Optional path to design-spec.md / Design.md (team conventions).",
    )


class DesignTokens(BaseModel):
    """W3C-style Design Tokens output."""

    colors: dict[str, str] = Field(default_factory=dict)
    typography: dict[str, dict[str, str | int]] = Field(default_factory=dict)
    spacing: dict[str, str] = Field(default_factory=dict)
    radius: dict[str, str] = Field(default_factory=dict)
    shadow: dict[str, str] = Field(default_factory=dict)


class ExtractTokensResponse(BaseModel):
    tokens: DesignTokens
    is_mock: bool = True


# ---------------------------------------------------------------------------
# Component mapping
# ---------------------------------------------------------------------------


class MapComponentsRequest(BaseModel):
    """Input for component library mapping."""

    model_config = ConfigDict(frozen=True)

    dsl: DSLFetchResponse
    component_lib: Literal["antd-vue", "element-plus", "antd-react", "custom"] = Field(
        ...,
        description="Target component library identifier.",
    )


class ComponentMapping(BaseModel):
    """Map of DSL node id -> component library component name."""

    mappings: dict[str, str] = Field(default_factory=dict)
    unmapped_node_ids: list[str] = Field(default_factory=list)
    coverage_rate: float = Field(
        ge=0.0,
        le=1.0,
        description="Fraction of nodes successfully mapped.",
    )


class MapComponentsResponse(BaseModel):
    mapping: ComponentMapping
    is_mock: bool = True


# ---------------------------------------------------------------------------
# Code generation
# ---------------------------------------------------------------------------


class GenerateCodeRequest(BaseModel):
    """Input for code generation."""

    model_config = ConfigDict(frozen=True)

    mode: Literal["pm", "designer-spec", "designer-dsl"] = Field(
        ...,
        description="Fidelity tier.",
    )
    dsl: DSLFetchResponse | None = Field(
        default=None,
        description="Required for designer-dsl; ignored for pm.",
    )
    tokens: DesignTokens | None = Field(
        default=None,
        description="Required for designer-spec/dsl; ignored for pm.",
    )
    component_mapping: ComponentMapping | None = Field(
        default=None,
        description="Required for designer-dsl.",
    )
    framework: Literal["react", "vue"] = Field(
        default="react",
        description="Target framework.",
    )
    output_dir: str = Field(
        ...,
        description="Where to write the generated project.",
    )


class GenerateCodeResponse(BaseModel):
    """Result of code generation."""

    output_dir: str
    files_written: list[str]
    framework: Literal["react", "vue"]
    mode: Literal["pm", "designer-spec", "designer-dsl"]
    is_mock: bool = True
    next_steps: list[str] = Field(
        default_factory=list,
        description="Human-readable next steps (e.g. 'cd <dir> && npm install').",
    )


__all__ = [
    "ComponentMapping",
    "DesignTokens",
    "DSLFetchRequest",
    "DSLFetchResponse",
    "DSLNode",
    "ExtractTokensRequest",
    "ExtractTokensResponse",
    "GenerateCodeRequest",
    "GenerateCodeResponse",
    "MapComponentsRequest",
    "MapComponentsResponse",
]
