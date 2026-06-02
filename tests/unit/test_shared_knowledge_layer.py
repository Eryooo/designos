"""共享知识层（knowledge/）结构测试 — Batch K0 baseline lock。

锁定 DesignOS 共享知识资产层的架构基线契约：
- knowledge/manifest.yaml 存在且可解析
- design/ux/product/frontend/research 五个 domain 都被 manifest 覆盖
  （声明了，且每个 domain 至少有一个资产挂在下面）
- 每个资产有 stable id：非空、全局唯一、形如 ``<domain>.<slug>`` 且 domain 前缀一致
- 每个资产必填字段齐全，source_of_truth 指向的文件真实存在
- 通用资产正文（各 domain 下的 .md）不含任何 skill 专属词 —— 共享层只放通用知识，
  "谁在用"只记录在 manifest 的 applicable_skills 里，不写进通用正文。

这些断言基于真实解析结果（解析 yaml + 读文件），不是对文本的字符串匹配，
避免"测试绿但共享层语义没守住"。
"""

from __future__ import annotations

import re
from pathlib import Path

import pytest
import yaml

pytestmark = pytest.mark.unit

_REPO_ROOT: Path = Path(__file__).resolve().parents[2]
_KNOWLEDGE: Path = _REPO_ROOT / "knowledge"
_MANIFEST: Path = _KNOWLEDGE / "manifest.yaml"

# 共享层必须覆盖的五个领域
_EXPECTED_DOMAINS = {"design", "ux", "product", "frontend", "research"}

# skill 专属词：禁止出现在通用资产正文里（manifest 的 applicable_skills 不在此约束内）
_SKILL_SPECIFIC_TERMS = ("uxeval", "prd2proto", "ai-analytics", "design-acceptance")

# 资产必填字段
_REQUIRED_ASSET_FIELDS = (
    "id",
    "version",
    "domain",
    "type",
    "applicable_skills",
    "source_of_truth",
    "decision_use",
    "quality_bar",
    "do_not_claim",
    "owner",
    "status",
)

_ID_PATTERN = re.compile(r"^[a-z]+\.[a-z0-9-]+$")
_VALID_STATUS = {"draft", "pilot", "stable"}


def _load_manifest() -> dict:
    assert _MANIFEST.is_file(), f"共享层 manifest 缺失: {_MANIFEST}"
    data = yaml.safe_load(_MANIFEST.read_text(encoding="utf-8"))
    assert isinstance(data, dict), "manifest 顶层必须是 mapping"
    return data


def test_manifest_exists_and_parses() -> None:
    """knowledge/manifest.yaml 存在且能被解析为 mapping。"""
    data = _load_manifest()
    assert data.get("layer") == "shared-knowledge"
    assert isinstance(data.get("assets"), list) and data["assets"], "assets 必须是非空列表"


def test_five_domains_declared_in_manifest() -> None:
    """manifest 的 domains 字段必须恰好声明五个预期领域。"""
    data = _load_manifest()
    declared = set(data.get("domains") or [])
    assert declared == _EXPECTED_DOMAINS, (
        f"domains 声明应为 {_EXPECTED_DOMAINS}，实际 {declared}"
    )


def test_every_domain_has_at_least_one_asset() -> None:
    """五个 domain 每个都被至少一个资产覆盖（不是只在 domains 列表里挂个名）。"""
    data = _load_manifest()
    covered = {asset["domain"] for asset in data["assets"]}
    missing = _EXPECTED_DOMAINS - covered
    assert not missing, f"以下 domain 在 manifest 中没有任何资产覆盖: {missing}"


def test_every_asset_has_stable_unique_id() -> None:
    """每个资产有 stable id：非空、唯一、形如 <domain>.<slug> 且前缀与 domain 一致。"""
    data = _load_manifest()
    seen: set[str] = set()
    for asset in data["assets"]:
        aid = asset.get("id")
        assert aid, f"资产缺少 id: {asset}"
        assert _ID_PATTERN.match(aid), f"id 不符合 <domain>.<slug> 规范: {aid}"
        assert aid not in seen, f"id 重复，不唯一: {aid}"
        seen.add(aid)
        prefix = aid.split(".", 1)[0]
        assert prefix == asset.get("domain"), (
            f"id 前缀 {prefix} 与 domain {asset.get('domain')} 不一致: {aid}"
        )


def test_every_asset_has_required_fields() -> None:
    """每个资产必填字段齐全，domain 合法，status 合法，applicable_skills 是已登记 skill。"""
    data = _load_manifest()
    known_skills = set(data.get("known_skills") or [])
    for asset in data["assets"]:
        for field in _REQUIRED_ASSET_FIELDS:
            assert field in asset and asset[field] not in (None, "", []), (
                f"资产 {asset.get('id')} 缺少字段或为空: {field}"
            )
        assert asset["domain"] in _EXPECTED_DOMAINS, (
            f"资产 {asset['id']} 的 domain 非法: {asset['domain']}"
        )
        assert asset["status"] in _VALID_STATUS, (
            f"资产 {asset['id']} 的 status 非法: {asset['status']}"
        )
        for skill in asset["applicable_skills"]:
            assert skill in known_skills, (
                f"资产 {asset['id']} 引用了未登记的 skill: {skill}"
            )


def test_source_of_truth_files_exist() -> None:
    """每个资产的 source_of_truth 指向的文件真实存在。"""
    data = _load_manifest()
    for asset in data["assets"]:
        target = _REPO_ROOT / asset["source_of_truth"]
        assert target.is_file(), (
            f"资产 {asset['id']} 的 source_of_truth 文件不存在: {asset['source_of_truth']}"
        )


def test_generic_asset_bodies_have_no_skill_specific_terms() -> None:
    """通用资产正文不得出现 skill 专属词。

    共享层只放通用知识——把正文里所有 skill 名删掉后它仍应完整成立。
    "谁在用"只记录在 manifest 的 applicable_skills，不写进通用正文。
    这是防止"把旧知识库原样搬迁成共享库"的结构红线。
    """
    offenders: list[str] = []
    for domain in _EXPECTED_DOMAINS:
        for md in (_KNOWLEDGE / domain).glob("*.md"):
            text = md.read_text(encoding="utf-8").lower()
            for term in _SKILL_SPECIFIC_TERMS:
                if term in text:
                    offenders.append(f"{md.relative_to(_REPO_ROOT)} 含专属词 '{term}'")
    assert not offenders, "通用资产正文出现 skill 专属词:\n" + "\n".join(offenders)


def test_manifest_assets_match_domain_directories() -> None:
    """manifest 声明的每个 domain 都有对应目录，且 source_of_truth 落在该 domain 目录下。"""
    data = _load_manifest()
    for domain in _EXPECTED_DOMAINS:
        assert (_KNOWLEDGE / domain).is_dir(), f"缺少 domain 目录: knowledge/{domain}"
    for asset in data["assets"]:
        sot = asset["source_of_truth"]
        assert sot.startswith(f"knowledge/{asset['domain']}/"), (
            f"资产 {asset['id']} 的 source_of_truth 未落在其 domain 目录下: {sot}"
        )

