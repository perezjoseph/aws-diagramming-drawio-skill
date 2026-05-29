---
name: drawio-diagramming
description: >
  Creates and exports draw.io XML architecture diagrams for AWS services. Uses filled AWS service icons,
  orthogonal edge routing, row-based layouts, and storytelling-first design. Handles CLI export to SVG/PNG
  with post-processing. Use when the user mentions AWS diagrams, draw.io, .drawio files, AWS architecture
  diagrams, system diagrams, infrastructure visuals, SVG/PNG export, AWS service icons, visualize AWS
  architecture, create an architecture diagram, or troubleshooting diagram rendering issues.
---

# draw.io Diagram Skill

Create `.drawio` XML files and export to SVG/PNG via the draw.io CLI.

## Bundled Resources

```
drawio/
├── SKILL.md                               ← This file
├── assets/aws-diagram-template.drawio     ← Starter template — copy for new diagrams
├── references/
│   ├── aws-fundamentals.md                ← Colors, containers, VPC membership, arrows, labels (hard rules)
│   ├── aws-icon-catalog.md                ← Full icon name/color catalog (primary reference)
│   ├── aws-diagram-guidelines.md          ← Official AWS diagramming best practices
│   ├── layout-and-edges.md                ← Arrow preset, layout patterns, grid rules
│   ├── icons-and-styles.md                ← Icon pattern, label positioning, canvas sizing, CLI install, export
│   ├── anti-slop-guards.md                ← Common LLM mistakes and fixes
│   └── updating-from-deck.md              ← Runbook for re-syncing the catalog when AWS ships a new deck
└── scripts/
    ├── export_diagrams.py                 ← Export + post-process pipeline (Python)
    ├── validate_drawio.py                 ← XML + generic layout anti-pattern validator (delegates AWS checks)
    ├── validate_aws_fidelity.py           ← AWS-2026 deck fidelity checks (colors, fonts, arrows, containers, VPC membership)
    ├── inspect_aws_deck.py                ← Inspect any AWS Architecture Icons PPTX (colors, sizes, arrows, fonts)
    └── extract_service_colors.py          ← Generate the per-service color map for validate_aws_fidelity.py
```

Typical workflow:
- Copy `assets/aws-diagram-template.drawio` when creating a new diagram
- Read `references/aws-fundamentals.md` for the hard rules (colors, containers, VPC, arrows)
- Read `references/aws-icon-catalog.md` when you need a `resIcon` name or category color
- Read `references/aws-diagram-guidelines.md` for official AWS rules
- Read `references/layout-and-edges.md` for layout patterns, edge routing, containers, and legends
- Read `references/icons-and-styles.md` for icon patterns, label positioning, CLI install, and export
- Read `references/anti-slop-guards.md` before finalizing any diagram
- Run `scripts/validate_drawio.py <file.drawio>` after generating — fix all FAIL items before exporting
- Run `scripts/export_diagrams.py [directory]` to export (defaults to `static/`, pass `.` for cwd)

When AWS publishes a new icon deck (quarterly release), follow
`references/updating-from-deck.md` and run
`scripts/inspect_aws_deck.py <deck.pptx> all` to diff the new release against
the catalog. Subcommands: `colors` (per-service hex), `sizes` (icon/canvas
dimensions), `containers` (label weight/size), `arrows` (preset spec),
`fonts` (theme stack), `all`.

## AWS Fundamentals (Must Not Violate)

Full rules in `references/aws-fundamentals.md`. The critical guardrails inline:

**7 colors only** — `#ED7100` Compute · `#7AA116` Storage · `#DD344C` Security · `#8C4FFF` Networking/Analytics · `#E7157B` App Integration · `#01A88D` AI/Bedrock · `#C925D1` Databases/DevTools

**4 gotchas:**
1. Databases = FUCHSIA `#C925D1` (not red)
2. Security = RED `#DD344C` (not fuchsia)
3. SageMaker = PURPLE `#8C4FFF` (not AI teal)
4. QuickSight → "Quick Suite" in 2026 (red `#DD344C`); stencil still `quicksight` (purple)

