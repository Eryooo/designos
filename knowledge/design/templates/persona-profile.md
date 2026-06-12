# 模板:Persona Profile（M03 产出物）

> 通用模板 · `design.templates.persona-profile` · status: pilot
> M03 人格 + 声音边界的填空骨架。MBTI 仅辅助,行为模式为主。

```yaml
persona_profile:
  meta:
    project: ""
    version: "0.1.0-draft"
    upstream:
      brand_brief_ref: ""
      worldview_ref: ""

  behavior_model:            # 主:可观测行为模式序列(必)
    sequence: []             # 例如 ["识别需求","拆解任务","执行调度","结果提升"]
    observable_signals:      # 每步骤的可观测信号
      - step: ""
        signal: ""           # 用户能看到/感知到什么
        scenario_example: ""
    rationale: ""            # 为什么是这条序列

  mbti_aux:                  # 辅:仅作沟通辅助语言,不可作为唯一依据
    type: ""                 # 允许融合型,如 "ESTJ × INFJ"
    dimensions:
      EI: ""                 # 简短说明该维度如何体现在行为模式中
      SN: ""
      TF: ""
      JP: ""
    note: "MBTI 仅作辅助语言,主体是 behavior_model"

  motivation_and_fear:
    core_desire: ""          # 核心欲望
    fears:                   # 核心恐惧分层
      capability_fear: ""    # 能力恐惧
      understanding_fear: "" # 理解恐惧
      value_fear: ""         # 价值恐惧
      safety_fear: ""        # 安全恐惧
    fear_responses:          # 每个恐惧的应对方式与可视化提示
      - fear: ""
        response: ""
        visual_cue: ""       # 与 M04 状态延展对齐
    hidden_flaw: ""          # 隐秘缺陷,让角色立体

  growth_arc:                # 成长弧三阶段(必)
    initial_state:
      capability: ""
      personality: ""
      relationship_with_user: ""
    key_event:
      trigger: ""            # 必须有合理触发
      process: ""
      change_point: ""
    transformed_state:
      new_capability: ""
      new_personality: ""
      new_relationship: ""

  voice_and_behavior:        # 声音与行为边界(必)
    catchphrases:            # 口头禅 2-3 个
      - ""
    scene_phrases:           # ≥6 场景含失败
      ack: []
      executing: []
      done: []
      fail: []               # 必填,失败话术
      idle: []
      suggest: []
      collaborate: []
    emotion_expressions:     # 情绪 × 语言 × 视觉(与 M04 状态延展对齐)
      - emotion: ""
        language_form: ""
        visual_cue: ""
    context_tone:            # 语境分层
      technical: ""
      business: ""
      collaborative: ""
    behavior_red_lines:      # 行为红线(必,可判定)
      never_say: []
      never_do: []

  action_network:            # 行动元六角色
    subject: ""
    object: ""
    sender: ""
    receiver: ""
    helper: ""
    opponent: ""

  inferences: []
  gaps: []
```

## 字段使用约束

- `behavior_model.sequence` 不能为空,且每步必有可观测信号。
- `mbti_aux.note` 强制保留(防止被当成主依据使用)。
- `motivation_and_fear.fears` 至少含 2 类恐惧。
- `voice_and_behavior.scene_phrases` 必须含 `fail`。
- `behavior_red_lines` 必须可判定,不可为"要友好"等空话。
- `growth_arc.key_event.trigger` 不能为空。

## 与下游契约

- `behavior_model.sequence` 由 M04 视觉状态延展、M05 核心事件消费。
- `voice_and_behavior` 由 M05 内容、M06 传播语调消费。
- `emotion_expressions.visual_cue` 与 M04 状态延展一一对应。
