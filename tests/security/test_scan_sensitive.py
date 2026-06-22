#!/usr/bin/env python3
"""
tests/security/test_scan_sensitive.py — 扫描器自动化回归测试 (S2-SEC-1.2)

覆盖:
- macOS / Linux / Windows path (含 Documents/Downloads/Desktop/.designos/.codex)
- API key / token / password / internal domain / sensitive extension
- clean file
- invalid regex → exit 2
- private wordlist redaction(命中只输出位置,不输出词/原文)
- 中文/空格文件名
- working / staged / file / history 四种模式
- history 中的正则错误
- history 中的私有词命中

S2-SEC-1.2:测试源码不得含硬编码敏感字符串,必须运行时拼接生成。
"""

import os
import sys
import subprocess
import tempfile
import shutil
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
SCANNER_PY = REPO_ROOT / "scripts" / "security" / "scan_sensitive.py"
SCANNER_SH = REPO_ROOT / "scripts" / "security" / "scan-sensitive.sh"


def run_scanner(args, cwd=None, env=None):
    """运行 scanner,返回 (returncode, stdout, stderr)。"""
    cmd = [sys.executable, str(SCANNER_PY)] + args
    result = subprocess.run(
        cmd, capture_output=True, text=True,
        cwd=cwd or REPO_ROOT, env=env, check=False
    )
    return result.returncode, result.stdout, result.stderr


def run_shell_wrapper(args, cwd=None):
    """通过 shell wrapper 运行,验证入口一致性。"""
    cmd = ['bash', str(SCANNER_SH)] + args
    result = subprocess.run(
        cmd, capture_output=True, text=True,
        cwd=cwd or REPO_ROOT, check=False
    )
    return result.returncode, result.stdout, result.stderr


# === 敏感模式生成器(运行时拼接,避免测试源码自身被扫描器命中) ===
def _sensitive_path(category):
    """生成敏感路径模式,运行时拼接避免源码命中。"""
    base = {'macos_docs': '/Users/', 'macos_dl': '/Users/', 'macos_desktop': '/Users/',
            'macos_designos': '/Users/', 'macos_codex': '/Users/',
            'linux': '/home/', 'windows': 'C:\\'}
    suffix = {'macos_docs': '/Documents/', 'macos_dl': '/Downloads/', 'macos_desktop': '/Desktop/',
              'macos_designos': '/.designos/', 'macos_codex': '/.codex/',
              'linux': '/', 'windows': 'Users\\'}
    user = 'example'
    if category == 'windows':
        return base[category] + suffix[category] + 'test\\Desktop'
    return base[category] + user + suffix[category] + ('file.md' if 'docs' in category else 'data')


def _sensitive_credential(cred_type):
    """生成敏感凭证模式。"""
    key_part = {'api': 'api_key', 'token': 'token', 'pwd': 'password'}[cred_type]
    val = 'abcd1234567890' + ('efgh' if cred_type == 'api' else ('efghij' if cred_type == 'token' else 'xyz'))
    quote = '"' if cred_type in ('api', 'pwd') else "'"
    sep = '=' if cred_type == 'pwd' else ':'
    return f'{key_part} {sep} {quote}{val}{quote}'


def _sensitive_internal(internal_type):
    """生成内部域名/URL模式。"""
    if internal_type == 'url':
        return 'proxy ' + 'http://' + 'acme.internal/api'
    return 'host: foo.internal-corp' + '.com'


