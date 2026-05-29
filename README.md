# drawio-diagramming

A Kiro skill that generates production-quality AWS architecture diagrams as `.drawio` XML, with automated validation and export to SVG/PNG.

## What it does

This skill teaches AI coding assistants to produce draw.io diagrams that follow the official AWS Architecture Icons style guide (R23-2026.01.30). It eliminates the most common LLM mistakes — wrong colors, broken icon names, services placed in the wrong VPC container, non-standard arrows — by encoding the verified rules from the AWS deck directly into the skill's reference files and validators.

**Key capabilities:**
- Generates valid `.drawio` XML with correct AWS service icons, category colors, and container nesting
- Enforces the 2026 AWS arrow preset (1.25pt black, filled classic head, orthogonal routing)
- Validates VPC membership (only ENI-resident services inside VPC containers)
- Checks all 155+ service icons against ground-truth colors extracted from the official PPTX deck
- Catches 20+ common LLM hallucinations (fake `grIcon` names, wrong hex codes, gradient fills that don't exist)
- Exports to SVG and PNG via the draw.io CLI with post-processing

## Why it exists

LLMs consistently get AWS diagram details wrong. They invent icon names that don't exist in the stencil, use pre-2026 color mappings (Databases as red instead of fuchsia, Security as fuchsia instead of red), put managed services inside VPC containers, and produce arrows that don't match any official preset. This skill fixes all of that by providing verified ground-truth references and automated validation.

## Structure

```
├── SKILL.md                            # Main skill file — workflow, rules, checklist
├── assets/
│   └── aws-diagram-template.drawio     # Starter template for new diagrams
├── references/
│   ├── aws-fundamentals.md             # Hard rules: colors, containers, VPC, arrows
│   ├── aws-icon-catalog.md             # Full resIcon name + color catalog (155+ services)
│   ├── aws-diagram-guidelines.md       # Official AWS diagramming best practices
│   ├── layout-and-edges.md             # Arrow presets, layout patterns, spacing, containers
│   ├── icons-and-styles.md             # Icon style pattern, labels, canvas sizing, export
│   ├── anti-slop-guards.md             # Common LLM mistakes with fixes
│   └── updating-from-deck.md           # Runbook for syncing with new AWS icon releases
└── scripts/
    ├── validate_drawio.py              # XML structure + layout anti-pattern validator
    ├── validate_aws_fidelity.py        # AWS-2026 deck fidelity checks (colors, fonts, arrows)
    ├── export_diagrams.py              # Export + post-process pipeline
    ├── inspect_aws_deck.py             # Inspect any AWS Architecture Icons PPTX
    └── extract_service_colors.py       # Generate per-service color map from deck
```

## Installation

Copy the `drawio-diagrams/` folder into your Kiro skills directory:

```bash
cp -r drawio-diagrams ~/.kiro/skills/
```

### Prerequisites

- [Kiro](https://kiro.dev) IDE
- [draw.io CLI](https://github.com/jgraph/drawio-desktop/releases) (for SVG/PNG export)
- Python 3.9+ (for validators and export scripts)

## Usage

The skill activates automatically when you ask Kiro to create AWS architecture diagrams, `.drawio` files, or export diagrams to SVG/PNG.

**Typical workflow:**
1. Describe the architecture you want to diagram
2. The skill reads its references, plans a layout, and generates `.drawio` XML
3. Runs `validate_drawio.py` to catch errors
4. Exports to SVG/PNG via `export_diagrams.py`

**Manual validation:**
```bash
python3 scripts/validate_drawio.py path/to/diagram.drawio
python3 scripts/export_diagrams.py .
```

## Updating for new AWS icon releases

When AWS publishes a new Architecture Icons deck (quarterly):

```bash
python3 scripts/inspect_aws_deck.py path/to/new-deck.pptx all
```

Then follow `references/updating-from-deck.md` to update the catalog and validator.

## What the validators catch

- Icon `fillColor` not in the 7 official AWS category colors
- Per-service color mismatch vs. PPTX ground truth (e.g., Aurora must be `#C925D1`)
- Non-existent `resIcon` or `grIcon` names (catches hallucinated stencil names)
- Wrong container styles (`group_public_subnet` doesn't exist, VPC must use `group_vpc2`)
- Arrow style violations (wrong color, width, arrowhead, or rounded corners)
- Managed services incorrectly placed inside VPC containers
- Font/size violations (must be 12pt Arial `#232F3E`)
- Layout anti-patterns (overlapping arrows, off-grid coordinates, dead zones)

## License

[MIT](LICENSE)

## Acknowledgments

- AWS service icon names and stencil definitions from [jgraph/drawio](https://github.com/jgraph/drawio) (Apache 2.0)
- Style rules verified against the [AWS Architecture Icons](https://aws.amazon.com/architecture/icons/) deck (R23-2026.01.30)
- Built for use with [Kiro](https://kiro.dev)
