> ⚠️ **ARCHIVED / OUTDATED — DO NOT USE FOR CURRENT STATUS.**
> 本文件是历史过程记录，不代表当前状态。当前权威状态见仓库根
> `INTERNAL-PILOT-README.md` / `REVIEW-MANIFEST.md` / `skills/status.matrix.yaml`。

# 企业级打磨问题清单与修复进程

**评估日期**: 2026-06-09  
**当前版本**: P0+P1+P2 Baseline  
**当前评分**: 75/100  
**目标评分**: 95/100（企业级）

---

## 📋 问题清单总览

### Critical（阻塞生产）- 6 项
### High（影响质量）- 8 项  
### Medium（降低体验）- 5 项  
### Low（锦上添花）- 4 项  
**Total**: 23 项

---

## 🚨 Critical 问题（阻塞生产使用）

### C1. 16/17 Prompts 为框架版

**问题描述**：
- 只有 01-input-diagnosis.md 完整
- 02-17 只有结构定义，缺少详细内容
- 无法真正引导 LLM 执行设计推理

**影响**：
- ❌ 无法执行完整的 PRD → 代码流程
- ❌ LLM 不知道如何生成 user_task_map
- ❌ 质量门无法真正验证产物质量

**当前状态**：
```
01-input-diagnosis.md:     ✅ 完整（~600 lines）
02-design-objectives.md:   ⚠️ 框架（~70 lines）
03-product-archetype.md:   ⚠️ 框架（~70 lines）
...
17-professional-gap.md:    ⚠️ 框架（~70 lines）
```

**修复方案**：
- **阶段 1**（P3.1 - 核心 prompts）：补充 3 个核心 prompts
  - 04-user-task-modeling.md
  - 07-information-architecture.md  
  - 10-component-strategy.md
- **阶段 2**（P3.2 - 次要 prompts）：补充 6 个次要 prompts
  - 02-design-objectives.md
  - 06-user-journey-mapping.md
  - 11-state-matrix.md
  - 12-interaction-rules.md
  - 15-constrained-code-generation.md
  - 17-professional-gap-assessment.md
- **阶段 3**（P3.3 - 剩余 prompts）：补充剩余 7 个

**工作量估算**：
- 核心 3 个：~1800 lines（3 * 600）
- 次要 6 个：~3600 lines（6 * 600）
- 剩余 7 个：~4200 lines（7 * 600）
- **Total**: ~9600 lines

**优先级**: 🔴 P0（必须）

---

### C2. LLM 集成未实现

**问题描述**：
- `_mock_stage_output()` 为简化实现
- 未真正调用 LLM + prompts-v2
- 无法验证 prompts 是否真的约束 LLM

**影响**：
- ❌ 测试基于 mock，不代表真实效果
- ❌ 不知道 LLM 是否会遵守 prompts 约束
- ❌ 不知道 quality gates 是否真的能阻塞低质量输出

**当前状态**：
```python
def _mock_stage_output(self, stage, inputs):
    # 简化实现：返回固定结构
    return {...}
```

**修复方案**：
- **P3.4**: 实现 LLM 集成
  - 实现 `LLMClient` 类（调用 Anthropic API）
  - 实现 `PromptLoader` 类（加载 prompts-v2）
  - 实现 `_real_stage_output()` 替换 mock
  - 处理 LLM 错误和重试

**技术方案**：
```python
class LLMClient:
    def __init__(self, api_key: str, model: str = "claude-3-opus"):
        self.api_key = api_key
        self.model = model
    
    def call(self, prompt: str, schema: Dict) -> Dict:
        """调用 LLM 并强制 JSON 输出"""
        # 1. 调用 Anthropic API
        # 2. 解析 JSON 输出
        # 3. 验证 schema
        # 4. 重试如果失败
        pass

class PromptLoader:
    def load(self, prompt_file: str, variables: Dict) -> str:
        """加载 prompt 并替换变量"""
        pass
```

**工作量估算**：~500 lines

**优先级**: 🔴 P0（必须）