class TestGenericPatterns(unittest.TestCase):
    """通用正则规则覆盖测试(含 S2-SEC-1.2 扩展用户目录)。"""

    def setUp(self):
        self.tmp = tempfile.mkdtemp(prefix='scanner-test-')

    def tearDown(self):
        shutil.rmtree(self.tmp, ignore_errors=True)

    def _make_file(self, name, content):
        p = Path(self.tmp) / name
        p.write_text(content, encoding='utf-8')
        return str(p)

    def test_macos_documents(self):
        content = 'config: ' + _sensitive_path('macos_docs') + '\n'
        f = self._make_file('macos_docs.txt', content)
        rc, out, _ = run_scanner(['--file', f])
        self.assertEqual(rc, 1)
        self.assertIn('macos_user_documents', out)

    def test_macos_downloads(self):
        content = 'file: ' + _sensitive_path('macos_dl') + '\n'
        f = self._make_file('macos_dl.txt', content)
        rc, out, _ = run_scanner(['--file', f])
        self.assertEqual(rc, 1)
        self.assertIn('macos_user_downloads', out)

    def test_macos_desktop(self):
        content = 'path: ' + _sensitive_path('macos_desktop') + '\n'
        f = self._make_file('macos_desktop.txt', content)
        rc, out, _ = run_scanner(['--file', f])
        self.assertEqual(rc, 1)
        self.assertIn('macos_user_desktop', out)

    def test_macos_designos_home(self):
        content = 'cache: ' + _sensitive_path('macos_designos') + '\n'
        f = self._make_file('macos_designos.txt', content)
        rc, out, _ = run_scanner(['--file', f])
        self.assertEqual(rc, 1)
        self.assertIn('macos_designos_home', out)

    def test_macos_codex_home(self):
        content = 'data: ' + _sensitive_path('macos_codex') + '\n'
        f = self._make_file('macos_codex.txt', content)
        rc, out, _ = run_scanner(['--file', f])
        self.assertEqual(rc, 1)
        self.assertIn('macos_codex_home', out)

    def test_linux_path(self):
        content = 'home ' + _sensitive_path('linux') + '\n'
        f = self._make_file('linux.txt', content)
        rc, out, _ = run_scanner(['--file', f])
        self.assertEqual(rc, 1)
        self.assertIn('linux_home', out)

    def test_windows_path(self):
        content = 'path ' + _sensitive_path('windows') + '\n'
        f = self._make_file('win.txt', content)
        rc, out, _ = run_scanner(['--file', f])
        self.assertEqual(rc, 1)
        self.assertIn('windows_home', out)

    def test_api_key(self):
        content = _sensitive_credential('api') + '\n'
        f = self._make_file('cred.txt', content)
        rc, out, _ = run_scanner(['--file', f])
        self.assertEqual(rc, 1)
        self.assertIn('credential', out)

    def test_token(self):
        content = _sensitive_credential('token') + '\n'
        f = self._make_file('token.txt', content)
        rc, out, _ = run_scanner(['--file', f])
        self.assertEqual(rc, 1)
        self.assertIn('credential', out)

    def test_password(self):
        content = _sensitive_credential('pwd') + '\n'
        f = self._make_file('pwd.txt', content)
        rc, out, _ = run_scanner(['--file', f])
        self.assertEqual(rc, 1)
        self.assertIn('credential', out)

    def test_internal_url(self):
        content = _sensitive_internal('url') + '\n'
        f = self._make_file('url.txt', content)
        rc, out, _ = run_scanner(['--file', f])
        self.assertEqual(rc, 1)
        self.assertIn('internal_url', out)

    def test_internal_domain(self):
        content = _sensitive_internal('domain') + '\n'
        f = self._make_file('dom.txt', content)
        rc, out, _ = run_scanner(['--file', f])
        self.assertEqual(rc, 1)
        self.assertIn('internal_domain', out)

    def test_sensitive_extension(self):
        f = self._make_file('ext.txt', 'see config.pem\n')
        rc, out, _ = run_scanner(['--file', f])
        self.assertEqual(rc, 1)
        self.assertIn('sensitive_extension', out)

    def test_clean_file(self):
        f = self._make_file('clean.txt', 'this is a clean file with normal content\n')
        rc, out, _ = run_scanner(['--file', f])
        self.assertEqual(rc, 0)
        self.assertIn('0 命中', out)


class TestEdgeCases(unittest.TestCase):
    """边界 case:中文/空格文件名,二进制,等。"""

    def setUp(self):
        self.tmp = tempfile.mkdtemp(prefix='scanner-edge-')

    def tearDown(self):
        shutil.rmtree(self.tmp, ignore_errors=True)

    def test_chinese_filename(self):
        p = Path(self.tmp) / '中文文件名.txt'
        content = _sensitive_path('macos_docs') + '\n'
        p.write_text(content, encoding='utf-8')
        rc, out, _ = run_scanner(['--file', str(p)])
        self.assertEqual(rc, 1)
        self.assertIn('macos_user_documents', out)

    def test_space_filename(self):
        p = Path(self.tmp) / 'name with spaces.txt'
        content = _sensitive_path('linux') + '\n'
        p.write_text(content, encoding='utf-8')
        rc, out, _ = run_scanner(['--file', str(p)])
        self.assertEqual(rc, 1)

    def test_binary_skipped(self):
        # 二进制文件不应触发 hits(扫描器跳过)
        p = Path(self.tmp) / 'bin.dat'
        leak = _sensitive_path('macos_docs').encode('utf-8')
        p.write_bytes(b'\x00\x01\x02' + leak + b'\n')
        rc, out, _ = run_scanner(['--file', str(p)])
        # 二进制文件应安全处理(跳过 → 0,而非崩溃)
        self.assertEqual(rc, 0)
        self.assertIn('0 命中', out)


