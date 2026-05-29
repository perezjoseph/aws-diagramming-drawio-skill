# AWS Architecture Diagram Guidelines

Official best practices from the **AWS Architecture Icons** deck
(Release 23-2026.01.30, light BG) and the canonical `Sidebar-AWS4.js` in the drawio
source tree. Read this reference when creating or reviewing architecture diagrams.

---

## System Elements

Every AWS diagram is built from five element types:

- **Groups** — show boundaries and connections between services (AWS Cloud, Region,
  VPC, subnets, AZs, security groups)
- **Arrows** — describe information flow or connect parts of a diagram
- **Service icons** — represent an AWS service (the filled square tile icons)
- **Resource icons** — represent a specific resource within a service
- **General resource icons** — apply to resources across multiple services

---

## Building a Diagram — AWS Recommended Order

1. Choose background style: **light (white)** or dark. This project uses light.
2. **Start with the structure**: lay out groups first (AWS Cloud, Region, VPC,
   subnets). Don't place icons first.
3. Add service or resource icons **inside** their containing groups.
4. **Connect** the steps with arrows to describe the workflow.
5. **Final touches**: numbered callouts (1, 2, 3...) for step ordering.

---

## Category Colors (Summary)

AWS uses **only 7 shared category colors** — not one per category. Full list is in
`aws-icon-catalog.md`. Quick reference:

| Hex | Color | Main categories |
|-----|-------|-----------------|
| `#ED7100` | Orange | Compute, Containers, Media |
| `#7AA116` | Green | Storage, IoT |
| `#DD344C` | Red | **Databases**, Developer Tools |
| `#8C4FFF` | Purple | Networking, Analytics, Serverless |
| `#E7157B` | Pink | App Integration, Management |
| `#01A88D` | Teal | AI/ML, End User Computing, Migration |
| `#C925D1` | Fuchsia | **Security**, Business Apps |

Common mistakes: Databases is RED (not blue). Security is FUCHSIA (not red).

---

## Groups

- Each group has an **icon** in the top-left corner and a **label** on the top border
- Colors and dash styles differentiate group purpose for readability
- Some groups **cross** multiple groups (e.g., Auto Scaling spans subnets);
  others **nest** strictly (VPC → subnets)
- Nested groups need **≥ 0.05"** buffer on all sides from the parent border
- Use a **Generic group** (gray) if the official presets don't fit
- **Do NOT** create groups with non-approved AWS icons
- **Do NOT** resize group icons

The **canonical nesting hierarchy** and per-container styles are documented in
`aws-icon-catalog.md` → *AWS Group Containers*.

### Common Container Gotchas

- Public/Private subnets use `grIcon=group_security_group` — NOT nonexistent
  `group_public_subnet` / `group_private_subnet`
- Security group is a plain dashed rect (no grIcon), stroke `#DD3522`
- Availability Zone is a plain dashed rect (no grIcon), stroke `#147EBA`
- Auto Scaling group uses `shape=mxgraph.aws4.groupCenter` (not `group`), dashed orange

---

## Icons

- Use icons at their predefined size, color, and format in diagrams
- Icons can scale for presentations (hold Shift to preserve aspect ratio)
- **Do NOT** crop, flip, rotate, or change icon shapes
- **Do NOT** alter icon colors — they have been accessibility tested
- Always use the **SVG** file, never PNG (quality degrades)

Drawio working size: 60×60 px main, 48×48 px supporting. AWS native SVG viewBox is
40×40 px (on a 32-pt design grid).

---

## Arrows

AWS ships only **4 preset arrows**:

| Variant | Meaning |
|---------|---------|
| `→` forward | A → B |
| `←` reverse | B → A |
| `↔` bidirectional | Two-way |
| `—` plain | Undirected connection |

All presets:
- 1.25pt line weight (`strokeWidth=1.25`)
- Black stroke (`strokeColor=#232F3E`)
- "Open Arrow" head at size 4 (`endArrow=classic;endFill=1;endSize=8`)
- Solid (no dash)

**Routing**: prefer straight lines and right angles (orthogonal). Diagonal only when
right angles aren't possible.

