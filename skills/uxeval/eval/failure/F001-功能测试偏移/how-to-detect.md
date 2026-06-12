# 如何检测与防御

## 检测信号

### 信号 1：task 没有 applicable_principles

```python
def detect_function_test_bias(tasks: list[Task]) -> list[str]:
    bad_tasks = [t for t in tasks if not t.applicable_principles]
    if len(bad_tasks) / len(tasks) > 0.10:
        return [f"{len(bad_tasks)} 个任务无原则映射，疑似功能测试"]
    return []
```

阈值：> 10% 的 task 无原则映射 → 报警

### 信号 2：success_criteria 含功能验证关键词

```python
FUNCTION_KEYWORDS = ["跳转正确", "按钮可点击", "提示成功", "返回 200", "API 响应"]

def detect_function_criteria(task: Task) -> bool:
    for criterion in task.success_criteria:
        if any(kw in criterion for kw in FUNCTION_KEYWORDS):
            return True
    return False
```

### 信号 3：issue 没有 user_impact 或描述过短

```python
if not issue.user_impact or len(issue.user_impact) < 50:
    raise ConstitutionViolation(rule=6, issue_id=issue.id)
```

### 信号 4：issue 的 principle_ids 为空

宪法直接拒绝（schema 已强制 min_length=1）。

### 信号 5：critical 占比异常

```python
critical_ratio = critical_count / total_count
if critical_ratio > 0.30:
    warn("critical 占比 > 30%，怀疑功能 bug 被错标为 critical")
```

## 防御措施（已落地到 v0.2.0）

### 措施 1：宪法第 4 条（已加）

> 不把功能存在与否当作主要体验问题：功能缺失记为产品问题不是体验问题

### 措施 2：task-generation prompt 加判别口诀（已加）

> 「点不点得了」是功能问题；「点不点得到 / 点了爽不爽」是体验问题

### 措施 3：schema 强制 evidence_refs.min_length=1 + user_impact 必填（已加）

```python
class Issue(BaseModel):
    evidence_refs: list[str] = Field(..., min_length=1)
    user_impact: str = Field(...)
    suggestion: str = Field(...)
```

### 措施 4：每个 task 必须 ≥ 1 条 applicable_principles（已加到 prompt）

> ✅ 每个 task 必须 ≥ 1 条 applicable_principles
> ❌ success_criteria 出现「按钮可点击」「跳转正确」→ 拒绝

### 措施 5：Checkpoint C2 强提示（已加到 pipeline.yaml）

```yaml
checkpoint:
  id: C2
  message: "请校准任务清单（重点检查：是否偏功能测试，是否漏掉关键体验任务）。"
```

### 措施 6：promptfoo 在 task-generation 后自动跑 forbidden 检查

```yaml
# eval/promptfoo.yaml 中
- name: detect-function-test-bias
  assert:
    - type: javascript
      value: |
        const bad = output.task_checklist_full.filter(t => 
          !t.applicable_principles?.length || 
          t.success_criteria.some(c => /跳转|可点击|API/.test(c))
        );
        return bad.length / output.task_checklist_full.length < 0.10;
```

## Postmortem 落地清单

- [x] constitution 加规则 #4
- [x] prompt 04 加判别口诀 + 反例
- [x] Issue schema 加 min_length=1 / 必填字段
- [x] Checkpoint C2 提示语
- [x] promptfoo 自动 check
- [x] 失败案例文档化（本目录）
