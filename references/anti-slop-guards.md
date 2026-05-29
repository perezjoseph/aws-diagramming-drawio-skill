# Anti-Slop Guards

Patterns AI models commonly produce that make AWS diagrams worse. Check every
diagram against every row before exporting.

Parent skill: drawio-diagrams

---

## Icon / Color Slop (AWS-Official)

These are the most common mistakes when an LLM guesses at AWS style:

| Pattern | Fix |
|---------|-----|
| Aurora / DynamoDB / RDS painted red `#DD344C` | Databases are **fuchsia `#C925D1`** in the 2026 deck. "Purple-ish" ≠ red ≠ blue ≠ `#8C4FFF` — use the extracted hex |
| SageMaker painted teal `#01A88D` | SageMaker is **purple `#8C4FFF`** (ML/Analytics) in 2026. Only Bedrock and Bedrock AgentCore use AI teal |
| API Gateway or Load Balancer painted pink `#E7157B` | Networking is **purple `#8C4FFF`**. API Gateway and ELB both use `#8C4FFF` |
| Amplify painted fuchsia or orange | Amplify is **red `#DD344C`** (Front-End Web & Mobile in 2026) |
| IAM / Secrets Manager painted fuchsia | Security moved to **red `#DD344C`** in 2026. Only pre-2026 diagrams use `#C925D1` |
| Database tile painted blue | Databases are **fuchsia `#C925D1`** — no pure blue in the 2026 service palette |
| Compute tile painted `#FF9900` | Use `#ED7100`. `#FF9900` is the dark-BG theme variant |
| Category colors "made up" (e.g. `#3334B9`) | Only 7 colors exist — see `aws-icon-catalog.md`. When unsure, run `scripts/inspect_aws_deck.py <deck.pptx> colors` against the official PPTX deck |
| Gradient fills on service icons | 2026 deck uses **flat fills only**. Gradients on service tiles indicate an outdated stencil pack or an LLM guess |
| `resIcon=mxgraph.aws4.iam` | Use `identity_and_access_management` (not `iam`) |
| `resIcon=...cloudwatch` (legacy) | Use `cloudwatch_2` — the current icon |
| `resIcon=...ebs` | Use `elastic_block_store` |
| `resIcon=...glacier` inverted to `s3_glacier` | Stencil name is `glacier` |
| `resIcon=...opensearch_service` | Use `elasticsearch_service` (legacy stencil name) |
| `resIcon=...quicksight` + `fillColor=#DD344C` | QuickSight was renamed to Quick Suite in 2026 (red), but the old glyph is still named `quicksight` and AWS retained it as purple. Pick: old QuickSight → `fillColor=#8C4FFF`; modern Quick Suite → `fillColor=#DD344C` + new glyph when it ships |
| Icons cropped, flipped, or rotated | Never modify AWS icon geometry |
| Icons at varying sizes | 60px main, 48px secondary — don't sprinkle random sizes |
| PNG instead of SVG | Always SVG — AWS deck says so explicitly |

## Container Slop (AWS-Official)

