# Failure Case: 32px 糊掉(F-V2)

本 failure case 演示失败模式 F-V2:小尺寸下形象不可辨,无四级简化。

## 输入

```yaml
persona_profile:
  behavior_model:
    sequence: ["识别","拆解","执行","提升"]
brand_brief:
  personality_keywords: [{keyword: "稳定"}]
```

## 错误产出(failure)

```yaml
visual_spec:
  shape_design:
    core_symbol:
      name: "复杂徽章"
      visual_weight_pct: 60
      description: "含多层细节与文字的徽章"
  
  recognizability:
    canonical_test:
      legible_at_32px: false  # 违反必过项
      remote_silhouette_recognizable: false
    size_tiers:
      large_ge_128px: {spec: "完整徽章"}
      mid_48_to_128: {spec: ""}  # 空
      small_24_to_48: {spec: ""}  # 空
      tiny_lt_24: {spec: ""}  # 空,四级未齐全
```

## 为什么失败

- `recognizability.canonical_test.legible_at_32px: false` 违反 M04 必过项:"核心符号 32px 下必须可辨"。
- `size_tiers` 只填了 `large_ge_128px`,其余三级为空,违反"四级简化齐全"必过项。
- Stage 4 Quality Gate QG1 不应放行此产出。

## 断言(failure 检测)

- `recognizability.canonical_test.legible_at_32px == false` → 判定失败
- `size_tiers.mid_48_to_128.spec == ""` 或任一 tier 为空 → 判定失败
