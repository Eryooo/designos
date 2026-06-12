# DesignOS MVP Freeze — Internal Trial Baseline

> **Status**: MVP trial candidate (not for external production use)  
> **Branch**: `skills-pilot-wave2`  
> **Commit**: `c60fa1e`  
> **Generated**: 2026-06-08

## 定位

DesignOS MVP 是首个内部可试用基线，包含 6 个完整 skill：

1. **uxeval** — UX 评估（支持 client mode 截图 + web mode Playwright）
2. **prd2proto** — PRD 转原型（支持 uxeval → interactive → design）
3. **ai-analytics** — AI 产品分析（LLM synthesis，非真自动爬取）
4. **ip-design** — IP 角色设计（生成型 archetype）
5. **brand-creative** MVP — 品牌创意前6子技能（策略 + 竞品 + 视觉系统）

**不含**：brand-voice / content-strategy / campaign-creative / brand-collateral / digital-assets / brand-guidelines / brand-audit（列为 post-MVP backlog）。

## 已包含 Skills

### 1. uxeval (evaluation archetype)
- **能力**：接收截图或 URL，产出结构化 UX 评分与改进建议
- **边界**：client mode 依赖用户提供的截图质量；web mode 需 Playwright 环境；不替代真人可用性测试
- **试用任务**：对内部产品首页做评估，检查输出是否有可操作建议

### 2. prd2proto (generation archetype)
- **能力**：接收 PRD，产出交互原型规范与 uxeval 评估
- **边界**：仍需人工 review；liveness check 依赖真实业务语境；不替代 PM/设计师最终定稿
- **试用任务**：用简短 PRD（如"任务管理 app，支持拖拽排序"），检查原型规范可读性

### 3. ai-analytics (analysis archetype)
- **能力**：分析 AI 产品的功能、定价、目标用户
- **边界**：当前是 LLM synthesis（基于训练数据），不是真自动爬取；信息可能过时
- **试用任务**：分析某竞品（如"Notion AI"），检查输出结构与合理性

### 4. ip-design (creative-generation archetype)
- **能力**：基于角色 persona 产出 IP 视觉方向与实现路径
- **边界**：pilot，需人工确认业务语境；形态方向需资深设计师评审；不声称可直接商用
- **试用任务**：输入简单 persona（如"科技助手机器人，友好可靠"），检查视觉方向合理性

### 5. brand-creative MVP（6 个子技能）

#### 5.1 brand-strategy
- **能力**：产出品牌策略基线（定位/差异化/人格关键词/北极星）
- **边界**：pilot，不替代资深品牌总监战略咨询；需人工评审后再落地
- **试用任务**：输入公司简介，检查产出是否有明确定位与人格方向

#### 5.2 competitive-analysis
- **能力**：竞品视觉风格与传播策略分析
- **边界**：当前基于 LLM 训练数据，不是实时爬取；需人工补充一手调研
- **试用任务**：分析某竞品（如"同类 SaaS"），检查分析维度完整性

#### 5.3 logo-design
- **能力**：产出 logo 设计规范（形态/色彩/应用场景/辅助图形）与 AI 绘图 prompt pack
- **边界**：不声称商标可注册/版权清洁/可直接商用；需专业 logo 设计师矢量精修；商标风险信号非法律意见
- **试用任务**：基于 brand_brief 产出 logo 规范，检查黑白可用性、最小尺寸、商标风险标注

#### 5.4 color-system
- **能力**：产出品牌色彩调色板（主色/辅色/对比度/可访问性/明暗双模式）
- **边界**：不声称已完成印刷打样验证；accessibility 标 needs_manual_check 时需人工验证
- **试用任务**：检查主色对比度是否 ≥4.5:1（WCAG AA），明暗背景可用性

#### 5.5 typography-system
- **能力**：产出字体系统（主/辅字体/字重层级/字号比例/中西文配对/跨端可用性）
- **边界**：不声称字体授权已确认；license_status 标 needs_verification 时不可直接商用
- **试用任务**：检查字体授权状态标注、中西文配对、跨端 fallback 规则

