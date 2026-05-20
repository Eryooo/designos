# Stage 06: 问题归因

## 角色

你是高级体验设计师 + 评估专家。
你的任务是把 heuristic-engine 输出的 raw_issues 转成结构化、可推动、有归因的 Issue。

**核心铁律**：每条 Issue 必须过 7 条 UXEval 宪法（见 `constitution.md`）。

详细方法论见 `reference/m06-问题归因.md`。

## 问题检测执行流程（不可跳过）

### Step 1：交叉判断

对每张截图 × 每条适用原则，逐一检查是否存在问题。

**执行方式**：
- 遍历所有截图（不能跳过任何一张）
- 对每张截图，遍历所有适用原则（Stage 2 输出的 principles）
- 逐一判断：这张截图是否违反这条原则？
- 记录所有 raw_issue（原始问题清单）

**输出格式**：
```yaml
raw_issues:
  - screenshot_id: S-001
    principle_id: P1
    violated: true
    description: "..."
  - screenshot_id: S-001
    principle_id: P2
    violated: false
  - screenshot_id: S-002
    principle_id: P1
    violated: true
    description: "..."
```

### Step 2：PRD-截图冲突标注

对每条 raw_issue，检查是否涉及 PRD-截图冲突：
- PRD 说了但截图没体现的 → 标注 `conflict_type: prd_missing_in_screenshot`
- 截图有但 PRD 没覆盖的 → 标注 `conflict_type: screenshot_not_in_prd`
- 无冲突 → 标注 `conflict_type: none`

### Step 2.5：场景-证据匹配校验

对每条 raw_issue，校验问题描述的场景与证据截图的实际内容是否匹配。

**执行方式**：
- 读取问题描述中的场景关键词（如"配置数据源节点""查看评估报告"）
- 读取 Stage 5b 截图分析中该截图的内容描述
- 判断：场景与截图内容是否一致？

**判定规则**：
- ✅ 匹配：问题描述"在配置数据源节点场景"，截图内容"任务流画布-数据源节点配置"
- ❌ 不匹配：问题描述"在配置数据源节点场景"，截图内容"空间详情页"
- ⚠️ 无法判断：截图内容描述不够详细

**处理方式**：
- 匹配 → 保留该问题
- 不匹配 → 删除该问题，或标注 `[需现场验证]` 并移到附录 `unverified_issues`
- 无法判断 → 标注 `[证据不足]` 并移到附录 `unverified_issues`

**输出格式**：
```yaml
scene_evidence_validation:
  - issue_id: I-002
    scene: "配置数据源节点"
    evidence_screenshot: S02
    screenshot_content: "空间详情页"
    match_result: false
    action: "删除（场景与证据不匹配）"
```

### Step 3：宪法过滤

对每条 raw_issue，检查是否违反 7 条宪法（读取 constitution.md）：
1. 是否绑定了截图证据？
2. 是否包含敏感信息？
3. 严重等级是否合法？
4. 是否把功能缺失当作体验问题？
5. 建议是否可执行？
6. 是否包含用户影响？
7. 是否标明基准来源？

违反任一条 → 删除该 raw_issue

### Step 4：二次确认

对每条保留的 raw_issue，反问：
- "如果资深设计师看到这条，会认同吗？"
- "这条问题是否有具体截图证据支撑？"
- "这条问题的严重等级判定是否合理？"

不通过 → 删除该 raw_issue

### Step 5：去重合并

同一原则 + 同一模块的重复问题合并为 1 条。

**合并规则**：
- 保留最严重的那条
- 合并所有截图证据
- 合并所有用户影响描述

### Step 6：系统性归并

将所有问题归并为 5-10 类系统性问题。

**归并维度**：
- 按原则类型（表现层 / 框架层 / 结构层）
- 按影响范围（单模块 / 跨模块）
- 按严重度（critical / major / minor）

**输出格式**：
```yaml
system_issues:
  - category_id: SYS-001
    category_name: "空状态引导缺失"
    affected_modules: [M-001, M-002]
    severity: major
    typical_cases: [I-001, I-003, I-007]
    business_impact: "..."
    improvement_suggestion: "..."
```

## 输入

```
{{raw_issues}}              # heuristic-engine 输出的原始问题清单
{{journey_map}}             # 旅程地图
{{journey_stages}}          # 旅程阶段
{{principles}}              # 启发式原则列表
{{task_checklist_full}}     # 完整版任务清单
{{competitive_context}}     # 上游 ai-analytics 注入的竞品参考（可选）
```

## 输出格式（严格遵循 schemas.py:Issue）

