# DesignOS Architecture

This document describes the system architecture of DesignOS.

## System Overview

DesignOS is a modular design workflow engine that transforms design expertise into reusable AI skills.

```
┌─────────────────────────────────────────────────────────────────┐
│                         User Interface                          │
│  (Claude Code, Cursor, Windsurf, Kiro, etc.)                   │
└────────────────────────────────┬────────────────────────────────┘
                                 │
                                 ▼
┌─────────────────────────────────────────────────────────────────┐
│                      CLI Entry Point                            │
│  npx <YOUR_INTERNAL_PACKAGE> → Installer → Skill Registration          │
└────────────────────────────────┬────────────────────────────────┘
                                 │
                                 ▼
┌─────────────────────────────────────────────────────────────────┐
│                      Kernel (Core Engine)                       │
│                                                                 │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐        │
│  │   Skill      │  │   Pipeline   │  │   Knowledge  │        │
│  │   Loader     │  │   Executor   │  │   Injector   │        │
│  └──────────────┘  └──────────────┘  └──────────────┘        │
└────────────────────────────────┬────────────────────────────────┘
                                 │
                 ┌───────────────┼───────────────┐
                 │               │               │
                 ▼               ▼               ▼
        ┌────────────┐  ┌────────────┐  ┌────────────┐
        │   uxeval   │  │prd2proto   │  │brand-creative│
        │            │  │            │  │            │
        │ Evaluation │  │ Generation │  │ Generation │
        └────────────┘  └────────────┘  └────────────┘
                 │               │               │
                 └───────────────┼───────────────┘
                                 │
                                 ▼
                    ┌──────────────────────────┐
                    │   Structured Output      │
                    │   (.md, .yaml, .json)    │
                    └──────────────────────────┘
```

## Core Components

### 1. Skill Loader

**Location**: `designos/kernel/skill_loader.py`

**Responsibilities**:
- Load `SKILL.md` manifests from `skills/` directory
- Parse frontmatter (name, version, type, archetype)
- Load knowledge files referenced in manifest
- Validate skill configuration

**Key Functions**:
- `load_skill(skill_path)` → `SkillConfig`
- `discover_skills(skills_dir)` → `List[SkillConfig]`
- `validate_manifest(skill_md)` → `ValidationResult`

### 2. Pipeline Executor

**Location**: `designos/kernel/pipeline_executor.py`

**Responsibilities**:
- Execute multi-stage skill pipelines
- Manage stage dependencies and data flow
- Handle checkpoints and quality gates
- Coordinate tool calls (MCP servers)

**Execution Flow**:
```
1. Load skill manifest
2. For each stage:
   a. Inject knowledge context
   b. Execute stage logic
   c. Validate output schema
   d. Store intermediate results
3. Generate final output
4. Run quality checks
```

### 3. Knowledge Injector

**Location**: `designos/kernel/knowledge_injector.py`

**Responsibilities**:
- Load knowledge files (principles, heuristics, templates)
- Inject context into AI prompts
- Support multi-modal knowledge (text, images, schemas)

**Knowledge Types**:
- **Principles**: `knowledge/ux-principles.md` (Nielsen heuristics, etc.)
- **Templates**: `skills/*/templates/` (journey-map, issue-report)
- **Reference**: `knowledge/design-systems/` (brand guidelines)

### 4. Skills

Each skill is a self-contained module with:

**Structure**:
```
skills/uxeval/
├── SKILL.md                 # Manifest (frontmatter + instructions)
├── knowledge/              # Skill-specific knowledge
│   ├── principles.md
│   └── heuristics.yaml
├── templates/              # Output templates
│   ├── journey-map.md
│   └── issues.yaml
└── tests/                  # Skill tests
    └── test_uxeval.py
```

**Skill Types**:
- **Evaluation**: Analyze and critique (uxeval)
- **Generation**: Create new artifacts (prd2proto, brand-creative, logo-design)
- **Analysis**: Extract insights (ai-analytics, ip-design)

## Data Flow

### Example: UXEval Execution

```
User Input (Screenshots)
         │
         ▼
┌─────────────────────┐
│ 1. Load uxeval      │  Read SKILL.md + knowledge/
│    skill manifest   │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│ 2. Inject knowledge │  Nielsen heuristics + templates
│    context          │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│ 3. Execute stages   │  
│    - Evidence       │  Stage 1: Extract UI elements
│    - Journey        │  Stage 2: Map user flow
│    - Issues         │  Stage 3: Identify problems
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│ 4. Generate output  │  journey-map.md + issues.xlsx
│                     │  + html-report/
└─────────────────────┘
```

## Configuration

### Skill Manifest (SKILL.md)

```yaml
---
name: uxeval
version: 1.0.0
type: evaluation
archetype: heuristic-evaluation
knowledge:
  - knowledge/nielsen-heuristics.md
  - knowledge/wcag-guidelines.md
templates:
  - templates/journey-map.md
  - templates/issue-report.yaml
---

# Instructions for AI Agent
[Detailed prompt...]
```

### Pipeline Config

```yaml
stages:
  - name: evidence
    input: screenshots
    output: evidence.json
    
  - name: journey
    input: evidence.json
    output: journey-map.md
    
  - name: issues
    input: [evidence.json, journey-map.md]
    output: issues.yaml
```

## Extension Points

### Adding a New Skill

1. Create `skills/my-skill/SKILL.md`
2. Define knowledge files
3. Create output templates
4. Add tests
5. Run `npx <YOUR_INTERNAL_PACKAGE>` to register

### Custom Knowledge

Add domain-specific knowledge:
```
knowledge/
└── custom/
    ├── brand-guidelines.md
    └── design-tokens.yaml
```

Reference in SKILL.md:
```yaml
knowledge:
  - ../../knowledge/custom/brand-guidelines.md
```

## Quality Gates

DesignOS enforces quality through:

1. **Schema Validation**: Outputs match declared schemas
2. **Archetype Contract**: Skills fulfill archetype requirements
3. **Test Coverage**: 259 tests across all skills
4. **Benchmark Metrics**: Coverage, accuracy, quality scores

## Performance

**Typical Execution Times**:
- uxeval (10 screenshots): ~2-3 minutes
- prd2proto (5-page PRD): ~4-5 minutes  
- brand-creative (full identity): ~3-4 minutes

**Resource Usage**:
- Memory: ~500MB per skill execution
- Disk: ~10MB output per run

## Security

- All skills run in isolated processes
- No network access during execution (unless MCP tools)
- Input validation on all file uploads
- Output sanitization before writing to disk

## Monitoring

**Metrics Collected**:
- Execution time per stage
- Token usage (AI API calls)
- Output file sizes
- Error rates
- Quality scores

**Logs**:
- `~/.designos/logs/` - Execution logs
- `output/*/metrics.json` - Per-run metrics

## References

- [Skill Specification](../skills/README.md)
- [Knowledge Base](../knowledge/README.md)
- [Benchmark Framework](benchmark.md)
- [API Reference](api-reference.md)

---

**Last Updated**: 2026-06-09  
**Architecture Version**: 0.6.2
