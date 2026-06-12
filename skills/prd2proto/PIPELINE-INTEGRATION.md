# Pipeline v2 Integration Guide

如何将 P0/P1 的 Quality Gates 和 Traceability 集成到 prd2proto pipeline。

---

## 架构概览

```
pipeline-v2.yaml
  ↓
prompts-v2/01-17-*.md
  ↓
kernel/quality-gates/gates.py (验证输出)
  ↓
kernel/traceability/tracer.py (生成追溯地图)
  ↓
最终产物 + professional_gap_report
```

---

## Runtime 集成

### 1. Quality Gates 集成

在每个 stage 执行后，调用对应的 quality gates：

```python
from kernel.quality_gates.gates import QualityGateExecutor, QualityGateBlocked

executor = QualityGateExecutor()

try:
    # 执行 stage
    output = execute_stage('input-diagnosis', inputs)
    
    # 验证质量门
    result = executor.execute(
        'gap_transparency_gate',
        requirement_inventory=output
    )
    
    if result.status == GateStatus.WARNING:
        context['warnings'].append(result.to_dict())
    
except QualityGateBlocked as e:
    # 处理阻塞
    return handle_blocked(e.result, context)
```

### 2. Traceability 集成

在生成最终产物后，自动生成 traceability_map：

```python
from kernel.traceability.tracer import TraceabilityGenerator

generator = TraceabilityGenerator()

# 收集所有推理资产
reasoning_assets = {
    'design_objectives': design_objectives,
    'user_task_map': user_task_map,
    'information_architecture': information_architecture,
    # ...
}

# 生成追溯地图
traceability_map = generator.generate_traceability_map(
    output_artifact=prototype_code,
    input_trace={
        "primary_inputs": [{"input_id": "prd-v1.2.pdf"}]
    },
    reasoning_assets=reasoning_assets
)

# 保存
save_artifact(traceability_map, "output/design-traceability-map.json")
```

### 3. Fallback Safe 处理

当输入质量不足时，自动降级：

```python
def handle_fallback_safe(context: dict):
    """降级到低保真模式"""
    
    # 1. 切换模式
    context['mode'] = 'pm'
    context['fidelity'] = 'low'
    
    # 2. 调整质量门阈值
    context['quality_thresholds']['inference_limit']['blocked'] = 0.6
    context['quality_thresholds']['input_completeness']['blocked'] = 0.4
    
    # 3. 标记所有输出需人工复核
    context['professional_gap_report']['human_review_requirements'] = {
        "review_required": True,
        "review_priority": "high",
        "review_focus_areas": ["所有设计推理资产（因输入不足降级）"]
    }
    
    # 4. 记录降级原因
    context['warnings'].append({
        "warning_id": "WARN-FALLBACK",
        "severity": "high",
        "message": "因输入质量不足，已降级到低保真模式（PM 模式）"
    })
    
    return context
```

---

## Stage Execution Flow

```
1. Load prompt from prompts-v2/XX-*.md
   ↓
2. Execute LLM with prompt + inputs
   ↓
3. Parse output as JSON
   ↓
4. Validate against schema (schema_gate)
   ↓
5. Execute stage-specific quality gates
   ↓
6. If BLOCKED:
     - Stop execution
     - Return blocker_report
   ↓
7. If WARNING:
     - Continue with flag
     - Add to warnings list
   ↓
8. If PASS:
     - Continue to next stage
   ↓
9. Save output artifact
```

---

## Quality Gate Configuration

从 `kernel/quality-gates/gate-config.yaml` 加载配置：

```python
import yaml

with open('kernel/quality-gates/gate-config.yaml') as f:
    gate_config = yaml.safe_load(f)

# 获取 stage 的质量门列表
stage_gates = gate_config['stages']['input-diagnosis']['gates']

# 获取阈值
thresholds = gate_config['thresholds']
```

---

## Error Handling

### Blocked 处理

