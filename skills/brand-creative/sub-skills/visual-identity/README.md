# visual-identity(占位 · B0 baseline)

> Phase 2 视觉识别系统 · 本批(B0)只建目录占位,不开发 runtime。

## 定位

完整 VI 手册(logo/色彩/字体/辅助图形/应用规范)

## 核心产出

- `vi_manual`

## 复用共享决策资产

- design.visual.visual-translation + design.quality.*

## 并行开发边界

- 必须串行(依赖 logo/color/typography 三者产出)

## B0 范围

本目录在 B0 只有本 README 占位。后续批次(B1+)开发:
- SKILL.md(frontmatter + 定位边界)
- pipeline.yaml(stages + 引用共享 knowledge)
- prompts/(各 stage prompt)
- tests/(结构与契约测试)

开发前若 `new_knowledge_needed`(见 ../../knowledge-manifest.yaml)中列出本子技能依赖的新资产,需先补共享决策库再开发。
