# DesignOS MVP Known Limits

> 诚实声明能力边界，不过度承诺。

## 总体定位

DesignOS MVP 是**辅助工具与初稿生成器**，不是替代资深专业人员的自动化系统。

所有产出默认为**中阶可用**（可供资深人员评审修改），不声称达到**高阶可评审**或**直接商用**标准。

---

## brand-creative 能力边界

### 1. 只到 visual-identity，不含完整 brand-guidelines

**当前包含**：
- brand-strategy（品牌策略基线）
- competitive-analysis（竞品分析）
- logo-design（logo 设计规范）
- color-system（色彩系统）
- typography-system（字体系统）
- visual-identity（VI 手册聚合层）

**不包含**（post-MVP）：
- brand-voice（品牌声音）
- content-strategy（内容策略）
- campaign-creative（营销创意）
- brand-collateral（品牌物料）
- digital-assets（数字资产）
- brand-guidelines（完整品牌手册）
- brand-audit（品牌审计）

**影响**：当前 MVP 只覆盖**视觉识别系统**，不含品牌声音、内容策略、营销创意。若需完整品牌手册，需等待 post-MVP 或人工补充。

---

### 2. brand-creative 仍是 pilot

所有 brand-creative 子技能标记为 `0.1.0-pilot`，意味着：

- ✅ **可用于**：内部快速原型验证、设计方向探索、初稿生成
- ❌ **不可用于**：跳过人工评审直接商用、高风险商业场景（如上市公司品牌发布）

**必须**：资深品牌总监/设计师人工评审后方可最终落地。

---

### 3. logo-design 边界

**不声称**：
- Logo 已商标查重/版权清洁/可直接注册
- 已生成最终商用 logo 视觉资产
- 辅助图形系统已完整设计

**产出定位**：
- 设计规范与 AI 绘图 prompt pack
- 需专业 logo 设计师矢量精修与品牌方定稿

**商标风险信号**：
- 输出中的 `trademark_risk_signals` 字段非法律意见
- Logo 注册需专业商标机构检索

**黑白可用性**：
- `black_white_usable: true` 为硬约束（一票否决）
- 若上游 logo 黑白不可用，visual-identity 会拒绝产出 VI 手册

**最小尺寸**：
- `min_size_px ≤ 32`（实际要求 16px，留安全余量）
- 若 favicon 16×16px 不可辨，判定为不合格

---

### 4. color-system 边界

**不声称**：
- 色彩已完成印刷打样验证
- 已覆盖所有可访问性场景（如色盲模式）

**accessibility 字段**：
- `pass`：主色/辅色对比度 ≥ 4.5:1（WCAG AA），可用
- `needs_manual_check`：对比度不足或未覆盖完整场景，需人工验证

**print_color_risk**：
- 标注 RGB → CMYK 转换的色差风险
- 印刷色值需经打样验证后方可最终确认

**明暗双模式**：
- 输出 `dark_light_usage` 字段定义明暗背景规则
- 实际应用需前端/设计师调试确认

---

### 5. typography-system 边界

**不声称**：
- 字体授权已确认/已完成商用授权采购
- 已覆盖所有语言场景（当前主要覆盖中西文）

**license_status 字段**：
- `verified`：开源协议确认（如 SIL OFL），可用
- `needs_verification`：商用授权需人工确认，不可直接商用

**中西文配对**：
- 输出 `cjk_latin_pairing` 字段建议配对
- 实际字重/字号匹配需设计师调试确认

**跨端可用性**：
- 输出 `cross_platform` 字段定义 web/iOS/Android fallback
- 实际兼容性需前端工程师验证

---

## uxeval 边界

### client mode
- **依赖**：用户提供的截图质量（分辨率/完整性/清晰度）
- **局限**：无法自动截图，无法验证动态交互

### web mode
- **依赖**：Playwright 环境与浏览器可用性
- **局限**：需 headless 浏览器，可能被反爬虫机制阻挡

**不替代**：真人可用性测试、A/B 测试、用户访谈

---

## prd2proto 边界

**仍需人工 review**：
- 原型规范需 PM/设计师评审确认
- liveness check（功能可实现性）依赖真实业务语境
- 不替代 PM/设计师最终定稿

**输出质量**：
- 结构化原型规范（可读、可评审）
- 不是可直接开发的最终设计稿

---

## ai-analytics 边界

**当前是 LLM synthesis**：
- 基于 LLM 训练数据（截至 2026 年 1 月）
- **不是**真自动爬取（无实时网络请求）
- 信息可能过时，需人工补充一手调研

**适用场景**：
- 快速了解竞品大致定位与功能
- 作为调研起点，非最终结论

---

## ip-design 边界

**pilot 状态**：
- 需人工确认业务语境
- 形态方向需资深设计师评审
- 不声称可直接商用

**输出定位**：
- IP 视觉方向与实现路径建议
- 不是最终可商用的 IP 角色资产

---

## 测试覆盖边界

**已覆盖**：
- 258 tests passed（brand-creative 71 + kernel 25 + 其他 skill 101 + factory 61）
- 4/4 archetype 验证通过
- 所有 skill 可通过 SkillLoader 加载

**未覆盖**：
- 端到端真实用户场景验证
- 长上下文场景（超过 200k tokens）
- 多语言场景（当前主要中英文）
- 真实商业项目压力测试

---

## 供应链与依赖边界

**依赖**：
- Python 3.12+
- npm / Node.js（如需 npm 发布）
- Anthropic Claude API（如需在线运行）
- Playwright（如需 uxeval web mode）

**安全提醒**：
- npm token 需妥善保管
- 不建议在公共 CI 中暴露 token
- 发布前需确认 package.json 不含敏感信息

---

## 总结

DesignOS MVP 是**辅助工具**，不是**替代方案**。

所有产出需经资深专业人员评审后方可最终落地，不可跳过人工决策直接商用。

MVP 适合内部快速验证与初稿生成，不适合高风险商业场景或外部正式推广。
