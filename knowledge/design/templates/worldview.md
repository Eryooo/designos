# 模板:Worldview（M02 产出物）

> 通用模板 · `design.templates.worldview` · status: pilot
> M02 世界观构建法的填空骨架。每字段对应 `design.ip.worldview-building` 必过项。

```yaml
worldview:
  meta:
    project: ""
    version: "0.1.0-draft"
    upstream:
      brand_brief_ref: ""    # 指向上游 M01 brief

  spacetime:
    era: ""                  # 古/今/未来/架空
    space_type: ""           # 物理/虚拟/混合
    core_locations:          # 3-5 个核心场所
      - name: ""
        atmosphere: ""
        function: ""

  rules:
    energy_rules:            # 能量规则
      sources: []
      consumption: ""
      cap: ""
    capability_rules:        # 能力规则
      can_do: []
      cannot_do: []          # 必须显式列出"不能做什么"
      growth_path: ""
    social_rules:            # 社会规则
      relationships: []
      position: ""
      conflict_sources: []   # 不能为空,必须有冲突来源

  relationship_network:      # 行动元六角色
    subject: ""              # 主体(IP)
    object: ""               # 客体(目标)
    sender: ""               # 发送者
    receiver: ""             # 接收者
    helper: ""               # 辅助者
    opponent: ""             # 反对者(必填)
    diagram_format: "mermaid"  # 关系图表达形式

  cultural_archetype:
    type: ""                 # 武侠/西游/赛博朋克/原创等
    core_imagery: []         # 3-5 个核心意象词
    transformation_logic: "" # 原型如何服务北极星

  worldview_keywords:        # 3-5 个,供 M04 消费
    - ""

  consistency_check:         # 自洽校验
    rules_self_consistent: true   # 规则之间无矛盾
    capability_has_boundary: true # 能力有边界

  inferences: []
  gaps: []
```

## 字段使用约束

- `capability_rules.cannot_do` 不能为空。
- `social_rules.conflict_sources` 不能为空。
- `relationship_network.opponent` 不能为空。
- `worldview_keywords` 数量 3–5。
- `consistency_check` 任一为 false → 不允许进入 M04。

## 与下游契约

- `worldview_keywords` 由 M04 视觉转化消费。
- `cultural_archetype` 由 M04 材质 / M05 内容叙事消费。
- `relationship_network` 由 M03 人格关系网络回扫使用。
