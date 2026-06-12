# Failure Case: 仅 MBTI 标签(F-P1)

本 failure case 演示失败模式 F-P1:人格建模只贴 MBTI 标签,无行为模式序列。

## 输入

```yaml
brand_brief:
  personality_keywords:
    - keyword: "主动"
    - keyword: "结果导向"
```

## 错误产出(failure)

```yaml
persona_profile:
  behavior_model:
    sequence: []  # 空,违反必过项
    observable_signals: []
    rationale: ""
  
  mbti_aux:
    type: "ESTJ"
    dimensions:
      EI: "外向主动"
      SN: "务实"
      TF: "理性"
      JP: "计划型"
    note: "MBTI 仅作辅助语言,主体是 behavior_model"  # 保留但实际未做
```

## 为什么失败

- `behavior_model.sequence` 为空,违反 M03 必过项:"行为模式序列不能为空且每步有可观测信号"。
- 只有 MBTI 标签,无可观测行为模式,不符合"行为模式为主 MBTI 仅辅助"。
- Stage 3 Checkpoint C3 不应放行此产出。

## 断言(failure 检测)

- `behavior_model.sequence == []` 或长度 < 3 → 判定失败
- `behavior_model.observable_signals == []` → 判定失败
