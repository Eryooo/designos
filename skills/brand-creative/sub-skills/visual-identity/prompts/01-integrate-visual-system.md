# Stage: integrate_visual_system

做资深设计总监式一致性判断：检查 logo / color / typography 三个子系统之间的一致性、冲突与缺口。

## 输入

- `visual_spec`: Logo 设计规范（来自 logo-design）
- `color_palette`: 品牌色彩调色板（来自 color-system）
- `typography_spec`: 字体系统规范（来自 typography-system）

## 任务

**你的任务不是重新设计视觉系统，而是作为资深设计总监做聚合判断。**

### 1. 气质一致性检查

对比三者的品牌语义层：

| 维度 | Logo 信号 | Color 信号 | Typography 信号 | 一致？ |
|---|---|---|---|---|
| 品牌人格 | visual_spec.form.rationale 传达的气质 | color_palette.primary.role 传达的情绪 | typography_spec.primary_font 传达的气质 | 判断 |
| 专业度 | 几何/有机/混合 | 冷色/暖色/中性 | 衬线/无衬线/手写 | 判断 |
| 动态感 | 对称/非对称/开放/封闭 | 高饱和/低饱和/渐变 | 字重对比/字号级差 | 判断 |

**判断标准**：
- 三者指向同一品牌人格 → consistent
- 轻微偏差但不冲突 → minor_deviation（标注，保留）
- 明显冲突（如 logo 极简几何 + color 浓烈热情 + 字体手写随性）→ conflict（降级 + 返工建议）

### 2. 技术一致性检查

- logo.color_refs 是否出现在 color_palette.primary/secondary 中？
- logo.min_size_px 与 typography 字号最小值是否兼容？
- color_palette.accessibility 标准是否同步应用于 logo 应用场景？
- typography.cross_platform 覆盖是否与 logo 应用场景一致？

### 3. 上游警告继承

扫描三个输入，收集所有待确认项：
- visual_spec.trademark_risk_signals（非空 → 继承）
- color_palette.accessibility == "needs_manual_check"（→ 继承）
- color_palette.print_color_risk（非空 → 继承）
- typography_spec.license_status == "needs_verification"（→ 继承）

### 4. 缺口识别

以下情况标记为 gap：
- 任一输入缺失（如 visual_spec 为空 → gap: "logo-design 未产出"）
- 一致性检查发现 conflict
- 上游 needs_verification / needs_manual_check 项

## 禁止事项

- **不得重新生成** logo / 色彩 / 字体方案
- **不得覆盖**上游产物的任何字段
- **不得声称**已完成法务/印刷/授权确认
- **不得吞掉缺口**：任何不确定项必须显式输出

## 输出

```json
{
  "consistency_check": {
    "personality_alignment": "consistent | minor_deviation | conflict",
    "personality_detail": "三者气质分析说明",
    "technical_alignment": "consistent | minor_deviation | conflict",
    "technical_detail": "技术兼容性说明",
    "conflict_resolution": ["如有冲突的处理建议"]
  },
  "inherited_warnings": [
    "logo: trademark_risk_signals 非空，需专业商标检索",
    "color: accessibility needs_manual_check",
    "typography: license needs_verification"
  ],
  "gaps": [
    "字体授权未确认，不可直接商用",
    "印刷色值未经打样验证"
  ],
  "auxiliary_graphics_direction": "从 logo mother_shape 提炼的辅助图形方向"
}
```

## 质量自检

- [ ] 三者气质一致性已判断（consistent / minor_deviation / conflict）？
- [ ] 技术兼容性已检查（色彩引用 / 尺寸兼容 / 跨端覆盖）？
- [ ] 上游所有 needs_verification / needs_manual_check / risk_signals 已继承？
- [ ] 缺口已显式输出（gaps 不为空）？
- [ ] 未重新生成或覆盖上游产物？
- [ ] 未声称已完成法务/印刷/授权确认？

## 如果上游缺失

若任一必需输入为空或格式错误：
```json
{
  "consistency_check": { "status": "incomplete", "missing": ["visual_spec"] },
  "inherited_warnings": [],
  "gaps": ["logo-design 未产出 visual_spec，无法完成 VI 聚合"],
  "auxiliary_graphics_direction": null
}
```
下游 generate_vi_manual 会产出降级版本并在 gaps 中声明。