#### 5.6 visual-identity
- **能力**：聚合 logo/color/typography 三者产出 VI 手册，做一致性判断与缺口声明
- **边界**：不声称是最终品牌手册（brand-guidelines 才是）；pilot，需资深设计总监评审；不声称已完成法务/印刷/授权确认
- **试用任务**：检查 VI 手册是否标注三者一致性、是否继承上游警告、gaps 是否非空

## 推荐内部试用方式

### 安装（首次）
```bash
# 标准（首次会提示确认）
npx <YOUR_INTERNAL_PACKAGE>
# 或跳过确认（脚本 / CI）
npx --yes designos@latest

# 或本地开发模式
cd /path/to/Agent-design-webmode
npm link
```

### 重新安装最新版（已安装过，命令同上）
```bash
npx <YOUR_INTERNAL_PACKAGE>
# 若被本地缓存挡住，强制清缓存再拉
npm cache clean --force && npx <YOUR_INTERNAL_PACKAGE>

# 或本地开发模式
cd /path/to/Agent-design-webmode
git pull origin skills-pilot-wave2
npm link
```

### 在 Claude Code 中试用
```
/designos uxeval <截图路径>
/designos prd2proto <PRD 文本>
/designos brand-creative:brand-strategy <公司简介>
/designos brand-creative:logo-design <brand_brief>
```

### 在 Codex / Trae / Cursor 中试用
- 通过 skill loader 加载：`brand-creative:visual-identity`
- 或直接调用 kernel pipeline engine

### 用户应该提供什么输入
- **uxeval**: 截图 PNG/JPG 或 URL
- **prd2proto**: 简短 PRD 文本（200-500 字）
- **ai-analytics**: 产品名称或简介
- **ip-design**: 角色 persona（性格/目标用户/使用场景）
- **brand-creative**: 公司简介或品牌简介（100-300 字）

### 如何判断产出是否可用
- 产出是否有明确结构（对齐 schema）
- 是否标注了"不声称"边界（不过度承诺）
- 是否有 gaps / needs_verification / needs_manual_check 字段
- 中阶产出：可供资深人员评审修改，不是直接商用
- 高阶产出：资深人员愿意在其上做评审，而非推倒重来

### 如何记录反馈
使用反馈模板（见 `internal_trial_guide.md`）：
- 试用的 skill 与任务
- 输入是什么
- 期望产出是什么
- 实际产出是什么
- 哪里不符合预期
- 建议改进方向

## 不建议外部正式推广

MVP 仍处于 pilot 阶段，以下场景**不建议**：
- 直接交付客户作为最终交付物
- 声称替代资深设计师/品牌总监/PM 最终决策
- 用于高风险商业场景（如上市公司品牌发布）
- 跳过人工评审直接商用

**适合场景**：
- 内部团队快速原型验证
- 设计方向探索（头脑风暴）
- 初稿生成（后续人工精修）
- 学习设计决策框架

## Post-MVP Backlog

以下 skill 列为 post-MVP，不在本次发布范围：
- **brand-voice**: 品牌声音（语调/口头禅/场景话术）
- **content-strategy**: 内容策略（内容支柱/渠道矩阵/节奏日历）
- **campaign-creative**: 营销创意（campaign 主题/视觉方向/传播素材）
- **brand-collateral**: 品牌物料（名片/信头/包装/宣传册）
- **digital-assets**: 数字资产（网站视觉/社交媒体模板/H5 规范）
- **brand-guidelines**: 完整品牌手册（策略/VI/声音/内容/物料）
- **brand-audit**: 品牌审计（当前品牌健康度/差距/优化建议）

## 版本候选

**建议版本号**: 0.6.0-mvp-trial（待用户确认）

**当前 package.json 版本**: 需检查 `package.json` / `npm-package/package.json`

**发布前必须**：
1. 确认版本号
2. 跑完整测试套件
3. 执行 release checklist
4. 本地 `npx` 验证
5. 确认 npm token 安全
6. 准备回滚方案

## 联系与反馈

内部试用期间，请通过以下方式反馈：
- GitHub Issues（internal repo）
- 内部 Slack channel
- 直接联系 DesignOS 核心团队

---

**重要提醒**：本 MVP 不替代资深专业人员最终评审与决策，仅作为辅助工具与初稿生成器。
