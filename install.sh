#!/usr/bin/env bash
set -euo pipefail

# DesignOS Install Script
# Usage: curl -fsSL https://raw.githubusercontent.com/<YOUR_ORG>/<YOUR_INTERNAL_REPO>/main/install.sh | bash
#
# ⚠️  请在 macOS 终端 / Linux shell 中直接运行，不要让 IDE 里的 AI 代跑
#     IDE AI 沙箱写不了 ~/.claude/skills 等全局目录，会降级成项目内安装，
#     违背"一次安装、任意项目可用"的目标。
#
# 支持的工具（自动检测）:
#   - Claude Code (CLI) → ~/.claude/skills/
#   - Codex (CLI)       → ~/.codex/skills/
#   - Trae (IDE)        → ~/.trae/skills/
#   - Qoder (IDE)       → ~/.qoderwork/skills/
#   - Cursor (IDE)      → ~/.cursor/skills-cursor/
#   - WorkBuddy (IDE)   → ~/.workbuddy/skills/

VERSION="0.5.0a1"
REPO="<YOUR_ORG>/<YOUR_INTERNAL_REPO>"
BRANCH="main"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
BLUE='\033[0;34m'
BOLD='\033[1m'
NC='\033[0m'

info()  { printf "${BLUE}▸${NC} %s\n" "$1"; }
ok()    { printf "${GREEN}✓${NC} %s\n" "$1"; }
warn()  { printf "${YELLOW}⚠${NC} %s\n" "$1"; }
err()   { printf "${RED}✗${NC} %s\n" "$1" >&2; }
header(){ printf "\n${BOLD}%s${NC}\n" "$1"; }

# -------------------------------------------------------------------
# Resolve DESIGNOS_HOME with fallback
# -------------------------------------------------------------------
# Priority:
#   1. $DESIGNOS_HOME (explicit override)
#   2. ~/.designos (if writable) — global mode
#   3. ./.designos (project-local fallback for sandboxed envs)

INSTALL_MODE="global"  # "global" or "local"

if [ -n "${DESIGNOS_HOME:-}" ]; then
  : # explicit override, respect user's choice
elif touch "$HOME/.designos.write_probe" 2>/dev/null; then
  rm -f "$HOME/.designos.write_probe"
  DESIGNOS_HOME="$HOME/.designos"
else
  warn "无法写入 $HOME（可能在 IDE AI 沙箱里），降级为项目内安装"
  warn "建议改用 macOS 终端 App 重新运行此脚本以获得全局安装"
  echo ""
  DESIGNOS_HOME="$PWD/.designos"
  INSTALL_MODE="local"
fi

SKILLS_DIR="$DESIGNOS_HOME/skills"
BIN_DIR="$DESIGNOS_HOME/bin"
VERSION_FILE="$DESIGNOS_HOME/.version"

# -------------------------------------------------------------------
# 1. Check prerequisites
# -------------------------------------------------------------------

header "DesignOS Installer v$VERSION ($INSTALL_MODE mode)"
echo ""
info "DESIGNOS_HOME: $DESIGNOS_HOME"
echo ""

if ! command -v curl &>/dev/null && ! command -v wget &>/dev/null; then
  err "需要 curl 或 wget，请先安装。"
  exit 1
fi

if ! command -v tar &>/dev/null; then
  err "需要 tar，请先安装。"
  exit 1
fi

# Check if already installed (upgrade path)
if [ -f "$VERSION_FILE" ]; then
  CURRENT=$(cat "$VERSION_FILE")
  info "检测到已安装版本: $CURRENT → 升级到 $VERSION"
fi


# -------------------------------------------------------------------
# 2. Download skills (or use local source for testing)
# -------------------------------------------------------------------

TMPDIR=$(mktemp -d)
trap 'rm -rf "$TMPDIR"' EXIT

