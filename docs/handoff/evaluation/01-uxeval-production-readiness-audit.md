# UXEval 生产就绪性排查报告

## 1. 报告目的

本报告不是评价这次单次跑得“像不像设计师”，而是判断：

1. `uxeval` 是否已经达到集团内可共享、可复用、可回归的生产级 skill 水平
2. 它距离“解放设计师处理低阶体验评估工作”还差哪些系统能力
3. 这次暴露的问题中，哪些只属于 `uxeval`，哪些应升级为 `DesignOS 全技能` 的统一质量门槛

## 2. 审计证据范围

本次结论基于三组证据：

### A. 本次 `client autonomous run`

- 输入：PRD + 26 张截图
- 输出：16 个问题、5 类系统性问题、PRD-截图冲突清单、Markdown/HTML/Excel/JSON 产物
- 代表意义：验证 `uxeval` 在**无人工 checkpoint** 下能否独立产出结构化结果

### B. `uxeval` skill 本体静态审计

审查文件包括：

- `SKILL.md`
- `pipeline.yaml`
- `constitution.md`
- `INPUT.md`
- `README.md`
- `prompts/`
- `tests/`
- `eval/`

### C. 对照组：`web/playwright` 真实环境执行结果

路径：`/Users/young/Documents/Codex/data-design-review`

重点对照：

- 真机点击路径是否暴露额外问题
- web 模式是否提供更强的证据类型
- 两个项目是否稳定暴露同一批系统性体验问题

## 3. 总体结论

### 当前评级

`L2：可试点，不可宣称生产级`

### 为什么不是生产级

`uxeval` 已经证明了自己具备三项很有价值的能力：

1. 能把 PRD、截图、问题、系统性归因沉淀成结构化产物
2. 能识别 `PRD 主线` 与 `截图现实覆盖` 的错位，而不是强行编成一个故事
3. 在 `web` 与 `client` 两种上下文下，都能稳定抓到同一批高价值系统问题：入口/空间上下文、空状态承接、前置条件表达、对象关系解释、高成本操作帮助

但它仍然不满足“生产级可替代中高级设计师做低阶评估”的最低条件，因为以下关键能力还没闭环：

- 单一真源没有建立
- 自动化模式没有正式产品化
- 宪法没有被真正机器执行到底
- 测试与回归基线处于失真状态
- 隐私与脱敏承诺没有转成硬执行
- web/client 没有共享同一套稳定证据协议

换句话说，`uxeval` 现在已经是一个**有价值的高潜原型**，但还不是**可组织化放量的生产技能**。

## 4. 核心发现

### P0-1：单一真源失效，技能定义已经自相矛盾

这是当前最严重的问题。不是“文档小错”，而是**不同执行体会按不同规则理解同一个 skill**。

证据：

- `README.md` 仍写 `v0.2.0`，[README.md](/Users/young/.designos/skills/uxeval/README.md:4)
- `pipeline.yaml` 已是 `0.3.1`，[pipeline.yaml](/Users/young/.designos/skills/uxeval/pipeline.yaml:2)
- `README.md` 说是 `7 条评估宪法`，[README.md](/Users/young/.designos/skills/uxeval/README.md:104)
- `SKILL.md` 写 `核心 8 条`，[SKILL.md](/Users/young/.designos/skills/uxeval/SKILL.md:129)
- `constitution.md` 也明确是 `8 条规则`，[constitution.md](/Users/young/.designos/skills/uxeval/constitution.md:3)
- 测试却只校验 `1-7`，[test_pipeline_integration.py](/Users/young/.designos/skills/uxeval/tests/test_pipeline_integration.py:40)
- `README.md` 的输出编号仍停留在 `04-问题报告`，[README.md](/Users/young/.designos/skills/uxeval/README.md:82)
- 本次真实运行实际产物已经到 `07-问题报告`，[run.yaml](/Users/young/Documents/Codex/desigonos/runs/20260521-uxeval-client-01/run.yaml:20)

影响：

- 不同模型、不同执行器、不同维护者读到的是不同 skill
- 无法定义“什么叫跑对了”
- 每次迭代都会继续制造漂移

结论：

在这一项修复前，不应把 `uxeval` 作为集团标准 skill 广泛分发。

### P0-2：验证体系失真，当前 skill 不能自证可用

一个宣称生产级的 skill，必须能在干净环境里快速自检。但当前验证链路存在硬断点。

证据：

