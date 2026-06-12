# Quality Gates Implementation

## 概述

Quality Gates 是 DesignOS 的核心质量保障机制，确保设计推理流程的每个阶段都符合资深设计师标准。

## 核心原则

1. **质量门不得被绕过**（核心原则 6）
2. **质量门失败必须有明确的处理策略**
3. **所有质量门结果必须可追溯**

## 质量门类型

### 1. Schema Gate
**目的**: 确保输出符合 artifact schema

**检测时机**: 每个 stage 输出后

**检测逻辑**:
```python
def schema_gate(artifact: dict, schema: dict) -> GateResult:
    """
    验证 artifact 是否符合 schema
    """
    validator = jsonschema.Draft7Validator(schema)
    errors = list(validator.iter_errors(artifact))
    
    if not errors:
        return GateResult(
            gate_id="schema_gate",
            status="pass",
            message="Artifact符合schema要求"
        )
    
    # 区分 critical 和 non-critical 错误
    critical_errors = [e for e in errors if is_critical_field(e.path)]
    
    if critical_errors:
        return GateResult(
            gate_id="schema_gate",
            status="blocked",
            errors=format_errors(critical_errors),
            recommendation="修复以下必需字段后重试"
        )
    else:
        return GateResult(
            gate_id="schema_gate",
            status="warning",
            errors=format_errors(errors),
            recommendation="建议补充以下可选字段"
        )
```

**失败处理**:
- Critical 字段缺失 → `blocked`
- Optional 字段缺失 → `warning`

---

### 2. Traceability Gate
**目的**: 确保关键决策可追溯到上游资产

**检测时机**: 生成 traceability_map 后

**检测逻辑**:
```python
def traceability_gate(
    traceability_map: dict,
    reasoning_assets: dict,
    output_artifact: dict
) -> GateResult:
    """
    验证可追溯性完整性
    """
    issues = []
    
    # 检查 1: 所有页面是否可追溯到 user_task
    if output_artifact['artifact_type'] == 'information_architecture':
        for page in output_artifact['pages']:
            if not has_task_mapping(page, reasoning_assets['user_task_map']):
                issues.append({
                    "type": "unauthorized_page",
                    "page_id": page['page_id'],
                    "message": f"页面 {page['page_name']} 无法追溯到任何 user_task"
                })
    
    # 检查 2: 关键决策是否有追溯依据
    for decision in traceability_map.get('decision_trace', []):
        if not decision.get('based_on'):
            issues.append({
                "type": "decision_without_basis",
                "decision_id": decision['decision_id'],
                "message": f"决策 {decision['decision_point']} 缺少追溯依据"
            })
    
    # 检查 3: 输入覆盖率
    coverage = traceability_map['coverage_analysis']['input_coverage']
    if coverage < 0.5:
        issues.append({
            "type": "low_input_coverage",
            "coverage": coverage,
            "message": f"输入覆盖率过低 ({coverage:.0%})"
        })
    
    if not issues:
        return GateResult(
            gate_id="traceability_gate",
            status="pass"
        )
    
    critical_issues = [i for i in issues if i['type'] in ['unauthorized_page', 'low_input_coverage']]
    
    if critical_issues:
        return GateResult(
            gate_id="traceability_gate",
            status="blocked",
            issues=critical_issues,
            recommendation="必须修复以下追溯性问题"
        )
    else:
        return GateResult(
            gate_id="traceability_gate",
            status="warning",
            issues=issues,
            recommendation="建议补充追溯依据"
        )
```

**失败处理**:
- unauthorized_page → `blocked`
- low_input_coverage (< 50%) → `blocked`
- decision_without_basis → `warning`

---

### 3. Gap Transparency Gate
**目的**: 确保输入缺失被显式记录，不被静默补全

**检测时机**: input-diagnosis stage 后

