# Troubleshooting Guide

Common issues and solutions for DesignOS.

## Installation Issues

### "Command not found: npx"

**Cause:** Node.js not installed or not in PATH.

**Solution:**
1. Install Node.js 16+ from [nodejs.org](https://nodejs.org/)
2. Verify: `node --version` (should show v16+)
3. Retry: `npx <YOUR_INTERNAL_PACKAGE>`

---

### "Python 3.11 not found"

**Cause:** Required Python version not installed.

**Solution:**
1. Install Python 3.11+ from [python.org](https://www.python.org/downloads/)
2. Verify: `python3 --version` (should show 3.11+)
3. Retry installation

**macOS users:**
```bash
brew install python@3.11
```

**Linux users:**
```bash
sudo apt install python3.11  # Ubuntu/Debian
sudo dnf install python3.11  # Fedora
```

---

### Installation Hangs at "Installing skills..."

**Cause:** Network timeout or permission issues.

**Solution 1:** Check network connection
```bash
curl -I https://registry.npmjs.org/
```

**Solution 2:** Clear npm cache
```bash
npm cache clean --force
npx <YOUR_INTERNAL_PACKAGE>
```

**Solution 3:** Install with verbose logging
```bash
DEBUG=* npx <YOUR_INTERNAL_PACKAGE>
```

---

## Usage Issues

### "Skill not found: /uxeval"

**Cause:** Skills not installed or IDE not restarted.

**Solution:**
1. Verify skills are installed:
   ```bash
   ls ~/.designos/skills/
   ```
   Should show: `ai-analytics`, `brand-creative`, `ip-design`, `prd2proto`, `uxeval`

2. Restart your AI coding assistant (Claude Code / Cursor)

3. If still not working, check IDE configuration:
   ```bash
   cat ~/.claude/config.json  # Claude Code
   cat ~/.cursor/config.json  # Cursor
   ```

---

### "Permission denied" when running skills

**Cause:** Installation directory not writable.

**Solution:**
```bash
# Fix permissions
chmod -R u+w ~/.designos

# Or reinstall to custom location
DESIGNOS_HOME=~/my-designos npx <YOUR_INTERNAL_PACKAGE>
```

---

### Output files not generated

**Cause:** Working directory not writable or skill error.

**Solution 1:** Check current directory permissions
```bash
ls -la .
# Should show writable directory
```

**Solution 2:** Specify custom output directory
```bash
/uxeval screenshots/ --output ~/Desktop/output
```

**Solution 3:** Check skill logs
```bash
/uxeval screenshots/ --verbose
```

---

## Performance Issues

### Skills run very slowly

**Cause:** Large input files or low system resources.

**Solution 1:** Optimize input size
- Compress screenshots (< 5MB each)
- Split large PRDs into sections
- Limit to 10-20 files per run

**Solution 2:** Increase system resources
- Close other apps
- Ensure 4GB+ free RAM
- Use SSD (not HDD)

---

### Out of memory errors

**Cause:** Processing too many files at once.

**Solution:**
```bash
# Process in batches
/uxeval screenshots/batch-1/ --output output/batch-1
/uxeval screenshots/batch-2/ --output output/batch-2
```

---

## Output Quality Issues

### Generated output is too generic

**Cause:** Insufficient input context.

**Solution:** Provide more context
```bash
# Add PRD for better context
/uxeval screenshots/ --prd docs/detailed-spec.md

# Add custom principles
/uxeval screenshots/ --principles custom-heuristics.yaml
```

---

### Output in wrong language

**Cause:** Language auto-detection from input files.

**Solution:** Force language
```bash
/uxeval screenshots/ --lang en  # English
/uxeval screenshots/ --lang zh  # Chinese
```

---

## IDE Integration Issues

### Claude Code: Skills not showing in autocomplete

**Cause:** Configuration not loaded.

**Solution:**
1. Restart Claude Code
2. Check config: `~/.claude/skills/`
3. Manually refresh: `/reload-skills` (if available)

---

### Cursor: "Unknown command" error

**Cause:** Custom command not registered.

**Solution:**
1. Open Cursor settings
2. Go to "Commands" section
3. Click "Reload Custom Commands"
4. Retry skill invocation

---

## Known Limitations

### Not Supported

❌ **Windows < 10** — Use WSL or upgrade to Windows 10+  
❌ **Python < 3.11** — Some dependencies require 3.11+  
❌ **Node.js < 16** — npm features require Node 16+

### Platform-Specific Issues

**macOS:**
- Gatekeeper may block install.sh → Right-click & "Open"
- Rosetta 2 required on Apple Silicon (auto-installed)

**Windows:**
- Use PowerShell or Git Bash (not CMD)
- Antivirus may flag install.sh → Add exception

**Linux:**
- Some distros need manual Python 3.11 install
- SELinux may block `~/.designos` → Configure policies

---

## Getting More Help

### Before Asking for Help

1. ✅ Check this troubleshooting guide
2. ✅ Search [GitHub Issues](<YOUR_INTERNAL_PRIVATE_REPO>/issues)
3. ✅ Read [FAQ](#faq) below

### How to Report Issues

When opening a GitHub Issue, include:

```
**Environment:**
- OS: macOS 14.0 / Windows 11 / Ubuntu 22.04
- Node.js version: `node --version`
- Python version: `python3 --version`
- DesignOS version: `npm list -g designos`
- AI Assistant: Claude Code / Cursor

**Steps to Reproduce:**
1. ...
2. ...

**Expected vs Actual Behavior:**
Expected: ...
Actual: ...

**Logs:**
(Paste output from `--verbose` flag)
```

### Community Support

- [GitHub Discussions](<YOUR_INTERNAL_PRIVATE_REPO>/discussions) — Q&A
- [Discord](https://discord.gg/designos) — Real-time chat (coming soon)

---

## FAQ

### Q: Can I use DesignOS offline?

A: Skills run locally, but some features require internet (AI model calls). Check skill documentation for offline support.

### Q: How do I update DesignOS?

A: Run `npx <YOUR_INTERNAL_PACKAGE>` — it detects existing installation and upgrades.

### Q: Can I customize skill behavior?

A: Yes! See [Custom Skills Guide](custom-skills.md).

### Q: Does DesignOS send data to external servers?

A: Skills use AI models that may send data to providers (OpenAI, Anthropic). No telemetry by default. See [Privacy Policy](privacy.md).

### Q: Can I contribute new skills?

A: Absolutely! See [Contributing Guide](../CONTRIBUTING.md).

---

**Still stuck?** Open an issue: <YOUR_INTERNAL_PRIVATE_REPO>/issues/new
