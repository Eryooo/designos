# API Reference

Complete reference for DesignOS CLI and programmatic API.

---

## CLI Commands

### Installation

```bash
npx <YOUR_INTERNAL_PACKAGE>
```

**What it does**:
- Installs DesignOS globally to `~/.designos/`
- Registers skills with your AI coding assistant (Claude Code, Cursor, etc.)
- Creates configuration file at `~/.designos/config.json`

**Options**:
- `--force` - Reinstall even if already installed
- `--path <dir>` - Install to custom directory
- `--skip-registration` - Skip AI assistant registration

**Example**:
```bash
npx <YOUR_INTERNAL_PACKAGE> --path ~/my-designos --force
```

---

### Skill Invocation

Skills are invoked through your AI coding assistant's slash command system:

```bash
/uxeval <screenshots-dir> [options]
/prd2proto <prd-file> [options]
/brand-creative <brief-file> [options]
/logo-design <requirements> [options]
/ip-design <character-brief> [options]
/ai-analytics <system-docs> [options]
```

---

## Skill-Specific APIs

### UXEval

**Command**: `/uxeval`

**Purpose**: Heuristic evaluation of UI/UX based on Nielsen principles and WCAG guidelines.

**Input**:
- `screenshots_dir` (required): Directory containing screenshots
- `--prd <file>` (optional): Product requirements document for context
- `--principles <file>` (optional): Custom heuristics YAML
- `--output <dir>` (optional): Output directory (default: `output/uxeval/`)
- `--lang <code>` (optional): Output language (`en`, `zh`, default: auto-detect)
- `--format <type>` (optional): Output format (`markdown`, `html`, `xlsx`, default: all)

**Output Structure**:
```
output/uxeval/
├── journey-map.md           # User journey with pain points
├── issues.xlsx              # Prioritized issue list
├── html-report/
│   ├── index.html
│   └── evidence/            # Annotated screenshots
├── delivery-assessment.json # Quality metrics
└── metrics.json             # Execution metrics
```

**Example**:
```bash
/uxeval screenshots/checkout-flow --prd docs/checkout-spec.md --lang en
```

**Output Schemas**:

**issues.yaml**:
```yaml
issues:
  - id: ISS-001
    severity: high          # high | medium | low
    title: "Hidden shipping cost"
    heuristic: "Visibility of System Status"
    location: "Cart Summary"
    evidence:
      - screenshot: "cart-01.png"
        annotation: "Price appears only at final step"
    impact:
      severity: high
      frequency: high       # high | medium | low
      fix_cost: low         # high | medium | low
    recommendation: "Display shipping estimate in cart"
    priority: 1            # Calculated: severity × frequency / fix_cost
```

---

### PRD2Proto

**Command**: `/prd2proto`

**Purpose**: Generate interactive prototype from Product Requirements Document.

**Input**:
- `prd_file` (required): Markdown or PDF PRD
- `--mode <type>` (optional): Generation mode
  - `pm`: Product Manager mode (wireframes)
  - `designer-spec`: Designer spec mode (detailed mockups)
  - `designer-dsl`: Full code generation (requires Figma/MasterGo MCP)
- `--framework <name>` (optional): `react`, `vue` (default: react)
- `--style <system>` (optional): `material`, `antd`, `tailwind` (default: tailwind)
- `--output <dir>` (optional): Output directory

**Output Structure**:
```
output/prd2proto/
├── app/                    # Generated React/Vue app
│   ├── src/
│   ├── public/
│   └── package.json
├── design-spec.md          # Design system documentation
├── tokens.json             # Design tokens (colors, spacing, typography)
├── quality-report.json     # Fidelity score & violations
└── README.md               # How to run
```

**Example**:
```bash
/prd2proto docs/dashboard-spec.md --mode designer-spec --framework react
```

---

### Brand-Creative

**Command**: `/brand-creative`

**Purpose**: Generate complete brand identity (logos, colors, typography, voice).

**Input**:
- `brief_file` (required): Brand brief (markdown)
- `--output <dir>` (optional): Output directory
- `--styles <list>` (optional): Comma-separated style preferences
- `--competitors <dir>` (optional): Competitor brand assets for analysis

**Output Structure**:
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

**Example**:
```bash
/brand-creative briefs/startup-brand.md --styles modern,minimalist
```

---

### Logo-Design

**Command**: `/logo-design`

**Purpose**: Generate logo design concepts with AI image prompts.

**Input**:
- `requirements` (required): Brief description or file path
- `--styles <list>` (optional): Style keywords
- `--iterations <n>` (optional): Number of variations (default: 3)

**Output**:
```
output/logo-design/
├── concept-1.md
├── concept-2.md
├── concept-3.md
└── image-prompts.txt       # Ready for Midjourney/DALL-E
```

---

### IP-Design

**Command**: `/ip-design`

**Purpose**: Character and IP design for brands, games, mascots.

**Input**:
- `character_brief` (required): Character description
- `--type <category>` (optional): `mascot`, `game-character`, `brand-ambassador`

