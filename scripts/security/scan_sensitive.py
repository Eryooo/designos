#!/usr/bin/env python3
"""
scripts/security/scan_sensitive.py — 单一真源敏感扫描器(S2-SEC-1.1)

用途：扫描仓库（working tree / staged / single file / git history）是否含敏感证据
公开仓库**只放规则**，真实敏感词清单由 .designos-private-evidence/sensitive-words.txt 提供

用法:
  python3 scripts/security/scan_sensitive.py                  # working tree
  python3 scripts/security/scan_sensitive.py --staged         # staged (pre-commit)
  python3 scripts/security/scan_sensitive.py --file <path>    # single file
  python3 scripts/security/scan_sensitive.py --history        # git history (slow)

退出码:
  0 = 无命中
  1 = 有命中
  2 = 配置/工具/正则错误

设计原则:
  - 单一真源:Shell 入口仅作 wrapper,本脚本承担全部扫描逻辑
  - 跨平台:不依赖 grep -P / GNU grep;只用 Python 3 标准库
  - 私有词表脱敏:命中只输出文件+行号+规则类型,绝不输出命中词或原文行
  - 二进制安全:跳过 NUL 字节文件,UTF-8 解码失败用 errors='replace'
  - 正则错误显式 exit 2,不静默吞掉
"""

import sys
import os
import re
import subprocess
import argparse
from pathlib import Path

PRIVATE_WORDLIST = ".designos-private-evidence/sensitive-words.txt"

# === 通用正则规则(公开可见的结构性规则,不含具体业务词)===
# S2-SEC-1.2: 扩展覆盖所有用户目录形式
# S2-SEC-1.3: 用户名字符集从 [a-zA-Z]+ 扩展为 [A-Za-z0-9._-]+ (支持 user_01, john-doe, john.smith 等常见形式)
GENERIC_PATTERNS = [
    # 凭证/密钥结构
    (r'(?i)(api[_-]?key|secret|token|password|access[_-]?token)\s*[:=]\s*["\'][a-zA-Z0-9_\-]{16,}["\']',
     'credential'),
    # 内部 URL / 域名结构(具体真实域名只放私有词表)
    (r'http://[a-z]+\.internal', 'internal_url'),
    (r'(?i)internal[_-](corp|company|domain)\.com', 'internal_domain'),
    # 本地绝对路径(暴露环境) — S2-SEC-1.3 用户名字符集扩展
    (r'/Users/[A-Za-z0-9._-]+/Documents/', 'macos_user_documents'),
    (r'/Users/[A-Za-z0-9._-]+/Downloads/', 'macos_user_downloads'),
    (r'/Users/[A-Za-z0-9._-]+/Desktop/', 'macos_user_desktop'),
    (r'/Users/[A-Za-z0-9._-]+/\.designos/', 'macos_designos_home'),
    (r'/Users/[A-Za-z0-9._-]+/\.codex/', 'macos_codex_home'),
    (r'/home/[A-Za-z0-9._-]+/', 'linux_home'),
    (r'\bC:\\Users\\[A-Za-z0-9._-]+\\', 'windows_home'),
    # 不该提交的敏感扩展名
    (r'\.(pem|key|p12|pfx|kdb|kdbx)$', 'sensitive_extension'),
]


def compile_patterns(patterns):
    """预编译正则。任一编译失败 → exit 2(显式上抛)。"""
    compiled = []
    for pat, label in patterns:
        try:
            compiled.append((re.compile(pat), label))
        except re.error as e:
            print(f"[REGEX-ERROR] pattern={pat!r}: {e}", file=sys.stderr)
            sys.exit(2)
    return compiled


def load_private_wordlist():
    """加载私有词表(每行一词,# 注释)。返回词集合,不存在时返回空集。"""
    p = Path(PRIVATE_WORDLIST)
    if not p.exists():
        return set()
    words = set()
    try:
        with open(p, 'r', encoding='utf-8', errors='replace') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#'):
                    words.add(line)
    except OSError as e:
        print(f"[WORDLIST-ERROR] {e}", file=sys.stderr)
        sys.exit(2)
    return words


