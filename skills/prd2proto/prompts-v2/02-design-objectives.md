# Prompt: 02 — Design Objectives Decomposition

**Stage**: `design-objectives`
**Phase**: 1 of 4 (Inputs & Foundation)
**Output**: `design_objectives` artifact
**Schema**: `kernel/contracts/artifacts/design-objectives.schema.json`

> **本 prompt 仅放规则、字段契约、判断准则、反模式与质量门，不放任何业务叙事案例**
> （不论真实或合成）。Archetype-specific 优先级引自
> `knowledge/design-work-paradigm/archetypes/README.md` §3，不在此展开。

---

## 1. Stage Role

You decompose the input PRD/brief into **measurable, prioritized,
downstream-binding objectives**, organized in four layers
(BG → PG → UG → EG) connected by an explicit derivation map.

This stage's output is the **objective contract** for stages 03~17;
goal layer errors propagate as systematic downstream errors.

---

## 2. Required Inputs

| Input | Source | Required |
|-------|--------|----------|
| `requirement_inventory` | Stage 01 | yes |
| `business_context` | Stage 01 (industry/market/stakeholder hints) | yes (or `[inferred]`) |
| `archetypes/README.md` §3 | Knowledge layer | yes (priority rules source) |

If `business_context` is missing, mark related fields `inferred: true` and
list in `gaps`.

---

## 3. Four-Layer Objective Model

```
BG (Business Goal)        — Why does the business invest in this?
    ↓
PG (Product Goal)         — What product capabilities serve the BG?
    ↓
UG (User Goal)            — What does the user want to accomplish? (JTBD)
    ↓
EG (Experience Goal)      — What measurable experience delivers the UG?
```

### Layer definitions

| Layer | Definition | Required relationship |
|-------|-----------|----------------------|
| `<business_goal_id>` | Business outcome with measurable metric + time window | top-level |
| `<product_goal_id>` | Product capability that drives BG (input metric) | `serves_business_goal` → `<business_goal_id>` |
| `<user_goal_id>` | JTBD: when `<situation>`, I want to `<action>`, so I can `<outcome>` | `supports_product_goal` → `<product_goal_id>` |
| `<experience_goal_id>` | Measurable, dimension-bound, derives from UES/HEART | `supports_user_goal` → `<user_goal_id>` |

### Derivation map (mandatory)

```yaml
goal_derivation_map:
  business_to_product:
    <business_goal_id>: [<product_goal_id>, ...]
  product_to_user:
    <product_goal_id>: [<user_goal_id>, ...]
  user_to_experience:
    <user_goal_id>: [<experience_goal_id>, ...]
```

A non-empty derivation map is **required**; empty maps fail quality gate.

---

## 4. Methodology Selection (rules, not cases)

For Experience Goals, select methodology by archetype:

| Archetype hint | Default methodology | Rationale (abstract) |
|----------------|---------------------|---------------------|
| `b2b-enterprise-workflow` / `internal-tool` | UES (efficiency-focused) | Non-voluntary use; growth metrics mislead |
| `b2c-consumer-product` | HEART | Voluntary use; happiness/engagement/retention apply |
| `b2b2c-platform` | Three-side hybrid (HEART for consumer side, UES for supplier/operator) | Multi-role goals require differentiated metrics |
| `content-community-product` | HEART + community-specific signals | Content engagement & UGC depth |
| `data-dashboard` | UES (task efficiency) + Performance | Decision-support tools, not entertainment |
| `ai-agent-product` (modifier) | Add AI-specific dimensions: trust, recoverability, transparency | Conversation + uncertainty |
| `brand-identity-brief` | Brand-specific: identifiability/memorability/extensibility | Not product engagement metrics |
| `hybrid-ambiguous` | Choose conservatively per dominant pattern; document choice | Ambiguity must not silently default |

Methodology must be declared in:
```yaml
experience_methodology:
  primary: <UES | HEART | hybrid | brand-specific>
  rationale: <reason tied to archetype, not narrative>
```

---

## 5. Format Skeletons (All Four Layers)

> These are **format骨架**, not business examples. They show the *shape* of a
> correct field, using `<placeholder>` tokens only. Never fill them with a
> specific product/company/IP/school/brand name.

### 5.1 Business Goal skeleton

```yaml
- id: <business_goal_id>            # e.g. BG-001
  statement: <measurable_business_outcome> by <time_window>
  metric: <number + unit + comparison>     # the north-star or input to it
  metric_type: north_star | input_metric | guardrail
  source: <source_requirement_id> | inferred
  rationale: <why this is a business outcome, not a feature>
```

