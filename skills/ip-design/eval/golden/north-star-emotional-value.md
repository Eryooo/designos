# Golden Case: 北极星情感价值

本 golden case 演示正确的北极星写法:含五要素且落在情感/体验价值。

## 输入

```yaml
product_brief: "企业 AI 助理,帮员工快速调用集团 AI 能力完成办公任务。"
target_user: "企业员工,职业:知识工作者/管理者,场景:日常办公,痛点:AI 工具太多难选、调用复杂"
```

## 期望产出(golden)

```yaml
north_star:
  statement: "让企业员工像点按钮一样调用集团 AI 能力,把复杂办公任务快速变成可用结果。"
  five_elements:
    user_object: "企业员工"
    method: "像点按钮一样"
    capability: "调用集团 AI 能力"
    value: "把复杂变简单"  # 情感/体验价值
    result: "可用结果"
  is_emotional_value: true
  rationale: "价值落在'把复杂变简单'的体验层,不是功能动作。"
```

## 断言

- `north_star.five_elements` 五字段齐全
- `north_star.is_emotional_value == true`
- `north_star.five_elements.value` 不含"调用""执行""写"等功能动词,含"简单""信任""掌控""安心"等情感/体验词
