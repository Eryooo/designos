"""
Interactive PRD Supplementation

提供交互式 PRD 补全的辅助函数
"""

from typing import Dict, List, Any


# GAP 提问模板
GAP_QUESTIONS = {
    "business_goals": {
        "question": "❓ 这个系统的主要业务目标是什么？",
        "examples": [
            "提升销售效率（减少 30% 管理时间）",
            "增加客户转化率（提升 20%）",
            "改善团队协作（实时共享客户信息）",
            "降低运营成本（减少人工成本 15%）"
        ],
        "prompt": "请输入 1-3 个业务目标（用分号分隔）："
    },

    "target_users": {
        "question": "❓ 主要用户是谁？",
        "examples": [
            "销售主管（管理 10-50 人团队，查看报表）",
            "销售员（录入客户，跟进线索）",
            "客服人员（处理客户问题）",
            "管理员（系统配置，权限管理）"
        ],
        "prompt": "请输入主要用户角色（用分号分隔）："
    },

    "core_features": {
        "question": "❓ 核心功能有哪些？",
        "examples": [
            "客户信息管理（CRUD）",
            "销售线索跟进（提醒、状态更新）",
            "销售漏斗（可视化转化流程）",
            "数据报表（销售额、转化率）",
            "团队协作（共享客户、任务分配）"
        ],
        "prompt": "请输入核心功能（用分号分隔）："
    },

    "constraints": {
        "question": "❓ 有什么技术或时间约束？",
        "examples": [
            "技术栈：React + Ant Design",
            "时间：3 个月内上线",
            "预算：50 万元",
            "兼容性：需支持 IE11"
        ],
        "prompt": "请输入约束（可选，直接回车跳过）："
    },

    "non_functional": {
        "question": "❓ 有什么性能/安全要求？",
        "examples": [
            "性能：页面加载 < 2s",
            "并发：支持 500 用户同时在线",
            "安全：数据加密存储",
            "可用性：99.9% SLA"
        ],
        "prompt": "请输入非功能需求（可选，直接回车跳过）："
    }
}


# PRD 升维模板（基于产品类型）
PRD_TEMPLATES = {
    "crm": {
        "business_goals": [
            "提升销售团队工作效率 30%",
            "提高客户转化率 20%",
            "实现客户信息集中管理"
        ],
        "target_users": [
            {"role": "销售主管", "description": "管理 10-50 人销售团队，需要查看团队业绩和客户分布"},
            {"role": "销售员", "description": "每天管理 20-100 个客户，需要快速录入和跟进"}
        ],
        "core_features": [
            {"name": "客户信息管理", "priority": "P0", "description": "客户基本信息 CRUD"},
            {"name": "销售线索跟进", "priority": "P0", "description": "线索状态更新、跟进提醒"},
            {"name": "销售数据报表", "priority": "P1", "description": "销售额、转化率统计"}
        ],
        "non_functional": {
            "performance": "页面加载 < 2s",
            "concurrency": "支持 500 用户",
            "security": "数据加密存储"
        }
    },

    "e-commerce": {
        "business_goals": [
            "提升 GMV 50%",
            "提高用户复购率 30%",
            "降低获客成本 20%"
        ],
        "target_users": [
            {"role": "C端用户", "description": "25-40 岁，移动端为主，追求便捷购物"},
            {"role": "商家", "description": "中小商家，需要简单的商品和订单管理"}
        ],
        "core_features": [
            {"name": "商品浏览", "priority": "P0"},
            {"name": "购物车", "priority": "P0"},
            {"name": "下单支付", "priority": "P0"},
            {"name": "订单管理", "priority": "P0"}
        ]
    },

    "saas": {
        "business_goals": [
            "获取 1000 家付费企业客户",
            "实现 80% 续费率",
            "降低人工服务成本 40%"
        ],
        "target_users": [
            {"role": "企业管理员", "description": "配置系统、管理权限"},
            {"role": "普通员工", "description": "日常使用核心功能"}
        ],
        "core_features": [
            {"name": "核心业务功能", "priority": "P0"},
            {"name": "权限管理", "priority": "P0"},
            {"name": "数据报表", "priority": "P1"}
        ]
    },

    "generic": {
        "business_goals": [
            "提升业务效率",
            "改善用户体验",
            "降低运营成本"
        ],
        "target_users": [
            {"role": "主要用户", "description": "系统的主要使用者"}
        ],
        "core_features": [
            {"name": "核心功能1", "priority": "P0"},
            {"name": "核心功能2", "priority": "P0"}
        ]
    }
}


