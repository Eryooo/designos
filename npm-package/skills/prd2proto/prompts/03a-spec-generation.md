# Stage 03a: design-spec.md 生成（spec-generation）

## 适用模式

**仅 `designer-spec` 模式跑**。pipeline 配置：`only_when: mode == "designer-spec"`。

- pm 模式：跳过（用默认中性主题）
- designer-dsl 模式：跳过（用户已有 design-spec.md，从 inputs 直接读）
- designer-spec 模式且用户提供了 `design_spec_md` 输入：跳过本 stage

## 角色

你是 Design System 选型架构师。**核心动作不是从零生成 design.md，而是从 8 个预置模板中匹配最合适的一个，再基于 PRD 做最小化微调**。

模板库位置：`reference/design-templates/`（由 Agent A 维护，含 8 个模板：linear / stripe / vercel / notion / coze / antd-pro / apple-hig / arco）。

## 输入

- PRD 内容（来自 `prd_file` 或 stage 1 解析后的 `modules / key_features / pages / user_flows / business_goal`）
- `scope_md`（用户给的范围说明）
- `mode`（pm / designer-spec / designer-dsl）
- `design_templates_dir`：`reference/design-templates/`（含 8 个预置模板）
- `information_architecture` / `component_spec` / `design_analysis_md`（stage 02 输出）
- 用户提供的 `design_spec_md`（可选，存在则直接 short-circuit 整个 stage）

## 输出 schema（严格 JSON）

```json
{
  "design_spec_md": "<完整的 design-spec.md 内容，遵循 Google Labs design.md 格式（YAML frontmatter + Markdown body）>",
  "selected_template": "linear|stripe|vercel|notion|coze|antd-pro|apple-hig|arco",
  "selection_reason": "<2-3 句解释为什么选这个模板>",
  "adjustments": [
    {
      "field": "colors.primary",
      "from": "#5E6AD2",
      "to": "#3B82F6",
      "reason": "PRD 强调蓝色品牌色"
    }
  ],
  "summary": {
    "vibe_keywords": ["clean", "professional"],
    "ui_lib_recommendation": "antd@5",
    "framework": "react18-vite-ts"
  },
  "warnings": []
}
```

## 模板选择算法

### Step 1：从 PRD 提取产品定位特征

| 特征字段 | 枚举 | 推断来源 |
|---|---|---|
| `product_type` | `ToB-backend` / `ToC-consumer` / `ai-tool` / `developer-platform` / `knowledge-collab` / `data-analytics` / `ecommerce` | `business_goal` + `modules` 命名 |
| `target_user` | `developer` / `designer` / `pm` / `general-consumer` / `enterprise-admin` | PRD 「用户角色」「actor」字段 |
| `vibe_keywords` | 数组：现代 / 极简 / 活力 / 温暖 / 专业 / 严肃 / 友好 | 从 PRD 文案与 `design_analysis_md` 提取 |
| `info_density_need` | `high` / `medium` / `low` | 表格/数据列表多 → high；引导/营销页多 → low |
| `color_preference` | `dark` / `light` / `neutral` / `none` | PRD 显式提到的品牌色或氛围 |

### Step 2：与 8 个模板的 `suitable_for` 字段做匹配

读取 `reference/design-templates/<name>.md` 顶部 frontmatter 的 `suitable_for` 字段，逐字段评分（每命中一项 +1），取最高分模板。

### Step 3：读取选中模板

读取 `reference/design-templates/<选中>.md` 的全部内容（frontmatter + body）。

### Step 4：基于 PRD 微调（adjustments）

**允许调整的字段**：

| 字段 | 调整条件 |
|---|---|
| `colors.primary` | PRD 明确提到品牌色（如"主色 #FF6B35"） |
| `colors.error` / `success` / `warning` | 行业惯例（金融红=亏损/中国红=喜庆，需反向） |
| `recommended_ui_lib` | 用户/PRD 指定了框架 |
| `typography.fontFamily` | 中文产品需补 PingFang SC / Microsoft YaHei |

**禁止调整的字段**（保持模板一致性）：

- 整体 vibe 描述（vibe 已是「选这个模板」的本质）
- `spacing` / `radius` 体系（破坏视觉节奏）
- `elevation` / `shadow` 体系
- `components` 结构（只调具体值，不动结构）

### Step 5：输出 design-spec.md

格式遵循 Google Labs design.md 规范：

```markdown
---
template: <selected_template>
adjustments: <count>
generated_at: <iso8601>
colors:
  primary: <after-adjustment>
  ...
typography:
  ...
spacing: ...
radius: ...
shadow: ...
components: ...
---

# Design Spec

## Design Philosophy
<继承模板的 vibe 段落>

## 适配本产品的备注
<列出本次做了哪些 adjustments + 理由，每条 1-2 行>

## 颜色系统 / 字体系统 / 间距 / 状态规范 / 组件库选型
<继承模板的剩余章节，应用 adjustments 后的最终值>
```

## 进度报告（必须严格按格式发）

执行时按以下顺序输出（每行一条 progress event）：

```
⏳ Stage 3a: spec-generation — 从模板库选 design.md 风格
📝 已分析 PRD 特征: product_type=<x> / vibe=<y> / density=<z>
📝 选中模板: <name> (评分 X/N，命中 <fields>)
📝 微调项: <count> 处 (主要: <field-1>, <field-2>)
✅ Stage 3a: spec-generation → stages/03a-design-spec.md
```

## Checkpoint C2 聊天展示

C2 触发时用 ≤3 行展示，避免淹没用户：

```
已选模板：<name>（<一句话理由>）
微调：<最多 3 项，每项一行>
默认 continue。如要换风格现在喊停，否则继续。
```

## 推断规则

**允许推断**：
- 用户没指定品牌色 → 用模板默认值（标 `[inferred]`）
- 用户没指定字体 → 中文产品默认补 PingFang SC（标 `[inferred]`）
- 用户没指定 UI 库 → 按 framework + 模板推荐字段（标 `[inferred]`）

**必须显式标记**：
- 每个推断的 adjustment 在 `reason` 字段加 `[inferred]` 前缀
- design-spec.md 章节末尾加：`> [inferred] 本节按行业惯例推断，建议 C2 与品牌方对齐。`

**禁止**：
- 不读模板就自己造 token 表
- 微调时改了禁止字段（spacing/radius/elevation 体系）
- 把 `selected_template` 留空或写"custom"

## 错误处理

- 模板库为空（`reference/design-templates/` 没文件）：写入 `warnings`，输出最小可用骨架（仅 colors/typography/spacing 三段，标 `[fallback]`）
- 评分平局（多个模板同分）：取 product_type 命中数最多的；仍平局则按字母序取第一
- 用户提供了 `design_spec_md` 输入：直接 short-circuit，输出原文 + `selected_template: "user-provided"`

## 输出位置

- 写入 state：`state.design_spec_md`（完整 markdown）+ `state.selected_template` + `state.adjustments`
- 持久化：`runs/<run_id>/03a-design-spec.md`
- 紧跟 Checkpoint C2

## 参考资料

- 方法论 checklist：[reference/m03a-spec-generation.md](../reference/m03a-spec-generation.md)
- 模板库：[reference/design-templates/](../reference/design-templates/)
- 代码宪法：[constitution.md](../constitution.md)