---

### C3. 真实场景未验证

**问题描述**：
- 所有测试基于 mock 数据
- 未用真实 PRD 测试完整流程
- 不知道 prompts 质量如何

**影响**：
- ❌ 不知道 LLM 真实表现
- ❌ prompts 可能有遗漏的约束
- ❌ quality gates 阈值可能不准确

**当前状态**：
- 0 个真实 PRD 测试
- 0 个真实设计师评审

**修复方案**：
- **P3.5**: 真实场景测试
  - 准备 3-5 个真实 PRD（不同复杂度）
  - 执行完整流程
  - 对比人工设计师的产物
  - 调整 prompts 和阈值

**测试用例**：
1. 简单 CRM（~500 字 PRD）
2. 中等复杂电商（~2000 字 PRD）
3. 复杂 SaaS（~5000 字 PRD）
4. 低质量 PRD（几句话）
5. 中文 + 英文 PRD

**工作量估算**：测试 + 调整工作

**优先级**: 🔴 P0（必须）

---

### C4. 字段级追溯不完整

**问题描述**：
- `auto_trace_from_reasoning_assets` 只实现了 IA
- 其他 artifact 类型为简化实现
- 无法追溯 component_strategy 的每个字段

**影响**：
- ⚠️ traceability_map 不完整
- ⚠️ 无法验证所有字段有来源
- ⚠️ professional_gap_report 不准确

**当前状态**：
```python
def auto_trace_from_reasoning_assets(self, output, assets):
    if output['artifact_type'] == 'information_architecture':
        return self._trace_ia_fields(output, assets)  # ✅ 完整
    
    # 其他类型未实现
    return {}  # ❌
```

**修复方案**：
- **P3.6**: 完善字段级追溯
  - 实现 `_trace_component_fields()`
  - 实现 `_trace_state_fields()`
  - 实现 `_trace_interaction_fields()`
  - 实现 `_trace_code_fields()`

**工作量估算**：~800 lines

**优先级**: 🔴 P0（影响质量报告）

---

### C5. 代码约束验证为简化实现

**问题描述**：
- `_extract_pages_from_code()` 为 mock
- 需要真实的 AST 解析
- 无法真正验证"代码是否来自 IA"

**影响**：
- ⚠️ code_constraint_gate 形同虚设
- ⚠️ 可能生成"授权外页面"
- ⚠️ 无法防止 LLM 自由发挥

**当前状态**：
```python
def _extract_pages_from_code(self, code: Dict) -> List[str]:
    # Mock 实现
    return []
```

**修复方案**：
- **P3.7**: 实现真实代码解析
  - 使用 AST 解析 React 代码
  - 提取所有 Route / Page 组件
  - 对比 IA 定义的页面列表
  - 识别"授权外页面"

**技术方案**：
```python
import ast
from typing import List

def extract_routes_from_react(code_dir: str) -> List[str]:
    """从 React 代码提取所有 routes"""
    routes = []
    # 1. 扫描所有 .tsx 文件
    # 2. 解析 AST
    # 3. 查找 <Route path="..." />
    # 4. 返回所有 paths
    return routes
```

**工作量估算**：~400 lines

**优先级**: 🟡 P1（影响约束效果）

---

### C6. Inference Detection 为关键字匹配

**问题描述**：
- `detect_inferred_fields()` 使用简单关键字匹配
- 无法真正检测推断内容
- 语义相似的内容无法识别

**影响**：
- ⚠️ inference_limit_gate 不准确
- ⚠️ 可能漏掉推断字段
- ⚠️ professional_gap_report 不完整

**当前状态**：
```python
def detect_inferred_fields(self, output, input_sources):
    # 简单关键字匹配
    if field_value in input_text:
        return False  # 非推断
    return True  # 推断
```

**修复方案**：
- **P3.8**: 实现语义匹配
  - 使用 embedding 计算相似度
  - 阈值判断是否为推断
  - 更准确的推断检测

