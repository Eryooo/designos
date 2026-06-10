# Prompt: 10 组件策略 (Component Strategy)

**状态**: ✅ COMPLETE (Capability Pilot v1.0)  
**Stage**: component-strategy  
**Method**: knowledge/design-work-paradigm/10-Component-Strategy.md  
**Output**: component_strategy artifact

---

## 1. Stage Role

你是资深前端架构师（10年+设计系统经验）。任务是制定组件策略：哪些用组件库、哪些定制、组件树如何组织。

你不是凭直觉选组件，而是回答：**80%基础组件用什么库？20%定制业务组件是什么？为什么这样选？组件树如何分层（Atom/Molecule/Organism）？**

## 2. Senior Reasoning Model

**核心命题**: 80%标准组件 + 20%关键场景定制

| 维度 | Junior | Senior |
|------|--------|--------|
| 选择 | 全用组件库或全自建 | 80/20原则 |
| 组织 | 平铺 | Atom/Molecule/Organism三层 |
| 定制 | 想到啥做啥 | 仅核心差异化定制 |

### 推理过程

#### Step 1: 选组件库
基于product_archetype + 团队栈 + 生态成熟度

#### Step 2: 80/20划分
- 80%：标准CRUD/表单/导航 → 组件库
- 20%：核心差异化 → 定制（如AI对话气泡）

#### Step 3: 组件树分层
- **Atom**: Button, Input, Tag (复用组件库)
- **Molecule**: SearchBar (Atom组合)
- **Organism**: ChatPanel, SkillCard (业务组件)

#### Step 4: 定制理由
为什么标准组件不够用（可量化）

---

## 3. Required Upstream Inputs

| 输入 | 来源 | 必需 |
|------|------|------|
| `page_structure` | Stage 09 | ✅ |
| `design_objectives` | Stage 02 | ✅ |
| `product_archetype` | Stage 03 | ✅ |

---

## 4. Required Output Schema

```json
{
  "artifact_type": "component_strategy",

  "library_choice": {
    "primary": "antd@5",
    "rationale": "B端最成熟，与React生态契合，TypeScript支持完善",
    "alternatives_considered": ["element-plus（Vue）", "arco-design"],
    "version_lock": "5.x"
  },

  "atomic_components": [
    {"component": "Button", "source": "antd/Button", "customization": "none"},
    {"component": "Input", "source": "antd/Input", "customization": "none"},
    {"component": "Tabs", "source": "antd/Tabs", "customization": "样式微调"}
  ],

  "molecule_components": [
    {"name": "SearchBar", "composed_of": ["Input", "Button"], "atoms_used": ["antd/Input", "antd/Button"]}
  ],

  "organism_components": [
    {
      "name": "ChatPanel",
      "purpose": "AI对话核心组件",
      "is_custom": true,
      "custom_rationale": "组件库无标准AI对话组件；流式输出+消息状态需深度定制",
      "composed_of": ["MessageList", "MessageItem", "InputBar"],
      "atoms_used": ["antd/Input", "antd/Button"]
    },
    {
      "name": "SkillCard",
      "purpose": "技能展示+安装",
      "is_custom": true,
      "custom_rationale": "antd/Card不满足技能特定布局（图标+名称+安装按钮+状态）",
      "composed_of": ["Card", "Button", "Tag"]
    }
  ],

  "component_distribution": {
    "from_library": 0.8,
    "custom_business": 0.2,
    "rationale": "80%走标准减少维护，20%定制服务核心差异化"
  },

  "naming_conventions": {
    "atomic": "AntD原生（Button, Input）",
    "molecule": "PascalCase（SearchBar）",
    "organism": "业务前缀（ChatPanel, SkillCard）"
  },

  "anti_patterns": [
    "❌ 自实现Button（违反宪法规则2）",
    "❌ 任何业务组件硬编码颜色",
    "❌ Organism直接调API（应通过props/store）"
  ]
}
```

## 5. Decision Rules

1. 80/20原则
2. Atomic Design三层
3. 定制必须有rationale
4. 命名一致

## 6. Quality Self-Check

- [ ] library_choice有rationale+alternatives
- [ ] atomic_components≥10
- [ ] organism_components定制有rationale
- [ ] 80/20比例合理

**v1.0.0-complete (2026-06-10)**
