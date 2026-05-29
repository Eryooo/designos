# Wave 3 端到端验证清单

> 用工厂装配 ai-analytics 骨架，验证 CONTRACT §4 Gate 4 的 5 条硬指标。

---

## 前置条件

Wave 2 三个 Agent 必须全部完成且通过：
- ✅ Agent A: `extract.py` + `test_extract.py` 全过
- ✅ Agent B: `validate.py` + `test_validate.py` 全过
- ✅ Agent C: `scaffold.py` + `test_scaffold.py` 全过
- ✅ 工厂回归：`cd .factory && pytest tests/ -q` 全过
- ✅ Kernel 零回归：`pytest tests/unit/ -q` 全过

---

## Gate 4 验收标准（CONTRACT §4）

### 4.1 装配速度（Time-to-Skeleton）

```bash
time python3 -m tools.scaffold \
    --archetype evaluation \
    --name ai-analytics \
    --output-dir /tmp/factory-test
```

**目标**: ≤ 30 分钟（首次），≤ 10 分钟（第二次不同 archetype），≤ 5 分钟（终态）

**实测记录**:
- 装配耗时: ___ 秒
- 产出文件数: ___
- 产出目录数: ___

### 4.2 骨架过 validate

```bash
cd .factory
python3 -m tools.validate /tmp/factory-test/ai-analytics --archetype evaluation
echo "Exit code: $?"
```

**目标**: exit code 0，无 violation

**实测记录**:
- Exit code: ___
- Violations: ___
- 报告输出: （粘贴）

### 4.3 骨架能被 kernel 加载

```python
from pathlib import Path
from _kernel_bridge import load_pipeline_skill

skill_dir = Path("/tmp/factory-test/ai-analytics")
skill = load_pipeline_skill(skill_dir)
print(f"✅ Loaded: {skill.name} v{skill.version}")
print(f"   Stages: {len(skill.get_stages())}")
print(f"   Outputs: {[o.id for o in skill.config.outputs]}")
```

**目标**: 不抛错，能打印 skill 信息

**实测记录**:
- 加载成功: ✅ / ❌
- Stage 数: ___
- Output 数: ___
- 错误（如有）: （粘贴）

### 4.4 骨架的 pytest 测试通过

```bash
cd /tmp/factory-test/ai-analytics
python3 -m pytest tests/ -v
```

**目标**: 占位测试全过（至少 2 个：test_frontmatter_runtime / test_pipeline_integration）

**实测记录**:
- 通过数: ___
- 失败数: ___
- 输出: （粘贴）

### 4.5 目录结构与 archetype 一致

```bash
cd .factory
python3 << 'EOF'
from archetypes import load_archetype
from pathlib import Path

archetype = load_archetype("evaluation")
skill_dir = Path("/tmp/factory-test/ai-analytics")

missing = []
for d in archetype.directory.required_directories:
    if not (skill_dir / d).exists():
        missing.append(f"directory: {d}")
for f in archetype.directory.required_files:
    if not (skill_dir / f).exists():
        missing.append(f"file: {f}")

if missing:
    print("❌ Missing:")
    for item in missing:
        print(f"   - {item}")
else:
    print("✅ All required directories and files present")
EOF
```

**目标**: 无缺失

**实测记录**:
- 缺失项: ___

---

## Gate 4 通过条件

5 条全部 ✅ 才算 Gate 4 通过。任一条 ❌，整个 Wave 3 失败，需回退修工厂。

---

## 后续（Gate 4 通过后）

1. 记录实测指标到 `.factory/CHANGELOG.md`
2. 对比 CONTRACT §2 北极星指标，标注达成情况
3. 启动 Wave 4（可选）：用工厂装配 prd2proto（generation archetype），验证跨 archetype 复用率
