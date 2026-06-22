#!/usr/bin/env bash
# scripts/security/scan-sensitive.sh
# 轻量兼容入口,调用 scripts/security/scan_sensitive.py(单一真源)。
#
# 用法:
#   bash scripts/security/scan-sensitive.sh                 # working tree (default)
#   bash scripts/security/scan-sensitive.sh --staged        # staged
#   bash scripts/security/scan-sensitive.sh --file <path>   # single file
#   bash scripts/security/scan-sensitive.sh --history       # git history
#
# 退出码:
#   0 = 无命中 / 1 = 有命中 / 2 = 配置或正则错误

set -uo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PY_SCANNER="$SCRIPT_DIR/scan_sensitive.py"

if ! command -v python3 >/dev/null 2>&1; then
  echo "[ERROR] python3 不可用,无法执行扫描" >&2
  exit 2
fi

if [ ! -f "$PY_SCANNER" ]; then
  echo "[ERROR] 找不到扫描器: $PY_SCANNER" >&2
  exit 2
fi

exec python3 "$PY_SCANNER" "$@"
