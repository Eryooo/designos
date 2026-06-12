# Stage: generate_logo_spec

产出 logo 设计规范,对齐 logo_spec.schema.json。

## 输入

- `form_direction`: 形态方向分析结果
- `brand_brief`: 品牌策略基线

## 任务

产出完整 logo 设计规范,包含:
1. **认知链路字段**(从 form_direction.cognitive_chain 继承,必须显式输出)
2. 形态方向与设计理由
3. 色彩参考(从品牌策略推导)
4. 黑白可用性验证
5. 最小可识别尺寸
6. 辅助图形方向
7. 商标风险信号
8. 应用场景

**关键要求**:
- 必须继承 form_direction 的 cognitive_schema / mother_shape / avoidance_rule
- 禁止在此阶段重新发明母形或跳跃到具体符号

## 关键约束(来自 logo-design-methodology)

### 1. 黑白可用性(硬约束,一票否决)

**必须先在纯黑白下成立,再考虑色彩。**

验证方法:
- 灰度模式:logo 转灰度后主体可识别
- 纯黑模式:logo 转纯黑(#000000)后轮廓清晰
- 反白模式:logo 反白(白色 logo + 深色背景)后可识别

**失败信号**:依赖颜色区分的元素,在灰度下糊成一团。
**返工条件**:重做至三模式均可识别。

### 2. 缩放与轮廓识别

**最小尺寸要求**:16×16px favicon 轮廓可辨(设为 min_size_px: 16 或更小)

验证方法:
- 剪影测试:遮住细节只看轮廓能否认出
- 小尺寸测试:16px 下是否需要简化版
- 大尺寸测试:招牌/包装尺寸下细节是否精致

**失败信号**:favicon 认不出,或大小尺寸像两个 logo。
**返工条件**:补简化版,16px 轮廓唯一可辨。

### 3. 组合形式与留白

定义:
- 横版锁版(horizontal lockup)
- 竖版锁版(vertical lockup)
- 纯图标版(icon only)
- 安全留白区(clear space,以 logo 某元素的 N 倍为单位)

### 4. 辅助图形系统

从 logo 提炼可延展的辅助图形(图案/纹理/分割线)。
**同源要求**:辅助图形与主 logo 共享形态语言,不是另起炉灶。

### 5. 商标风险信号(非法律意见)

检查并标注:
- 是否使用行业通用符号(如医疗十字/金融盾牌)
- 是否与知名品牌形态相似
- 是否含通用词汇

**必须声明**:"本信号非商标查重结果,logo 注册需专业商标机构检索。"

## 输出

严格对齐 logo_spec.schema.json,必须包含认知链路字段:

```json
{
  "cognitive_schema": "Verticality",
  "mother_shape": "upward-opening arc anchored at base",
  "first_impression_prediction": "向上生长、展开、未完成的上升",
  "likely_misread": [
    "若弧度过大可能读为容器/杯",
    "若底部不稳可能读为漂浮"
  ],
  "avoidance_rule": [
    "不封闭顶部(会变成完成态)",
    "不对称底部(会失去稳定感)"
  ],
  "form": {
    "primary_shape": "几何组合标:圆形图形+字标横排",
    "rationale": "从品牌人格'专业/温暖'推导,通过 Verticality schema 传达成长势能,几何圆润结合体现可靠与亲和..."
  },
  "color_refs": ["#0066CC", "#FFFFFF"],
  "black_white_usable": true,
  "min_size_px": 16,
  "auxiliary_graphics": [
    "从主图形圆角几何提炼的辅助网格图案",
    "可用于背景纹理与分割线的圆角矩形组合"
  ],
  "trademark_risk_signals": [
    "使用圆形几何为通用形态,建议在图形内增加差异化细节",
    "本信号非商标查重,logo 注册需专业商标机构检索"
  ],
  "application_scenarios": [
    "网站 header(横版,最小 120px 宽)",
    "favicon(纯图标版,16×16px)",
    "名片(横版,黑白可用)",
    "APP icon(纯图标版,iOS/Android 多尺寸)",
    "招牌/包装(大尺寸,展示细节)"
  ]
}
```

## 质量自检(对照 brand-creative-failure-modes)

- [ ] **F-LO1 黑白不可用**:灰/黑/白三模式均验证 ✓
- [ ] **F-LO2 小尺寸失效**:min_size_px ≤ 32 且有简化策略 ✓
- [ ] **F-X1 策略断链**:form.rationale 回溯到 brand_brief ✓
- [ ] **F-X2 过度承诺**:无"可注册/版权清洁/最终商用"声明 ✓
- [ ] **认知链路字段完整**:cognitive_schema / mother_shape / first_impression / likely_misread / avoidance_rule 全部输出 ✓
- [ ] **继承上游决策**:cognitive_schema / mother_shape 与 form_direction 一致 ✓
- [ ] 辅助图形与主 logo 同源 ✓
- [ ] 商标风险已标注 + 声明非查重 ✓