- `statement` must be a business **outcome**, never a feature name.
- If derived without explicit PRD basis, set `source: inferred` and explain.

### 5.2 Product Goal skeleton

```yaml
- id: <product_goal_id>             # e.g. PG-001
  statement: <product_capability_that_drives_a_business_goal>
  serves_business_goal: <business_goal_id>   # exactly one, must exist
  input_metric: <number + unit + comparison> # leading indicator for the BG
  source: <source_requirement_id> | inferred
```

- `input_metric` is a **leading** indicator (product can move it directly),
  distinct from the BG's lagging outcome metric.

### 5.3 User Goal skeleton (JTBD)

```
when <user_situation_with_specific_trigger>,
I want to <user_intent_with_action_verb>,
so I can <user_value_outcome>
```

```yaml
- id: <user_goal_id>                # e.g. UG-001
  jtbd: "when <situation>, I want to <action>, so I can <outcome>"
  supports_product_goal: <product_goal_id>   # exactly one, must exist
  pain_points: [<current_friction>, ...]
  source: <source_requirement_id> | inferred
```

- `<situation>` — the trigger context (NOT a product feature)
- `<action>` — the user-side intent (verb-led, NOT a feature name)
- `<outcome>` — the value the user receives (NOT the product capability)

**Anti-pattern**: writing `<action>` as a feature name
(e.g. "I want to use feature X").

### 5.4 Experience Goal skeleton (GSM)

```yaml
- id: <experience_goal_id>          # e.g. EG-001
  goal: <single_sentence_desired_experience>
  signal: <observable_behavior_or_perception>
  metric: <number + unit + comparison>
  why_this_metric: <reason_connected_to_user_goal_and_archetype>
  supports_user_goal: <user_goal_id>          # exactly one, must exist
  dimension: <dimension_from_chosen_methodology>   # e.g. a UES/HEART dimension
```

`metric` must be:
- A measurable value (not a qualitative claim)
- Bound to a `dimension` from the chosen methodology
- Achievable per archetype norms (not arbitrary)

---

## 7. Archetype-Specific Priorities

Quote priorities from `archetypes/README.md` §3 for the chosen archetype.
Examples of priority structure (NOT business cases):

```yaml
archetype_priorities:
  business_goal_focus: [<dimension>, <dimension>, ...]
  product_goal_focus: [<dimension>, <dimension>, ...]
  user_goal_focus: [<dimension>, <dimension>, ...]
  experience_goal_focus: [<dimension>, <dimension>, ...]
```

For B2B2C, priorities **must be split into three role-sets**:
- `consumer_side`
- `supplier_side`
- `platform_operator_side`

---

## 8. Conflict Identification

Surface inter-goal conflicts explicitly:

```yaml
goal_conflicts:
  - between: [<goal_id_a>, <goal_id_b>]
    nature: <how they trade off>
    resolution_strategy: <prioritization rule based on archetype>
    accepted_loss: <what is sacrificed>
```

Common conflict patterns by archetype (rule, not case):
- B2B: efficiency vs. compliance
- B2C: growth vs. trust
- B2B2C: supplier value vs. consumer value vs. platform take rate
- AI-agent: speed vs. accuracy vs. transparency
- Brand: differentiation vs. familiarity

---

## 9. Output Schema (excerpt)

Conform to `kernel/contracts/artifacts/design-objectives.schema.json`.
Required top-level keys:

```yaml
business_goals: []        # min 1
product_goals: []         # min 1
user_goals: []            # min 1
experience_goals: []      # min 1
goal_derivation_map: {}   # required, non-empty
experience_methodology: {}
archetype_priorities: {}
goal_conflicts: []        # may be empty list, not omitted
```

---

## 10. Decision Rules

- ✅ Every PG must `serves_business_goal` → exactly one BG
- ✅ Every UG must `supports_product_goal` → exactly one PG
- ✅ Every EG must `supports_user_goal` → exactly one UG
- ✅ `goal_derivation_map` non-empty (≥1 entry per layer)
- ✅ Each EG has full GSM (`goal`, `signal`, `metric`, `why_this_metric`)
- ✅ Methodology choice tied to `primary_archetype` from stage 03
- ✅ For B2B2C, three role-sets must each have ≥1 UG and ≥1 EG
- ❌ Don't omit `archetype_priorities` (downstream stages require it)
- ❌ Don't use vague metrics ("better UX", "faster")
- ❌ Don't write JTBD with feature names
- ❌ Don't apply b2c HEART to internal-tool
- ❌ Don't apply b2b efficiency-only logic to b2c

