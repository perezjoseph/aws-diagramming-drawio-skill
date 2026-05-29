# Layout and Edge Rules

This reference covers layout patterns, edge routing, containers, legends, and callouts —
reconciled with the official **AWS Architecture Icons** deck (R23-2026.01.30) and the
canonical drawio `Sidebar-AWS4.js` stencil definitions.

Parent skill: drawio-diagrams

---

## Perfectly Straight Connections

Every arrow must be perfectly straight — purely horizontal or purely vertical. No
bends, no waypoints. Align icons so connected pairs share X (vertical) or Y (horizontal)
centers.

AWS style (slide 16 of the official deck): *"Use straight lines and right angles to
connect objects wherever possible. Diagonal lines only when right angles are not
possible."*

- **Horizontal:** same Y center. `exitX=1;exitY=0.5` → `entryX=0;entryY=0.5`
- **Vertical:** same X center. `exitX=0.5;exitY=1` → `entryX=0.5;entryY=0`
- **Never use waypoints** — if you need one, the layout is wrong. Move icons.

Layout drives connections, not the other way around.

---

## AWS Preset Arrow Styles (slide 16 + slide 27)

**The head is a solid filled triangle, not hollow.** The deck text on slide 16 says
"Preset arrows use the 'Open Arrow' in Size 4" — "Open Arrow" is the PowerPoint UI
name for a specific arrowhead preset, NOT a visual description of the fill. In
OOXML every preset arrow uses `<a:headEnd type="arrow" w="med" len="sm"/>`, which
renders as a **solid filled triangle** (verified by pixel-sampling the slide 16
reference image — the triangle is uniformly dark pixels from tip to base, not just
two outline edges). In drawio XML this maps to `endArrow=classic;endFill=1;endSize=8`.

All preset arrows are solid, 1.25pt, black (`#000000`, theme tx1 / windowText).
Corners at orthogonal bends are **sharp** (miter join, `<a:miter>` in OOXML) — never
rounded. In drawio that means `rounded=0` on every edge.

**Drawio style mapping (strictly AWS-official look):**
```
edgeStyle=orthogonalEdgeStyle;rounded=0;html=1;
strokeColor=#000000;
strokeWidth=1.25;
endArrow=classic;endFill=1;endSize=8;
```

### Four head/tail direction combinations

| Variant | Head | Tail | Use |
|---------|------|------|-----|
| `→` forward | filled classic | none | Directional A → B |
| `←` reverse | none | filled classic | Directional B → A |
| `↔` bidirectional | filled classic | filled classic | Two-way exchange |
| `—` plain | none | none | Connection without direction |

### Three arrow shapes — pick ONE per diagram

Slide 16 says: *"Use straight lines and right angles to connect objects wherever
possible. In the instance where right angles are not possible, you may use a
diagonal line as provided."*

That gives three allowed shapes. **A single diagram must commit to one** (straight
is the preferred default; elbow is the natural fallback when icons can't be
axis-aligned; diagonal is the last resort). Mixing elbow AND diagonal in the same
diagram is a violation of slide 16.

| Shape | drawio style | When to use |
|-------|--------------|-------------|
| **Straight** (horizontal or vertical) | `edgeStyle=orthogonalEdgeStyle` + icons share an X or Y center so the router produces one segment | Default — always try this first |
| **Right-angle / elbow** | `edgeStyle=orthogonalEdgeStyle` + icons at different rows and different columns; router auto-adds one 90° bend | When a straight line is geometrically impossible |
| **Diagonal** | `edgeStyle=none` (no orthogonal router) | Last resort — only when right angles don't work, and apply to every edge in the diagram |

Straight + elbow is OK in the same diagram (elbow is just the fallback for straight
— same preset family). Diagonal must stand alone.

---

## Arrow Semantics (Extended, NON-OFFICIAL)

AWS itself does **not** differentiate request vs. data vs. async arrows. If you need
those semantics for storytelling in a demo or tutorial, use the table below — but
**always include a legend** that declares what each style means so readers know you've
gone beyond AWS defaults.

