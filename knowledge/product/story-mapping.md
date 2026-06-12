# 故事地图方法（Story Mapping）

> 通用资产 · `product.story-mapping` · status: draft
> 把需求拆解为 modules / features / flows 的通用故事地图方法。本文与任一具体
> PRD 无关,只给结构与判定规则;不规定输出 schema,不绑定任何 stage 编号。

## 三层结构

```
business_goal（一句话目标）
    ├─ modules（业务能力域，骨架/backbone）
    │   ├─ key_features（完成活动的最小动作）
    │   └─ pages（UI 承载单元）
    └─ user_flows（跨模块的端到端任务切片）
```

- backbone = 用户的主要活动(modules)
- walking skeleton = 完成活动所需的最小动作(features + pages)
- 横向切片 = 用户实际做事的端到端流(flows)

## INVEST 判定（每个 feature）

| 字母 | 含义 | 判定 |
|---|---|---|
| Independent | 独立 | 描述清楚不依赖其他 feature 上下文 |
| Negotiable | 可协商 | 推断的验收标注为可改 |
| Valuable | 有价值 | 必须能说出用户价值,不写"系统功能" |
| Estimable | 可估算 | 具体到能估开发量 |
| Small | 小 | 过长即拆 |
| Testable | 可测试 | 验收可被验证 |

## 关键路径判定

一条 flow 是关键路径,当它:对应 business_goal 的核心动词、跨 ≥2 个 module、在需求中反复出现。

## 适用边界

本文给方法与判定;具体输出字段、stage 顺序、checkpoint 由消费方 skill 决定。

## 占位说明

本文为 K0 架构基线的 draft 占位,后续批次补全拆解示例。
