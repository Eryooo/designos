"""
Quality Gates Implementation

DesignOS 质量门实现，确保设计推理流程符合资深设计师标准。
"""

from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from enum import Enum
import jsonschema


class GateStatus(Enum):
    """质量门状态"""
    PASS = "pass"
    WARNING = "warning"
    BLOCKED = "blocked"


@dataclass
class GateResult:
    """质量门结果"""
    gate_id: str
    status: GateStatus
    message: str = ""
    errors: Optional[List[Dict]] = None
    issues: Optional[List[Dict]] = None
    recommendation: str = ""
    metadata: Optional[Dict] = None

    def to_dict(self) -> Dict:
        return {
            "gate_id": self.gate_id,
            "status": self.status.value,
            "message": self.message,
            "errors": self.errors or [],
            "issues": self.issues or [],
            "recommendation": self.recommendation,
            "metadata": self.metadata or {}
        }


class QualityGateBlocked(Exception):
    """质量门阻塞异常"""
    def __init__(self, result: GateResult):
        self.result = result
        super().__init__(f"Quality gate {result.gate_id} blocked: {result.message}")


# ============================================================================
# Gate 1: Schema Gate
# ============================================================================

def schema_gate(artifact: Dict, schema: Dict) -> GateResult:
    """
    验证 artifact 是否符合 schema

    Args:
        artifact: 要验证的 artifact
        schema: JSON Schema

    Returns:
        GateResult
    """
    validator = jsonschema.Draft7Validator(schema)
    errors = list(validator.iter_errors(artifact))

    if not errors:
        return GateResult(
            gate_id="schema_gate",
            status=GateStatus.PASS,
            message="Artifact 符合 schema 要求"
        )

    # 区分 critical 和 non-critical 错误
    formatted_errors = []
    critical_count = 0

    for error in errors:
        field_path = ".".join(str(p) for p in error.path)
        is_critical = _is_critical_field(error, schema)

        formatted_errors.append({
            "field": field_path,
            "message": error.message,
            "validator": error.validator,
            "critical": is_critical
        })

        if is_critical:
            critical_count += 1

    if critical_count > 0:
        return GateResult(
            gate_id="schema_gate",
            status=GateStatus.BLOCKED,
            message=f"发现 {critical_count} 个 critical schema 错误",
            errors=formatted_errors,
            recommendation="修复以下必需字段后重试"
        )
    else:
        return GateResult(
            gate_id="schema_gate",
            status=GateStatus.WARNING,
            message=f"发现 {len(errors)} 个 non-critical schema 警告",
            errors=formatted_errors,
            recommendation="建议补充以下可选字段以提升质量"
        )


def _is_critical_field(error: jsonschema.ValidationError, schema: Dict) -> bool:
    """判断字段是否为 critical"""
    # 如果是 required 验证失败，则为 critical
    if error.validator == 'required':
        return True

    # 如果字段在 schema 的 required 列表中，则为 critical
    field_path = list(error.path)
    if field_path:
        current_schema = schema
        for path_part in field_path[:-1]:
            if isinstance(path_part, str) and 'properties' in current_schema:
                current_schema = current_schema['properties'].get(path_part, {})

        if 'required' in current_schema:
            last_field = field_path[-1]
            return last_field in current_schema.get('required', [])

    return False


# ============================================================================
# Gate 2: Traceability Gate
# ============================================================================

