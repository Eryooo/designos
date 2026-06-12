# Web Mode Known Boundaries

本文件回答一个问题：**web mode 现在“能信到哪”，不能信到哪。**
配合 `web_mode_validation_baseline.md` 使用：baseline 说“怎么验证”，本文件说“边界在哪”。

- 日期：2026-06-01
- run_mode：web

## 1. 现在已经适合哪些场景

- 无需登录、或登录态可手动预置（持久化目录已有 cookie）的 Web 应用走查。
- 单页主链路自动取证：导航 → 截图 → DOM 抽取 → 批量 JSON 脚本执行。
- 本地可控站点上的多 tab / iframe 切换与读取（已在 mock server 上 smoke 通过）。
- 表单填充（只填不提交）类只读取证。
- web mode 作为“比 client mode 更强、更易自证”的主评估模式：证据 confidence 为
  `ground_truth`（URL + DOM + 截图三通道），强于 client mode 的人工截图通道。

## 2. 哪些场景仍需进一步真实验证（当前不要承诺）

| 场景 | 现状 | 还缺什么 |
| --- | --- | --- |
| 真实登录验证 | persistent context 已实现 | 真账号密码登录全流程（含 SSO/二次验证）真站点回归 |
| 多 tab 验证 | mock server 通过 | 真实站点懒加载新窗口、跨域新标签的稳定性回归 |
| iframe 验证 | mock server 通过 | 真实跨域 iframe、嵌套 iframe、动态注入 iframe 的回归 |
| heuristic-engine 集成 | adapter 产出 DetectionRequest 结构成立 | driver → heuristic-engine → 问题清单端到端闭环回归 |

## 3. heuristic-engine 集成目前到哪一步

- ✅ 已实现：`heuristic_adapter.build_detection_request()` 把 driver 的执行证据
  （截图 + DOM snapshot）转换成 heuristic-engine 的 DetectionRequest 结构，
  含 `mode="web"`、`dom_data`、默认 10 条 Nielsen 原则。
- ✅ 已接线：`execute_batch` 工具会在批量执行后调用 adapter，返回 `detection_request`。
- ⚠️ 未充分验证：从 DetectionRequest 实际喂给 heuristic-engine、产出并归因问题清单的
  **端到端闭环**未纳入本基线回归。引用此能力时必须标“已接线、闭环未回归”。

## 4. 措辞纪律（防止“已实现”被写成“已生产可用”）

- 第 1 节能力 → 可写“已验证可用”。
- 第 2、3 节能力 → 只能写“已实现 / 已接线，但未充分验证”，并指向本文件。
- 任何对外文档、SKILL.md、release note 不得把第 2/3 节能力描述为“生产可用 / 已上线 / 稳定”。