- 当前环境直接运行测试失败：`No module named pytest`
- `test_pipeline_integration.py` 仍依赖不存在的 stage `heuristic-detection`，[test_pipeline_integration.py](/Users/young/.designos/skills/uxeval/tests/test_pipeline_integration.py:170)
- 同一测试还断言 `heuristic-detection` 是 tool stage，[test_pipeline_integration.py](/Users/young/.designos/skills/uxeval/tests/test_pipeline_integration.py:189)
- `pipeline.yaml` 里根本没有这个 stage，[pipeline.yaml](/Users/young/.designos/skills/uxeval/pipeline.yaml:26)
- 测试断言 `skill.config.version == "1.0.0"`，[test_pipeline_integration.py](/Users/young/.designos/skills/uxeval/tests/test_pipeline_integration.py:160)
- 实际 pipeline 版本是 `0.3.1`，[pipeline.yaml](/Users/young/.designos/skills/uxeval/pipeline.yaml:2)
- Promptfoo 配置引用的 `eval/judges/parse_json.js` 文件缺失，[promptfoo.yaml](/Users/young/.designos/skills/uxeval/eval/promptfoo.yaml:26)

影响：

- 当前测试不是“保质量”，而是在制造“看起来有测试”的假象
- 发布后无法判断是 skill 退化了，还是测试自己已经过期

结论：

没有可信测试，就不可能持续逼近“比中高级设计师更稳、更高效”的终极目标。

### P0-3：宪法没有真正被内核级执行，合规与证据纪律存在虚高

`uxeval` 的强项之一是“宣称自己有宪法”。但当前问题是：**宪法更多停留在文本层，而不是执行层**。

证据：

- `constitution.md` 定义了 8 条规则，[constitution.md](/Users/young/.designos/skills/uxeval/constitution.md:8)
- 但示例 `verify_constitution` 只检查 1、2、3、5、6、7，未覆盖规则 4 和 8，[constitution.md](/Users/young/.designos/skills/uxeval/constitution.md:177)
- `SKILL.md` 要求 Stage 6 执行 8 条宪法校验，[SKILL.md](/Users/young/.designos/skills/uxeval/SKILL.md:114)
- `constitution.md` 下方又写成 `7 步检查`，[constitution.md](/Users/young/.designos/skills/uxeval/constitution.md:205)
- Prompt 05b 说敏感信息检测后“不阻塞流程，让 heuristic-detection 决定是否打码”，但 `heuristic-detection` stage 并不存在，[05b-screenshot-analysis.md](/Users/young/.designos/skills/uxeval/prompts/05b-screenshot-analysis.md:112)
- 宪法要求 evidence 路径不能包含真实用户名，[constitution.md](/Users/young/.designos/skills/uxeval/constitution.md:45)
- 本次评测包和运行清单仍直接暴露 `/Users/young/...`，[for-skill-review-manifest.json](/Users/young/Documents/Codex/desigonos/outputs/for-skill-review-manifest.json:6)
- `06-问题清单.json` 没有 `unverified_issues` 和 `out_of_scope_issues` 段，说明“附录迁移规则”没有被结构化保留

影响：

- 证据纪律和隐私合规会被高估
- 一旦对外分享产物，敏感本机路径、用户名、内部地址可能进入共享链路

结论：

生产级 skill 不能只“提醒模型小心”，必须把规则变成**硬门禁**。

### P0-4：自动化模式不是正式能力，仍然依赖人类特批

用户这次明确要求“完全不需要人工确认”，skill 才被我强行切换成自动模式。但这不是 skill 原生支持的能力。

证据：

- `SKILL.md` 明确要求不要跳过模式选择，[SKILL.md](/Users/young/.designos/skills/uxeval/SKILL.md:36)
- `SKILL.md` 明确要求 3 个 checkpoint 用户不回复就等待，[SKILL.md](/Users/young/.designos/skills/uxeval/SKILL.md:120)
- `README.md` 也把 3 个 checkpoint 作为固定工作流，[README.md](/Users/young/.designos/skills/uxeval/README.md:75)
- `pipeline.yaml` 只有 checkpoint，没有 `strict / semi-auto / autonomous` 三种正式策略，[pipeline.yaml](/Users/young/.designos/skills/uxeval/pipeline.yaml:59)
- 本次自动运行只能在运行清单中标记 `bypassed_by_user_request`，[run.yaml](/Users/young/Documents/Codex/desigonos/runs/20260521-uxeval-client-01/run.yaml:5)

