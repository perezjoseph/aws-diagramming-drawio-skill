#!/usr/bin/env python3
"""
AWS-Official Fidelity checks for draw.io diagrams.

Extracted from validate_drawio.py to keep each file under the 100 KB tool
limit. All checks in this module verify conformance to the AWS 2026
architecture icon deck.

Checks included:
  - Icon fillColor fidelity (7 category colors)
  - Gradient fills (only Customer Engagement + AR/VR)
  - Group icon (grIcon) validity
  - Security group style
  - Container background fills (fillColor=none)
  - Container label font weight (regular, 12pt)
  - Label font (Arial)
  - Label sizes
  - Arrow style fidelity (black 1.25pt, filled classic head)
  - Arrow-shape consistency (straight / elbow / diagonal - pick one)

Entry point:
    run_aws_fidelity_checks(vertices, edges, id_to_geo, helpers)

where helpers exposes parse_style(style_str) -> dict and fail/warn/ok
functions matching validate_drawio.py's global reporters.
"""


def run_aws_fidelity_checks(vertices, edges, id_to_geo, helpers):
    """Run every AWS-official fidelity check.

    Args:
        vertices: list of mxCell elements where vertex="1"
        edges: list of mxCell elements where edge="1"
        id_to_geo: dict mapping cell id -> {"x","y","width","height"}
        helpers: object exposing .parse_style, .fail, .warn, .ok
    """
    parse_style = helpers.parse_style
    fail = helpers.fail
    warn = helpers.warn
    ok = helpers.ok

    # =========================================================
    print("\n--- AWS-Official Fidelity ---")
    # =========================================================

    # Official AWS category colors (from PPTX + Sidebar-AWS4.js)
    AWS_CATEGORY_COLORS = {
        "#ED7100",  # Compute, Containers, Media, Blockchain, Quantum
        "#7AA116",  # Storage, IoT, Cloud Financial Mgmt
        "#DD344C",  # Security & Identity, Business Apps, Contact Center,
                    # Front-End Web & Mobile, Migration, Robotics
        "#8C4FFF",  # Networking, Analytics, Serverless, Games
        "#E7157B",  # App Integration, Management & Governance
        "#01A88D",  # AI/ML, End User Computing
        "#C925D1",  # Databases, Developer Tools, Customer Enablement,
                    # Satellite, End User Computing label
        "#3334B9",  # Customer Engagement (the one palette with a blue gradient)
        "#BC1356",  # AR/VR (the other gradient palette)
    }

    AWS_NEUTRAL_COLORS = {
        "#232F3E",  # Smile navy — icon tile bg, AWS Cloud stroke, primary text
        "#232F3D",  # Same (1-point shift tolerated)
        "#FFFFFF",  # Glyph + canvas
        "#F1F3F3",  # Pale accent
        "#161E2D",  # Alternate text
        "#7D8998",  # Gray for Generic/Server/DC
        "#00A4A6",  # Container teal (Region/AZ/Private subnet)
        "#147EBA",  # Region/AZ font color
        "#AAB7B8",  # VPC font color
        "#DD3522",  # Security group stroke
        "#D86613",  # Auto Scaling / EC2 contents / Elastic Beanstalk / Spot Fleet
        "#CD2264",  # AWS Account / Step Functions workflow
        "#248814",  # Public subnet font
        "#3F8624",  # IoT Greengrass font
        "#5A6C86",  # Generic/Server/DC font
        "#E6F6F7",  # Private subnet fill
        "#F2F6E8",  # Public subnet fill
        "#EFF0F3",  # Generic group filled variant
        "#666666",  # Common annotation gray
        "#FF9900",  # Dark-BG theme Compute — tolerated but not preferred
        "#879196",  # Illustrations fill
        "#545B64",  # Illustrations fontColor / AWS preset arrow stroke
        "#F34482",  # AR/VR gradient top
        "#4D72F3",  # Customer Engagement gradient top
    }

    # Hexes that definitively indicate an LLM guessed wrong
    # Keep this small — only include hexes that LLMs demonstrably invent.
    KNOWN_BAD_COLORS = {
        "#FF6600": "Not AWS — generic orange. Compute is #ED7100.",
        "#4D4D4D": "Not AWS — use #7D8998 for gray Generic groups.",
        "#CC0000": "Not AWS — Security is #DD344C or #DD3522 for security group.",
    }

    # --- Check 1: invalid or suspect fillColor on service icons ---
    print("\n  Icon fillColor fidelity:")
    bad_fill_colors = []
    for v in vertices:
        style_str = v.get("style", "")
        style = parse_style(style_str)
        if "resIcon" not in style_str:
            continue
        fc = (style.get("fillColor", "") or "").upper()
        if not fc:
            continue
        if fc in {c.upper() for c in KNOWN_BAD_COLORS}:
            bad_fill_colors.append(
                f"'{v.get('id', '?')}': fillColor={fc} — {KNOWN_BAD_COLORS.get(fc, '')}"
            )
        elif fc not in {c.upper() for c in AWS_CATEGORY_COLORS}:
            # Not an official category color — flag as warning
            bad_fill_colors.append(
                f"'{v.get('id', '?')}': fillColor={fc} is NOT one of the 7 AWS category colors"
            )
    if bad_fill_colors:
        fail(f"{len(bad_fill_colors)} icons use non-AWS-official fillColor:")
        for b in bad_fill_colors[:10]:
            print(f"      → {b}")
    else:
        ok("All service icon fillColors are AWS-official")

    # --- Check 1b: per-service fillColor matches the PPTX ground truth ---
    # Source: AWS-Architecture-Icons-Deck_For-Light-BG_01302026.pptx (R23)
    # Extracted by scripts/extract_service_colors.py from embedded SVG fills.
    # Maps resIcon name -> correct category color. A {set} means the service
    # has multiple legitimate variants (e.g. "sagemaker" is #8C4FFF for
    # plain SageMaker on slide 36 but #01A88D for SageMaker AI on slide 43).
    print("\n  Per-service fillColor match (PPTX ground truth):")
    SERVICE_ICON_COLORS = {
        "amplify": "#DD344C", "api_gateway": "#8C4FFF", "app_mesh": "#8C4FFF",
        "app_runner": "#ED7100", "appflow": "#E7157B", "appsync": "#E7157B",
        "application_discovery_service": "#01A88D", "athena": "#8C4FFF",
        "aurora": "#C925D1", "auto_scaling": "#E7157B", "auto_scaling2": "#ED7100",
        "backup": "#7AA116", "batch": "#ED7100", "bedrock": "#01A88D",
        "bedrock_agentcore": "#01A88D", "billing_conductor": "#7AA116",
        "budgets": "#7AA116", "certificate_manager": "#DD344C", "chime": "#DD344C",
        "clean_rooms": "#8C4FFF", "client_vpn": "#8C4FFF", "cloud9": "#C925D1",
        "cloudendure_disaster_recovery": "#7AA116", "cloudendure_migration": "#01A88D",
        "cloudformation": "#E7157B", "cloudfront": "#8C4FFF",
        "cloudsearch2": "#8C4FFF", "cloudshell": "#C925D1",
        "cloudtrail": "#E7157B", "cloudwatch_2": "#E7157B",
        "codeartifact": "#C925D1", "codebuild": "#C925D1",
        "codecommit": "#C925D1", "codedeploy": "#C925D1",
        "codepipeline": "#C925D1", "cognito": "#DD344C",
        "comprehend": "#01A88D", "config": "#E7157B", "connect": "#DD344C",
        "control_tower": "#E7157B", "cost_explorer": "#7AA116",
        "data_exchange": "#8C4FFF", "database_migration_service": "#C925D1",
        "datasync": "#01A88D", "device_farm": "#DD344C",
        "devops_agent": "#E7157B", "direct_connect": "#8C4FFF",
        "documentdb_with_mongodb_compatibility": "#C925D1",
        "dynamodb": "#C925D1", "ec2": "#ED7100", "ecs": "#ED7100",
        "eks": "#ED7100", "elastic_beanstalk": "#ED7100",
        "elastic_block_store": "#7AA116", "elastic_file_system": "#7AA116",
        "elastic_load_balancing": "#8C4FFF", "elasticache": "#C925D1",
        "elasticsearch_service": "#8C4FFF", "elemental_mediaconnect": "#ED7100",
        "elemental_mediaconvert": "#ED7100", "elemental_medialive": "#ED7100",
        "elemental_mediapackage": "#ED7100", "elemental_mediastore": "#ED7100",
        "elemental_mediatailor": "#ED7100", "emr": "#8C4FFF",
        "eventbridge": "#E7157B", "express_workflow": "#E7157B",
        "fargate": "#ED7100", "finspace": "#8C4FFF", "forecast": "#01A88D",
        "freertos": "#7AA116", "fsx": "#7AA116", "glacier": "#7AA116",
        "global_accelerator": "#8C4FFF", "glue": "#8C4FFF",
        "greengrass": "#7AA116", "guardduty": "#DD344C",
        "identity_and_access_management": "#DD344C", "inspector": "#DD344C",
        "iot_core": "#7AA116", "iot_events": "#7AA116",
        "iot_sitewise": "#7AA116", "iq": "#C925D1", "kendra": "#01A88D",
        "key_management_service": "#DD344C", "keyspaces": "#C925D1",
        "kinesis": "#8C4FFF", "kinesis_data_firehose": "#8C4FFF",
        "kinesis_data_streams": "#8C4FFF",
        "kinesis_video_streams": {"#8C4FFF", "#ED7100"},
        "lake_formation": "#8C4FFF", "lambda": "#ED7100", "lex": "#01A88D",
        "lightsail": "#ED7100", "local_zones": "#ED7100",
        "location_service": "#DD344C", "macie": "#DD344C",
        "managed_service_for_apache_flink": "#8C4FFF",
        "managed_service_for_grafana": "#E7157B",
        "managed_service_for_prometheus": "#E7157B",
        "managed_services": "#C925D1",
        "managed_streaming_for_kafka": "#8C4FFF",
        "managed_workflows_for_apache_airflow": "#E7157B",
        "memorydb": "#C925D1", "migration_hub": "#01A88D", "mq": "#E7157B",
        "neptune": "#C925D1", "network_firewall": "#DD344C",
        "nova": "#01A88D", "organizations": "#E7157B",
        "outposts_family": "#ED7100", "partner_central": "#E7157B",
        "pinpoint": "#DD344C", "polly": "#01A88D", "privatelink": "#8C4FFF",
        "professional_services": "#C925D1", "proton": "#E7157B",
        "q": "#01A88D", "quick_suite": "#DD344C", "rds": "#C925D1",
        "redshift": "#8C4FFF", "rekognition": "#01A88D",
        "route_53": "#8C4FFF", "s3": "#7AA116",
        "sagemaker": {"#01A88D", "#8C4FFF"},
        "secrets_manager": "#DD344C", "security_hub": "#DD344C",
        "shield": "#DD344C", "simple_email_service": "#DD344C",
        "single_sign_on": "#DD344C", "site_to_site_vpn": "#8C4FFF",
        "snowball_edge": "#7AA116", "sns": "#E7157B", "sqs": "#E7157B",
        "step_functions": "#E7157B", "storage_gateway": "#7AA116",
        "support": "#C925D1", "systems_manager": "#E7157B",
        "textract": "#01A88D", "timestream": "#C925D1",
        "transcribe": "#01A88D", "transfer_family": "#01A88D",
        "transit_gateway": "#8C4FFF", "translate": "#01A88D",
        "trusted_advisor": "#E7157B", "vpc": "#8C4FFF",
        "vpc_lattice": "#8C4FFF", "waf": "#DD344C",
        "wavelength": "#ED7100", "workmail": "#DD344C",
        "workspaces": "#01A88D", "xray": "#C925D1",
        # Aliases the inspector-to-catalog mapper misses (drawio has two
        # PrivateLink stencils; both render purple).
        "privatelink": "#8C4FFF",
        "vpc_privatelink": "#8C4FFF",
        "quicksight": "#8C4FFF",  # legacy pre-2026 Analytics purple
    }
    mismatches = []
    unknown = []
    resicon_re = __import__("re").compile(r"resIcon=mxgraph\.aws4\.([a-z0-9_]+)")
    for v in vertices:
        style_str = v.get("style", "")
        if "resIcon" not in style_str:
            continue
        m = resicon_re.search(style_str)
        if not m:
            continue
        icon = m.group(1)
        style = parse_style(style_str)
        fc = (style.get("fillColor", "") or "").upper()
        if not fc:
            continue
        expected = SERVICE_ICON_COLORS.get(icon)
        if expected is None:
            unknown.append(f"'{v.get('id','?')}': resIcon={icon} — not in ground-truth map")
            continue
        if isinstance(expected, (set, frozenset)):
            expected_set = {c.upper() for c in expected}
            if fc not in expected_set:
                mismatches.append(
                    f"'{v.get('id','?')}': resIcon={icon} fillColor={fc} — "
                    f"expected one of {sorted(expected_set)}"
                )
        else:
            if fc != expected.upper():
                mismatches.append(
                    f"'{v.get('id','?')}': resIcon={icon} fillColor={fc} — "
                    f"expected {expected.upper()} (per PPTX R23)"
                )
    if mismatches:
        fail(f"{len(mismatches)} icons use the wrong category color for the service:")
        for m_ in mismatches[:10]:
            print(f"      → {m_}")
    else:
        ok("All service icon colors match the PPTX ground truth")
    if unknown:
        warn(f"{len(unknown)} icons use resIcons not in the ground-truth map:")
        for u in unknown[:5]:
            print(f"      → {u}")

    # --- Check 2: Gradient fills on service icons ---
    # Only Customer Engagement (#3334B9 + #4D72F3) and AR/VR (#BC1356 + #F34482)
    # legitimately use gradients. Anything else is suspect.
    print("\n  Gradient fills:")
    LEGIT_GRADIENT_PAIRS = {
        ("#3334B9", "#4D72F3"),  # Customer Engagement
        ("#BC1356", "#F34482"),  # AR/VR
    }
    gradient_icons = []
    for v in vertices:
        style_str = v.get("style", "")
        if "resIcon" not in style_str or "gradientColor" not in style_str:
            continue
        style = parse_style(style_str)
        gc = (style.get("gradientColor", "") or "").upper()
        fc = (style.get("fillColor", "") or "").upper()
        if gc and gc.lower() != "none":
            pair = (fc, gc)
            if pair not in {(f.upper(), g.upper()) for f, g in LEGIT_GRADIENT_PAIRS}:
                gradient_icons.append(
                    f"'{v.get('id', '?')}': gradientColor={gc}, fillColor={fc} — "
                    f"only Customer Engagement ({'#3334B9'}/{'#4D72F3'}) and AR/VR "
                    f"use gradients in the AWS palette"
                )
    if gradient_icons:
        fail(f"{len(gradient_icons)} service icons have non-AWS-official gradients:")
        for g in gradient_icons[:5]:
            print(f"      → {g}")
    else:
        ok("No illegal gradient fills")

    # --- Check 3: nonexistent grIcon names ---
    print("\n  Group icon (grIcon) validity:")
    INVALID_GR_ICONS = {
        "mxgraph.aws4.group_public_subnet",
        "mxgraph.aws4.group_private_subnet",
        "mxgraph.aws4.group_vpc",  # legacy — use group_vpc2
    }
    VALID_GR_ICONS = {
        "mxgraph.aws4.group_aws_cloud",
        "mxgraph.aws4.group_aws_cloud_alt",
        "mxgraph.aws4.group_region",
        "mxgraph.aws4.group_vpc2",
        "mxgraph.aws4.group_security_group",
        "mxgraph.aws4.group_auto_scaling_group",
        "mxgraph.aws4.group_account",
        "mxgraph.aws4.group_ec2_instance_contents",
        "mxgraph.aws4.group_elastic_beanstalk",
        "mxgraph.aws4.group_spot_fleet",
        "mxgraph.aws4.group_aws_step_functions_workflow",
        "mxgraph.aws4.group_on_premise",
        "mxgraph.aws4.group_corporate_data_center",
        "mxgraph.aws4.group_iot_greengrass",
        "mxgraph.aws4.group_iot_greengrass_deployment",
    }
    bad_gr_icons = []
    for v in vertices:
        style_str = v.get("style", "")
        style = parse_style(style_str)
        gri = style.get("grIcon", "")
        if not gri:
            continue
        if gri in INVALID_GR_ICONS:
            suggestion = ""
            if "public_subnet" in gri:
                suggestion = " Use group_security_group with strokeColor=#7AA116 and fillColor=#F2F6E8."
            elif "private_subnet" in gri:
                suggestion = " Use group_security_group with strokeColor=#00A4A6 and fillColor=#E6F6F7."
            elif gri == "mxgraph.aws4.group_vpc":
                suggestion = " Use group_vpc2 (current artwork)."
            bad_gr_icons.append(
                f"'{v.get('id', '?')}': grIcon={gri} does not exist or is legacy.{suggestion}"
            )
        elif gri not in VALID_GR_ICONS and "group_" in gri:
            # Unknown group icon — warn rather than fail (may be a new stencil)
            bad_gr_icons.append(
                f"'{v.get('id', '?')}': grIcon={gri} is not in the known valid list — verify against Sidebar-AWS4.js"
            )
    if bad_gr_icons:
        fail(f"{len(bad_gr_icons)} group icons are invalid or suspect:")
        for b in bad_gr_icons[:10]:
            print(f"      → {b}")
    else:
        ok("All group icons are valid")

    # --- Check 4: Security group with grIcon (should be plain rect) ---
    print("\n  Security group style:")
    sg_violations = []
    for v in vertices:
        val = (v.get("value", "") or "").lower()
        style_str = v.get("style", "")
        style = parse_style(style_str)
        # Heuristic: label mentions security group
        if "security group" not in val:
            continue
        if "grIcon" in style_str:
            sg_violations.append(
                f"'{v.get('id', '?')}': Security group should be a plain dashed rect with NO grIcon. "
                f"Use strokeColor=#DD3522, dashed=1, no grIcon."
            )
        elif style.get("strokeColor", "").upper() == "#DD344C":
            sg_violations.append(
                f"'{v.get('id', '?')}': Security group strokeColor should be #DD3522, not #DD344C (that's Databases red)."
            )
    if sg_violations:
        warn(f"{len(sg_violations)} security group style issues:")
        for s in sg_violations[:5]:
            print(f"      → {s}")
    else:
        ok("Security groups styled correctly")

    # --- Check 4b: Container background fills ---
    # Verified from 2026 deck: every container uses <a:noFill/>. Legacy pale
    # subnet fills (#E6F6F7 teal, #F2F6E8 green) are NOT used in the current deck.
    print("\n  Container background fills:")
    LEGACY_SUBNET_FILLS = {"#E6F6F7", "#F2F6E8", "#EFF0F3"}
    container_fill_violations = []
    for v in vertices:
        style_str = v.get("style", "")
        style = parse_style(style_str)
        # Only check actual container shapes
        is_group = "shape=mxgraph.aws4.group" in style_str or "shape=mxgraph.aws4.groupCenter" in style_str
        if not is_group:
            continue
        fc = (style.get("fillColor", "") or "").upper()
        if not fc:
            continue
        if fc == "NONE":
            continue  # correct
        if fc.upper() in {c.upper() for c in LEGACY_SUBNET_FILLS}:
            container_fill_violations.append(
                f"'{v.get('id', '?')}': fillColor={fc} is a pre-2026 pale subnet fill. "
                f"The 2026 deck uses fillColor=none on every container — set it explicitly."
            )
        elif fc.upper() == "DEFAULT":
            container_fill_violations.append(
                f"'{v.get('id', '?')}': fillColor=default renders as white (opaque). "
                f"Use fillColor=none so the background stays transparent, per the 2026 deck."
            )
        else:
            container_fill_violations.append(
                f"'{v.get('id', '?')}': fillColor={fc} — 2026 deck containers use fillColor=none only. "
                f"Only the stroke + grIcon should carry the visual semantics."
            )
    if container_fill_violations:
        warn(f"{len(container_fill_violations)} containers have background fills:")
        for c in container_fill_violations[:8]:
            print(f"      → {c}")
    else:
        ok("All containers have fillColor=none (2026 preset)")

    # --- Check 4c: Container label weight + size ---
    # Verified from slides 21 and 25: every container label is 12pt Arial
    # regular weight. Drawio's fontStyle=1 (bold) and fontSize=14 are common
    # LLM mistakes that make the diagram look subtly off.
    print("\n  Container label font weight:")
    label_violations = []
    for v in vertices:
        style_str = v.get("style", "")
        if "shape=mxgraph.aws4.group" not in style_str and "shape=mxgraph.aws4.groupCenter" not in style_str:
            continue
        style = parse_style(style_str)
        fs = style.get("fontStyle", "")
        sz = style.get("fontSize", "")
        if fs == "1":
            label_violations.append(
                f"'{v.get('id', '?')}': fontStyle=1 (bold). Container labels are "
                f"REGULAR weight in the 2026 deck — remove fontStyle=1."
            )
        if sz in ("13", "14", "15", "16"):
            label_violations.append(
                f"'{v.get('id', '?')}': fontSize={sz}. Container labels are 12pt "
                f"in the 2026 deck — set fontSize=12."
            )
    if label_violations:
        warn(f"{len(label_violations)} containers have non-standard label weight/size:")
        for lv in label_violations[:8]:
            print(f"      → {lv}")
    else:
        ok("All container labels are 12pt regular Arial (2026 deck standard)")

    # --- Check 5: Font family on icon labels ---
    # AWS 2026 deck themes 1 & 2 both specify <a:minorFont><a:latin typeface="Arial">.
    # The default drawio font is Helvetica, which renders differently and is the
    # easiest way to spot a non-AWS-official diagram. Every labeled AWS cell
    # should set fontFamily=Arial explicitly.
    print("\n  Label font:")
    bad_fonts = []
    missing_fonts = []
    for v in vertices:
        style_str = v.get("style", "")
        if "resIcon" not in style_str and "shape=mxgraph.aws4" not in style_str:
            continue
        style = parse_style(style_str)
        ff = (style.get("fontFamily", "") or "").strip()
        if not ff:
            missing_fonts.append(v.get("id", "?"))
        elif ff.lower() != "arial":
            bad_fonts.append(
                f"'{v.get('id', '?')}': fontFamily={ff} — AWS labels must be Arial"
            )
    if bad_fonts:
        warn(f"{len(bad_fonts)} icons use non-Arial fonts:")
        for b in bad_fonts[:5]:
            print(f"      → {b}")
    elif missing_fonts:
        warn(
            f"{len(missing_fonts)} icons missing explicit fontFamily=Arial — "
            f"drawio defaults to Helvetica which renders differently than the "
            f"AWS deck's Arial. Add fontFamily=Arial to every labeled cell."
        )
        for mid in missing_fonts[:5]:
            print(f"      → {mid}")
    else:
        ok("All AWS label fonts are Arial (matches 2026 deck theme)")

    # --- Check 6: Label size on service icons ---
    print("\n  Label sizes:")
    bad_font_sizes = []
    for v in vertices:
        style_str = v.get("style", "")
        if "resIcon" not in style_str and "shape=mxgraph.aws4" not in style_str:
            continue
        style = parse_style(style_str)
        fs = style.get("fontSize", "")
        if fs:
            try:
                fs_val = int(fs)
                # AWS official: 12pt for standard, 16pt for Training & Cert
                if fs_val not in (10, 11, 12, 13, 14, 16):
                    bad_font_sizes.append(
                        f"'{v.get('id', '?')}': fontSize={fs}pt — AWS uses 12pt (or 16pt for T&C)"
                    )
            except ValueError:
                pass
    if bad_font_sizes:
        warn(f"{len(bad_font_sizes)} icons have non-standard font sizes:")
        for b in bad_font_sizes[:5]:
            print(f"      → {b}")
    else:
        ok("All AWS label sizes are within range")

    # --- Check 7: VPC membership — managed services should not be inside VPC ---
    # Fully-managed AWS services (S3, Bedrock, QuickSight, etc.) live in AWS
    # Cloud but outside the customer VPC. Putting them INSIDE a VPC container
    # misrepresents the architecture.
    print("\n  VPC membership correctness:")

    # Services that must NEVER appear inside a VPC container. Matches resIcon
    # suffixes (after "mxgraph.aws4."). Kept conservative — only include
    # services that are unambiguously non-VPC.
    MANAGED_NON_VPC_ICONS = {
        "s3": "S3 is a regional service",
        "bedrock": "Bedrock foundation models are a managed service",
        "bedrock_agentcore": "Bedrock AgentCore is a managed service",
        "sagemaker": "SageMaker training/endpoint is a managed service",
        "quick_suite": "Quick Suite is a managed BI service",
        "quicksight": "QuickSight is a managed BI service",
        "amplify": "Amplify Hosting is an edge service",
        "cloudfront": "CloudFront is an edge service",
        "route_53": "Route 53 is a global DNS service",
        "api_gateway": "API Gateway is a regional managed service",
        "appsync": "AppSync is a regional managed service",
        "cloudwatch_2": "CloudWatch is a regional managed service",
        "xray": "X-Ray is a regional managed service",
        "cloudtrail": "CloudTrail is a regional managed service",
        "codecommit": "CodeCommit is a managed git service",
        "codepipeline": "CodePipeline is a managed CI/CD service",
        "codebuild": "CodeBuild is a managed build service",
        "codedeploy": "CodeDeploy is a managed deployment service",
        "step_functions": "Step Functions is a managed orchestration service",
        "sns": "SNS is a regional messaging service",
        "sqs": "SQS is a regional messaging service",
        "eventbridge": "EventBridge is a regional service",
        "secrets_manager": "Secrets Manager is a regional managed service",
        "identity_and_access_management_iam": "IAM is a global service",
        "key_management_service": "KMS is a regional managed service",
    }

    # Identify VPC containers by grIcon
    vpc_containers = []
    for v in vertices:
        style_str = v.get("style", "") or ""
        if "grIcon=mxgraph.aws4.group_vpc" in style_str:
            geo = id_to_geo.get(v.get("id"))
            if geo:
                vpc_containers.append((v.get("id"), geo))

    vpc_violations = []
    if vpc_containers:
        for v in vertices:
            style_str = v.get("style", "") or ""
            if "resIcon" not in style_str:
                continue
            style = parse_style(style_str)
            res_icon = (style.get("resIcon", "") or "").replace("mxgraph.aws4.", "")
            if res_icon not in MANAGED_NON_VPC_ICONS:
                continue
            geo = id_to_geo.get(v.get("id"))
            if not geo:
                continue
            icon_cx = geo["x"] + geo["width"] / 2
            icon_cy = geo["y"] + geo["height"] / 2
            for vpc_id, vpc_geo in vpc_containers:
                if (
                    vpc_geo["x"] < icon_cx < vpc_geo["x"] + vpc_geo["width"]
                    and vpc_geo["y"] < icon_cy < vpc_geo["y"] + vpc_geo["height"]
                ):
                    reason = MANAGED_NON_VPC_ICONS[res_icon]
                    vpc_violations.append(
                        f"'{v.get('id', '?')}' (resIcon={res_icon}) sits inside "
                        f"VPC '{vpc_id}'. {reason} — move it outside the VPC "
                        f"container. If it needs VPC data, add a "
                        f"vpc_privatelink bridge icon between them."
                    )
                    break
    if vpc_violations:
        fail(
            f"{len(vpc_violations)} managed services are incorrectly placed "
            f"inside a VPC container:"
        )
        for vv in vpc_violations[:8]:
            print(f"      → {vv}")
    else:
        ok("All managed services are outside VPC containers")

    # --- Check 8: Direct arrows crossing the VPC boundary without a bridge ---
    # If an icon OUTSIDE the VPC is connected to an icon INSIDE the VPC (or
    # vice-versa), there should be a vpc_privatelink / vpc_endpoint / vpn
    # bridge icon in between. A bare arrow punching through the border is
    # architecturally wrong.
    print("\n  VPC boundary arrows:")

    # Bridge icons that legitimately span the VPC boundary
    BRIDGE_ICONS = {
        "vpc_privatelink",
        "privatelink",
        "vpc_endpoints",
        "endpoints",
        "vpn_connection",
        "direct_connect",
        "transit_gateway",
        "nat_gateway",
        "internet_gateway",
        "elastic_load_balancing_network_load_balancer",
        "elastic_load_balancing",
    }

    def _in_any_vpc(cell_id):
        geo = id_to_geo.get(cell_id)
        if not geo:
            return None
        cx = geo["x"] + geo["width"] / 2
        cy = geo["y"] + geo["height"] / 2
        for vpc_id, vpc_geo in vpc_containers:
            if (
                vpc_geo["x"] < cx < vpc_geo["x"] + vpc_geo["width"]
                and vpc_geo["y"] < cy < vpc_geo["y"] + vpc_geo["height"]
            ):
                return vpc_id
        return None

    def _is_bridge(cell_id):
        for v in vertices:
            if v.get("id") != cell_id:
                continue
            style_str = v.get("style", "") or ""
            style = parse_style(style_str)
            res_icon = (style.get("resIcon", "") or "").replace("mxgraph.aws4.", "")
            return res_icon in BRIDGE_ICONS
        return False

    boundary_violations = []
    if vpc_containers:
        for e in edges:
            src = e.get("source")
            tgt = e.get("target")
            if not src or not tgt:
                continue
            src_vpc = _in_any_vpc(src)
            tgt_vpc = _in_any_vpc(tgt)
            # Both inside same VPC: OK
            if src_vpc and src_vpc == tgt_vpc:
                continue
            # Both outside any VPC: OK
            if src_vpc is None and tgt_vpc is None:
                continue
            # Crosses boundary — one end must be a bridge
            if _is_bridge(src) or _is_bridge(tgt):
                continue
            boundary_violations.append(
                f"Edge '{e.get('id', '?')}' ({src} → {tgt}) crosses a VPC "
                f"boundary without a bridge icon (PrivateLink, VPC endpoint, "
                f"NAT/Internet gateway, or NLB). Add a vpc_privatelink icon "
                f"on the boundary and route the arrow through it."
            )
    if boundary_violations:
        warn(
            f"{len(boundary_violations)} edges cross the VPC boundary "
            f"without a bridge icon:"
        )
        for bv in boundary_violations[:8]:
            print(f"      → {bv}")
    else:
        ok("VPC boundary crossings all go through bridge icons")

    # --- Check 9: Grouping expectations for delivery / observability ---
    # CodeCommit + CodePipeline + CodeDeploy almost always represent a delivery
    # pipeline; CloudWatch + X-Ray almost always represent observability. Both
    # groups benefit from an explicit dashed container so the operational
    # concern is visually obvious. Flag when 2+ pipeline or observability
    # icons exist without a surrounding rectangular container.
    print("\n  Operational-concern grouping:")

    DELIVERY_ICONS = {"codecommit", "codepipeline", "codedeploy", "codebuild", "codeartifact"}
    OBSERVABILITY_ICONS = {"cloudwatch_2", "cloudwatch", "xray", "cloudtrail"}

    def _find_icons(group):
        result = []
        for v in vertices:
            style_str = v.get("style", "") or ""
            if "resIcon" not in style_str:
                continue
            style = parse_style(style_str)
            res_icon = (style.get("resIcon", "") or "").replace("mxgraph.aws4.", "")
            if res_icon in group:
                geo = id_to_geo.get(v.get("id"))
                if geo:
                    result.append((v.get("id"), geo, res_icon))
        return result

    # Find plain dashed rectangles that could act as custom containers
    custom_dashed_rects = []
    for v in vertices:
        style_str = v.get("style", "") or ""
        style = parse_style(style_str)
        if (
            style.get("dashed") == "1"
            and style.get("fillColor") == "none"
            and "resIcon" not in style_str
            and "grIcon" not in style_str
            and "shape=mxgraph.aws4.group" not in style_str
        ):
            geo = id_to_geo.get(v.get("id"))
            if geo and geo.get("width", 0) > 150 and geo.get("height", 0) > 80:
                custom_dashed_rects.append((v.get("id"), geo))

    def _all_inside(icons, containers):
        if not icons:
            return True
        for _, igeo, _ in icons:
            icx = igeo["x"] + igeo["width"] / 2
            icy = igeo["y"] + igeo["height"] / 2
            inside = any(
                cgeo["x"] < icx < cgeo["x"] + cgeo["width"]
                and cgeo["y"] < icy < cgeo["y"] + cgeo["height"]
                for _, cgeo in containers
            )
            if not inside:
                return False
        return True

    grouping_issues = []
    delivery_icons = _find_icons(DELIVERY_ICONS)
    if len(delivery_icons) >= 2 and not _all_inside(delivery_icons, custom_dashed_rects):
        grouping_issues.append(
            f"{len(delivery_icons)} pipeline icons "
            f"({', '.join(i[2] for i in delivery_icons)}) but not all are "
            f"inside a dashed 'Delivery pipeline' container. Group them in a "
            f"dashed rectangle (strokeColor=#C925D1 or #E7157B)."
        )
    obs_icons = _find_icons(OBSERVABILITY_ICONS)
    if len(obs_icons) >= 2 and not _all_inside(obs_icons, custom_dashed_rects):
        grouping_issues.append(
            f"{len(obs_icons)} observability icons "
            f"({', '.join(i[2] for i in obs_icons)}) but not all are inside a "
            f"dashed 'Observability' container. Group them in a dashed "
            f"rectangle (strokeColor=#7D8998 gray or #E7157B pink)."
        )
    if grouping_issues:
        warn(f"{len(grouping_issues)} operational-concern grouping issues:")
        for gi in grouping_issues:
            print(f"      → {gi}")
    else:
        ok("Pipeline and observability services are properly grouped")

    # --- Check 6: Arrow style fidelity to the 2026 preset ---
    # Verified from slide27.xml of the 2026 deck:
    #   strokeColor=#000000, strokeWidth=1.25,
    #   endArrow=classic, endFill=1, endSize=8 — a solid filled sharp triangle.
    #   solid (no dashed).
    # Note: slide 16 labels the preset "Open Arrow Size 4" — that's the
    # PowerPoint UI name for this preset, not a description of the fill.
    # Navy #232F3E on arrows is a common LLM mistake (that's the icon tile
    # background + label text color, not the arrow stroke).
    print("\n  Arrow style fidelity:")
    OFFICIAL_ARROW_STROKE = {"#000000", "#545B64"}  # preset from drawio + AWS
    NAVY_MISTAKES = {"#232F3E", "#232F3D", "#161E2D"}
    arrow_issues = []
    for e in edges:
        eid = e.get("id", "?")
        style = parse_style(e.get("style", ""))
        sc = (style.get("strokeColor", "") or "").upper()
        sw = style.get("strokeWidth", "1")
        ea = (style.get("endArrow", "classic") or "classic").lower()
        ef = style.get("endFill", "1")
        dashed = style.get("dashed", "0")

        if sc.upper() in {c.upper() for c in NAVY_MISTAKES}:
            arrow_issues.append(
                f"'{eid}': strokeColor={sc} is navy (icon/text color). "
                f"Use black #000000 per the 2026 deck preset."
            )
        elif sc and sc.upper() not in {c.upper() for c in OFFICIAL_ARROW_STROKE} \
                and dashed != "1":
            # Non-preset solid arrow color — allowed only if part of a Style-B legend.
            # Flag as warn so the author can confirm.
            arrow_issues.append(
                f"'{eid}': strokeColor={sc} is not the 2026 preset black. "
                f"OK if the diagram uses Style B multi-encoding with a legend, "
                f"otherwise switch to #000000."
            )

    # Arrow width check — 1.25 is preset, 2 is Training & Cert
    AWS_ARROW_WIDTHS = {"1.25", "2"}
    for e in edges:
        eid = e.get("id", "?")
        style = parse_style(e.get("style", ""))
        sw = str(style.get("strokeWidth", "") or "")
        if sw and sw not in AWS_ARROW_WIDTHS:
            arrow_issues.append(
                f"'{eid}': strokeWidth={sw} is non-standard. "
                f"Use 1.25pt (preset) or 2pt (Training & Cert)."
            )

    # Arrow head check — the 2026 deck's "Open Arrow" preset (slide 16) renders
    # as a solid filled classic triangle — "Open Arrow" is PowerPoint's UI name
    # for the preset, not a description of the fill. In drawio XML that maps to
    # endArrow=classic + endFill=1.
    #  - endArrow=classic + endFill=1 → AWS preset (solid filled triangle)  ✓
    #  - endArrow=classic + endFill=0 → hollow outline triangle (not AWS)
    #  - endArrow=open    + endFill=0 → thin stealth V (not AWS)
    for e in edges:
        eid = e.get("id", "?")
        style = parse_style(e.get("style", ""))
        ea = (style.get("endArrow", "") or "").lower()
        ef = str(style.get("endFill", "") or "")
        if ea == "open":
            arrow_issues.append(
                f"'{eid}': endArrow=open renders a thin V-stealth head. "
                f"The 2026 deck preset (slide 16: 'Open Arrow Size 4') is a "
                f"solid filled triangle: endArrow=classic;endFill=1;endSize=8."
            )
        elif ea == "classic" and ef == "0":
            arrow_issues.append(
                f"'{eid}': endArrow=classic;endFill=0 is a hollow outline "
                f"triangle. The 2026 deck preset is SOLID filled — set "
                f"endFill=1 for the correct AWS Open Arrow head."
            )

    # Arrow-shape consistency check — slide 16 allows three shapes (straight,
    # right-angle/elbow, diagonal) and instructs authors to pick one per diagram.
    # A diagram that mixes elbow + diagonal is inconsistent; straight + elbow is
    # OK because elbow is the fallback when straight isn't possible.
    arrow_shapes = set()
    for e in edges:
        eid = e.get("id", "?")
        style = parse_style(e.get("style", ""))
        src = e.get("source")
        tgt = e.get("target")
        src_geo = id_to_geo.get(src)
        tgt_geo = id_to_geo.get(tgt)
        if not src_geo or not tgt_geo:
            continue

        es = style.get("edgeStyle", "")
        if es == "none":
            # Check if the endpoints are actually axis-aligned — if so, the
            # edge renders as straight; otherwise it's a diagonal.
            sx = src_geo["x"] + src_geo["width"] * float(style.get("exitX", "1"))
            sy = src_geo["y"] + src_geo["height"] * float(style.get("exitY", "0.5"))
            tx = tgt_geo["x"] + tgt_geo["width"] * float(style.get("entryX", "0"))
            ty = tgt_geo["y"] + tgt_geo["height"] * float(style.get("entryY", "0.5"))
            if abs(sx - tx) < 5 or abs(sy - ty) < 5:
                arrow_shapes.add("straight")
            else:
                arrow_shapes.add("diagonal")
        elif es == "orthogonalEdgeStyle":
            # Orthogonal — classify as straight if source/target axis-aligned,
            # otherwise elbow (the router adds one 90° bend).
            sx = src_geo["x"] + src_geo["width"] * float(style.get("exitX", "1"))
            sy = src_geo["y"] + src_geo["height"] * float(style.get("exitY", "0.5"))
            tx = tgt_geo["x"] + tgt_geo["width"] * float(style.get("entryX", "0"))
            ty = tgt_geo["y"] + tgt_geo["height"] * float(style.get("entryY", "0.5"))
            if abs(sx - tx) < 5 or abs(sy - ty) < 5:
                arrow_shapes.add("straight")
            else:
                arrow_shapes.add("elbow")

    # The mix straight+elbow is OK (elbow is the natural fallback for straight).
    # Flag diagonal mixed with anything else.
    if "diagonal" in arrow_shapes and len(arrow_shapes) > 1:
        arrow_issues.append(
            f"Mixed arrow shapes {sorted(arrow_shapes)}. Slide 16 says to pick "
            f"ONE of straight / right-angle / diagonal per diagram. Diagonal is "
            f"the last-resort escape hatch — if you're using it on some edges, "
            f"use it on all, or rework layout so right angles work everywhere."
        )

    if arrow_issues:
        # These are warnings not failures — the diagram may intentionally use
        # Style B with explicit legend. Let the author decide.
        warn(f"{len(arrow_issues)} edges deviate from the 2026 arrow preset:")
        for a in arrow_issues[:10]:
            print(f"      → {a}")
    else:
        shapes = " + ".join(sorted(arrow_shapes)) if arrow_shapes else "none"
        ok(f"All arrows follow the 2026 AWS preset (black, 1.25pt, solid filled classic triangle; shapes: {shapes})")

