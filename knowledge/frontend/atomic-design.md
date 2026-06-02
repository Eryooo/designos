# Atomic Design 组件分层（Atomic Design）

> 通用资产 · `frontend.atomic-design` · status: pilot

## purpose

用 atoms / molecules / organisms / templates / pages 五层结构组织 UI 组件,让组件职责、复用边界与目录结构可评审、可实现。

## applies_to

- 前端组件设计、原型代码生成、组件库规划。
- 需要从页面需求拆解组件层级的场景。

## decision_framework

五层定义:
- atoms:最小不可拆 UI 单位,无业务语义。
- molecules:由 atoms 组成的功能小组件。
- organisms:承载业务片段的复杂组件。
- templates:页面骨架,定义 organisms 排布。
- pages:套数据的具体页面实例。

引用方向严格自下而上:atoms ← molecules ← organisms ← templates ← pages。

## senior_heuristics

- 样式不是组件:不要建 `RedButton`,用 Button + variant。
- 带业务语义通常是 organism,通用控件通常是 atom/molecule。
- 组件复用维度决定位置:跨页复用进 shared,页面专用留页面域。
- organism 过多说明过度拆分,过少说明粒度太粗。

## quality_rubric

| 分级 | 信号 |
|---|---|
| 优 | 层级清晰、命名稳定、引用方向单一、复用边界明确 |
| 中 | 大体合理但少量业务组件层级混乱 |
| 差 | 页面一把梭,或 atoms 反向依赖 organisms |

## common_failure_modes

- 把 class/style 变化建成新组件。
- 组件粒度过大:一个 Page 包所有逻辑。
- 组件粒度过小:每个 span 都建组件。
- 跨层反向引用造成耦合。

## source_assets

- `skills/prd2proto/reference/m02-design-analysis.md`
- `skills/prd2proto/reference/textbook/atomic-design.md`

## do_not_claim

- 不规定具体框架或组件库 API。
- 不替代项目已有架构规范。
- 不保证组件可直接生成代码,只定义分层口径。
