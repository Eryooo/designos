# Reference: PRD 结构化理解（m01 checklist）

> Stage 01 `prd-understanding` 约束清单。教学材料见 `textbook/story-mapping.md`。

## 输出 schema 强约束

```json
{
  "modules": [...], "key_features": [...], "pages": [...],
  "user_flows": [...], "business_goal": "<one sentence>", "warnings": []
}
```

## 字段约束清单

### modules
- [ ] 数量 1-15（>15 过度拆分；<3 → warnings）
- [ ] `id`：`M-001` 三位顺序
- [ ] `name`：名词短语，2-6 汉字或 2-4 英文词
- [ ] `priority` ∈ `{P0, P1, P2}`，PRD 没明说全 P0
- [ ] `page_ids` 必须能对上 `pages[].id`

### key_features
- [ ] 数量 3-30
- [ ] 必填：`id / name / module_id / description / user_value`
- [ ] `description` 动词开头："新增/编辑/查看/删除/批量..."
- [ ] `acceptance` 数组，每条可验证；推断保留 `[inferred]`

### pages
- [ ] 数量 2-50
- [ ] `path` ∈ `{/xxx, /xxx/:id, /xxx/:id?}`
- [ ] `page_type` ∈ `{list, form, detail, dashboard, wizard, settings, auth, error}`
- [ ] `primary_actions` 1-5 个，按用户最可能动作排序
- [ ] `navigates_to` 必须列 page_id

### user_flows
- [ ] 数量 1-10
- [ ] `steps` 长度 2-8
- [ ] 每步必填：`step / page_id / action / expected`
- [ ] 至少一个 `is_critical_path: true`
- [ ] `actor` 必须人类角色（系统流程不算 user_flow）

## 推断规则

允许（必须标 `[inferred]`）：
- PRD 没说的 priority → 全 P0
- 没写的 acceptance → 按 description 推
- user_flow expected 缺失 → 按通用产品逻辑补

禁止替 PM 写需求：PRD 没提的功能不要凭直觉补；强烈认为缺失 → 写 `warnings`。

## 常见陷阱

| 陷阱 | 错误 | 正确 |
|---|---|---|
| 替 PM 加需求 | 凭直觉补 feature | 写 warnings |
| 章节标题当 module | "非功能需求" 建成 module | 丢到 business_goal/warnings |
| page 与 feature 混淆 | "保存草稿" 既建 page 又建 feature | feature 用 `/rules/edit/:id?` |
| 业务流当 user_flow | "数据每天凌晨同步" | user_flow 必须人类 actor |
| 过度拆分页面 | `/rules/list` `/rules/filter` 分开 | 一 URL = 一 page，filter 进 primary_actions |

## 推断标记规范

```text
"description": "[inferred] 自动每 30s 保存一次"
"pain_points": ["规则切换误覆盖", "[inferred] 批量调整缺撤销"]
```

C1 高亮所有 `[inferred]`，**漏标比误标更糟**。

## 与下游 stage 的契约

| 字段 | 谁消费 | 怎么用 |
|---|---|---|
| `modules` | design-analysis | 推站点导航 |
| `key_features` | design-analysis | 推组件需求 |
| `pages` | design-analysis | 直接生成路由表 |
| `user_flows` | design-analysis | 标关键路径，review-gate 校验覆盖 |
| `business_goal` | review-gate | 总评引用 |

教学材料：`textbook/story-mapping.md`。