**检测逻辑**:
```python
def gap_transparency_gate(requirement_inventory: dict) -> GateResult:
    """
    验证 gap 透明度
    """
    gaps = requirement_inventory['gaps']
    critical_gaps = [g for g in gaps if g['impact'] == 'critical']
    
    # 检查是否有 critical gaps 但 readiness_decision 仍然是 proceed
    decision = requirement_inventory['readiness_decision']['decision']
    
    if critical_gaps and decision == 'proceed':
        return GateResult(
            gate_id="gap_transparency_gate",
            status="blocked",
            message="存在 critical gaps 但决策为 proceed，违反核心原则 4",
            critical_gaps=critical_gaps,
            recommendation="必须进入 blocked 或 fallback_safe 状态"
        )
    
    # 检查完整性评分
    overall_score = requirement_inventory['completeness_assessment']['overall_score']
    
    if overall_score < 0.3:
        return GateResult(
            gate_id="gap_transparency_gate",
            status="blocked",
            message=f"输入完整性过低 ({overall_score:.0%})",
            recommendation="输入质量不足以生成合格产物，必须补充输入"
        )
    
    if overall_score < 0.5 and decision != 'fallback_safe':
        return GateResult(
            gate_id="gap_transparency_gate",
            status="warning",
            message=f"输入完整性中等 ({overall_score:.0%})，建议降级到 fallback_safe",
            recommendation="当前模式可能产生低质量产物"
        )
    
    return GateResult(
        gate_id="gap_transparency_gate",
        status="pass"
    )
```

**失败处理**:
- critical gaps + proceed → `blocked`
- overall_score < 0.3 → `blocked`
- overall_score < 0.5 + proceed → `warning`

---

### 4. Inference Limit Gate
**目的**: 限制推断内容占比，防止"AI 幻觉"

**检测时机**: 每个 reasoning asset 生成后

**检测逻辑**:
```python
def inference_limit_gate(artifact: dict) -> GateResult:
    """
    验证推断内容占比
    """
    inferred_fields = artifact.get('inferred_fields', [])
    
    # 计算推断占比
    total_fields = count_all_fields(artifact)
    inferred_count = len(inferred_fields)
    inferred_ratio = inferred_count / total_fields if total_fields > 0 else 0
    
    THRESHOLD_BLOCKED = 0.5  # 50% 阈值
    THRESHOLD_WARNING = 0.3  # 30% 阈值
    
    if inferred_ratio >= THRESHOLD_BLOCKED:
        return GateResult(
            gate_id="inference_limit_gate",
            status="blocked",
            message=f"推断内容占比过高 ({inferred_ratio:.0%})",
            inferred_count=inferred_count,
            total_fields=total_fields,
            recommendation="输入不足，无法生成高质量产物。必须补充输入或降级到 fallback_safe"
        )
    
    if inferred_ratio >= THRESHOLD_WARNING:
        return GateResult(
            gate_id="inference_limit_gate",
            status="warning",
            message=f"推断内容占比较高 ({inferred_ratio:.0%})",
            inferred_count=inferred_count,
            total_fields=total_fields,
            recommendation="建议标记为需人工复核"
        )
    
    return GateResult(
        gate_id="inference_limit_gate",
        status="pass",
        inferred_ratio=inferred_ratio
    )
```

**失败处理**:
- inferred_ratio >= 50% → `blocked`
- inferred_ratio >= 30% → `warning`

---

### 5. Code Constraint Gate
**目的**: 确保生成的代码受设计推理资产约束

**检测时机**: code-generation stage 后