def detect_product_type(prd_content: str) -> str:
    """
    检测产品类型

    Args:
        prd_content: PRD 内容

    Returns:
        产品类型（crm, e-commerce, saas, generic）
    """
    content_lower = prd_content.lower()

    if any(keyword in content_lower for keyword in ['crm', '客户', '销售', '线索', 'customer']):
        return 'crm'
    elif any(keyword in content_lower for keyword in ['电商', '商城', '购物', 'e-commerce', 'shop']):
        return 'e-commerce'
    elif any(keyword in content_lower for keyword in ['saas', '订阅', '企业服务']):
        return 'saas'
    else:
        return 'generic'


def generate_prd_from_template(product_type: str, original_content: str) -> Dict:
    """
    基于模板生成完整 PRD

    Args:
        product_type: 产品类型
        original_content: 原始输入

    Returns:
        完整 PRD 结构
    """
    template = PRD_TEMPLATES.get(product_type, PRD_TEMPLATES['generic'])

    return {
        "product_type": product_type,
        "business_goals": template['business_goals'],
        "target_users": template['target_users'],
        "core_features": template['core_features'],
        "non_functional": template.get('non_functional', {}),
        "original_input": original_content,
        "generated_by": "template",
        "confidence": 0.7  # 模板生成的置信度
    }


def format_prd_summary(prd: Dict) -> str:
    """格式化 PRD 摘要"""
    lines = []
    lines.append("【生成的 PRD 摘要】\n")

    lines.append("业务目标：")
    for goal in prd['business_goals']:
        lines.append(f"  - {goal}")

    lines.append("\n目标用户：")
    for user in prd['target_users']:
        if isinstance(user, dict):
            lines.append(f"  - {user['role']}: {user.get('description', '')}")
        else:
            lines.append(f"  - {user}")

    lines.append("\n核心功能：")
    for feature in prd['core_features']:
        if isinstance(feature, dict):
            priority = feature.get('priority', 'P0')
            lines.append(f"  - [{priority}] {feature['name']}")
        else:
            lines.append(f"  - {feature}")

    if prd.get('non_functional'):
        lines.append("\n非功能需求：")
        for key, value in prd['non_functional'].items():
            lines.append(f"  - {key}: {value}")

    return "\n".join(lines)


def convert_template_to_prd_content(prd: Dict) -> str:
    """将模板 PRD 转换为 markdown 格式"""
    lines = []
    lines.append("# PRD - 产品需求文档\n")
    lines.append(f"> 基于用户输入自动生成\n")

    lines.append("## 1. 业务目标\n")
    for goal in prd['business_goals']:
        lines.append(f"- {goal}")

    lines.append("\n## 2. 目标用户\n")
    for user in prd['target_users']:
        if isinstance(user, dict):
            lines.append(f"### {user['role']}\n")
            lines.append(f"{user.get('description', '')}\n")

    lines.append("## 3. 核心功能\n")
    for feature in prd['core_features']:
        if isinstance(feature, dict):
            lines.append(f"### {feature['name']} ({feature.get('priority', 'P0')})\n")
            if feature.get('description'):
                lines.append(f"{feature['description']}\n")

    if prd.get('non_functional'):
        lines.append("## 4. 非功能需求\n")
        for key, value in prd['non_functional'].items():
            lines.append(f"- {key}: {value}")

    return "\n".join(lines)