**技术方案**：
```python
from sentence_transformers import SentenceTransformer

class InferenceDetector:
    def __init__(self):
        self.model = SentenceTransformer('paraphrase-MiniLM-L6-v2')
    
    def is_inferred(self, field_value: str, sources: List[str]) -> bool:
        field_emb = self.model.encode(field_value)
        for source in sources:
            source_emb = self.model.encode(source)
            similarity = cosine_similarity(field_emb, source_emb)
            if similarity > 0.8:  # 高度相似
                return False
        return True  # 推断
```

**工作量估算**：~300 lines

**优先级**: 🟡 P1（可用 embedding API）

---

## 🔶 High 问题（影响质量）

### H1. 设计方法文档 15/19 为框架

**问题描述**：
- `knowledge/design-work-paradigm/01-16-*.md` 为框架
- 缺少详细的方法说明
- 用户无法学习设计推理方法

**影响**：
- ⚠️ 文档不完整
- ⚠️ 用户无法理解设计思路
- ⚠️ 降低"资深设计师"标准的可信度

**修复方案**：
- **P4.1**: 补充设计方法文档
  - 每个方法 ~2000 words
  - 包含：原理、步骤、示例、常见错误

**工作量估算**：~15,000 words

**优先级**: 🟡 P1（文档完整性）

---

### H2. Professional Gap Report 评分为规则 based

**问题描述**：
- 9 维度评分为简单规则
- 未使用 ML 模型
- 评分可能不准确

**影响**：
- ⚠️ 质量评估不够智能
- ⚠️ 可能误判产物质量

**修复方案**：
- **P4.2**: 训练评分模型（长期）
  - 收集设计师评分数据
  - 训练 ML 模型
  - 替换规则 based 评分

**优先级**: 🟢 P2（长期优化）

---

### H3. 缺少人工复核界面

**问题描述**：
- professional_gap_report 只是 JSON
- 没有可视化界面
- 设计师难以复核

**影响**：
- ⚠️ 人工复核体验差
- ⚠️ 难以快速发现问题

**修复方案**：
- **P4.3**: 开发复核界面
  - 可视化 gap report
  - 高亮需复核的字段
  - 支持在线修改

**优先级**: 🟡 P1（用户体验）

---

### H4. 缺少版本管理

**问题描述**：
- reasoning_assets 无版本控制
- 无法回退到上一版本
- 无法对比不同版本

**影响**：
- ⚠️ 修改后无法撤销
- ⚠️ 无法追踪变更历史

**修复方案**：
- **P4.4**: 实现版本管理
  - 每次生成保存版本
  - 支持版本对比
  - 支持回退

**优先级**: 🟡 P1（企业级功能）

---

### H5. 缺少增量更新

**问题描述**：
- 修改 PRD 后需要重新执行全部
- 无法只更新受影响的部分
- 效率低

**影响**：
- ⚠️ 迭代效率低
- ⚠️ 浪费计算资源

**修复方案**：
- **P4.5**: 实现增量更新
  - 分析变更影响范围
  - 只重新执行受影响的 stages
  - 复用未变更的资产

**优先级**: 🟡 P1（效率优化）

---

### H6. 缺少协作功能

**问题描述**：
- 单人使用
- 无法多人协作
- 无法评论和讨论

**影响**：
- ⚠️ 团队协作困难
- ⚠️ 知识无法沉淀

**修复方案**：
- **P4.6**: 实现协作功能
  - 多人在线编辑
  - 评论和讨论
  - 权限管理

**优先级**: 🟢 P2（团队功能）

---

### H7. 缺少性能优化

**问题描述**：
- 顺序执行所有 stages
- 部分 stages 可并行
- 执行时间长

**影响**：
- ⚠️ 用户等待时间长
- ⚠️ 资源利用率低

**修复方案**：
- **P4.7**: 性能优化
  - 分析 stage 依赖关系
  - 并行执行无依赖的 stages
  - 缓存 LLM 结果

**优先级**: 🟡 P1（用户体验）

---

### H8. 缺少错误恢复