**检测逻辑**:
```python
def code_constraint_gate(
    generated_code: dict,
    information_architecture: dict,
    component_strategy: dict,
    state_matrix: dict
) -> GateResult:
    """
    验证代码是否受推理资产约束
    """
    issues = []
    
    # 检查 1: 所有生成的页面是否来自 IA
    generated_pages = extract_pages_from_code(generated_code)
    ia_pages = {p['page_id'] for p in information_architecture['pages']}
    
    unauthorized_pages = [p for p in generated_pages if p not in ia_pages]
    if unauthorized_pages:
        issues.append({
            "type": "unauthorized_page",
            "pages": unauthorized_pages,
            "message": f"发现 {len(unauthorized_pages)} 个未授权页面（不在 IA 中）"
        })
    
    # 检查 2: 所有使用的组件是否来自 component_strategy
    used_components = extract_components_from_code(generated_code)
    allowed_components = {c['component_id'] for c in component_strategy['component_inventory']}
    
    unauthorized_components = [c for c in used_components if c not in allowed_components]
    if unauthorized_components:
        issues.append({
            "type": "unauthorized_component",
            "components": unauthorized_components,
            "message": f"发现 {len(unauthorized_components)} 个未授权组件（不在 component_strategy 中）"
        })
    
    # 检查 3: 状态实现是否与 state_matrix 一致
    for page in generated_pages:
        expected_states = get_expected_states(page, state_matrix)
        actual_states = extract_states_from_page_code(generated_code, page)
        
        missing_states = set(expected_states) - set(actual_states)
        if missing_states:
            issues.append({
                "type": "missing_state",
                "page": page,
                "missing_states": list(missing_states),
                "message": f"页面 {page} 缺少状态: {', '.join(missing_states)}"
            })
    
    if not issues:
        return GateResult(
            gate_id="code_constraint_gate",
            status="pass"
        )
    
    critical_issues = [i for i in issues if i['type'] in ['unauthorized_page', 'missing_state']]
    
    if critical_issues:
        return GateResult(
            gate_id="code_constraint_gate",
            status="blocked",
            issues=critical_issues,
            recommendation="代码生成违反约束，必须修复"
        )
    else:
        return GateResult(
            gate_id="code_constraint_gate",
            status="warning",
            issues=issues,
            recommendation="建议补充组件定义或修正代码"
        )
```

**失败处理**:
- unauthorized_page → `blocked`
- missing_state → `blocked`
- unauthorized_component → `warning`

---

## 质量门执行器

```python
class QualityGateExecutor:
    """质量门执行器"""
    
    def __init__(self):
        self.gates = {
            'schema_gate': schema_gate,
            'traceability_gate': traceability_gate,
            'gap_transparency_gate': gap_transparency_gate,
            'inference_limit_gate': inference_limit_gate,
            'code_constraint_gate': code_constraint_gate
        }
        self.results = []
    
    def execute(self, gate_id: str, **kwargs) -> GateResult:
        """执行单个质量门"""
        gate_func = self.gates.get(gate_id)
        if not gate_func:
            raise ValueError(f"Unknown gate: {gate_id}")
        
        result = gate_func(**kwargs)
        self.results.append(result)
        
        # 根据结果决定是否阻塞
        if result.status == 'blocked':
            raise QualityGateBlocked(result)
        
        return result
    
    def execute_all(self, stage: str, context: dict) -> List[GateResult]:
        """执行某个 stage 的所有质量门"""
        stage_gates = get_gates_for_stage(stage)
        results = []
        
        for gate_id in stage_gates:
            try:
                result = self.execute(gate_id, **context)
                results.append(result)
            except QualityGateBlocked as e:
                # 记录阻塞原因并停止执行
                results.append(e.result)
                break
        
        return results
    
    def get_summary(self) -> dict:
        """获取质量门执行摘要"""
        return {
            "total_gates": len(self.results),
            "passed": len([r for r in self.results if r.status == 'pass']),
            "warnings": len([r for r in self.results if r.status == 'warning']),
            "blocked": len([r for r in self.results if r.status == 'blocked']),
            "results": self.results
        }
```

---

## 质量门配置

```yaml
# kernel/quality-gates/gate-config.yaml

stages:
  input-diagnosis:
    gates:
      - gap_transparency_gate
    on_blocked: stop_execution
    on_warning: continue_with_flag
  
  design-objectives:
    gates:
      - schema_gate
      - inference_limit_gate
    on_blocked: stop_execution
    on_warning: continue_with_flag
  
  user-task-modeling:
    gates:
      - schema_gate
      - inference_limit_gate
      - traceability_gate
    on_blocked: stop_execution
  
  information-architecture:
    gates:
      - schema_gate
      - traceability_gate
    on_blocked: stop_execution
  
  code-generation:
    gates:
      - code_constraint_gate
    on_blocked: stop_execution
  
  traceability-generation:
    gates:
      - schema_gate
      - traceability_gate
    on_blocked: stop_execution

thresholds:
  inference_limit:
    warning: 0.3
    blocked: 0.5
  
  input_completeness:
    warning: 0.5
    blocked: 0.3
  
  input_coverage:
    warning: 0.7
    blocked: 0.5
```

---

## 失败处理策略

