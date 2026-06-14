# S1-0B Execution Prompt — Source-of-Truth Decision + Declared-vs-Implemented Audit

> Owner: Codex planning / Claude Code execution  
> Repo: `/Users/young/Documents/Codex/Agent-design-webmode`  
> Branch: `feature/senior-designer-paradigm-engine`  
> Status: execute only after S1-0A is reviewed and committed locally  
> Scope: governance / audit / source-of-truth calibration only; no runtime feature development

---

## 1. Current Path

The current release path is no longer "push MVP immediately". It is:

1. **S0 security cleanup**: sanitize sensitive evidence, disable public publishing wording, fix scan-sensitive coverage.
2. **S1-0A existing foundation inventory**: prove DesignOS already has most unified foundations; prevent duplicate standard/kernel/validator creation.
3. **S1-0B source-of-truth and coverage audit**: decide which existing source is authoritative, and audit declared-vs-implemented coverage for five skills.
4. **S1-0C minimal calibration**: only after audit, patch stale status/readiness wording and add missing coverage fields if needed.
5. **MVP trial freeze**: only after security + governance + coverage baseline is clean.

Do not jump to runtime fixes, public release, npm publish, or main merge in S1-0B.

---

## 2. S1-0B Goals

S1-0B has two P0 goals:

### Goal A — Decide standard source-of-truth

Clarify the relationship between:

- `knowledge/manifest.yaml`: shared-knowledge active asset manifest, currently referenced by skills.
- `knowledge/design-work-paradigm/manifest.yaml`: Senior Designer Work Paradigm manifest, currently a methodology engine with numbered methods.
- `knowledge/design-work-paradigm/*.md`: method files. Note: current manifest registers 20 methods (`00`-`19`), while the directory contains 40 method markdown files excluding README. This mismatch is itself an audit finding.

Expected decision:

- Do not create a third standard.
- Prefer `knowledge/manifest.yaml` as the **active skill integration source**, because existing skills actually reference it.
- Treat `knowledge/design-work-paradigm/` as the **methodology library / rationale layer**, not the active skill integration contract, unless evidence proves otherwise.
- Produce an explicit A-to-B mapping proposal, but do not force all mappings to be complete in this batch.

### Goal B — Audit declared vs implemented coverage

For these five skills:

- `skills/uxeval`
- `skills/prd2proto`
- `skills/ai-analytics`
- `skills/ip-design`
- `skills/brand-creative`

Audit, with evidence:

- Which shared knowledge assets are declared in each `knowledge-manifest.yaml`.
- Which declared assets are actually consumed in `pipeline.yaml`, prompts, reference files, runtime, schemas, or tests.
- Which pipeline gates are declared:
  - `prd2proto` uses `quality_gates:` and has runtime code executing `kernel/quality-gates`.
  - `uxeval`, `ai-analytics`, and `ip-design` use pipeline `gate:` pause semantics. Do not call these "kernel quality gates" unless runtime execution is proven.
  - `brand-creative` is a group skill and may not have a root `pipeline.yaml`.
- Which artifact schemas inherit or reference `kernel/contracts/artifacts/artifact-base.schema.json`.
- Whether each skill's `status.matrix.yaml` maturity and blockers match actual implementation.

---

## 3. Non-Goals

Do not do any of the following:

- Do not create `SENIOR-CAPABILITY-STANDARD.md`.
- Do not create `SENIOR-DESIGN-METHODOLOGY-KERNEL.md`.
- Do not create `kernel/seniorcap/*`.
- Do not create `skill-capability.schema.json`.
- Do not create five new `capability.yaml` files.
- Do not create a new validator outside `.factory` before the audit proves the exact need.
- Do not change runtime behavior.
- Do not change `.factory/archetypes/`.
- Do not edit npm publishing workflow, package version, tag, release files, or public install wording.
- Do not touch `.claude/settings.local.json`, `designos/__init__.py`, `__pycache__`, or `.pyc`.
- Do not import private business evidence into the repo.

---

## 4. Required Outputs

Create or update only audit/governance documents unless a tiny manifest wording correction is absolutely required and justified.

Required files:

1. `docs/audits/S1-0B-STANDARD-SOURCE-OF-TRUTH-DECISION.md`
   - Decision record for `knowledge/manifest.yaml` vs `knowledge/design-work-paradigm/`.
   - Must include evidence, selected source-of-truth, non-selected layer role, unresolved mapping gaps, and exact follow-up actions.

2. `docs/audits/S1-0B-DECLARED-VS-IMPLEMENTED-COVERAGE.md`
   - Skill-by-skill coverage audit.
   - Must include declaration source, implementation evidence, status, gaps, and confidence.