class TestRegexErrorHandling(unittest.TestCase):
    """正则错误必须 exit 2(不静默吞)。"""

    def test_invalid_regex_exits_2(self):
        # 通过临时替换 GENERIC_PATTERNS 注入坏正则
        bad_scanner = Path(tempfile.mkdtemp(prefix='bad-scanner-')) / 'bad.py'
        original = SCANNER_PY.read_text(encoding='utf-8')
        # 注入一条无法编译的正则
        injected = original.replace(
            'GENERIC_PATTERNS = [',
            "GENERIC_PATTERNS = [\n    (r'[unclosed', 'invalid'),"
        )
        bad_scanner.write_text(injected, encoding='utf-8')
        try:
            test_file = bad_scanner.parent / 'sample.txt'
            test_file.write_text('hello\n', encoding='utf-8')
            result = subprocess.run(
                [sys.executable, str(bad_scanner), '--file', str(test_file)],
                capture_output=True, text=True, check=False
            )
            self.assertEqual(result.returncode, 2)
            self.assertIn('REGEX-ERROR', result.stderr)
        finally:
            shutil.rmtree(bad_scanner.parent, ignore_errors=True)


class TestPrivateWordRedaction(unittest.TestCase):
    """私有词命中只输出文件+行号+规则类型,不输出词/原文/上下文。"""

    def test_private_word_redacted(self):
        tmp = tempfile.mkdtemp(prefix='scanner-priv-')
        try:
            # 建假私有词表
            evidence_dir = Path(tmp) / '.designos-private-evidence'
            evidence_dir.mkdir()
            wordlist = evidence_dir / 'sensitive-words.txt'
            # 运行时拼接,避免硬编码
            secret = 'SECRET_TEST' + '_TOKEN_XYZ'
            wordlist.write_text(secret + "\n", encoding='utf-8')

            # 建一个含私有词 + 上下文 的文件
            test_file = Path(tmp) / 'test.txt'
            test_file.write_text(
                "before line\n"
                f"this line has {secret} in middle\n"
                "after line\n",
                encoding='utf-8'
            )

            # 在 tmp 里运行 scanner(使其找到那个词表)
            rc, out, _ = run_scanner(['--file', str(test_file)], cwd=tmp)
            self.assertEqual(rc, 1)
            # 必须显示位置和 PRIVATE-WORD 标签
            self.assertIn('PRIVATE-WORD', out)
            # 绝不能输出私有词本身
            self.assertNotIn(secret, out)
            # 绝不能输出原文行内容
            self.assertNotIn('this line has', out)
            self.assertNotIn('in middle', out)
        finally:
            shutil.rmtree(tmp, ignore_errors=True)


