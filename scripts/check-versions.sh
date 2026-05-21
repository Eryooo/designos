#!/usr/bin/env bash
# DesignOS 版本号一致性校验
# 用法：./scripts/check-versions.sh
# 退出码：0 = 全部一致，1 = 不一致

set -euo pipefail

REPO_ROOT="$(cd "$(dirname "$0")/.." && pwd)"

# 读取所有版本号位置
NPM_PKG_VER=$(node -p "require('${REPO_ROOT}/npm-package/package.json').version")
INSTALL_VER=$(grep '^VERSION=' "${REPO_ROOT}/npm-package/install.sh" | head -1 | cut -d'"' -f2)
SKILL_VER=$(python3 -c "import yaml; print(yaml.safe_load(open('${REPO_ROOT}/skills/uxeval/pipeline.yaml'))['version'])")

echo "版本号清单："
echo "  npm-package/package.json:        ${NPM_PKG_VER}"
echo "  npm-package/install.sh VERSION:  ${INSTALL_VER}"
echo "  skills/uxeval/pipeline.yaml:     ${SKILL_VER}（独立演进，仅警告）"
echo ""

# npm 包版本必须 == install.sh VERSION
if [[ "${NPM_PKG_VER}" != "${INSTALL_VER}" ]]; then
  echo "❌ 不一致：npm-package version (${NPM_PKG_VER}) ≠ install.sh VERSION (${INSTALL_VER})"
  echo "   修复：把 install.sh 第 19 行 VERSION=\"...\" 改成 ${NPM_PKG_VER}"
  exit 1
fi

# skill 版本独立演进，但 minor 升级时应该至少高于上一个 npm 包版本里捎带的 skill 版本
# 这里只警告不阻断
echo "✅ npm 包版本号一致：${NPM_PKG_VER}"
echo ""

# 检查 npm-package/skills/ 副本是否与主目录 skills/ 同步
DIFF=$(diff -rq "${REPO_ROOT}/skills/uxeval" "${REPO_ROOT}/npm-package/skills/uxeval" 2>&1 || true)
if [[ -n "${DIFF}" ]]; then
  echo "❌ npm-package/skills/uxeval 与 skills/uxeval 不一致："
  echo "${DIFF}" | head -10
  echo ""
  echo "   修复：执行 ./scripts/sync-skills.sh"
  exit 1
fi

echo "✅ npm-package/skills 副本已同步"
exit 0
