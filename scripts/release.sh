#!/usr/bin/env bash
# DesignOS 一键发布脚本
# 用法：./scripts/release.sh [patch|minor|major]
# 默认 minor（0.2.0 → 0.3.0）

set -euo pipefail

# ⚠️ internal pilot 安全闸：本脚本会 push 到远端并触发公网 npm 发布。
# 当前阶段（旧仓库历史未清理、旧 npm 包待 deprecate、不发公网包）禁止运行。
# 重新启用前请：改为内部/private registry，确认目标仓库，再移除本闸。
echo "⛔ release.sh 在 internal pilot 阶段已停用（防止误发公网 npm / 误推旧仓库）。"
echo "   见 INTERNAL-PILOT-README.md / REVIEW-MANIFEST.md。如确需发布，手动移除本闸。"
exit 1

REPO_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "${REPO_ROOT}"

BUMP_TYPE="${1:-minor}"

# ─── Step 1: 检查 git 状态 ───────────────────────────────────────────
echo "📋 Step 1: 检查 git 状态"
if [[ -n "$(git status --porcelain)" ]]; then
  echo "❌ 工作区不干净，请先 commit 或 stash"
  git status --short
  exit 1
fi
echo "✅ 工作区干净"

# ─── Step 2: 计算新版本号 ─────────────────────────────────────────────
echo ""
echo "📋 Step 2: 计算新版本号"
CURRENT_VER=$(node -p "require('./npm-package/package.json').version")
echo "   当前版本：${CURRENT_VER}"

# 手动 semver bump（不依赖 npm version 命令）
IFS='.' read -r MAJOR MINOR PATCH <<< "${CURRENT_VER}"
case "${BUMP_TYPE}" in
  patch) PATCH=$((PATCH + 1)) ;;
  minor) MINOR=$((MINOR + 1)); PATCH=0 ;;
  major) MAJOR=$((MAJOR + 1)); MINOR=0; PATCH=0 ;;
  *) echo "❌ 无效参数：${BUMP_TYPE}（可选 patch/minor/major）"; exit 1 ;;
esac
NEW_VER="${MAJOR}.${MINOR}.${PATCH}"
echo "   新版本：${NEW_VER}（${BUMP_TYPE}）"
echo ""

read -p "确认发布 ${NEW_VER}？(y/N) " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
  echo "取消发布"
  exit 0
fi

# ─── Step 3: 更新所有版本号位置 ───────────────────────────────────────
echo ""
echo "📋 Step 3: 更新版本号"

# 3a. npm-package/package.json
sed -i '' "s/\"version\": \"${CURRENT_VER}\"/\"version\": \"${NEW_VER}\"/" npm-package/package.json
echo "   ✅ npm-package/package.json → ${NEW_VER}"

# 3b. npm-package/install.sh
sed -i '' "s/^VERSION=\".*\"/VERSION=\"${NEW_VER}\"/" npm-package/install.sh
echo "   ✅ npm-package/install.sh → ${NEW_VER}"

# 3c. skills/uxeval/pipeline.yaml（skill 版本跟随 npm 包版本）
sed -i '' "s/^version: .*/version: ${NEW_VER}/" skills/uxeval/pipeline.yaml
echo "   ✅ skills/uxeval/pipeline.yaml → ${NEW_VER}"

# ─── Step 4: 同步 skills → npm-package/skills ────────────────────────
echo ""
echo "📋 Step 4: 同步 skills 副本"
bash scripts/sync-skills.sh

# ─── Step 5: 版本号一致性校验 ─────────────────────────────────────────
echo ""
echo "📋 Step 5: 版本号一致性校验"
bash scripts/check-versions.sh

# ─── Step 6: commit + tag ─────────────────────────────────────────────
echo ""
echo "📋 Step 6: 提交并打 tag"
git add -A
git commit -m "chore: release v${NEW_VER}

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>"
git tag "v${NEW_VER}"
echo "   ✅ commit + tag v${NEW_VER}"

# ─── Step 7: push（触发 CI 自动 npm publish）──────────────────────────
echo ""
echo "📋 Step 7: 推送到 GitHub"
git push origin main
git push origin "v${NEW_VER}"
echo "   ✅ 已推送 main + tag v${NEW_VER}"

# ─── Step 8: 等待 CI 发布（或手动 publish）────────────────────────────
echo ""
echo "📋 Step 8: 发布到 npm"
echo "   GitHub Actions 会自动 npm publish（监听 tag v*）"
echo "   如果 CI 未配置 NPM_TOKEN，手动执行："
echo "   cd npm-package && npm publish --registry=<YOUR_INTERNAL_REGISTRY>"
echo ""

# ─── Step 9: 验证 ────────────────────────────────────────────────────
echo "📋 Step 9: 验证（等 CI 完成后执行）"
echo "   npm view <YOUR_INTERNAL_PACKAGE>@latest version --registry=<YOUR_INTERNAL_REGISTRY>"
echo "   预期输出：${NEW_VER}"
echo ""
echo "🎉 发布完成！用户执行 npx <YOUR_INTERNAL_PACKAGE> 即可拿到 v${NEW_VER}"