| Arrow meaning | Style | When to use |
|---------------|-------|-------------|
| Request flow (primary) | `strokeWidth=2;endArrow=classic;endFill=1;endSize=8` | Synchronous request path |
| Data read/write | `strokeWidth=1;endArrow=classic;endFill=1;endSize=8` | Service accessing a data store |
| Async / event | `strokeWidth=1;dashed=1;endArrow=classic;endFill=1;endSize=8` | Event-driven, decoupled |
| Return / response | `strokeWidth=1;dashed=1;strokeColor=#666666;endArrow=classic;endFill=1;endSize=8` | Response flowing back |
| Bidirectional | `startArrow=classic;startFill=1;startSize=8;endArrow=classic;endFill=1;endSize=8` | Two-way sync |

For pure AWS-faithful reference architecture diagrams, use only the preset variants
above — no thickness or dash differentiation.

---

## Parallel Arrow Spacing

When multiple arrows connect to the same icon side, offset their exit/entry points so
they run parallel with visible padding — never stacked on top of each other.

- Fractional `exitY` / `entryY` for horizontal arrows sharing the same icon side
  (e.g., `exitY=0.25`, `exitY=0.5`, `exitY=0.75`).
- Fractional `exitX` / `entryX` for vertical arrows sharing the same icon side.
- Minimum 10px visual gap between parallel arrows.
- All exit/entry points must stay within icon bounds (0.0 to 1.0).
- For 60px icons, max 3 parallel arrows per side at 0.25 / 0.5 / 0.75 (15px apart).

**Example — 3 arrows exiting the right side:**
```
Arrow 1:  exitX=1;exitY=0.25   → top quarter
Arrow 2:  exitX=1;exitY=0.5    → center
Arrow 3:  exitX=1;exitY=0.75   → bottom quarter
```

**Example — 2 arrows exiting the bottom:**
```
Arrow 1:  exitX=0.35;exitY=1   → left of center
Arrow 2:  exitX=0.65;exitY=1   → right of center
```

---

## Row-Based Layout

Organize icons into horizontal rows at fixed Y coordinates.

- **Row 1 (main flow):** Primary services at same Y. Horizontal edges only.
- **Row 2 (supporting):** Databases/storage directly below parent at same X. Vertical
  edges only.
- **Row 3 (monitoring):** Above or below. Smaller icons (48×48), lighter stroke.

### Icon Spacing (Tight by Default)

The 2026 AWS deck packs icons tightly — a reference architecture slide typically shows
5-8 icons at ~130-160px inter-column gap and ~150-180px inter-row gap. Keep diagrams
**compact**; empty canvas reads as "I didn't know what to put here." Rules:

| Spacing | Default | When to use | Upper bound |
|---------|---------|-------------|-------------|
| Horizontal gap (icon center → icon center) | **140-160px** | ~4-6 icons per row. 140 works for short labels, 160 when labels like "Amazon Bedrock AgentCore" (~150px wide) need clearance | 180px if long arrow labels |
| Vertical gap (icon center → icon center) | **160-180px** | Stacked rows, labels below each icon | 200px if callouts sit above each row |
| Icon edge → container edge (padding) | **40px** | Generic rule — leaves room for icon label + callout | — |
| Icon label height allowance (below icon) | **30px** | 2 lines Arial 12pt + 6px buffer | — |

**Never** leave more than ~200px between two connected icons. A 300px+ horizontal gap
with nothing in between is a signal the layout is stretched — either add more icons to
tell the story or compress the row.

**Container sizing**: a VPC / subnet / pipeline container with 3 icons inside should
be ~**400-500px wide × 120-160px tall**, not 800×340. Size from icons + 30-40px
padding per side, never draw an oversized box around a few icons. An outsized container
screams "unnecessary whitespace" at any reader.

### Edge Connection Points — Use Centers

**Default to center-to-center connections** on edges: `exitX=1, exitY=0.5` (right-center)
and `entryX=0, entryY=0.5` (left-center) for horizontal arrows; `exitY=1, entryY=0`
for top-to-bottom vertical arrows. Corner connections (`exitX=1, exitY=1` or
`exitX=0.5, exitY=0.25` etc.) should only be used when center-to-center creates
an actual conflict — never reflexively to "offset" an arrow.

