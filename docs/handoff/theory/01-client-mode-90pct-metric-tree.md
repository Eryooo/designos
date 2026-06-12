# Client Mode 90%+ 技术指标树

目标：把 `uxeval client mode` 的“90%+ 可用度”从一句产品目标，拆成可观测、可归因、可持续拉升的技术指标体系。

---

## 1. 先统一结论

后续 Route B 的所有修复，不应该只看：

- 最终是不是 `final_delivery_ready`
- gate 有没有拦住低质量结果

而应该同时看两层指标：

1. `结果指标`
   - 最终覆盖度和可信度是否达到目标
   - first-pass 自动做成率是否在提升

2. `驱动指标`
   - PRD 解析准不准
   - critical path 提取得准不准
   - 截图与页面/状态匹配准不准
   - OCR/markdown/fusion 是否真的把已有证据吃干净
   - auto-remediation 有没有把 case 往 final 拉升

一句话：

`最终目标是 90%+；技术路径是把 90%+ 拆成一组前段、中段、后段的关键指标。`

---

## 2. 北极星指标

这是 client mode 的最终业务指标，不可替代：

### 2.1 Final Delivery Readiness Rate

定义：
- 在“输入基本合格”的真实 case 中，最终达到 `final_delivery_ready` 的比例

目标：
- `>= 70%`：进入试点可用
- `>= 85%`：进入强可用阶段
- `>= 90%`：达到 client mode 主力模式目标

### 2.2 Critical Path Coverage Rate

定义：
- P0/P1 主链路关键页面 + 关键状态的覆盖率

目标：
- `P0 页面覆盖率 >= 90%`
- `P0 状态覆盖率 >= 90%`
- `P1 页面覆盖率 >= 85%`
- `P1 状态覆盖率 >= 85%`

### 2.3 Trusted Evidence Rate

定义：
- 进入主结论的证据中，属于 `trusted` 的比例

目标：
- `normal mode final`：`>= 99%`
- `fallback`：`>= 85%`

### 2.4 Low-Value Human Work Reduction

定义：
- 用户在一次 client run 中被要求做的低价值整理劳动量

重点看：
- 是否要求重命名截图
- 是否要求手写整套 mapping
- 是否反复被打断补零散信息

目标：
- 不要求批量重命名
- 不要求手写完整 mapping
- clarification 次数 `<= 1`

---

## 3. 上游输入质量指标

这些指标回答的是：

`系统有没有尽可能把前面的输入吃准，而不是把锅都甩给 gate。`

### 3.1 PRD Parsing Accuracy Proxy

定义：
- PRD 结构化后，是否正确提取：
  - 核心模块
  - 关键任务
  - 关键页面
  - 关键状态
  - P0/P1 优先级

建议指标：
- `module_extraction_completeness`
- `critical_page_extraction_completeness`
- `critical_state_extraction_completeness`
- `priority_tag_precision`

目标：
- P0/P1 页面和状态提取完整率 `>= 95%`

### 3.2 Capture Mission Precision

定义：
- `capture_mission` 里定义的 must-capture pages/states 是否真的对最终交付有高相关性

建议指标：
- `mission_page_precision`
- `mission_state_precision`
- `mission_overcollection_rate`

目标：
- 关键采集任务单不要过宽
- “必须补”的页面/状态误报率要低

### 3.3 Input Sufficiency Detection Accuracy

定义：
- 系统对“当前输入是否足够”的判断是否准确

建议指标：
- `true_missing_evidence_precision`
- `false_supplement_request_rate`

目标：
- 不要把“系统自己没吃懂”误判成“用户没给”

---

## 4. 证据摄取与融合指标

这些指标回答的是：

`用户已经给了的证据，系统有没有真正吃进去。`

### 4.1 OCR Yield

定义：
- 截图中可抽取文本的有效产出率

建议指标：
- `ocr_available_rate`
- `readable_screenshot_rate`
- `text_signal_density`
- `ocr_failure_rate`

目标：
- 高质量截图的有效文字提取率持续拉升

### 4.2 Markdown Utilization Rate

定义：
- `screens-description.md` / `screens-map.md` / `screens-index.md` 被有效利用的比例

建议指标：
- `description_link_success_rate`
- `markdown_to_screenshot_alignment_rate`

### 4.3 Trusted Mapping Rate

定义：
- `screenshot -> page/state` 自动映射中，进入 `trusted` 的比例

建议指标：
- `trusted_mapping_rate`
- `provisional_mapping_rate`
- `conflicting_mapping_rate`
- `clarification_needed_rate`

目标：
- trusted 持续升
- provisional/conflicting 持续降

### 4.4 Evidence Fusion Uplift

定义：
- OCR + markdown + filename + directory + remediation 组合后，相对单一信号的提升量

建议指标：
- `fusion_uplift_trusted_mapping`
- `fusion_uplift_critical_page_hit`
- `fusion_uplift_state_hit`

---

## 5. 主链路覆盖指标