**Containers**: `fillColor=none` always. No `group_public_subnet`/`group_private_subnet`. VPC = `group_vpc2`. Security group = plain dashed rect `#DD3522`. AZ = plain dashed rect `#147EBA`. Auto Scaling = `groupCenter`, dashed `#D86613`.

**VPC membership**: only ENI-resident services inside VPC. Managed services (S3, Bedrock, API GW, Quick Suite, CloudWatch…) outside VPC. Use `vpc_privatelink` bridge icon for cross-boundary data access.

**Arrows**: 1.25pt black `#000000`, `endArrow=classic;endFill=1;endSize=8`, `rounded=0`. Straight/elbow only (no diagonal unless last resort). Never mix diagonal with elbow.

**Labels**: 12pt Arial `#232F3E`, below icon, max 2 lines, always "AWS"/"Amazon" prefix.

**Icons**: 60×60px filled tile, white glyph. No crop/flip/rotate/PNG/gradient.

## Workflow

Follow these steps in order every time you create a diagram:

### Step 1: Define the Story
Answer these four questions before touching any XML:
1. **What is this diagram communicating?** One sentence. If you can't say it in one sentence, split into multiple diagrams.
2. **Who is the actor?** What triggers the flow?
3. **What is the happy path?** Trace trigger → outcome step by step.
4. **What are the supporting concerns?** (persistence, caching, async, monitoring)

### Step 2: Read References
- Read `references/aws-fundamentals.md` — hard rules: colors, containers, VPC membership, arrows
- Read `references/layout-and-edges.md` — arrow styles, container creation, callout rules
- Read `references/icons-and-styles.md` — icon patterns, label positioning
- Read `references/aws-icon-catalog.md` — look up every `resIcon` name and category color you'll need

### Step 3: Plan the Layout
Map the story to a grid. The happy path is the main horizontal row. Supporting concerns go below at the same X. Async/event patterns go to the right. Group related services with dashed containers using category colors. Calculate container sizes from child icons (40px padding).

**Keep it tight.** Use 140px horizontal spacing and 160px vertical spacing between icons as your default — the AWS deck packs icons densely and stretched diagrams read as empty. Size the canvas to fit the content plus a 40px margin on every side. Do NOT default to 1600×900; that's only correct when the diagram genuinely fills it. See `references/layout-and-edges.md` → *Icon Spacing* and *Fit-to-Content Canvas*.

**For VPC / multi-AZ diagrams specifically:**
- **Regional services** (ALB, NLB, API Gateway, CloudFront) sit **between** the AZs or on their own row, centered on the VPC's X-midpoint. They do NOT belong inside a single AZ's subnet.
- **Auto Scaling groups** span both AZs' private subnets as a horizontal band.
- **Nested containers** must clear the parent's title strip — reserve 30px at the top of every container before placing a child container inside it. If an Auto Scaling group covers the "Private subnet" title, the ASG is drawn in the wrong place.
- See `references/layout-and-edges.md` → *Nested Container Title Clearance* and *Cross-AZ and Regional Resources*.

### Step 4: Write the XML
Build the diagram following the XML rules, edge rules, and layout patterns from the references. **Pick arrow style A (AWS RA — uniform arrows, numbered callouts tell the story) by default.** Only use style B (multi-encoding) when numbering alone can't convey the distinction. Use descriptive labels (role first, service name second). Add numbered callouts **on every arrow** (at midpoints), not in a margin column. Add a numbered-steps list below the diagram — plain text rows with small circle markers — describing each step in active voice with the service named.

### Step 5: Check Anti-Slop Guards
Read `references/anti-slop-guards.md` and check your diagram against every pattern. The most common failures:
- Generic labels ("Lambda" instead of "Message Handler\nAWS Lambda")
- Arrow styles mixed without purpose — pick Style A (uniform, numbered) or Style B (multi-encoded) and stick with it
- Flat chain layout (everything in one row — group by domain instead)
- Callouts floating in a margin column instead of sitting on the arrows they label
- Step descriptions that describe the icon ("API Gateway routes requests") instead of the action in context ("API Gateway forwards the POST /forecast request to the Forecast Lambda")

