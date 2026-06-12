"""Unit tests for frontmatter-driven preflight behavior."""

from __future__ import annotations

from pathlib import Path

import pytest
import yaml

from kernel.config import load_config
from kernel.contracts.enums import SkillType
from kernel.contracts.schemas import DesignOSConfig, GlobalConfig, SkillContext
from kernel.mcp.registry import MCPRegistry
import kernel.preflight.checker as checker_mod
from kernel.preflight.checker import PreflightChecker
from kernel.preflight.requirements import requirements_from_skill
from kernel.skill_loader import load_pipeline_skill


def _make_skill(root: Path, *, missing_command: str = "definitely-missing-command-12345 --version") -> Path:
    skill_dir = root / "demo-preflight"
    skill_dir.mkdir(parents=True, exist_ok=True)
    (skill_dir / "SKILL.md").write_text(
        "---\n"
        "name: demo-preflight\n"
        "version: 1.2.3\n"
        "type: pipeline\n"
        "requires:\n"
        "  kernel: \">=1.0.0,<2.0.0\"\n"
        "  mcp_servers:\n"
        "    - name: pdf-parser\n"
        "      builtin: true\n"
        "    - name: playwright-driver\n"
        "      builtin: false\n"
        "      required_when: 'mode == \"web\"'\n"
        "      requires_external:\n"
        f"        - command: \"{missing_command}\"\n"
        "          install_hint: \"Install Playwright before using web mode.\"\n"
        "modes:\n"
        "  - id: client\n"
        "  - id: web\n"
        "---\n"
        "# Demo preflight skill\n",
        encoding="utf-8",
    )
    (skill_dir / "pipeline.yaml").write_text(
        yaml.safe_dump(
            {
                "name": "demo-preflight-pipeline",
                "version": "1.2.3",
                "stages": [
                    {
                        "id": "noop",
                        "type": "composite",
                        "outputs": ["ok"],
                    }
                ],
            }
        ),
        encoding="utf-8",
    )
    return skill_dir


def _ctx(workspace: Path, *, mode: str | None) -> SkillContext:
    return SkillContext(
        workspace=workspace,
        skill_name="demo-preflight",
        skill_version="1.2.3",
        run_id="preflight-test",
        mode=mode,  # type: ignore[arg-type]
        config=DesignOSConfig(workspace=workspace, global_config=GlobalConfig()),
    )


def test_requirements_from_skill_use_parsed_frontmatter(tmp_path: Path) -> None:
    skill = load_pipeline_skill(_make_skill(tmp_path))

    requirements = requirements_from_skill(skill)

    assert len(requirements) == 1
    assert requirements[0].command == "definitely-missing-command-12345 --version"
    assert requirements[0].required_when == 'mode == "web"'
    assert requirements[0].server_name == "playwright-driver"


def test_load_config_carries_skill_config_into_registry(tmp_path: Path) -> None:
    skill = load_pipeline_skill(_make_skill(tmp_path))
    workspace = tmp_path / "ws"
    workspace.mkdir()

    cfg = load_config(workspace=workspace, skill_config=skill.config)
    registry = MCPRegistry(cfg.mcp_servers)

    assert cfg.skill_config is not None
    assert cfg.skill_config.version == "1.2.3"
    assert registry.names() == ["pdf-parser", "playwright-driver"]


@pytest.mark.asyncio
async def test_preflight_is_mode_specific_for_web_dependency(tmp_path: Path) -> None:
    skill = load_pipeline_skill(_make_skill(tmp_path))
    checker = PreflightChecker()
    workspace = tmp_path / "ws"
    workspace.mkdir()

    client_errors = await checker.check(skill, _ctx(workspace, mode="client"))
    web_errors = await checker.check(skill, _ctx(workspace, mode="web"))

    assert client_errors == []
    assert len(web_errors) == 1
    assert "definitely-missing-command-12345 --version" in web_errors[0]
    assert "Install Playwright before using web mode." in web_errors[0]


def test_loaded_skill_config_exposes_modes_and_mcp_servers(tmp_path: Path) -> None:
    skill = load_pipeline_skill(_make_skill(tmp_path))

    assert skill.name == "demo-preflight"
    assert skill.skill_type is SkillType.PIPELINE
    assert skill.config.version == "1.2.3"
    assert skill.config.supported_modes == ["client", "web"]
    assert [server.name for server in skill.config.mcp_servers] == ["pdf-parser", "playwright-driver"]


@pytest.mark.asyncio
async def test_uxeval_client_preflight_allows_markdown_fallback_without_ocr(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    repo_root = Path(__file__).resolve().parents[2]
    skill = load_pipeline_skill(repo_root / "skills" / "uxeval")
    checker = PreflightChecker(repo_root=repo_root)
    workspace = tmp_path / "ws"
    (workspace / "inputs").mkdir(parents=True)
    (workspace / "inputs" / "screens-description.md").write_text(
        "# 页面说明\n\n当前无 OCR，但提供了页面说明。",
        encoding="utf-8",
    )

    async def fake_probe(req, repo_root_arg):
        if req.server_name == "image-analyzer":
            return False
        return True

    monkeypatch.setattr(checker_mod, "_probe", fake_probe)

    errors = await checker.check(
        skill,
        SkillContext(
            workspace=workspace,
            skill_name="uxeval",
            skill_version="1.0.0",
            run_id="preflight-test",
            mode="client",
            config=DesignOSConfig(workspace=workspace, global_config=GlobalConfig()),
        ),
    )

    assert errors == []


@pytest.mark.asyncio
async def test_uxeval_client_preflight_fails_without_ocr_or_markdown_fallback(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    repo_root = Path(__file__).resolve().parents[2]
    skill = load_pipeline_skill(repo_root / "skills" / "uxeval")
    checker = PreflightChecker(repo_root=repo_root)
    workspace = tmp_path / "ws"
    workspace.mkdir(parents=True)

    async def fake_probe(req, repo_root_arg):
        if req.server_name == "image-analyzer":
            return False
        return True

    monkeypatch.setattr(checker_mod, "_probe", fake_probe)

    errors = await checker.check(
        skill,
        SkillContext(
            workspace=workspace,
            skill_name="uxeval",
            skill_version="1.0.0",
            run_id="preflight-test",
            mode="client",
            config=DesignOSConfig(workspace=workspace, global_config=GlobalConfig()),
        ),
    )

    assert len(errors) == 1
    assert "probe_ocr.py" in errors[0]
    assert "screens-description.md" in errors[0]
