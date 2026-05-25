"""Unit tests for kernel.config."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml

from kernel.config import load_config, load_env_file
from kernel.contracts.enums import SkillType
from kernel.contracts.schemas import GlobalConfig, MCPServerConfig, SkillConfig


def test_env_loader_parses_basic_lines(tmp_path: Path) -> None:
    target = tmp_path / ".env.local"
    target.write_text(
        "\n".join(
            [
                "# comment",
                "FOO=bar",
                'BAZ="hello world"',
                "export QUUX='single quoted'",
                "EMPTY=",
                "INLINE=value # trailing",
            ]
        ),
        encoding="utf-8",
    )
    parsed = load_env_file(target)
    assert parsed["FOO"] == "bar"
    assert parsed["BAZ"] == "hello world"
    assert parsed["QUUX"] == "single quoted"
    assert parsed["EMPTY"] == ""
    assert parsed["INLINE"] == "value"


def test_env_loader_missing_file_returns_empty(tmp_path: Path) -> None:
    assert load_env_file(tmp_path / "absent") == {}


def test_load_config_layers_priority(tmp_path: Path, monkeypatch: Any) -> None:
    workspace: Path = tmp_path / "ws"
    workspace.mkdir()
    user_cfg: Path = tmp_path / "user.yaml"
    user_cfg.write_text(
        yaml.safe_dump({"primary_model": "user-claude", "fallback_model": "user-fallback"}),
        encoding="utf-8",
    )
    project_cfg: Path = workspace / "designos.project.yaml"
    project_cfg.write_text(
        yaml.safe_dump(
            {"name": "proj", "created": "2026-05-18T00:00:00+00:00", "owner": "young"}
        ),
        encoding="utf-8",
    )
    skill = SkillConfig(
        name="uxeval",
        version="1.0.0",
        skill_type=SkillType.PIPELINE,
        mcp_servers=[MCPServerConfig(name="pdf-parser")],
    )

    cfg = load_config(workspace=workspace, user_config_path=user_cfg, skill_config=skill)
    assert isinstance(cfg.global_config, GlobalConfig)
    assert cfg.global_config.primary_model == "user-claude"
    assert cfg.project_config is not None
    assert cfg.project_config.name == "proj"
    assert cfg.skill_config is not None
    assert cfg.skill_config.version == "1.0.0"
    assert "pdf-parser" in cfg.mcp_servers

    # CLI override wins.
    cfg2 = load_config(
        workspace=workspace,
        user_config_path=user_cfg,
        skill_config=skill,
        cli_overrides={"global_config": GlobalConfig(primary_model="cli-claude")},
    )
    assert cfg2.global_config.primary_model == "cli-claude"


def test_env_local_applied(tmp_path: Path, monkeypatch: Any) -> None:
    workspace: Path = tmp_path / "ws"
    workspace.mkdir()
    (workspace / ".env.local").write_text("DESIGNOS_TEST_VAR=hello\n", encoding="utf-8")
    monkeypatch.delenv("DESIGNOS_TEST_VAR", raising=False)
    cfg = load_config(workspace=workspace, user_config_path=tmp_path / "absent.yaml")
    assert cfg.env.get("DESIGNOS_TEST_VAR") == "hello"