### Step 6: Validate and Export
Run `scripts/validate_drawio.py <file.drawio>` — fix ALL failures and warnings. Then export with `scripts/export_diagrams.py .`

## Diagram Philosophy

A diagram is a visual argument, not a parts list. Every element must serve the narrative.

- **Time flows left-to-right, top-to-bottom** — read diagrams like text
- **Size shows importance** — main flow icons at 60px, monitoring at 48px
- **7-box rule** — more than ~7 primary elements means split into layered diagrams
- **One-screen rule** — must be readable without scrolling or zooming
- **Descriptive labels** — lead with the role, not the service name: "Order Processor\nAWS Lambda" not "Lambda"
- **Every arrow tells a story** — different styles for request flow, data access, async events
- **Always number the flow** — callouts at every step, flow key in legend

## XML Rules

1. Start with `<mxCell id="0"/>` and `<mxCell id="1" parent="0"/>`. All content uses `parent="1"`.
2. Never include XML comments (`<!-- -->`).
3. Always include `html=1` in every cell style.
4. Line breaks: `&#xa;` or `<br>`, never `\n`.
5. Grid-align all coordinates to multiples of 10.
6. All IDs must be unique. `vertex="1"` and `edge="1"` are mutually exclusive.
7. `mxGraphModel` needs `page="1"` and `background="#FFFFFF"`.

## Edge Rules

Every edge needs: `parent="1"`, `<mxGeometry relative="1" as="geometry" />` child, `edgeStyle=orthogonalEdgeStyle`, and **`rounded=0`** (sharp corners at bends — the PPTX uses miter line-joins, never rounded).

**All arrows must be perfectly straight** — purely horizontal or vertical. Align icons so connected pairs share X or Y centers. Never use waypoints; if you need one, the layout is wrong.

**Parallel arrows must not overlap** — when multiple arrows share an icon side, offset exit/entry points (0.25, 0.5, 0.75) so arrows run parallel with padding. All points must stay within icon bounds (0.0-1.0). See `references/layout-and-edges.md` for examples.

**Arrow types tell the story.** Default to Style A (uniform arrows with numbered callouts on each arrow). Use Style B (thick/thin/dashed) only when numbering alone cannot convey the distinction. See `references/layout-and-edges.md` for both style tables.

## Layout

Row-based layout with fixed Y per row. Main flow left-to-right, supporting services below at same X. For detailed patterns, spacing, fan-out rules, and container sizing, see `references/layout-and-edges.md`.

## Icons and Export

60×60px filled AWS icons. For icon patterns, label positioning, CLI install, and export instructions, see `references/icons-and-styles.md`.

## Checklist

Before exporting, verify:

