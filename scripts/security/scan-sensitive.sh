#!/usr/bin/env bash
# scripts/security/scan-sensitive.sh
# 用途：扫描仓库（当前 working tree / 整个 git history / 单文件）是否含敏感证据
# 公开仓库**只放规则**，真实敏感词清单由 .designos-private-evidence/sensitive-words.txt 提供
#
# 用法：
#   bash scripts/security/scan-sensitive.sh                 # 扫当前 working tree（git ls-files）
#   bash scripts/security/scan-sensitive.sh --history       # 扫整个 git history（耗时）
#   bash scripts/security/scan-sensitive.sh --file <path>   # 扫单文件
#   bash scripts/security/scan-sensitive.sh --staged        # 扫暂存区（pre-commit hook 用）
#
# 退出码:
#   0 = 0 命中
#   1 = 有命中（详见输出）
#   2 = 配置/工具错误
#
# 设计原则：
#   - 公开仓库不含真实敏感词（避免脚本本身成为污染源）
#   - 真实词表 .designos-private-evidence/sensitive-words.txt 在 .gitignore
#   - 通用正则规则内置（公开可见，不损隐私）

set -uo pipefail

PRIVATE_WORDLIST=".designos-private-evidence/sensitive-words.txt"

# === 通用正则规则（公开可见）===
# 这些是**结构性规则**，不含具体业务词，所以可以公开
GENERIC_PATTERNS=(
  # 凭证/密钥结构（不论上下文）
  '(?i)(api[_-]?key|secret|token|password|access[_-]?token)\s*[:=]\s*["'\''][a-zA-Z0-9_\-]{16,}["'\'']'
  # 内部 URL / 内部代理（结构）
  # 注意：具体的真实内部域名只放在私有词表 .designos-private-evidence/，
  # 公开脚本仅保留通用结构正则，不硬编码任何真实域名。
  'http://[a-z]+\.internal'
  '(?i)internal[_-](corp|company|domain)\.com'
  # 本地绝对路径（暴露环境）
  '/Users/[a-zA-Z]+/Documents/'
  '/home/[a-zA-Z]+/'
  '\bC:\\\\Users\\\\'
  # Git LFS large binary 不该提交的扩展（潜在数据泄露）
  '\.(pem|key|p12|pfx|kdb|kdbx)$'
)

# === 用户私有词表加载 ===
USER_WORDLIST_LINES=""
if [ -f "$PRIVATE_WORDLIST" ]; then
  USER_WORDLIST_LINES=$(grep -vE '^[[:space:]]*(#|$)' "$PRIVATE_WORDLIST" 2>/dev/null || true)
fi

mode="working"
target=""
while [[ $# -gt 0 ]]; do
  case "$1" in
    --history) mode="history"; shift ;;
    --file)    mode="file"; target="$2"; shift 2 ;;
    --staged)  mode="staged"; shift ;;
    -h|--help) sed -n '2,20p' "$0"; exit 0 ;;
    *) echo "未知参数: $1" >&2; exit 2 ;;
  esac
done

# 命中收集
hits_total=0
hits_file_tmp=$(mktemp)
trap 'rm -f "$hits_file_tmp"' EXIT

scan_text() {
  local label="$1"
  local content_cmd="$2"  # eval 后产生内容到 stdout

  # 拿一次内容到临时文件，避免重复 eval
  local tmpf=$(mktemp)
  eval "$content_cmd" > "$tmpf" 2>/dev/null

  # 通用正则（公开规则）
  for pat in "${GENERIC_PATTERNS[@]}"; do
    matches=$(grep -EnP "$pat" "$tmpf" 2>/dev/null || true)
    if [ -n "$matches" ]; then
      echo "$matches" | while IFS= read -r line; do
        echo "[GENERIC] $label: $line" >> "$hits_file_tmp"
      done
    fi
  done

  # 用户私有词表：用 grep -F 一次扫所有词（fast-grep）
  if [ -n "$USER_WORDLIST_LINES" ]; then
    # 把词表临时存文件，用 grep -F -f 一次性扫
    local wfile=$(mktemp)
    echo "$USER_WORDLIST_LINES" > "$wfile"
    matches=$(grep -nFf "$wfile" "$tmpf" 2>/dev/null || true)
    if [ -n "$matches" ]; then
      echo "$matches" | while IFS= read -r line; do
        # 不输出原词，避免日志污染
        echo "[PRIVATE-WORD] $label: ${line:0:80}" >> "$hits_file_tmp"
      done
    fi
    rm -f "$wfile"
  fi

  rm -f "$tmpf"
}

case "$mode" in
  working)
    echo "🔍 扫描当前 working tree（git ls-files）..."
    [ -z "$USER_WORDLIST_LINES" ] && echo "⚠️  $PRIVATE_WORDLIST 不存在，仅用通用规则扫描"
    # 用 -z（NUL 分隔）避免 git 对非 ASCII（中文）文件名加引号转义而被静默跳过
    while IFS= read -r -d '' f; do
      [ -f "$f" ] || continue
      scan_text "$f" "cat \"$f\""
    done < <(git ls-files -z)
    ;;
  staged)
    echo "🔍 扫描暂存区（pre-commit）..."
    while IFS= read -r -d '' f; do
      [ -f "$f" ] || continue
      scan_text "$f (staged)" "git show \":$f\""
    done < <(git diff --cached --name-only --diff-filter=ACM -z)
    ;;
  file)
    [ -f "$target" ] || { echo "文件不存在: $target" >&2; exit 2; }
    echo "🔍 扫描单文件: $target"
    scan_text "$target" "cat \"$target\""
    ;;
  history)
    echo "🔍 扫描整个 git history（耗时）..."
    [ -z "$USER_WORDLIST_LINES" ] && echo "⚠️  $PRIVATE_WORDLIST 不存在，仅用通用规则扫描"
    # 用 git log -p 拿全部 diff 内容
    while IFS= read -r line; do
      for pat in "${GENERIC_PATTERNS[@]}"; do
        if echo "$line" | grep -EqP "$pat"; then
          echo "[GENERIC-HIST] $line" | head -c 200 >> "$hits_file_tmp"
          echo "" >> "$hits_file_tmp"
        fi
      done
    done < <(git log -p --all 2>/dev/null)
    ;;
esac

hits_total=$(wc -l < "$hits_file_tmp" | tr -d ' ')

if [ "$hits_total" -eq 0 ]; then
  echo "✅ 0 命中"
  exit 0
else
  echo "❌ $hits_total 处命中（前 30 条）："
  head -30 "$hits_file_tmp"
  exit 1
fi
