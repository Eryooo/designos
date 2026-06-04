# competitive-analysis — 竞品分析子技能

> Phase 1 策略与定位 · B1.1 已交付 pilot 版本

## 定位

竞品分析(视觉风格/传播策略/市场空白),为 brand-strategy 提供可追溯的证据基础。

## 核心产出

- `competitor_matrix`(comparison_matrix):竞品对比矩阵,至少 3 个竞品,必含 visual_style
- `market_gap_report`:市场空白报告,至少 1 个有证据基础的市场空白

## 复用共享决策资产

- `knowledge/research/competitor-analysis.md`(K1 已交付)

## 并行开发边界

- 可并行(仅依赖用户输入,无上游子技能依赖)
- 下游消费者:`brand-strategy`

## B1.1 交付内容

- ✅ SKILL.md(frontmatter + 定位边界)
- ✅ pipeline.yaml(2 stages + 引用共享 knowledge)
- ✅ constitution.md(核心约束,observed/inferred/unknown 分级)
- ✅ prompts/(2 个 stage prompt,支持插值)
- ✅ reference/(1 个参考案例,展示事实分级)
- ✅ eval/golden/(1 个 golden case)
- ✅ eval/failure/(2 个 failure cases:insufficient_data + over-inference)
- ✅ eval/promptfoo.yaml(promptfoo 评测配置,3 个 test cases)
- ✅ tests/(pytest 结构与契约测试)

## 实际能力

**能做:**
- 从 product_brief / target_market / competitor_hints 产出结构化竞品矩阵
- 至少覆盖 3 个直接竞品,包含视觉风格/传播策略/市场定位维度
- 每条竞品事实区分 observed / inferred / unknown
- 识别至少 1 个未被竞品占据的市场空白(情感/价值/视觉空间)
- 输入不足时输出 status: insufficient_data,不编造事实

**不能做(pilot 限制):**
- ❌ 不自动爬取或验证外部资料;仅消费用户提供的输入
- ❌ 不声称完成深度竞品审计(专利/财务/组织不在范围)
- ❌ 不保证分析结论超过输入资料质量
- ❌ 不预设行业;依赖用户输入的 target_market 范围

## 质量标准(B1.0 contract)

- 竞品矩阵至少覆盖 3 个直接竞品
- 视觉风格维度(色彩/形态/辅助图形)必须填充
- 每个竞品必须有 visual_style 字段(frozen schema 要求)
- market_gap_report 指出至少 1 个未被竞品占据的情感/视觉空间
- 未验证结论必须标注 `[inferred]`
- 输入不足时 status 字段标注 `insufficient_data`

## 测试运行

```bash
# 结构与契约测试
pytest skills/brand-creative/sub-skills/competitive-analysis/tests/

# Promptfoo 评测(需安装 promptfoo)
cd skills/brand-creative/sub-skills/competitive-analysis
promptfoo eval -c eval/promptfoo.yaml
```
