# DesignOS MVP Release Checklist

> 发布前必须逐项检查，确保质量与安全。

## 1. Git 状态检查

### 1.1 分支确认
```bash
git branch --show-current
# 预期: skills-pilot-wave2
```

### 1.2 无脏文件
```bash
git status --short
# 预期: 干净（除非有待提交的 MVP freeze 文档）
```

### 1.3 提交历史确认
```bash
git log --oneline -12
# 预期: 最新 commit 为 B1.3 (c60fa1e) 或 MVP freeze commit
```

### 1.4 无空白问题
```bash
git diff --check
# 预期: 无输出（无尾随空白/混合缩进/冲突标记）
```

### 1.5 backlog 分支隔离
```bash
git branch | grep factory-and-prd2proto-p1
# 确认: factory-and-prd2proto-p1 存在但不参与本次发布
```

---

## 2. 测试检查

### 2.1 brand-creative 全量测试
```bash
PYTHONPATH="$PWD" python3 -m pytest -q \
  skills/brand-creative/tests/ \
  skills/brand-creative/sub-skills/logo-design/tests/ \
  skills/brand-creative/sub-skills/color-system/tests/ \
  skills/brand-creative/sub-skills/typography-system/tests/ \
  skills/brand-creative/sub-skills/visual-identity/tests/ \
  tests/integration/test_brand_creative_visual_parallel_runtime.py \
  --import-mode=importlib
```
**预期**: 71 passed

### 2.2 kernel + foundation 测试
```bash
PYTHONPATH="$PWD" python3 -m pytest -q \
  tests/unit/test_stage_field_compliance.py \
  tests/unit/test_kernel_skill_loader.py \
  tests/unit/test_kernel_orchestrator.py \
  tests/integration/test_brand_creative_foundation_runtime.py \
  --import-mode=importlib
```
**预期**: 25 passed

### 2.3 其他 skill 回归测试
```bash
PYTHONPATH="$PWD" python3 -m pytest -q \
  skills/ip-design/tests/ \
  skills/prd2proto/tests/ \
  skills/ai-analytics/tests/ \
  --import-mode=importlib
```
**预期**: 101 passed

### 2.4 factory 测试
```bash
cd .factory && python3 -m pytest tests/ -q
```
**预期**: 61 passed, 1 warning（既有 warning，非 blocker）

### 2.5 archetype 验证
```bash
cd .factory
python3 -m tools.validate ../skills/uxeval --archetype evaluation
python3 -m tools.validate ../skills/prd2proto --archetype generation
python3 -m tools.validate ../skills/ai-analytics --archetype analysis
python3 -m tools.validate ../skills/ip-design --archetype creative-generation
```
**预期**: 4/4 All checks passed

---

## 3. Skill Validate 检查

### 3.1 SkillLoader 可加载所有 MVP skill
```python
from kernel.skill_loader import SkillLoader
loader = SkillLoader(["./skills"])

# 加载所有 MVP skill
skills = [
    "uxeval",
    "prd2proto",
    "ai-analytics",
    "ip-design",
    "brand-creative",
    "brand-creative:brand-strategy",
    "brand-creative:competitive-analysis",
    "brand-creative:logo-design",
    "brand-creative:color-system",
    "brand-creative:typography-system",
    "brand-creative:visual-identity",
]

for skill_id in skills:
    skill = loader.load(skill_id)
    print(f"✓ {skill_id} loaded")
```
**预期**: 所有 skill 可加载

### 3.2 所有 pipeline.yaml 结构合规
- stage.knowledge 必须在 stage 级别（非顶层）
- 无 StageConfig 不支持字段（description/purpose/config/model/temperature/output_format）
- 所有 knowledge 路径真实存在

---

## 4. npm 发布安全检查

### 4.1 package.json 检查
```bash
cat package.json  # 或 npm-package/package.json
```
**确认**:
- 无敏感信息（token / 密钥 / 内部 URL）
- version 字段正确（待用户确认版本号）
- main / bin 入口正确
- dependencies 版本锁定

### 4.2 npm token 安全
```bash
npm whoami
# 确认当前 npm 账号
```
**警告**: npm token 需妥善保管，不建议在公共 CI 中暴露。

### 4.3 .npmignore 检查
```bash
cat .npmignore
```
**确认**: 排除了 `.claude/` / `tests/` / `__pycache__` / `.env` 等无需发布文件。

### 4.4 npm pack 预览
```bash
npm pack --dry-run
# 预览将发布的文件清单
```
**确认**: 无意外包含的敏感文件。

---

## 5. 版本号检查

### 5.1 当前版本号
```bash
# 检查多个版本源
grep '"version"' package.json | head -1
grep 'version' pyproject.toml | head -1
grep '__version__' designos/__init__.py | head -1
```
**当前**: 0.5.0（待确认）

### 5.2 建议版本号
**选项 1**: `0.6.0` — 新的 minor 版本（推荐）  
**选项 2**: `0.6.0-mvp-trial` — 明确标注 MVP 试用版  
**选项 3**: `0.5.1` — 小版本更新（若 0.5.0 已发布且稳定）

**等待用户确认版本号，不要擅自修改。**

---

## 6. Tag 检查

### 6.1 确认无重复 tag
```bash
git tag | grep v0.6.0
# 预期: 无输出（tag 尚未创建）
```

### 6.2 tag 命名规范
**推荐**: `v0.6.0` 或 `v0.6.0-mvp-trial`  
**不推荐**: `mvp` / `release` / `试用版`（不符合语义化版本）

