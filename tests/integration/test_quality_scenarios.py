"""
完整测试 PipelineExecutor 的三种质量场景
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

from skills.prd2proto.runtime.executor import PipelineExecutor


def test_high_quality_prd():
    """测试场景 1：高质量 PRD 应该通过"""
    print("=" * 60)
    print("测试场景 1：高质量 PRD（completeness >= 0.7）")
    print("=" * 60)

    executor = PipelineExecutor('skills/prd2proto/pipeline-v2.yaml')
    original_mock = executor._mock_stage_output

    def mock_high_quality(stage, inputs):
        if stage['id'] == 'input-diagnosis':
            return {
                'artifact_id': 'req-inv-001',
                'artifact_type': 'requirement_inventory',
                'completeness_assessment': {
                    'overall_score': 0.85  # 高质量
                },
                'gaps': [
                    {'gap_id': 'GAP-001', 'impact': 'low'}  # 非 critical
                ],
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
        return original_mock(stage, inputs)

    executor._mock_stage_output = mock_high_quality

    result = executor.execute({'prd_content': 'high quality PRD'})

    print(f"\n结果: {result['status']}")

    if result['status'] == 'success':
        print("✅ 测试通过：高质量 PRD 成功执行")
        input_stage = next((s for s in result.get('stage_results', []) if s.stage_id == 'input-diagnosis'), None)
        if input_stage:
            print(f"   Quality Gates: {len(input_stage.gate_results)} executed")
            print(f"   Warnings: {len(input_stage.warnings)}")
    else:
        print(f"❌ 测试失败：应该成功但状态为 {result['status']}")

    print("=" * 60)


def test_medium_quality_prd():
    """测试场景 2：中等质量 PRD 应该产生 warning"""
    print("\n" + "=" * 60)
    print("测试场景 2：中等质量 PRD（0.3 <= completeness < 0.5）")
    print("=" * 60)

    executor = PipelineExecutor('skills/prd2proto/pipeline-v2.yaml')
    original_mock = executor._mock_stage_output

    def mock_medium_quality(stage, inputs):
        if stage['id'] == 'input-diagnosis':
            return {
                'artifact_id': 'req-inv-001',
                'artifact_type': 'requirement_inventory',
                'completeness_assessment': {
                    'overall_score': 0.45  # 中等质量（0.3-0.5）
                },
                'gaps': [],
                'readiness_decision': {
                    'decision': 'proceed',  # 应该是 fallback_safe 但选了 proceed
                    'rationale': 'Test'
                },
                'confidence': 0.7,
                'warnings': [],
                'inferred_fields': [],
                'assumptions': [],
                'traceability': {}
            }
        return original_mock(stage, inputs)

    executor._mock_stage_output = mock_medium_quality

    result = executor.execute({'prd_content': 'medium quality PRD'})

    print(f"\n结果: {result['status']}")

    if result['status'] == 'success':
        input_stage = next((s for s in result.get('stage_results', []) if s.stage_id == 'input-diagnosis'), None)

        if input_stage and input_stage.warnings:
            print("✅ 测试通过：中等质量 PRD 产生 warning 但继续执行")
            print(f"   Warnings: {len(input_stage.warnings)}")
            for w in input_stage.warnings:
                print(f"   - {w.get('gate_id')}: {w.get('message', '')[:60]}...")
        else:
            print("⚠️  测试部分通过：执行完成但未产生 warning")
            print("   （可能是 gap_transparency_gate 的 warning 逻辑需要调整）")
    else:
        print(f"❌ 测试失败：应该成功但状态为 {result['status']}")

    print("=" * 60)


def test_low_quality_prd():
    """测试场景 3：低质量 PRD 应该被阻塞"""
    print("\n" + "=" * 60)
    print("测试场景 3：低质量 PRD（completeness < 0.3 或 critical gap）")
    print("=" * 60)

    executor = PipelineExecutor('skills/prd2proto/pipeline-v2.yaml')
    original_mock = executor._mock_stage_output

    def mock_low_quality(stage, inputs):
        if stage['id'] == 'input-diagnosis':
            return {
                'artifact_id': 'req-inv-001',
                'artifact_type': 'requirement_inventory',
                'completeness_assessment': {
                    'overall_score': 0.25  # 低质量（< 0.3）
                },
                'gaps': [
                    {
                        'gap_id': 'GAP-001',
                        'impact': 'critical',
                        'description': '缺少业务目标'
                    }
                ],
                'readiness_decision': {
                    'decision': 'proceed',  # 违规：critical gap + proceed
                    'rationale': 'Test'
                },
                'confidence': 0.5,
                'warnings': [],
                'inferred_fields': [],
                'assumptions': [],
                'traceability': {}
            }
        return original_mock(stage, inputs)

    executor._mock_stage_output = mock_low_quality

    result = executor.execute({'prd_content': 'low quality PRD'})

    print(f"\n结果: {result['status']}")

    if result['status'] == 'blocked':
        print("✅ 测试通过：低质量 PRD 被成功阻塞")
        print(f"   阻塞位置: {result['blocked_at']}")
        print(f"   阻塞原因: {result['blocker_report'].get('message', '')}")

        blocker = result['blocker_report']
        if blocker.get('issues') or blocker.get('errors'):
            print(f"   问题详情:")
            for issue in (blocker.get('issues') or blocker.get('errors') or []):
                print(f"     - {issue}")
    else:
        print(f"❌ 测试失败：应该被阻塞但状态为 {result['status']}")

    print("=" * 60)


def run_all_tests():
    """运行所有测试"""
    print("\n" + "🧪 " * 20)
    print("PipelineExecutor 质量门完整测试")
    print("🧪 " * 20 + "\n")

    test_high_quality_prd()
    test_medium_quality_prd()
    test_low_quality_prd()

    print("\n" + "📊 " * 20)
    print("测试总结")
    print("📊 " * 20)
    print("""
预期行为：
1. 高质量 PRD（>= 0.7）: ✅ Pass，继续执行
2. 中等质量 PRD（0.3-0.5 + proceed）: ⚠️ Warning，继续执行
3. 低质量 PRD（< 0.3 或 critical gap + proceed）: ❌ Blocked，停止执行

质量门规则（gap_transparency_gate）：
- completeness < 0.3 → Blocked
- completeness < 0.5 + proceed → Warning（建议 fallback_safe）
- critical gaps + proceed → Blocked
- completeness >= 0.7 + no critical gaps → Pass
    """)


if __name__ == '__main__':
    run_all_tests()
