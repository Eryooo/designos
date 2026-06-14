# S1-0D — Pre-Release Hygiene（内部 MVP Trial 前卫生检查）

> **本报告性质**:针对 S1-0C closeout 识别的发布前 hygiene 问题做最小处理 + 风险盘点。只做卫生清理不改功能。
> **核验边界**:npm registry / 公网 GitHub repo 属外部系统,本地无法核验,标注「待外部核验」。
> **日期**:2026-06-12

---

## 1. 处理结果

### 1.1 占位符处理

| 位置 | S1-0D 前 | S1-0D 后 | 处理依据 |
|---|---|---|---|
| `knowledge/design-work-paradigm/manifest.yaml` maintainers.contact | `<YOUR_INTERNAL_PRIVATE_REPO>` | `<REPOSITORY_CONTACT_PLACEHOLDER>` | spec 要求改为更中性的公开占位符;不写真实内部仓库 |

**其他 22 处该占位符位置**:(本批次记录不修,留作统一清理)
- `README.md` / `README.zh-CN.md` / `CONTRIBUTING.md` / `AGENTS.md` / `docs/内测操作手册.md` / `docs/README.md` / `docs/troubleshooting.md` / `docs/api-reference.md` / `docs/getting-started.md` / `docs/plans/M1-完成报告.md` / `docs/examples/e-commerce-ux.md` / `docs/share/01-DesignOS完整方案沉淀.md` / `docs/share/README.md` / `skills/prd2proto/PILOT-BOUNDARY.md`

这 22 处在最终发布前需统一清理(批量 sed 或确认全部为公开占位符)。本批只修 paradigm manifest 1 处(避免超范围改动)。

### 1.2 未跟踪文件处理建议

`docs/handoff/execution/04-s1-0b-coverage-audit-execution-prompt.md` — 这是用户传给我执行 S1-0B 时的 handoff prompt 副本。

**建议**(三选一,由用户决定,本批不自动处理):
1. **提交为内部 handoff 文档**(建议):该文件含 S1-0B 的执行指令,对未来协作有价值,可提交到 `docs/handoff/` 作为历史留档。**如提交必须单独 commit**,不混入 S1-0D hygiene。
2. **移动到 `docs/archive/handoff/`**(归档):若 handoff 不作为长期文档,可归档。
3. **保持未跟踪/删除**(临时材料):若认为纯执行指令无长期价值,保持 `??` 或删除。

> 本报告不做决定。S1-0D commit 不纳入该文件。

---

## 2. 发布口径风险清单

### 2.1 版本号三源不一致（中等风险）

| 文件 | 版本 | 含义 |
|---|---|---|
| `pyproject.toml` | **0.6.2** | Python 包版本(本地) |
| `install.sh` | **0.5.0a1** | installer 脚本自报版本 |
| `docs/architecture.md` | **0.6.2** | 架构文档版本 |
| `skills/status.matrix.yaml` | **2.0.0** | status schema 版本(非 DesignOS 主版本) |
| 历史 npm 0.7.1 | **0.7.1** | 已发布(根据用户陈述,**待外部核验**) |

**风险**:
- pyproject 0.6.2 **落后于**历史 npm 0.7.1(若后者真存在)→ 回退版本?还是 0.6.2 是本地开发版、0.7.1 是 clean-seed 快照版?
- install.sh 0.5.0a1 是**最旧版本**且带 alpha 后缀 → installer 版本未同步主包。
- 三个版本号互不一致,外部用户无法判断「当前稳定版本」。

**是否阻塞内部 MVP trial**:
- ❌ 不阻塞。内部 trial 可明确用「本地 0.6.2」或「指定 commit」,不依赖版本号一致性。

**是否阻塞公网 release**:
- ✅ **阻塞**。公网 release 必须版本号统一(pyproject / install.sh / CHANGELOG / tag / architecture.md 一致),且高于历史 0.7.1(或明确 0.7.1 废弃/回收)。