### Blocked 模式
```python
def handle_blocked(result: GateResult, context: dict):
    """处理 blocked 状态"""
    
    # 1. 停止执行
    context['execution_status'] = 'blocked'
    
    # 2. 生成阻塞报告
    blocker_report = {
        "gate_id": result.gate_id,
        "blocked_at": context['current_stage'],
        "blockers": result.issues or result.errors,
        "recommendation": result.recommendation,
        "user_action_required": True
    }
    
    # 3. 记录到 traceability_map
    context['traceability_map']['quality_gate_trace']['gates_failed'].append({
        "gate_id": result.gate_id,
        "gate_name": result.gate_name,
        "failure_reason": result.message
    })
    
    # 4. 返回给用户
    return {
        "status": "blocked",
        "message": f"执行已阻塞于 {context['current_stage']} 阶段",
        "blocker_report": blocker_report
    }
```

### Fallback Safe 模式
```python
def handle_fallback_safe(context: dict):
    """降级到低保真模式"""
    
    # 1. 切换到 PM 模式
    context['mode'] = 'pm'
    context['fidelity'] = 'low'
    
    # 2. 调整质量门阈值
    context['quality_thresholds'] = {
        'inference_limit': 0.6,  # 允许更多推断
        'input_completeness': 0.4  # 降低输入要求
    }
    
    # 3. 标记所有输出为"需人工复核"
    context['professional_gap_report']['human_review_requirements'] = {
        "review_required": True,
        "review_priority": "high",
        "review_focus_areas": ["所有设计推理资产（因输入不足降级到 fallback_safe）"]
    }
    
    # 4. 记录降级原因
    context['warnings'].append({
        "warning_id": "WARN-FALLBACK",
        "severity": "high",
        "message": "因输入质量不足，已降级到低保真模式（PM 模式）",
        "recommendation": "补充输入后可切换到高保真模式"
    })
    
    return context
```

### Warning 模式
```python
def handle_warning(result: GateResult, context: dict):
    """处理 warning 状态"""
    
    # 1. 继续执行
    context['execution_status'] = 'proceeding_with_warnings'
    
    # 2. 记录 warning
    context['warnings'].append({
        "warning_id": f"WARN-{result.gate_id.upper()}",
        "gate_id": result.gate_id,
        "severity": "medium",
        "message": result.message,
        "recommendation": result.recommendation
    })
    
    # 3. 标记需人工复核
    if result.gate_id in ['inference_limit_gate', 'traceability_gate']:
        context['professional_gap_report']['human_review_requirements']['review_required'] = True
        context['professional_gap_report']['human_review_requirements']['review_focus_areas'].append(
            f"{result.gate_id}: {result.message}"
        )
    
    return context
```

---

## 测试要求

### 单元测试
```python
# tests/quality_gates/test_schema_gate.py

def test_schema_gate_pass():
    artifact = create_valid_artifact()
    schema = load_schema('design_objectives')
    result = schema_gate(artifact, schema)
    assert result.status == 'pass'

def test_schema_gate_blocked_missing_required_field():
    artifact = create_artifact_missing_required_field()
    schema = load_schema('design_objectives')
    result = schema_gate(artifact, schema)
    assert result.status == 'blocked'
    assert 'business_goals' in result.errors

def test_schema_gate_warning_missing_optional_field():
    artifact = create_artifact_missing_optional_field()
    schema = load_schema('design_objectives')
    result = schema_gate(artifact, schema)
    assert result.status == 'warning'
```

### 集成测试
```python
# tests/integration/test_quality_gates_integration.py

def test_pipeline_blocked_by_gap_transparency_gate():
    """测试 critical gaps 阻塞执行"""
    prd = load_low_quality_prd()  # completeness < 0.3
    
    with pytest.raises(QualityGateBlocked) as excinfo:
        run_pipeline(prd)
    
    assert excinfo.value.gate_id == 'gap_transparency_gate'
    assert 'completeness' in excinfo.value.message

def test_pipeline_fallback_safe_on_medium_quality_input():
    """测试中等质量输入降级到 fallback_safe"""
    prd = load_medium_quality_prd()  # completeness 0.5
    
    result = run_pipeline(prd)
    
    assert result['mode'] == 'pm'
    assert result['fidelity'] == 'low'
    assert result['warnings']
```

---

## 版本历史

- **v1.0.0** (2026-06-09 P1): 完整质量门实现
