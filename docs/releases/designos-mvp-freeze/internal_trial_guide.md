# DesignOS MVP Internal Trial Guide

> 内部试用指南：如何安装、试用、记录反馈。

## 安装

> `npx` 从 npm registry 拉取最新发布版。安装与更新用同一组命令——`@latest` 始终指向最新版本，无需改命令。

### 首次安装 / 更新到最新版（从 npm）

两种命令方式都支持，按需要选：

```bash
# 方式 A：标准（首次运行会提示确认安装）
npx <YOUR_INTERNAL_PACKAGE>

# 方式 B：跳过确认（适合脚本 / CI / 想强制无交互拉最新）
npx --yes designos@latest
```

> 不要用 `npx <YOUR_INTERNAL_PACKAGE>`（不带 `@latest`）——本地有旧缓存时会直接复用、不升级。
> 始终带 `@latest` 才能保证拿到最新发布版。

### 首次安装（本地开发模式）
```bash
cd /path/to/Agent-design-webmode
git checkout skills-pilot-wave2
git pull origin skills-pilot-wave2
npm link
```

---

## 重新安装最新版

### 从 npm 更新（与首次安装相同命令）
```bash
# 方式 A
npx <YOUR_INTERNAL_PACKAGE>

# 方式 B（若被本地缓存挡住，先清缓存再拉）
npx --yes designos@latest
# 或
npm cache clean --force && npx <YOUR_INTERNAL_PACKAGE>
```

### 从本地更新
```bash
cd /path/to/Agent-design-webmode
git pull origin skills-pilot-wave2
npm link
```

---

## 在 Claude Code 中试用

### 启动 Claude Code
```bash
claude
```

### 调用 DesignOS skill

#### 1. uxeval（UX 评估）
```
/designos uxeval <截图路径>
# 或
/designos uxeval --url https://example.com
```

**输入示例**：
- 截图：`screenshots/product-homepage.png`
- URL：`https://example.com`（需 Playwright 环境）

**期望产出**：结构化 UX 评分（可读性/导航/视觉层级/可访问性）+ 改进建议

---

#### 2. prd2proto（PRD 转原型）
```
/designos prd2proto <PRD 文本>
```

**输入示例**：
```
任务管理 app，支持拖拽排序、标签分类、截止日期提醒。目标用户是项目经理。
```

**期望产出**：交互原型规范 + uxeval 评估报告

---

#### 3. ai-analytics（AI 产品分析）
```
/designos ai-analytics <产品名称>
```

**输入示例**：
```
Notion AI
```

**期望产出**：功能清单、定价模式、目标用户、竞争优势分析

---

#### 4. ip-design（IP 角色设计）
```
/designos ip-design <角色 persona>
```

**输入示例**：
```
科技助手机器人，友好可靠，面向企业用户，辅助日常办公任务。
```

**期望产出**：IP 视觉方向（形态/色彩/气质）+ 实现路径

---

#### 5. brand-creative（品牌创意）

##### 5.1 brand-strategy（品牌策略）
```
/designos brand-creative:brand-strategy <公司简介>
```

**输入示例**：
```
我们是一家 B2B SaaS 公司，提供项目管理工具，目标客户是 50-500 人规模的科技公司。
```

**期望产出**：品牌定位、差异化、人格关键词、北极星价值主张

---

##### 5.2 competitive-analysis（竞品分析）
```
/designos brand-creative:competitive-analysis <竞品名称>
```

**输入示例**：
```
Notion / Asana / Monday.com
```

**期望产出**：视觉风格分析、传播策略、市场空白

---

##### 5.3 logo-design（Logo 设计）
```
/designos brand-creative:logo-design <brand_brief>
```

**输入示例**（需先运行 brand-strategy 产出 brand_brief）：
```
基于 brand_brief（从 brand-strategy 产出）
```

**期望产出**：logo 设计规范（形态/色彩/应用场景/辅助图形）+ AI 绘图 prompt pack

---

##### 5.4 color-system（色彩系统）
```
/designos brand-creative:color-system <brand_brief>
```

**期望产出**：品牌色彩调色板（主色/辅色/对比度/可访问性/明暗双模式）

---

##### 5.5 typography-system（字体系统）
```
/designos brand-creative:typography-system <brand_brief>
```

**期望产出**：字体系统（主/辅字体/字重层级/字号比例/中西文配对/跨端可用性）

---

##### 5.6 visual-identity（VI 手册）
```
/designos brand-creative:visual-identity
```

**前置条件**：必须先运行 logo-design / color-system / typography-system

**期望产出**：VI 手册（聚合 logo/color/typography，做一致性判断与缺口声明）

---

## 在 Codex / Trae / Cursor 中试用

### 通过 SkillLoader 加载
```python
from kernel.skill_loader import SkillLoader

loader = SkillLoader(["/path/to/skills"])
skill = loader.load("brand-creative:visual-identity")
```