```python
def handle_blocked(result: GateResult, context: dict) -> dict:
    """处理阻塞状态"""
    
    blocker_report = {
        "status": "blocked",
        "gate_id": result.gate_id,
        "blocked_at": context['current_stage'],
        "blockers": result.issues or result.errors,
        "recommendation": result.recommendation,
        "user_action_required": True
    }
    
    # 记录到 traceability_map
    context['traceability_map']['quality_gate_trace'] = {
        "gates_failed": [{
            "gate_id": result.gate_id,
            "failure_reason": result.message
        }]
    }
    
    return blocker_report
```

### Warning 处理

```python
def handle_warning(result: GateResult, context: dict):
    """处理警告状态"""
    
    context['warnings'].append({
        "warning_id": f"WARN-{result.gate_id.upper()}",
        "gate_id": result.gate_id,
        "severity": "medium",
        "message": result.message,
        "recommendation": result.recommendation
    })
    
    # 标记需人工复核
    if result.gate_id in ['inference_limit_gate', 'traceability_gate']:
        context['professional_gap_report']['human_review_requirements']['review_required'] = True
    
    return context
```

---

## Output Structure

```
output/prd2proto/
├── design-reasoning/
│   ├── requirement-inventory.json
│   ├── design-objectives.json
│   ├── user-task-map.json
│   ├── business-flow.json
│   ├── user-journey-map.json
│   ├── information-architecture.json
│   ├── page-flow.json
│   ├── page-structure.json
│   ├── component-strategy.json
│   ├── state-matrix.json
│   ├── interaction-rules.json
│   └── design-traceability-map.json
├── prototype/
│   ├── app/
│   ├── design-spec.md
│   ├── tokens.json
│   └── tokens.css
└── quality/
    ├── professional-gap-report.json
    ├── quality-gate-results.json
    └── review-checklist.md
```

---

## Testing

### 单元测试

```python
# tests/integration/test_pipeline_v2.py

def test_input_diagnosis_blocked_on_low_quality():
    """测试低质量输入被阻塞"""
    
    prd = load_low_quality_prd()  # completeness < 0.3
    
    with pytest.raises(QualityGateBlocked) as excinfo:
        run_pipeline_v2(prd)
    
    assert excinfo.value.result.gate_id == 'gap_transparency_gate'
    assert 'completeness' in excinfo.value.result.message

def test_fallback_safe_on_medium_quality():
    """测试中等质量输入降级"""
    
    prd = load_medium_quality_prd()  # completeness 0.5
    
    result = run_pipeline_v2(prd)
    
    assert result['mode'] == 'pm'
    assert result['fidelity'] == 'low'
    assert len(result['warnings']) > 0
```

---

## P1 Limitations

### Runtime Integration (未实现)

- ❌ Pipeline executor 需要集成 quality gates
- ❌ Pipeline executor 需要集成 traceability generator
- ❌ Blocked/Fallback Safe 处理需要完整实现

### Prompts (部分实现)

- ✅ 01-input-diagnosis.md 完整
- ⚠️ 02-17 为框架版本

### Quality Gates (简化实现)

- ✅ 5 个 gates 核心逻辑完整
- ⚠️ 辅助方法为简化实现（需要真实代码解析）

### Traceability (简化实现)

- ✅ TraceabilityGenerator 核心逻辑完整
- ⚠️ 字段级追溯仅实现 IA
- ⚠️ Inference detection 为关键字匹配

---

## Next Steps (P2)

1. **Runtime Integration**
   - 实现 PipelineExecutor 集成 quality gates
   - 实现 blocked/fallback_safe 处理
   - 实现 traceability 自动生成

2. **Prompts 完善**
   - 补充 02-17 prompts 完整内容
   - 添加更多示例

3. **Quality Gates 完善**
   - 实现真实的代码解析
   - 完善 traceability validation

4. **端到端测试**
   - 测试完整的 PRD → 推理资产 → 代码流程
   - 测试质量门阻塞场景
   - 测试 fallback_safe 降级场景

---

## Version History

- **v1.0.0** (2026-06-09 P1): 集成指南初版