**Output**:
```
output/ip-design/
├── persona-profile.md      # Personality, backstory, traits
├── voice-samples.md        # Dialogue examples
├── behavior-boundaries.yaml # Do's and don'ts
├── visual-translation.md   # Design direction
└── image-prompt.txt
```

---

### AI-Analytics

**Command**: `/ai-analytics`

**Purpose**: Audit analytics systems and recommend improvements.

**Input**:
- `system_docs` (required): Current analytics documentation
- `--focus <area>` (optional): `tracking`, `dashboards`, `experimentation`

**Output**:
```
output/ai-analytics/
├── maturity-assessment.md  # Current state analysis
├── gap-analysis.yaml       # Missing capabilities
└── roadmap.md              # 3-phase improvement plan
```

---

## Configuration API

### Config File: `~/.designos/config.json`

```json
{
  "version": "0.6.2",
  "skills_dir": "/Users/you/.designos/skills/",
  "output_dir": "./output/",
  "default_language": "en",
  "ai_assistant": "claude-code",
  "telemetry": false
}
```

**Fields**:
- `skills_dir`: Where skills are installed
- `output_dir`: Default output location
- `default_language`: ISO 639-1 language code
- `ai_assistant`: Auto-detected assistant type
- `telemetry`: Anonymous usage stats (opt-in)

---

## Python API (Advanced)

For programmatic usage:

```python
from designos import Skill, Pipeline

# Load a skill
skill = Skill.load('uxeval')

# Execute with custom config
result = skill.run(
    input_dir='screenshots/',
    prd_path='docs/spec.md',
    output_dir='custom-output/',
    lang='zh'
)

# Access outputs
print(result.journey_map)
print(result.issues)
print(result.metrics)
```

### Skill Class

```python
class Skill:
    @classmethod
    def load(cls, name: str) -> 'Skill':
        """Load skill by name"""
        
    def run(self, **kwargs) -> SkillResult:
        """Execute skill with parameters"""
        
    @property
    def manifest(self) -> SkillManifest:
        """Access skill manifest"""
```

### Pipeline Class

```python
class Pipeline:
    def __init__(self, stages: List[Stage]):
        """Initialize multi-stage pipeline"""
        
    def execute(self, context: dict) -> PipelineResult:
        """Run all stages"""
        
    def add_checkpoint(self, stage_name: str, validator: Callable):
        """Add quality gate"""
```

---

## Error Codes

| Code | Meaning | Solution |
|------|---------|----------|
| `E001` | Skill not found | Run `npx <YOUR_INTERNAL_PACKAGE>` to install |
| `E002` | Invalid input format | Check file exists and is readable |
| `E003` | Missing required parameter | Add required CLI argument |
| `E004` | Schema validation failed | Check output matches expected format |
| `E005` | Knowledge file not found | Verify `knowledge/` directory exists |
| `E006` | MCP server unavailable | Install required MCP server |
| `E007` | Output directory not writable | Check permissions |
| `E008` | Execution timeout | Reduce input size or increase timeout |

---

## Environment Variables

- `DESIGNOS_HOME`: Override installation directory (default: `~/.designos`)
- `DESIGNOS_OUTPUT`: Override output directory (default: `./output`)
- `DESIGNOS_VERBOSE`: Enable debug logging (`1` or `true`)
- `DESIGNOS_NO_COLOR`: Disable colored output
- `DESIGNOS_TIMEOUT`: Execution timeout in seconds (default: 300)

**Example**:
```bash
export DESIGNOS_VERBOSE=1
export DESIGNOS_TIMEOUT=600
/uxeval screenshots/
```

---

## Batch Processing

Process multiple inputs:

```bash
# Evaluate multiple screen sets
for dir in screenshots/*/; do
  /uxeval "$dir" --output "output/$(basename $dir)"
done

# Generate prototypes from multiple PRDs
find docs/prds/ -name "*.md" -exec /prd2proto {} \;
```

---

## Integration with CI/CD

### GitHub Actions

```yaml
- name: Run UX Evaluation
  run: |
    npx <YOUR_INTERNAL_PACKAGE>
    /uxeval screenshots/ --format json
    
- name: Upload Report
  uses: actions/upload-artifact@v3
  with:
    name: ux-report
    path: output/uxeval/
```

---

## Versioning

DesignOS follows [Semantic Versioning](https://semver.org/):

- **Major** (0.x.0): Breaking changes to skill API or output schemas
- **Minor** (0.x.0): New skills or features, backward compatible
- **Patch** (0.0.x): Bug fixes, documentation updates

Check version:
```bash
cat ~/.designos/version.txt
```

---

## Community Skills

Install community-contributed skills:

```bash
npx <YOUR_INTERNAL_PACKAGE> install <github-repo>
```

Example:
```bash
npx <YOUR_INTERNAL_PACKAGE> install username/my-custom-skill
```

---

## Support

- **Documentation**: <YOUR_INTERNAL_PRIVATE_REPO>#readme
- **Issues**: <YOUR_INTERNAL_PRIVATE_REPO>/issues
- **Discussions**: <YOUR_INTERNAL_PRIVATE_REPO>/discussions

---

**Last Updated**: 2026-06-09  
**API Version**: 0.6.2