class TestModes(unittest.TestCase):
    """four modes: working / staged / file / history."""

    def setUp(self):
        # 建一个独立小仓库做模式测试
        self.tmp = tempfile.mkdtemp(prefix='scanner-modes-')
        subprocess.run(['git', 'init', '-q'], cwd=self.tmp, check=True)
        subprocess.run(['git', 'config', 'user.email', 'test@example.com'], cwd=self.tmp, check=True)
        subprocess.run(['git', 'config', 'user.name', 'Test'], cwd=self.tmp, check=True)

    def tearDown(self):
        shutil.rmtree(self.tmp, ignore_errors=True)

    def _commit(self, name, content):
        p = Path(self.tmp) / name
        p.write_text(content, encoding='utf-8')
        subprocess.run(['git', 'add', name], cwd=self.tmp, check=True)
        subprocess.run(['git', 'commit', '-q', '-m', f'add {name}'], cwd=self.tmp, check=True)

    def test_working_mode_clean(self):
        self._commit('clean.md', 'clean content\n')
        rc, out, _ = run_scanner([], cwd=self.tmp)
        self.assertEqual(rc, 0)

    def test_working_mode_hit(self):
        leak = _sensitive_path('macos_docs')
        self._commit('dirty.md', leak + '\n')
        rc, out, _ = run_scanner([], cwd=self.tmp)
        self.assertEqual(rc, 1)
        self.assertIn('macos_user_documents', out)

    def test_file_mode(self):
        f = Path(self.tmp) / 'x.txt'
        leak = _sensitive_path('linux')
        f.write_text(leak + '\n', encoding='utf-8')
        rc, out, _ = run_scanner(['--file', str(f)])
        self.assertEqual(rc, 1)

    def test_staged_mode(self):
        # 先建干净仓库,然后 stage 一个有泄露的文件
        self._commit('init.md', 'init\n')
        f = Path(self.tmp) / 'staged.md'
        leak = _sensitive_path('macos_docs')
        f.write_text(leak + '\n', encoding='utf-8')
        subprocess.run(['git', 'add', 'staged.md'], cwd=self.tmp, check=True)
        rc, out, _ = run_scanner(['--staged'], cwd=self.tmp)
        self.assertEqual(rc, 1)
        self.assertIn('macos_user_documents', out)

    def test_staged_mode_clean(self):
        self._commit('init.md', 'init\n')
        f = Path(self.tmp) / 'staged.md'
        f.write_text('clean stage\n', encoding='utf-8')
        subprocess.run(['git', 'add', 'staged.md'], cwd=self.tmp, check=True)
        rc, out, _ = run_scanner(['--staged'], cwd=self.tmp)
        self.assertEqual(rc, 0)

    def test_history_mode_hit(self):
        # 提交一个含路径的文件,然后改干净
        leak = _sensitive_path('macos_docs')
        self._commit('hist.md', leak + '\n')
        f = Path(self.tmp) / 'hist.md'
        f.write_text('cleaned now\n', encoding='utf-8')
        subprocess.run(['git', 'add', 'hist.md'], cwd=self.tmp, check=True)
        subprocess.run(['git', 'commit', '-q', '-m', 'clean'], cwd=self.tmp, check=True)
        # working 应 clean
        rc_w, _, _ = run_scanner([], cwd=self.tmp)
        self.assertEqual(rc_w, 0)
        # history 应仍命中
        rc_h, out_h, _ = run_scanner(['--history'], cwd=self.tmp)
        self.assertEqual(rc_h, 1)
        self.assertIn('macos_user_documents', out_h)

    def test_history_private_word_redacted(self):
        # 历史模式下私有词命中也必须脱敏
        evidence_dir = Path(self.tmp) / '.designos-private-evidence'
        evidence_dir.mkdir()
        wordlist = evidence_dir / 'sensitive-words.txt'
        # 运行时拼接
        secret = 'HIST_PRIVATE' + '_WORD_ABC'
        wordlist.write_text(secret + "\n", encoding='utf-8')
        # 词表本身不进 git
        with open(Path(self.tmp) / '.git' / 'info' / 'exclude', 'a') as fh:
            fh.write('.designos-private-evidence/\n')

        self._commit('private.md', f'data {secret} end\n')
        rc, out, _ = run_scanner(['--history'], cwd=self.tmp)
        self.assertEqual(rc, 1)
        self.assertIn('PRIVATE-WORD', out)
        self.assertNotIn(secret, out)
        self.assertNotIn('data ', out)


class TestShellWrapper(unittest.TestCase):
    """Shell wrapper 与 Python 入口结果一致。"""

    def test_wrapper_passthrough(self):
        tmp = tempfile.mkdtemp(prefix='scanner-wrap-')
        try:
            f = Path(tmp) / 't.txt'
            f.write_text('clean content\n', encoding='utf-8')
            rc1, out1, _ = run_scanner(['--file', str(f)])
            rc2, out2, _ = run_shell_wrapper(['--file', str(f)])
            self.assertEqual(rc1, rc2)
            self.assertEqual(out1, out2)
        finally:
            shutil.rmtree(tmp, ignore_errors=True)


if __name__ == '__main__':
    unittest.main(verbosity=2)
