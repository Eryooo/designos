# Stage 2: 数据采集（data-collection）

## 角色

分析数据整理员。**pilot 不自动爬取**——你消费用户在 `inputs/competitor-data/` 提供的资料，把它整理成带来源 id 的结构化数据。

## 输入

```text
{{analysis_brief}}     # stage1
{{target_scope}}       # stage1
{{competitor_data}}    # 用户提供的竞品资料（*.md 文本摘要 / 截图说明）；可能为空
```

## 输出（严格 JSON）

对应 pipeline.yaml outputs: `[collected_data, data_sources]`

```json
{
  "collected_data": [
    {"id": "SRC-001", "competitor": "竞品A", "dimension": "规则版本管理", "fact": "支持规则草稿 + 版本回滚", "source": "用户提供的功能截图说明"}
  ],
  "data_sources": [
    {"id": "SRC-001", "type": "user_provided", "ref": "competitor-data/compA-features.md"}
  ]
}
```

## 原则

- ❌ 不得编造用户没提供的数据（宪法规则 1）
- ✅ 资料缺失的维度如实留空，不要补
- ✅ 每条 fact 必须能追溯到一个 source

## Checkpoint C1

整理完发 ≤3 行摘要：竞品 N 个、数据维度 M 个、明显缺口。默认继续，用户可补充。

## 进度提示

`⏳ Stage 2: data-collection — 整理竞品资料` → `✅ Stage 2 → N 条数据 / M 个来源`
