# Failure Case: 北极星功能化(F-S1)

本 failure case 演示失败模式 F-S1:北极星写成功能动作,缺失情感/体验价值。

## 输入

同 golden case。

## 错误产出(failure)

```yaml
north_star:
  statement: "帮企业员工调用集团 AI 能力。"
  five_elements:
    user_object: "企业员工"
    method: ""
    capability: "调用集团 AI"
    value: "调用 AI"  # 功能动作,非情感价值
    result: ""
  is_emotional_value: false  # 违反必过项
  rationale: ""
```

## 为什么失败

- `value` 字段写成"调用 AI"等功能动作,不是情感/体验价值。
- `is_emotional_value: false` 违反 M01 必过项:"北极星必须落在情感/体验价值"。
- Stage 1 Checkpoint C1 不应放行此产出。

## 断言(failure 检测)

- `north_star.is_emotional_value == false` → 判定失败
- `north_star.five_elements.value` 含"调用""执行""写周报"等功能动词 → 判定失败
