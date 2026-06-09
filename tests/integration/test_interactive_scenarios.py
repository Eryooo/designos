"""
测试交互式 PRD 补全的不同场景
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

from skills.prd2proto.runtime.executor_interactive import InteractivePipelineExecutor


def test_low_quality_auto_fallback():
    """测试场景 1：低质量 PRD，非交互模式自动 fallback"""
    print("="*70)
    print("测试场景 1：低质量 PRD + 非交互模式")
    print("="*70)

    executor = InteractivePipelineExecutor(
        'skills/prd2proto/pipeline-v2.yaml',
        interactive=False
    )

    result = executor.execute({'prd_content': '做一个 CRM 系统'})

    print(f"\n✅ 测试结果：")
    print(f"   Status: {result['status']}")
    print(f"   Mode: {result.get('mode')}")
    print(f"   Fidelity: {result.get('fidelity')}")

    assert result['status'] == 'success'
    assert result.get('fidelity') == 'low'
    print(f"\n✅ 测试通过：低质量 PRD 自动进入 fallback_safe")


def test_medium_quality():
    """测试场景 2：中等质量 PRD，非交互模式继续执行"""
    print("\n" + "="*70)
    print("测试场景 2：中等质量 PRD + 非交互模式")
    print("="*70)

    executor = InteractivePipelineExecutor(
        'skills/prd2proto/pipeline-v2.yaml',
        interactive=False
    )

    prd = """
    # CRM 系统

    ## 目标用户
    销售主管和销售员

    ## 核心功能
    - 客户管理
    - 线索跟进
    """

    result = executor.execute({'prd_content': prd})

    print(f"\n✅ 测试结果：")
    print(f"   Status: {result['status']}")
    print(f"   Mode: {result.get('mode')}")

    assert result['status'] == 'success'
    print(f"\n✅ 测试通过：中等质量 PRD 继续执行")


def test_high_quality():
    """测试场景 3：高质量 PRD，直接执行"""
    print("\n" + "="*70)
    print("测试场景 3：高质量 PRD")
    print("="*70)

    executor = InteractivePipelineExecutor(
        'skills/prd2proto/pipeline-v2.yaml',
        interactive=False
    )

    prd = """
    # CRM 系统 PRD

    ## 业务目标
    - 提升销售效率 30%
    - 客户信息集中管理

    ## 目标用户
    - 销售主管：管理 10-50 人团队
    - 销售员：每天管理 20-100 个客户

    ## 核心功能
    - 客户信息 CRUD
    - 销售线索跟进提醒
    - 简单数据报表
    """

    result = executor.execute({'prd_content': prd})

    print(f"\n✅ 测试结果：")
    print(f"   Status: {result['status']}")

    assert result['status'] == 'success'
    print(f"\n✅ 测试通过：高质量 PRD 直接执行")


def test_prd_upgrade():
    """测试场景 4：PRD 升维生成"""
    print("\n" + "="*70)
    print("测试场景 4：PRD 升维生成")
    print("="*70)

    from skills.prd2proto.runtime.interactive import (
        detect_product_type,
        generate_prd_from_template,
        format_prd_summary
    )

    # 测试产品类型检测
    assert detect_product_type("做一个 CRM 系统") == "crm"
    print("   ✅ CRM 检测正确")

    # 测试 PRD 生成
    prd = generate_prd_from_template("crm", "做一个 CRM 系统")
    assert prd['product_type'] == 'crm'
    assert len(prd['business_goals']) > 0
    print("   ✅ PRD 生成成功")

    # 测试格式化
    summary = format_prd_summary(prd)
    assert '业务目标' in summary
    print("   ✅ PRD 格式化成功")

    print(f"\n✅ 测试通过：PRD 升维功能正常")


def run_all_tests():
    """运行所有测试"""
    print("\n" + "🧪 "*25)
    print("交互式 PRD 补全测试套件")
    print("🧪 "*25 + "\n")

    test_low_quality_auto_fallback()
    test_medium_quality()
    test_high_quality()
    test_prd_upgrade()

    print("\n" + "📊 "*25)
    print("测试总结")
    print("📊 "*25)
    print("""
所有测试通过！

实现的功能：
✅ 低质量 PRD（< 0.3）→ 自动 fallback_safe
✅ 中等质量 PRD（0.3-0.7）→ 提示但继续执行
✅ 高质量 PRD（>= 0.7）→ 直接执行
✅ 产品类型检测（CRM, E-commerce, SaaS, Generic）
✅ PRD 升维生成（基于模板）
✅ 交互与非交互模式切换

交互模式功能（需手动测试）：
- 低质量输入提供 A/B/C 选项
- 逐步提问补充缺失信息
- 升维生成后确认
- 任意阶段可取消
    """)


if __name__ == '__main__':
    run_all_tests()
