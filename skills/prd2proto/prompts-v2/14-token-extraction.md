# Prompt: 14 Design Tokens提取 (Design Tokens Extraction)

**状态**: ✅ COMPLETE (Capability Pilot v1.0 - 框架级，本轮不做完整生成)  
**Stage**: token-extraction  
**Output**: design_tokens.json (W3C DTCG格式)

---

## 1. Stage Role

你是资深Design Tokens工程师。任务是从design-spec/DSL/组件库主题中**提取标准化Design Tokens**，输出W3C格式。

注意：本轮P0为**框架级实现**，不做完整DSL解析（属于P3批次范围）。pm模式可使用组件库默认主题+少量定制。

## 2. Senior Reasoning Model

**核心命题**: 标准化Token = 多端一致+主题切换基础

### Token分类（W3C标准）

| 类别 | 子项 | 示例值 |
|------|------|-------|
| **color** | brand/text/bg/border/state | brand.primary: #1890FF |
| **typography** | family/size/weight/line-height | size.body: 14px |
| **spacing** | 4/8/12/16/24/32/48 | md: 16px |
| **borderRadius** | sm/md/lg/full | md: 8px |
| **shadow** | sm/md/lg | md: 0 2px 8px rgba(0,0,0,0.1) |
| **opacity** | disabled/overlay | disabled: 0.4 |
| **motion** | duration/easing | normal: 200ms |

### Token命名规范

`{category}.{semantic}.{variant}`：
- `color.brand.primary` ✅（语义化）
- `color.blue.500` ⚠️（仅作primitive）
- `color.btn-primary-bg` ❌（过于具体）

---

## 3. Required Upstream Inputs

| 输入 | 来源 | 必需 |
|------|------|------|
| `design_spec_md` | 用户提供或Stage 13 | ⭕ |
| `dsl_tree` | DSL输入（仅designer-dsl） | ❌ pm模式不需要 |
| `component_lib` | Stage 10 | ✅ |

---

## 4. Required Output (W3C DTCG格式)

```json
{
  "$schema": "https://design-tokens.github.io/community-group/format/",
  
  "color": {
    "brand": {
      "primary": {"$value": "#1890FF", "$type": "color"},
      "primary-hover": {"$value": "#096DD9", "$type": "color"},
      "primary-active": {"$value": "#0050B3", "$type": "color"}
    },
    "text": {
      "primary": {"$value": "#000000d9", "$type": "color"},
      "secondary": {"$value": "#00000073", "$type": "color"},
      "disabled": {"$value": "#00000040", "$type": "color"}
    },
    "bg": {
      "default": {"$value": "#ffffff", "$type": "color"},
      "secondary": {"$value": "#fafafa", "$type": "color"}
    },
    "border": {
      "default": {"$value": "#d9d9d9", "$type": "color"}
    },
    "state": {
      "success": {"$value": "#52c41a", "$type": "color"},
      "warning": {"$value": "#faad14", "$type": "color"},
      "error": {"$value": "#f5222d", "$type": "color"}
    }
  },

  "typography": {
    "family": {
      "default": {"$value": "PingFang SC, sans-serif", "$type": "fontFamily"}
    },
    "size": {
      "h1": {"$value": "24px", "$type": "fontSize"},
      "h2": {"$value": "20px", "$type": "fontSize"},
      "body": {"$value": "14px", "$type": "fontSize"},
      "caption": {"$value": "12px", "$type": "fontSize"}
    },
    "weight": {
      "regular": {"$value": "400", "$type": "fontWeight"},
      "medium": {"$value": "500", "$type": "fontWeight"},
      "bold": {"$value": "600", "$type": "fontWeight"}
    },
    "lineHeight": {
      "tight": {"$value": "1.2", "$type": "number"},
      "normal": {"$value": "1.5", "$type": "number"}
    }
  },

  "spacing": {
    "xs": {"$value": "4px", "$type": "spacing"},
    "sm": {"$value": "8px", "$type": "spacing"},
    "md": {"$value": "16px", "$type": "spacing"},
    "lg": {"$value": "24px", "$type": "spacing"},
    "xl": {"$value": "32px", "$type": "spacing"}
  },

  "borderRadius": {
    "sm": {"$value": "4px", "$type": "borderRadius"},
    "md": {"$value": "8px", "$type": "borderRadius"},
    "lg": {"$value": "12px", "$type": "borderRadius"}
  },

  "_metadata": {
    "source": "antd@5 default theme + small customization",
    "design_spec_provided": false,
    "mode": "pm",
    "p0_status": "framework_level"
  }
}
```

## 5. Decision Rules

1. 语义化命名（不是primitive值）
2. 覆盖7类Token
3. 与组件库主题对齐
4. design-spec提供时严格遵守

## 6. Quality Self-Check

- [ ] 7类Token齐全
- [ ] 命名语义化
- [ ] 与组件库一致
- [ ] _metadata标注mode

## 7. P0范围说明

**本轮（P0）**：框架级输出（基于组件库默认+design-spec）  
**未来（P3）**：真实DSL提取（Figma/MasterGo MCP）

**v1.0.0-complete (2026-06-10)**