| Pattern | Fix |
|---------|-----|
| `grIcon=mxgraph.aws4.group_public_subnet` | **Does not exist.** Use `group_security_group` with stroke `#7AA116` and fill `#F2F6E8` |
| `grIcon=mxgraph.aws4.group_private_subnet` | **Does not exist.** Use `group_security_group` with stroke `#00A4A6` and fill `#E6F6F7` |
| Security group with a grIcon | Plain rect, **no grIcon**, stroke `#DD3522` |
| Availability Zone with a grIcon | Plain rect, **no grIcon**, stroke `#147EBA`, dashed |
| VPC using `group_vpc` | Use `group_vpc2` (the current artwork) |
| Auto Scaling group using `shape=...group` | Use `shape=mxgraph.aws4.groupCenter` with `align=center`, `spacingTop=25` |
| Auto Scaling solid stroke | Must be `dashed=1` — indicates elasticity |
| Region solid stroke | Must be `dashed=1` — indicates geographic boundary |
| Group `fontColor` same as stroke | Not always — Region stroke `#00A4A6` but fontColor `#147EBA`. See `aws-icon-catalog.md` |
| Nested groups touching borders | Maintain ≥ 0.05" (~5px) buffer on all sides |
| Using AWS Cloud as the only container when the story is internal architecture | Use AWS Account or no outer container when more appropriate |
| Creating a custom group for services when an official preset exists | Prefer VPC / Subnet / ASG / Step Functions / etc. presets |
| **S3 inside a VPC container** | S3 is a regional service — move it OUTSIDE the VPC box, inside AWS Cloud only |
| **Bedrock / AgentCore / SageMaker endpoint inside VPC** | Managed AI services live outside the VPC. Move them to AWS Cloud; if they need VPC data, add a `vpc_privatelink` bridge icon |
| **Quick Suite / QuickSight inside VPC** | Quick Suite is a managed service. Draw it outside the VPC and add a `vpc_privatelink` (VPC Connection) icon between Aurora/RDS and Quick Suite |
| **Amplify / API Gateway / CloudFront inside VPC** | These are edge/regional services — leave them in AWS Cloud only, not the VPC box |
| **Direct arrow from Quick Suite to Aurora crossing the VPC border** | Misrepresents the architecture. Add a `vpc_privatelink` bridge icon and route `aurora → vpc_conn → quick_suite` |
| **CodeCommit / CodePipeline / CodeDeploy with no container** | Group them in a dashed rectangle labeled "Delivery pipeline" (stroke `#C925D1` or `#E7157B`). See `aws-icon-catalog.md` for custom container style |
| **CloudWatch / X-Ray with no container** | Group them in a dashed rectangle labeled "Observability" (stroke `#7D8998` gray or `#E7157B` pink). Signals that they span across all other services |
| Custom dashed container with `fillColor` set | Keep `fillColor=none` — same rule as every AWS container |
| Custom dashed container with bold label | 12pt Arial **regular** — same rule as every AWS container |

---

## Content Slop