**问题描述**：
- LLM 调用失败后整个流程失败
- 无法从中间断点恢复
- 用户需要重新执行

**影响**：
- ⚠️ 稳定性差
- ⚠️ 用户体验差

**修复方案**：
- **P4.8**: 实现错误恢复
  - 保存中间结果
  - LLM 调用失败自动重试
  - 支持从断点继续

**优先级**: 🟡 P1（稳定性）

---

## 🟡 Medium 问题（降低体验）

### M1. 交互式补充体验粗糙

**问题描述**：
- CLI 交互体验差
- 缺少智能提示
- 缺少历史记录

**修复方案**：
- **P5.1**: 优化交互体验
  - Web UI 替代 CLI
  - 智能提示补充内容
  - 保存历史记录

**优先级**: 🟢 P2

---

### M2. PRD 升维模板过于简单

**问题描述**：
- 只有 4 个产品类型模板
- 模板内容较少
- 无法覆盖复杂场景

**修复方案**：
- **P5.2**: 丰富模板库
  - 增加更多产品类型
  - 模板更详细
  - 支持用户自定义模板

**优先级**: 🟢 P2

---

### M3. 缺少设计系统集成

**问题描述**：
- 无法导入 Figma Design System
- 无法使用企业组件库
- 生成的组件可能与规范不符

**修复方案**：
- **P5.3**: 设计系统集成
  - Figma API 集成
  - 导入企业组件库
  - 约束生成符合规范

**优先级**: 🟢 P2

---

### M4. 缺少多语言支持

**问题描述**：
- Prompts 为中文
- 不支持英文 PRD
- 国际化不足

**修复方案**：
- **P5.4**: 多语言支持
  - Prompts 英文版
  - 自动检测语言
  - 支持多语言切换

**优先级**: 🟢 P2

---

### M5. 缺少导出功能

**问题描述**：
- 产物只有 JSON
- 无法导出为 PDF/PPT
- 无法分享给非技术人员

**修复方案**：
- **P5.5**: 导出功能
  - 导出为 PDF
  - 导出为 PPT
  - 导出为 Figma

**优先级**: 🟢 P2

---

## 🟢 Low 问题（锦上添花）

### L1. 缺少 AI 对话界面

**修复方案**: P6.1 - 实现 AI 对话补充 PRD

**优先级**: ⚪ P3

---

### L2. 缺少学习模式

**修复方案**: P6.2 - 添加学习路径和教程

**优先级**: ⚪ P3

---

### L3. 缺少数据统计

**修复方案**: P6.3 - 统计使用数据和质量趋势

**优先级**: ⚪ P3

---

### L4. 缺少插件生态

**修复方案**: P6.4 - 支持第三方插件扩展

**优先级**: ⚪ P3

---

## 📈 修复进程（Roadmap）

### Phase 3: 核心功能完善（P3 - 2 周）

**目标**: 让系统"可用"

| 阶段 | 任务 | 工作量 | 优先级 |
|------|------|--------|--------|
| P3.1 | 补充 3 个核心 prompts | ~1800 lines | 🔴 P0 |
| P3.2 | 补充 6 个次要 prompts | ~3600 lines | 🔴 P0 |
| P3.3 | 补充剩余 7 个 prompts | ~4200 lines | 🔴 P0 |
| P3.4 | 实现 LLM 集成 | ~500 lines | 🔴 P0 |
| P3.5 | 真实场景测试 | 测试工作 | 🔴 P0 |
| P3.6 | 完善字段级追溯 | ~800 lines | 🔴 P0 |
| P3.7 | 实现真实代码解析 | ~400 lines | 🟡 P1 |
| P3.8 | 实现语义匹配 | ~300 lines | 🟡 P1 |

**Total**: ~11,600 lines + 测试

**完成后评分**: 85/100

---

### Phase 4: 质量与体验提升（P4 - 1 月）

**目标**: 让系统"好用"