def traceability_gate(
    traceability_map: Dict,
    reasoning_assets: Dict,
    output_artifact: Optional[Dict] = None
) -> GateResult:
    """
    验证可追溯性完整性

    Args:
        traceability_map: 可追溯性地图
        reasoning_assets: 所有推理资产
        output_artifact: 最终产物（可选）

    Returns:
        GateResult
    """
    issues = []

    # 类型守卫（2026-06-10 Phase 3.5）：
    # LLM 输出的 traceability 字段可能是 str/None 而非 dict，
    # gate 必须容错，否则 .get() 会抛 'str' object has no attribute 'get'。
    if not isinstance(traceability_map, dict):
        traceability_map = {}
    if not isinstance(reasoning_assets, dict):
        reasoning_assets = {}
    if output_artifact is not None and not isinstance(output_artifact, dict):
        output_artifact = None

    # 检查 1: 如果是 IA，验证所有页面是否可追溯到 user_task
    if output_artifact and output_artifact.get('artifact_type') == 'information_architecture':
        user_task_map = reasoning_assets.get('user_task_map', {})
        for page in output_artifact.get('pages', []):
            if not isinstance(page, dict):
                continue
            if not _has_task_mapping(page, user_task_map):
                issues.append({
                    "type": "unauthorized_page",
                    "severity": "critical",
                    "page_id": page.get('page_id'),
                    "page_name": page.get('page_name'),
                    "message": f"页面 '{page.get('page_name')}' 无法追溯到任何 user_task"
                })

    # 检查 2: 关键决策是否有追溯依据
    for decision in traceability_map.get('decision_trace', []):
        if not isinstance(decision, dict):
            continue
        based_on = decision.get('based_on', [])
        if not based_on:
            issues.append({
                "type": "decision_without_basis",
                "severity": "high",
                "decision_id": decision.get('decision_id'),
                "decision_point": decision.get('decision_point'),
                "message": f"决策 '{decision.get('decision_point')}' 缺少追溯依据"
            })

    # 检查 3: 输入覆盖率
    #
    # 设计分级（2026-06-10 Phase 3.5 修复）：
    # - 中间 stage（如 user-task-modeling）不强制产出完整 traceability_map，
    #   其追溯由最终 Stage 16 (traceability-generation) 统一生成。
    # - 因此：traceability_map 为空 = "尚未生成追溯地图"，降级为 warning（不阻塞）。
    # - 只有当 traceability_map 已存在 coverage_analysis 但覆盖率确实低时，
    #   才视为真问题并 block。
    has_traceability = bool(traceability_map) and 'coverage_analysis' in traceability_map
    coverage_analysis = traceability_map.get('coverage_analysis', {})
    input_coverage = coverage_analysis.get('input_coverage', 0)

    if not has_traceability:
        # 中间 stage 未生成追溯地图：warning 提示，不阻塞
        issues.append({
            "type": "traceability_not_generated",
            "severity": "low",
            "message": (
                "本 stage 未产出 coverage_analysis（中间 stage 正常现象）；"
                "完整追溯将由 Stage 16 traceability-generation 统一生成"
            )
        })
    elif input_coverage < 0.5:
        issues.append({
            "type": "low_input_coverage",
            "severity": "critical",
            "coverage": input_coverage,
            "message": f"输入覆盖率过低 ({input_coverage:.0%})"
        })
    elif input_coverage < 0.7:
        issues.append({
            "type": "medium_input_coverage",
            "severity": "medium",
            "coverage": input_coverage,
            "message": f"输入覆盖率中等 ({input_coverage:.0%})，建议提升"
        })

    # 检查 4: Scope creep 是否说明
    scope_creep = coverage_analysis.get('scope_creep_items', [])
    unapproved_creep = [item for item in scope_creep if item.get('approval_status') != 'approved']

    if unapproved_creep:
        issues.append({
            "type": "unapproved_scope_creep",
            "severity": "high",
            "items": unapproved_creep,
            "message": f"发现 {len(unapproved_creep)} 个未批准的范围扩展"
        })

    # 判断结果
    if not issues:
        return GateResult(
            gate_id="traceability_gate",
            status=GateStatus.PASS,
            message="可追溯性检查通过"
        )

    critical_issues = [i for i in issues if i['severity'] == 'critical']

    if critical_issues:
        return GateResult(
            gate_id="traceability_gate",
            status=GateStatus.BLOCKED,
            message=f"发现 {len(critical_issues)} 个 critical 追溯性问题",
            issues=issues,
            recommendation="必须修复以下追溯性问题后才能继续"
        )
    else:
        return GateResult(
            gate_id="traceability_gate",
            status=GateStatus.WARNING,
            message=f"发现 {len(issues)} 个追溯性警告",
            issues=issues,
            recommendation="建议补充追溯依据以提升质量"
        )


def _has_task_mapping(page: Dict, user_task_map: Dict) -> bool:
    """检查页面是否可追溯到 user_task"""
    related_tasks = page.get('related_tasks', [])
    if not related_tasks:
        return False

    all_task_ids = set()
    for task_list in ['primary_tasks', 'secondary_tasks', 'edge_tasks']:
        tasks = user_task_map.get(task_list, [])
        all_task_ids.update(task.get('task_id') for task in tasks)

    return any(task_id in all_task_ids for task_id in related_tasks)


