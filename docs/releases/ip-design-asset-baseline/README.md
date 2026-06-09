# IP Design Asset Baseline — I0(2026-06-02)

> 本文档记录 I0 批次产出的"IP 设计资产基线":一套通用资深设计决策库 + 资产壳。
> 本批**不开发 ip-design skill runtime**,runtime 留给 I1。

## 范围

- 共享设计决策库:`knowledge/design/` 下 7 个子目录、22 个新增资产文件。
- skill 资产壳:`skills/ip-design/` 下 adapter + reference README。
- 测试:`skills/ip-design/tests/test_ip_asset_quality.py`(11 个测试)。
- shared manifest:已登记 `ip-design` 为 known_skill,登记 22 个新 ip 资产。
- backlog:I1 进入 ip-design skill runtime(SKILL.md / pipeline.yaml / prompts / private reference 的 stage 绑定 / eval / golden case)。

## 资产清单(22 项)

### 总纲与方法论(8)
- `design.ip.methodology` — 六阶段总纲与跨阶段判断逻辑。
- `design.strategy.brand-strategy-alignment` — M01 品牌策略对齐。
- `design.ip.worldview-building` — M02 世界观构建。
- `design.persona.persona-modeling` — M03 人格建模(行为模式为主,MBTI 仅辅助)。
- `design.persona.voice-and-behavior-boundary` — 声音与行为红线(M03 配套)。
- `design.visual.visual-translation` — M04 视觉转化(基因继承/识别度/小尺寸/状态/风格谱系/禁忌)。
- `design.visual.image-prompt-system` — M04 提示词系统(四层/多平台/稳定/一致/负向)。
- `design.ip.content-narrative` — M05 内容叙事。
- `design.ip.brand-material-realization` — M06 品牌物料落地。

### 质量门槛(4)
- `design.quality.ip-design-quality-rubric` — 九维 rubric + 一票否决。
- `design.quality.stage-review-checklists` — 六阶段必过项放行规则。
- `design.quality.common-failure-modes` — 跑偏与失败模式集合。
- `design.quality.professional-gap-report` — 不达中阶时的诚实声明。

### 模板(6)
- `design.templates.brand-brief / worldview / persona-profile / visual-spec / content-plan / brand-material-spec`。

### 案例(2)
- `design.cases.xfx-ipdesign` — 武侠原型 + 既有品牌基因继承。
- `design.cases.xfg-ip-kimi` — 企业效率场景型,提示词与状态延展精细化。

## 与旧资产的关系

旧 `trae_projects/ipdesign/` 与 `trae_projects/xfg-ip-kimi/` 是反抽来源,**未原样搬迁**。我们做了:
- **直接迁移(0)**:无原样复制。
- **反抽升维**:六阶段框架、人格三件套、视觉四维、提示词四层、状态延展、严格禁忌、行动元六角色、行为模式动机链等结构,被反抽并补强为决策内容(冲突取舍 / 量化标准 / 多维 rubric / 失败模式 / 诚实 gap)。
- **废弃**:旧库的"示例略"占位、单依赖 MBTI 的人格断言、缺识别度量化的视觉映射、缺多平台稳定性控制的提示词。
- **隔离**:所有项目专属符号(讯飞 / 小飞侠 / 小飞棍 / 武侠原型 / 效率权杖 / 深空灰 / 活力橙等)只允许出现在 `cases/`,通用层由结构测试拦截。

## 验证

```
python3 -m pytest -q skills/ip-design/tests/        → 11 passed
python3 -m pytest -q tests/unit/test_shared_knowledge_layer.py  → 9 passed
python3 -m pytest -q skills/uxeval/tests/           → 41 passed
python3 -m pytest -q skills/prd2proto/tests/        → 73 passed
python3 -m pytest -q skills/ai-analytics/tests/     → 7 passed
.factory/python3 -m pytest -q tests/                → 49 passed
.factory/python3 -m tools.validate ../skills/{uxeval,prd2proto,ai-analytics} --archetype <each>
                                                    → All checks passed
```

## 进入 I1 的前置条件已满足

- 决策方法论 8 件 + 质量门槛 4 件 + 模板 6 件 + 案例 2 件全部就位且测试锁定。
- adapter 已声明 ip-design 引用的全部共享资产 id。
- 测试覆盖六阶段、模板齐全、rubric 存在、failure modes ≥ 5、专属词不入通用、无过度承诺、MBTI 仅辅助。
- 结合 `designos-skill-factory` 守则,I1 可基于本基线开发 runtime。
