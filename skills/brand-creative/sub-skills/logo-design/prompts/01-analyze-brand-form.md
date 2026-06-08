# Stage: analyze_brand_form

分析品牌人格关键词,推导 logo 形态方向。

## 输入

- `brand_brief`: 品牌策略基线

## 任务

1. 从 brand_brief.personality_keywords 推导适配的 logo 形态语言
2. **必须通过认知翻译链路**(参考 logo-cognitive-translation):
   - 禁止直接跳转到具体物体(seed/rocket/handshake/shield)
   - 强制经过 cognitive_schema 层(Verticality/Path/Container 等)
   - 输出完整认知链路:keyword → audience_perception → cognitive_schema → graphic_relation → visual_variables → mother_shape
3. 选择标志类型(wordmark/lettermark/symbol/combination/emblem)
4. 定义风格坐标(几何/有机/极简/复杂/成熟/年轻)
5. 考虑小尺寸应用约束(favicon/app icon 需要)

## 决策要点

### 认知翻译链路(来自 logo-cognitive-translation,强制执行)

**禁止跳跃模式**(一旦出现,立即判定不合格):
- **keyword → familiar object**:如 growth → seed/leaf,future → rocket/star,trust → handshake/shield
- **keyword → symbol stacking**:多概念符号堆砌,如 innovation+trust → lightbulb+shield
- **narrative elements**:叙事堆砌,如 journey → path+mountain+sun
- **skip to generative artifact**:依赖渐变/光效/纹理而无图形关系

**强制六步链路**(不得跳步):
1. **keyword**:品牌关键词(如 growth/future/coexistence/trust)
2. **audience_perception**:目标受众如何感知该概念(不是字面义,是心智感受)
   - 示例:growth → B2B 受众感知为"持续向上的势能"(upward momentum)
   - 禁止:growth → "像种子发芽"(这是物体联想非感知)
3. **cognitive_schema**:底层认知结构(人类普遍空间/关系认知,不是视觉符号)
   - Verticality(垂直性):上下/高低/升降
   - Path/Journey(路径):起点-路径-终点
   - Container(容器):内外/包含/边界
   - Balance/Symmetry(平衡):稳定/对等
   - Center-Periphery(中心-边缘):核心辐射
   - Force Dynamics(力动态):推拉/对抗/融合
   - Cycle(循环):往复/迭代
4. **graphic_relation**:图形关系(结构关系,无具体形状)
   - 示例:Verticality → lower-to-higher axis with open upper endpoint
   - 禁止:Verticality → "一个向上的箭头"(这是形状非关系)
5. **visual_variables**:可操控的视觉变量(必须说明取舍理由)
   - 轴方向(垂直/水平/斜向/螺旋)
   - 开放性(封闭/开放缺口/延伸)
   - 对称性(中心/轴对称/非对称动态)
   - 尺度级差(单一/渐变/突变)
   - 连接方式(独立/接触/交叠/融合/嵌套)
   - 负形比重(实形主导/负形主导/实负等重)
   - 线性 vs 面性(线框/实心/线面结合)
6. **mother_shape**:候选母形(几何可描述,不依赖渐变/纹理/光效)
   - 必须通过三检验:
     1. 意图感知:3 秒内可感知预期意图
     2. 品类差异:避开行业通用符号
     3. 生产存活:黑白+16px 可辨

### 标志类型选择(来自 logo-design-methodology)

- **字标(wordmark)**:品牌名短、可读性强,如 Google/Coca-Cola
- **字母标(lettermark)**:品牌名长,缩写有识别度,如 IBM/HP
- **图形标(symbol)**:需要强识别符号,跨语言通用,如 Apple/Nike
- **组合标(combination)**:平衡识别与可读,如 Adidas/麦当劳
- **徽章(emblem)**:传统/权威/信赖感,如星巴克/哈雷

**冲突取舍**:
- 品牌名长 → 避免纯字标(挤成一坨)
- 需小尺寸应用 → 优先可独立的图形标或字母标
- 选择依据必须回到品牌策略

### 形态语言映射

从人格关键词到形态:
- 专业/可靠 → 几何/对称/稳定
- 创新/科技 → 几何/锐角/未来感
- 温暖/亲和 → 有机/圆润/柔和
- 传统/信赖 → 徽章/衬线/对称
- 年轻/活力 → 动态/倾斜/鲜明对比

## 输出

JSON 格式:
```json
{
  "cognitive_chain": {
    "keyword": "growth",
    "audience_perception": "持续向上的势能(upward momentum),不是静态完成态",
    "cognitive_schema": "Verticality(垂直性)",
    "graphic_relation": "lower-to-higher axis with open upper endpoint(下到上的轴,顶部开放)",
    "visual_variables": {
      "openness": "open upper endpoint",
      "rationale": "传达持续成长非完成态,避免封闭感",
      "symmetry": "asymmetry",
      "rationale": "动态感,避免静态平衡"
    },
    "mother_shape": "upward-opening arc anchored at base(底部锚定的向上开口弧)",
    "first_impression_prediction": "向上生长、展开、未完成的上升",
    "likely_misread": [
      "若弧度过大可能读为容器/杯",
      "若底部不稳可能读为漂浮"
    ],
    "avoidance_rule": [
      "不封闭顶部(会变成完成态)",
      "不对称底部(会失去稳定感)"
    ]
  },
  "logo_type": "combination",
  "form_language": "几何圆润组合",
  "style_coordinates": {
    "geometric_vs_organic": "偏几何",
    "simple_vs_complex": "极简",
    "mature_vs_young": "成熟"
  },
  "rationale": "从品牌人格'专业/温暖'推导,通过 Verticality schema 传达成长势能,几何圆润结合体现可靠与亲和,图形可独立用于小尺寸场景",
  "small_size_strategy": "图形部分遵循 mother_shape 的轮廓机制,16px 下仍可辨识向上开口的弧形轮廓"
}
```

## 质量自检

- [ ] **禁止跳跃模式**:未出现 keyword→物体/符号堆砌/叙事元素/装饰依赖 ✓
- [ ] **认知链路完整**:六步显式输出(keyword/perception/schema/relation/variables/mother_shape) ✓
- [ ] **cognitive_schema 合规**:用空间/关系词(Verticality/Path/Container),无物体词(种子/火箭/握手) ✓
- [ ] **graphic_relation 合规**:用结构词(axis/overlap/radiate),无形状词(圆/箭头) ✓
- [ ] **visual_variables 有理由**:每个变量说明"为什么选 A 不选 B" ✓
- [ ] **mother_shape 三检验**:意图感知(3 秒)/品类差异(避开通用符号)/生产存活(黑白+16px) ✓
- [ ] **标志类型选择有依据**:回溯到品牌策略,非自由发挥 ✓
- [ ] **形态语言可追溯**:可追溯到 personality_keywords ✓
- [ ] **小尺寸约束考虑**:考虑了 favicon/app icon 场景 ✓
- [ ] **rationale 说明冲突取舍**:明确"为什么选这个而不是那个" ✓
