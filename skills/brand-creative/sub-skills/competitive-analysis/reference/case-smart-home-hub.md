# Reference Case: Smart Home Hub Competitor Analysis

> 展示 observed / inferred / unknown 事实分级与 competitor_matrix 输出示例。

## 输入

```yaml
product_brief: |
  智能家居控制中心,面向家庭用户,支持语音/触控交互,整合主流智能设备。
  核心卖点:极简交互、家庭场景优化、全设备兼容。

target_market: "中国一线城市,家庭场景,25-40 岁中产阶级"

competitor_hints:
  - "小米智能家居中心,白色简洁风格,主打性价比"
  - "华为全屋智能,黑/金配色,高端定位"
  - "Apple HomeKit,极简设计,封闭生态"
```

## Stage 1 输出:competitor_raw_data

```json
{
  "competitors": [
    {
      "name": "小米智能家居中心",
      "visual_style_observed": "白色简洁风格",
      "visual_style_inferred": "米家 app 主色调橙色#FF6700,圆角卡片设计[inferred from 米家品牌基因]",
      "communication_observed": "主打性价比",
      "communication_inferred": "年轻化语调,重视社交媒体与米粉社区[inferred from 小米品牌传统]",
      "market_position_observed": "",
      "market_position_inferred": "面向性价比敏感用户,价格区间 ¥199-799[inferred]"
    },
    {
      "name": "华为全屋智能",
      "visual_style_observed": "黑/金配色",
      "visual_style_inferred": "科技感几何设计[inferred from 华为品牌视觉]",
      "communication_observed": "高端定位",
      "communication_inferred": "专业理性语调[inferred]",
      "market_position_observed": "高端定位",
      "market_position_inferred": "面向高收入家庭,价格区间 ¥1999+[inferred]"
    },
    {
      "name": "Apple HomeKit",
      "visual_style_observed": "极简设计",
      "visual_style_inferred": "白/灰配色,无衬线字体,卡片式布局[inferred from Apple 设计语言]",
      "communication_observed": "封闭生态",
      "communication_inferred": "品质/隐私导向传播[inferred]",
      "market_position_observed": "",
      "market_position_inferred": "面向 Apple 生态用户[inferred]"
    }
  ],
  "data_sufficiency": "partial",
  "gaps": [
    "visual_style 仅有基础描述,缺少辅助图形/图标风格",
    "communication 无具体渠道与语料样例"
  ]
}
```

## Stage 2 输出:competitor_matrix

```json
{
  "competitors": [
    {
      "name": "小米智能家居中心",
      "visual_style": "白色机身+橙色点缀#FF6700,圆角卡片设计,线性图标辅助[部分 inferred]",
      "communication": "年轻化亲和语调,主打性价比,重视社交媒体传播[部分 inferred]",
      "market_position": "面向性价比敏感用户,价格区间 ¥199-799[inferred]"
    },
    {
      "name": "华为全屋智能",
      "visual_style": "黑/金配色,科技感几何设计[部分 inferred]",
      "communication": "专业理性语调,高端定位[部分 inferred]",
      "market_position": "面向高收入家庭,价格区间 ¥1999+[inferred]"
    },
    {
      "name": "Apple HomeKit",
      "visual_style": "白/灰极简配色,无衬线字体,卡片式布局[部分 inferred]",
      "communication": "品质/隐私导向,封闭生态传播[部分 inferred]",
      "market_position": "面向 Apple 生态用户,价格区间 ¥1499+[inferred]"
    }
  ],
  "status": "complete"
}
```

## Stage 2 输出:market_gap_report

```markdown
# 市场空白报告

## Gap 1: 温暖亲和的视觉语言

**维度**: visual

**描述**:
竞品小米/华为/Apple 分别采用橙色科技感、黑金高冷、白灰极简风格,
均为冷静理性或科技导向视觉语言。
市场空白:温暖亲和的家庭化视觉,可用暖黄/米色+有机圆润形态,
强化"家的温度"情感连接。

**证据**:
- product_brief 强调"家庭场景优化"(observed)
- 竞品视觉均为科技/性价比导向,缺少情感温度(observed + inferred)
- target_market 为家庭中产阶级,对"家"的情感价值敏感(observed)

---

## Gap 2: 传播策略具体渠道

**维度**: communication

**描述**:
insufficient data on competitor specific communication channels and content strategy.
gap identification requires: competitor_hints 包含传播渠道(KOL/社区/内容形式)资料。

**当前可推断**:
小米重视米粉社区,Apple 重视隐私叙事,但具体内容策略/KOL 合作/用户运营无足够证据。
```

## 关键示范点

1. **事实分级**:
   - `白色简洁风格`(observed,用户直接提供)
   - `橙色#FF6700,圆角卡片`(inferred,基于米家品牌基因推断)
   - 传播渠道具体策略(unknown,标注 insufficient data)

2. **visual_style 完整性**:每个竞品至少包含色彩/形态/辅助图形三要素

3. **market_gap 证据链**:Gap 1 有明确证据(product_brief + 竞品观察);Gap 2 证据不足,明确标注

4. **[inferred] 标注**:在 competitor_matrix 中追加 `[部分 inferred]`,在 market_gap_report 中说明推断依据