影响：

- 当前 skill 无法稳定支撑“设计师零介入”
- 每次全自动执行都在偏离原技能定义

结论：

如果终极目标是“设计师不再投入低阶评估劳动”，那 `autonomous mode` 必须从“例外”升级为“一等公民”。

### P1-1：架构职责漂移，client/web 分支尚未真正收敛

现在看起来是双模式，但内部其实存在多套不完全一致的执行心智。

证据：

- `pipeline.yaml` 的 client 分支是 `screenshot-loading`，[pipeline.yaml](/Users/young/.designos/skills/uxeval/pipeline.yaml:106)
- Prompt 05b 仍把自己描述为给 `image-analyzer` 的内部模板，[05b-screenshot-analysis.md](/Users/young/.designos/skills/uxeval/prompts/05b-screenshot-analysis.md:8)
- 模板里还保留 `--from heuristic-detection` 的恢复命令，[任务清单-简洁版.md](/Users/young/.designos/skills/uxeval/templates/任务清单-简洁版.md:60)
- Stage 06 顶部写“把 heuristic-engine 输出的 raw_issues 转成 Issue”，但同一 prompt 的 Step 1 又要求自己遍历截图并生成 `raw_issues`，[06-issue-attribution.md](/Users/young/.designos/skills/uxeval/prompts/06-issue-attribution.md:6)

影响：

- 不同执行器会把 Stage 6 理解成“检测器”或“归因器”
- web/client 结果很难天然可比

结论：

必须把职责拆清为：`collector -> detector -> attribution -> exporter`。

### P1-2：输入契约对真实设计师不友好，生产化输入适配缺位

这次真实执行已经证明：真正的用户不会先帮 skill 把世界整理好。

证据：

- `SKILL.md` 说“用户只需丢 PRD，AI 自动完成目录创建、scope 推断”，[SKILL.md](/Users/young/.designos/skills/uxeval/SKILL.md:76)
- `INPUT.md` 却要求用户预先准备 `inputs/prd.pdf`、`inputs/scope.md`、规范命名截图，[INPUT.md](/Users/young/.designos/skills/uxeval/INPUT.md:12)
- 本次真实输入是 `00_input/数据挖掘V3.9.4.pdf` + 时间戳截图目录，而不是标准 `inputs/`

影响：

- skill 只有在“被熟练使用的人提前配合”时才顺手
- 一旦扩散到集团设计师，失败率会快速上升

结论：

必须把“输入适配层”做成正式能力，而不是让执行者临场兜底。

### P1-3：最终产物没有表达可靠性层级，容易被过度信任

当前输出结果结构化程度不错，但“可靠性元信息”不足。

证据：

- `06-问题清单.json` 有 `source_basis`，但没有 `confidence`
- 也没有 `unverified_issues`、`out_of_scope_issues`
- 本次最终报告虽然写出 `4 项 PRD 核心能力未被截图覆盖`，[07-问题报告.md](/Users/young/Documents/Codex/desigonos/runs/20260521-uxeval-client-01/07-问题报告.md:8)
- 但主报告仍把 16 条问题作为统一强度输出，没有显式“高置信 / 中置信 / 需补证”的分层

影响：

- 业务方、设计师、后续模型会默认所有问题同等可信
- 自动模式下尤其危险

结论：

生产级 skill 必须输出 `confidence + evidence_basis + coverage_score + unresolved_conflicts`。

### P1-4：Prompt 在诱导模型编造量化数据

这是一个非常危险的隐性问题。它不一定每次都爆，但一旦爆，会严重损害可信度。

证据：

- `06-issue-attribution.md` 示例直接使用“平均 8 秒”“实测平均 11s”“5 名用户 20 次点击”的数字，[06-issue-attribution.md](/Users/young/.designos/skills/uxeval/prompts/06-issue-attribution.md:184)
- 同文件还把“高频操作需滚动扫读，平均耗时 8-12 秒”作为系统问题正例，[06-issue-attribution.md](/Users/young/.designos/skills/uxeval/prompts/06-issue-attribution.md:160)
- 但当前 skill 的静态截图模式并没有用户实验数据源、trace timing 或埋点输入

影响：

- 模型可能产出“看起来更专业”的伪精确数字
- 对外分享时会大幅削弱信任

结论：

若无真实 trace 或用户测试数据，必须禁止使用伪量化话术，统一改成 `定性 + [推断] + 证据基础`。

