"""DesignOS — AI-native design capability suite."""

from pathlib import Path

__version__ = "0.6.2"


def bundled_resource_path(*parts: str) -> Path:
    """Locate a resource bundled with the designos package.

    Examples:
        bundled_resource_path("skills", "uxeval", "SKILL.md")
        bundled_resource_path("AGENTS.md")
    """
    pkg_root = Path(__file__).parent
    bundled = pkg_root / "_bundled"
    if bundled.exists():
        return bundled.joinpath(*parts)
    # Dev mode fallback: walk up to repo root
    for parent in pkg_root.parents:
        if (parent / "skills").is_dir() and (parent / "AGENTS.md").exists():
            return parent.joinpath(*parts)
    raise FileNotFoundError(f"bundled resource not found: {parts}")
