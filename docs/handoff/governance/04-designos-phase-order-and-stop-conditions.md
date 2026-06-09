# DesignOS 阶段顺序与停止条件

## 1. 当前阶段顺序

当前后续工作顺序固定为：

1. `client mode` Freeze 后人工验收支持
2. `web mode` 封装
3. `Skills Factory Template` 抽象
4. 剩余 6 个 skills 按 archetype 推进

不要跳回去重新深挖 frozen client mode，除非发现 release blocker。

---

## 2. 每个阶段的停止条件

### 阶段 A：Client Mode Freeze 后支持

停止条件：

- `client mode` 冻结产物完整
- baseline 命令可复跑
- 用户完成端到端人工验收或明确记录问题

进入下一阶段：
- web mode 封装

### 阶段 B：Web Mode 封装

停止条件：

- 明确 web mode 输入契约
- 明确 browser/playwright 证据采集契约
- 明确与 client mode 的差异边界
- 完成至少一轮 benchmark / end-to-end 评估
- 形成可试点的 web mode release baseline

进入下一阶段：
- skills factory template 抽取

### 阶段 C：Skills Factory Template

停止条件：

- 这 8 套模板被明确抽出并落盘：
  1. Input Contract
  2. Evidence Contract
  3. Delivery Contract
  4. Runtime Skeleton
  5. Benchmark / Eval Harness
  6. Release Skeleton
  7. Skill Archetype Model
  8. Production Definition of Done

进入下一阶段：
- 剩余 6 个 skills 按 archetype 开发

### 阶段 D：剩余 6 个 Skills

停止条件：

- 第 2 个 skill 明显比 `uxeval` 开发更快
- 模板确实复用成功
- skill 开发周期开始从周级压到天级

---

## 3. 全局禁止事项

任何阶段都不要：

- 再次无限修 frozen client mode
- 重新定义总目标和分层
- 为了速度牺牲质量阈值
- 每个新 skill 再重发明一套输入/证据/交付/benchmark/发布方法

---

## 4. 一句话收口

`当前的核心不是把同一个 skill 无限打磨，而是按阶段收口、按阶段切换、按模板放大。`