When two edges share an icon side and centers overlap, **offset by 0.25/0.5/0.75**
(quarter and three-quarter points), not by corner points (0/1). Corner exits look
ragged and suggest the author lost track of which arrow goes where.

### Fit-to-Content Canvas

**Do not start from a fixed 1600×900 canvas.** Start from the icon layout, then size
the canvas to fit with a 40px margin on every side.

```
canvas.width  = (rightmost icon x + icon width) - (leftmost icon x) + 80px + 2*40px
canvas.height = (bottom icon y + icon height + label_space) - (top icon y) + 80px
```

Typical results:

| Diagram complexity | Canvas size |
|--------------------|-------------|
| 3-5 icons, single row | ~900×500 |
| 5-7 icons with 2 rows | ~1100×700 |
| 8-12 icons with 3-4 rows + containers | ~1400×900 |
| Full VPC with subnets across 2 AZs | ~1500×850 |

Use 16:9 (1600×900) **only** when the diagram genuinely fills that space. A 4-icon
pipeline on a 1600×900 canvas looks empty and unprofessional. Update the `pageWidth`
and `pageHeight` attributes on `mxGraphModel` to match the fit-to-content size.

### Vertical Column Alignment

Supporting icons MUST share the same X center as their parent. When they don't, the
orthogonal edge router produces a visible L-shape detour that reads like a routing
bug, not an intentional relationship.

```
Main row:     User Svc (x=600)    Post Svc (x=760)
                  │                     │
Data row:     Aurora (x=600)      DynamoDB (x=760)
```

**The recurring trap** — placing a data/supporting icon ABOVE a main-flow icon and
then forgetting to share X. The edge router creates the detour silently; the
validator catches it only if the offset is small.

**Decision tree when a parent and child are not X-aligned:**

| Situation | Fix |
|-----------|-----|
| You can move the child | **Move it to share X with the parent.** Straight vertical edge. |
| The child is shared by multiple parents | Pick the dominant parent's X and accept an L-shape for the others. Use `exitY=0.5` side exits, not top/bottom, so the router's bend looks intentional. |
| The child sits on a different Y row by category convention | Don't use a top/bottom exit. Use `exitX=1,exitY=0.5` → `entryX=0,entryY=0.5` so the router produces a side-to-side L. A top/bottom-to-top/bottom edge with mismatched X creates a crooked, awkward path. |
| You need both a straight flow edge AND a cross-row data edge | Use a **second edge** with an offset exit point (`exitY=0.25` or `exitY=0.75`) to avoid stacking on the main flow edge. |