def is_binary_file(path):
    """检测二进制文件:读前 8KB,含 NUL 字节即视为二进制。"""
    try:
        with open(path, 'rb') as f:
            chunk = f.read(8192)
        return b'\x00' in chunk
    except OSError:
        return True  # 读不到就跳过


def scan_lines(label, lines_iter, generic_compiled, private_words):
    """
    通用扫描内核:接收逐行迭代器,返回 hits 列表。
    hits 元素 = (label, lineno, rule_type, redacted_excerpt_or_None)
    私有词命中:redacted_excerpt = None(完全脱敏)
    通用规则命中:redacted_excerpt = 原行(公开规则,可显示上下文)
    """
    hits = []
    for lineno, line in enumerate(lines_iter, start=1):
        line_str = line.rstrip('\n')
        # 通用规则
        for regex, rule_label in generic_compiled:
            if regex.search(line_str):
                hits.append((label, lineno, f'GENERIC:{rule_label}', line_str))
        # 私有词表:全脱敏
        if private_words:
            for word in private_words:
                if word in line_str:
                    hits.append((label, lineno, 'PRIVATE-WORD', None))
                    break  # 同行多词只记一次,避免词数泄露
    return hits


def scan_file(path, generic_compiled, private_words):
    """扫单个文件。二进制跳过。返回 hits 列表。"""
    if is_binary_file(path):
        return []
    try:
        with open(path, 'r', encoding='utf-8', errors='replace') as f:
            return scan_lines(path, f, generic_compiled, private_words)
    except OSError as e:
        print(f"[READ-ERROR] {path}: {e}", file=sys.stderr)
        return []


def git_ls_files():
    """调 git ls-files -z,正确处理中文/空格文件名。"""
    result = subprocess.run(
        ['git', 'ls-files', '-z'],
        capture_output=True, check=False
    )
    if result.returncode != 0:
        print(f"[GIT-ERROR] ls-files: {result.stderr.decode('utf-8', errors='replace')}", file=sys.stderr)
        sys.exit(2)
    raw = result.stdout
    if not raw:
        return []
    # 末尾的 NUL 后会有空段,filter 掉
    files = [f.decode('utf-8', errors='replace') for f in raw.split(b'\x00') if f]
    return files


def git_staged_files():
    """暂存区文件清单,仅 ACM(新增/复制/修改)。"""
    result = subprocess.run(
        ['git', 'diff', '--cached', '--name-only', '--diff-filter=ACM', '-z'],
        capture_output=True, check=False
    )
    if result.returncode != 0:
        print(f"[GIT-ERROR] diff --cached: {result.stderr.decode('utf-8', errors='replace')}", file=sys.stderr)
        sys.exit(2)
    raw = result.stdout
    if not raw:
        return []
    return [f.decode('utf-8', errors='replace') for f in raw.split(b'\x00') if f]


def git_show_staged(path):
    """读暂存区版本。返回 (lines_iter or None, error)。"""
    result = subprocess.run(
        ['git', 'show', f':{path}'],
        capture_output=True, check=False
    )
    if result.returncode != 0:
        return None, result.stderr.decode('utf-8', errors='replace')
    text = result.stdout.decode('utf-8', errors='replace')
    return text.splitlines(), None


