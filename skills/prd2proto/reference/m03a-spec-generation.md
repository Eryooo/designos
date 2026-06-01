# Reference: design-spec.md 生成（m03a checklist）

> Stage 03a `spec-generation` 约束清单。**从模板库选 + 微调**，不从零生成。教学材料见 `textbook/design-tokens-w3c.md`。

## 模板匹配算法（必须严格执行）

### Step 1：从 PRD 提取 5 个产品定位特征

| 字段 | 枚举 |
|---|---|
| `product_type` | ToB-backend / ToC-consumer / ai-tool / developer-platform / knowledge-collab / data-analytics / ecommerce |
| `target_user` | developer / designer / pm / general-consumer / enterprise-admin |
| `vibe_keywords` | 数组：现代/极简/活力/温暖/专业/严肃/友好 |
| `info_density_need` | high / medium / low |
| `color_preference` | dark / light / neutral / none |

### Step 2：与 8 模板的 `suitable_for` 字段评分

读取 `reference/design-templates/<name>.md` frontmatter `suitable_for`，逐字段命中 +1。候选：linear / stripe / vercel / notion / coze / antd-pro / apple-hig / arco。

### Step 3：取最高分模板

平局：取 `product_type` 命中最多；仍平局 → 字母序第一。

### Step 4：基于 PRD 微调

每条 adjustment 必须 4 字段：`field / from / to / reason`。

## 微调允许 vs 禁止

| 字段 | 允许 | 触发条件 |
|---|---|---|
| `colors.primary` | ✅ | PRD 明确指定品牌色 |
| `colors.error/success/warning` | ✅ | 行业惯例 |
| `recommended_ui_lib` | ✅ | 用户/PRD 指定框架 |
| `typography.fontFamily` | ✅ | 中文产品补 PingFang SC |
| 整体 vibe / spacing / radius / elevation / components 结构 | ❌ | 破坏一致性 |

## 输出 JSON 必须字段

```json
{
  "design_spec_md": "<完整 markdown，YAML frontmatter + body>",
  "selected_template": "linear|stripe|vercel|notion|coze|antd-pro|apple-hig|arco|user-provided",
  "selection_reason": "<2-3 句>",
  "adjustments": [{"field":"...","from":"...","to":"...","reason":"..."}],
  "summary": {"vibe_keywords":[],"ui_lib_recommendation":"","framework":""},
  "warnings": []
}
```

- [ ] `selected_template` ∈ 9 个允许值
- [ ] `selection_reason` 2-3 句，不能空
- [ ] `adjustments` 每条 4 字段
- [ ] 推断 adjustment `reason` 加 `[inferred]` 前缀

## design-spec.md 格式（Google Labs 规范）

```markdown
---
template: <selected_template>
adjustments: <count>
generated_at: <iso8601>
colors / typography / spacing / radius / shadow / components
---

# Design Spec
## Design Philosophy   <继承模板 vibe>
## 适配本产品的备注     <列出 adjustments + 理由>
## 颜色 / 字体 / 间距 / 状态 / 组件库选型
```

## 错误处理

- [ ] 模板库为空 → warnings + 最小骨架（colors/typography/spacing 三段，标 `[fallback]`）
- [ ] 用户提供 `design_spec_md` 输入 → short-circuit，输出原文 + `selected_template: "user-provided"`

## 与下游 stage 的契约

| 产物 | 谁消费 |
|---|---|
| `design_spec_md` 颜色 token 表 | token-extraction |
| 组件规范 + 状态规范 | code-generation + review-gate |
| `selected_template` | C2 checkpoint 展示 |
| `summary.framework` | code-generation MCP |

## 推断标记

每个推断 adjustment `reason` 加 `[inferred]`。design-spec 章节末尾加：

```markdown
> [inferred] 本节按行业惯例推断，建议 C2 与品牌方对齐。
```

教学材料：`textbook/design-tokens-w3c.md`（W3C DTCG 三层架构 + 推荐尺度）。
