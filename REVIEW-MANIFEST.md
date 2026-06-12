# DesignOS Clean Snapshot — REVIEW MANIFEST

**快照日期**: 2026-06-11
**来源 commit**: `24459da` (feature/senior-designer-paradigm-engine)
**生成方式**: `git archive HEAD`（仅导出 git 已跟踪文件）
**文件总数**: 778（git-tracked）

---

## 1. 这是什么

DesignOS 的一个**干净内部试用快照**，从当前已脱敏的 HEAD 导出，
**不包含任何旧 git 历史**。用于新建干净私有仓库 / 内部试用，
不用于对外发布。

---

## 2. 适用范围（务必阅读）

- ✅ **internal pilot only** — 仅供集团内部试用
- ❌ **not public release** — 非公开发布版本
- ❌ **not enterprise-ready** — 未达到企业级就绪
- ❌ **not all-skills senior-level** — 并非全 skills 达到资深水准
- ❌ **do not redistribute** — 不得对外分发

---

## 3. 目标口径（重要）

- **prd2proto 是当前推进最深的 seniorization pilot**（资深化样板），
  但仍未 fully validated。
- **DesignOS 的最终目标是全 skills 达到资深设计师级能力**
  （prd2proto / uxeval / ai-analytics / ip-design / brand-creative），
  目前仍在推进中。
- 其他 skills 尚未达到 senior-level。
- **不得宣称"所有 skills 已达资深设计师水准"或"enterprise-ready"。**

### 权威状态源（判断当前状态只看这些）
- `INTERNAL-PILOT-README.md` — 试用状态入口
- `REVIEW-MANIFEST.md` — 本文件
- `skills/status.matrix.yaml` — 逐 skill 五层 readiness
  （全部 `validated: false` / `enterprise_ready: false`）
- `docs/STATUS-DEFINITION.md` — 五层 readiness 口径定义，禁止跳级推导

### 注意：docs/archive/ 是历史快照，不代表当前状态
旧里程碑报告（COMPLETION_REPORT / FINAL_STATUS / P0_* /
ULTIMATE_GOAL_ASSESSMENT 等）已移入 `docs/archive/` 并标记 OUTDATED，
**不要据此判断当前状态**。

---

## 4. 安全 / 脱敏 / 口径状态

| 项 | 状态 |
|----|------|
| S0-1 治理机制 + 质量门 | ✅ 完成 |
| S0-2 当前 HEAD 证据污染清零 | ✅ 完成 |
| S0-3 prompts-v2 运行时 prompt 卫生 | ✅ 完成 |
| 扫描工具中文名漏扫缺陷修复 + 2 处漏掉的真实污染补脱敏 | ✅ 完成 |
| 内部试用口径治理（归档历史报告 + 校准 README） | ✅ 完成 |
| 公网包引用占位符化 + 禁用公网 npm 自动发布 | ✅ 完成 |
| 全量敏感扫描（覆盖全部文件，含中文名） | ✅ **0 命中** |

### 本快照不包含
- ❌ 旧 git 历史（`.git/`）
- ❌ 私有证据目录（`.designos-private-evidence/`）
- ❌ sensitive-words 私有词表
- ❌ input-prd / outputs / run.log / pipeline-full-result
- ❌ npm-package 镜像目录
- ❌ 真实 PRD / 真实业务案例 / 真实品牌词 / 真实凭证

### 重要说明：以下仍 pending
- **旧仓库历史清理**：旧仓库（origin）git 历史仍含污染，
  filter-repo / force push / GitHub Support 清缓存 pending。
  本快照适合"打包 / 新建干净仓库"试用，**不适合给旧仓库 clone 权限**。
- **npm 旧包**：旧 `designos@0.6.2` 可能已发公网，需 unpublish / deprecate。
  新包应走 scoped / private / 内部 registry。公网自动发布 workflow 已禁用。
- **暴露过的旧 PAT**：push 前请先撤销，用 `gh auth login` / SSH。

---

## 5. 测试结果（来源 commit 24459da）

| skill | 结果 |
|-------|------|
| prd2proto | 65 passed / 8 failed |
| ip-design | 21 passed |
| brand-creative | 99 passed |
| uxeval（单独跑） | 41 passed |

### 已知失败项（与脱敏/卫生/口径治理无关）
prd2proto 的 8 个失败是**既有的 pipeline 结构问题**，与本轮改动无关：
- `test_p1_smoke.py`（5 个）：pipeline stage 结构（dsl-fetch 等）
- `test_reality_hardening.py`（3 个）：`完全自动化` 措辞 / pipeline gate 结构

### 测试基础设施已知问题
`pytest skills/`（全量一起跑）会有 collection error（各 skill conftest
路径冲突）；分 skill 单独跑均正常。

---

## 6. 后续路线（不在本快照范围，均 pending）

```
✅ S0-1/S0-2/S0-3 + 扫描修复 + 口径治理 + 公网引用清理（当前 HEAD 已干净）
→ ⏳ 旧仓库历史清理（filter-repo / force push / GitHub Support 清缓存）
→ ⏳ npm 旧包处理（unpublish / deprecate v0.6.2）+ 新包 scoped/private
→ ⏳ S1: All-skills Senior Capability Standardization（全 skills 资深化标准）
→ ⏳ S2-S7: 逐 skill 升级 + synthetic golden cases + senior review rubric
            + 统一 status matrix
```

---

## 7. 是否可用于新 private repo 的 initial commit

✅ **可以。** 本快照敏感扫描 0 命中、无旧 git 历史、无私有证据、
口径一致（internal pilot / 非公开 / 非全 skills 资深 / 不发公网包）。
用 `NEW-REPO-INIT.sh` 在新 private 仓库做单 commit 起步。

**push 前提醒**：先撤销此前暴露的旧 PAT，用 `gh auth login` 或 SSH，
不要把 token 放进 remote URL。

---

**本 manifest 随快照分发，阅读后请遵守第 2 节适用范围。**
