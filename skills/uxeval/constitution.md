# UXEval 评估宪法

> 这 8 条规则是 UXEval Skill 不可违反的硬约束。
> 任何阶段的输出违反任一条款都会被 Kernel 拒绝并重试；连续 2 次违反则进入失败模式提交人工。

---

## 1. 每条问题必须绑定证据（evidence_refs 非空）

**Why**：体验问题必须从主观描述变成可沟通证据，才能推动产品和研发认同。

**怎么实现**：
- 每个 `Issue.evidence_refs` 字段至少包含 1 条 `Evidence` 引用
- `Evidence.kind` 只能是 `screenshot / dom / trace / video` 四类之一
- 所有 evidence 的 `path` 必须实际存在于 `evidence/` 目录

**违反示例（拒）**：
```yaml
- id: I-001
  title: "登录后首页加载慢"
  evidence_refs: []   # ✗ 空
```

**合规示例（接受）**：
```yaml
- id: I-001
  evidence_refs: [E-001, E-002]
```

---

## 2. 不输出敏感信息

**Why**：评估产物会被分享、归档、长期沉淀，敏感信息一旦泄露不可挽回。

**禁止泄露**：
- 真实账号 / 密码 / Token / API Key
- 真实人名 / 手机号 / 身份证号 / 邮箱（除非本来就是公开数据）
- 内部测试环境完整 URL（仅可写域名级别，如 `*.example.internal`）
- 数据库连接串、SSH 密钥

**怎么实现**：
- Kernel 的 `Sanitizer` 在每个 stage 输出后扫描
- `image-analyzer` 会基于文件名 / OCR / `.md` 说明文件输出风险提示，但仍不提供像素级敏感信息自动打码
- 如果截图来自真实环境，或 `signal_warnings` / OCR 文本提示可能含敏感内容，必须人工复核并打码
- evidence 路径不能包含真实用户名

---

## 3. 严重等级在合法枚举内

**合法枚举**：`critical / major / minor / suggestion`

| 等级 | 标准 |
|---|---|
| `critical` | 用户无法完成核心任务，或数据/资金/合规风险 |
| `major` | 用户能完成任务但显著阻碍效率，或多步骤才能绕过 |
| `minor` | 用户体验不佳但不影响完成任务 |
| `suggestion` | 优化建议，对用户行为无直接影响 |

**违反示例（拒）**：`severity: "中"`、`severity: "P0"`、`severity: "high"`

---

## 4. 不把功能存在与否当作主要体验问题

**Why**：UXEval 的边界是「体验质量」，不是「需求覆盖」。功能缺失是产品 PRD 范围问题，不是体验问题。

**怎么处理**：
- 「PRD 要求的搜索功能未实现」→ 不是 UXEval 范围，标记为 `out_of_scope`
- 「搜索功能存在但找不到入口」→ ✓ UXEval 问题（`F2 系统状态可见性`）
- 「搜索结果排序不合理」→ ✓ UXEval 问题（`S3 灵活性与效率`）

**判断口诀**：「功能在不在」交给 `/design-acceptance`，「功能好不好用」才是 UXEval。

---

## 5. 建议方案必须可执行

**Why**：「这里要改一下」不是建议，是吐槽。可执行建议必须说清楚 改什么 / 改成什么 / 为什么。

**强制三要素**：
- **改什么**：明确指向元素 / 流程 / 文案
- **改成什么**：给出具体方向（不必给设计稿，但要给明确选择）
- **为什么**：链接到对应启发式原则 + 用户影响

**违反示例（拒）**：
> 建议优化登录页

**合规示例（接受）**：
> 建议把「登录」按钮从次要按钮（灰色边框）改为主按钮（实心填充蓝），
> 因为当前页面有 6 个同级按钮，违反了 P3（一致性与标准化），
> 用户首次访问时点击登录按钮的成功率仅 32%（数据来自 web-automation trace）。

---

## 6. 问题描述必须包含用户影响

**Why**：问题描述要从「设计师视角」转到「用户视角」，否则推动力为零。

**强制结构**：「在 {场景} 下，{角色} {做什么}时，遇到 {问题现象}，导致 {影响}」

**违反示例（拒）**：
> 按钮太小

**合规示例（接受）**：
> 在「数据规则配置」场景下，运营专员保存配置时，
> 「保存」按钮被遮罩层下方的浮窗遮挡 30%，
> 导致用户多次点击未响应、误以为系统卡死，平均额外耗时 8 秒。

---

## 7. PRD 与实现冲突时标明基准来源

**Why**：评估时常会遇到「页面这样做了，但 PRD 没写」或「PRD 这样写了，页面没做到」。这种情况下，问题归因必须说清楚以哪一方为准。

**`Issue.source_basis` 必须明确填**：
- `prd`：以 PRD 为基准（实现没满足 PRD 时使用，常见于设计还原偏差）
- `screenshot`：以实现为基准（PRD 没写、实现自由发挥时使用）
- `inferred`：基于通用启发式原则推断（PRD 与实现都没明确，但违反通用原则）

**违反示例（拒）**：
```yaml
- id: I-005
  description: "PRD 说这里有筛选，实现没有"
  source_basis: ""   # ✗ 没填
```

**合规示例（接受）**：
```yaml
- id: I-005
  description: "PRD 第 3.2 节要求支持多条件筛选，实现仅有单条件下拉。在「数据查询」场景下..."
  source_basis: prd
```

