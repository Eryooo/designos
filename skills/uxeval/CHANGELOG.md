# UXEval Skill CHANGELOG

> **版本管理规则**（行业标准 semver，0.x 阶段视为不稳定 API）：
> - 主版本号变更（0.x → 1.0）：进入稳定期，对外承诺 API 兼容
> - 次版本号变更（0.1 → 0.2）：新增 stage / 字段 / 约束，可能不向后兼容
> - 补丁版本（0.2.0 → 0.2.1）：表述优化、bug 修复、原则 ID 重命名

---

## v0.2.0 - 2026-05-21

### Added

- **Step 0.5 环境预检**：执行评估前自主探测 PDF 解析、截图读取、Excel 生成等能力，缺失时强制提醒安装，复检循环直到闭环（或用户回退到「降级快速模式」）
- **Stage 5.5 PRD-截图冲突分析**：新增独立 stage，对比 PRD 要求 vs 截图实际，输出冲突清单作为 Stage 6 上下文
- **Step 2.5 场景-证据匹配校验**：Stage 6 新增校验步骤，问题描述场景与证据截图内容必须匹配，否则移到 unverified_issues 附录
- **宪法第 8 条**：证据截图必须与问题场景匹配（防止 I-002 类误判）
- **Step 6 系统性归并强化**：Stage 6 输出必须从业务视角归纳 5-10 类系统性问题，每类含量化影响和可执行建议
- **异常场景任务**：Stage 4 新增 Step 2.5 识别异常场景（5 类：上下文切换、页面渲染、网络异常、并发冲突、边界条件）
- **PDF 提取强约束**：禁止纯多模态"看"PDF，必须提取完整文本到 `inputs/prd.md`，AI 自主判断当前环境的最优工具
- **截图输出 `content_description`**：05b 输出每张截图的页面类型、主要元素、数据状态描述
- **问题输出 `evidence_content`**：06 问题清单引用截图时附带内容描述，用于场景-证据校验
- **Golden Sample few-shot**：06 prompt 引入 case-001 的 3 条代表性问题作为示例
- **三层启发式原则体系**：reference/m02 重构为表现层 P / 框架层 F / 结构层 S 三层（17 条原则），按产品特征自适应选取
- **任务生成强化**：必须基于完整旅程地图派生（角色+功能+场景分析 → 旅程地图 → 测试脚本 + 任务清单），禁止直接按截图写检查清单

### Changed

- **原则 ID 体系**：从 Nielsen H1-H12 系列迁移到三层 P/F/S 系列（H1→F2、H2→P2、H3→S1、H5→F1、H6→S2、H7→S3、H11→F5、H12→P3）
- **截图分析批次**：从「每批 5 张」改为「每次 1 张」，避免高分辨率截图爆 context
- **prompts 目录结构**：从 `prompts/v1.0.0/` 平铺为 `prompts/`，CHANGELOG 移到 skill 根目录
- **工具调用策略**：从硬编码 pdftotext → AI 自主判断当前 IDE/CLI 环境的最优工具

### Fixed

- 工具未安装时不再静默跳过（强制提示安装或显式降级）
- 不同 IDE/CLI 环境（Claude Code / Codex / Trae / Cursor）下的工具检测兼容性
- I-002 类场景-证据不匹配的误判（已增加多重校验）

### 端到端验证

- ✅ designos1 实测：26 张截图 + PDF 全量解析跑通
- ⚠️ 已知遗留：客户端模式无法发现主路径异常（需 M2 阶段增强 Web 模式）

---

## v0.1.0 - 2026-05-15（首版试跑）

### Added

- 首版 7 个 prompt：
  - `01-prd-understanding.md`
  - `02-principle-mapping.md`
  - `03-journey-modeling.md`
  - `04-task-generation.md`
  - `05a-script-generation.md`（仅 web 模式）
  - `05b-screenshot-analysis.md`（仅 client 模式）
  - `06-issue-attribution.md`

### Source

基于 `legacy/agent-prototypes/uxeval-agent.html` 与 `legacy/sharing-materials/体验评估分享内容.md` 方法论框架，参考 `/Users/young/Documents/trae_projects/design-review/outputs/` 真实评估产物结构。

### Note

> 早期 commit 中曾标记为 `v1.0.0`，按 semver 规则 `1.0.0` 表示首次稳定发布；M1 试点阶段实为 `v0.1.0`，已在 v0.2.0 升级时一并修正。

### Validation

- [x] 所有 prompt 含明确角色定义
- [x] 所有 prompt 含输入/输出格式
- [x] 所有 prompt 含 ≥ 1 个 few-shot 示例
- [x] 所有 prompt 引用 constitution.md
- [x] 所有 prompt 含约束清单