if [ -n "${LOCAL_SOURCE:-}" ]; then
  header "使用本地源 (测试模式)"
  if [ ! -d "$LOCAL_SOURCE/skills" ]; then
    err "LOCAL_SOURCE=$LOCAL_SOURCE 下找不到 skills/ 目录"
    exit 1
  fi
  EXTRACTED="$LOCAL_SOURCE"
  ok "本地源: $LOCAL_SOURCE"
else
  header "下载 DesignOS Skills"

  ARCHIVE_URL="https://github.com/$REPO/archive/refs/heads/$BRANCH.tar.gz"

  if command -v curl &>/dev/null; then
    curl -fsSL "$ARCHIVE_URL" -o "$TMPDIR/designos.tar.gz"
  else
    wget -q "$ARCHIVE_URL" -O "$TMPDIR/designos.tar.gz"
  fi

  tar -xzf "$TMPDIR/designos.tar.gz" -C "$TMPDIR"

  # Find extracted directory (could be designos-main or Agent-design-main)
  EXTRACTED=$(find "$TMPDIR" -maxdepth 1 -type d ! -name "$(basename "$TMPDIR")" | head -1)

  if [ -z "$EXTRACTED" ] || [ ! -d "$EXTRACTED/skills" ]; then
    err "下载解压失败，找不到 skills/ 目录。"
    err "请检查网络连接或手动下载: https://github.com/$REPO"
    exit 1
  fi

  ok "下载完成"
fi

# -------------------------------------------------------------------
# 3. Install skills to ~/.designos/skills/
# -------------------------------------------------------------------

header "安装 Skills"

mkdir -p "$SKILLS_DIR"
mkdir -p "$BIN_DIR"

SKILL_COUNT=0
for skill_dir in "$EXTRACTED/skills"/*/; do
  [ -d "$skill_dir" ] || continue
  skill_name=$(basename "$skill_dir")
  target="$SKILLS_DIR/$skill_name"

  # Remove old version
  [ -d "$target" ] && rm -rf "$target"
  cp -r "$skill_dir" "$target"
  ok "$skill_name"
  SKILL_COUNT=$((SKILL_COUNT + 1))
done

# Copy AGENTS.md for project injection
if [ -f "$EXTRACTED/AGENTS.md" ]; then
  cp "$EXTRACTED/AGENTS.md" "$DESIGNOS_HOME/AGENTS.md"
fi

# Write version
echo "$VERSION" > "$VERSION_FILE"

info "已安装 $SKILL_COUNT 个 skill 到 $SKILLS_DIR"

# -------------------------------------------------------------------
# 4. Create `designos` helper script
# -------------------------------------------------------------------

header "创建辅助命令"

cat > "$BIN_DIR/designos" << 'HELPER_EOF'
#!/usr/bin/env bash
set -euo pipefail

DESIGNOS_HOME="${DESIGNOS_HOME:-$HOME/.designos}"

case "${1:-help}" in
  inject)
    # Inject AGENTS.md into current project directory (for Trae/Codex/Workbuddy)
    if [ -f "$DESIGNOS_HOME/AGENTS.md" ]; then
      cp "$DESIGNOS_HOME/AGENTS.md" ./AGENTS.md
      echo "✓ AGENTS.md 已注入到当前目录"
      echo "  现在可以在 IDE 里说 /uxeval"
    else
      echo "✗ 找不到 AGENTS.md，请重新运行 install.sh" >&2
      exit 1
    fi
    ;;
  update)
    npx <YOUR_INTERNAL_PACKAGE>
    ;;
  list)
    echo "已安装的 Skills:"
    for d in "$DESIGNOS_HOME/skills"/*/; do
      [ -d "$d" ] || continue
      name=$(basename "$d")
      version=$(grep -m1 "^version:" "$d/SKILL.md" 2>/dev/null | awk '{print $2}' || echo "?")
      echo "  $name ($version)"
    done
    ;;
  path)
    echo "$DESIGNOS_HOME/skills"
    ;;
  help|--help|-h|"")
    echo "DesignOS $(cat "$DESIGNOS_HOME/.version" 2>/dev/null || echo "?")"
    echo ""
    echo "通常不需要任何命令——安装后直接在 IDE 对话框说 /uxeval 即可。"
    echo ""
    echo "命令："
    echo "  designos list     列出已安装的 skills"
    echo "  designos path     输出 skills 安装路径"
    echo "  designos update   升级到最新版（等同 npx <YOUR_INTERNAL_PACKAGE>）"
    echo "  designos inject   注入 AGENTS.md 到当前目录（IDE 不识别时兜底）"
    echo "  designos help     显示帮助"
    ;;
  *)
    echo "未知命令: $1（输入 designos help 查看帮助）" >&2
    exit 1
    ;;
