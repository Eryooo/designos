# typography-system

品牌字体系统子技能 — 产出可落地的字重层级、字号比例、中西文配对与跨端规范。

## 概述

基于 `brand_brief` 的人格关键词推导字体气质方向,产出完整字体系统:主字体/辅助字体、字重层级、字号比例、行高、中西文配对、fallback 栈、授权风险信号与跨端可用性说明。

## 核心输出

- `typography_spec`
- 主字体 / 辅助字体配对
- 3-4 层字重层级
- 模块化字号比例
- 中西文行高与配对说明
- Web / iOS / Android / 印刷跨端可用性
- 商用授权风险状态与 fallback 字体栈

## 质量标准

- 中西文配对必须说明字重/字面/重心协调逻辑
- 字重层级必须 3-4 个且相邻可辨
- 字号比例必须和谐,不允许随意跳级
- `license_status` 必须诚实标注 `verified` 或 `needs_verification`
- `cross_platform` 至少覆盖 Web / iOS / Android 三端
- fallback 字体栈必须可执行,不能只给理想字体名

## 使用方式

```python
from designos.kernel import SkillLoader

loader = SkillLoader()
skill = loader.load_skill("brand-creative:typography-system")

result = skill.run({
    "brand_brief": {
        "north_star": "让专业人士感到被支持",
        "personality_keywords": ["专业", "现代", "可靠", "清晰"],
        ...
    }
})

typography_spec = result["typography_spec"]
```

## 能力边界

- ✅ 产出字体系统规范 + 授权风险信号 + 跨端 fallback
- ✅ 中西文配对与层级比例说明
- ✅ Web / iOS / Android / 印刷可用性建议
- ❌ 不声称已完成字体商用授权采购
- ❌ 不声称覆盖所有语言场景
- ❌ `license_status=needs_verification` 时不得宣称授权已确认

## 依赖

- 上游: brand-strategy (提供 brand_brief)
- 并行同级: logo-design / color-system
- 下游: visual-identity

## 文件结构

- `SKILL.md`: 子技能元数据
- `pipeline.yaml`: 两阶段 pipeline (字体方向分析 → 字体系统产出)
- `constitution.md`: 核心原则与红线
- `prompts/`: Stage prompts
- `tests/`: Runtime 测试

## 版本

- 0.1.0-pilot: 初始 pilot 版本, runtime ready