**Return traffic**: show with dashed/intermittent arrows.

**Do NOT** use anything besides preset or default arrows for AWS-faithful
reference architecture. For tutorials/demos that need request-vs-data-vs-async
distinctions, see the extended styles in `layout-and-edges.md` and always include a
legend.

---

## Icon Labels

- **All label text is 12pt Arial** throughout the diagram (16pt for Training & Cert)
- Color: `#232F3E` (near-black navy)
- Service names must fit on **no more than two lines**
- Labels sit **below** the icon, **center-aligned**
- **"AWS" or "Amazon"** should always accompany the service name
- Lines should **never break mid-word** — break after the second word if needed
- Short forms (e.g., "Amazon EC2" for "Amazon Elastic Compute Cloud") are OK
  **after** the full name has been introduced once
- **Do NOT** duplicate short forms across two services

### Role-First Naming (Project Convention)

Label icons with **what they do**, then **what they are**:

- Good: `Order Processor\nAWS Lambda`
- Good: `User Session Store\nAmazon DynamoDB`
- Bad: bare `Lambda`, bare `DynamoDB`

This turns a parts list into a story.

---

## Numbered Callouts

- Use numbered callouts to draw attention to **steps in a process**
- Shape: **black filled circle** with **bold white number**
- Two fixed sizes — **large** (24px, simple diagrams) or **small** (16px, complex)
- **Never mix sizes** within the same diagram
- Order linearly: **left-to-right**, **top-to-bottom**, or **clockwise**
- Be consistent in callout placement
- **Do NOT** use letters or other symbols — numbers only
- **Do NOT** stretch or recolor callouts

### Placement

- Above-left of the annotated icon, OR at the midpoint of the relevant arrow
- **Never** at icon center Y (blocks horizontal arrows)
- 6px minimum gap from icon edge or label text

### Flow Key Wording

Every callout needs a matching step in the flow key. Write as
**verb + service + object**:

- Bad: *"API Gateway"* (just a label)
- Bad: *"API requests routed"* (passive, vague)
- Good: *"API Gateway forwards POST /forecast to the Forecast Lambda"*

---

## Service Scope in Diagrams

Place services at the correct scope level:

- **Global services** (S3, CloudFront, Route 53, IAM) — inside the AWS account
  boundary but NOT inside a VPC or region
- **Regional services** (VPC, Lambda, DynamoDB) — inside a region boundary
- **Zonal services** (EC2 instances, EBS volumes) — inside an Availability Zone

---

## Diagram Composition

- Depict **one or at most two flows** per diagram — don't try to show everything
- Put the **title at the top**, communicating the system and the diagram's purpose
- Always show the **AWS account boundary**, even for single-account solutions
- For multi-account scenarios, show only **participating** accounts
- Use different colored lines to distinguish traffic flows when needed
  (e.g., blue for US-East-1, red for EU-West-1) — and label them in the legend
- **Avoid too many lines** — simplify by grouping or omitting obvious connections
- Check arrow directions match the actual flow
- Always do **peer review** — if peers need lots of explanation, revisit the diagram

---

## Training & Certification Style

When diagrams need maximum accessibility:

- White background only
- All type **16pt** throughout
- All type **black** throughout
- All line weights **2pt** throughout
- Do NOT alter any icon or line colors

---

## Explicit Don'ts (From the AWS Deck)

| Source | Don't |
|--------|-------|
| Slide 14 | Create groups with non-approved AWS icons |
| Slide 14 | Resize group icons |
| Slide 15 | Crop service icons |
| Slide 15 | Flip or rotate icons |
| Slide 15 | Change icon shapes |
| Slide 16 | Use anything besides preset or default arrows |
| Slide 17 | Use short forms without introducing the full name first |
| Slide 17 | Reuse the same short form for two services |
| Slide 17 | Break a label line mid-word |
| Slide 18 | Mix large + small callouts in the same diagram |
| Slide 18 | Change callout color or font size |
| Slide 18 | Use letters or other symbols in place of numbers |
| Slide 18 | Manually stretch a callout |
| Slide 18 | Create new callout shapes |
| Slide 26 | Insert a PNG when an SVG is available |
