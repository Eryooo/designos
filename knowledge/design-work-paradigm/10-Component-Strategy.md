# 10. 组件策略 (Component Strategy)

> **方法论级别**: Senior Designer Standard  
> **核心命题**: 80%复用标准组件，20%定制关键场景

## 定义与目的

组件策略是决定何时使用组件库标准组件、何时定制、如何保持一致性的方法。

### 资深 vs 初级

**初级**：全用标准组件（不适配）或全定制（不一致）  
**资深**：80%标准组件，20%关键场景定制，保持设计系统一致

核心要素：组件库选型、复用 vs 定制、状态完整性、变体管理

## 适用场景

- ✅ 使用组件库的项目（Ant Design/Material）
- ✅ 需要保持视觉一致性
- ✅ 有设计系统的团队
- ⚠️ 极简项目可简化
- ❌ 纯品牌创意项目

## 推理过程

### Step 1: 选择组件库
Ant Design（B端）/Material（通用）/自研（品牌强）

### Step 2: 识别标准场景
表单/表格/按钮/弹窗 → 用标准组件

### Step 3: 识别定制场景
核心差异化功能、品牌特色、特殊交互

### Step 4: 设计组件状态
default/hover/active/disabled/loading/error

### Step 5: 建立变体规范
size(large/medium/small), type(primary/default/ghost)

## 质量标准

### Must Have
1. ✅ 组件库选型有依据
2. ✅ 标准组件覆盖率 > 80%
3. ✅ 定制组件有必要性说明
4. ✅ 所有组件状态完整
5. ✅ 组件变体有规范

## 失败模式

### FM-1: 滥用标准组件
不适配场景也硬套，体验差

### FM-2: 过度定制
每个地方都定制，不一致且成本高

### FM-3: 状态不全
只设计正常状态，忘记disabled/loading

### FM-4: 变体混乱
同一类组件有多种尺寸/颜色，无规范

## Anti-Patterns

1. ❌ 全标准或全定制
2. ❌ 不考虑适配性
3. ❌ 状态缺失
4. ❌ 变体无规范
5. ❌ 不遵循设计系统
6. ❌ 重复造轮子
7. ❌ 定制理由不充分
8. ❌ 未来扩展性差

## 与其他方法的关系

- **上游依赖**：09-content-structure
- **下游消费**：11-state-matrix, 12-interaction-rules

## 实例：表单提交按钮

**Junior**：
- 方案A：直接用 Ant Design Button，所有表单一样
- 方案B：每个表单都定制按钮样式

**Senior**：
- 标准场景：80%表单用 Ant Design Primary Button
- 定制场景：关键转化页面（支付/注册）定制大按钮+渐变色
- 状态：default(蓝)/hover(深蓝)/active(更深)/disabled(灰)/loading(转圈)
- 变体：size(large 48px/medium 40px/small 32px)

## 版本历史

- **v1.0.0** (2026-06-09): 资深设计师级别完整方法论
