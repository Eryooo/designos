# Excel Builder MCP Server

Excel 报告生成 MCP Server，为 DesignOS 提供结构化问题报告的 Excel 导出能力。

## 功能

提供 `build_issue_report` 工具，支持三种报告模板：

### 1. uxeval 模板（3 个 sheet）
- **问题清单**：ID / 标题 / 严重等级 / 原则 / 描述 / 证据 / 建议
- **摘要**：按严重等级聚合问题数量
- **原则覆盖**：按启发式原则聚合问题数量

### 2. design-acceptance 模板（3 个 sheet）
- **差异清单**：ID / 页面 / 差异类型 / 设计值 / 实现值 / 偏差量
- **页面汇总**：按页面聚合问题数量
- **组件汇总**：按组件聚合问题数量

### 3. competitor 模板（2 个 sheet）
- **功能对比矩阵**：多产品功能对比表
- **维度评分**：多维度评分对比

## 特性

- 中文内容正确显示（无乱码）
- 严重等级颜色标记：critical=红 / major=橙 / minor=黄 / suggestion=灰
- 列宽自动调整（上限 50 字符）
- 表头加粗 + 浅蓝背景
- 文件已存在时自动覆盖

## 安装

```bash
cd mcp-servers/excel-builder
pip install -e .
```

## 开发

```bash
# 安装开发依赖
pip install -e ".[dev]"

# 运行测试
pytest tests/ -v
```

## 使用示例

```python
from core import build_issue_report

issues = [
    {
        "id": "I-001",
        "title": "登录按钮位置不明显",
        "severity": "critical",
        "principle_ids": ["H1", "H4"],
        "description": "用户在首页找不到登录入口",
        "evidence_refs": ["E-001"],
        "suggestion": "将登录按钮移至页面中心",
        "user_impact": "用户无法快速找到登录入口",
    }
]

result = build_issue_report(
    issues=issues,
    output_dir="/path/to/run/outputs",
    template="uxeval",
)

print(f"Excel: {result['issue_report']['path']}")
print(f"HTML: {result['html_report']['path']}")
print(f"Evidence: {result['evidence_pack']['path']}")
```

## MCP 工具接口

### build_issue_report

**输入**：
```json
{
  "issues": [
    {
      "id": "string",
      "title": "string",
      "severity": "critical|major|minor|suggestion",
      "principle_ids": ["string"],
      "description": "string",
      "evidence_refs": ["string"],
      "suggestion": "string",
      "user_impact": "string"
    }
  ],
  "output_path": "string | null",
  "output_dir": "string | null",
  "template": "uxeval|design-acceptance|competitor",
  "journey_map": "object | null",
  "principles": "array | object | null"
}
```

**输出**：
```json
{
  "issue_report": {
    "id": "issue_report",
    "type": "issue_report",
    "path": "string",
    "format": "xlsx",
    "summary": "string",
    "sheet_count": 3
  },
  "html_report": {
    "id": "html_report",
    "type": "html_report",
    "path": "string",
    "format": "html",
    "summary": "string"
  },
  "evidence_pack": {
    "id": "evidence_pack",
    "type": "evidence_pack",
    "path": "string",
    "format": "directory",
    "summary": "string"
  }
}
```

## 错误处理

- `ExcelBuilderError`: 模板未知、路径无效、issues 列表为空（部分模板）

## 依赖

- `mcp>=1.0.0`: MCP 协议支持
- `openpyxl>=3.1.0`: Excel 文件生成
- `pydantic>=2.0.0`: 数据验证

## 许可

Apache 2.0