# ============================================================================
# Gate 3: Gap Transparency Gate
# ============================================================================

def gap_transparency_gate(requirement_inventory: Dict) -> GateResult:
    """
    验证 gap 透明度，确保输入缺失被显式记录

    Args:
        requirement_inventory: 需求清单

    Returns:
        GateResult
    """
    gaps = requirement_inventory.get('gaps', [])
    critical_gaps = [g for g in gaps if g.get('impact') == 'critical']

    decision = requirement_inventory.get('readiness_decision', {}).get('decision')
    overall_score = requirement_inventory.get('completeness_assessment', {}).get('overall_score', 0)

    # 检查 1: critical gaps + proceed 违规
    if critical_gaps and decision == 'proceed':
        return GateResult(
            gate_id="gap_transparency_gate",
            status=GateStatus.BLOCKED,
            message=f"存在 {len(critical_gaps)} 个 critical gaps 但决策为 proceed",
            issues=[{
                "type": "critical_gap_ignored",
                "gaps": critical_gaps,
                "message": "违反核心原则 4（输入缺失不得静默补全）"
            }],
            recommendation="必须进入 blocked 或 fallback_safe 状态"
        )

    # 检查 2: 完整性评分过低
    if overall_score < 0.3:
        return GateResult(
            gate_id="gap_transparency_gate",
            status=GateStatus.BLOCKED,
            message=f"输入完整性过低 ({overall_score:.0%})",
            issues=[{
                "type": "low_completeness",
                "score": overall_score,
                "message": "输入质量不足以生成合格产物"
            }],
            recommendation="必须补充输入或停止执行"
        )

    # 检查 3: 完整性中等但决策为 proceed
    if overall_score < 0.5 and decision == 'proceed':
        return GateResult(
            gate_id="gap_transparency_gate",
            status=GateStatus.WARNING,
            message=f"输入完整性中等 ({overall_score:.0%})，建议降级",
            issues=[{
                "type": "medium_completeness",
                "score": overall_score,
                "message": "建议降级到 fallback_safe 模式"
            }],
            recommendation="当前模式可能产生低质量产物，建议切换到低保真模式"
        )

    return GateResult(
        gate_id="gap_transparency_gate",
        status=GateStatus.PASS,
        message="Gap 透明度检查通过",
        metadata={
            "overall_score": overall_score,
            "critical_gaps": len(critical_gaps),
            "decision": decision
        }
    )


# ============================================================================
# Gate 4: Inference Limit Gate
# ============================================================================

def inference_limit_gate(
    artifact: Dict,
    threshold_warning: float = 0.3,
    threshold_blocked: float = 0.5
) -> GateResult:
    """
    验证推断内容占比，防止 AI 幻觉

    Args:
        artifact: 要检查的 artifact
        threshold_warning: 警告阈值
        threshold_blocked: 阻塞阈值

    Returns:
        GateResult
    """
    inferred_fields = artifact.get('inferred_fields', [])

    # 计算总字段数
    total_fields = _count_all_fields(artifact)
    inferred_count = len(inferred_fields)
    inferred_ratio = inferred_count / total_fields if total_fields > 0 else 0

    if inferred_ratio >= threshold_blocked:
        return GateResult(
            gate_id="inference_limit_gate",
            status=GateStatus.BLOCKED,
            message=f"推断内容占比过高 ({inferred_ratio:.0%})",
            issues=[{
                "type": "high_inference_ratio",
                "inferred_count": inferred_count,
                "total_fields": total_fields,
                "ratio": inferred_ratio,
                "message": f"{inferred_count}/{total_fields} 字段为推断"
            }],
            recommendation="输入不足，无法生成高质量产物。必须补充输入或降级到 fallback_safe",
            metadata={
                "inferred_ratio": inferred_ratio,
                "threshold_blocked": threshold_blocked
            }
        )

    if inferred_ratio >= threshold_warning:
        return GateResult(
            gate_id="inference_limit_gate",
            status=GateStatus.WARNING,
            message=f"推断内容占比较高 ({inferred_ratio:.0%})",
            issues=[{
                "type": "medium_inference_ratio",
                "inferred_count": inferred_count,
                "total_fields": total_fields,
                "ratio": inferred_ratio
            }],
            recommendation="建议标记为需人工复核",
            metadata={
                "inferred_ratio": inferred_ratio,
                "threshold_warning": threshold_warning
            }
        )

    return GateResult(
        gate_id="inference_limit_gate",
        status=GateStatus.PASS,
        message=f"推断内容占比合理 ({inferred_ratio:.0%})",
        metadata={
            "inferred_ratio": inferred_ratio
        }
    )


