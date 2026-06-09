# Skills Reference

DesignOS comes with 5 production-ready skills, each with independent versioning and documentation.

## Available Skills

### 🎯 UX Evaluation & Research

#### [uxeval](uxeval.md) `v1.0.0`

Heuristic-based UX evaluation engine using Nielsen's 10 usability principles.

**Use cases:**
- Evaluate UI screenshots for usability issues
- Generate user journey maps from PRDs
- Prioritize UX problems by severity

**Quick start:**
```bash
/uxeval screenshots/login-flow
```

**Key features:**
- Multi-evidence cross-validation (screenshots + PRD + scripts)
- Automated task decomposition
- Issue attribution with principle mapping

---

### 📋 Prototyping & Specification

#### [prd2proto](prd2proto.md) `v0.2.0`

Transform PRD documents into interactive prototype specifications.

**Use cases:**
- Convert feature specs to page structures
- Generate Figma-ready component lists
- Create interaction flow diagrams

**Quick start:**
```bash
/prd2proto docs/feature-spec.md
```

**Key features:**
- Multi-modal input (text + sketches)
- Component library mapping
- Interaction state modeling

---

### 📊 Analytics & Strategy

#### [ai-analytics](ai-analytics.md) `v0.1.0`

AI-powered analytics system audit and implementation planning.

**Use cases:**
- Audit existing analytics systems for AI integration
- Generate technical roadmaps
- Cost-benefit analysis

**Quick start:**
```bash
/ai-analytics --existing-system
```

**Key features:**
- Technology stack analysis
- Integration feasibility scoring
- ROI estimation

---

### 🎨 Design Systems

#### [ip-design](ip-design.md) `v0.1.0-pilot`

IP character design system with visual guidelines generation.

**Use cases:**
- Create character design specifications
- Generate multi-angle reference sheets
- Build style guides

**Quick start:**
```bash
/ip-design --concept "friendly robot mascot"
```

**Key features:**
- Concept to visual spec conversion
- Color palette generation
- Application example mockups

---

#### [brand-creative](brand-creative.md) `v0.1.0-baseline`

Complete brand identity toolkit with 6 specialized sub-skills.

**Sub-skills:**
- `brand-strategy` — Brand positioning & core values
- `competitive-analysis` — Visual differentiation strategy
- `logo-design` — Logo concepts & variations
- `color-system` — Brand color palette & usage rules
- `typography-system` — Type selection & hierarchy
- `visual-identity` — Complete VI manual

**Quick start:**
```bash
# Run specific sub-skill
/brand-creative --sub logo-design

# Run full brand system
/brand-creative
```

**Key features:**
- Foundation → Creative → Guidelines pipeline
- Knowledge-driven generation
- Multi-archetype support

---

## Skill Versioning

Each skill has **independent semantic versioning**:

```
DesignOS 0.6.1 (package version)
├── uxeval 1.0.0          (stable)
├── prd2proto 0.2.0       (beta)
├── ai-analytics 0.1.0    (alpha)
├── ip-design 0.1.0-pilot (pilot)
└── brand-creative 0.1.0-baseline (baseline)
```

This allows skills to evolve independently without blocking DesignOS releases.

## Common Options

All skills support these common flags:

```bash
--help              # Show help message
--output DIR        # Custom output directory (default: ./output)
--verbose           # Detailed logging
--format json|yaml  # Output format
```

## Next Steps

- **[Examples](../examples/)** — See skills in action
- **[API Reference](../api-reference.md)** — Advanced usage
- **[Custom Skills](../custom-skills.md)** — Build your own
