# Visual Identity Integration Methodology

> DesignOS pilot synthesis — 聚合判断规则，非权威来源。

## purpose

定义 visual-identity 聚合层如何判断 logo / color / typography 三个子系统的一致性、如何处理冲突、如何产出质量门与缺口声明。

## applies_to

- brand-creative:visual-identity 子技能
- 任何需要将多个视觉子系统合并为统一品牌识别系统的场景

## decision_framework

### 聚合判断三层模型

#### 第一层：品牌语义一致性

三个子系统是否表达同一品牌人格？

| 检查项 | Logo 信号源 | Color 信号源 | Typography 信号源 |
|---|---|---|---|
| 品牌气质 | form.rationale / mother_shape | primary.role / 色彩情绪 | primary_font.family 气质 |
| 专业度 | 几何vs有机 | 冷暖饱和度 | 衬线vs无衬线 |
| 动态感 | 对称vs非对称 | 饱和度梯度 | 字重对比度 |

**判定规则**：
- 三者指向同一象限 → `consistent`
- 两者一致、一者偏离但不矛盾 → `minor_deviation`（标注保留）
- 两者以上互相矛盾 → `conflict`（降级 + 返工建议）

#### 第二层：技术兼容性

| 检查项 | 判定标准 | 失败处理 |
|---|---|---|
| 色彩引用 | logo.color_refs ⊆ color_palette.primary ∪ secondary | 不一致 → 标注 gap |
| 尺寸兼容 | logo.min_size_px 与 typography 最小字号可共存 | 冲突 → 标注 gap |
| 跨端覆盖 | typography.cross_platform 覆盖 logo 应用场景 | 缺失 → inherited_warning |
| 可访问性 | color.accessibility 标准同步应用于 logo 场景 | 未同步 → gap |

#### 第三层：上游警告继承

**强制继承规则**（不得过滤或降级）：

| 上游字段 | 触发条件 | 继承方式 |
|---|---|---|
| visual_spec.trademark_risk_signals | 数组非空 | 原样写入 inherited_warnings |
| color_palette.accessibility | == "needs_manual_check" | 写入 inherited_warnings |
| color_palette.print_color_risk | 非空 | 写入 inherited_warnings |
| typography_spec.license_status | == "needs_verification" | 写入 inherited_warnings |

### 冲突处理决策树

```
发现不一致
├── 是否影响品牌核心识别？
│   ├── 否 → minor_deviation，标注保留
│   └── 是 → conflict
│       ├── 哪个子系统偏离品牌策略？
│       │   ├── 可定位 → gaps 中写返工建议（指明子技能 + 返工方向）
│       │   └── 无法定位 → gaps 中写"需人工评审确认品牌方向"
│       └── 是否阻塞 VI 手册产出？
│           ├── 是 → 降级产出，gaps 声明无法达标
│           └── 否 → 产出但 consistency_check 标注 conflict
```

### 应用规范覆盖要求

VI 手册 application_rules 至少 5 个场景，每个场景必须交叉引用三个子系统：

| 场景 | 必须引用 Logo | 必须引用 Color | 必须引用 Typography |
|---|---|---|---|
| 名片 | 尺寸/位置/锁版 | 主色/辅色使用 | 字体/字号/字重 |
| 网站 | header 规格/favicon | 色彩系统/暗色模式 | web font/行高 |
| 社交媒体 | 头像用纯图标版 | 色彩适配暗色 | 可读性字号 |
| 包装 | 最小尺寸/CMYK | CMYK 色值/色差 | 印刷字体 |
| 海报 | 大尺寸细节展示 | 色彩氛围/大面积 | 标题字体/层级 |

## quality_rubric

| 维度 | 高阶(8-10) | 中阶(5-7) | 低阶(0-4) |
|---|---|---|---|
| 一致性判断 | 三层模型全部判断且有依据 | 判断了但依据不足 | 未做一致性检查 |
| 冲突处理 | 明确策略 + 返工建议 | 标注了但无建议 | 吞掉冲突 |
| 应用规范 | ≥5场景且交叉引用 | 3-4场景 | <3场景或无交叉引用 |
| 缺口声明 | 完整继承 + pilot 边界 | 部分继承 | 吞掉缺口 |

## common_failure_modes

| 失败模式 | 表现 | 检测信号 | 防线 |
|---|---|---|---|
| 拼接而非聚合 | 直接复制三份 JSON 无判断 | consistency_check 为空或 "all good" | 强制非空 + 必须有维度判断 |
| 吞掉缺口 | inherited_warnings 为空但上游有 needs_verification | gaps 为空 | 测试强制检查上游警告继承 |
| 覆盖上游 | vi_manual 产出后上游 state 被修改 | 测试断言上游不变 | constitution 一票否决 |
| 过度承诺 | 声称"最终商用""商标已确认" | 关键词扫描 | constitution 禁止 + 测试检测 |
| 假装完整 | 缺少上游输入但不声明 | 缺失输入时 gaps 为空 | prompt 降级行为 + 测试验证 |

## do_not_claim

- 不声称 VI 手册已覆盖所有应用场景
- 不声称已达"高阶可评审"（默认中阶可用）
- 不声称已完成法务/印刷/字体授权确认
- 不声称是最终品牌手册（brand-guidelines 才是最终交付物）
- 不声称一致性检查可替代资深设计总监人工评审
