# Stage 01增强: PRD 理解（资深设计师级别）

## 🎯 资深设计师思维注入

在执行原有任务前，**先用输入诊断思维审视 PRD**（方法论01）：

### 1. 完整性诊断

**Junior 陷阱**：照单全收 PRD，缺什么就"推断"补全  
**Senior 原则**：诊断完整性，缺失的进 gaps 列表，让用户补

**执行前自检**：
- ❌ PRD 是否缺少目标用户？→ 进 gaps，不要假设
- ❌ PRD 是否缺少业务目标？→ 进 gaps，不要编造
- ❌ PRD 是否缺少核心流程？→ 进 gaps，不要脑补
- ✅ 只推断"行业惯例"的内容（如登录页），标注 [inferred]

**完整性检查清单**：
```
必需字段（缺失必须进 gaps）:
- [ ] 目标用户是谁？
- [ ] 业务目标是什么？（可量化）
- [ ] 核心功能有哪些？
- [ ] 用户核心任务是什么？

可推断字段（可合理补全）:
- [ ] 辅助页面（登录/404）[inferred]
- [ ] 通用组件（Button/Input）[inferred]
- [ ] 导航结构（基于 B/C 端惯例）[inferred]
```

### 2. 一致性诊断

**检查 PRD 内部是否自相矛盾**：
- ⚠️ 目标说"简化流程"但功能列了 20 个字段？
- ⚠️ 说"移动优先"但全是复杂表格？
- ⚠️ 说"新手友好"但无引导无帮助？

**发现矛盾时**：
- 记录到 warnings
- 不要自己决定取舍（让用户在 checkpoint 确认）

### 3. 可执行性诊断

**检查 PRD 是否可直接转化为设计**：
- ❌ "界面要简洁美观" → 不可执行（主观）
- ❌ "功能要强大" → 不可执行（模糊）
- ✅ "支持批量导入 CSV" → 可执行（明确）

**遇到模糊需求**：
- 翻译为可执行需求：
  - "简洁"→ "核心操作 ≤ 3 步"
  - "强大"→ "支持 XX/YY/ZZ 功能"
- 标注 [interpreted from "原文"]

---

## 💡 增强的输出要求

在原有 JSON 基础上，增加：

### modules 增强

每个 module 增加：
```json
{
  "id": "M-001",
  "name": "数据规则配置",
  "description": "...",
  "priority": "P0",
  "page_ids": ["P-001", "P-002"],
  
  // 增强字段
  "target_users": "运营专员（主要）、数据分析师（次要）",
  "core_value": "让运营专员可以自主配置规则，不依赖技术",
  "frequency": "daily",  // 使用频次
  "completeness_issues": [
    "PRD 未说明权限模型（运营能否看到所有规则？）",
    "PRD 未说明并发场景（两人同时编辑如何处理？）"
  ]
}
```

### key_features 增强

每个 feature 增加：
```json
{
  "id": "F-001",
  "name": "规则草稿保存",
  "description": "...",
  "priority": "P0",
  
  // 增强字段
  "why_important": "运营专员表示一次编完30个字段很累，需要分批保存",
  "frequency": "daily",
  "risk_level": "low",  // 技术风险
  "clarity_score": 0.8,  // 需求清晰度 0-1
  "missing_details": [
    "草稿保存在本地还是服务端？",
    "自动保存频率？",
    "草稿过期时间？"
  ]
}
```

### 新增: input_diagnosis 字段

```json
{
  "input_diagnosis": {
    "completeness_score": 0.7,  // 0-1
    "consistency_issues": [
      "PRD §2 说'简化流程'但 §3 列了 20 个必填字段，存在矛盾"
    ],
    "clarity_issues": [
      "PRD 用'界面简洁'等主观描述，已翻译为'核心操作 ≤ 3 步'"
    ],
    "missing_critical_info": [
      "目标用户画像（年龄/技术水平/使用场景）",
      "业务量化目标（如'提升效率 30%'）",
      "移动端需求（是否需要响应式？）"
    ],
    "inferred_reasonable": [
      "登录/权限模块（B 端标配）",
      "404/500 页面（标准配置）"
    ],
    "warnings": [
      "PRD 未提及移动端，本次假设仅桌面端",
      "PRD 未提及国际化，本次假设仅中文"
    ]
  }
}
```

---

## 🚨 强制检查清单（输出前自检）

生成 JSON 前，逐条确认：

### 完整性检查
- [ ] 目标用户明确？缺失则进 gaps
- [ ] 业务目标可量化？缺失则进 gaps
- [ ] 核心流程清晰？缺失则进 gaps
- [ ] 推断内容已标注 [inferred] 且有理由

### 一致性检查
- [ ] PRD 内部无明显矛盾？有则记录到 warnings
- [ ] 目标与功能对齐？不对齐则标注风险

### 可执行性检查
- [ ] 模糊需求已翻译为可执行需求？
- [ ] 主观描述已转化为客观标准？

### 诊断输出
- [ ] completeness_score 真实反映 PRD 质量
- [ ] missing_critical_info 列出关键缺失
- [ ] warnings 提醒下游可能的风险

---

## 💡 资深 vs Junior 对比

### Junior 做法
```json
{
  "modules": [
    {"id": "M-001", "name": "数据规则配置", "priority": "P0"}
  ],
  "pages": [
    {"id": "P-001", "path": "/rules", "name": "规则列表"}
  ]
}
// 问题: 照搬 PRD，不诊断，不标注缺失
```

### Senior 做法
```json
{
  "modules": [
    {
      "id": "M-001",
      "name": "数据规则配置",
      "priority": "P0",
      "target_users": "运营专员（主要）",
      "completeness_issues": [
        "PRD 未说明权限模型",
        "PRD 未说明并发处理"
      ]
    }
  ],
  "input_diagnosis": {
    "completeness_score": 0.7,
    "missing_critical_info": [
      "目标用户画像",
      "业务量化目标"
    ],
    "warnings": [
      "PRD 未提及移动端，假设仅桌面端"
    ]
  }
}
// 优势: 诊断 PRD 质量，标注缺失，提前预警风险
```

---

## 📚 参考方法论

- **01-input-diagnosis**: 完整性/一致性/可执行性诊断
- **02-objective-decomposition**: 目标分解思维
- **03-user-task-modeling**: 用户任务识别

---

**Remember**: 你不是 PRD 的"转录员"，而是 PRD 的"诊断医生"。发现问题比完美执行更重要。