**Concrete example** (from this project's supply-chain diagram):
- Wrong: Lambda at (540, 290) with `exitX=0.35;exitY=0` → Aurora at (710, 170) with
  `entryX=0.35;entryY=1` — exits/entries are top/bottom but X centers differ by
  170px, forcing a crooked detour.
- Right: Move Aurora to (540, 170) so it sits directly above Lambda; the edge is
  now a straight vertical line with `exitX=0.5;exitY=0` → `entryX=0.5;entryY=1`.

### Fan-Out Patterns

- **Horizontal Chain (preferred):** Source → T1 → T2 → T3 on same Y row.
- **Vertical Fan-Out:** Source centered above targets with shared horizontal rail.
- **AVOID:** One source to many non-adjacent targets from same exit point — arrows
  cross icons.


---

## AWS Group Containers

See `references/aws-icon-catalog.md` (Group Containers section) for the full
authoritative container style table and ready-to-paste examples. Summary below.

### When to Use Which Container

| Scenario | Container | Why |
|----------|-----------|-----|
| Any architecture touching AWS services | AWS Cloud group | Always show the boundary |
| Multi-account or security-critical | AWS Account | Shows ownership |
| Multi-region | Region (dashed teal) | Geographic boundary |
| Network topology | VPC + subnets | Required for network stories |
| Zonal placement | Availability Zone (plain dashed rect) | When AZ matters |
| Elastic compute | Auto Scaling group (dashed orange, centered) | Indicates elasticity |
| Cross-cutting firewall | Security group (plain dashed red rect) | Overlays services it protects |
| Step Functions workflow | Step Functions workflow group | Wrap a single state machine |
| Related services without official category | Generic group (gray) | Fallback |
| Delivery pipeline (CodeCommit + CodePipeline + CodeDeploy) | Custom dashed rect, pink `#E7157B` or purple `#C925D1` | Operational concern — no AWS-native preset exists |
| Observability (CloudWatch + X-Ray + CloudTrail) | Custom dashed rect, gray `#7D8998` or pink `#E7157B` | Cross-cutting concern across the whole architecture |
| Security & compliance (GuardDuty + Security Hub) | Custom dashed rect, red `#DD344C` | Security ops grouping |
| Data platform (Glue + Lake Formation + Athena) | Custom dashed rect, purple `#8C4FFF` | Analytics grouping |

**Don't use** AWS Cloud for every diagram if you're showing internal architecture —
use AWS Account or skip the outer wrapper if it adds no meaning.

### What Goes Inside a VPC Container

VPC containers hold only services that **run on customer-managed ENIs in
customer subnets**. Everything else is managed by AWS and lives outside the VPC
box (still inside AWS Cloud). The common mistake is to put S3, Bedrock,
SageMaker, Quick Suite, or API Gateway inside the VPC — those are all managed
services with regional endpoints.

**Inside VPC**: EC2, Fargate, ECS, EKS workers, RDS, Aurora, ElastiCache,
Redshift, ALB/NLB/CLB, NAT gateways, VPC endpoints, Lambda ONLY when
VPC-attached.

**Outside VPC** (inside AWS Cloud only): S3, DynamoDB, SQS, SNS, Bedrock,
Bedrock AgentCore, SageMaker (managed endpoint), Quick Suite, QuickSight,
CloudWatch, X-Ray, API Gateway, Amplify, CloudFront, CodeCommit, CodePipeline,
CodeBuild, CodeDeploy, Secrets Manager, Step Functions, Glue, Athena.

See `references/aws-icon-catalog.md` for the full list and rationale.

### VPC Connection Bridge Icon

When a managed service OUTSIDE the VPC needs to read data INSIDE the VPC (Quick
Suite reading Aurora, Bedrock Knowledge Base reading RDS, AppFlow pulling from
RDS), draw the connection via a **VPC PrivateLink bridge icon** between them.
Use `resIcon=mxgraph.aws4.vpc_privatelink`, labeled "VPC Connection".

```
aurora → [vpc_privatelink] → quick_suite
```

Never draw a bare arrow punching through the VPC border — it implies a network
path that does not exist in AWS.

### Custom Dashed Containers for Operational Concerns

For pipeline, observability, and similar groupings that don't have an AWS
preset, use a plain dashed rectangle with `fillColor=none`:

```xml
<mxCell id="pipeline_box" parent="1" style="rounded=0;whiteSpace=wrap;html=1;dashed=1;strokeColor=#E7157B;fillColor=none;verticalAlign=top;align=left;spacingLeft=12;spacingTop=6;fontColor=#E7157B;fontSize=12;fontFamily=Arial;" value="Delivery pipeline" vertex="1">
  <mxGeometry height="140" width="540" x="..." y="..." as="geometry" />
</mxCell>
```

Rules for custom containers:
- Always `dashed=1` (distinguishes from AWS Group containers which are solid or have AWS-specific dash semantics)
- Always `fillColor=none`
- Label is 12pt Arial **regular** (not bold), color matches stroke
- Title anchored top-left via `verticalAlign=top;align=left;spacingLeft=12;spacingTop=6`
- No `grIcon` — these are not AWS-native groupings
- Size = children bounding box + 30-40px padding each side

### Container Geometry

- `container=0` to avoid coordinate nesting in hand-written XML (drawio auto-sets 1
  when you edit visually, but hand-written XML should use 0 so child coordinates are
  absolute).
- `parent="1"` on every container — don't nest parents manually.
- Buffer of ≥ 5px (0.05") on every side between inner and outer group borders.
- Compute size from children: `container.size = child_bounding_box + 40px padding`
  (and +50 for label clearance below).

### Child Icon Placement Inside Containers

Container titles sit on the **top-left corner** of the container border (the group's
built-in label). When placing a child icon that uses `verticalLabelPosition=top`
(label above the icon), its label zone will collide with the container title if the
icon is placed near the top-left corner.

**Rules:**

1. If an icon near the top of a container must have its label ABOVE (because of
   arrows approaching from below), offset the icon **horizontally** so its label
   does not overlap the container's title zone. For a 12pt title of ~N characters,
   the title zone spans roughly `(container.x + spacingLeft, container.y + 5)` to
   `(container.x + spacingLeft + N*7px, container.y + 20)`. Keep icon-label x-range
   outside this box.
2. If horizontal offset isn't possible, flip the label to BELOW
   (`verticalLabelPosition=bottom;verticalAlign=top`) and route approaching arrows
   to enter from the **left or right** side instead of the bottom. This uses an
   L-shaped edge (exit top of source, enter left of target, or vice versa) — still
   axis-aligned, one bend only.
3. As a last resort, increase the container's `spacingTop` to reserve a title-only
   strip below the border, and place icons beneath it.

**Example (Aurora inside VPC)**: VPC title at top-left. An Aurora icon directly below
the VPC title with label above would overlap. Move Aurora right along the top row
(x clear of the title text), keep label above, and route `Lambda → Aurora` as an L:
exit Lambda top, enter Aurora left. Callout sits on the horizontal segment of the L.

### Nested Container Title Clearance

A container's title sits on its own border at Y ≈ `container.y + 8` (height ≈ 16-20px
depending on fontSize). When you place a **child container** — Auto Scaling group
inside a subnet, subnet inside a VPC, anything nested — the child container's
rectangle must NOT overlap the parent's title strip.

**Rule — 30px title clearance band:**

For every nested container whose parent has a title, reserve the parent's
`[parent.y, parent.y + 30]` band as title-only. Child containers start at
`child.y ≥ parent.y + 30`, not `parent.y + 5` or `parent.y + 10`.

When the child is an Auto Scaling group or Security Group that **spans multiple
subnets**, the child's `y` must clear the title of the topmost subnet it crosses, not
just the outer container. Compute:

```
child.y = max(parent.y, *[subnet.y for subnet in crossed_subnets]) + 30
child.height = max_bottom_edge_of_crossed_subnets - child.y - 10
```

**Concrete failure mode (observed in iteration-1 VPC eval):**
- Private subnet at `(310, 450, 520×150)` → title zone at y=455-475.
- Auto Scaling group at `(380, 460, 1010×140)` → top edge at y=460 covers the
  subnet title.
- Fix: ASG should start at y=485 (parent.y + 30 + 5 buffer = 450 + 35 = 485) and
  shrink its height accordingly, OR move the subnet labels to the side/bottom so
  the title strip is free.

The simpler fix is usually to push the ASG's `y` down by 30-35px and reduce its
`height` by the same amount. This is what the AWS deck does on slide 25 — the ASG
hugs the bottom two-thirds of the subnet row, leaving the subnet title strip
visible at the top.

### Cross-AZ and Regional Resources — Position Between, Not Inside

Some AWS services are **regional** (not zonal) — they span multiple AZs by design:

- Application Load Balancer, Network Load Balancer (ALB/NLB are regional)
- API Gateway
- Route 53
- CloudFront
- Any managed service not tied to a specific AZ

When your diagram shows two or more AZs side-by-side, these regional resources
must NOT be drawn *inside* one AZ's subnet — that misrepresents the architecture.
They belong **centered between the AZs**, either:

1. **Above the AZ row**, centered on the VPC's X-midpoint. The AZ containers
   start below the regional-service row. Arrows fan down from the regional
   service into each AZ's targets.
2. **On a regional row inside the VPC**, above the AZ containers but inside the
   VPC border. Typical for ALB/NLB that terminate traffic at the VPC level
   before distributing to zonal targets.

Likewise, **Auto Scaling groups** that span AZs should be drawn as a container
whose X-range covers both AZs' private subnets — it is drawn as a horizontal band
spanning the AZs (see "Nested Container Title Clearance" above for the vertical
geometry).

**Wrong** (observed in iteration-1):
- ALB placed at `x=540` inside Public subnet AZ1's bounds (310-830). The ALB
  visually belongs to AZ1 only, which is architecturally incorrect.

**Right:**
- ALB placed at `x = (az1.x + az2.x + az2.width) / 2 - 30` — the X-midpoint of
  the two AZs, minus half the icon width. That puts the ALB visually between
  the AZs, matching the regional/cross-zonal semantics.
- Alternatively, draw a single "Load Balancer" row at `y = az_top - 80` (above
  the AZ containers, inside the VPC), with the ALB centered on the VPC's
  midpoint.

| Service | Placement |
|---------|-----------|
| Users / external actor | Outside VPC, left of everything |
| Internet Gateway / NAT Gateway (VPC edge) | Left edge of VPC, between Users and the AZ row |
| ALB / NLB (regional) | Above the AZ row OR on its own row, centered on VPC midpoint |
| Auto Scaling group | Container spanning the AZs' private subnets |
| Aurora cluster (with writer + reader) | One writer in AZ1's DB subnet, one reader in AZ2's DB subnet — connected by a replication arrow |
| EC2 / RDS instance (zonal) | Inside the specific AZ's subnet |


### Canonical Nesting Hierarchy

```
AWS Cloud
└── AWS Account             (pink `#CD2264`, solid)
    └── Region              (teal `#00A4A6`, **dashed**)
        └── VPC             (purple `#8C4FFF`, solid, group_vpc2)
            ├── Availability Zone    (blue-teal `#147EBA`, **dashed**, plain rect)
            │   ├── Public subnet    (green stroke, pale green fill, group_security_group)
            │   └── Private subnet   (teal stroke, pale teal fill, group_security_group)
            │       └── Auto Scaling group  (orange `#D86613`, **dashed**, groupCenter)
            │           └── EC2 instance contents
            └── Security group       (red `#DD3522`, plain rect, crosses subnets)
```

### Critical Container Gotchas

- **Public/Private subnets** use `grIcon=mxgraph.aws4.group_security_group`.
  There is NO `group_public_subnet` or `group_private_subnet` grIcon — those
  names will render as broken/missing icons.
- **Security group** is a plain dashed rectangle (**no grIcon**) with stroke
  `#DD3522` (a distinct red, slightly different from the `#DD344C` that Security
  category service icons use).
