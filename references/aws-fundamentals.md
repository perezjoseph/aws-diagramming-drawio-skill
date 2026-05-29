# AWS Fundamentals (Must Not Violate)

Guardrails verified from the official AWS Architecture Icons deck (R23-2026.01.30)
and the canonical `Sidebar-AWS4.js`. Every rule here has been a recurring LLM mistake.

Parent skill: drawio-diagrams

---

## The 7 Category Colors

Do not invent variants. Every AWS service icon uses exactly one of these fills:

| Hex | Categories |
|-----|-----------|
| `#ED7100` | Compute / Containers / Media |
| `#7AA116` | Storage / IoT / Cloud Financial Mgmt |
| `#DD344C` | **Security** / Business Apps / Front-End Web & Mobile / Customer Experience |
| `#8C4FFF` | Networking / Analytics / Serverless / **Machine Learning (SageMaker)** |
| `#E7157B` | App Integration / Management |
| `#01A88D` | AI/ML (Bedrock) / End User Computing / Migration |
| `#C925D1` | **Databases** / Developer Tools / Customer Enablement |

---

## The Four Gotchas That Bite Every Time

Verified from R23-2026.01.30 deck SVGs:

1. **Databases is FUCHSIA `#C925D1`** — NOT red, NOT purple. Aurora, DynamoDB, RDS,
   Neptune, ElastiCache, MemoryDB, DocumentDB all render as `#C925D1`.
2. **Security is RED `#DD344C`** — NOT fuchsia. Changed from fuchsia in pre-2026
   decks. IAM, Secrets Manager, Cognito, KMS, WAF, GuardDuty all render as `#DD344C`.
3. **SageMaker is PURPLE `#8C4FFF`** — NOT AI teal. AWS categorizes it under ML
   (Analytics purple), not AI. Bedrock/Bedrock AgentCore stay teal `#01A88D`.
4. **QuickSight was renamed to "Amazon Quick Suite"** in 2026 (red `#DD344C`), but
   the drawio stencil still ships `resIcon=mxgraph.aws4.quicksight` which renders
   the old purple glyph. Match the fillColor to the visual glyph you want.

**When in doubt, verify against the official deck:**
```bash
python3 scripts/inspect_aws_deck.py \
    /path/to/AWS-Architecture-Icons-Deck_For-Light-BG_*.pptx \
    colors "Amazon Aurora service icon."
```

---

## Container Fills

**All AWS containers use `fillColor=none`** (verified against slides 20, 21, 25 of
the 2026 deck — every `<p:spPr>` on a rectangle/roundRect container has
`<a:noFill/>`). The pale teal / pale green subnet fills that older references show
are NOT in the current deck. Emit `fillColor=none` on every group container; let the
stroke color + corner grIcon carry the semantics.

### Container Gotchas

- `group_public_subnet` / `group_private_subnet` **do not exist**. Use
  `group_security_group` with different stroke/fill colors.
- Security group has **no grIcon** — it's a plain dashed rect with stroke `#DD3522`.
- Availability Zone has **no grIcon** — plain dashed rect, stroke `#147EBA`.
- Auto Scaling group uses `shape=mxgraph.aws4.groupCenter` (not `group`), dashed orange.
- VPC uses `group_vpc2` (not legacy `group_vpc`).

See `aws-icon-catalog.md` → *Container Style Table* for the full style reference
with ready-to-paste XML examples.

---

## VPC Membership

Only services that run on customer-managed ENIs in customer subnets belong inside
the VPC box. Managed services live outside the VPC, still inside AWS Cloud. This is
the single most common architecture-correctness mistake.

### Inside VPC

EC2, Fargate, ECS, EKS workers, RDS, Aurora, ElastiCache, Redshift, ALB/NLB/CLB,
NAT gateways, VPC endpoints, Lambda *only if VPC-attached*.

### Outside VPC (inside AWS Cloud only)

S3, DynamoDB, SQS, SNS, Bedrock, Bedrock AgentCore, SageMaker (managed endpoint),
Quick Suite, QuickSight, CloudWatch, X-Ray, API Gateway, Amplify, CloudFront,
CodeCommit, CodePipeline, CodeBuild, CodeDeploy, Secrets Manager, Step Functions,
Glue, Athena.

### VPC Connection Bridge

When a managed service outside the VPC needs data inside (e.g. Quick Suite reading
Aurora), draw the connection via a `resIcon=mxgraph.aws4.vpc_privatelink` icon
between them — never a direct arrow piercing the VPC border.

---

## Custom Dashed Containers for Operational Concerns

Not every grouping is a VPC/subnet. Delivery pipelines
(CodeCommit+CodePipeline+CodeDeploy) and observability (CloudWatch+X-Ray) almost
always cross VPC boundaries and benefit from their own visual grouping.

Use a plain dashed rectangle (`dashed=1;fillColor=none`) with a color that matches
the services inside — typically pink `#E7157B`, purple `#C925D1`, or gray `#7D8998`.

See `layout-and-edges.md` → *Custom Dashed Containers for Operational Concerns* for
templates and XML examples.

---

## Arrow Defaults (2026 AWS-Official Preset)

Verified from slide 16 + slide 27 + drawio rendering:

- Width: **1.25pt** (`strokeWidth=1.25`)
- Color: **black `#000000`** (not navy `#232F3E`)
- Head: solid filled triangle → `endArrow=classic;endFill=1;endSize=8`
  - PowerPoint's slide-16 label "Open Arrow Size 4" describes the **arrow preset
    menu item**, not a hollow outline. When rendered, both PowerPoint and drawio
    show it as a solid filled triangle with sharp edges — the same shape drawio
    calls `classic`.
  - Do NOT use `endArrow=open;endFill=0` — that renders a thin stealth V, which is
    a different arrow style not used by the 2026 deck.
- Solid (no dash)
- Corners: **sharp** (`rounded=0`) — miter join, never rounded

### Three Allowed Arrow Shapes

Pick ONE per diagram — never mix:

1. **Straight lines** (horizontal / vertical) — the preferred default. In drawio:
   `edgeStyle=orthogonalEdgeStyle` with connected icons sharing an X or Y center so
   the edge renders as a single perpendicular segment.
2. **Right-angle / elbow** — for connections that can't be straight because the two
   icons are at different rows AND different columns. In drawio:
   `edgeStyle=orthogonalEdgeStyle`, one natural L-bend (zero waypoints).
3. **Diagonal lines** — last resort *"in the instance where right angles are not
   possible"* (slide 16). In drawio: `edgeStyle=none` producing a direct diagonal.

Straight + elbow is fine (same family). Diagonal must stand alone.

### Four Head/Tail Combinations

Only 4 exist: →, ←, ↔, —. Custom request/data/async styles (thick/thin/dashed) are
allowed but must be explained in a legend.

See `layout-and-edges.md` → *AWS Preset Arrow Styles* for the full drawio style
mapping and extended semantic arrow table.

---

## Labels

- **Font**: 12pt Arial, color `#232F3E`
- **Position**: below icon, center-aligned
- **Max**: 2 lines, never break mid-word
- **Prefix**: always "AWS" or "Amazon" (never bare "Lambda" or "S3")

---

## Icons

- Filled colored-square tile, white glyph
- Size: **60×60 px** in drawio
- Never crop, flip, rotate, or use PNG
- No `gradientColor` — every regular category icon is flat fill

See `icons-and-styles.md` for the full icon style pattern and label positioning rules.