### 6.3 tag 创建命令（待用户确认后执行）
```bash
git tag -a v0.6.0 -m "DesignOS MVP trial baseline"
git push origin v0.6.0
```

---

## 7. npx 安装验证

### 7.1 本地验证（发布前）
```bash
npm link
npx <YOUR_INTERNAL_PACKAGE> --version
# 预期: 显示版本号
```

### 7.2 发布后验证（发布后）
```bash
npx <YOUR_INTERNAL_PACKAGE>
designos --version
# 预期: 0.6.0
```

### 7.3 冒烟测试
```bash
# 尝试加载一个 skill
designos uxeval --help
# 预期: 显示帮助信息，无报错
```

---

## 8. 回滚方案

### 8.1 git 回滚
```bash
# 若发现问题，回退到上一个稳定 commit
git reset --hard <上一个稳定 commit>
git push origin skills-pilot-wave2 --force
```
**警告**: `--force` 会覆盖远端历史，需团队确认。

### 8.2 npm 回滚
```bash
# 若已发布到 npm 但有问题
npm unpublish designos@0.6.0
# 或发布修复版本 0.6.1
```
**限制**: npm unpublish 有时间窗口限制（72 小时内）。

### 8.3 tag 回滚
```bash
# 删除本地 tag
git tag -d v0.6.0
# 删除远端 tag
git push origin :refs/tags/v0.6.0
```

---

## 9. Token / Supply Chain 风险提醒

### 9.1 npm token 风险
- ❌ 不要在公共 repo / CI 日志中暴露 npm token
- ✅ 使用 GitHub Secrets 或本地环境变量
- ✅ 定期轮换 token

### 9.2 依赖供应链风险
- ✅ 使用 `package-lock.json` 锁定依赖版本
- ✅ 定期运行 `npm audit` 检查漏洞
- ❌ 不要使用 `^` / `~` 宽松版本范围（生产环境）

### 9.3 代码签名（可选）
```bash
git config --global user.signingkey <GPG key>
git tag -s v0.6.0 -m "DesignOS MVP trial baseline"
```

---

## 10. 禁止提交文件最终检查

### 10.1 禁止文件清单
```bash
git status --short | grep -E "settings\.local\.json|designos/__init__\.py|__pycache__|\.pyc|\.env|\.DS_Store"
```
**预期**: 无输出（或仅 MVP freeze 文档）

### 10.2 精确提交
```bash
# 不要使用 git add .
# 精确 add 每个文件
git add docs/releases/designos-mvp-freeze/README.md
git add docs/releases/designos-mvp-freeze/mvp_manifest.json
git add docs/releases/designos-mvp-freeze/known_limits.md
git add docs/releases/designos-mvp-freeze/internal_trial_guide.md
git add docs/releases/designos-mvp-freeze/release_checklist.md
git add README.md  # 如有修改
git add CHANGELOG.md  # 如有修改
```

---

## 11. 最终 Checklist

### 必须完成（发布前）
- [ ] Git 状态检查通过（分支正确/无脏文件/无空白问题）
- [ ] 258 tests passed（71 + 25 + 101 + 61）
- [ ] 4/4 archetype 验证通过
- [ ] 所有 MVP skill 可通过 SkillLoader 加载
- [ ] package.json 无敏感信息
- [ ] .npmignore 正确配置
- [ ] npm pack 预览无意外文件
- [ ] 版本号已确认（待用户确认）
- [ ] 禁止文件未被提交
- [ ] MVP freeze 文档已生成（5 个文件）

### 可选（发布后）
- [ ] README.md 更新（最小必要更新）
- [ ] CHANGELOG.md 更新（Unreleased / MVP candidate）
- [ ] tag 已创建并推送
- [ ] npm 已发布
- [ ] npx 安装验证通过
- [ ] 回滚方案已准备

### 等待用户确认
- [ ] 是否推送 skills-pilot-wave2
- [ ] 是否开 PR 合并 main
- [ ] 是否更新版本号（建议 0.6.0）
- [ ] 是否打 tag（v0.6.0 或 v0.6.0-mvp-trial）
- [ ] 是否发布 npm

---

## 12. 发布流程建议

### 阶段 1: 冻结基线（当前）
1. ✅ 生成 MVP freeze 文档（5 个文件）
2. ✅ 提交 MVP freeze 文档
3. ⏸️ 暂不推送，等待用户确认

### 阶段 2: 推送与 PR（待用户确认）
1. `git push origin skills-pilot-wave2`
2. 开 PR: `skills-pilot-wave2` → `main`
3. PR 标题: "feat: DesignOS MVP trial baseline (B1.1-B1.3)"
4. PR 描述: 包含 MVP manifest / known limits / trial guide 链接

### 阶段 3: 合并与 tag（待用户确认）
1. PR 通过后合并到 main
2. `git checkout main && git pull`
3. `git tag -a v0.6.0 -m "DesignOS MVP trial baseline"`
4. `git push origin v0.6.0`

### 阶段 4: npm 发布（待用户确认）
1. 更新 package.json version 为 `0.6.0`
2. internal pilot 阶段**不发公网**：`npm publish --registry=<YOUR_INTERNAL_REGISTRY>`（或 `--access restricted`）
3. 验证: `npx <YOUR_INTERNAL_PACKAGE>`

---

**当前状态**: 阶段 1 完成，等待用户确认后进入阶段 2。