- **Availability Zone** is a plain dashed rectangle (**no grIcon**) with stroke
  `#147EBA`.
- **Auto Scaling group** uses `shape=mxgraph.aws4.groupCenter` (not `group`),
  with `align=center`, `spacingTop=25`, and `dashed=1`.
- **VPC** uses `group_vpc2`, not the legacy `group_vpc`.
- The `fontColor` often differs from the `strokeColor` (e.g., Region stroke is
  `#00A4A6` but fontColor is `#147EBA`). Follow the table in
  `aws-icon-catalog.md` — do not assume font = stroke.

---

## Legends

Legends are required when your diagram uses any semantics the AWS preset system
doesn't define (custom arrow styles, callout numbering, non-standard groups).

Legend structure:

1. **Line Styles** — rounded box showing each arrow style used in the diagram with a
   short label for its meaning. Use real drawio edges, not Unicode arrows.
2. **Flow Key** — numbered list pairing each callout number with a verb-first
   description of that step (see Callouts section).

Place the legend in the bottom-right or bottom-left of the canvas. Keep it compact —
the legend itself should not need a legend.

---

## Callouts (MANDATORY)

Every architecture diagram must include numbered callouts showing the request flow
step by step. This is what turns a parts list into a narrative.

AWS official callouts (slide 18 of the deck):