这组指标最关键，因为它最直接决定 client mode 是否接近 90%+。

### 5.1 Critical Path Hit Rate

定义：
- P0/P1 主链路中，被截图实际覆盖到的关键页面/状态比例

建议指标：
- `critical_path_page_hit_rate`
- `critical_path_state_hit_rate`
- `critical_path_full_path_completion_rate`

### 5.2 Uncovered Critical Node Count

定义：
- 仍未覆盖的关键节点数

建议指标：
- `missing_p0_pages_count`
- `missing_p0_states_count`
- `missing_p1_pages_count`
- `missing_p1_states_count`

### 5.3 Core Feature Coverage

定义：
- 核心业务能力对应的页面/状态覆盖度

建议指标：
- `core_feature_coverage`
- `p0_feature_coverage`

---

## 6. 自动补救能力指标

这组指标回答的是：

`系统在不打扰用户的前提下，能把多少 case 自动从不够格拉向 final。`

### 6.1 Auto-Remediation Lift

定义：
- auto-remediation 前后，关键指标的提升量

建议指标：
- `critical_path_coverage_pre_post_delta`
- `trusted_mapping_pre_post_delta`
- `delivery_status_pre_post_delta`

### 6.2 First-Pass Final Rate

定义：
- 不靠人工 clarification，第一次直接进入 final 的比例

建议指标：
- `first_pass_final_rate`

这是后续最重要的效率指标之一。

### 6.3 Salvageable Input Rate

定义：
- 原本看起来要补资料，但实际上通过更强 ingestion/fusion/remediation 可以做成的比例

建议指标：
- `salvageable_input_rate`
- `upstream_diagnosis_distribution`
  - `input_truly_insufficient`
  - `existing_input_was_salvageable_but_needed_better_ingestion`

目标：
- 尽量提升“可挽救输入”的自动做成率

---

## 7. 人工介入负担指标

这组指标保证 client mode 不会为了提高 final rate，又把低价值工作还给用户。

### 7.1 Clarification Burden

定义：
- 一次 run 里真正需要人工确认的歧义项数量

建议指标：
- `clarification_package_count`
- `clarification_item_count`
- `critical_clarification_item_count`

目标：
- clarification 次数 `<= 1`
- clarification item 尽量控制在最小集合

### 7.2 Supplement Request Precision

定义：
- 系统要求补资料时，是不是都真缺关键输入

建议指标：
- `supplement_request_precision`
- `false_supplement_request_rate`

### 7.3 Low-Value Work Return Rate

定义：
- 系统是否把低价值整理劳动甩回给用户

重点观察：
- 是否要求大规模 rename
- 是否要求用户手工整理整套 mapping
- 是否要求用户补非关键页面

目标：
- 持续下降到接近 0

---

## 8. 最终交付质量指标

这组指标回答的是：

`系统不仅要做成，还要做得可信。`

### 8.1 Final Gate Precision

定义：
- 被放进 `final_delivery_ready` 的 run，是否真的都够格

目标：
- normal mode 最终交付近 `99%-100%` 可信

### 8.2 Fallback Safety Precision

定义：
- 被放进 fallback 的正向结论，是否都仍在 `85%+` 可信区间

### 8.3 Unverified Leakage Rate

定义：
- 低置信度、待验证内容混入主结论的比例

目标：
- 接近 0

---

## 9. 建议落成的指标看板

后续每一批 Route B 修复，都建议固定看这一组 dashboard：

### A. 结果层
- `final_delivery_ready_rate`
- `fallback_safe_rate`
- `supplement_required_rate`
- `blocked_rate`

### B. 核心覆盖层
- `p0_page_coverage`
- `p0_state_coverage`
- `p1_page_coverage`
- `p1_state_coverage`
- `critical_path_full_path_completion_rate`

### C. 证据可信层
- `trusted_mapping_rate`
- `provisional_mapping_rate`
- `conflicting_mapping_rate`
- `unverified_leakage_rate`

### D. 自动做成率层
- `first_pass_final_rate`
- `auto_remediation_lift`
- `salvageable_input_rate`

### E. 用户负担层
- `clarification_item_count`
- `supplement_request_precision`
- `low_value_work_return_rate`

---

## 10. 后续批次怎么用这套指标

从现在开始，每一批 Route B 都不只问：

- 这批修了什么功能

还必须回答：

- 提升了哪几个关键指标
- 对 `90%+` 目标的直接贡献是什么
- 有没有让用户负担变轻
- 有没有提高 first-pass success
- 有没有提升 trusted evidence 占比

也就是说，后面每批都应该能映射成：

`功能修复 -> 技术指标提升 -> final/fallback 结果改善`

---

## 11. 一句话收口

`client mode 要做到 90%+，不能只靠最后一层 gate；必须把 PRD 解析、capture mission、evidence fusion、critical path coverage、auto-remediation、clarification burden、final audit 全部拆成可观测指标，然后逐项拉升。`