esac
HELPER_EOF

chmod +x "$BIN_DIR/designos"

# -------------------------------------------------------------------
# 5. Configure PATH
# -------------------------------------------------------------------

PATH_CONFIGURED=false

if [ -n "${SKIP_IDE_INSTALL:-}" ]; then
  info "跳过 PATH 配置（SKIP_IDE_INSTALL）"
elif [ "$INSTALL_MODE" = "local" ]; then
  info "项目内安装模式：跳过 PATH 配置（用 $BIN_DIR/designos 直接调用）"
elif ! echo "$PATH" | tr ':' '\n' | grep -qx "$BIN_DIR"; then
  SHELL_RC=""
  case "${SHELL:-}" in
    */zsh)  SHELL_RC="$HOME/.zshrc" ;;
    */bash)
      if [ "$(uname)" = "Darwin" ] && [ -f "$HOME/.bash_profile" ]; then
        SHELL_RC="$HOME/.bash_profile"
      else
        SHELL_RC="$HOME/.bashrc"
      fi
      ;;
    */fish) SHELL_RC="$HOME/.config/fish/config.fish" ;;
  esac

  if [ -n "$SHELL_RC" ]; then
    MARKER="# Added by DesignOS"
    if ! grep -q "$MARKER" "$SHELL_RC" 2>/dev/null; then
      echo "" >> "$SHELL_RC"
      echo "export PATH=\"$BIN_DIR:\$PATH\"  $MARKER" >> "$SHELL_RC"
      PATH_CONFIGURED=true
      ok "PATH 已写入 $SHELL_RC"
    fi
  fi
fi

# -------------------------------------------------------------------
# 6. Detect and configure IDEs/CLIs
# -------------------------------------------------------------------

header "配置工具"

INSTALLED_TOOLS=()

if [ -n "${SKIP_IDE_INSTALL:-}" ]; then
  warn "已设置 SKIP_IDE_INSTALL，跳过 IDE/CLI 全局配置（仅安装到 $DESIGNOS_HOME）"
elif [ "$INSTALL_MODE" = "local" ]; then
  warn "项目内安装模式：跳过 IDE 全局软链（沙箱写不了 ~/.<ide>/skills）"
  info "改为注入项目级 AGENTS.md 到当前目录"
  if [ -f "$DESIGNOS_HOME/AGENTS.md" ]; then
    cp "$DESIGNOS_HOME/AGENTS.md" "$PWD/AGENTS.md"
    ok "AGENTS.md → $PWD/AGENTS.md"
  fi
else

