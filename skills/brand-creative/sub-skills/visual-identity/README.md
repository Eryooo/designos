# visual-identity

品牌视觉识别系统聚合子技能。

## 快速定位

- **职责**：聚合 logo-design / color-system / typography-system 三者产出，做一致性判断，产出 VI 手册
- **不做**：不重新生成 logo / 色彩 / 字体，不覆盖上游产物
- **输入**：visual_spec + color_palette + typography_spec（全部来自上游）
- **输出**：vi_manual（对齐 vi_manual.schema.json）

## 使用方式

通过 SkillLoader 加载：`brand-creative:visual-identity`

### 前置条件

必须先完成以下三个子技能：
1. `brand-creative:logo-design` → 产出 visual_spec
2. `brand-creative:color-system` → 产出 color_palette
3. `brand-creative:typography-system` → 产出 typography_spec

### 典型 workflow 位置

```
brand-strategy → [logo-design | color-system | typography-system](parallel) → visual-identity(sequential)
```

## Pipeline 结构

| Stage | 职责 | 输出 |
|---|---|---|
| integrate_visual_system | 三者一致性检查 + 冲突识别 + 警告继承 | integration_analysis |
| generate_vi_manual | 聚合产出 VI 手册 | vi_manual |

## 核心判断维度

1. **气质一致性**：logo 形态 / color 情绪 / typography 气质 是否指向同一品牌人格
2. **技术兼容性**：色彩引用 / 尺寸兼容 / 跨端覆盖 是否同步
3. **缺口诚实声明**：上游警告全部继承，不吞掉

## 能力边界

- 不声称最终商用、不声称商标已确认、不声称字体授权已确认、不声称印刷色已验证
- 不覆盖上游产物、不重新生成视觉方案

## 测试

```bash
PYTHONPATH="$PWD" python3 -m pytest -q skills/brand-creative/sub-skills/visual-identity/tests/ --import-mode=importlib
```