def _count_all_fields(obj: Any, count: int = 0) -> int:
    """递归计算对象中的所有字段数"""
    if isinstance(obj, dict):
        for key, value in obj.items():
            # 跳过元数据字段
            if key in ['artifact_id', 'artifact_type', 'created_at', 'metadata']:
                continue
            count += 1
            count = _count_all_fields(value, count)
    elif isinstance(obj, list):
        for item in obj:
            count = _count_all_fields(item, count)

    return count


# ============================================================================
# Gate 5: Code Constraint Gate
# ============================================================================

def code_constraint_gate(
    generated_code: Dict,
    information_architecture: Dict,
    component_strategy: Dict,
    state_matrix: Optional[Dict] = None
) -> GateResult:
    """
    验证生成的代码是否受设计推理资产约束

    Args:
        generated_code: 生成的代码
        information_architecture: 信息架构
        component_strategy: 组件策略
        state_matrix: 状态矩阵（可选）

    Returns:
        GateResult
    """
    issues = []

    # 检查 1: 所有生成的页面是否来自 IA
    generated_pages = _extract_pages_from_code(generated_code)
    ia_pages = {p.get('page_id') for p in information_architecture.get('pages', [])}

    unauthorized_pages = [p for p in generated_pages if p not in ia_pages]
    if unauthorized_pages:
        issues.append({
            "type": "unauthorized_page",
            "severity": "critical",
            "pages": unauthorized_pages,
            "message": f"发现 {len(unauthorized_pages)} 个未授权页面（不在 IA 中）"
        })

    # 检查 2: 所有使用的组件是否来自 component_strategy
    used_components = _extract_components_from_code(generated_code)
    allowed_components = {c.get('component_id') for c in component_strategy.get('component_inventory', [])}

    unauthorized_components = [c for c in used_components if c not in allowed_components]
    if unauthorized_components:
        issues.append({
            "type": "unauthorized_component",
            "severity": "medium",
            "components": unauthorized_components,
            "message": f"发现 {len(unauthorized_components)} 个未授权组件（不在 component_strategy 中）"
        })

    # 检查 3: 状态实现是否与 state_matrix 一致（如果提供）
    if state_matrix:
        for page_id in generated_pages:
            expected_states = _get_expected_states(page_id, state_matrix)
            actual_states = _extract_states_from_page_code(generated_code, page_id)

            missing_states = set(expected_states) - set(actual_states)
            if missing_states:
                issues.append({
                    "type": "missing_state",
                    "severity": "critical",
                    "page": page_id,
                    "missing_states": list(missing_states),
                    "message": f"页面 {page_id} 缺少状态: {', '.join(missing_states)}"
                })

    # 判断结果
    if not issues:
        return GateResult(
            gate_id="code_constraint_gate",
            status=GateStatus.PASS,
            message="代码约束检查通过"
        )

    critical_issues = [i for i in issues if i.get('severity') == 'critical']

    if critical_issues:
        return GateResult(
            gate_id="code_constraint_gate",
            status=GateStatus.BLOCKED,
            message=f"发现 {len(critical_issues)} 个 critical 代码约束违规",
            issues=issues,
            recommendation="代码生成违反约束，必须修复"
        )
    else:
        return GateResult(
            gate_id="code_constraint_gate",
            status=GateStatus.WARNING,
            message=f"发现 {len(issues)} 个代码约束警告",
            issues=issues,
            recommendation="建议补充组件定义或修正代码"
        )


def _extract_pages_from_code(generated_code: Dict) -> List[str]:
    """从生成的代码中提取页面 ID"""
    # 简化实现，实际应该解析代码结构
    pages = generated_code.get('pages', [])
    return [p.get('page_id') for p in pages if 'page_id' in p]


def _extract_components_from_code(generated_code: Dict) -> List[str]:
    """从生成的代码中提取使用的组件"""
    # 简化实现，实际应该解析代码
    components = set()
    for page in generated_code.get('pages', []):
        page_components = page.get('components_used', [])
        components.update(page_components)
    return list(components)