### P1-5：web 模式与 client 模式的高价值证据没有被统一建模

这是对照组给出的最重要结论之一。

对照观察：

- `web/playwright` 项目抓到了 `空间错跳`、`模型训练空白页`、`新开页签反馈缺失`、`覆盖层拦截点击` 等**交互级问题**
- 本次 `client` 模式则更擅长沉淀**结构化问题清单、系统性归因和冲突边界**
- 两者共同稳定暴露的问题包括：
  - 空状态承接弱
  - 前置条件表达不足
  - 对象关系不自解释
  - 高成本动作帮助不足
  - 入口/导航上下文复杂

影响：

- 说明 `uxeval` 的启发式骨架是有价值的
- 也说明 `client` 模式不能替代 `web` 模式的交互证据

结论：

必须统一 `Evidence.kind = screenshot / dom / trace / video / navigation_path`，否则双模式只能“看起来一体”，不能真正回归比较。

### P1-6：工具依赖写在定义里，但可执行兜底策略缺位

证据：

- `pipeline.yaml` 直接依赖 `playwright-driver`、`image-analyzer`、`excel-builder`，[pipeline.yaml](/Users/young/.designos/skills/uxeval/pipeline.yaml:95)
- 但 skill 中没有描述“这些工具不可用时的标准降级路径”
- 本次真实成功运行，实际上是靠通用文件能力、Python 库和本地视觉能力兜底，而不是按 pipeline 原样落地

影响：

- skill 在不同客户端、不同团队环境里不可移植
- 同一 skill 在 Codex、Claude、Cursor、Trae 等环境下结果稳定性会显著不同

结论：

每个工具依赖都需要 `probe -> preferred path -> fallback path -> degrade flag`。

### P2-1：技能包过重且多文档并行，持续维护成本高

依据 `skill-creator` 的最佳实践，skill 应尽量保持单一入口、渐进式披露，避免 README、CHANGELOG、INPUT 等并行真源。

当前情况：

- `SKILL.md` 185 行
- `README.md` 202 行
- `constitution.md` 254 行
- `INPUT.md` 115 行
- 四个核心说明文件合计 756 行

影响：

- 每次改动都需要多点同步
- 非常容易继续制造漂移

结论：

应把 skill 收敛成：

- `SKILL.md`：入口工作流 + 跳转说明
- `references/`：详细规则、输入协议、评测规范
- `scripts/`：可执行预检、导出、校验

### P2-2：评测集不够代表生产现实

证据：

- 当前只有 1 个 golden case
- 只有 1 个 failure case
- 没有 web mode golden
- 没有 autonomous mode golden
- 没有敏感信息/脱敏 case
- 没有 `PRD 强 + 截图弱`、`PRD 弱 + 截图强`、`路由错跳` 这样的高价值失败样本

影响：

- skill 即使“通过评测”，也可能只是在过拟合少数理想样本

结论：

如果目标是“设计师不再做低阶劳动”，那回归集必须覆盖真实最脏、最烦、最容易翻车的场景。

## 5. 横向对照结论：web 模式 vs client 模式

### 共同证明 skill 核心有效的部分

两边都稳定打到了同一批系统问题：

1. 入口和空间上下文复杂
2. 空状态没有承接下一步
3. 前置条件表达不足
4. 模型/任务流/输出的对象关系不清
5. 高成本动作帮助不足

这说明 `uxeval` 的启发式骨架不是随机命中，而是具备一定跨模式稳定性。

### web 模式额外暴露的生产级问题

`data-design-review` 中只有真实点击和导航才能暴露的问题，本次 client 模式抓不到：

1. 空间入口错跳
2. 错误落点后的模型训练空白页
3. 新开页签缺少反馈
4. 覆盖层拦截点击
5. 真实多工作空间路径的上下文可信度问题

这说明：

- `client` 模式更像“静态证据归因器”
- `web` 模式才有能力成为“真实任务执行审计器”

### client 模式额外体现的优势

本次 `client autonomous run` 在结构化沉淀层更整齐：

- 冲突分析更显式
- 任务清单更结构化
- 报告归并更容易继续喂给下游模型

这说明：

- 两种模式不应互相替代
- 应该在统一 schema 下分别承载不同证据强项

## 6. 距离“解放设计师”的真实差距

如果终极目标是：

> DesignOS 所有 Skills 产出达到生产级，甚至比中高级设计师更稳、更高效，让设计师不再投入低阶劳动

