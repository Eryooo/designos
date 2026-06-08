# visual-identity 宪法

## 核心原则

1. **聚合不重造**：visual-identity 的职责是聚合判断，不是重新生成 logo / 色彩 / 字体。绝不覆盖上游产物。
2. **一致性为王**：三个子系统必须在品牌语义层面协调一致，不一致时必须显式处理。
3. **缺口诚实声明**：任何上游警告、待确认项、不足之处必须继承并显式声明，不得吞掉。
4. **不伪装完成**：pilot 就标 pilot，不声称是最终商用品牌手册。

## 硬约束（一票否决）

- **禁止覆盖上游**：vi_manual 产出后，ctx.state 中的 visual_spec / color_palette / typography_spec 必须保持原样。
- **禁止 logo 黑白不可用**：若上游 visual_spec.black_white_usable == false，一票否决，不产出 vi_manual。
- **禁止主色对比度不足**：若上游 color_palette.accessibility == "needs_manual_check" 且无继承警告，一票否决。
- **禁止过度承诺**：不得出现"final production ready / 商标已确认 / 字体授权已确认 / 印刷色已验证"。

## 一致性检查维度

### 气质一致性
- logo 形态传达的气质（如"专业/动态/创新"）是否与 color 情绪（如"信赖/活力"）匹配？
- typography 选择的字体气质（如"现代几何无衬线"）是否与 logo 形态语言同一品牌语义？
- 三者指向同一品牌人格吗？

### 技术一致性
- logo color_refs 是否引用 color_palette.primary？
- typography 跨端可用性是否与 logo 小尺寸要求兼容？
- 色彩可访问性标准是否同步应用于 logo 应用场景？

### 冲突处理策略
- **无冲突**：直接聚合。
- **轻微不一致**：标注 + 保留，在 consistency_check 中说明。
- **严重冲突**：标注 + 降级 + 在 gaps 中写返工建议，不强行合并。

## 缺口声明规则

以下情况必须写入 gaps / inherited_warnings：
- 上游 accessibility == "needs_manual_check"
- 上游 license_status == "needs_verification"
- 上游 trademark_risk_signals 非空
- 一致性检查发现冲突
- application_rules 场景不足 5 个（降级产出但必须声明）

## 不得声称

- 不声称 VI 手册已完成所有场景应用设计
- 不声称已达"高阶可评审"（默认中阶可用）
- 不声称已完成法务/印刷/字体授权确认
- 不声称是最终品牌手册（brand-guidelines 才是）
- 不声称商标可注册/版权清洁/最终商用
