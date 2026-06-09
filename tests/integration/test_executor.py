"""
测试 PipelineExecutor 的质量门阻塞场景
"""

import sys
from pathlib import Path

# 添加项目根目录
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

from skills.prd2proto.runtime.executor import PipelineExecutor


def test_quality_gate_blocks():
    """测试质量门阻塞低质量输入"""
    print("=" * 60)
    print("测试场景：低质量 PRD 应该被阻塞")
    print("=" * 60)

    # 创建 executor
    executor = PipelineExecutor('skills/prd2proto/pipeline-v2.yaml')

    # 修改 mock 输出为低质量
    original_mock = executor._mock_stage_output

    def mock_low_quality(stage, inputs):
        if stage['id'] == 'input-diagnosis':
            return {
                'artifact_id': 'req-inv-001',
                'artifact_type': 'requirement_inventory',
                'completeness_assessment': {
                    'overall_score': 0.25  # 低于 0.3 阈值
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

    # 执行
    result = executor.execute({'prd_content': 'low quality PRD'})

    # 验证结果
    print("\n" + "=" * 60)
    print(f"测试结果: {result['status']}")

    if result['status'] == 'blocked':
        print("✅ 测试通过：质量门成功阻塞低质量输入")
        print(f"   阻塞位置: {result['blocked_at']}")
        print(f"   阻塞原因: {result['blocker_report'].get('message', '')}")
    else:
        print("❌ 测试失败：质量门未阻塞低质量输入")

    print("=" * 60)


if __name__ == '__main__':
    test_quality_gate_blocks()