那么当前 `uxeval` 还差 4 层能力。

### 第 1 层：从“能产出”到“能自证”

现在已做到：

- 能产出
- 能结构化

但还没做到：

- 能自测
- 能回归
- 能证明自己这次没漂

### 第 2 层：从“像专家”到“比专家稳”

专家的优势不是多会写问题，而是：

- 知道哪里证据不够
- 不会把推断说成事实
- 不会泄露敏感上下文
- 知道什么时候不能下结论

当前 `uxeval` 在这四点上还没全部产品化。

### 第 3 层：从“一个 skill 跑通”到“组织可放量”

可放量意味着：

- 新设计师不会因为输入格式不标准就失败
- 新环境不会因为少一个 MCP 就整体不可用
- 下游模型可以稳定消费它的结构化结果

当前 `uxeval` 还处在“高手带着跑”阶段，不是“组织自然扩散”阶段。

### 第 4 层：从“评估助手”到“低阶劳动替代者”

低阶劳动真正要被替代，skill 必须稳定包办：

1. 输入适配
2. 安全预检
3. 证据采集
4. 冲突识别
5. 问题检测
6. 置信度标记
7. 脱敏导出
8. 回归验证

当前最缺的是第 6、7、8 项。

## 7. 修复优先级建议

### 第一阶段：必须先修，才能谈生产

1. 建立单一真源
   - 统一 `SKILL / pipeline / constitution / tests / README`
   - 清理过时 stage 名称、版本号、编号体系

2. 补齐正式自动化模式
   - `strict`
   - `semi-auto`
   - `autonomous`

3. 把宪法改成真门禁
   - 规则 4、8 补进内核验证
   - `unverified_issues / out_of_scope_issues` 成为结构字段
   - 输出前强制脱敏

4. 修复测试体系
   - 删除或恢复 `heuristic-detection`
   - 修复缺失文件和错误断言
   - 确保干净环境一键 smoke test

### 第二阶段：修完后可进入小范围试点

1. 统一 web/client 证据 schema
2. 为问题补 `confidence`
3. 为 run 补 `coverage_score`
4. 为输入补 `input-manifest`
5. 为导出补 `share-safe` 模式

### 第三阶段：修完后才有资格冲击“设计师低阶劳动替代”

1. 建立 8-12 个真实回归案例
2. 引入质量阈值
   - 问题精度
   - 证据完整率
   - 冲突识别率
   - 脱敏通过率
3. 建立跨模式一致性评测
4. 建立失败自恢复与降级策略

## 8. 对 DesignOS 全部 Skills 的统一质量门槛建议

`uxeval` 暴露出的不是孤例，而是一组平台级质量门槛。以后任何要被称为“生产级”的 DesignOS skill，都至少要满足下面 8 条：

1. 单一真源
   - skill 定义、约束、测试、导出协议不能多套口径并存

2. 一键自证
   - 干净环境下可运行 smoke test

3. 正式降级策略
   - 缺工具、缺输入、缺权限时，能明确降级，而不是静默失败

4. 结构化可靠性元数据
   - `confidence`
   - `coverage`
   - `source_basis`
   - `unresolved_assumptions`

5. 隐私默认安全
   - 分享包默认不暴露用户名、本机路径、账号、内部域名

6. 模式统一协议
   - 多模式 skill 的下游输出必须共 schema

7. 回归集覆盖脏场景
   - 不能只测理想输入

8. 明确的人类退出条件
   - skill 什么时候可独立跑完
   - 什么时候必须升级人工

## 9. 最终判断

如果现在问：

> `uxeval` 能不能作为集团内共享 skill 直接大规模铺开？

我的判断是：

`不能直接铺开，只适合在强 owner 带领下做小范围试点。`

如果换个问题：

> `uxeval` 值不值得继续打磨到生产级？

我的判断是：

`非常值得。`

因为它已经证明了最难伪造的两件事：

1. 它能稳定抓到高价值系统问题，而不是只会写零碎吐槽
2. 它能把问题沉淀成结构化资产，具备继续被模型和团队消费的价值

真正阻碍它进入生产的，不是“启发式评估逻辑不行”，而是：

- 技能工程化
- 合规产品化
- 回归基础设施

只要这三层补起来，`uxeval` 是有机会从“一个厉害的技能 demo”，走到“能替设计师稳定处理低阶体验评估劳动”的。
