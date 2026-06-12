#!/usr/bin/env bash
# DesignOS 新仓库初始化脚本（clean snapshot → 新 private repo）
#
# 用法：
#   1. 在 GitHub 新建一个 PRIVATE 仓库（不要 init README）
#   2. 在本 snapshot 目录下运行： bash NEW-REPO-INIT.sh
#   3. 按提示 gh auth login → git remote add origin <URL> → git push
#
# 安全：
#   - 不要在 URL 里硬编码 token。先 `gh auth login` 或配置
#     git credential helper / SSH，push 时自动用凭证。
#   - 本脚本默认【不执行 push】，需你手动取消最后注释或单独跑。

set -euo pipefail

# ---- 0. 前置确认（防止在错误目录运行）----
if [ -d ".git" ]; then
  echo "⚠️  当前目录已有 .git，请确认这是干净 snapshot 目录而非旧仓库。"
  echo "   若确认要重建，请先手动 rm -rf .git。已中止。"
  exit 1
fi
if [ ! -f "REVIEW-MANIFEST.md" ]; then
  echo "⚠️  未找到 REVIEW-MANIFEST.md，可能不在 snapshot 目录。已中止。"
  exit 1
fi

# ---- 1. 初始化 ----
git init
git add .
git commit -m "Initial clean internal pilot"
git branch -M main

# ---- 2. 关联远端（替换占位符后再运行）----
# git remote add origin <NEW_PRIVATE_REPO_URL>

# ---- 3. 推送（确认无误后手动取消注释执行）----
# git push -u origin main

echo ""
echo "✅ 本地初始化完成。下一步（手动）："
echo "   1. gh auth login   （或配置 SSH / credential helper，勿在 URL 放 token）"
echo "   2. git remote add origin <NEW_PRIVATE_REPO_URL>"
echo "   3. git push -u origin main"
