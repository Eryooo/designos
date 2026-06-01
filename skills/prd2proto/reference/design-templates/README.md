# Design Templates 模板库

8 个预置 design.md 模板，让 prd2proto 在用户不提供 `design-spec.md` 时，能够基于 PRD 内容与用户偏好自动选择匹配的视觉风格。

## 目的

- **降低门槛**：不强制用户写 design-spec.md，也能拿到风格统一的高保真原型
- **风格一致性**：每个模板预置完整 token 体系（颜色 / 字号 / 间距 / 圆角 / 阴影 / 组件），保证宪法规则 1（不硬编码）得到落实
- **行业惯例**：覆盖金融、开发者工具、AI、企业后台、消费、文档等主流场景
- **可微调**：选中模板后允许在白名单字段内调整，但核心 vibe 不允许改

所有模板严格遵循 Google Labs design.md 规范：YAML frontmatter（机器可读 token） + Markdown body（设计哲学与使用守则）。

## 模板对照表

| 模板 | 适用场景 | 关键特征 | 推荐组件库 |
|---|---|---|---|
| stripe | 金融/支付/SaaS、企业服务 | 干净专业、紫色主调、大量留白、清晰排版 | shadcn-ui / element-plus |
| linear | 开发者工具/项目管理/issue tracker | 暗色优先、紧凑信息密度、键盘优先、灰阶克制 | radix / arco-design |
| vercel | 开发者平台/部署/性能监控 | 黑白高对比、几何感、单色调极简、等宽字体 | shadcn-ui / arco-design |
| notion | 知识管理/文档协作/内部 wiki | 温暖中性、灰白主调、可读性优先、轻量装饰 | shadcn-ui / element-plus |
| coze | AI Agent 平台/对话式 AI 工具 | 浅色全屏、大圆角卡片、亲和力强、彩色点缀 | antd@5 / arco-design |
| antd-pro | 企业后台/数据平台/管理系统 | 蓝灰体系、信息密度高、表格表单驱动 | antd@5 / ant-design-vue |
| apple-hig | 消费级 App / 高端品牌 | 圆润通透、胶囊按钮、大留白、动态层次 | radix / element-plus |
| arco | 字节系产品/年轻消费产品 | 清爽现代、橙红主色、丰富插画风、活力 | @arco-design/web-react / @arco-design/web-vue |

## AI 选择算法

```
输入：PRD 内容 + 用户偏好（可选）
输出：选中的模板 path + 选择理由（结构化 JSON）

匹配维度（按权重从高到低）：
1. 产品类型分类
   - ToB 后台 / 数据平台          → antd-pro
   - 开发者工具 / DevTool         → linear（暗色密集）/ vercel（极简单色）
   - AI Agent / 对话式工具        → coze
   - 知识管理 / 文档协作          → notion
   - 金融 / 支付 / SaaS           → stripe
   - ToC 高端消费 / 品牌站        → apple-hig
   - ToC 年轻向 / 字节系          → arco

2. 视觉气质关键词
   "干净 / 专业 / 严肃"         → stripe / antd-pro
   "活力 / 年轻 / 热闹"         → arco / coze
   "极简 / 极致简洁 / 几何"     → vercel
   "温暖 / 亲和 / 可读"         → notion / coze
   "暗色 / 紧凑 / 工程感"       → linear
   "高端 / 优雅 / 圆润"         → apple-hig

3. 信息密度需求
   高（每屏 100+ 字段、大表格）     → antd-pro / linear
   中（卡片化、模块清晰）           → coze / arco / stripe
   低（大留白、内容居中）           → apple-hig / vercel / notion

4. 暗色 vs 浅色偏好
   优先暗色                       → linear（默认暗）
   仅浅色                         → notion / apple-hig / arco
   两者皆可                       → 其余 5 个

5. 行业惯例
   金融偏稳重克制                 → stripe / antd-pro
   AI 偏新偏柔软                  → coze
   电商偏热闹偏活力               → arco
   企业 / 政企严肃                → antd-pro
   开发者偏暗色或极简             → linear / vercel
```

冲突仲裁：用户显式偏好 > PRD 内容推断 > 行业惯例 > 默认 stripe（最中性）。

## 微调规则

选中模板后，**允许调整**的字段（写入到衍生 design-spec.md）：

- `colors.primary` / `colors.on-primary`：替换为用户品牌主色
- `colors.success` / `colors.error` / `colors.warning`：本地化品牌的状态色（如中国习惯红涨绿跌可调）
- `typography.*.fontFamily`：根据语言环境（中文/英文/日韩）调整字体栈
- `recommended_ui_lib`：根据用户已有技术栈替换组件库

**禁止调整**的字段（破坏模板核心 vibe）：

- `spacing.*`：间距体系是模板灵魂，乱调会破坏节奏
- `rounded.*`：圆角整体策略不能切换（如 apple-hig 的 full 胶囊按钮不能改成直角）
- `elevation.*`：阴影哲学（重 vs 轻 vs 无）不能切换
- Markdown body 中的 "Design Philosophy" 与 "Do's and Don'ts"：直接拷贝即可，不要改写

如果用户的需求与上述禁止字段强冲突，正确做法是**重新选另一个模板**，不要硬改。

## 模板版本

所有 8 个模板统一使用 `version: alpha`，对应 prd2proto v0.2 迭代周期。后续会随用户反馈迭代到 beta / v1。

## 文件清单

- `stripe.md`
- `linear.md`
- `vercel.md`
- `notion.md`
- `coze.md`
- `antd-pro.md`
- `apple-hig.md`
- `arco.md`

## 备注

色值参考真实品牌的视觉语言，但不直接照抄商标色，可在选中后基于品牌色微调。所有模板色值仅作起点参考，最终以 design-spec.md 或用户品牌色为准（宪法规则 4）。