---

## 8. 证据截图必须与问题场景匹配

**Why**：客户端模式（截图）的固有局限是无法验证交互行为，只能看到静态画面。如果问题描述的场景与证据截图的实际内容不匹配，说明证据无效或推断错误。

**怎么实现**：
- 每条问题的 `description` 必须明确场景（如"在「配置数据源节点」场景下"）
- 每条问题的 `evidence_refs` 引用的截图必须真实展示该场景，或由说明文件 / 人工证据描述明确覆盖该场景
- Stage 6 问题检测时必须交叉校验：问题场景 vs OCR / 文件名 / 说明文件 / 人工证据描述是否匹配
- 任何 client 模式自动提取的证据线索都必须保留 `confidence / source_channel / evidence_basis`
- 只有 `verification_status == verified` 的 issue 才允许进入主问题清单
- 如果截图不匹配，有三种处理方式：
  1. 截图错误 → 更换正确的截图
  2. 场景推断错误 → 删除该问题
  3. 当前截图只有低置信度 hint、或 `evidence_assessment` 已判定证据不足 → 标注 `[需现场验证]` 或 `[证据不足]` 并移到附录

**违反示例（拒）**：
```yaml
- id: I-002
  description: "在「配置数据源节点」场景下，数据源下拉无搜索..."
  evidence_refs: [S02]  # S02 实际是"空间详情页"，不是数据源下拉
```

**合规示例（接受）**：
```yaml
- id: I-002
  description: "在「配置数据源节点」场景下，数据源下拉无搜索..."
  evidence_refs: [S05]  # S05 确实显示数据源下拉框界面
  note: "截图显示下拉框已展开，列表中无搜索框"
```

或者（如果截图未覆盖）：
```yaml
- id: I-002-unverified
  description: "PRD F-14 要求数据源下拉支持搜索，但现有截图未覆盖该场景"
  evidence_refs: []
  source_basis: prd
  status: "[需现场验证]"
  # 移到附录 unverified_issues
```

---

## 验证机制

Kernel 在每个 stage 输出后会跑这 7 条 check：

```python
def verify_constitution(stage_output: dict) -> list[ViolationError]:
    violations = []
    if "issues" in stage_output:
        for issue in stage_output["issues"]:
            if not issue.evidence_refs:
                violations.append(ViolationError(rule=1, issue_id=issue.id))
            if not issue.user_impact:
                violations.append(ViolationError(rule=6, issue_id=issue.id))
            if issue.severity not in ALLOWED_SEVERITIES:
                violations.append(ViolationError(rule=3, issue_id=issue.id))
            if not issue.suggestion or len(issue.suggestion) < 30:
                violations.append(ViolationError(rule=5, issue_id=issue.id))
            if not issue.source_basis:
                violations.append(ViolationError(rule=7, issue_id=issue.id))
    if Sanitizer.scan(stage_output).has_pii:
        violations.append(ViolationError(rule=2))
    return violations
```

连续 2 次违反同一条 → stage 标记为 `failed`，进入人工 review 队列。

---

## 自检执行（Stage 6 输出前必须执行）

> 这 7 步检查是 Stage 6（问题检测 + 归因）输出前的强制流程。
> 每条问题必须通过全部检查，不通过的问题直接删除或移到附录，不进入主报告。

### 执行方式

逐条检查所有问题（raw_issues），按以下顺序：

**□ 检查 1：证据绑定**
- 每条问题是否引用了具体截图文件名？
- 违反 → 标记 `[unverified]` 并移到附录

**□ 检查 1.5：场景-证据匹配**
- 每条问题的场景描述与证据截图内容是否匹配？
- 违反 → 标记 `[需现场验证]` 并移到附录

**□ 检查 2：严重等级合法性**
- severity 是否在 `critical / major / minor / suggestion` 内？
- 违反 → 拒绝输出，重新判定

**□ 检查 3：功能缺失混入**
- 是否有"功能不存在"类问题混入？
- 违反 → 移到 `out_of_scope` 清单

**□ 检查 4：建议可执行性**
- 每条建议是否说清"改什么 / 改成什么 / 为什么"？
- 违反 → 补充建议或删除该问题

**□ 检查 5：用户影响完整性**
- user_impact 是否包含"场景 + 角色 + 问题 + 影响"四要素？
- 违反 → 补充或删除该问题

**□ 检查 6：推断比例与交付资格**
- `[inferred]` 标记的问题是否超过总数 30%？
- 超过，或 `evidence_assessment.delivery_status` 不是 `final_delivery_ready / fallback_safe` → 回去补截图分析（Stage 5b）并要求补资料
- 如果 `audited_delivery_assessment.delivery_status != "final_delivery_ready"`，不得交付最终报告

**□ 检查 7：核心场景覆盖**
- 是否遗漏了 PRD 中的核心场景？
- 对比 Stage 1 的 `key_tasks`，缺失 → 补充分析

### 输出要求

- 通过自检、且 `verification_status == verified` 的问题 → 进入 `issues` 主清单
- 未通过检查 1/4/5 → 移到附录 `unverified_issues`
- 未通过检查 3 → 移到附录 `out_of_scope_issues`
- 未通过检查 2 → 拒绝输出，重新推理
- 未通过检查 6/7 → 回到 Stage 5b 重新分析

---