- **Black filled circle** with **bold white number**
- Two fixed sizes — **large** for simple diagrams, **small** for complex ones. Never
  mix sizes in one diagram.
- Order strictly linearly: left-to-right, top-to-bottom, or clockwise
- Numbers only — never letters or other symbols
- Don't manually stretch callouts or create new callout shapes

### Drawio Style for Callouts

**Large (24px)** — for simple diagrams:
```
ellipse;whiteSpace=wrap;html=1;fillColor=#232F3E;strokeColor=#FFFFFF;fontColor=#FFFFFF;fontStyle=1;fontSize=14
```

**Small (16px)** — for complex diagrams:
```
ellipse;whiteSpace=wrap;html=1;fillColor=#232F3E;strokeColor=#FFFFFF;fontColor=#FFFFFF;fontStyle=1;fontSize=11
```

**NEVER use edgeLabel elements for step numbers.** A common LLM mistake is to
attach numbered labels directly to edges using `edgeLabel` style with
`labelBackgroundColor=#000000` (black badge with white text). This produces
inline text badges that look nothing like the official AWS callout circles.
Always create a **separate vertex cell** with the ellipse style above,
positioned at the arrow midpoint. The validator flags edgeLabel step numbers
as a FAIL.

### Callout Placement

- Place **above-left of the icon** or **at arrow midpoint**
- `(icon.x, icon.y - 30)` works for 24px callouts above a 60px icon
- **Never** at icon center Y — it blocks horizontal arrows
- **Never** in a margin column disconnected from icons
- 6px minimum gap from icon edge or label text

