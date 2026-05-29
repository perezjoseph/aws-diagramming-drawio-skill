# Updating the catalog from a new AWS Architecture Icons deck

AWS ships a new deck **quarterly** (end of January, April, July; no Q4 release).
Each release changes at least one of: icon colors, new services, renamed
services, arrow preset, or the deck's aspect ratio. This file is the runbook
for re-syncing the drawio-diagramming skill to a new release.

The skill **does not bundle** the PPTX — it's ~17 MB and AWS considers it a
living asset. We download it on demand, inspect it with bundled scripts, and
update the catalog diffs into git.

## 1. Download the deck

Go to [aws.amazon.com/architecture/icons](https://aws.amazon.com/architecture/icons/)
and copy the "Light BG" deck URL. The URL pattern is roughly:

```
https://d1.awsstatic.com/webteam/architecture-icons/...
AWS-Architecture-Icons-Deck_For-Light-BG_<MMDDYYYY>.pptx
```

Save it anywhere — do NOT commit the PPTX:

```bash
curl -L -o /tmp/aws-icons.pptx \
  "https://d1.awsstatic.com/.../AWS-Architecture-Icons-Deck_For-Light-BG_04302026.pptx"
```

## 2. Run the self-describing inspector

The skill ships `scripts/inspect_aws_deck.py` — a swiss-army tool that unpacks
any AWS deck PPTX and reports everything the catalog depends on.

```bash
python3 scripts/inspect_aws_deck.py /tmp/aws-icons.pptx all
```

Subcommands you can run individually:

| Subcommand | Reports |
|------------|---------|
| `colors [DESCR ...]` | Fill hex for every service icon (or filtered subset) |
| `sizes` | Service icon, resource icon, group decorator, callout sizes + slide canvas dimensions |
| `containers` | Font weight and size on every container label on slides 21 and 25 |
| `arrows` | Preset arrow spec from slide 27 (weight, dash, head/tail, prstGeom) |
| `fonts` | Theme font stack (majorFont + minorFont per theme) |
| `all` | Runs every report — best for a release-to-release diff |

The inspector prints the release identifier from slide 1 (e.g.
`Release 23-2026.01.30`) so you can confirm which deck version you're looking
at.

## 3. Diff against the current catalog

For each report section, compare against the corresponding area of
`references/aws-icon-catalog.md`:

### Category colors

The `colors` report prints `Service → hex`. If any hex changed for a service,
update these three places in the catalog:

1. The **Service → Color table** at the top of `aws-icon-catalog.md` (§Verified
   Service → Color Mapping).
2. The **Official AWS Category Colors** table (§Official AWS Category Colors).
3. The **per-category service tables** further down (each category header
   shows its `fillColor`).

If a category's color shifted wholesale (e.g. Security moved fuchsia → red
in the 2025→2026 transition), also update:

- `SKILL.md` § AWS Fundamentals — the 7-color table
- `references/anti-slop-guards.md` — any rule that named the old color

### Service renames

Services occasionally get renamed (`QuickSight` → `Quick Suite`, 2026). When
the deck's descr string changes:

1. Add the new name as the primary entry in the service table for the new
   category (Quick Suite is in Business Apps).
2. Keep the legacy stencil ID (`quicksight`) documented under the old category
   as a fallback for pre-rename deployments.
3. Update the **Service → Color Mapping** gotcha section with the rename note.
4. Note whether drawio's `aws4.xml` ships the new stencil — search it with
   `strings /Applications/draw.io.app/Contents/Resources/app.asar | grep
   'name="<new_name>"'`. If yes, use `resIcon=<new_stencil>`; if no, embed the
   extracted SVG.

### Icon sizes and canvas

The `sizes` report gives the authoritative pixel dimensions. Update the
**Canvas + icon sizing** table in `references/icons-and-styles.md` if any value
changes. The drawio canvas proportion formula (`icon_drawio = 48 ×
canvas_width / 1280`) only needs revisiting if the deck changes its slide
canvas from 1280 × 720.

### Arrow preset

The `arrows` report shows line weight, dash, head/tail types, and prstGeom.
If any of these change, update:

- `SKILL.md` § AWS Fundamentals (arrow preset subsection)
- `references/layout-and-edges.md` § AWS Preset Arrow Styles
- `scripts/validate_drawio.py` — the `OFFICIAL_ARROW_STROKE`,
  `AWS_ARROW_WIDTHS`, and arrow-head-check constants near line ~2370
- `references/anti-slop-guards.md` arrow rows

The deck's preset is **1.25pt black, headEnd `type="arrow" w="med" len="sm"`,
solid**. Drawio renders that as either `endArrow=classic;endFill=0` (hollow
outline) or `endArrow=classic;endFill=1` (solid filled) depending on
interpretation — inspect the actual render and pick the one that matches.

### Container labels

The `containers` report shows weight (bold/regular) and point size for every
container label on slides 21 and 25. Update `aws-icon-catalog.md` § AWS Group
Containers if the deck ever shifts to bold or a non-12pt size. Drawio
containers must then set/clear `fontStyle=1` and change `fontSize` to match.

### Fonts

The `fonts` report prints majorFont and minorFont from each theme.
`theme1.xml` and `theme2.xml` are the deck's primary themes. If the body font
changes from Arial, update:

- `references/icons-and-styles.md` § Label Font
- `scripts/validate_drawio.py` (the `Label font` check, near line ~2320)
- `assets/aws-diagram-template.drawio` (replace every `fontFamily=Arial;`)

## 4. Re-validate the starter template and any existing diagrams

```bash
python3 scripts/validate_drawio.py assets/aws-diagram-template.drawio
find . -name '*.drawio' -exec python3 scripts/validate_drawio.py {} \;
```

Fix any warnings the updated catalog now surfaces.

## 5. Commit

```
git checkout -b update-aws-icons-<release-id>
git add references/ scripts/ SKILL.md assets/
git commit -m "Update catalog to AWS Architecture Icons Release <ID>"
```

Reference the AWS deck's release identifier in the commit message so future
readers can map the skill version to the deck version.

## Troubleshooting

**"I downloaded the deck but the inspector finds 0 slides."**
Make sure you saved the `.pptx` file, not a `.ppt` (legacy binary) or a
landing-page HTML. PPTX files are zip archives — you can verify with
`unzip -l <file>.pptx` (should list `ppt/slides/*.xml`).

**"A service name I expect shows NOT FOUND."**
The `descr` strings in the deck vary between releases. Run
`python3 scripts/inspect_aws_deck.py <deck> colors` with NO filter to see
every descr string, then re-run with the exact string you find. Examples of
non-obvious names:
- `Amazon Simple Storage Service (Amazon S3) service icon.` (not just "S3")
- `AWS Identity and Access Management (IAM) service icon.` (not just "IAM")
- `Amazon Quick Suite service icon.` (renamed from QuickSight)

**"drawio MCP search_shapes returns 0 results for a service I know exists."**
The drawio MCP library exposes a CURATED SUBSET. The full stencil list lives
in drawio's app bundle — search with
`strings /Applications/draw.io.app/Contents/Resources/app.asar |
grep 'name="<query>"'`. If the stencil exists in the bundle, the
`mxgraph.aws4.<name>` style works in your `.drawio` file even though the MCP
doesn't show it.
