# UXEval V1 Golden Cases 验收清单

## 1. 验收目标

本轮验收不是继续找零碎代码问题，而是判断当前 `V1` 是否已经达到：

- 可替代一部分低价值设计工作
- 能显著减少截图整理、命名、补说明、证据归档等机械劳动
- 在证据充分时可稳定产出最终交付
- 在证据不足时不会伪装成交付完成

收工判断只看两件事：

- 当前版本是否已经 `ready for pilot`
- 如果还没到，剩下的是不是明确的 `release blocker`

## 2. 核心标准

### 2.1 正常模式标准

- 只有在证据充分、关键页面和关键状态覆盖充分、问题证据链闭合时，才允许进入 `final_delivery_ready`
- 允许进入最终报告的结果，必须符合你定义的近乎满分标准
- 自动化目标是尽量让系统自己补救、自己归档、自己起草映射，而不是频繁叫用户回来救场

### 2.2 Fallback 标准

- `fallback_safe` 可以输出受限结果
- 但不能冒充最终报告
- 所有正向断言都必须具备清晰证据基础

### 2.3 用户负担标准

- 不允许要求用户先大规模重命名截图
- 不允许要求用户手工补完整 `screens-map`
- 用户只应补最少量系统客观拿不到的信息

## 3. Golden Cases

### Case 1: 高质量截图 + 说明充分

目标：
验证系统是否可以几乎不打断用户，直接达到 `final_delivery_ready`

输入建议：

- 5-10 张高分辨率关键页面截图
- 覆盖主流程关键页面
- 覆盖 `default / loading / error / success / empty` 中与场景相关的状态
- 提供 `screens-description.md`

预期结果：

- 尽量不需要人工补料
- auto-remediation 可运行但不应制造多余暂停
- draft mapping 应大部分自动确认
- 允许进入最终报告
- 输出完整 `issue_report / html_report / evidence_pack`

判定重点：

- 用户是否几乎不用整理截图
- 最终报告是否可信
- 是否存在“明明证据足够却还频繁打断”的问题

### Case 2: 高质量截图 + 无说明

目标：
验证系统能否更多依赖 OCR、页面文本线索和自动映射，而不是强依赖人工说明

输入建议：

- 5-10 张高分辨率截图
- 不提供 `screens-description.md`
- 命名可以普通，不需要很规范

预期结果：

- 如果 OCR / cue 足够，应尽量自动继续
- 不应因为“没有说明文件”就直接变成高摩擦流程
- 如仍有少数歧义，应该只要求确认少量截图

判定重点：

- 系统是否真正使用了 OCR 和自动映射
- 用户是否只被要求补最少量信息
- 最终是 `final_delivery_ready`、`fallback_safe` 还是 `supplement_required`

### Case 3: 乱命名截图 + 说明充分

目标：
验证“命名是加速项，不是门槛”是否真的成立

输入建议：

- 使用类似 `IMG_1024.png`、`final-01.png`、`页面截图1.png` 这类真实混乱命名
- 提供较好的 `screens-description.md`

预期结果：

- 不应要求用户先重命名整套截图
- 系统应优先依赖 markdown、OCR、自动映射
- 如仍需人工介入，应优先给最小 clarification package

判定重点：

- 命名混乱是否单独导致被卡住
- 系统是否先建议 `screens-description.md` / clarification，而不是先建议 rename
- 用户是不是只需要补极少量确认

### Case 4: 低质量截图 + 说明不足

目标：
验证系统是否会正确阻断或降级，而不是产出伪高质量结果

输入建议：

- 低分辨率截图
- 关键页面不全
- 无说明文件或说明极弱

预期结果：

- 不应进入最终报告
- 应优先 auto-remediation
- auto-remediation 后仍不够，应一次性给出结构化补料清单
- 如只能 fallback，应给 bounded package，而不是假完整报告

判定重点：

- 是否会误放行 `final_delivery_ready`
- 补料要求是否具体、一次性、可执行
- fallback 是否边界清晰

### Case 5: 大系统、多模块、多状态

目标：
验证系统在真实复杂场景下，是否仍然能显著减少整理劳动，而不是把复杂度甩回给用户

输入建议：

- 多模块截图
- 覆盖多个流程
- 命名可以混乱
- 说明可部分提供、部分缺失

预期结果：

- 系统应先做 proactive planning
- 系统应先 auto-remediation
- 系统应先 auto-draft mapping
- 用户只被要求补少数关键歧义项，而不是补全量 mapping 或全量 rename

判定重点：

- 是否仍然保持低摩擦输入
- 是否只打断一次
- clarification package 是否真正缩小到少数截图

## 4. 每个 Case 都要记录的结果

对每个 Case，统一记录：

- 输入情况
- 用户是否需要补资料
- 用户被打断几次
- 是否需要自己写 `screens-map`
- 是否需要重命名截图
- 最终状态：
  - `final_delivery_ready`
  - `fallback_safe`
  - `supplement_required`
  - `blocked`
- 交付产物：
  - 最终报告
  - bounded fallback package
  - clarification package
- 你主观判断：
  - 替代了哪些低价值工作
  - 还有哪些工作仍要人工做

## 5. V1 Ready 判断

### 判定为 V1 Ready for Pilot

满足以下条件即可认为可进入试点：

- Case 1 稳定进入 `final_delivery_ready`
- Case 2 至少能在一部分场景下无需说明直接完成，或仅需极少补充
- Case 3 证明乱命名不是主要门槛
- Case 4 不会误交付伪完整结果
- Case 5 在复杂场景下仍显著减少人工整理工作
- 用户平均不会被反复打断
- 最终主观判断是：
  - 这套系统已经能替代一部分低价值设计工作

### 判定为 Not Ready

只要出现以下任一项，就应视为仍有 release blocker：

- 证据不足却仍进入最终报告
- 乱命名本身成为主要阻断因素
- 大型截图集仍要求大量手工 mapping 或 rename
- clarification 范围过大，接近用户自己重做
- auto-remediation 形同虚设
- fallback 边界不清，仍在冒充最终结果

## 6. 建议输出格式

每个 Case 用同一模板记录：

```md
## Case X

### 输入
- ...

### 系统行为
- ...

### 用户实际需要做的事
- ...

### 最终状态
- final_delivery_ready / fallback_safe / supplement_required / blocked

### 是否达到目标
- 达到 / 部分达到 / 未达到

### 结论
- 替代了哪些低价值工作
- 剩余问题是否属于 release blocker
```

## 7. 最终收官判断

这轮 Golden Cases 跑完后，只输出一句结论即可：

- `V1 ready for pilot`
- `V1 not ready`

如果是 `not ready`，只允许列出真正的 release blockers，不再发散讨论长期优化项。
