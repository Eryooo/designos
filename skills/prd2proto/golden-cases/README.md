# prd2proto Golden Cases

**目的**：保留典型场景的 PRD 输入和预期产出，用于：
1. 端到端冒烟测试（pipeline 是否能正常跑通）
2. 质量回归（修改 prompt/runtime 后产出质量是否退化）
3. 新人快速理解 pipeline 能力（看 case 比看代码快）

---

## 当前状态: scaffold（占位）

**本轮（P0）**: 只建目录结构 + 框架性内容（PRD输入示例 + 预期输出说明）  
**未来（P1+）**: 跑真实 LLM 产出 expected-outputs 完整 JSON

---

## 三个典型场景

| Case | 场景 | 复杂度 | 重点验证 |
|------|------|-------|---------|
| **case-01** | SaaS 规则引擎 | 高 | 复杂业务流程 + 多角色权限 |
| **case-02** | 数据看板 | 中 | 信息架构 + 状态矩阵 |
| **case-03** | 审批工作流 | 中高 | 业务流程 + 异常处理 + 协作 |

---

## 目录结构

```
golden-cases/
├── README.md (本文件)
└── case-XX-{name}/
    ├── README.md         (该 case 的描述、输入/输出说明)
    ├── inputs/
    │   ├── prd.md        (PRD 文档)
    │   └── scope.md      (范围说明，可选)
    └── expected-outputs/
        ├── 01-input-diagnosis.json
        ├── 02-design-objectives.json
        ├── ...
        └── 17-professional-gap-assessment.json
```

---

## 使用方式

### 跑某个 case

```bash
python3 skills/prd2proto/runtime/executor.py \
  --prd skills/prd2proto/golden-cases/case-01-saas-rule-engine/inputs/prd.md \
  --max-tokens 32768 \
  --out /tmp/case-01-output.json
```

### 对比预期输出

```bash
diff <(jq . /tmp/case-01-output.json) \
     <(jq . skills/prd2proto/golden-cases/case-01-saas-rule-engine/expected-outputs/...)
```

---

## 维护原则

1. **PRD 输入要真实**：从实际项目改写（去敏感数据），避免 toy example
2. **预期输出可演进**：每次 prompt/schema 变更后重新生成
3. **不锁死字段值**：用 schema 验证结构，用人工 review 验证质量
4. **覆盖关键能力**：4 层目标推导/状态矩阵/业务流程/可追溯性

---

**版本**: scaffold v0.1（2026-06-10 P0）
