# typography-system Constitution

本文件定义 typography-system 子技能的运行时强制约束(runtime hard constraints)。

## 1. 字体角色与配对规则(Font Role & Pairing Rules)

### 1.1 主辅字体配对

**强制要求:**
- `primary_font` 必须存在(标题/品牌展示)
- `secondary_font` 可选(正文/功能文本)
- 如果只有一个字体家族,必须在 `typography_direction` 中说明理由

**配对原则:**
- 主字体可个性化(品牌识别度优先)
- 辅助字体必须易读(功能性优先)
- 两者在字重/字面/重心上需协调

### 1.2 中西文配对(CJK-Latin Pairing)

**触发条件:**
- 品牌面向中文市场或多语言市场

**强制要求:**
- `cjk_latin_pairing` 字段必须存在且非空
- 必须说明中西文在字重/字面/重心上的协调方式
- 必须检测中西文配对失衡风险(如中文粗西文细)

**示例:**
```json
{
  "cjk_latin_pairing": "中文采用思源黑体(Medium),西文采用 Inter(Medium),两者字重/字面匹配,中英混排视觉重量协调"
}
```

**失败信号(F-TY2):**
- `cjk_latin_pairing` 缺失
- 中西文字重明显不匹配(如中文 Bold 配西文 Light)

## 2. 字重层级约束(Weight Hierarchy Constraints)

### 2.1 数量与区分度

**强制要求:**
- `weight_hierarchy` 必须 3-4 个字重
- 相邻字重必须可明显区分(避免 Regular 与 Medium 难辨)
- 不得超过 5 个字重(过载会导致层级混乱)

**示例:**
```json
{
  "weight_hierarchy": ["Light", "Regular", "Medium", "Bold"]
}
```

### 2.2 禁止模式

**禁止:**
- ❌ 只有 1-2 个字重(层级不足)
- ❌ 6 个以上字重(过载)
- ❌ 相邻字重视觉差异过小

## 3. 字号比例约束(Size Scale Constraints)

### 3.1 模块化比例

**强制要求:**
- 采用模块化比例(1.25 / 1.333 / 1.414 / 1.5 / 1.618 等经典比例)
- 相邻字号比值必须一致(形成和谐梯度)
- 定义最小可读字号(正文不小于平台可读下限)

**示例(1.25 比例):**
```json
{
  "size_scale": [12, 15, 18.75, 23.44, 29.3, 36.63],
  "scale_ratio": 1.25,
  "min_readable_size": 12
}
```

### 3.2 验证标准

字号梯度必须通过以下测试:
1. **一致性测试**: 相邻字号比值是否一致
2. **可读性测试**: 最小字号是否 >= 平台可读下限(Web: 12px, iOS/Android: 11pt)
3. **和谐性测试**: 比例是否为经典模块化比例

## 4. 行高与间距约束(Line Height & Spacing Constraints)

### 4.1 行高定义

**强制要求:**
- `line_height` 必须分别定义正文与标题
- 正文行高通常 1.4-1.6 倍字号
- 标题行高可紧凑(1.1-1.3 倍)
- 中文行高需大于西文(中文字面满,需更多呼吸)

**示例:**
```json
{
  "line_height": {
    "body": { "cjk": 1.6, "latin": 1.5 },
    "heading": { "cjk": 1.3, "latin": 1.2 }
  }
}
```

### 4.2 字间距(Letter Spacing)

**原则:**
- 中文一般不加字间距
- 西文大写标题可微调(通常 +0.05em ~ +0.1em)
- 正文字间距保持默认(0)

## 5. 授权风险约束(License Risk Constraints) — 硬约束

### 5.1 授权类型标注

**强制要求:**
- `license_status` 必须是 "verified" 或 "needs_verification"
- 每个字体必须标注授权类型:商用授权 / 开源协议(SIL/OFL)/ 系统字体 / 需采购
- **未确认授权时,必须标注 "needs_verification"**

