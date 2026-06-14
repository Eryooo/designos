# S1-0B Coverage Matrix — 全资产 × 实现证据

> 配套 `S1-0B-DECLARED-VS-IMPLEMENTED-COVERAGE.md` 的细粒度矩阵。每行 = 一个 skill 声明的资产 × 其实现证据。
> 状态口径见主报告 §0。本批只审计不改造。
> 日期:2026-06-12

## 1. 资产级矩阵

| skill | 声明资产 id | 显式 id 锚定证据 | 状态 |
|---|---|---|---|
| prd2proto | product.prd-understanding | 零命中(实现于 reference/m01) | partially_implemented |
| prd2proto | product.user-story-mapping | 零命中 | partially_implemented |
| prd2proto | product.information-architecture | 零命中 | partially_implemented |
| prd2proto | product.interaction-state-coverage | 零命中 | partially_implemented |
| prd2proto | frontend.atomic-design | 零命中 | partially_implemented |
| prd2proto | frontend.design-token-rules | 零命中(reference/m04-token) | partially_implemented |
| prd2proto | frontend.component-state-rules | 零命中 | partially_implemented |
| prd2proto | frontend.code-quality-constitution | 零命中(constitution.md) | partially_implemented |
| prd2proto | design.design-strategy | 零命中 | partially_implemented |
| prd2proto | design.design-template-selection | 零命中(reference/design-templates) | partially_implemented |
| prd2proto | design.tone-and-visual-direction | 零命中 | partially_implemented |
| uxeval | ux.heuristic-principles | 零命中(reference/m02-启发式原则) | partially_implemented |
| uxeval | ux.journey-modeling | 零命中(reference/m03-旅程建模) | partially_implemented |
| uxeval | ux.evidence-quality | 零命中(reference/m05-证据采集) | partially_implemented |
| uxeval | ux.severity-rubric | 零命中 | partially_implemented |
| uxeval | ux.issue-attribution | 零命中(reference/m06-问题归因) | partially_implemented |
| uxeval | ux.ux-failure-modes | 零命中 | partially_implemented |
| uxeval | product.interaction-state-coverage | 零命中 | partially_implemented |
| ai-analytics | research.methodology-selection | 零命中(reference/m03) | partially_implemented |
| ai-analytics | research.competitor-analysis | 零命中(reference/m04) | partially_implemented |
| ai-analytics | research.user-persona-quality | 零命中 | partially_implemented |
| ai-analytics | research.data-completeness-rubric | 零命中 | partially_implemented |
| ai-analytics | design.design-strategy | 零命中 | partially_implemented |
| ai-analytics | design.tone-and-visual-direction | 零命中 | partially_implemented |
| ip-design | design.ip.methodology | tests=2(prompt 未直引) | partially_implemented |
| ip-design | design.strategy.brand-strategy-alignment | prompts+reference+tests+pipeline | implemented |
| ip-design | design.ip.worldview-building | prompts=2+reference+tests+pipeline | implemented |
| ip-design | design.persona.persona-modeling | prompts+reference+tests+pipeline | implemented |
| ip-design | design.persona.voice-and-behavior-boundary | prompts+reference+tests+pipeline | implemented |
| ip-design | design.visual.visual-translation | prompts+reference+tests+pipeline | implemented |
| ip-design | design.visual.image-prompt-system | prompts+reference+tests+pipeline | implemented |
| ip-design | design.ip.content-narrative | prompts+reference+tests+pipeline | implemented |
| ip-design | design.ip.brand-material-realization | prompts+reference+tests+pipeline | implemented |
| ip-design | design.quality.ip-design-quality-rubric | prompts+reference+tests+pipeline | implemented |
| ip-design | design.quality.stage-review-checklists | prompts+reference+tests+pipeline | implemented |
| ip-design | design.quality.common-failure-modes | prompts+reference+tests+pipeline | implemented |
| ip-design | design.quality.professional-gap-report | prompts+reference+tests+pipeline | implemented |
| ip-design | design.templates.brand-brief | prompts+reference+tests+pipeline | implemented |
| ip-design | design.templates.worldview | prompts+reference+tests+pipeline | implemented |
| ip-design | design.templates.persona-profile | prompts+reference+tests+pipeline | implemented |
| ip-design | design.templates.visual-spec | prompts+reference+tests+pipeline | implemented |
| ip-design | design.templates.content-plan | prompts+reference+tests+pipeline | implemented |
| ip-design | design.templates.brand-material-spec | prompts+reference+tests+pipeline | implemented |
| brand-creative | design.strategy.brand-strategy-methodology | 零命中 | declared_only |
| brand-creative | design.visual.logo-design-methodology | 零命中(sub-skill logo-design 有 pipeline) | declared_only |
| brand-creative | design.visual.logo-cognitive-translation | 零命中 | declared_only |
| brand-creative | design.visual.color-system-methodology | 零命中(sub-skill color-system 有 pipeline) | declared_only |
| brand-creative | design.visual.typography-system-methodology | 零命中(sub-skill 有 pipeline) | declared_only |
| brand-creative | design.visual.visual-identity-integration-methodology | 零命中(sub-skill 有 pipeline) | declared_only |
| brand-creative | design.strategy.brand-audit-methodology | 零命中(sub-skill brand-audit 无 pipeline) | declared_only |
| brand-creative | design.strategy.brand-voice-methodology | 零命中(sub-skill brand-voice 无 pipeline) | declared_only |
| brand-creative | design.quality.brand-identity-quality-rubric | tests=2 | partially_implemented |
| brand-creative | design.quality.brand-creative-failure-modes | 零命中 | declared_only |
| brand-creative | research.competitor-analysis | 零命中(sub-skill competitive-analysis 有 pipeline) | declared_only |
| brand-creative | design.persona.voice-and-behavior-boundary | 零命中 | declared_only |
| brand-creative | design.visual.image-prompt-system | 零命中 | declared_only |
| brand-creative | design.quality.professional-gap-report | 零命中 | declared_only |

## 2. Skill 级汇总矩阵

| skill | maturity | 声明 | implemented | partially | declared_only | runtime | 真质量门 | gate语义 | artifact-base |
|---|---|---|---|---|---|---|---|---|---|
| prd2proto | pilot | 11 | 0 | 11 | 0 | ✅ | ✅ quality_gates | quality_gates | 3/7 |
| uxeval | beta | 7 | 0 | 7 | 0 | ❌ | ❌ | gate(暂停门) | 0 |
| ai-analytics | pilot | 6 | 0 | 6 | 0 | ❌ | ❌ | gate(暂停门) | 0 |
| ip-design | pilot | 19 | 18 | 1 | 0 | ❌ | ❌ | gate(暂停门) | 0 |
| brand-creative | alpha | 14 | 0 | 1 | 13 | ❌ | ❌ | n/a(group) | unknown |

## 3. 关键计数

```
总声明资产(去重前)      : 57
显式 id 锚定 implemented  : 18  (全部来自 ip-design)
partially_implemented    : 25  (隐式 reference 实现,id 未锚定)
declared_only            : 13  (全部来自 brand-creative)
runtime 接入 skill        : 1/5 (prd2proto)
真 kernel 质量门接入       : 1/5 (prd2proto)
artifact-base 继承 schema  : 3   (全部来自 prd2proto, 占其 7 schema 的 43%)
```

---

*矩阵结束。判定口径与缺口分析见主报告 `S1-0B-DECLARED-VS-IMPLEMENTED-COVERAGE.md`。*
