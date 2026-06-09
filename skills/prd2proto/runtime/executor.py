"""
Pipeline Executor - Runtime Integration

集成 quality gates 和 traceability 的 pipeline 执行器。

简化版本：直接导入文件而不使用 Python 模块导入。
"""

import sys
from pathlib import Path
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
import yaml
import json
import importlib.util

# 动态加载模块
PROJECT_ROOT = Path(__file__).parent.parent.parent.parent

def load_module_from_file(module_name: str, file_path: Path):
    """从文件动态加载模块"""
    spec = importlib.util.spec_from_file_location(module_name, file_path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = module
    spec.loader.exec_module(module)
    return module

# 加载 gates 和 tracer
gates = load_module_from_file('gates', PROJECT_ROOT / 'kernel/quality-gates/gates.py')
tracer = load_module_from_file('tracer', PROJECT_ROOT / 'kernel/traceability/tracer.py')

QualityGateExecutor = gates.QualityGateExecutor
QualityGateBlocked = gates.QualityGateBlocked
GateStatus = gates.GateStatus
TraceabilityGenerator = tracer.TraceabilityGenerator


@dataclass
class StageResult:
    """Stage 执行结果"""
    stage_id: str
    status: str  # success, blocked, warning
    output: Dict
    gate_results: List[Dict]
    warnings: List[Dict]


class PipelineExecutor:
    """Pipeline 执行器"""

    def __init__(self, pipeline_config_path: str):
        """
        初始化 Pipeline 执行器

        Args:
            pipeline_config_path: pipeline-v2.yaml 路径
        """
        self.config_path = Path(pipeline_config_path)
        self.config = self._load_config()
        self.gate_executor = QualityGateExecutor()
        self.tracer = TraceabilityGenerator()
        self.context = {
            'mode': 'pm',
            'fidelity': 'medium',
            'reasoning_assets': {},
            'warnings': [],
            'current_stage': None
        }

    def _load_config(self) -> Dict:
        """加载 pipeline 配置"""
        with open(self.config_path) as f:
            return yaml.safe_load(f)

    def execute(self, inputs: Dict) -> Dict:
        """
        执行完整 pipeline

        Args:
            inputs: 输入参数（prd_content, etc.）

        Returns:
            执行结果
        """
        print(f"🚀 Starting pipeline: {self.config['name']}")
        print(f"   Mode: {self.context['mode']}, Fidelity: {self.context['fidelity']}")

        stage_results = []

        try:
            for stage in self.config['stages']:
                stage_id = stage['id']
                print(f"\n📍 Stage: {stage_id}")

                # 检查 status（跳过 framework 的 stage）
                if stage.get('status') == 'framework':
                    print(f"   ⚠️  Skipped (framework - not implemented yet)")
                    continue

                # 执行 stage
                result = self._execute_stage(stage, inputs)
                stage_results.append(result)

                # 检查是否 blocked
                if result.status == 'blocked':
                    print(f"   ❌ Blocked at {stage_id}")
                    return {
                        'status': 'blocked',
                        'blocked_at': stage_id,
                        'blocker_report': result.output,
                        'stage_results': stage_results
                    }

                # 检查是否需要 fallback_safe
                if result.status == 'fallback_safe':
                    print(f"   ⚠️  Fallback safe at {stage_id}")
                    self._handle_fallback_safe()

            # 生成最终产物
            print(f"\n✅ Pipeline completed")
            return {
                'status': 'success',
                'reasoning_assets': self.context['reasoning_assets'],
                'warnings': self.context['warnings'],
                'stage_results': stage_results
            }

        except Exception as e:
            print(f"\n❌ Pipeline error: {e}")
            import traceback
            traceback.print_exc()
            return {
                'status': 'error',
                'error': str(e),
                'stage_results': stage_results
            }

    def _execute_stage(self, stage: Dict, inputs: Dict) -> StageResult:
        """
        执行单个 stage

        Args:
            stage: stage 配置
            inputs: 输入

        Returns:
            StageResult
        """
        stage_id = stage['id']
        self.context['current_stage'] = stage_id

        # 模拟 stage 输出（实际应该调用 LLM）
        output = self._mock_stage_output(stage, inputs)

        # 执行质量门
        gate_results = []
        warnings = []

        if 'quality_gates' in stage:
            for gate_id in stage['quality_gates']:
                try:
                    print(f"   🔍 Quality Gate: {gate_id}")

                    gate_kwargs = self._prepare_gate_kwargs(gate_id, output)
                    result = self.gate_executor.execute(gate_id, **gate_kwargs)

                    gate_results.append(result.to_dict())

                    if result.status == GateStatus.WARNING:
                        print(f"      ⚠️  Warning: {result.message}")
                        warnings.append({
                            'gate_id': gate_id,
                            'message': result.message
                        })

                except QualityGateBlocked as e:
                    print(f"      ❌ Blocked: {e.result.message}")
                    return StageResult(
                        stage_id=stage_id,
                        status='blocked',
                        output={
                            'gate_id': gate_id,
                            'message': e.result.message,
                            'issues': e.result.issues or e.result.errors,
                            'recommendation': e.result.recommendation
                        },
                        gate_results=gate_results,
                        warnings=warnings
                    )

        # 保存到 reasoning_assets
        if 'outputs' in stage:
            for output_name in stage['outputs']:
                self.context['reasoning_assets'][output_name] = output

        print(f"   ✅ Completed")

        return StageResult(
            stage_id=stage_id,
            status='success',
            output=output,
            gate_results=gate_results,
            warnings=warnings
        )

    def _mock_stage_output(self, stage: Dict, inputs: Dict) -> Dict:
        """模拟 stage 输出"""
        stage_id = stage['id']

        # 为测试提供 mock 数据
        if stage_id == 'input-diagnosis':
            return {
                'artifact_id': 'req-inv-001',
                'artifact_type': 'requirement_inventory',
                'completeness_assessment': {
                    'overall_score': 0.85
                },
                'gaps': [],
                'readiness_decision': {
                    'decision': 'proceed',
                    'rationale': 'Input quality is high'
                },
                'confidence': 0.9,
                'warnings': [],
                'inferred_fields': [],
                'assumptions': [],
                'traceability': {}
            }

        # 其他 stages 返回基础结构
        return {
            'artifact_id': f"{stage_id}-001",
            'artifact_type': stage_id.replace('-', '_'),
            'confidence': 0.8,
            'gaps': [],
            'inferred_fields': [],
            'warnings': [],
            'traceability': {}
        }

    def _prepare_gate_kwargs(self, gate_id: str, output: Dict) -> Dict:
        """准备质量门参数"""
        if gate_id == 'gap_transparency_gate':
            return {'requirement_inventory': output}

        elif gate_id == 'schema_gate':
            schema = {'type': 'object', 'properties': {}}
            return {'artifact': output, 'schema': schema}

        elif gate_id == 'inference_limit_gate':
            return {'artifact': output}

        elif gate_id == 'traceability_gate':
            return {
                'traceability_map': output.get('traceability', {}),
                'reasoning_assets': self.context['reasoning_assets'],
                'output_artifact': output
            }

        elif gate_id == 'code_constraint_gate':
            return {
                'generated_code': output,
                'information_architecture': self.context['reasoning_assets'].get('information_architecture', {}),
                'component_strategy': self.context['reasoning_assets'].get('component_strategy', {}),
                'state_matrix': self.context['reasoning_assets'].get('state_matrix')
            }

        return {}

    def _handle_fallback_safe(self):
        """处理 fallback_safe 降级"""
        print(f"\n   ⚠️  Entering Fallback Safe Mode")

        self.context['mode'] = 'pm'
        self.context['fidelity'] = 'low'

        print(f"      - Mode: {self.context['mode']}")
        print(f"      - Fidelity: {self.context['fidelity']}")

        self.context['warnings'].append({
            'warning_id': 'WARN-FALLBACK',
            'severity': 'high',
            'message': '因输入质量不足，已降级到低保真模式（PM 模式）'
        })


def main():
    """测试 PipelineExecutor"""
    import argparse

    parser = argparse.ArgumentParser(description='Run prd2proto pipeline v2')
    parser.add_argument('--pipeline', default='skills/prd2proto/pipeline-v2.yaml')
    parser.add_argument('--mode', default='pm', choices=['pm', 'designer-spec'])

    args = parser.parse_args()

    # 创建 executor
    executor = PipelineExecutor(args.pipeline)

    # 准备输入
    inputs = {
        'prd_file': 'test-prd.md',
        'prd_content': '# Test PRD\n\nA simple CRM system.',
        'mode': args.mode
    }

    # 执行 pipeline
    result = executor.execute(inputs)

    # 输出结果
    print(f"\n{'='*60}")
    print(f"Pipeline Result: {result['status']}")

    if result['status'] == 'blocked':
        print(f"\nBlocked at: {result['blocked_at']}")
        print(f"Blocker: {result['blocker_report']}")

    elif result['status'] == 'success':
        print(f"\nReasoning Assets: {len(result['reasoning_assets'])} generated")
        print(f"Warnings: {len(result['warnings'])}")

    print(f"{'='*60}")


if __name__ == '__main__':
    main()
