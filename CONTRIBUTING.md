# 贡献指南

感谢你对 DesignOS 的关注！我们欢迎各种形式的贡献。

## 如何贡献

### 报告 Bug
在提交 Issue 前，请先搜索现有 Issue 避免重复。报告时请包含：
- 复现步骤
- 预期行为 vs 实际行为
- 环境信息（OS、Python 版本、AI 助手版本）
- 错误日志或截图

### 提出功能建议
欢迎在 Issues 中提出新功能建议。请说明：
- 使用场景与痛点
- 期望的行为
- 是否愿意参与开发

### 提交代码

#### 开发环境设置

```bash
# 克隆仓库
git clone <YOUR_INTERNAL_PRIVATE_REPO>.git
cd designos

# 安装开发依赖
pip install -e ".[dev]"

# 运行测试
pytest

# 代码检查
ruff check .
pyright
```

#### 开发流程

1. **Fork 仓库并创建分支**
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. **编写代码**
   - 遵循现有代码风格
   - 为新功能添加测试
   - 更新相关文档

3. **运行质量检查**
   ```bash
   # 代码格式检查
   ruff check .
   
   # 类型检查
   pyright
   
   # 运行测试
   pytest
   ```

4. **提交变更**
   - 遵循 [Conventional Commits](https://www.conventionalcommits.org/) 规范
   - 示例：
     ```
     feat(uxeval): add support for Figma screenshots
     fix(brand-creative): resolve color contrast calculation
     docs(readme): update installation instructions
     ```

5. **推送并创建 Pull Request**
   ```bash
   git push origin feature/your-feature-name
   ```
   
   在 PR 描述中说明：
   - 改动的内容与原因
   - 测试结果
   - 是否有 breaking changes

#### 代码规范

- **Python 代码**：遵循 PEP 8，使用 ruff 自动格式化
- **类型注解**：所有公共 API 必须有完整类型注解
- **测试覆盖**：新功能需要单元测试，Bug 修复需要回归测试
- **文档更新**：API 变更需同步更新 AGENTS.md

#### 测试要求

```bash
# 运行全部测试
pytest

# 运行特定测试
pytest tests/unit/test_uxeval.py

# 查看覆盖率
pytest --cov=designos
```

所有 PR 必须通过 CI 检查：
- ✅ Lint (ruff)
- ✅ Type check (pyright)
- ✅ Unit tests (pytest)

### 添加新 Skill

如果你想贡献新的 skill：

1. **在 `skills/<skill-name>/` 创建目录结构**：
   ```
   skills/your-skill/
   ├── SKILL.md              # 元数据（必需）
   ├── pipeline.yaml         # 执行流程（必需）
   ├── knowledge-manifest.yaml  # 知识库清单（必需）
   ├── prompts/              # Prompt 模板
   ├── reference/            # 参考文档
   └── tests/                # 测试用例
   ```

2. **在 SKILL.md 中声明版本号与依赖**：
   ```yaml
   ---
   name: your-skill
   version: 0.1.0
   description: 简短描述
   ---
   ```

3. **编写 pipeline.yaml**：
   定义执行阶段、输入输出、依赖关系

4. **添加测试**：
   至少包含 smoke test 与集成测试

5. **更新 README.md**：
   在"核心技能"章节添加说明

## 发布流程

由维护者负责发布：

1. 更新版本号（`npm-package/package.json` + `pyproject.toml` + `designos/__init__.py`）
2. 更新 CHANGELOG.md
3. 创建 git tag：`git tag -a v0.x.0 -m "Release v0.x.0"`
4. 推送 tag：`git push origin v0.x.0`
5. 发布：internal pilot 阶段**不发公网 npm**；改走内部/private/scoped registry
   （`npm publish --registry=<YOUR_INTERNAL_REGISTRY>` 或 `--access restricted`）

## 行为准则

- 尊重所有贡献者
- 建设性地提出反馈
- 专注于技术讨论，避免人身攻击
- 欢迎新手，耐心解答问题

## 许可证

贡献的代码将以 Apache 2.0 许可证发布。

## 问题？

有任何疑问请在 [Discussions](<YOUR_INTERNAL_PRIVATE_REPO>/discussions) 提出，或通过 Issues 联系我们。
