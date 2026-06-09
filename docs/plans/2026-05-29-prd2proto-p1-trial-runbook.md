# prd2proto pm 模式：跑一次真 PRD（验收手册）

> 给用户：当 task 15（写 7 个 prompt）完成后，按本手册跑一次真 PRD，验收 P1 batch。

---

## 0. 前置检查

```bash
cd /Users/young/Documents/Codex/Agent-design-webmode

# 确认 P1 测试基线还过
python3 -m pytest skills/prd2proto/tests/test_p1_smoke.py -v

# 确认工厂 + kernel 零回归
python3 -m pytest tests/unit/ -q
cd .factory && python3 -m pytest tests/ -q && cd ..

# 确认 frontend-codegen Mock 健康
python3 -m pytest mcp-servers/frontend-codegen/tests/ -q
```

预期：248/248 全过。任一失败先回看 docs/plans/2026-05-29-prd2proto-p1-completion.md 找原因。

---

## 1. 准备真 PRD

把要测的 PRD 文档放到 `inputs/prd.md`（或 `.pdf` / `.docx`）。

最小可行 PRD 要包含：
- 产品名 + 核心目标
- 至少 2-3 个核心模块
- 每个模块的关键页面（如「登录页」「主页」「设置页」）
- 主用户流（如「用户从主页 → 进入设置 → 修改密码」）

太少信息 prompt 会问你补；太多也行，prd-understanding stage 会自动结构化。

### 同时写一份 scope.md

`inputs/scope.md` 几句话即可：

```markdown
# 评估范围

- 产品：<你的产品名>
- 模式：pm（PM 演示用低保真原型）
- 框架目标：React （或 Vue）
- 重点模块：<列你最关心的 1-2 个模块>
- 不在范围：<明确不要做哪些>
```

---

## 2. 跑 prd2proto

> 当前 prd2proto 还没接 IDE slash command（这是 P5 的事），所以这一轮用 CLI 直跑。

期望命令（如果 designos CLI 已支持）：
```bash
designos run prd2proto --mode pm --prd inputs/prd.md --scope inputs/scope.md
```

如果 designos CLI 还没接 prd2proto，也可以手动一步步跑各 stage（见 §4 fallback）。

---

## 3. 验收点

### 3.1 必须跑通的 4 个 stage（pm 模式）

- ✅ `prd-understanding`：返回 modules / key_features / pages / user_flows / business_goal（JSON）
- ✅ `design-analysis`：返回 information_architecture（markdown）+ component_spec（markdown）— 此处会有 Checkpoint C1 让你确认
- ✅ `code-generation`：调 frontend-codegen Mock，写出 React 项目骨架到 outputs/prototype_code/
- ✅ `review-gate`：返回 review_report 含 4 条宪法软审查 + Checkpoint C4

### 3.2 必须跳过的 4 个 stage（pm 模式）

- ❌ spec-generation（only_when=designer-spec）
- ❌ dsl-fetch（only_when=designer-dsl）
- ❌ token-extraction（only_when=mode != "pm"）
- ❌ component-mapping（only_when=designer-dsl）

### 3.3 产出文件

跑完后 `outputs/prototype_code/` 应该有：

```
prototype_code/
├── package.json     ← React + Vite
├── index.html
├── README.md
└── src/
    ├── main.jsx
    └── App.jsx      ← 当前 mock 是固定登录页
```

试一下：
```bash
cd outputs/prototype_code
npm install
npm run dev
```

应该能在 localhost 看到一个登录页面（mock 固定模板）。

⚠️ 当前 frontend-codegen 是 Mock，所以**不管 PRD 写啥，生成的 App.jsx 都是同一个登录页**。这是 P3 才解决的事。

---

## 4. 验收的"看什么"

### 4.1 看 prd-understanding 输出（最重要）

它能不能正确把你的 PRD 拆成：
- modules（核心模块清单，名字 + 简介）
- pages（每个模块下的页面，最好带 route 名）
- user_flows（关键用户流，是 list of flow，每个 flow 是 list of step）
- business_goal（一句话业务目标）

如果这块没出来或者明显错了，**说明 prd-understanding prompt 还要改**，回头改 prompts/01-prd-understanding.md。

### 4.2 看 design-analysis 输出（次重要）

它能不能正确：
- 把 PRD 的页面变成 information_architecture（站点地图 / 页面树）
- 给每个页面列出需要的组件 + 7 种状态需求（默认/悬停/按下/聚焦/禁用/加载/错误）

### 4.3 看 review-gate 输出

它对 mock 生成的固定登录页做的 4 条宪法软审查报告：
- constitution_violations（应该不为空，因为 mock 代码里有硬编码颜色 #3B82F6 等）
- fidelity_score（pm 模式应该 60-80 分，因为 mock 不真做 DSL）

### 4.4 看 Checkpoint 体验

- C1（design-analysis 之后）：你能看到信息架构 + 组件清单，决定 continue / modify / supplement
- C4（review-gate 之后）：你能看到生成代码 + 审查报告，决定 continue / modify / supplement

---

## 5. 验收预期 vs 已知边界

| 项 | 预期 |
|---|---|
| pm 模式 4 stages 跑通 | ✅ 必须 |
| 产出能 npm install + npm run dev | ✅ 必须 |
| App.jsx 内容真随 PRD 变 | ❌ Mock 固定，等 P3 |
| review-gate 准确指出 4 条宪法违反 | 软审查，看 LLM 自我审查质量 |
| token / DSL / 组件映射 | ❌ 不在 pm 模式 |
| 成功率（pm 模式） | 目标 80%+（prompt 跑得稳） |

---

## 6. 验收完后写一份反馈

跑完一次后，把以下信息写到 `docs/plans/2026-05-29-prd2proto-p1-trial-feedback.md`：

```markdown
# prd2proto P1 试跑反馈（pm 模式）

## 输入
- PRD 长度 / 内容简介
- scope.md 内容

## 实际跑通情况
- prd-understanding：✅/❌（说明）
- design-analysis：✅/❌（说明）
- code-generation：✅/❌（说明）
- review-gate：✅/❌（说明）

## prompt 质量评价（最关键）
- 哪个 prompt 输出明显不达预期
- 哪个 prompt 体验很好
- 用户填什么内容时容易踩坑

## checkpoint 体验
- C1 / C4 提示是否清晰
- 用户决策路径是否合理

## 想立即修的 1-3 件事
（按优先级）

## 想留给 P2 修的事
（不阻塞 P1 收尾）
```

---

## 7. 然后呢

根据反馈：

- **prompt 改进点**：直接改 skills/prd2proto/prompts/，重跑一次
- **架构问题**：开新 batch（如：发现 Checkpoint UX 不好）
- **frontend-codegen 真实需求清单**：把"如果不是 mock 我希望它能干什么"列出来 → 这就是 P3 batch 的需求基线
- **跨 batch 共性发现**：如果发现 prd2proto 的某个模式跟工厂 archetype 不对，开 archetype 升级 batch

如果 4 stages 跑得都顺，那 P1 batch 收尾，可以推 P2（designer-spec 模式）或者 P3（frontend-codegen 真 MCP）。

---

## 一句话总纲

> **本次试跑的目的不是验证 frontend-codegen（它是 mock），而是验证 prompt 质量 + checkpoint 体验 + 工厂装配产物的真实可用性。Mock 产物本身是死的，真信号在 LLM 这一段。**
