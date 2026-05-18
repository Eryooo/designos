"""Built-in heuristic principles library.

Provides Nielsen's 10 usability heuristics plus 5 business-domain extensions
(data trust, performance, accessibility, information density, cross-platform
consistency) sourced from ``legacy/sharing-materials/体验评估分享内容.md``.

A skill can override the catalogue by passing its own principle list to the
``detect`` tool; otherwise this list is used as the default.
"""

from __future__ import annotations

from schemas import HeuristicPrinciple

# ---------------------------------------------------------------------------
# Nielsen 10 — translated to the bilingual labels used in DesignOS reports.
# ---------------------------------------------------------------------------

NIELSEN_PRINCIPLES: list[HeuristicPrinciple] = [
    HeuristicPrinciple(
        id="H1",
        name="系统状态可见性",
        description=(
            "系统应在合理时间内通过适当反馈让用户了解正在发生什么"
            "（加载、操作结果、当前位置、当前选中状态）。"
        ),
        source="Nielsen 1994 - Visibility of system status",
    ),
    HeuristicPrinciple(
        id="H2",
        name="匹配用户心智",
        description=(
            "系统语言、概念和顺序应贴近用户工作心智，避免技术术语和"
            "工程内部命名直接暴露给用户。"
        ),
        source="Nielsen 1994 - Match between system and the real world",
    ),
    HeuristicPrinciple(
        id="H3",
        name="用户控制与自由",
        description=(
            "用户经常误操作，需要清晰的撤销、退出和确认机制，避免"
            "出现无法回退的死路径。"
        ),
        source="Nielsen 1994 - User control and freedom",
    ),
    HeuristicPrinciple(
        id="H4",
        name="一致性与标准",
        description=(
            "同类操作、同类状态在不同页面/区域应使用同样的措辞、"
            "图标、布局，遵循平台和组织的设计规范。"
        ),
        source="Nielsen 1994 - Consistency and standards",
    ),
    HeuristicPrinciple(
        id="H5",
        name="错误预防",
        description=(
            "比报错更好的是阻止错误发生：用确认、约束、默认值、"
            "二次确认避免高风险操作。"
        ),
        source="Nielsen 1994 - Error prevention",
    ),
    HeuristicPrinciple(
        id="H6",
        name="识别而非记忆",
        description=(
            "尽量减少用户的记忆负担，把对象、动作、选项以可识别的"
            "形式呈现，必要时给出说明而不是要求用户记住。"
        ),
        source="Nielsen 1994 - Recognition rather than recall",
    ),
    HeuristicPrinciple(
        id="H7",
        name="灵活与高效",
        description=(
            "为新手提供易学路径，同时给熟练用户提供快捷方式（"
            "快捷键、批量操作、个性化设置）。"
        ),
        source="Nielsen 1994 - Flexibility and efficiency of use",
    ),
    HeuristicPrinciple(
        id="H8",
        name="美学与极简设计",
        description=(
            "界面只展示与当前任务相关的信息，控制视觉噪音，"
            "保持视觉层级清晰。"
        ),
        source="Nielsen 1994 - Aesthetic and minimalist design",
    ),
    HeuristicPrinciple(
        id="H9",
        name="帮助用户识别和恢复错误",
        description=(
            "错误信息应使用普通语言准确说明问题，并给出可执行的"
            "恢复建议；危险操作应明确后果。"
        ),
        source="Nielsen 1994 - Help users recognize, diagnose and recover from errors",
    ),
    HeuristicPrinciple(
        id="H10",
        name="帮助和说明",
        description=(
            "即使最理想是不需要帮助文档，系统也应提供易于检索的"
            "上下文帮助、术语解释和操作说明。"
        ),
        source="Nielsen 1994 - Help and documentation",
    ),
]


# ---------------------------------------------------------------------------
# Business extensions — derived from the sharing materials.
# ---------------------------------------------------------------------------

BUSINESS_EXTENSIONS: list[HeuristicPrinciple] = [
    HeuristicPrinciple(
        id="B1",
        name="数据可信与可追溯",
        description=(
            "对涉及数据展示、识别结果、报告产出的页面，需说明"
            "统计口径、数据来源、更新时间，关键结论可追溯到明细。"
        ),
        source="DesignOS 业务扩展（参考：体验评估分享内容.md）",
    ),
    HeuristicPrinciple(
        id="B2",
        name="加载与性能反馈",
        description=(
            "长耗时操作必须有进度反馈、可取消机制和失败恢复路径，"
            "避免出现无反馈的等待。"
        ),
        source="DesignOS 业务扩展",
    ),
    HeuristicPrinciple(
        id="B3",
        name="可访问性",
        description=(
            "界面元素应满足键盘可达、对比度、表单标签、屏幕阅读器"
            "标注等基础可访问性要求。"
        ),
        source="DesignOS 业务扩展（参考 WCAG 2.1 AA）",
    ),
    HeuristicPrinciple(
        id="B4",
        name="信息密度与视觉层级",
        description=(
            "B 端复杂列表、详情页应控制信息密度，主操作、次操作、"
            "危险操作的视觉权重应有明确层级。"
        ),
        source="DesignOS 业务扩展",
    ),
    HeuristicPrinciple(
        id="B5",
        name="跨端一致性",
        description=(
            "Web、客户端、移动端在同一业务能力上的术语、状态、操作"
            "应保持一致，避免用户跨端时重新学习。"
        ),
        source="DesignOS 业务扩展",
    ),
]


def default_principles() -> list[HeuristicPrinciple]:
    """Return the default principle catalogue (Nielsen 10 + 5 extensions).

    Returns:
        A new list of :class:`HeuristicPrinciple` objects (safe to mutate by
        the caller; the underlying models are immutable Pydantic instances).
    """

    return [*NIELSEN_PRINCIPLES, *BUSINESS_EXTENSIONS]


def principle_index(principles: list[HeuristicPrinciple]) -> dict[str, HeuristicPrinciple]:
    """Index a principle list by id for quick lookup.

    Args:
        principles: The principles to index.

    Returns:
        Mapping from principle id to :class:`HeuristicPrinciple`.
    """

    return {p.id: p for p in principles}


__all__ = [
    "BUSINESS_EXTENSIONS",
    "NIELSEN_PRINCIPLES",
    "default_principles",
    "principle_index",
]