**AWS Fundamentals:**
- [ ] Every category color used is one of the 7 official AWS colors (no invented hexes)
- [ ] Databases icons are FUCHSIA `#C925D1`, not red, not blue
- [ ] Security icons are RED `#DD344C`, not fuchsia
- [ ] Compute icons are `#ED7100` (not `#FF9900` — that's dark-BG theme)
- [ ] All `resIcon` names exist (verify against icon-catalog, especially gotchas: `cloudwatch_2`, `identity_and_access_management`, `elastic_block_store`, `elasticsearch_service`)
- [ ] All `grIcon` names exist — no `group_public_subnet` or `group_private_subnet`
- [ ] Security group is a plain dashed red rect (no grIcon, stroke `#DD3522`)
- [ ] Availability Zone is a plain dashed rect (no grIcon, stroke `#147EBA`)
- [ ] VPC uses `group_vpc2`
- [ ] Auto Scaling uses `shape=mxgraph.aws4.groupCenter`, dashed `#D86613`
- [ ] Container `fontColor` matches the table (e.g., Region stroke `#00A4A6`, font `#147EBA`)

**Canvas & Spacing:**
- [ ] Canvas sized to fit content + 40px margin — not a rigid 1600×900 on a sparse diagram
- [ ] Inter-icon horizontal spacing 140-180px (not 240px+), vertical 160-200px
- [ ] No "dead zone" where two connected icons are >200px apart with nothing between them

**VPC / Multi-AZ Geometry (if applicable):**
- [ ] Regional services (ALB/NLB/API GW/CloudFront) centered between AZs, not inside one AZ
- [ ] Auto Scaling group drawn as a horizontal band spanning both AZs' private subnets
- [ ] Every nested container clears its parent's 30px title strip (no ASG rectangle covering "Private subnet" title text)
- [ ] Aurora writer in AZ1's DB subnet, reader in AZ2's DB subnet, replication arrow between them
- [ ] **Only VPC-resident services inside the VPC box**: EC2/Fargate/ECS/EKS/RDS/Aurora/ElastiCache/ALB/NLB/NAT — nothing else
- [ ] **Managed services outside the VPC** (still inside AWS Cloud): S3, Bedrock, Bedrock AgentCore, SageMaker, Quick Suite, API Gateway, Amplify, CloudWatch, X-Ray, CodePipeline, Lambda (unless VPC-attached)
- [ ] **VPC Connection bridge icon** (`vpc_privatelink`) between any managed service and VPC-interior data store it reads (e.g., Quick Suite → Aurora)
- [ ] **No bare arrow** pierces the VPC border — route through NLB, NAT, VPC endpoint, or PrivateLink bridge

**Operational Concern Groupings:**
- [ ] Delivery pipeline (CodeCommit/CodePipeline/CodeBuild/CodeDeploy) grouped in a dashed rectangle (stroke `#C925D1` or `#E7157B`)
- [ ] Observability (CloudWatch/X-Ray/CloudTrail) grouped in a dashed rectangle (stroke `#7D8998` or `#E7157B`)
- [ ] Custom dashed containers use `dashed=1;fillColor=none`, 12pt Arial regular label matching stroke color

**Story & Structure:**
- [ ] Story defined in one sentence before layout began
- [ ] References read (aws-fundamentals, layout-and-edges, icons-and-styles, icon-catalog)
- [ ] Arrow style chosen (A: uniform + numbered callouts on arrows, or B: multi-encoded + legend) and applied consistently
- [ ] Numbered callouts sit **on the arrows** (not in a margin column), one per step
- [ ] Numbered-steps list below the diagram — active voice, service named, step described in context
- [ ] ≤7 primary elements (split if needed)
- [ ] Descriptive labels — role first, service name second (not bare "Lambda")
- [ ] Every label 12pt Arial `#232F3E`, max 2 lines, prefixed with AWS/Amazon
- [ ] Services grouped by domain using official container presets where possible

**Geometry:**
- [ ] All arrows perfectly straight (no bends, no waypoints)
- [ ] Parallel arrows offset with padding — no overlapping edges on same icon side
- [ ] Supporting nodes directly below parent (same X)
- [ ] Containers sized with 40px padding, ≥5px buffer between nested borders
- [ ] All coordinates grid-aligned to multiples of 10

**XML:**
- [ ] `page="1"`, `background="#FFFFFF"`, all `html=1`
- [ ] Every edge has `parent="1"`, `mxGeometry`, `orthogonalEdgeStyle`, `rounded=0`
- [ ] All IDs unique; no `<!-- -->` comments; no `\n` in labels (use `&#xa;`)
- [ ] Anti-slop guards checked (`references/anti-slop-guards.md`)
- [ ] Validation passes: `scripts/validate_drawio.py` — zero failures, zero warnings
- [ ] Exported via `scripts/export_diagrams.py`

## References

- [draw.io XML Reference](https://github.com/jgraph/drawio-mcp/blob/main/shared/xml-reference.md)
- [draw.io Style Reference](https://github.com/jgraph/drawio-mcp/blob/main/shared/style-reference.md)
- [AWS Architecture Icons](https://aws.amazon.com/architecture/icons/)
- [Sidebar-AWS4.js](https://github.com/jgraph/drawio/blob/dev/src/main/webapp/js/diagramly/sidebar/Sidebar-AWS4.js) — authoritative resIcon names
