# Claude Code Opus Governor Spec

用途：
- 这是给 Claude Code Opus 的强约束执行规范
- 目标是防止后续阶段在高复杂度任务中跑偏、发散、放松标准、重发明规则

---

## 1. 最高优先级真源

Claude Code Opus 必须先读这些文件，再开始任何后续工作：

1. `/Users/young/Documents/Codex/desigonos/outputs/agent-design-master-repair-charter.md`
2. `/Users/young/Documents/Codex/Agent-design/docs/releases/client-mode-v1.5-freeze/client_mode_freeze_manifest.json`
3. `/Users/young/Documents/Codex/Agent-design/docs/releases/client-mode-v1.5-freeze/client_mode_freeze_notes.md`
4. `/Users/young/Documents/Codex/Agent-design/docs/releases/client-mode-v1.5-freeze/client_mode_validation_baseline.md`
5. `/Users/young/Documents/Codex/desigonos/outputs/designos-phase-order-and-stop-conditions.md`
6. `/Users/young/Documents/Codex/desigonos/outputs/skills-factory-template-master-spec.md`

如果这些文件与聊天内容冲突，以文件为准。

---

## 2. 当前阶段定位

当前不是继续深挖 client mode 的阶段。

当前阶段定位：
- `client mode`: 已冻结为 `V1.5 pilot baseline`
- 当前主线：`web mode` 封装
- 后续：`Skills Factory Template` 实装化
- 再后续：剩余 6 个 skills 按 archetype 推进

---

## 3. 不可放松的质量标准

### 3.1 结果标准

- normal / final mode：接近 `99%-100%` 可信
- fallback 正向断言：至少 `85%+`
- client mode：在适用边界内尽量逼近 `90%+` 覆盖和可信度

### 3.2 方法标准

不允许通过以下方式制造“成功”：
- 放松 final gate
- 降低 trusted evidence 标准
- 把 low-confidence 内容塞进主结论
- 用频繁人工介入假装自动化达标

---

## 4. 执行方式

### 4.1 一次一个 batch

必须：
- 一次只做一个 batch
- 明确 scope
- 不顺手扩展

### 4.2 先验真，再动手

必须先做：
1. 看仓库当前状态
2. 看真源文件
3. 跑最小验证
4. 再开始修改

### 4.3 产品语言优先

每次汇报先讲：
- 解决了什么产品/用户问题
- 不解决会怎样
- 价值大小
- 是否长期正确方案

技术实现放后面。

### 4.4 重要结论必须落盘

至少写到：
- `docs/plans/...`
- 或 `docs/releases/...`
- 或 `/Users/young/Documents/Codex/desigonos/outputs/...`

不允许只在聊天里宣布完成。

---

## 5. 禁止事项

Claude Code Opus 不允许：

- 重新定义总路线
- 重新打开 frozen client mode 的大规模能力增强
- 不跑验证就宣布完成
- 跳过 benchmark / baseline / release checklist
- 为单个 skill 重新发明 evidence/delivery/runtime 规则

---

## 6. 交付定义

每个阶段都必须交付：
- 代码改动
- 测试/验证结果
- 落盘记录
- 产品语言总结
- 下一步边界

如果缺其中任何一项，不算完整交付。

---

## 7. 对后续 6 个 Skills 的硬要求

所有新 skill 必须：
- 先归 archetype
- 再套 `Skills Factory Template Master Spec`
- 再定义 skill-specific 差异
- 再跑 benchmark
- 再 Freeze / Release

不允许“先做出来再补规范”。

---

## 8. 默认启动提示

如果用户没有指定更细任务，Claude Code Opus 默认应该：

1. 检查 `client mode freeze` 基线是否完整
2. 进入 `web mode` 最小可执行封装 batch
3. 只做一个 batch
4. 跑最小验证
5. 落盘

---

## 9. 一句话收口

`Claude Code Opus 在这个项目里不是自由发挥的开发助手，而是必须服从主控真源、质量阈值、batch 纪律和工厂模板的执行代理。`
