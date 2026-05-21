#!/usr/bin/env bash
# 同步 skills/* → npm-package/skills/*
# 用法：./scripts/sync-skills.sh

set -euo pipefail

REPO_ROOT="$(cd "$(dirname "$0")/.." && pwd)"

echo "🔄 同步 skills/ → npm-package/skills/"
rm -rf "${REPO_ROOT}/npm-package/skills"
cp -r "${REPO_ROOT}/skills" "${REPO_ROOT}/npm-package/skills"

echo "✅ 同步完成"
diff -rq "${REPO_ROOT}/skills" "${REPO_ROOT}/npm-package/skills" >/dev/null && echo "✅ 副本与主目录完全一致"
