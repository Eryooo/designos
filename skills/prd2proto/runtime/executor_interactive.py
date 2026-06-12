"""
Pipeline Executor v2 - Interactive PRD Supplementation

支持交互式 PRD 补全的 pipeline 执行器
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

# 加载模块
gates = load_module_from_file('gates', PROJECT_ROOT / 'kernel/quality-gates/gates.py')
tracer = load_module_from_file('tracer', PROJECT_ROOT / 'kernel/traceability/tracer.py')
interactive = load_module_from_file('interactive', PROJECT_ROOT / 'skills/prd2proto/runtime/interactive.py')

QualityGateExecutor = gates.QualityGateExecutor
QualityGateBlocked = gates.QualityGateBlocked
GateStatus = gates.GateStatus
TraceabilityGenerator = tracer.TraceabilityGenerator

GAP_QUESTIONS = interactive.GAP_QUESTIONS
detect_product_type = interactive.detect_product_type
generate_prd_from_template = interactive.generate_prd_from_template
format_prd_summary = interactive.format_prd_summary
convert_template_to_prd_content = interactive.convert_template_to_prd_content


@dataclass
class StageResult:
    """Stage 执行结果"""
    stage_id: str
    status: str
    output: Dict
    gate_results: List[Dict]
    warnings: List[Dict]


class InteractivePipelineExecutor:
    """支持交互的 Pipeline 执行器"""

    def __init__(self, pipeline_config_path: str, interactive: bool = True):
        """
        初始化

        Args:
            pipeline_config_path: pipeline-v2.yaml 路径
            interactive: 是否启用交互模式
        """
        self.config_path = Path(pipeline_config_path)
        self.config = self._load_config()
        self.gate_executor = QualityGateExecutor()
        self.tracer = TraceabilityGenerator()
        self.interactive = interactive
        self.context = {
            'mode': 'pm',
            'fidelity': 'medium',
            'reasoning_assets': {},
            'warnings': [],
            'current_stage': None,
            'supplemented': {}  # 补充的信息
        }

    def _load_config(self) -> Dict:
        """加载 pipeline 配置"""
        with open(self.config_path) as f:
            return yaml.safe_load(f)

    def execute(self, inputs: Dict) -> Dict:
        """
        执行完整 pipeline（支持交互）

        Args:
            inputs: 输入参数

        Returns:
            执行结果
        """
        print(f"🚀 Starting pipeline: {self.config['name']}")
        print(f"   Mode: {self.context['mode']}, Interactive: {self.interactive}")

        try:
            # Stage 1: Input Diagnosis
            req_inventory = self._execute_input_diagnosis(inputs)

            completeness = req_inventory['completeness_assessment']['overall_score']

            # 根据质量决定处理方式
            if completeness < 0.3:
                # 低质量：交互补充或升维
                return self._handle_low_quality(req_inventory, inputs)

            elif completeness < 0.7:
                # 中等质量：提示但允许继续
                return self._handle_medium_quality(req_inventory, inputs)

            else:
                # 高质量：直接执行
                return self._continue_pipeline(req_inventory, inputs)

        except Exception as e:
            print(f"\n❌ Pipeline error: {e}")
            import traceback
            traceback.print_exc()
            return {
                'status': 'error',
                'error': str(e)
            }

    def _execute_input_diagnosis(self, inputs: Dict) -> Dict:
        """执行 input-diagnosis stage"""
        print(f"\n📍 Stage: input-diagnosis")

        # 模拟执行（实际应调用 LLM）
        output = self._mock_input_diagnosis(inputs)

        # 执行质量门
        try:
            result = self.gate_executor.execute('gap_transparency_gate', requirement_inventory=output)
            print(f"   🔍 Quality Gate: gap_transparency_gate - {result.status.value}")
        except QualityGateBlocked as e:
            print(f"   ⚠️  Quality Gate blocked: {e.result.message}")

        return output

    def _handle_low_quality(self, req_inventory: Dict, inputs: Dict) -> Dict:
        """处理低质量输入（< 0.3）"""
        print("\n" + "="*60)
        print("🔍 输入诊断结果：")
        print(f"   - 完整性评分：{req_inventory['completeness_assessment']['overall_score']:.2f}（低）")
        print(f"   - 缺失关键信息：")

        for gap in req_inventory['gaps']:
            if gap.get('impact') == 'critical':
                print(f"     ✗ {gap['description']}")

        if not self.interactive:
            # 非交互模式：直接进入 fallback_safe
            print("\n⚠️  非交互模式，自动进入低保真模式")
            return self._fallback_safe_mode(req_inventory, inputs)

        # 交互模式：提供选项
        print("\n💡 我可以帮你补充 PRD，或者基于常见场景生成完整版 PRD。")
        print("\n选项：")
        print("  A. 我来补充（对话模式，逐步提问）")
        print("  B. 帮我生成常见版本（基于行业最佳实践）")
        print("  C. 直接生成低保真原型（大量推断）")

        choice = self._ask_user("\n选择 (A/B/C): ")

        if choice.upper() == 'A':
            return self._interactive_supplement(req_inventory, inputs)
        elif choice.upper() == 'B':
            return self._upgrade_prd(req_inventory, inputs)
        else:
            return self._fallback_safe_mode(req_inventory, inputs)

    def _handle_medium_quality(self, req_inventory: Dict, inputs: Dict) -> Dict:
        """处理中等质量输入（0.3-0.7）"""
        print("\n" + "="*60)
        print("⚠️  输入质量中等")
        print(f"   - 完整性评分：{req_inventory['completeness_assessment']['overall_score']:.2f}")

        if req_inventory['gaps']:
            print("   - 建议补充以下信息以提升质量：")
            for gap in req_inventory['gaps'][:3]:  # 只显示前3个
                print(f"     • {gap['description']}")

        if not self.interactive:
            print("\n→ 继续执行（中等保真）")
            return self._continue_pipeline(req_inventory, inputs)

        choice = self._ask_user("\n继续吗？(y/n/补充): ")

        if choice.lower() == 'n':
            return {'status': 'cancelled', 'message': '用户取消执行'}
        elif choice == '补充':
            return self._interactive_supplement(req_inventory, inputs)
        else:
            return self._continue_pipeline(req_inventory, inputs)

    def _interactive_supplement(self, req_inventory: Dict, inputs: Dict) -> Dict:
        """交互式补充 PRD"""
        print("\n" + "="*60)
        print("📝 开始补充 PRD")
        print("="*60)

        supplemented = {}

        # 逐个询问缺失的关键信息
        for gap in req_inventory['gaps']:
            if gap.get('impact') != 'critical':
                continue

            category = gap.get('category', 'unknown')
            if category in GAP_QUESTIONS:
                answer = self._ask_gap(category)
                if answer:
                    supplemented[category] = answer

        # 更新输入并重新诊断
        inputs['supplemented'] = supplemented
        inputs['prd_content'] = self._build_supplemented_prd(inputs['prd_content'], supplemented)

        print("\n✅ PRD 补充完成，重新诊断...")
        req_inventory = self._execute_input_diagnosis(inputs)

        new_score = req_inventory['completeness_assessment']['overall_score']
        print(f"\n📊 新的完整性评分：{new_score:.2f}")

        if new_score >= 0.7:
            print("   ✅ 达到高质量标准，继续生成高保真原型")
        elif new_score >= 0.3:
            print("   ⚠️  仍为中等质量，继续生成中保真原型")
        else:
            print("   ⚠️  质量未达标，进入低保真模式")

        return self._continue_pipeline(req_inventory, inputs)

    def _upgrade_prd(self, req_inventory: Dict, inputs: Dict) -> Dict:
        """升维生成完整 PRD"""
        print("\n" + "="*60)
        print("💡 基于你的需求生成完整 PRD...")
        print("="*60)

        # 检测产品类型
        product_type = detect_product_type(inputs['prd_content'])
        print(f"\n检测到产品类型：{product_type}")

        # 生成 PRD
        upgraded_prd = generate_prd_from_template(product_type, inputs['prd_content'])

        # 显示摘要
        print("\n" + format_prd_summary(upgraded_prd))

        if not self.interactive:
            # 非交互模式：直接使用
            inputs['prd_content'] = convert_template_to_prd_content(upgraded_prd)
            req_inventory = self._execute_input_diagnosis(inputs)
            return self._continue_pipeline(req_inventory, inputs)

        choice = self._ask_user("\n这个方向对吗？(y/n/查看详情): ")

        if choice.lower() == 'y':
            inputs['prd_content'] = convert_template_to_prd_content(upgraded_prd)
            req_inventory = self._execute_input_diagnosis(inputs)
            return self._continue_pipeline(req_inventory, inputs)
        elif choice.lower() == 'n':
            return self._interactive_supplement(req_inventory, inputs)
        else:
            print("\n【完整 PRD】")
            print(convert_template_to_prd_content(upgraded_prd))
            return self._upgrade_prd(req_inventory, inputs)

    def _fallback_safe_mode(self, req_inventory: Dict, inputs: Dict) -> Dict:
        """进入低保真模式"""
        print("\n" + "="*60)
        print("⚠️  进入 Fallback Safe 模式（低保真）")
        print("="*60)

        self.context['mode'] = 'pm'
        self.context['fidelity'] = 'low'

        # 计算推断占比
        inferred_count = len(req_inventory.get('assumptions', []))
        total_info = len(req_inventory.get('functional_requirements', [])) + inferred_count
        inferred_ratio = inferred_count / total_info if total_info > 0 else 0.6

        print(f"\n已进入低保真模式：")
        print(f"   - 保真度：低（线框图级别）")
        print(f"   - 推断内容：~{inferred_ratio:.0%}")
        print(f"   - 用途：概念验证，不可直接使用")

        if req_inventory.get('assumptions'):
            print(f"\n推断的假设：")
            for assumption in req_inventory['assumptions'][:3]:
                print(f"   • {assumption.get('description', '')}")

        print(f"\n⚠️  这些假设可能与实际需求不符，建议补充 PRD 后重新生成")

        if self.interactive:
            choice = self._ask_user("\n继续吗？(yes/no): ")
            if choice.lower() != 'yes':
                return {'status': 'cancelled', 'message': '用户取消低保真模式'}

        return self._continue_pipeline(req_inventory, inputs)

    def _continue_pipeline(self, req_inventory: Dict, inputs: Dict) -> Dict:
        """继续执行 pipeline"""
        print(f"\n{'='*60}")
        print(f"→ 继续执行 pipeline")
        print(f"   Mode: {self.context['mode']}, Fidelity: {self.context['fidelity']}")
        print(f"{'='*60}")

        # 保存 requirement_inventory
        self.context['reasoning_assets']['requirement_inventory'] = req_inventory

        # 执行其余 stages（简化：跳过 framework stages）
        for stage in self.config['stages'][1:]:  # 跳过 input-diagnosis
            if stage.get('status') == 'framework':
                continue

            print(f"\n📍 Stage: {stage['id']}")
            print(f"   ⚠️  Skipped (not implemented)")

        print(f"\n✅ Pipeline completed (mock)")

        return {
            'status': 'success',
            'mode': self.context['mode'],
            'fidelity': self.context['fidelity'],
            'reasoning_assets': self.context['reasoning_assets'],
            'warnings': self.context['warnings']
        }

    def _ask_user(self, prompt: str) -> str:
        """询问用户"""
        try:
            return input(prompt).strip()
        except (EOFError, KeyboardInterrupt):
            return ''

    def _ask_gap(self, category: str) -> str:
        """询问特定类别的 gap"""
        question_data = GAP_QUESTIONS.get(category, {})

        print(f"\n{question_data.get('question', '❓')}")

        if question_data.get('examples'):
            print("\n常见参考：")
            for example in question_data['examples']:
                print(f"   • {example}")

        answer = self._ask_user(f"\n{question_data.get('prompt', '请输入：')}")
        return answer

    def _build_supplemented_prd(self, original_content: str, supplemented: Dict) -> str:
        """构建补充后的 PRD"""
        lines = [original_content, "\n\n## 补充信息\n"]

        if 'business_goals' in supplemented:
            lines.append(f"\n### 业务目标\n{supplemented['business_goals']}")

        if 'target_users' in supplemented:
            lines.append(f"\n### 目标用户\n{supplemented['target_users']}")

        if 'core_features' in supplemented:
            lines.append(f"\n### 核心功能\n{supplemented['core_features']}")

        return "\n".join(lines)

    def _mock_input_diagnosis(self, inputs: Dict) -> Dict:
        """模拟 input-diagnosis 输出"""
        content = inputs.get('prd_content', '')

        # 简单启发式评估
        has_goals = '目标' in content or 'goal' in content.lower()
        has_users = '用户' in content or 'user' in content.lower()
        has_features = '功能' in content or 'feature' in content.lower()

        score_parts = []
        if has_goals:
            score_parts.append(0.3)
        if has_users:
            score_parts.append(0.3)
        if has_features:
            score_parts.append(0.4)

        overall_score = sum(score_parts) if score_parts else 0.2

        # 识别 gaps
        gaps = []
        if not has_goals:
            gaps.append({
                'gap_id': 'GAP-001',
                'category': 'business_goals',
                'description': '缺少业务目标',
                'impact': 'critical'
            })
        if not has_users:
            gaps.append({
                'gap_id': 'GAP-002',
                'category': 'target_users',
                'description': '缺少目标用户定义',
                'impact': 'critical'
            })
        if not has_features:
            gaps.append({
                'gap_id': 'GAP-003',
                'category': 'core_features',
                'description': '缺少核心功能列表',
                'impact': 'critical'
            })

        return {
            'artifact_id': 'req-inv-001',
            'artifact_type': 'requirement_inventory',
            'completeness_assessment': {
                'overall_score': overall_score,
                'dimensions': {
                    'business_goals_clarity': 0.3 if has_goals else 0.0,
                    'user_definition_clarity': 0.3 if has_users else 0.0,
                    'functional_requirements_completeness': 0.4 if has_features else 0.0
                }
            },
            'gaps': gaps,
            'readiness_decision': {
                'decision': 'proceed' if overall_score >= 0.3 else 'blocked',
                'rationale': f'Completeness: {overall_score:.2f}'
            },
            'functional_requirements': [],
            'assumptions': [
                {'description': f'假设基于{len(content)}字符的输入推断'}
            ],
            'confidence': overall_score,
            'warnings': [],
            'inferred_fields': [],
            'traceability': {}
        }


def main():
    """测试交互式 executor"""
    import argparse

    parser = argparse.ArgumentParser(description='Interactive prd2proto pipeline')
    parser.add_argument('--pipeline', default='skills/prd2proto/pipeline-v2.yaml')
    parser.add_argument('--prd', help='PRD content or file')
    parser.add_argument('--no-interactive', action='store_true', help='Disable interactive mode')

    args = parser.parse_args()

    # 准备输入
    if args.prd:
        prd_content = args.prd
    else:
        prd_content = input("请输入 PRD 内容（或输入文件路径）：").strip()

    # 创建 executor
    executor = InteractivePipelineExecutor(
        args.pipeline,
        interactive=not args.no_interactive
    )

    # 执行
    result = executor.execute({'prd_content': prd_content})

    # 输出结果
    print(f"\n{'='*60}")
    print(f"Pipeline Result: {result['status']}")
    print(f"{'='*60}")


if __name__ == '__main__':
    main()