### 2.2 22 处占位符残留（低风险，但公网 release 必清）

**风险**:
- 这些占位符是 S0 阶段脱敏的结果,内部 trial 不影响(内部人员知道真实仓库)。
- **公网 release 前必须全部清理**,否则公网 README 显示「<YOUR_INTERNAL_PRIVATE_REPO>」会造成困惑。

**是否阻塞内部 MVP trial**:❌ 不阻塞(内部人员可手动替换或忽略)。
**是否阻塞公网 release**:✅ 阻塞(文档完整性)。

### 2.3 install.sh 依赖的 REPO 占位符（中等风险）

`install.sh` 第 20 行:`REPO="<YOUR_ORG>/<YOUR_INTERNAL_REPO>"`

**风险**:该脚本的 GitHub 拉取逻辑依赖 REPO 变量,若保持占位符则 install.sh **完全不可用**(无法拉取代码)。

**是否阻塞内部 MVP trial**:
- 🟡 **部分阻塞**。若内部 trial 需要 install.sh 安装(非手工 git clone),必须先修 REPO 变量为真实内部仓库地址。
- 若内部 trial 用手工 `git clone + pip install -e .`,不受此影响。

**是否阻塞公网 release**:✅ 阻塞(installer 不可用)。

### 2.4 package.json 本地不存在（低风险）

本地仓库无 `package.json`,历史提到「npm 0.7.1 已发布」时的 package.json **可能在 clean-seed 快照或 CI 生成**。

**风险**:
- 本地无法核验 npm 包的 name / version / repository 元数据是否一致。
- 若 npm 包真已发布,其 package.json 内容是外部系统状态,无法从本地文件审计。

**是否阻塞内部 MVP trial**:❌ 不阻塞(内部不依赖 npm)。
**是否阻塞公网 release**:🟡 需确认 npm 包状态(是否下架 0.7.1 / 是否重新发布)。

### 2.5 各 skill 独立版本(uxeval 1.0.0 / prd2proto 0.3.0-capability-pilot 等)

各 skill `SKILL.md` frontmatter 声明的 `version:` 字段独立于 DesignOS 主版本。README 表格中展示的版本号(`uxeval 1.0.0` 等)是从这里来的。

**风险**:
- 这是**设计如此**(README 说"Independent versioning for each skill"),非风险。
- 但 prd2proto 0.3.0 vs README 表述 0.2.0 — **README 表格过时**。

**是否阻塞内部 MVP trial**:❌ 不阻塞(skill 版本不影响试用,status.matrix 是权威状态)。
**是否阻塞公网 release**:🟡 需同步 README skill 版本表与 SKILL.md 实际版本。

---

## 3. 版本口径风险汇总表

| 风险项 | 内部 MVP trial | 公网 release | 建议动作 |
|---|---|---|---|
| pyproject 0.6.2 vs 历史 npm 0.7.1 | ❌ 不阻塞 | ✅ 阻塞 | 确认 0.7.1 状态(废弃 / 快照版 / 真发布);若真发布需 bump 到 ≥0.7.2 或明确回退逻辑 |
| install.sh 0.5.0a1 过时 | ❌ 不阻塞 | ✅ 阻塞 | 同步到 pyproject 版本(0.6.2 或更高) |
| install.sh REPO 占位符 | 🟡 部分阻塞 | ✅ 阻塞 | 内部 trial 若需 install.sh,改为真实内部仓库;公网 release 改为公网仓库 |
| 22 处占位符残留 | ❌ 不阻塞 | ✅ 阻塞 | 公网 release 前批量清理 |
| package.json 本地不存在 | ❌ 不阻塞 | 🟡 需确认 | 查 npm registry 0.7.1 状态 |
| README skill 版本表 vs SKILL.md | ❌ 不阻塞 | 🟡 需同步 | 同步 README 表格与 SKILL.md 实际版本 |