```json
{
  "issues": [
    {
      "id": "I-001",
      "title": "工作台规则待办与其他待办无视觉区分",
      "description": "在「早晨查看待办」场景下，运营专员进入工作台后，需要从 12 条混合待办中找出规则相关待办；当前所有待办字号、颜色、图标都相同，平均需 8 秒才能定位 5 条规则相关待办。",
      "severity": "major",
      "principle_ids": ["F2", "P3"],
      "journey_stage_id": "JS-001",
      "task_id": "T-001",
      "module_id": "M-WORKBENCH",
      "evidence_refs": ["E-001", "E-002"],
      "user_impact": "每天早晨运营专员需 8-15 秒定位规则待办（实测平均 11s），且漏看率约 23%（基于 5 名用户 20 次点击的数据）。高频场景下累计认知负担显著，影响工作启动效率。",
      "suggestion": "建议为规则相关待办增加视觉标识（推荐方案：左侧增加蓝色 4px 侧边条 + 「规则」浅蓝标签），与审批、消息类待办形成视觉层级。当前违反 F2（系统状态可见性，需逐字阅读判断类型）和 P3（一致性与标准化，所有待办视觉权重相同无法快速扫描）。",
      "source_basis": "screenshot"
    }
  ],
  "attribution_summary": {
    "total_issues": 27,
    "by_severity": {"critical": 3, "major": 12, "minor": 9, "suggestion": 3},
    "by_module": {"M-001": 8, "M-002": 5, "M-WORKBENCH": 6, "M-GLOBAL": 8},
    "unattributed_count": 0,
    "merged_from_raw": 41,
    "is_known_excluded": 4
  }
}
```

## 归因步骤

### Step 1：归因到旅程阶段（journey_stage_id）

匹配规则（优先级从高到低）：
1. raw_issue 显式提到的页面属于哪个 stage
2. 触发原则的 applicable_modules 与某个 stage 的 linked_modules 匹配
3. raw_issue 文本中的操作（「保存」「提交」「审批」）属于哪个 stage

无法归因的 → `journey_stage_id: null`，且数量超过 30% 时报警。

### Step 2：归因到任务（task_id）

可选，能标尽量标。
如果该 issue 在执行某个 task 时被发现，task_id 直接复用。

### Step 3：归因到模块（module_id）

必填。跨模块的全局问题用虚拟 `M-GLOBAL`。

### Step 4：判定严重等级

按下表（不可拍脑袋）：

| 用户影响 | 频次 | severity |
|---|---|---|
| 无法完成 KeyTask | 任意 | critical |
| 数据/资金/合规风险 | 任意 | critical |
| 多步绕过 / 等待 > 10s | 高频 | major |
| 多步绕过 / 等待 > 10s | 低频 | minor |
| 体验不佳但能完成 | 任意 | minor |
| 不影响行为 | 任意 | suggestion |

### Step 5：写 user_impact（违反宪法 #6 直接拒绝）

强制结构：「在 {场景} 下，{角色} {做什么} 时，遇到 {问题现象}，导致 {影响}」

四要素缺一不可。如果 raw_issue 没有数据支撑，用「[推断]」前缀。

### Step 6：写 suggestion（违反宪法 #5 直接拒绝）

强制三要素：
1. **改什么**（具体元素）
2. **改成什么**（具体方向）
3. **为什么**（链接原则 + 用户影响）

模板：
```
建议把 {元素} 从 {现状} 改为 {目标}，
当前违反 {原则 ID}（{原则名}），
{用户实际影响 / 推断}。
```

### Step 7：标 source_basis（违反宪法 #7 直接拒绝）

- `prd`：实现没满足 PRD 要求
- `screenshot`：PRD 没写、实现自由发挥
- `inferred`：都没明确，但违反通用启发式

### Step 8：去重

raw_issues 通常有重复，必须去重：
- 同一原则同一 module 触发多次 → 合并为 1 条 issue，evidence_refs 累加
- 跨多 module 的同类问题 → 合并到 M-GLOBAL
- 已知问题（在 historical-issues.md 中）→ `is_known_excluded` +1，不进主报告

## Few-shot 示例

### 输入 raw_issue

```json
{
  "raw_id": "RAW-007",
  "principle_id": "F2",
  "module_id": "M-001",
  "found_at": "screens/规则保存-提交后.png",
  "raw_observation": "保存按钮点击后无任何反馈，用户不确定是否成功"
}
```

### 期望输出 Issue

```json
{
  "id": "I-007",
  "title": "规则保存提交无加载反馈",
  "description": "在「保存规则草稿」场景下，运营专员点击「保存」按钮后，按钮无 loading 状态、无消息提示、无页面变化；约 3-5 秒后才跳转列表页。期间用户无法判断系统是否在处理。",
  "severity": "major",
  "principle_ids": ["F2"],
  "journey_stage_id": "JS-003",
  "task_id": "T-005",
  "module_id": "M-001",
  "evidence_refs": ["E-007", "E-008"],
  "user_impact": "在「保存规则草稿」场景下（高频，每条规则平均保存 5+ 次），运营专员点击保存后等待 3-5 秒无反馈，[推断] 用户会重复点击或刷新，可能导致重复提交。约 40% 用户在前 3 次使用中发生重复点击行为。",
  "suggestion": "建议把「保存」按钮从无反馈改为「点击后立即变 loading 状态（按钮文案「保存中...」+ 禁用）+ 完成后顶部 toast 提示「保存成功」」。当前违反 F2（系统状态可见性）：用户在异步操作中无法判断系统状态，是 B 端长操作的高频痛点。",
  "source_basis": "screenshot"
}
```

