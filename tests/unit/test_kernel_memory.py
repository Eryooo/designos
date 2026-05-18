"""Unit tests for kernel.memory."""

from __future__ import annotations

from pathlib import Path

import pytest

from kernel.errors import SanitizerError
from kernel.memory import (
    MemoryAdapter,
    OrganizationMemory,
    ProjectMemory,
    Sanitizer,
    SessionMemory,
)


def test_session_memory_read_write() -> None:
    sm = SessionMemory()
    assert sm.read("missing") is None
    sm.write("k", {"x": 1})
    assert sm.read("k") == {"x": 1}


def test_project_memory_persists_to_disk(tmp_path: Path) -> None:
    pm = ProjectMemory(tmp_path)
    pm.write("uxeval/run-001", {"answer": 42})
    assert pm.read("uxeval/run-001") == {"answer": 42}
    target = tmp_path / ".designos" / "memory" / "uxeval" / "run-001.json"
    assert target.exists()


def test_project_memory_rejects_invalid_keys(tmp_path: Path) -> None:
    pm = ProjectMemory(tmp_path)
    with pytest.raises(Exception):
        pm.write("", {})
    with pytest.raises(Exception):
        pm.write("/abs", {})


def test_sanitizer_detects_phone_email_url_keys() -> None:
    s = Sanitizer()
    payload = {
        "phone": "13900008888",
        "email": "user@example.com",
        "url": "https://wiki.internal/page",
        "key": "sk-ant-aaaaaaaaaaaaaaaaaaaa1234",
    }
    hits = s.scan(payload)
    labels = {hit.split(":", 1)[0] for hit in hits}
    assert "phone_cn" in labels
    assert "email" in labels
    assert "internal_url" in labels
    assert "anthropic_key" in labels


def test_sanitizer_clean_payload_passes() -> None:
    s = Sanitizer()
    assert s.scan({"summary": "no PII here"}) == []


def test_organization_memory_propose_blocks_pii(tmp_path: Path) -> None:
    om = OrganizationMemory(tmp_path)
    with pytest.raises(SanitizerError):
        om.propose("uxeval/golden", {"phone": "13800008888"})


def test_organization_memory_propose_writes_staging(tmp_path: Path) -> None:
    om = OrganizationMemory(tmp_path)
    url = om.propose("uxeval/golden", {"summary": "ok"})
    assert url.startswith("file://")
    staged = list((tmp_path / ".designos" / "memory" / "staging" / "uxeval" / "golden").glob("*.json"))
    assert len(staged) == 1


def test_memory_adapter_three_tier(tmp_path: Path) -> None:
    adapter = MemoryAdapter(tmp_path)
    adapter.write_session("s", "v")
    adapter.write_project("p", {"x": 1})
    assert adapter.read_session("s") == "v"
    assert adapter.read_project("p") == {"x": 1}
    assert adapter.search_organization("anything") == []
    url = adapter.propose_to_organization("uxeval/g", {"hello": "world"})
    assert "staging" in url
