# Icons, Styles, and Export

AWS icon patterns, label positioning, CLI installation, and export.
Parent skill: drawio-diagrams

---

## AWS Icon Style

Filled icons — a **colored square tile with a white line-art glyph**. This is the
resourceIcon pattern.

### Canvas + icon sizing (for AWS-summit-grade output)

Ground truth from the 2026 AWS Architecture Icons deck
(`AWS-Architecture-Icons-Deck_For-Light-BG_01302026.pptx`):

| Element | Exact deck size | Derivation |
|---------|-----------------|------------|
| Slide canvas | **1280 × 720 px** (13.333" × 7.5", 16:9) | `ppt/presentation.xml` `<p:sldSz>` |
| Service icon | **48 × 48 px** (0.500") | Verified on slides 20–21 |
| Group decorator (corner icon) | **40 × 40 px** (0.417") | Verified on slide 25 (Groups) |
| Small callout (complex diagrams) | **≈29 × 29 px**, **11pt** bold white | Verified on slide 18 |
| Large callout (simple diagrams) | **≈35 × 35 px**, **14pt** bold white | Verified on slide 18 |

**Drawio canvas must be 16:9.** The typical drawio default is 1600 × 1000 (1.6
ratio); set `pageHeight=900` so the diagram drops onto a widescreen slide
(1280 × 720) with zero letterboxing. Zoom is uniform and icon sizes stay
perfectly proportional.

**Drawio icon size: 60 × 60 px on a 1600-wide canvas.** When that canvas scales
to the deck's 1280 wide, 60 × (1280/1600) = 48 px exactly — matching the deck
standard. If you change the canvas width, recompute: `icon_drawio = 48 ×
canvas_width / 1280`.

**Drawio callout size: 20 × 20 px on a 1600-wide canvas.** Scales to ~16 px on a
1280 slide, which is visually equivalent to the deck's "small callout" style
(the deck's 29 px callouts carry larger text; drawio renders crisp text at
smaller sizes, so 20 px reads the same).

### resourceIcon Pattern (Most Services)

```
shape=mxgraph.aws4.resourceIcon;
resIcon=mxgraph.aws4.<SERVICE>;
fillColor=<CATEGORY_COLOR>;
strokeColor=#ffffff;
fontFamily=Arial;
```

**The `fontFamily=Arial` is mandatory for every labeled cell** — it matches the
2026 deck's theme1/theme2 minor font (verified from `ppt/theme/theme1.xml`
`<a:minorFont><a:latin typeface="Arial">`). Without it, drawio defaults to
Helvetica which renders slightly differently and is an instant tell that the
diagram wasn't produced to AWS standard.

**Complete example — Lambda (Compute, `#ED7100`):**

```xml
<mxCell id="lambda" value="Order Processor&#xa;AWS Lambda"
  style="sketch=0;points=[[0,0,0],[0.25,0,0],[0.5,0,0],[0.75,0,0],[1,0,0],[0,1,0],[0.25,1,0],[0.5,1,0],[0.75,1,0],[1,1,0],[0,0.25,0],[0,0.5,0],[0,0.75,0],[1,0.25,0],[1,0.5,0],[1,0.75,0]];outlineConnect=0;fontColor=#232F3E;fontFamily=Arial;fillColor=#ED7100;strokeColor=#ffffff;dashed=0;verticalLabelPosition=bottom;verticalAlign=top;align=center;html=1;fontSize=12;fontStyle=0;aspect=fixed;pointerEvents=1;shape=mxgraph.aws4.resourceIcon;resIcon=mxgraph.aws4.lambda"
  vertex="1" parent="1">
  <mxGeometry x="500" y="300" width="60" height="60" as="geometry" />
</mxCell>
```

### Direct Shape (No resourceIcon Variant)

Some resources only exist as direct shapes (IGW, NAT GW, IAM Role, IAM Policy,
EC2 Instance, Lambda Function).

```
shape=mxgraph.aws4.internet_gateway;
fillColor=#8C4FFF;
strokeColor=#ffffff;
```

See `aws-icon-catalog.md` → *Resource-Level Icons* for the full list.

---

## Label Positioning

AWS rule (slide 17 of the deck): labels sit **below** the icon, **center-aligned**,
12pt Arial, color `#232F3E`.

Drawio defaults label position based on style:

- **Main flow icons** (icon below labels, horizontal arrows): use
  `verticalLabelPosition=bottom;verticalAlign=top` (label BELOW icon — AWS standard)
- **When labels would collide with arrows from below**: switch to
  `verticalLabelPosition=top;verticalAlign=bottom` (label ABOVE icon)

Use `&#xa;` for line breaks:
```
value="Order Processor&#xa;AWS Lambda"
```

### Label Content Rules (AWS-Official)

- Always include `AWS` or `Amazon` prefix in the service name
- Maximum 2 lines — break after the 2nd word of the service name if needed
  (`AWS` + newline + `Elastic Beanstalk`)
- Never break mid-word
- Role-first naming for your own naming: **what it does, then the service**
  - Good: `Order Processor\nAWS Lambda`
  - Bad: bare `Lambda`

### Label Font

- **Font family**: Arial (AWS uses no alternative)
- **Size**: 12pt (16pt for Training & Certification diagrams)
- **Weight**: Regular (bold only on group labels for emphasis if needed)
- **Color**: `#232F3E` (AWS Smile navy, very dark near-black)

---

## Common Icon Gotchas

See `aws-icon-catalog.md` for the full list. Highlights:

- CloudWatch → `cloudwatch_2` (the `cloudwatch` name is the legacy icon)
- IAM → `identity_and_access_management` (not `iam`)
- EBS → `elastic_block_store`, EFS → `elastic_file_system`
- OpenSearch → `elasticsearch_service` (legacy stencil name)
- S3 Glacier → `glacier`, EC2 Auto Scaling → `auto_scaling2`
- ECS/EKS/ECR → use full names: `elastic_container_service`, etc.

**Developer Tools do NOT use a gradient.** The category is red `#DD344C`, flat fill.
Any reference you see to a blue `#3334B9` with `gradientColor=#4D72F3` was from an
older, incorrect skill version.

---

## Light Theme Colors

```
fontColor=#232F3E    (primary text — AWS Smile navy)
strokeColor=#232F3E  (dark arrows)
strokeColor=#ffffff  (white icon glyph stroke)
fontColor=#666666    (secondary annotations)
fillColor=#F1F3F3    (pale background accent)
```

For accurate AWS category colors, see
`aws-icon-catalog.md` → *Official AWS Category Colors*.

---

## Installing the draw.io CLI

| Platform | Install | Binary | On PATH? |
|----------|---------|--------|----------|
| macOS | `brew install --cask drawio` | `/Applications/draw.io.app/Contents/MacOS/draw.io` | No — alias needed |
| Windows | `winget install JGraph.Draw` | `%LOCALAPPDATA%\Programs\draw.io\draw.io.exe` | No |
| Linux | `sudo snap install drawio` | `/snap/bin/drawio` | Yes |

macOS alias:
```
echo 'alias drawio="/Applications/draw.io.app/Contents/MacOS/draw.io"' >> ~/.zshrc
```

---

## Export

Use the bundled Python script — it runs the CLI export and applies the post-processing
pipeline:

```bash
python3 scripts/export_diagrams.py [directory]   # defaults to static/, use . for cwd
```

Manual single-file export (then post-process SVG):
```bash
drawio --export --format svg --embed-svg-images --output OUT.svg INPUT.drawio
drawio --export --format png --output OUT.png INPUT.drawio
```

**Never** use `--svg-theme dark` — it breaks category colors and inverts foreground
text in ways that violate the light-BG system.