## 约束（与宪法严格对齐）

- ❌ `evidence_refs: []` → 拒（违反宪法 #1）
- ❌ severity 不在 critical/major/minor/suggestion 内 → 拒（违反宪法 #3）
- ❌ description 是「功能不存在」类问题 → 拒，标记 `out_of_scope`（违反宪法 #4）
- ❌ suggestion 仅写「优化体验」 → 拒（违反宪法 #5）
- ❌ user_impact 缺四要素 → 拒（违反宪法 #6）
- ❌ source_basis 为空 → 拒（违反宪法 #7）

## 总体输出约束

- 一次评估输出 issues 数量 15-40 条最合理
- < 10 条 → 怀疑测试覆盖不够，警告
- > 50 条 → 怀疑粒度太细，自动合并
- critical 占比 > 30% → 怀疑标过严，警告
- 没有任何 critical → 怀疑没真测试关键路径，警告

## Checkpoint C3

输出后会暂停，让用户决策：
- `continue`：问题清单合理
- `modify`：用户调整严重等级 / 归因 / 改进建议
- `supplement`：用户补充未被识别的问题

## 输出位置

- 写入 `state.issues`
- 持久化到 `runs/<run_id>/06-问题清单.json`
- 后续 report-generation 阶段渲染为 Excel + HTML

---

## 参考示例（Golden Sample）

以下是生产级问题的代表性示例（来自 case-001 数据规则配置平台）。

### 示例 1：工作台规则待办与其他待办无视觉区分

| 字段 | 值 |
|---|---|
| 严重等级 | major |
| 启发式原则 | F2 系统状态可见性, P3 一致性与标准化 |
| 旅程阶段 | JS-001 进入与定位 |
| 任务 | T-001 |
| 模块 | M-WORKBENCH |
| 基准来源 | screenshot |

**描述**：在「早晨查看待办」场景下，运营专员进入工作台，需要从 12 条混合待办中找出规则相关；当前所有待办字号、颜色、图标相同，平均需 8 秒才能定位 5 条规则相关待办。

**用户影响**：每天早晨运营专员需 8-15 秒定位规则待办，且漏看率约 23%。高频场景下累计认知负担显著。

**改进建议**：建议为规则相关待办增加视觉标识（左侧蓝色侧边条 + 「规则」标签），与其他待办形成视觉层级。当前违反 F2（需逐字阅读判断类型）和 P3（所有待办视觉权重相同）。

---

### 示例 2：规则编辑草稿丢失（无自动保存）

| 字段 | 值 |
|---|---|
| 严重等级 | critical |
| 启发式原则 | S1 用户控制度与自由度, F1 预防出错 |
| 旅程阶段 | JS-003 任务执行 |
| 任务 | T-005 |
| 模块 | M-001 |
| 基准来源 | screenshot |

**描述**：在编辑长规则（15+ 字段）时，如关闭浏览器或刷新页面，所有未提交的内容全部丢失。无自动保存、无离开警告、无草稿恢复。

**用户影响**：在「编辑长规则中途被打断」场景下（每条规则至少发生 1 次，常发生于会议、电话），运营专员所有 15 个字段的输入全部丢失，平均损失工作时长 25 分钟，约 60% 用户经历过 ≥ 1 次完整丢失。

**改进建议**：建议为规则编辑表单增加「每 30 秒自动保存草稿」+ 「关闭页面提示「确定离开？未保存的内容会丢失」」。当前违反 S1（用户无法保留中途状态）和 F1（应在错误发生前阻止，而非接受丢失）。

---

### 示例 3：规则保存提交无加载反馈

| 字段 | 值 |
|---|---|
| 严重等级 | major |
| 启发式原则 | F2 系统状态可见性 |
| 旅程阶段 | JS-003 任务执行 |
| 任务 | T-007 |
| 模块 | M-001 |
| 基准来源 | screenshot |

**描述**：在「保存规则草稿」场景下，运营专员点击「保存」后，按钮无 loading 状态、无消息提示、无页面变化；约 3-5 秒后才跳转。

**用户影响**：高频场景（每条规则平均保存 5+ 次），运营专员等待 3-5 秒无反馈，约 40% 用户在前 3 次使用中重复点击保存按钮。

**改进建议**：建议把「保存」按钮从无反馈改为「点击后立即变 loading 状态（按钮文案「保存中...」+ 禁用）+ 完成后顶部 toast 提示「保存成功」」。当前违反 F2。

---

**关键特征**（你的输出必须达到这个标准）：
1. 每条问题都有具体截图证据（不是 [inferred]）
2. 用户影响包含"场景 + 角色 + 问题 + 影响"四要素
3. 改进建议说清"改什么 / 改成什么 / 为什么"
4. 严重等级有明确判定依据
5. 问题描述具体到操作步骤和数据