### Flow Key Wording

Every callout number needs a corresponding step in the flow key. Write steps as
**verb + service + object**, describing the action in context — not the icon.

- Bad: *"API Gateway"* (this is a parts list, not a story)
- Bad: *"API requests routed"* (passive, vague)
- Good: *"API Gateway forwards POST /forecast to the Forecast Lambda"*

---

## Edge Labels

- Add `labelBackgroundColor=#FFFFFF` on busy diagrams to keep labels readable when
  they sit on top of other elements.
- For crossings where two edges must intersect: `jumpStyle=arc;jumpSize=6` on one
  edge (not both).
- The AWS deck does **not** typically label arrows — labels sit near the arrow as
  separate text. Prefer numbered callouts over arrow labels when possible.

---

## Typography Rules (AWS-Official)

All label text in diagrams follows these rules, verified from the official deck:

- **Font**: Arial, 12pt, regular weight, color `#232F3E` (dark navy, near-black)
- Labels sit **below** the icon, **center-aligned**
- Maximum **2 lines** per label — lines never break mid-word
- "AWS" or "Amazon" must accompany the service name:
  - `AWS Lambda` ✓
  - `Amazon S3` ✓
  - just `Lambda` ✗ (even though common in casual writing)
- Short forms are acceptable after the full name appears once in the document
- Never reuse a short form for two services (e.g., "ELB" can't mean both Elastic Load
  Balancing and Elastic Beanstalk in the same doc)

Group labels sit on the **top edge** of the group border, **left-aligned** after the
corner icon, also at 12pt Arial.

---

## Training & Certification Override

When a diagram is destined for AWS training or certification materials:

- All type: **16pt**, black
- All lines: **2pt**, color-untouched
- White background only

This is stricter than general architecture style. Use it only when you know the
output is for training/cert.

---

## Layout Planning Checklist

Before writing any XML:

1. **One sentence story**: What does this diagram communicate? If you can't state it
   in one sentence, split into multiple diagrams.
2. **Row assignment**: Main flow Y, supporting services Y+200, monitoring Y-100.
3. **Happy path**: Trace trigger → outcome step by step, numbering each edge.
4. **Container plan**: What boundaries matter? AWS Cloud always. Account for
   multi-account. VPC only if network topology is part of the story.
5. **Grid**: Snap coordinates to multiples of 10.
6. **Legend content**: List every arrow style and every callout number.

Then write the XML. If the XML forces you to break these rules, the layout is
wrong — go back to step 2.
