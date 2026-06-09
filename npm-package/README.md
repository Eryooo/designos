# DesignOS

<div align="center">

**🎨 AI-Powered Design Workflow Engine**

Transform design expertise into reusable AI skills for Claude Code, Cursor, and more.

[![npm version](https://img.shields.io/npm/v/designos.svg)](https://www.npmjs.com/package/designos)
[![npm downloads](https://img.shields.io/npm/dm/designos.svg)](https://www.npmjs.com/package/designos)
[![GitHub stars](https://img.shields.io/github/stars/Eryooo/designos?style=social)](https://github.com/Eryooo/designos)
[![License](https://img.shields.io/badge/license-Apache%202.0-blue.svg)](LICENSE)
[![CI Status](https://github.com/Eryooo/designos/workflows/CI/badge.svg)](https://github.com/Eryooo/designos/actions)

[Quick Start](#-quick-start) • [Skills](#-skills) • [Documentation](docs/README.md) • [Examples](docs/examples/)

</div>

---

## 🚀 Quick Start

Install DesignOS with a single command:

```bash
npx designos@latest
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

## 📖 Documentation

- **[Getting Started](docs/getting-started.md)** — Installation & first steps
- **[Skills Reference](docs/skills/)** — Detailed docs for each skill
- **[Examples](docs/examples/)** — Real-world use cases
- **[API Reference](docs/api-reference.md)** — CLI & pipeline API
- **[Contributing](CONTRIBUTING.md)** — Join the community

---

## 💬 Community

- **[GitHub Discussions](https://github.com/Eryooo/designos/discussions)** — Ask questions & share ideas
- **[Issues](https://github.com/Eryooo/designos/issues)** — Bug reports & feature requests
- **[Changelog](CHANGELOG.md)** — Release notes

---

## 🎯 Use Cases

- **Product Managers:** Rapidly validate interaction flows
- **Designers:** Generate design variations at scale
- **Developers:** Understand design intent & self-check
- **Startups:** Launch without a full-time designer

---

## 📊 Quality

- ✅ **259 tests** passed across all skills
- ✅ **4/4 archetypes** validated with real-world PRDs
- ✅ **CI/CD pipeline** (lint + type-check + unit tests)
- ✅ **Independent versioning** for each skill

---

## ⭐ Star History

<a href="https://star-history.com/#Eryooo/designos&Date">
 <picture>
   <source media="(prefers-color-scheme: dark)" srcset="https://api.star-history.com/svg?repos=Eryooo/designos&type=Date&theme=dark" />
   <source media="(prefers-color-scheme: light)" srcset="https://api.star-history.com/svg?repos=Eryooo/designos&type=Date" />
   <img alt="Star History Chart" src="https://api.star-history.com/svg?repos=Eryooo/designos&type=Date" />
 </picture>
</a>

---

## 🤝 Contributing

We welcome contributions! See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

```bash
# Clone and install
git clone https://github.com/Eryooo/designos.git
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

<div align="center">
  <sub>Built with ❤️ by the DesignOS community</sub>
</div>
