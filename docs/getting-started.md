# Getting Started with DesignOS

This guide will help you install and use DesignOS in less than 5 minutes.

## Prerequisites

- **Node.js 16+** — For running `npx` command
- **Python 3.11+** — For running skills (auto-installed by DesignOS)
- **AI Coding Assistant** — Claude Code, Cursor, or compatible tool

## Installation

### Step 1: Install DesignOS

Run this command in your terminal:

```bash
npx <YOUR_INTERNAL_PACKAGE>
```

This will:
- ✅ Install all 5 skills to `~/.designos/skills/`
- ✅ Detect and configure supported IDEs (Claude Code, Cursor, etc.)
- ✅ Create helper commands

**Expected output:**
```
DesignOS Installer v0.6.1

✓ ai-analytics
✓ brand-creative
✓ ip-design
✓ prd2proto
✓ uxeval
▸ Installed 5 skills to ~/.designos/skills
```

### Step 2: Verify Installation

Open Claude Code or Cursor and type:

```bash
/uxeval --help
```

You should see the help message for the `uxeval` skill.

## Your First UX Evaluation

Let's evaluate a login flow with screenshots.

### Prepare Your Files

Create a directory with screenshots:
```
my-project/
├── screenshots/
│   ├── login-screen.png
│   ├── signup-screen.png
│   └── forgot-password.png
└── docs/
    └── prd.md  (optional)
```

### Run the Evaluation

In Claude Code / Cursor:

```bash
/uxeval screenshots/
```

**With PRD context:**
```bash
/uxeval screenshots/ --prd docs/prd.md
```

### Review Output

DesignOS generates:
- `output/uxeval/journey-map.md` — User journey analysis
- `output/uxeval/issues.md` — Prioritized problem list
- `output/uxeval/tasks.md` — Task decomposition

## Next Steps

### Try Other Skills

**Generate a brand logo:**
```bash
/brand-creative --sub logo-design
```

**Convert PRD to prototype:**
```bash
/prd2proto docs/feature-spec.md
```

**Audit AI analytics:**
```bash
/ai-analytics --existing-system
```

### Explore Documentation

- [Skills Reference](skills/README.md) — Detailed docs for each skill
- [Examples](examples/) — Real-world use cases
- [API Reference](api-reference.md) — Advanced usage

## Troubleshooting

### "Command not found: /uxeval"

**Solution:** Restart your AI assistant after installation.

### "Python 3.11 not found"

**Solution:** Install Python 3.11+ from [python.org](https://www.python.org/downloads/)

### Skills not showing up

**Solution:** Check installation path:
```bash
ls ~/.designos/skills/
```

You should see: `ai-analytics`, `brand-creative`, `ip-design`, `prd2proto`, `uxeval`

### More help?

- [Troubleshooting Guide](troubleshooting.md)
- [GitHub Discussions](<YOUR_INTERNAL_PRIVATE_REPO>/discussions)

## Configuration

### Custom Installation Path

```bash
DESIGNOS_HOME=~/my-custom-path npx <YOUR_INTERNAL_PACKAGE>
```

### Skip IDE Auto-Configuration

```bash
npx <YOUR_INTERNAL_PACKAGE> --no-ide-config
```

## Updating DesignOS

To update to the latest version:

```bash
npx <YOUR_INTERNAL_PACKAGE>
```

DesignOS will detect existing installation and upgrade in-place.

## Uninstallation

```bash
rm -rf ~/.designos
```

---

**🎉 Congratulations!** You're ready to use DesignOS. Check out [examples](examples/) to see what's possible.
