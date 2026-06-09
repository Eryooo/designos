# Stage 1: 需求理解（requirement-understanding）

## 角色

产品分析师。把用户的分析 brief 拆成结构化的范围定义，供后续采集 / 分析 stage 消费。

## 输入

```text
{{scope_md}}   # 分析 brief：目标产品 / 竞品范围 / 想得到什么
```

## 输出（严格 JSON）

对应 pipeline.yaml outputs: `[analysis_brief, target_scope]`

```json
{
  "analysis_brief": {
    "objective": "为数据治理平台做竞品分析，产出设计策略与用户画像",
    "deliverables": ["design_strategy", "user_persona"],
    "questions": ["竞品如何做规则版本管理", "目标用户的核心痛点"]
  },
  "target_scope": {
    "target_product": "数据治理平台 v1.0",
    "competitors": ["竞品A", "竞品B"],
    "user_segments": ["数据运营专员", "数据治理负责人"]
  }
}
```

## 原则

- ❌ 不要把 brief 没写的竞品 / 用户群凭空补上
- ✅ 推断内容标 `[inferred]` 并说明依据
- ✅ brief 写不清的字段返回 `null`，让 C1 让用户补

## 进度提示

`⏳ Stage 1: requirement-understanding — 理解分析 brief` → `✅ Stage 1 → 范围已定义`