def _get_expected_states(page_id: str, state_matrix: Dict) -> List[str]:
    """获取页面的期望状态"""
    for page_state in state_matrix.get('page_states', []):
        if page_state.get('page_id') == page_id:
            return [s.get('state_name') for s in page_state.get('states', [])]
    return []


def _extract_states_from_page_code(generated_code: Dict, page_id: str) -> List[str]:
    """从页面代码中提取实现的状态"""
    # 简化实现，实际应该解析代码
    for page in generated_code.get('pages', []):
        if page.get('page_id') == page_id:
            return page.get('states_implemented', [])
    return []


# ============================================================================
# Quality Gate Executor
# ============================================================================

class QualityGateExecutor:
    """质量门执行器"""

    GATES = {
        'schema_gate': schema_gate,
        'traceability_gate': traceability_gate,
        'gap_transparency_gate': gap_transparency_gate,
        'inference_limit_gate': inference_limit_gate,
        'code_constraint_gate': code_constraint_gate
    }

    def __init__(self):
        self.results: List[GateResult] = []

    def execute(self, gate_id: str, **kwargs) -> GateResult:
        """执行单个质量门"""
        gate_func = self.GATES.get(gate_id)
        if not gate_func:
            raise ValueError(f"Unknown gate: {gate_id}")

        result = gate_func(**kwargs)
        self.results.append(result)

        # 根据结果决定是否阻塞
        if result.status == GateStatus.BLOCKED:
            raise QualityGateBlocked(result)

        return result

    def execute_all(self, stage: str, context: Dict) -> List[GateResult]:
        """执行某个 stage 的所有质量门"""
        stage_gates = self._get_gates_for_stage(stage)
        results = []

        for gate_id in stage_gates:
            try:
                gate_kwargs = self._prepare_gate_kwargs(gate_id, context)
                result = self.execute(gate_id, **gate_kwargs)
                results.append(result)
            except QualityGateBlocked as e:
                # 记录阻塞原因并停止执行
                results.append(e.result)
                break

        return results

    def get_summary(self) -> Dict:
        """获取质量门执行摘要"""
        return {
            "total_gates": len(self.results),
            "passed": len([r for r in self.results if r.status == GateStatus.PASS]),
            "warnings": len([r for r in self.results if r.status == GateStatus.WARNING]),
            "blocked": len([r for r in self.results if r.status == GateStatus.BLOCKED]),
            "results": [r.to_dict() for r in self.results]
        }

    def _get_gates_for_stage(self, stage: str) -> List[str]:
        """获取某个 stage 的质量门列表"""
        # 简化实现，实际应该从配置文件读取
        stage_gates_map = {
            'input-diagnosis': ['gap_transparency_gate'],
            'design-objectives': ['schema_gate', 'inference_limit_gate'],
            'user-task-modeling': ['schema_gate', 'inference_limit_gate', 'traceability_gate'],
            'information-architecture': ['schema_gate', 'traceability_gate'],
            'code-generation': ['code_constraint_gate'],
            'traceability-generation': ['schema_gate', 'traceability_gate']
        }
        return stage_gates_map.get(stage, [])

    def _prepare_gate_kwargs(self, gate_id: str, context: Dict) -> Dict:
        """准备质量门参数"""
        # 根据不同的质量门准备不同的参数
        if gate_id == 'schema_gate':
            return {
                'artifact': context.get('current_artifact'),
                'schema': context.get('current_schema')
            }
        elif gate_id == 'traceability_gate':
            return {
                'traceability_map': context.get('traceability_map'),
                'reasoning_assets': context.get('reasoning_assets'),
                'output_artifact': context.get('current_artifact')
            }
        elif gate_id == 'gap_transparency_gate':
            return {
                'requirement_inventory': context.get('requirement_inventory')
            }
        elif gate_id == 'inference_limit_gate':
            return {
                'artifact': context.get('current_artifact')
            }
        elif gate_id == 'code_constraint_gate':
            return {
                'generated_code': context.get('generated_code'),
                'information_architecture': context.get('reasoning_assets', {}).get('information_architecture'),
                'component_strategy': context.get('reasoning_assets', {}).get('component_strategy'),
                'state_matrix': context.get('reasoning_assets', {}).get('state_matrix')
            }
        return {}
