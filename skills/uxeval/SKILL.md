---
name: uxeval
description: 体验启发式评估 + 可用性测试。当用户说体验评估、启发式评估、可用性测试、UX 走查、/uxeval 时使用。支持客户端模式（用户提供截图）和 Web 模式（Playwright 自动截图）两种证据采集方式。
---

# UXEval — 体验启发式评估

## 触发条件

用户说出以下任一意图时立即启动：
- 自然语言：「做体验评估」「启发式走查」「可用性测试」「UX 评估」
- 快捷命令：`/uxeval`、`/uxeval client`、`/uxeval web <URL>`

## Step 0：欢迎 + 模式选择

回复用户：

```
我将用 UXEval 评估你的产品。请确认：

1. Web 应用还是客户端应用？
   - Web：我用 Playwright 自动登录 + 截图（需要 URL + 账号密码）
   - 客户端：你提供产品截图

2. 必需输入：
   - PRD 文档（.md / .pdf / .docx）
   - 评估范围（几句话：目标、角色、产品范围）

3. 推荐输入：
   - 5+ 张关键页面截图（客户端模式）
   - 用户角色描述（PRD 里没写清楚时）

准备好了吗？可以先提供 PRD，其他我会引导你补充。
```

不要跳过模式选择直接开始分析。

## Step 1：自动初始化

用户只需丢 PRD，AI 自动完成目录创建、scope 推断。不要让用户建目录或填表。

1. **找 PRD**：优先用户给的路径 → 消息附件 → 粘贴正文（>500字） → 自动扫描当前目录
2. **建目录**：自动创建 `inputs/` `outputs/` `runs/`
3. **推断 scope.md**：从 PRD 自动提取评估范围，写到 `inputs/scope.md`，让用户审阅
4. **确认模式**：根据 Step 0 的回答写入 `designos.project.yaml`

## Step 2：7 阶段流水线

按以下顺序逐 stage 执行。每个 stage 读取对应 prompt 文件 + reference 知识库。

| # | Stage | 读取 | 输出 | 备注 |
|---|---|---|---|---|
| 1 | PRD 结构化理解 | `prompts/v1.0.0/01-prd-understanding.md` + `reference/m01-需求理解.md` | modules / roles / scenarios / key_tasks / evaluation_boundary | |
| 2 | 启发式原则映射 | `prompts/v1.0.0/02-principle-mapping.md` + `reference/m02-启发式原则.md` | principles JSON | |
| 3 | 旅程建模 | `prompts/v1.0.0/03-journey-modeling.md` + `reference/m03-旅程建模.md` | journey_map / journey_stages | **⚠️ Checkpoint C1** |
| 4 | 任务生成 | `prompts/v1.0.0/04-task-generation.md` + `reference/m04-任务生成.md` | task_checklist_full / task_checklist_lite | **⚠️ Checkpoint C2** |
| 5a | 脚本生成（仅 web） | `prompts/v1.0.0/05a-script-generation.md` + `reference/m05-证据采集.md` | evaluation_script | |
| 5b | 截图分析（仅 client） | `prompts/v1.0.0/05b-screenshot-analysis.md` + 读取 `inputs/screens/` | screenshots / image_analysis | 必须逐张分析所有截图，**每次只读 1 张**逐张分析，每张输出结构化观察后再读下一张。禁止跳过任何截图，报告进度："已分析 X/Y 张截图" |
| 5.5 | PRD-截图冲突分析 | Stage 5b 输出 + Stage 1 输出 | prd_screenshot_conflicts | |
| 6 | 问题检测 + 归因 | `prompts/v1.0.0/06-issue-attribution.md` + `reference/m06-问题归因.md` | issues JSON | **⚠️ Checkpoint C3** + ⚠️ 宪法自检 |
| 7 | 报告生成 | `templates/*.md` | Markdown + Excel + evidence_pack | |

每个 stage 的执行方式：
1. 读取对应 prompt 文件（含角色设定 + 输入输出格式）
2. 读取对应 reference 文件（领域知识）
3. 用当前模型推理，产出写到 `outputs/`
4. 遇到 Checkpoint 暂停等用户确认

### Stage 5.5：PRD-截图冲突分析

对比 PRD 和截图，输出：
- PRD 说了但截图没体现的功能/页面（标注"需补充现场验证"）
- 截图有但 PRD 没覆盖的功能/页面（标注"可能是新增或变更"）
- 冲突处理规则：PRD 是主基准、截图是现实校准层、冲突不直接抹平而是显式标注

这些冲突点不作为体验问题，但作为 Stage 6 的评估上下文。

### Stage 6：宪法自检

Stage 6 输出前必须逐条执行 7 条宪法校验，不通过的问题删除。

## Checkpoint 交互

三个暂停点（C1 / C2 / C3），用户回复：
- `继续` → 进入下一阶段
- `修改 <说明>` → 按说明调整后重新输出
- `补充 <内容>` → 追加信息后重新推理

不要超时跳过 Checkpoint。用户不回复就等待。

## 宪法约束（不可违反）

读取 `constitution.md`，核心 7 条：
1. 只评体验问题，不评功能 bug
2. 每条问题必须绑定截图证据
3. 每条问题必须映射到启发式原则
4. 严重等级必须有判定依据
5. 不编造 PRD 没写的功能
6. 推断内容必须标记 [inferred]
7. 不输出无证据的主观判断

## 工具调用

需要工具时直接调用（通过 terminal / Bash）：
- **PDF/DOCX 解析**：PRD 是 PDF 时必须用 `pdftotext` 或 python 脚本转为 Markdown，写到 `inputs/prd.md`。禁止只靠多模态"看"PDF。需要 pdftotext 时提示用户安装（`brew install poppler` 或 `apt install poppler-utils`）
- **Playwright**（仅 web 模式）：执行 Stage 7a 生成的 .spec.mjs 脚本
- **Excel 生成**：最终报告用 openpyxl 或 excel-builder 脚本生成 .xlsx。需要 openpyxl 时提示用户安装
- **图片分析**：截图用多模态视觉能力直接分析

## 对话风格

- 每次回复 ≤ 3 段
- 每完成一个 stage 报一次进度
- 不说"完美的评估"，说"已完成第 X 阶段，输出在 outputs/..."
- 承认局限：Web 自动化不稳时明说

## 错误处理

- PRD 缺失 → 拒绝执行，请求补充
- scope.md 缺失 → 从 PRD 自动推断，让用户审阅
- 截图缺失（client 模式）→ 询问用补文字描述还是补截图
- 宪法违反 → 重新生成（最多 3 次）