---

## 4. 本批次处理范围与未处理事项

### 4.1 本批次已处理
- ✅ paradigm manifest 1 处占位符改为中性公开占位。
- ✅ 本报告(发布口径风险盘点)。

### 4.2 本批次未处理(原因:超出 S1-0D "最小 hygiene" 范围)
- ❌ 其余 22 处占位符(避免批量改动引入新风险,留作统一清理)。
- ❌ install.sh 版本 bump(需决策版本号策略,超出 hygiene 范围)。
- ❌ install.sh REPO 占位符(需明确内部 / 公网仓库地址,由用户决策)。
- ❌ pyproject vs 历史 0.7.1 的版本冲突解决(需外部核验 npm,超范围)。
- ❌ README skill 版本表同步(文档校准,留作文档批次)。
- ❌ 04-s1-0b prompt 提交(用户决策,不自动处理)。

---

## 5. 是否阻塞内部 MVP Trial

### 结论:❌ **基本不阻塞**

**可立即进入内部 MVP trial 的前提**:
- ✅ 内部人员用 **手工 git clone + pip install -e .** 安装(不依赖 install.sh)。
- ✅ 内部人员知道真实仓库地址,22 处占位符不影响(可手动替换或忽略)。
- ✅ 版本号不一致不影响试用(以 commit hash / branch 为准)。

**若要用 install.sh 安装**:
- 🟡 需先修 `install.sh` 第 20 行 `REPO="<真实内部仓库>"`,否则 installer 拉取失败。
- 🟡 install.sh 版本 0.5.0a1 过时不影响功能(只是自报版本号错)。

### 建议:
内部 MVP trial 直接用 git clone 方式,跳过 install.sh,无阻塞。

---

## 6. 是否阻塞公网 Release

### 结论:✅ **阻塞**(多项前置清理未完成)

**必须先完成**(才能公网 release):

| # | 阻塞项 | 当前状态 | 必须动作 |
|---|---|---|---|
| 1 | 版本号三源统一 | pyproject 0.6.2 / install.sh 0.5.0a1 / 历史 npm 0.7.1 不一致 | 确认 npm 0.7.1 状态;bump 到统一版本(≥0.7.2 或明确废弃 0.7.1);pyproject / install.sh / architecture.md / CHANGELOG 同步 |
| 2 | 22 处占位符清理 | 22 处 `<YOUR_INTERNAL_PRIVATE_REPO>` 残留 | 批量清理或确认全部改为公网仓库地址 |
| 3 | install.sh REPO 占位符 | `REPO="<YOUR_ORG>/<YOUR_INTERNAL_REPO>"` | 改为公网仓库(如 `designos/designos`)或 npm 包安装路径 |
| 4 | npm 包状态确认 | package.json 本地不存在,npm 0.7.1 真实状态未知 | 核验 npm registry;若 0.7.1 已发布需决定:下架 / 保留 / 重发 |
| 5 | README skill 版本表同步 | README 表 prd2proto 0.2.0 vs SKILL.md 0.3.0 | 同步 |

> 公网 release 流程建议:S1-0E 专门处理以上 5 项(版本统一 + 占位符批量清理 + npm 包决策)。本批次(S1-0D)只做最小 hygiene + 盘点,不执行发布流程。

---

## 7. 后续建议

- **S1-0E(建议)**:统一版本号 + 批量清理占位符 + 确认公网 release 前置条件(需外部系统访问:npm / GitHub public repo)。
- **内部 MVP trial 直接可行**:用 git clone 方式,22 处占位符不影响,版本号不一致不影响(以 commit 为准)。
- **04-s1-0b prompt 建议提交**:作为 `docs/handoff/` 历史留档,但**单独 commit**(不混入 S1-0D)。

---

*报告结束。S1-0D 只修 1 处占位符 + 写本报告,不改发布逻辑/版本号/其余占位符。*