def scan_history(generic_compiled, private_words):
    """
    history 模式:用 git log -p --all 流式拉所有 diff,逐行扫。
    正则错误已在 compile_patterns 阶段拦截;此处 git 错误 → exit 2。
    """
    proc = subprocess.Popen(
        ['git', 'log', '-p', '--all'],
        stdout=subprocess.PIPE, stderr=subprocess.PIPE,
        bufsize=1
    )
    if proc.stdout is None:
        print("[GIT-ERROR] log -p --all: no stdout", file=sys.stderr)
        sys.exit(2)

    hits = []
    current_label = "<history>"
    try:
        for raw_line in proc.stdout:
            line = raw_line.decode('utf-8', errors='replace').rstrip('\n')
            # 跟踪当前 commit / 文件作为 label(轻量,不解析全 diff)
            if line.startswith('commit '):
                current_label = line[:50]
            elif line.startswith('+++') or line.startswith('---'):
                current_label = line[:80]
            # 只扫 diff 加行(避免重复扫历史多版本)
            if not line.startswith('+') or line.startswith('+++'):
                continue
            content = line[1:]  # 去掉 + 前缀
            # 通用规则
            for regex, rule_label in generic_compiled:
                if regex.search(content):
                    hits.append((current_label, 0, f'GENERIC:{rule_label}', content[:200]))
            # 私有词表:全脱敏
            if private_words:
                for word in private_words:
                    if word in content:
                        hits.append((current_label, 0, 'PRIVATE-WORD', None))
                        break
    finally:
        proc.stdout.close()
        proc.wait()
        if proc.returncode != 0:
            err = proc.stderr.read().decode('utf-8', errors='replace') if proc.stderr else ''
            # git log 退出非零(如空仓库)不视为致命
            if 'fatal' in err.lower():
                print(f"[GIT-ERROR] log -p: {err}", file=sys.stderr)
                sys.exit(2)
        if proc.stderr:
            proc.stderr.close()
    return hits


def emit_hits(hits, max_show=30):
    """输出命中。私有词命中只显示文件+行号+规则类型,不输出词/原文/上下文。"""
    print(f"❌ {len(hits)} 处命中(前 {max_show} 条):")
    for label, lineno, rule_type, excerpt in hits[:max_show]:
        if rule_type == 'PRIVATE-WORD':
            # 完全脱敏:只输出位置和规则类型
            print(f"  [{rule_type}] {label}:{lineno}")
        else:
            # 通用规则:显示上下文(规则本身公开)
            shown = excerpt[:160] if excerpt else ''
            print(f"  [{rule_type}] {label}:{lineno}: {shown}")


def main():
    parser = argparse.ArgumentParser(description='Sensitive scanner (S2-SEC-1.1)')
    g = parser.add_mutually_exclusive_group()
    g.add_argument('--working', action='store_true', help='Scan working tree (default)')
    g.add_argument('--staged', action='store_true', help='Scan staged files')
    g.add_argument('--file', metavar='PATH', help='Scan single file')
    g.add_argument('--history', action='store_true', help='Scan git history (slow)')
    args = parser.parse_args()

    # 模式判定(默认 working)
    mode = 'working'
    if args.staged:
        mode = 'staged'
    elif args.file:
        mode = 'file'
    elif args.history:
        mode = 'history'

    generic_compiled = compile_patterns(GENERIC_PATTERNS)
    private_words = load_private_wordlist()
    if not private_words:
        print(f"⚠️  {PRIVATE_WORDLIST} 不存在,仅用通用规则扫描", file=sys.stderr)

    all_hits = []

    if mode == 'working':
        print("🔍 扫描当前 working tree (git ls-files)...")
        files = git_ls_files()
        for f in files:
            if not os.path.isfile(f):
                continue
            all_hits.extend(scan_file(f, generic_compiled, private_words))

    elif mode == 'staged':
        print("🔍 扫描暂存区 (pre-commit)...")
        files = git_staged_files()
        for f in files:
            lines, err = git_show_staged(f)
            if err:
                print(f"[GIT-ERROR] show :{f}: {err}", file=sys.stderr)
                continue
            label = f"{f} (staged)"
            all_hits.extend(scan_lines(label, iter(lines), generic_compiled, private_words))

    elif mode == 'file':
        path = args.file
        if not os.path.isfile(path):
            print(f"文件不存在: {path}", file=sys.stderr)
            sys.exit(2)
        print(f"🔍 扫描单文件: {path}")
        all_hits.extend(scan_file(path, generic_compiled, private_words))

    elif mode == 'history':
        print("🔍 扫描整个 git history(耗时)...")
        all_hits.extend(scan_history(generic_compiled, private_words))

    if not all_hits:
        print("✅ 0 命中")
        sys.exit(0)
    else:
        emit_hits(all_hits)
        sys.exit(1)


if __name__ == '__main__':
    main()