# Function: link skills directory to a target IDE skills dir
link_skills_to() {
  local tool_name="$1"
  local target_dir="$2"

  mkdir -p "$target_dir"

  for skill_dir in "$SKILLS_DIR"/*/; do
    [ -d "$skill_dir" ] || continue
    local skill_name target
    skill_name=$(basename "$skill_dir")
    target="$target_dir/$skill_name"

    [ -L "$target" ] && rm "$target"
    [ -d "$target" ] && rm -rf "$target"
    ln -s "$skill_dir" "$target"
  done

  ok "$tool_name → $target_dir"
  INSTALLED_TOOLS+=("$tool_name")
}

# --- Claude Code (CLI) ---
if [ -d "$HOME/.claude" ] || command -v claude &>/dev/null; then
  link_skills_to "Claude Code" "$HOME/.claude/skills"
fi

# --- Codex (CLI) ---
if [ -d "$HOME/.codex" ] || command -v codex &>/dev/null; then
  link_skills_to "Codex" "$HOME/.codex/skills"
fi

# --- Trae (IDE) ---
if [ -d "$HOME/.trae" ]; then
  link_skills_to "Trae" "$HOME/.trae/skills"
fi
if [ -d "$HOME/.trae-cn" ]; then
  link_skills_to "Trae CN" "$HOME/.trae-cn/skills"
fi

# --- Qoder / QoderWork (IDE) ---
if [ -d "$HOME/.qoderwork" ] || [ -d "/Applications/QoderWork.app" ]; then
  link_skills_to "Qoder" "$HOME/.qoderwork/skills"
fi

# --- Cursor (IDE) ---
if [ -d "$HOME/.cursor" ] || command -v cursor &>/dev/null; then
  link_skills_to "Cursor" "$HOME/.cursor/skills-cursor"
fi

# --- WorkBuddy (IDE) ---
if [ -d "$HOME/.workbuddy" ]; then
  link_skills_to "WorkBuddy" "$HOME/.workbuddy/skills"
fi

if [ ${#INSTALLED_TOOLS[@]} -eq 0 ]; then
  warn "未检测到任何已知 IDE/CLI"
  info "若你用的工具支持 AGENTS.md，请进入项目目录后运行: designos inject"
fi

fi  # end of SKIP_IDE_INSTALL guard

# -------------------------------------------------------------------
# 7. Summary
# -------------------------------------------------------------------

echo ""
printf "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}\n"
printf "${GREEN}  ✓ DesignOS v$VERSION 已安装${NC}\n"
printf "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}\n"
echo ""

if [ "$INSTALL_MODE" = "local" ]; then
  warn "已降级为项目内安装：$DESIGNOS_HOME"
  printf "  仅在当前项目目录（$PWD）的 IDE 会话里能用 /uxeval\n"
  echo ""
  printf "  ${BOLD}建议${NC} → 退出 IDE，在 macOS ${BOLD}终端 App${NC} 里重新运行：\n"
  printf "         ${BLUE}npx <YOUR_INTERNAL_PACKAGE>${NC}\n"
  echo ""
  printf "  这样 skill 会装到 ~/.designos 并软链到所有 IDE 的全局 skills 目录，\n"
  printf "  之后在任何项目目录都能 /uxeval。\n"
elif [ ${#INSTALLED_TOOLS[@]} -gt 0 ]; then
  printf "  ${BOLD}已全局生效${NC}（${INSTALLED_TOOLS[*]+${INSTALLED_TOOLS[*]}}），共 $SKILL_COUNT 个 skill\n"
  echo ""
  printf "  ${BOLD}下一步${NC} → 在任何项目目录的对话框说 ${GREEN}/uxeval${NC}\n"
  echo ""
  # IDE-specific hints (only show if user actually has that IDE)
  for tool in "${INSTALLED_TOOLS[@]+${INSTALLED_TOOLS[@]}}"; do
    case "$tool" in
      "Claude Code")
        echo "    · Claude Code 已在跑的会话需要重启才能识别"
        ;;
    esac
  done
else
  warn "未检测到任何已知 IDE（Claude Code / Codex / Trae / Qoder / Cursor）"
  printf "  在项目目录运行 ${BLUE}designos inject${NC} 注入 AGENTS.md 后使用\n"
fi

echo ""
printf "  其他命令：${BLUE}designos help${NC}\n"
echo ""

if [ "$PATH_CONFIGURED" = true ]; then
  warn "PATH 已更新，请运行: source ${SHELL_RC:-~/.zshrc}（或开新终端）"
fi

echo ""