**示例:**
```json
{
  "primary_font": {
    "family": "Inter",
    "license": "SIL Open Font License 1.1"
  },
  "license_status": "verified"
}
```

```json
{
  "primary_font": {
    "family": "Helvetica Neue",
    "license": "商用字体,需确认授权范围"
  },
  "license_status": "needs_verification"
}
```

### 5.2 失败信号(F-TY1)

**授权风险未标(一票否决):**
- `license_status` 字段缺失
- 商用字体无授权信息
- 声称授权已确认但未提供证据

### 5.3 Fallback 字体栈

**强制要求:**
- 必须定义 fallback 字体栈(主字体不可用时的降级)
- fallback 字体必须跨端可用(如系统字体)
- 必须覆盖 CJK 与 Latin 场景

**示例:**
```json
{
  "font_stack": {
    "cjk": "\"Noto Sans SC\", \"PingFang SC\", \"Microsoft YaHei\", sans-serif",
    "latin": "\"Inter\", -apple-system, BlinkMacSystemFont, \"Segoe UI\", Roboto, sans-serif"
  }
}
```

## 6. 跨端可用性约束(Cross-Platform Constraints)

### 6.1 必须覆盖端

**强制要求:**
- `cross_platform` 必须包含至少 Web / iOS / Android 三端
- 每端必须说明字体可用性或 fallback 方案
- 印刷场景需说明字体格式(TrueType/OpenType/可转曲)

**示例:**
```json
{
  "cross_platform": {
    "web": {
      "format": "WOFF2",
      "loading": "font-display: swap",
      "fallback": "系统无衬线"
    },
    "ios": {
      "availability": "需内嵌或使用系统字体",
      "fallback": "PingFang SC / San Francisco"
    },
    "android": {
      "availability": "需内嵌或使用 Noto Sans",
      "fallback": "Roboto / Noto Sans CJK"
    },
    "print": {
      "format": "OpenType",
      "notes": "可转曲输出"
    }
  }
}
```

### 6.2 降级策略

若某端字体不可用:
- 必须提供合理 fallback 字体
- fallback 字体必须与主字体风格接近
- 避免 fallback 到系统默认丑字体(如 Times New Roman)

## 7. 输出合规性检查(Output Compliance Check)

### 7.1 必须字段

`typography_spec` 输出必须包含:
- `primary_font` (object, 包含 family 与 license)
- `weight_hierarchy` (array, 长度 3-5)
- `license_status` (enum: "verified" | "needs_verification")

### 7.2 可选但推荐字段

- `secondary_font` (正文场景推荐)
- `size_scale` (模块化字号梯度)
- `line_height` (中西文分别定义)
- `cjk_latin_pairing` (中文市场必需)
- `cross_platform` (跨端场景必需)

### 7.3 Schema 合规

输出必须通过 `typography_spec.schema.json` 验证:
- `license_status` 只能是 "verified" 或 "needs_verification"
- `weight_hierarchy` 长度必须在 [3, 5] 区间

## 8. 能力边界声明(Capability Boundary)

### 8.1 运行时不得声称

- 不得声称字体已完成商用授权采购(产出授权类型识别与风险预警,采购需用户/法务确认)
- 不得声称已覆盖所有语言场景(如阿拉伯文/泰文等复杂书写系统需专项)
- `license_status` 标 "needs_verification" 时,不得声称授权已确认
- 不得声称已替代专业字体排印师的精细调校

### 8.2 输出中的免责声明

在 `typography_spec` 中建议包含 `_meta.disclaimer`:
```json
{
  "_meta": {
    "disclaimer": "本字体系统需字体授权/法务确认后方可商用。license_status 为 needs_verification 的字体需人工验证授权范围。跨端 fallback 需实际测试验证。"
  }
}
```

---

**Constitution 版本**: 0.1.0-pilot
**对应 Contract**: B1.0 sub-skill-contracts.yaml#typography-system
**强制执行**: 所有 pipeline stages 必须遵守上述约束,违反即视为 runtime error。
