# DesignOS 发布流程

## 发布前 Checklist

- [ ] `CHANGELOG.md` 已更新，包含本次版本的变更说明
- [ ] 所有测试通过：`uv run pytest`
- [ ] Lint 通过：`uv run ruff check .`
- [ ] 类型检查通过：`uv run pyright`
- [ ] 版本号已 bump（`pyproject.toml` 中的 `version`）
- [ ] 本地 build 成功：`uv build`
- [ ] wheel 内容验证通过（含 skills/ mcp-servers/ AGENTS.md）
- [ ] git tag 已打：`git tag v<version>`

## 版本管理约定

遵循 [SemVer 2.0](https://semver.org/)：

- **MAJOR**（1.0.0）：不兼容的 API 变更
- **MINOR**（0.2.0）：向后兼容的新功能
- **PATCH**（0.1.1）：向后兼容的 bug 修复

当前处于 `0.x` 阶段，MINOR 版本可包含破坏性变更。

## 本地发布到 TestPyPI

```bash
# 1. 确保 build 干净
rm -rf dist/
uv build

# 2. 验证 wheel 内容
unzip -l dist/designos-*.whl | grep "_bundled"

# 3. 上传到 TestPyPI（需要 API token）
uv publish --publish-url https://test.pypi.org/legacy/

# 4. 验证安装
pip install --index-url https://test.pypi.org/simple/ designos
```

## 生产发布（推荐：通过 CI）

### 方式一：Tag 触发（推荐）

```bash
# 1. Bump version in pyproject.toml
# 2. Commit
git add pyproject.toml CHANGELOG.md
git commit -m "release: v0.2.0"

# 3. Tag and push
git tag v0.2.0
git push origin main --tags
```

CI 会自动：build -> verify -> publish to PyPI -> create GitHub Release。

### 方式二：手动触发

在 GitHub Actions 页面选择 `Publish to PyPI` workflow，点击 "Run workflow"，
选择 target（testpypi 或 pypi）。

## 回滚步骤

PyPI 不支持覆盖已发布版本，回滚方式：

1. **yank 有问题的版本**（标记为不推荐，但不删除）：
   ```bash
   # 在 PyPI 项目页面操作，或用 API
   # https://pypi.org/manage/project/designos/releases/
   ```

2. **发布修复版本**：
   ```bash
   # Bump patch version
   # e.g., 0.2.0 有问题 -> 发布 0.2.1
   ```

3. **紧急情况**：联系 PyPI support 删除版本（极少使用）。

## GitHub Trusted Publishing 配置

首次发布前需在 PyPI 配置 OIDC：

1. 登录 https://pypi.org，进入项目 `designos` 的 Publishing 设置
2. 添加 "GitHub" publisher：
   - Owner: `Eryooo`
   - Repository: `designos`
   - Workflow: `publish.yml`
   - Environment: `pypi`
3. 对 TestPyPI 重复上述步骤（environment 填 `testpypi`）
