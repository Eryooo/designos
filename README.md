# DesignOS

<div align="center">

**🎨 AI-Powered Design Workflow Engine**

Transform design expertise into reusable AI skills for Claude Code, Cursor, and more.

![Skills](https://img.shields.io/badge/skills-5-purple?style=for-the-badge)
![Status](https://img.shields.io/badge/status-internal_pilot-yellow?style=for-the-badge)
[![License](https://img.shields.io/badge/license-Apache%202.0-orange?style=for-the-badge)](LICENSE)

> **Internal pilot — not a public release.** Status of record:
> [`INTERNAL-PILOT-README.md`](INTERNAL-PILOT-README.md) · [`REVIEW-MANIFEST.md`](REVIEW-MANIFEST.md)

[Quick Start](#-quick-start) • [Skills](#-skills) • [Documentation](docs/README.md) • [Examples](docs/examples/)

</div>

---

## 🚀 Quick Start

> Internal pilot is distributed as a clean snapshot, **not** a public npm package.
> Install from your internal private repo / registry rather than the public registry.

```bash
# from the internal private repo checkout
pip install -e ".[dev]"
```

Then use in any AI coding assistant:

```bash
/uxeval screenshots/login-flow        # UX evaluation
/brand-creative --sub logo-design     # Logo design
/prd2proto docs/feature-spec.md       # PRD to prototype
```

**👉 [Full Installation Guide](docs/getting-started.md)**

---

## ✨ Skills

| Skill | Description | Version |
|-------|-------------|---------|
| **uxeval** | Heuristic UX evaluation engine | 1.0.0 |
| **prd2proto** | PRD to interactive prototype pipeline | 0.2.0 |
| **ai-analytics** | AI analytics system audit | 0.1.0 |
| **ip-design** | IP character design system | 0.1.0-pilot |
| **brand-creative** | Complete brand identity toolkit (6 sub-skills) | 0.1.0-baseline |

**👉 [Explore All Skills](docs/skills/)**

---

## 🔄 How It Works

```
User Input
(Screenshots / PRD / Design Brief)
         │
         ▼
┌─────────────────────┐
│ Knowledge Injection │  Load design principles, heuristics, templates
│                     │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│ Pipeline Execution  │  Multi-stage processing: analyze → evaluate → generate
│                     │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│ Structured Output   │  Markdown, YAML, HTML reports
│                     │
└─────────────────────┘
```

---

## 📸 Output Examples

### UXEval: E-Commerce Checkout Evaluation

**Input:**
```bash
/uxeval screenshots/checkout-flow --prd docs/checkout-spec.md
```

**Output:**
```
output/uxeval/
├── journey-map.md           # User journey with pain points
├── issues.xlsx              # Prioritized issue list (Severity × Frequency × Fix Cost)
├── html-report/             # Interactive HTML report
│   ├── index.html
│   └── evidence/            # Annotated screenshots
└── delivery-assessment.json # Quality metrics & coverage
```

**Sample Issue Detection:**
```markdown
## Critical Issue #1: Hidden Shipping Cost
**Severity:** High | **Nielsen Principle:** Visibility of System Status
**Location:** Cart Summary

**Evidence:**
- Screenshot cart-01.png: Price appears only at final step
- User quote: "Why is there suddenly ¥50 more at checkout?"

**Impact:**
- Severity: High (affects purchase decision)
- Frequency: High (100% users encounter)
- Fix Cost: Low (display logic adjustment)

**Recommendation:** Display shipping estimate in cart
```

### PRD2Proto: SaaS Dashboard Prototype

**Input:**
```bash
/prd2proto docs/dashboard-spec.md --mode designer-spec --framework react
```

**Output:**
```
output/prd2proto/
├── app/                    # Generated React app
│   ├── src/
│   │   ├── components/
│   │   └── pages/
│   ├── public/
│   └── package.json
├── design-spec.md          # Design system docs
├── tokens.json             # Design tokens (colors, spacing, typography)
├── quality-report.json     # Fidelity score & violations
└── README.md               # How to run
```

### Brand-Creative: Full Brand Identity

**Input:**
```bash
/brand-creative briefs/startup-brand.md --styles modern,minimalist
```

**Output:**
```
output/brand-creative/
├── logo/
│   ├── concept.md          # Logo design rationale
│   ├── simplification-tiers.yaml  # 4-tier simplification
│   └── image-prompt.txt    # AI image generation prompt
├── color-system.yaml       # Brand colors with semantic meanings
├── typography.yaml         # Font pairings
├── voice-guide.md          # Brand voice & tone
├── rubric-evaluation.json  # 9-dimension self-assessment
└── gap-report.md           # Quality gaps vs senior designer
```

**👉 [See More Examples](docs/examples/)**

---

## 🎯 Why DesignOS?

| Tool | What it does | When to use |
|------|-------------|-------------|
| **Figma AI** | Visual design generation | When you need pixel-perfect mockups |
| **ui-ux-pro-max** | Design system generation (67 styles) | When you need a complete design system |
| **DesignOS** | **Design intelligence workflow** | When you need evaluation + generation + analysis |

**DesignOS = The only tool that both evaluates and generates design artifacts**

---

## 📊 Detailed Skills Comparison

| Skill | Input | Output | Use Case | Time |
|-------|-------|--------|----------|------|
| **uxeval** | Screenshots + PRD | Journey map + Issue list + HTML report | UX review, usability testing | 2-3 min |
| **prd2proto** | PRD document | Runnable React/Vue prototype | Rapid validation, demos | 4-5 min |
| **brand-creative** | Brand brief | Logo + Colors + Typography + Voice | Brand building, rebranding | 3-4 min |
| **logo-design** | Requirements | 3 design concepts + Image prompts | Logo creation | 1-2 min |
| **ip-design** | Character description | Persona + Dialogue + Visual guide | Mascots, game characters | 2-3 min |
| **ai-analytics** | System docs | Maturity assessment + Roadmap | Analytics system audit | 3-4 min |

---

## 📖 Documentation

- **[Getting Started](docs/getting-started.md)** — Installation & first steps
- **[Skills Reference](docs/skills/)** — Detailed docs for each skill
- **[Examples](docs/examples/)** — Real-world use cases
- **[API Reference](docs/api-reference.md)** — CLI & pipeline API
- **[Contributing](CONTRIBUTING.md)** — Join the community

---

## 💬 Community

- **Internal pilot feedback** — file issues/discussions in your internal private repo
- **[Changelog](CHANGELOG.md)** — Release notes

---

## 🎯 Use Cases

- **Product Managers:** Rapidly validate interaction flows
- **Designers:** Generate design variations at scale
- **Developers:** Understand design intent & self-check
- **Startups:** Launch without a full-time designer

---

## 📊 Quality & Status

> **Internal pilot — not public release, not enterprise-ready, not all-skills senior-level.**
> The authoritative status source is `INTERNAL-PILOT-README.md` / `REVIEW-MANIFEST.md`.

- ✅ Per-skill unit tests pass when run individually (some cross-skill collection
  quirks and a few known pipeline-structure failures remain — see REVIEW-MANIFEST)
- 🧪 **4 product archetypes** exercised with synthetic PRDs (not validated against
  real-world production usage)
- ✅ **CI/CD pipeline** (lint + type-check + unit tests)
- ✅ **Independent versioning** for each skill
- ⚠️ **prd2proto** is the most advanced seniorization pilot; other skills
  (uxeval / ai-analytics / ip-design / brand-creative) still require seniorization

---

## 🤝 Contributing

We welcome contributions! See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

```bash
# Clone and install (replace with your internal private repo URL)
git clone <YOUR_INTERNAL_PRIVATE_REPO_URL>
cd designos
pip install -e ".[dev]"

# Run tests
pytest

# Code quality checks
ruff check .
pyright
```

---

## 📝 License

Apache 2.0 — See [LICENSE](LICENSE) for details.

---

## 🔗 Related Projects

- [ui-ux-pro-max-skill](https://github.com/nextlevelbuilder/ui-ux-pro-max-skill) - Design system generator
- [awesome-design-md](https://github.com/VoltAgent/awesome-design-md) - Brand design library
- [Claude Code](https://claude.ai/code) - AI coding assistant
- [Cursor](https://cursor.sh) - AI code editor

---

**Languages:** English | [简体中文](README.zh-CN.md)

<div align="center">
  <sub>Built with ❤️ by the DesignOS community</sub>
</div>