| Pattern | Fix |
|---------|-----|
| Generic labels ("Lambda", "S3") | Role-first: "Order Processor\nAWS Lambda" |
| Placeholder text ("Service A") | Infer from context or ask the user |
| Dropping the "AWS" or "Amazon" prefix | Include it on every label |
| Short forms before the full name | Introduce the full name once, then short form |
| Reusing a short form for two services | Each short form must be unique per diagram |
| Label lines breaking mid-word | Break after the 2nd word of the service name |
| Every AWS service included | 7-box rule; split into layered diagrams |
| Missing legends when using non-preset arrow styles | Legend required for any style not in AWS's 4 presets |
| Unlabeled arrows with no callouts | Label arrows or add numbered callouts |
| Flow Key wording describes icons | Step text = verb + service + object; describe the action, not the parts |
| Callouts in margin column | Place on the relevant arrow (midpoint), or above-left of the icon |
| Numbered edgeLabels on arrows (labelBackgroundColor badges) | Use proper callout ellipses (fillColor=#232F3E, strokeColor=#FFFFFF, bold white number). edgeLabel badges are not the AWS callout style — slide 18 specifies filled circles |
| Mixing large + small callouts | Pick one size per diagram |
| Letters or emojis as callouts | Numbers only (1, 2, 3...) |

---

## Layout Slop

| Pattern | Fix |
|---------|-----|
| Scattered icon placement | Row-based layout with fixed Y per row |
| Diagonal-looking orthogonal edges | Align connected nodes on same row/column; ensure exit/entry points produce axis-aligned segments |
| Crooked arrow segments | Every segment must be purely horizontal or vertical. If exit Y ≠ entry Y on a side-to-side connection, align the icons or adjust exit/entry points |
| Top/bottom exit used when icons don't share X center | Use side-to-side `exitX=1,exitY=0.5 → entryX=0,entryY=0.5` so the router's L-bend looks intentional. Or move the child to share X. See `layout-and-edges.md` → *Vertical Column Alignment* decision tree |
| Arrow enters node body | Entry/exit points must be on the perimeter (0 or 1 on at least one axis), never inside the node |
| Overlapping labels/text | Space icons so label zones don't overlap adjacent icons. ≥80px vertical gap for bottom-labeled icons |
| Spider-web edges from one node | Limit to 2-3 connections; restructure |
| Tiny icons on huge canvas | Size canvas to content; 60px icons, 160px spacing |
| Arrows painted navy `#232F3E` | 2026 preset is **black `#000000`**. Navy is only the icon tile background and text color, not arrow stroke |
| Arrow width 1pt or 2pt | 2026 preset is **1.25pt**. 2pt only for Training & Certification diagrams |
| `endArrow=classic;endFill=0` (hollow outline triangle) | 2026 deck slide 16 says "Open Arrow Size 4" — that's PowerPoint's UI name for the preset, but it renders as a SOLID FILLED triangle. Use `endArrow=classic;endFill=1;endSize=8` |
| `endArrow=open;endFill=0` (thin V-stealth) | Not the AWS preset. Use `endArrow=classic;endFill=1` (solid filled triangle) |
| Mixing elbow + diagonal arrows in the same diagram | Slide 16 allows three shapes (straight / right-angle / diagonal) but says to "use straight lines and right angles wherever possible." Pick ONE shape and stick with it — diagonal only as last resort, applied uniformly |
| No visual hierarchy | Edge style hierarchy: thick=main, thin=data, dashed=async (but label these in a legend — AWS doesn't use them natively) |
| Fan-out from same exit point | Chain pattern or vertical fan-out with offset exit/entry |
| Overlapping parallel arrows | Offset exit/entry points (0.25, 0.5, 0.75) — keep within icon bounds |
| Callouts at icon center Y | Place above icon, never at arrow routing Y |
| Phase labels overlapping icons | 30px clearance from nearest label |

---

## Typography Slop

| Pattern | Fix |
|---------|-----|
| Labels at inconsistent sizes | 12pt Arial throughout (16pt for Training & Cert) |
| Non-Arial font on icon labels | Arial only — AWS specifies no alternative |
| Label color anything other than `#232F3E` | Body labels must be `#232F3E` |
| Bold labels scattered | Plain labels are regular weight; bold only for group headings if emphasis is needed |
| `\n` in label values | Use `&#xa;` or `<br>` — `\n` is literal in drawio XML |

---

## XML Slop

| Pattern | Fix |
|---------|-----|
| Edge `parent` set to container | Always `parent="1"` |
| Missing `<mxGeometry relative="1">` on edges | Always include child element |
| `--svg-theme dark` in export | Never; post-process SVGs |
| Missing `edgeStyle=orthogonalEdgeStyle` | Always use orthogonal |
| `container=1` on hand-written groups | Use `container=0` — drawio sets 1 when editing visually |
| Redundant AWS Cloud group | Only when it adds meaning — AWS Account or no outer wrapper is often better |
| Wrong `resIcon` names | Check `references/aws-icon-catalog.md` |
| XML comments `<!-- -->` | Never include |
| Missing `html=1` | Always include in every style |
| `\n` in labels | Use `&#xa;` or `<br>` |
| Self-closing edge cells | Include `<mxGeometry>` child |
| Off-grid coordinates | Snap to multiples of 10 |
| Duplicate IDs | Every `id` must be unique across the diagram |

---

## Final Sanity Check

Before declaring a diagram done:

1. **Every color** used is either an AWS category color (7 total) or a
   documented neutral (structural colors list). No invented hexes.
2. **Every grIcon** reference is a real stencil name (verify against the group
   container table in `aws-icon-catalog.md`).
3. **Every arrow** is perfectly horizontal or vertical. No diagonals, no waypoints.
4. **Every label** is 12pt Arial `#232F3E`, includes "AWS"/"Amazon", max 2 lines.
5. **Numbered callouts** cover every step of the flow, with a flow-key legend.
6. **Container nesting** respects the canonical hierarchy (AWS Cloud → Account →
   Region → VPC → AZ → Subnet → ASG → EC2).
7. **Validation script** (`scripts/validate_drawio.py`) passes with zero failures and
   zero warnings.