---

## 11. Common Junior vs Senior

| Junior mistake | Senior correction |
|----------------|-------------------|
| Treats BG/PG/UG/EG as parallel labels | Enforces layered derivation; orphan EG without UG link is rejected |
| Methodology default to one (e.g. always HEART) | Methodology selected per `primary_archetype` |
| JTBD = feature description | JTBD = situation + intent + outcome (no feature names) |
| EG metric is qualitative | EG metric is measurable + dimension-bound |
| Conflicts hidden | Conflicts surfaced explicitly with resolution strategy |
| B2B2C modeled as single side | Three role-sets (consumer/supplier/operator) |
| `archetype_priorities` omitted | Quoted from `archetypes/README.md` §3 |

---

## 12. Quality Self-Check

Before emitting:

- [ ] All four layers non-empty
- [ ] `goal_derivation_map` non-empty in all three sub-maps
- [ ] Each EG has GSM (4 fields)
- [ ] Methodology declared with archetype-tied rationale
- [ ] `archetype_priorities` present and matches `archetypes/README.md` §3
- [ ] B2B2C → three role-sets present (if applicable)
- [ ] No business-narrative examples in any field
- [ ] No specific product/company/IP/school/brand names
- [ ] `bash scripts/security/scan-sensitive.sh --file <output>` returns 0 hits

---

## 13. Inference Boundary

This stage MAY infer:
- BG metrics when only qualitative business intent provided
  (mark `inferred: true` and explain in `rationale`)
- Methodology choice from archetype (per §4)
- Goal conflicts from cross-layer tensions

This stage MUST NOT infer:
- `primary_archetype` (consumed from stage 03; if missing, request rerun)
- User personas (left to stages relying on `requirement_inventory`)
- Specific UI/page structure (later stages)

---

## 14. Forbidden Behaviors

- ❌ Embedding any specific product/company/IP/school/brand/color name in any field
- ❌ Using business-narrative examples to "illustrate" reasoning
  (use `<placeholder>` form instead)
- ❌ Defaulting methodology when archetype clearly indicates otherwise
- ❌ Hiding inferred goals (must be marked `inferred: true`)
- ❌ Empty `goal_derivation_map` (passes schema but breaks downstream)
- ❌ Single-side modeling for B2B2C archetype

---

## 15. Downstream Constraints

Stages 04~17 will consume:
- `business_goals` / `product_goals` for traceability anchoring
- `user_goals` (JTBD) for stage 04 task modeling
- `experience_goals` (GSM) for stages 09~12 (state, interaction, page)
- `archetype_priorities` for archetype-aware reasoning
- `goal_derivation_map` for stage 16 traceability

Schema critical fields here drive **most** downstream schema dependencies.

---

## 16. Regeneration Triggers

The orchestrator MUST regenerate this stage's output (or request a rerun)
when any of these conditions hold. These are **quality gates that fail the
artifact**, not soft warnings:

| Trigger | Condition | Action |
|---------|-----------|--------|
| `missing_layer` | Any of BG/PG/UG/EG is empty | regenerate |
| `broken_derivation` | Any PG/UG/EG lacks a valid parent link, or parent id not found | regenerate |
| `empty_derivation_map` | `goal_derivation_map` empty in any sub-map | regenerate |
| `incomplete_gsm` | Any EG missing one of goal/signal/metric/why_this_metric | regenerate |
| `qualitative_metric` | Any metric lacks number+unit+comparison | regenerate |
| `methodology_mismatch` | Methodology contradicts `primary_archetype` (§4) | regenerate |
| `missing_priorities` | `archetype_priorities` absent | regenerate |
| `b2b2c_single_side` | Archetype is b2b2c but role-sets < 3 | regenerate |
| `pollution_detected` | `scan-sensitive` finds a hit, or any business-narrative example present | regenerate + flag |
| `confidence_low` | Self-assessed objective confidence < 0.6 | regenerate once; if still low → `human_review` |

Regeneration policy:
- Max 2 automatic regenerations per stage.
- On the 2nd failure, escalate to `human_review` with a structured
  `regeneration_report` listing which triggers fired and what was attempted.
- Never silently emit an artifact that fails a hard trigger
  (`missing_layer`, `broken_derivation`, `pollution_detected`).

---

**Version**: S0-v1.0 (2026-06-12 — Batch S0 refactor: removed all
business examples, replaced with abstract field contracts, methodology
selection now archetype-driven, B2B2C three-role-sets enforced)
