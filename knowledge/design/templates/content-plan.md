# 模板:Content Plan（M05 产出物）

> 通用模板 · `design.templates.content-plan` · status: pilot

```yaml
content_plan:
  meta:
    project: ""
    version: "0.1.0-draft"
    upstream:
      brand_brief_ref: ""
      persona_ref: ""

  ip_debut:                  # 首秀(必)
    appearance_form: ""      # 行动 / 台词 / 困境 / 反差
    scene:
      time: ""
      place: ""
      background: ""
    trigger: ""              # 用户何时首次见到 IP
    first_line: ""           # 第一句台词,必须体现人格
    debut_goal: ""           # 希望用户感受到什么

  core_events:               # ≥3 个核心事件,关系递进
    - id: "E1"
      stage: "建立信任"
      scene: ""
      challenge: ""
      process: ""
      emotional_gain: ""
      relationship_after: ""
    - id: "E2"
      stage: "深化关系"
      scene: ""
      challenge: ""
      process: ""
      emotional_gain: ""
      relationship_after: ""
    - id: "E3"
      stage: "默契与惊喜"
      scene: ""
      challenge: ""
      process: ""
      emotional_gain: ""
      relationship_after: ""

  dialogue_corpus:           # 对话语料库,≥6 场景含失败
    confirm: []
    executing: []
    done: []
    fail: []                 # 必填
    idle: []
    proactive_greeting: []
    suggest: []
    collaborate: []
    note: "与 voice_and_behavior 一致,不重新发明"

  content_matrix:            # 渠道矩阵
    - channel: ""
      content_type: ""
      frequency: ""
      theme_direction: ""
      target_user_match_rationale: ""

  cadence_calendar:          # 周期化节奏
    period_unit: "week"      # week / month
    schedule:
      - period: 1
        theme: ""
        channels: []
      - period: 2
        theme: ""
        channels: []

  inferences: []
  gaps: []
```

## 字段使用约束

- `ip_debut.first_line` 必体现人格(非泛泛打招呼)。
- `core_events` ≥ 3,关系状态递进不重复。
- `dialogue_corpus` 必含 `fail` 场景。
- `content_matrix` 每条必含 `target_user_match_rationale`。
- `cadence_calendar.schedule` ≥ 4 个周期,体现可持续节奏。

## 与下游契约

- `dialogue_corpus` 复用 voice-and-behavior 的语料,统一来源。
- `content_matrix` 渠道决定 M06 物料的尺寸/规格选取。
