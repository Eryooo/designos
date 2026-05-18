# UXEval Prompts CHANGELOG

> 版本管理规则：
> - 主版本号变更（1.x → 2.x）：prompt 输入/输出 schema 不兼容
> - 次版本号变更（1.0 → 1.1）：新增字段、不破坏现有调用
> - 补丁版本（1.0.0 → 1.0.1）：表述优化、bug 修复

## v1.0.0 - 2026-05-15

### Added

- 首版 7 个 prompt：
  - `01-prd-understanding.md`（共享于 prd-understanding / persona-derivation / scenario-derivation 三 stage）
  - `02-principle-mapping.md`
  - `03-journey-modeling.md`
  - `04-task-generation.md`
  - `05a-script-generation.md`（仅 web 模式）
  - `05b-screenshot-analysis.md`（仅 client 模式，作为 image-analyzer MCP 内部参考）
  - `06-issue-attribution.md`

### Source

基于 `legacy/agent-prototypes/uxeval-agent.html` 与 `legacy/sharing-materials/体验评估分享内容.md`
方法论框架，参考 `/Users/young/Documents/trae_projects/design-review/outputs/` 真实评估产物结构。

### Validation

- [x] 所有 prompt 含明确角色定义
- [x] 所有 prompt 含输入/输出格式
- [x] 所有 prompt 含 ≥ 1 个 few-shot 示例
- [x] 所有 prompt 引用 constitution.md
- [x] 所有 prompt 含约束清单