### 直接调用 kernel pipeline engine
```python
from kernel.pipeline.engine import PipelineEngine

engine = PipelineEngine(llm=llm_client)
async for event in engine.execute(skill, ctx):
    print(event)
```

---

## 用户应该提供什么输入

| Skill | 输入格式 | 示例 |
|---|---|---|
| **uxeval** | 截图 PNG/JPG 或 URL | `screenshots/homepage.png` 或 `https://example.com` |
| **prd2proto** | 简短 PRD 文本（200-500 字） | "任务管理 app，支持拖拽排序..." |
| **ai-analytics** | 产品名称或简介 | "Notion AI" |
| **ip-design** | 角色 persona（性格/目标用户/使用场景） | "科技助手机器人，友好可靠..." |
| **brand-strategy** | 公司简介或品牌简介（100-300 字） | "我们是 B2B SaaS 公司..." |
| **competitive-analysis** | 竞品名称（1-3 个） | "Notion / Asana / Monday.com" |
| **logo-design** | brand_brief（来自 brand-strategy） | 自动从上游获取 |
| **color-system** | brand_brief（来自 brand-strategy） | 自动从上游获取 |
| **typography-system** | brand_brief（来自 brand-strategy） | 自动从上游获取 |
| **visual-identity** | visual_spec + color_palette + typography_spec | 自动从上游获取 |

---

## 如何判断产出是否可用

### 结构完整性
- ✅ 产出对齐 schema（有明确字段结构）
- ✅ 无明显格式错误或缺失必需字段

### 边界标注
- ✅ 有 `do_not_claim` 边界声明（不过度承诺）
- ✅ 有 `gaps` / `needs_verification` / `needs_manual_check` 字段
- ✅ 明确标注"不声称商标可注册/版权清洁/可直接商用"等

### 质量层级
- **中阶可用**：可供资深人员评审修改，不是直接商用
  - 结构清晰、有理有据、可追溯决策逻辑
  - 需人工调整细节、补充业务语境
- **高阶可评审**：资深人员愿意在其上做评审，而非推倒重来
  - 决策链路完整、冲突处理明确、失败模式已标注
  - 仅需微调即可落地

### 红线检查
- ❌ 不应出现"final production ready"
- ❌ 不应出现"商标已确认"
- ❌ 不应出现"字体授权已确认"
- ❌ 不应出现"印刷色已验证"
- ❌ 不应出现"可直接商用"

---

## 如何记录反馈

### 反馈模板

```markdown
## 试用反馈

**Skill**: brand-creative:logo-design

**试用任务**: 为 B2B SaaS 公司设计 logo

**输入**:
- brand_brief: { north_star: "让专业人士感到被支持", personality_keywords: ["专业", "现代", "可靠"] }

**期望产出**:
- logo 设计规范，包含形态方向、色彩参考、黑白可用性验证

**实际产出**:
- visual_spec: { form: {...}, black_white_usable: true, min_size_px: 16 }

**哪里不符合预期**:
- 形态方向过于抽象，缺少具体几何描述
- trademark_risk_signals 字段为空，未标注风险

**建议改进方向**:
- prompt 中强制输出 mother_shape 几何描述
- 即使 low_risk 也要标注 trademark_risk_signals 非空
```

### 提交反馈渠道
- GitHub Issues（internal repo）
- 内部 Slack channel: `#designos-feedback`
- 直接联系 DesignOS 核心团队

---

## 常见问题

### Q1: 为什么 brand-creative 需要先运行 brand-strategy？
A: brand-strategy 产出 `brand_brief`，是 logo-design / color-system / typography-system 的必需输入。建议按顺序运行：brand-strategy → logo/color/typography(parallel) → visual-identity(sequential)。

### Q2: visual-identity 为什么会拒绝产出？
A: 若上游 logo 黑白不可用（`black_white_usable: false`）或主色对比度不足（`accessibility: "fail"`），visual-identity 会一票否决，不产出 VI 手册。这是质量门机制。

### Q3: 为什么 logo 不声称商标可注册？
A: DesignOS 不做商标查重（需专业商标机构检索），只标注 `trademark_risk_signals`（如"使用行业通用符号"）。商标注册需人工确认。

### Q4: 产出的 AI 绘图 prompt 可以直接用吗？
A: 可以用于 Midjourney / Stable Diffusion / 即梦等平台生成初稿，但生成结果仍需专业设计师矢量精修与品牌方定稿。

### Q5: uxeval web mode 为什么需要 Playwright？
A: web mode 需自动截图与交互模拟，依赖 headless 浏览器（Playwright）。若无 Playwright 环境，使用 client mode 手动提供截图。

---

## 下一步

试用完成后，请：
1. 填写反馈模板
2. 提交至内部反馈渠道
3. 参与 DesignOS 内部迭代讨论

感谢试用！
