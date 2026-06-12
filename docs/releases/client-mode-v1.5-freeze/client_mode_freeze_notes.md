# Client Mode Freeze Notes

## Freeze Conclusion

`client mode` 现在可以按 `V1.5 freeze` 冻结，并进入试点。

原因不是“门槛放松了”，而是：

- final-capable golden cases 已经全部过线
- salvageable case 的 `trusted_mapping_rate` 已经从 `0.8` 拉到 `1.0`
- bounded cases 的失败已经稳定归因为 `objective input insufficiency`
- 当前 `release blocker = 0`

## 当前已知适用边界

这些场景现在适合 `final_delivery_ready`：

- 高质量截图 + 关键页面/关键状态覆盖充分
- 高质量截图 + OCR / markdown 说明足够支撑 page/state trusted mapping
- salvageable 输入：原始输入基本够，但需要 runtime ingestion / remediation 把已有证据吃成 trusted coverage
- 复杂多模块、多状态场景，只要 OCR / markdown / critical-path coverage 足够强

这些场景现在适合 `bounded`，而不应冒充 final：

- 有一部分可信 evidence，但 trusted mapping / critical-path coverage 还没过线
- 可以形成受限结论，但不能达到 normal mode 接近 `99%-100%` 的 final 信度

这些场景仍然必须补资料：

- 无 OCR 且无有效说明文件
- 关键页面本身没给全
- 关键状态缺失，导致 `critical_path_state_hit_rate` 明显不足
- 截图可读性不足，无法形成 trusted evidence

## 当前不适用场景

以下问题不再视为当前 release blocker，而是输入客观不足：

- 高质量截图，但没有 OCR、没有 `screens-description.md`、也没有足够页面说明
- 真缺关键页面或关键状态
- 低分辨率截图导致 page/state 无法被可信识别

这些场景会继续：

- `blocked`
- `supplement_required`
- 或 bounded 结果

这是当前产品边界，不是当前版本质量失败。

## Freeze 期间不再做的事

这版冻结后，不再继续做：

- 新 OCR 能力
- 新 mapping 逻辑扩展
- 新 clarification 逻辑扩展
- client mode 新 CLI
- client mode 范围外增强

## 后续阶段

- `client mode` 已冻结
- 下一阶段应转向 `web mode` 封装
- `web mode` 收住后，再抽 `Skills Factory Template`

这一步只做阶段切换说明，不在本批开始 web mode 代码。
