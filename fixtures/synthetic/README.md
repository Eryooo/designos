# Synthetic Fixtures

> **🚫 SYNTHETIC / SANITIZED ONLY** — 此目录只允许 synthetic / sanitized fixture。

## 规则

### ✅ 允许
- Synthetic PRD(如 Acme Demo 后台管理系统)
- Sanitized screenshot descriptions
- Generic input examples
- Abstracted scenarios

### ❌ 禁止
- 真实 PRD
- 真实截图(含敏感内容)
- 真实 URL
- 真实客户名 / 项目名
- 真实业务文案
- 真实账号 / token / password

## 真实材料去哪里?

真实材料**不进入仓库**,留在用户本地或 `<DESIGNOS_WORKSPACE_ROOT>/evidence/`(仅本地,不提交)。

## Synthetic Fixture 用途

- Dry-run replay
- 防回归测试
- 文档示例

## 从真实案例抽象规则

如果从真实案例抽象而来,必须:
1. 删除所有真实内容(行业细节、项目名、文案、字段值、链接、截图、数据)
2. 只保留结构性问题
3. 标记 `SYNTHETIC / SANITIZED`
4. 必须能复现 failure mode 或 gate 问题

## 示例

```yaml
# ✅ 正确 synthetic fixture
skill: prd2proto
prd_synthetic: |
  [synthetic] Acme Demo 管理后台
  目标用户:[synthetic] IT管理员

# ❌ 错误:含真实项目
skill: prd2proto
prd: |
  真实客户XYZ公司CRM系统  # 禁止
```
