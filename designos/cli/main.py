"""DesignOS CLI entry point (M1 placeholders).

Concrete command implementations land in milestone M1 (A6). This module
ships only the command surface so the ``designos`` console script wires
up correctly from day one.
"""

from __future__ import annotations

import typer

from designos import __version__

app: typer.Typer = typer.Typer(
    help="DesignOS — AI-native design capability suite.",
    no_args_is_help=True,
    add_completion=False,
)


@app.command()
def version() -> None:
    """Print DesignOS version."""

    typer.echo(f"DesignOS {__version__}")


@app.command()
def init(name: str) -> None:
    """Create a new DesignOS workspace (M1: A6)."""

    typer.echo(f"[TODO] init {name}")


@app.command()
def run(skill: str) -> None:
    """Execute a Skill against the current workspace (M1: A6)."""

    typer.echo(f"[TODO] run {skill}")


@app.command()
def resume() -> None:
    """Resume a paused Skill run from the latest checkpoint (M1: A6)."""

    typer.echo("[TODO] resume")


@app.command()
def config() -> None:
    """Open an interactive configuration wizard (M1: A6)."""

    typer.echo("[TODO] config")


@app.command()
def history() -> None:
    """List historical Skill runs (M1: A6)."""

    typer.echo("[TODO] history")


@app.command()
def preflight(skill: str) -> None:
    """Run preflight checks for a Skill without executing it (M1: A6)."""

    typer.echo(f"[TODO] preflight {skill}")


if __name__ == "__main__":  # pragma: no cover - module entry point
    app()