| 阶段 | 任务 | 工作量 | 优先级 |
|------|------|--------|--------|
| P4.1 | 补充设计方法文档 | ~15,000 words | 🟡 P1 |
| P4.2 | 训练评分模型 | ML 工作 | 🟢 P2 |
| P4.3 | 开发复核界面 | ~2000 lines | 🟡 P1 |
| P4.4 | 实现版本管理 | ~800 lines | 🟡 P1 |
| P4.5 | 实现增量更新 | ~1000 lines | 🟡 P1 |
| P4.6 | 实现协作功能 | ~3000 lines | 🟢 P2 |
| P4.7 | 性能优化 | 优化工作 | 🟡 P1 |
| P4.8 | 错误恢复 | ~500 lines | 🟡 P1 |

**Total**: ~7,300 lines + 文档 + ML

**完成后评分**: 90/100

---

### Phase 5: 企业级打磨（P5 - 1 月）

**目标**: 让系统"企业级"

| 阶段 | 任务 | 优先级 |
|------|------|--------|
| P5.1 | 优化交互体验 | 🟢 P2 |
| P5.2 | 丰富模板库 | 🟢 P2 |
| P5.3 | 设计系统集成 | 🟢 P2 |
| P5.4 | 多语言支持 | 🟢 P2 |
| P5.5 | 导出功能 | 🟢 P2 |

**完成后评分**: 95/100

---

### Phase 6: 生态与扩展（P6 - 持续）

**目标**: 让系统"生态化"

| 阶段 | 任务 | 优先级 |
|------|------|--------|
| P6.1 | AI 对话界面 | ⚪ P3 |
| P6.2 | 学习模式 | ⚪ P3 |
| P6.3 | 数据统计 | ⚪ P3 |
| P6.4 | 插件生态 | ⚪ P3 |

**完成后评分**: 100/100

---

## 📊 工作量总估算

### 代码量
```
P3: ~11,600 lines
P4: ~7,300 lines  
P5: ~5,000 lines
P6: ~3,000 lines
────────────────
Total: ~27,000 lines
```

### 时间
```
P3: 2 周（核心功能）
P4: 1 月（质量提升）
P5: 1 月（企业级）
P6: 持续（生态）
────────────────
Total: ~3 月 → 企业级
```

---

## 🎯 建议执行顺序

### 立即执行（本周）

1. ✅ P3.1: 补充 3 个核心 prompts（user-task, IA, component）
2. ✅ P3.4: 实现 LLM 集成
3. ✅ P3.5: 用 1 个真实 PRD 测试

**目标**: 让 1 个完整流程跑通

---

### 短期执行（2 周）

4. ✅ P3.2-P3.3: 补充剩余 prompts
5. ✅ P3.6: 完善字段级追溯
6. ✅ P3.7-P3.8: 代码解析 + 语义匹配

**目标**: 功能完整，评分 85/100

---

### 中期执行（1 月）

7. ✅ P4.1-P4.8: 质量与体验提升

**目标**: 好用，评分 90/100

---

### 长期执行（2-3 月）

8. ✅ P5.1-P5.5: 企业级打磨
9. ✅ P6.1-P6.4: 生态化

**目标**: 企业级，评分 95-100/100

---

## ✅ 结论

### 当前状态
- **评分**: 75/100
- **问题**: 23 项（6 Critical + 8 High + 5 Medium + 4 Low）
- **工作量**: ~27,000 lines
- **时间**: ~3 月 → 企业级

### 最快路径（2 周 → 可用）
1. P3.1: 3 核心 prompts（~1800 lines）
2. P3.4: LLM 集成（~500 lines）
3. P3.5: 真实测试

**完成后**: 评分 80/100，可用但需人工复核

### 稳健路径（2 月 → 好用）
1. P3 全部（~11,600 lines）
2. P4 核心（P4.1, P4.3, P4.4, P4.5, P4.8）

**完成后**: 评分 90/100，好用且稳定

### 完美路径（3 月 → 企业级）
1. P3 + P4 + P5 全部

**完成后**: 评分 95/100，企业级

---

**你希望按哪个路径执行？**