3. Optional only if useful:
   - `docs/audits/S1-0B-COVERAGE-MATRIX.csv` or `.md`
   - machine-readable matrix with columns:
     `skill`, `declared_asset_id`, `declared_in`, `implementation_evidence`, `evidence_type`, `coverage_status`, `confidence`, `gap`, `next_action`.

Do not add runtime tests in S1-0B unless a pure audit script is needed and approved by the current scope.

---

## 5. Minimum Evidence Rules

Every claim must be backed by exact local evidence:

- File path
- Relevant field / section / line summary
- Whether evidence is declaration, implementation, test, runtime, or documentation

Use these statuses:

- `implemented`: declaration has concrete prompt/runtime/schema/test evidence.
- `partially_implemented`: evidence exists but is incomplete or only prompt-level.
- `declared_only`: declared in manifest/pipeline, no concrete implementation found.
- `not_applicable`: skill shape does not require this item.
- `unknown`: cannot prove from local files.

Do not use "complete", "enterprise-ready", "production-ready", or "fully implemented" unless supported by runtime and tests.

---

## 6. Validation Commands

Run these at minimum:

```bash
cd /Users/young/Documents/Codex/Agent-design-webmode

git status --short
git diff --check

bash scripts/security/scan-sensitive.sh
bash scripts/security/scan-sensitive.sh --file docs/audits/S1-0B-STANDARD-SOURCE-OF-TRUTH-DECISION.md
bash scripts/security/scan-sensitive.sh --file docs/audits/S1-0B-DECLARED-VS-IMPLEMENTED-COVERAGE.md

python3 - <<'PY'
import yaml, pathlib
root = pathlib.Path('.')
km = yaml.safe_load(open(root / 'knowledge/manifest.yaml', encoding='utf-8'))
pm = yaml.safe_load(open(root / 'knowledge/design-work-paradigm/manifest.yaml', encoding='utf-8'))
paradigm_md = [p for p in (root / 'knowledge/design-work-paradigm').glob('*.md') if p.name != 'README.md']
print('shared_assets', len(km.get('assets', [])))
print('paradigm_manifest_methods', len(pm.get('methods', [])))
print('paradigm_method_md_excluding_readme', len(paradigm_md))
print('unregistered_paradigm_md_count', len(set(p.name for p in paradigm_md) - set(m.get('file') for m in pm.get('methods', []))))
PY
```

If tests are run, keep them limited to non-invasive validation:

```bash
cd /Users/young/Documents/Codex/Agent-design-webmode/.factory
python3 -m pytest tests/ -q
```

---

## 7. Commit Policy

Before S1-0B work:

1. Confirm S1-0A is committed or explicitly left uncommitted by the user.
2. If S1-0A is not committed, stop and ask whether to commit S1-0A first.
3. Do not mix S1-0A and S1-0B in one commit.

Suggested commit split:

1. `docs(governance): freeze S1-0A existing foundation inventory`
2. `docs(audit): decide S1-0B source-of-truth and coverage baseline`

Do not push unless the user explicitly says push.

---

## 8. Claude Code Prompt

Copy the following prompt into Claude Code:

```text
你是 DesignOS 工程治理与架构审计执行者。当前任务是 S1-0B，不是功能开发。

工作目录:
/Users/young/Documents/Codex/Agent-design-webmode

当前分支:
feature/senior-designer-paradigm-engine

背景:
S0 已完成敏感信息脱敏与公网发布禁用口径。S1-0A 已完成现有统一底座盘点，结论是 DesignOS 不缺新标准/新内核，真正问题是 source-of-truth 双源未裁定、声明 vs 实现未审计、强制层覆盖不足。

第一步，先确认 S1-0A 状态:
1. 运行 git status --short。
2. 如果 S1-0A 的 4 个文件仍未提交：
   - CLAUDE.md
   - .claude/skills/designos-governor/SKILL.md
   - .claude/skills/designos-knowledge-architect/SKILL.md
   - docs/audits/S1-0A-EXISTING-FOUNDATION-INVENTORY.md
   请先停止并问我是否先提交 S1-0A。不要把 S1-0A 和 S1-0B 混在一个 commit。
3. 如果 S1-0A 已提交，再继续 S1-0B。

S1-0B 目标:
1. 裁定标准 source-of-truth:
   - knowledge/manifest.yaml
   - knowledge/design-work-paradigm/manifest.yaml
   - knowledge/design-work-paradigm/*.md
2. 审计 5 个 skill 的声明 vs 实现覆盖:
   - skills/uxeval
   - skills/prd2proto
   - skills/ai-analytics
   - skills/ip-design
   - skills/brand-creative

重要事实:
- knowledge/manifest.yaml 当前是 active shared-knowledge manifest，已被 skill knowledge-manifest 引用。
- knowledge/design-work-paradigm/manifest.yaml 当前登记 20 个方法(00-19)，但目录里有 40 个方法 md 文件(不含 README)，存在登记与目录不一致。
- prd2proto 使用 pipeline quality_gates:，且 runtime 执行 kernel/quality-gates。
- uxeval / ai-analytics / ip-design 使用 pipeline gate: 暂停门语义，不要把它们直接称为 kernel quality gates，除非你找到 runtime 执行证据。
- brand-creative 是 group skill，可能没有 root pipeline.yaml。

禁止事项:
- 不要创建 SENIOR-CAPABILITY-STANDARD.md。
- 不要创建 SENIOR-DESIGN-METHODOLOGY-KERNEL.md。
- 不要创建 kernel/seniorcap/*。
- 不要创建 skill-capability.schema.json。
- 不要创建 5 份 capability.yaml。
- 不要新建脱离 .factory 的 validator。
- 不要改 runtime。
- 不要改 .factory/archetypes。
- 不要改 npm 发布、版本号、tag、workflow、公网 install 文案。
- 不要触碰 .claude/settings.local.json、designos/__init__.py、__pycache__、*.pyc。
- 不要把本地业务证据、截图、真实客户/项目数据写入仓库。

要求输出:
1. docs/audits/S1-0B-STANDARD-SOURCE-OF-TRUTH-DECISION.md
   内容必须包括:
   - 决策摘要
   - 两套标准体系证据
   - 选择哪个作为 active skill integration source-of-truth
   - 未选择体系的角色定位
   - 目录文件与 manifest 登记不一致问题
   - 不新增第三套标准的理由
   - 后续最小改造建议

2. docs/audits/S1-0B-DECLARED-VS-IMPLEMENTED-COVERAGE.md
   内容必须按 5 个 skill 展开:
   - 声明了哪些 shared knowledge assets
   - 哪些在 prompt/reference/pipeline/runtime/schema/tests 中找到实现证据
   - 哪些只是 declared_only
   - pipeline gate / quality_gates 的真实类型与执行证据
   - artifact-base 继承或未继承情况
   - status.matrix maturity 是否与事实一致
   - 每项给出 implemented / partially_implemented / declared_only / not_applicable / unknown

可选:
- 如果矩阵很大，可新增 docs/audits/S1-0B-COVERAGE-MATRIX.md 或 .csv。

验证:
必须运行:
cd /Users/young/Documents/Codex/Agent-design-webmode
git status --short
git diff --check
bash scripts/security/scan-sensitive.sh
bash scripts/security/scan-sensitive.sh --file docs/audits/S1-0B-STANDARD-SOURCE-OF-TRUTH-DECISION.md
bash scripts/security/scan-sensitive.sh --file docs/audits/S1-0B-DECLARED-VS-IMPLEMENTED-COVERAGE.md

再运行这个事实核验脚本:
python3 - <<'PY'
import yaml, pathlib
root = pathlib.Path('.')
km = yaml.safe_load(open(root / 'knowledge/manifest.yaml', encoding='utf-8'))
pm = yaml.safe_load(open(root / 'knowledge/design-work-paradigm/manifest.yaml', encoding='utf-8'))
paradigm_md = [p for p in (root / 'knowledge/design-work-paradigm').glob('*.md') if p.name != 'README.md']
print('shared_assets', len(km.get('assets', [])))
print('paradigm_manifest_methods', len(pm.get('methods', [])))
print('paradigm_method_md_excluding_readme', len(paradigm_md))
print('unregistered_paradigm_md_count', len(set(p.name for p in paradigm_md) - set(m.get('file') for m in pm.get('methods', []))))
PY

提交:
- 不要 push。
- 如果 S1-0A 已单独提交，S1-0B 可提交为:
  docs(audit): decide S1-0B source-of-truth and coverage baseline
- 如果 S1-0A 未提交，先停下来问我，不能混提交。

Closeout 必须包含:
1. 修改文件清单
2. source-of-truth 决策结论
3. 5 skill 覆盖率/缺口摘要
4. 哪些结论是本地证据确认，哪些仍 unknown
5. 敏感扫描结果
6. 是否提交、commit hash、是否推送
7. 是否可以进入 S1-0C
```

---

## 9. Reviewer Checklist

When Claude Code reports back, review these first:

- Did it stop if S1-0A was uncommitted?
- Did it avoid mixing S1-0A and S1-0B commits?
- Did it distinguish `quality_gates:` from `gate:`?
- Did it avoid claiming uxeval / ai-analytics / ip-design execute kernel quality gates?
- Did it identify the `design-work-paradigm` manifest-vs-directory mismatch?
- Did it avoid creating new standards, kernel modules, or validators?
- Did it keep all evidence local and non-sensitive?
- Did `scan-sensitive` pass for the new docs?
- Did it produce a decision, not just another broad inventory?

