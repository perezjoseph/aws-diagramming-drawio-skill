# AWS Icon Catalog for draw.io

Reference for AWS service icons, category colors, and group container styles used in
architecture diagrams.

**All values verified against three authoritative sources:**
1. **The official PPTX deck** — `AWS-Architecture-Icons-Deck_For-Light-BG_<DATE>.pptx`
   downloaded from [aws.amazon.com/architecture/icons](https://aws.amazon.com/architecture/icons/).
   Current release: **R23-2026.01.30**, light-BG variant. This is the authoritative
   source — the drawio stencils can lag it.
2. **`Sidebar-AWS4.js`** in the jgraph/drawio dev branch — the palette definitions used by drawio.
3. **`aws4.xml`** — the stencil file shipped with drawio that actually renders each icon.

When the three disagree, **the PPTX deck wins**, and this catalog is updated to
match. To verify a service's color yourself, run the bundled script:

```bash
python3 scripts/inspect_aws_deck.py /path/to/AWS-Architecture-Icons-Deck*.pptx colors \
    "Amazon Aurora service icon." "AWS Lambda service icon."
```

This unzips the deck, finds the `<p:pic>` block matching each descr, follows the
`r:embed` relationship to the embedded SVG, and extracts the non-neutral `fill=` hex.

Icons use the **filled resourceIcon style** (colored square tile, white line-art glyph)
unless the service only exists as a direct shape.

---

## Verified Service → Color Mapping (2026)

The 7-color palette is correct at the category level, but several high-traffic
services live in a surprising category. **These were recurring LLM mistakes** —
extracted fresh from the 2026 deck SVG fills:

| Service | 2026 fillColor | Category (2026) | Common LLM guess |
|---------|---------------|-----------------|------------------|
| Amazon Aurora | `#C925D1` | Databases | wrong: `#DD344C` red or `#3334B9` blue |
| Amazon DynamoDB | `#C925D1` | Databases | wrong: `#DD344C` red |
| Amazon RDS, Neptune, ElastiCache, MemoryDB, DocumentDB | `#C925D1` | Databases | wrong: `#DD344C` red |
| Amazon SageMaker | `#8C4FFF` | ML (under Analytics purple) | wrong: `#01A88D` teal (AI) |
| Amazon API Gateway | `#8C4FFF` | Networking | wrong: `#E7157B` pink |
| Elastic Load Balancing, Network LB, App LB | `#8C4FFF` | Networking | wrong: `#E7157B` pink |
| AWS Amplify | `#DD344C` | Front-End Web & Mobile | wrong: `#C925D1` fuchsia or orange |
| AWS IAM, Cognito, Secrets Manager, KMS, WAF, GuardDuty | `#DD344C` | Security | wrong: `#C925D1` fuchsia |
| Amazon Connect, Pinpoint, SES | `#DD344C` | Customer Experience | wrong: blue gradient |
| Amazon Quick Suite *(also "Amazon Quick" — short form; formerly QuickSight)* | `#DD344C` | Business Apps | wrong: `#8C4FFF` purple. Stencil: `quick_suite` (drawio v29.6.6+). Legacy QuickSight `quicksight` is still in Analytics `#8C4FFF` |
| Amazon Bedrock, Bedrock AgentCore | `#01A88D` | Artificial Intelligence | usually right |
| AWS Lambda, AWS Fargate, ECS, EKS | `#ED7100` | Compute / Containers | usually right |
| Amazon S3, EBS, EFS, FSx, Backup | `#7AA116` | Storage | usually right |
| Amazon SNS, SQS, Step Functions, EventBridge | `#E7157B` | Application Integration | usually right |
| Amazon CloudWatch, CloudFormation, CloudTrail | `#E7157B` | Management & Governance | usually right |
| AWS DataSync, Transfer Family, Migration Hub | `#01A88D` | Migration & Modernization | wrong: `#DD344C` red |
| AWS CodePipeline, CodeBuild, CodeCommit, Cloud9, X-Ray | `#C925D1` | Developer Tools | wrong: `#DD344C` red |

### The four gotchas that bite every time

1. **Aurora looks "purple"** — it is, but the AWS palette calls that shade fuchsia
   (`#C925D1`). There is no `#8C4FFF` purple in Databases.
2. **SageMaker moved** from AI teal (`#01A88D`) in older decks to Analytics purple
   (`#8C4FFF`) in the 2026 deck.
3. **QuickSight was renamed to "Amazon Quick Suite"** in the 2026 deck (also
   written as "Amazon Quick" — short form for the same service, same icon) and
   moved from Analytics (`#8C4FFF` purple) to Business Apps (`#DD344C` red).

   **The drawio `aws4` stencil ships the new icon as `mxgraph.aws4.quick_suite`**
   (verified in drawio v29.6.6's bundled `aws4.xml` — stencil name `quick suite`,
   reference style `mxgraph.aws4.quick_suite`). Use it with the Business Apps red
   fill:

   ```
   shape=mxgraph.aws4.resourceIcon;resIcon=mxgraph.aws4.quick_suite;fillColor=#DD344C
   ```

   The legacy `resIcon=quicksight` still exists in the Analytics category (old
   purple chart glyph). If a deployment still uses the pre-rename QuickSight API
   endpoints, keep `quicksight`+`#8C4FFF`. For all new 2026-style diagrams, use
   `quick_suite`+`#DD344C`.
4. **Security moved from fuchsia to red** in the 2026 deck — `#C925D1` → `#DD344C`.

---

## Official AWS Category Colors (LIGHT BG)

Current drawio uses **flat fills** for every service-icon category. The only two
palettes with gradients are `CustomerEngagement` and `ARVR`. Don't add gradients to
regular service icons.

| Hex | Categories that use it | Source |
|-----|------------------------|--------|
| `#ED7100` | Compute, Containers, Media Services, Blockchain, Quantum Technologies | sidebar |
| `#7AA116` | Storage, IoT, Cloud Financial Management | sidebar |
| `#DD344C` | **Security & Identity**, Business Applications, Customer Experience / Engagement, Front-End Web & Mobile, Robotics | sidebar + 2026 deck SVG extraction |
| `#C925D1` | **Databases**, Developer Tools, Customer Enablement, Satellite | sidebar + 2026 deck SVG extraction |
| `#8C4FFF` | Analytics, Networking & Content Delivery, Serverless, Games, Machine Learning (SageMaker etc.) | sidebar + 2026 deck SVG extraction |
| `#E7157B` | Application Integration, Management & Governance | sidebar |
| `#01A88D` | Artificial Intelligence, End User Computing, **Migration & Modernization** | 2026 deck SVG extraction (DataSync, Transfer Family, Migration Hub, Application Discovery) |

### Critical — Common LLM Mistakes

- **Databases is FUCHSIA `#C925D1`**, not blue. An earlier version of this catalog
  claimed `#3334B9` blue with a gradient — that was wrong. Blue is only used by the
  Customer Engagement palette.
- **Security & Identity is RED `#DD344C`**, not fuchsia. An even earlier version
  claimed fuchsia — also wrong.
- **No gradients on Databases, Developer Tools, or Security** in drawio. All three
  are flat fills.
- **Compute is `#ED7100`**, not `#FF9900`. The latter only appears in the dark-BG
  theme.

### Structural / Neutral Colors

| Hex | Role |
|-----|------|
| `#232F3E` | AWS "Smile" brand navy — icon tile background (General Resources); AWS Cloud group stroke; primary label text |
| `#232F3D` | Variant of navy used for Users/Client illustrations fill |
| `#FFFFFF` | Icon glyph color; light-BG canvas |
| `#F1F3F3` | Pale accent background |
| `#161E2D` | Alternate near-black text color |
| `#7D8998` | Gray for Generic groups |
| `#5A6C86` | Gray for Server/DC container fontColor |
| `#879196` | Gray for Illustrations (Users, Devices, etc.) |
| `#00A4A6` | Container teal — Region, AZ, Private subnet stroke |
| `#147EBA` | Region / AZ / Private subnet fontColor |
| `#248814` | Public subnet fontColor |
| `#3F8624` | IoT Greengrass fontColor |
| `#AAB7B8` | VPC group fontColor |
| `#DD3522` | Security group stroke |
| `#D86613` | Auto Scaling / EC2 instance contents / Elastic Beanstalk / Spot Fleet |
| `#CD2264` | AWS Account / Step Functions workflow |
| `#E6F6F7` | Private subnet fillColor (pale teal — **pre-2026 only, do not use for new diagrams**) |
| `#F2F6E8` | Public subnet fillColor (pale green — **pre-2026 only, do not use for new diagrams**) |
| `#EFF0F3` | Generic group (legacy filled variant — **2026 deck uses fillColor=none instead**) |
| `#545B64` | Arrow strokeColor in the official drawio preset arrows |
| `#666666` | Common annotation gray |

---

## Icon Style Pattern

Every service icon uses this style string:

```
sketch=0;
points=[[0,0,0],[0.25,0,0],[0.5,0,0],[0.75,0,0],[1,0,0],[0,1,0],[0.25,1,0],[0.5,1,0],[0.75,1,0],[1,1,0],[0,0.25,0],[0,0.5,0],[0,0.75,0],[1,0.25,0],[1,0.5,0],[1,0.75,0]];
outlineConnect=0;
fontColor=#232F3E;
fillColor=<CATEGORY_HEX>;
strokeColor=#ffffff;
dashed=0;
verticalLabelPosition=bottom;
verticalAlign=top;
align=center;
html=1;
fontSize=12;
fontStyle=0;
aspect=fixed;
pointerEvents=1;
shape=mxgraph.aws4.resourceIcon;
resIcon=mxgraph.aws4.<SERVICE>
```

- Canvas size: **60×60 px** (60 is the drawio working size; AWS native SVG viewBox is 40×40)
- Label sits **below** the icon, **center-aligned**, **12pt Arial**, color `#232F3E`
- Never alter icon colors, crop, flip, rotate, or scale non-proportionally
- No `gradientColor` — every regular category icon is flat fill


---

## Service Icons by Category

All names verified to exist in `aws4.xml` (the stencil) unless explicitly marked.

### Analytics — `fillColor=#8C4FFF`

| Service | resIcon |
|---------|---------|
| Amazon Athena | `athena` |
| Amazon CloudSearch | `cloudsearch2` |
| Amazon Data Firehose | `kinesis_data_firehose` |
| Amazon EMR | `emr` |
| Amazon FinSpace | `finspace` |
| Amazon Kinesis | `kinesis` |
| Amazon Kinesis Data Streams | `kinesis_data_streams` |
| Amazon Kinesis Video Streams | `kinesis_video_streams` |
| Amazon Managed Service for Apache Flink | `managed_service_for_apache_flink` |
| Amazon MSK | `managed_streaming_for_kafka` |
| Amazon OpenSearch Service | `elasticsearch_service` |
| Amazon QuickSight | `quicksight` |
| Amazon Redshift | `redshift` |
| AWS Clean Rooms | `clean_rooms` |
| AWS Data Exchange | `data_exchange` |
| AWS Glue | `glue` |
| AWS Lake Formation | `lake_formation` |

### Application Integration — `fillColor=#E7157B`

| Service | resIcon |
|---------|---------|
| Amazon AppFlow | `appflow` |
| Amazon API Gateway | `api_gateway` |
| Amazon EventBridge | `eventbridge` |
| Amazon MQ | `mq` |
| Amazon MWAA | `managed_workflows_for_apache_airflow` |
| Amazon SNS | `sns` |
| Amazon SQS | `sqs` |
| AWS AppSync | `appsync` |
| AWS Express Workflows | `express_workflow` |
| AWS Step Functions | `step_functions` |

### Artificial Intelligence / ML — `fillColor=#01A88D`

| Service | resIcon |
|---------|---------|
| Amazon Bedrock | `bedrock` |
| Amazon Bedrock AgentCore | `bedrock_agentcore` ¹ |
| Amazon Comprehend | `comprehend` |
| Amazon Kendra | `kendra` |
| Amazon Lex | `lex` |
| Amazon Polly | `polly` |
| Amazon Rekognition | `rekognition` |
| Amazon SageMaker | `sagemaker` |
| Amazon SageMaker Canvas | `sagemaker_canvas` |
| Amazon Textract | `textract` |
| Amazon Transcribe | `transcribe` |
| Amazon Translate | `translate` |
| Amazon Q Developer | `q_developer` ¹ |
| Amazon Q | `q` ¹ |
| Amazon Nova | `nova` ¹ |

¹ Registered in the drawio sidebar (v29+) but may not be in older bundled `aws4.xml`
stencils. If the icon renders as broken, update drawio or fall back to
`sagemaker` / `bedrock` / `comprehend`.

### Business Applications — `fillColor=#DD344C`

| Service | resIcon |
|---------|---------|
| Amazon Chime | `chime` |
| Amazon Connect | `connect` |
| Amazon Quick Suite *(also "Amazon Quick")* | `quick_suite` |
| Amazon WorkMail | `workmail` |

### Cloud Financial Management — `fillColor=#7AA116`

| Service | resIcon |
|---------|---------|
| AWS Billing Conductor | `billing_conductor` ¹ |
| AWS Budgets | `budgets` |
| AWS Cost Explorer | `cost_explorer` |

### Compute — `fillColor=#ED7100`

| Service | resIcon |
|---------|---------|
| Amazon EC2 | `ec2` |
| Amazon EC2 Auto Scaling | `auto_scaling2` |
| Amazon Lightsail | `lightsail` |
| AWS App Runner | `app_runner` |
| AWS Batch | `batch` |
| AWS Elastic Beanstalk | `elastic_beanstalk` |
| AWS Lambda | `lambda` |
| AWS Local Zones | `local_zones` |
| AWS Outposts | `outposts_family` |
| AWS Wavelength | `wavelength` |

### Containers — `fillColor=#ED7100`

| Service | resIcon |
|---------|---------|
| Amazon ECR | `ecr` |
| Amazon ECS | `ecs` |
| Amazon EKS | `eks` |
| AWS Fargate | `fargate` |

### Customer Enablement — `fillColor=#C925D1`

| Service | resIcon |
|---------|---------|
| AWS IQ | `iq` |
| AWS Managed Services | `managed_services` |
| AWS Professional Services | `professional_services` |
| AWS Support | `support` |

### Customer Experience / Engagement — `fillColor=#DD344C`

| Service | resIcon |
|---------|---------|
| Amazon Connect | `connect` |
| Amazon Pinpoint | `pinpoint` |
| Amazon SES | `simple_email_service` |

### Databases — `fillColor=#C925D1`

| Service | resIcon |
|---------|---------|
| Amazon Aurora | `aurora` |
| Amazon DocumentDB | `documentdb_with_mongodb_compatibility` |
| Amazon DynamoDB | `dynamodb` |
| Amazon ElastiCache | `elasticache` |
| Amazon Keyspaces | `keyspaces` |
| Amazon MemoryDB for Redis | `memorydb_for_redis` |
| Amazon Neptune | `neptune` |
| Amazon RDS | `rds` |
| Amazon Timestream | `timestream` |
| AWS DMS | `database_migration_service` |

### Developer Tools — `fillColor=#C925D1`

| Service | resIcon |
|---------|---------|
| AWS Cloud Development Kit (CDK) | `cloud_development_kit` |
| AWS Cloud9 | `cloud9` |
| AWS CloudShell | `cloudshell` |
| AWS CodeArtifact | `codeartifact` |
| AWS CodeBuild | `codebuild` |
| AWS CodeCommit | `codecommit` |
| AWS CodeDeploy | `codedeploy` |
| AWS CodePipeline | `codepipeline` |
| AWS X-Ray | `xray` |

### End User Computing — `fillColor=#01A88D`

| Service | resIcon |
|---------|---------|
| Amazon AppStream 2.0 | `appstream_20` |
| Amazon WorkSpaces | `workspaces` |

### Front-End Web & Mobile — `fillColor=#DD344C`

| Service | resIcon |
|---------|---------|
| AWS Amplify | `amplify` |
| AWS Device Farm | `device_farm` |
| Amazon Location Service | `location_service` |

### Internet of Things — `fillColor=#7AA116`

| Service | resIcon |
|---------|---------|
| AWS IoT Core | `iot_core` |
| AWS IoT Events | `iot_events` |
| AWS IoT Greengrass | `greengrass` |
| AWS IoT SiteWise | `iot_sitewise` |
| FreeRTOS | `freertos` |

### Management & Governance — `fillColor=#E7157B`

| Service | resIcon |
|---------|---------|
| Amazon CloudWatch | `cloudwatch_2` |
| Amazon Managed Grafana | `managed_service_for_grafana` |
| Amazon Managed Service for Prometheus | `managed_service_for_prometheus` |
| AWS Auto Scaling | `auto_scaling` |
| AWS CloudFormation | `cloudformation` |
| AWS CloudTrail | `cloudtrail` |
| AWS Config | `config` |
| AWS Control Tower | `control_tower` |
| AWS DevOps Guru | `devops_guru` |
| AWS DevOps Agent | `devops_agent` ¹ |
| AWS Organizations | `organizations` |
| AWS Partner Central | `partner_central` ¹ |
| AWS Proton | `proton` |
| AWS Systems Manager | `systems_manager` |
| AWS Trusted Advisor | `trusted_advisor` |

### Media Services — `fillColor=#ED7100`

| Service | resIcon |
|---------|---------|
| Amazon Elastic Transcoder | `elastic_transcoder` |
| AWS Elemental MediaConnect | `elemental_mediaconnect` |
| AWS Elemental MediaConvert | `elemental_mediaconvert` |
| AWS Elemental MediaLive | `elemental_medialive` |
| AWS Elemental MediaPackage | `elemental_mediapackage` |
| AWS Elemental MediaStore | `elemental_mediastore` |
| AWS Elemental MediaTailor | `elemental_mediatailor` |

### Migration & Modernization — `fillColor=#01A88D`

| Service | resIcon |
|---------|---------|
| AWS Application Discovery Service | `application_discovery_service` |
| AWS Application Migration Service | `cloudendure_migration` |
| AWS DataSync | `datasync` |
| AWS DMS | `database_migration_service` |
| AWS Elastic Disaster Recovery | `cloudendure_disaster_recovery` |
| AWS Migration Hub | `migration_hub` |
| AWS Transfer Family | `transfer_family` |

### Networking & Content Delivery — `fillColor=#8C4FFF`

| Service | resIcon |
|---------|---------|
| Amazon CloudFront | `cloudfront` |
| Amazon Route 53 | `route_53` |
| Amazon VPC | `vpc` |
| Amazon VPC Lattice | `vpc_lattice` |
| AWS App Mesh | `app_mesh` |
| AWS Client VPN | `client_vpn` |
| AWS Direct Connect | `direct_connect` |
| AWS Global Accelerator | `global_accelerator` |
| AWS PrivateLink | `privatelink` |
| AWS Site-to-Site VPN | `site_to_site_vpn` |
| AWS Transit Gateway | `transit_gateway` |
| Elastic Load Balancing | `elastic_load_balancing` |

### Security, Identity & Compliance — `fillColor=#DD344C`

| Service | resIcon |
|---------|---------|
| Amazon Cognito | `cognito` |
| Amazon GuardDuty | `guardduty` |
| Amazon Inspector | `inspector` |
| Amazon Macie | `macie` |
| AWS Certificate Manager | `certificate_manager` |
| AWS IAM | `identity_and_access_management` |
| AWS IAM Identity Center | `single_sign_on` |
| AWS KMS | `key_management_service` |
| AWS Network Firewall | `network_firewall` |
| AWS Secrets Manager | `secrets_manager` |
| AWS Security Hub | `security_hub` |
| AWS Shield | `shield` |
| AWS WAF | `waf` |

*Note: IAM Identity Center's stencil name is the legacy `single_sign_on`.*

### Serverless — `fillColor=#8C4FFF` (framing container only)

Serverless is a cross-category framing. When you label a container "Serverless,"
use purple stroke; but the service icons inside keep their home category colors.

| Service | resIcon | Home category |
|---------|---------|---------------|
| AWS Lambda | `lambda` | Compute (orange) |
| AWS Fargate | `fargate` | Containers (orange) |
| AWS Step Functions | `step_functions` | App Integration (pink) |
| Amazon EventBridge | `eventbridge` | App Integration (pink) |
| AWS SAM | `serverless_application_repository` | — (purple) |

### Storage — `fillColor=#7AA116`

| Service | resIcon |
|---------|---------|
| Amazon EBS | `elastic_block_store` |
| Amazon EFS | `elastic_file_system` |
| Amazon FSx | `fsx` |
| Amazon S3 | `s3` |
| Amazon S3 Glacier | `glacier` |
| AWS Backup | `backup` |
| AWS Snow Family (Snowball) | `snowball` |
| AWS Snowball Edge | `snowball_edge` |
| AWS Snowcone | `snowcone` |
| AWS Storage Gateway | `storage_gateway` |


---

## Resource-Level Icons (No resourceIcon Variant)

Certain resources exist only as direct shapes (no colored tile wrapper). Set
`fillColor` to the category hex and `strokeColor=#ffffff`.

| Icon | Shape name | `fillColor` |
|------|-----------|-------------|
| Internet Gateway | `internet_gateway` | `#8C4FFF` |
| NAT Gateway | `nat_gateway` | `#8C4FFF` |
| Customer Gateway | `customer_gateway` | `#8C4FFF` |
| Network Load Balancer | `network_load_balancer` | `#8C4FFF` |
| Application Load Balancer | `application_load_balancer` | `#8C4FFF` |
| EC2 Instance | `instance` | `#ED7100` |
| Lambda Function | `lambda_function` | `#ED7100` |
| IAM Role | `role` | `#DD344C` |
| IAM Policy | `policy` | `#DD344C` |
| IAM User | `user` | `#DD344C` |

For VPN Gateway, there is no dedicated stencil — use `vpc` or `site_to_site_vpn`
from the Networking category instead.

---

## AWS Group Containers

**Every AWS container uses `fillColor=none` in the 2026 deck.** This was verified by
extracting the `<p:spPr>` blocks of every rectangle/roundRect on slides 20, 21, and
25 — 100% of them have `<a:noFill/>`. Older versions of this skill showed pale
subnet fills (`#E6F6F7` teal for private, `#F2F6E8` green for public); those
colors are NOT in the current deck. Emit `fillColor=none` on every group
container; let the stroke color plus corner grIcon carry the visual semantics.

**Every AWS container label is 12pt Arial, regular weight (NOT bold).** Verified
by inspecting `<a:rPr>` on every container label on slides 21 and 25 —
`b="0"` (or absent, which defaults to regular) and `sz="1200"` (12pt). Previous
versions of this skill set `fontStyle=1;fontSize=14` on "AWS Cloud" and other
groups — those diagrams look subtly off vs. the deck. **Never set
`fontStyle=1` on a container cell**; never set `fontSize=14`. The single
consistent rule: `fontSize=12;fontFamily=Arial`, no `fontStyle` attribute at all.

Group containers are NOT all styled the same. Each one specifies a stroke color,
dash style, grIcon, and sometimes a fill color — verified from the canonical
`Sidebar-AWS4.js` AWS Groups palette.

All containers share this common style foundation:

```
shape=mxgraph.aws4.group;    (or groupCenter for Auto Scaling)
grIcon=<specific>;
strokeColor=<specific>;
fillColor=none;              (or pale fill for Public/Private subnet)
fontColor=<specific>;
dashed=<0 or 1>;
verticalAlign=top;
align=left;                  (center for Auto Scaling)
spacingLeft=30;              (skip for Auto Scaling, which uses spacingTop=25)
html=1;
container=0;                 (use 0 in hand-written XML so child coordinates are absolute)
```

### Container Style Table

| Container | `grIcon` | `strokeColor` | `fontColor` | `fillColor` | `dashed` |
|-----------|----------|---------------|-------------|-------------|----------|
| AWS Cloud (alt) | `group_aws_cloud_alt` | `#232F3E` | `#232F3E` | `none` | 0 |
| AWS Cloud (cloud-only) | `group_aws_cloud` | `#232F3E` | `#232F3E` | `none` | 0 |
| Region | `group_region` | `#00A4A6` | `#147EBA` | `none` | **1** |
| Availability Zone | *(none — plain rect)* | `#147EBA` | `#147EBA` | `none` | **1** |
| VPC | `group_vpc2` | `#8C4FFF` | `#AAB7B8` | `none` | 0 |
| Private subnet | `group_security_group` + `grStroke=0` | `#00A4A6` | `#147EBA` | `none` | 0 |
| Public subnet | `group_security_group` + `grStroke=0` | `#7AA116` | `#248814` | `none` | 0 |
| Security group | *(none — plain rect)* | `#DD3522` | `#DD3522` | `none` | 0 |
| Auto Scaling group | `group_auto_scaling_group` + `grStroke=1` (and `shape=groupCenter`) | `#D86613` | `#D86613` | `none` | **1** |
| AWS Account | `group_account` | `#CD2264` | `#CD2264` | `none` | 0 |
| EC2 instance contents | `group_ec2_instance_contents` | `#D86613` | `#D86613` | `none` | 0 |
| Elastic Beanstalk container | `group_elastic_beanstalk` | `#D86613` | `#D86613` | `none` | 0 |
| Spot Fleet | `group_spot_fleet` | `#D86613` | `#D86613` | `none` | 0 |
| Step Functions workflow | `group_aws_step_functions_workflow` | `#CD2264` | `#CD2264` | `none` | 0 |
| Server contents | `group_on_premise` | `#7D8998` | `#5A6C86` | `none` | 0 |
| Corporate data center | `group_corporate_data_center` | `#7D8998` | `#5A6C86` | `none` | 0 |
| IoT Greengrass | `group_iot_greengrass` | `#7AA116` | `#3F8624` | `none` | 0 |
| IoT Greengrass Deployment | `group_iot_greengrass_deployment` | `#7AA116` | `#3F8624` | `none` | 0 |
| Generic group (dashed) | *(none — plain rect)* | `#5A6C86` | `#5A6C86` | `none` | **1** |
| Generic group (filled) | *(none — plain rect)* | *(none)* | `#232F3D` | `#EFF0F3` | 0 |

### Critical Corrections vs. Previous Skill Versions

- **Public/Private subnets** use `grIcon=group_security_group` with `grStroke=0` —
  NOT nonexistent `group_public_subnet` / `group_private_subnet` grIcons. The
  stroke & fill colors differentiate them.
- **Security group** is a plain dashed rectangle (no grIcon). Stroke is `#DD3522`,
  slightly different from the `#DD344C` Security-category service icons use.
- **Auto Scaling group** uses `shape=mxgraph.aws4.groupCenter` (not `group`), with
  `grStroke=1`, `align=center` (not left), `spacingTop=25`, and `dashed=1`.
- **VPC** uses `group_vpc2` (v2 artwork), not legacy `group_vpc`.
- VPC fontColor is **`#AAB7B8`** (muted gray-blue), NOT `#232F3E`.

### Ready-to-Paste Group Examples

**AWS Cloud:**
```xml
<mxCell id="awsCloud" value="AWS Cloud"
  style="shape=mxgraph.aws4.group;grIcon=mxgraph.aws4.group_aws_cloud_alt;strokeColor=#232F3E;fillColor=none;fontColor=#232F3E;fontSize=12;fontFamily=Arial;verticalAlign=top;align=left;spacingLeft=30;container=0;html=1"
  vertex="1" parent="1">
  <mxGeometry x="80" y="40" width="1200" height="800" as="geometry" />
</mxCell>
```

**Region (dashed teal):**
```xml
<mxCell id="usEast1" value="us-east-1"
  style="shape=mxgraph.aws4.group;grIcon=mxgraph.aws4.group_region;strokeColor=#00A4A6;fillColor=none;fontColor=#147EBA;verticalAlign=top;align=left;spacingLeft=30;dashed=1;container=0;html=1"
  vertex="1" parent="1">
  <mxGeometry x="120" y="100" width="1100" height="700" as="geometry" />
</mxCell>
```

**Availability Zone (plain dashed rect — no grIcon):**
```xml
<mxCell id="az1" value="Availability Zone 1"
  style="fillColor=none;strokeColor=#147EBA;dashed=1;verticalAlign=top;fontStyle=0;fontColor=#147EBA;whiteSpace=wrap;html=1;container=0"
  vertex="1" parent="1">
  <mxGeometry x="160" y="180" width="500" height="500" as="geometry" />
</mxCell>
```

**VPC (uses `group_vpc2`, muted `#AAB7B8` font):**
```xml
<mxCell id="vpc" value="VPC — 10.0.0.0/16"
  style="shape=mxgraph.aws4.group;grIcon=mxgraph.aws4.group_vpc2;strokeColor=#8C4FFF;fillColor=none;fontColor=#AAB7B8;verticalAlign=top;align=left;spacingLeft=30;container=0;html=1"
  vertex="1" parent="1">
  <mxGeometry x="180" y="240" width="900" height="420" as="geometry" />
</mxCell>
```

**Private subnet (teal stroke, `group_security_group` icon with `grStroke=0`, pale teal fill):**
```xml
<mxCell id="privSubnet" value="Private subnet"
  style="shape=mxgraph.aws4.group;grIcon=mxgraph.aws4.group_security_group;grStroke=0;strokeColor=#00A4A6;fillColor=none;fontColor=#147EBA;verticalAlign=top;align=left;spacingLeft=30;container=0;html=1"
  vertex="1" parent="1">
  <mxGeometry x="220" y="320" width="380" height="280" as="geometry" />
</mxCell>
```

**Public subnet (green stroke, `group_security_group` icon with `grStroke=0`, pale green fill):**
```xml
<mxCell id="pubSubnet" value="Public subnet"
  style="shape=mxgraph.aws4.group;grIcon=mxgraph.aws4.group_security_group;grStroke=0;strokeColor=#7AA116;fillColor=none;fontColor=#248814;verticalAlign=top;align=left;spacingLeft=30;container=0;html=1"
  vertex="1" parent="1">
  <mxGeometry x="640" y="320" width="380" height="280" as="geometry" />
</mxCell>
```

**Security group (plain red rect — no grIcon):**
```xml
<mxCell id="sg" value="Security group"
  style="fillColor=none;strokeColor=#DD3522;verticalAlign=top;fontStyle=0;fontColor=#DD3522;whiteSpace=wrap;html=1;container=0"
  vertex="1" parent="1">
  <mxGeometry x="240" y="360" width="320" height="200" as="geometry" />
</mxCell>
```

**Auto Scaling group (dashed orange, `groupCenter` shape, centered label, `grStroke=1`):**
```xml
<mxCell id="asg" value="Auto Scaling group"
  style="shape=mxgraph.aws4.groupCenter;grIcon=mxgraph.aws4.group_auto_scaling_group;grStroke=1;strokeColor=#D86613;fillColor=none;fontColor=#D86613;verticalAlign=top;align=center;spacingTop=25;dashed=1;container=0;html=1"
  vertex="1" parent="1">
  <mxGeometry x="260" y="380" width="280" height="200" as="geometry" />
</mxCell>
```

**AWS Account:**
```xml
<mxCell id="prodAccount" value="Production Account"
  style="shape=mxgraph.aws4.group;grIcon=mxgraph.aws4.group_account;strokeColor=#CD2264;fillColor=none;fontColor=#CD2264;fontSize=12;fontFamily=Arial;verticalAlign=top;align=left;spacingLeft=30;container=0;html=1"
  vertex="1" parent="1">
  <mxGeometry x="100" y="100" width="1000" height="700" as="geometry" />
</mxCell>
```

### Canonical Nesting Order

```
AWS Cloud
└── AWS Account
    └── Region                (teal stroke, dashed)
        └── VPC              (purple, group_vpc2)
            ├── Availability Zone       (blue-teal stroke, dashed, plain rect)
            │   ├── Public subnet       (green stroke, pale green fill)
            │   │   └── Load Balancer / NAT / Bastion
            │   └── Private subnet      (teal stroke, pale teal fill)
            │       └── Auto Scaling group    (orange, dashed, groupCenter)
            │           └── EC2 instance contents
            └── Security group          (red plain rect, crosses AZs)
```

**Buffer rule**: nested groups need ≥ 0.05" (≈5px) on every side — never let inner
borders touch outer borders.

**Crossing groups**: Auto Scaling and Security Group *overlay* subnets/AZs to show
cross-cutting membership. They do not strictly nest.

### Which AWS Services Go Inside a VPC

Only services that **run on customer-managed ENIs in customer subnets** belong
inside the VPC container. Fully-managed AWS services live in AWS Cloud but
*outside* the VPC box — they are accessed from the VPC via regional endpoints,
VPC interface endpoints, or VPC Connection bridges.

**Inside VPC (has subnets, route tables, ENIs):**
- EC2 instances, ECS on EC2, EKS worker nodes
- RDS / Aurora clusters (they run in subnets)
- ElastiCache clusters
- Redshift clusters
- Elastic Load Balancers (ALB, NLB, CLB)
- NAT gateways, transit gateways, VPC endpoints
- Lambda functions **only if VPC-attached** (default Lambda is not in VPC)
- Fargate tasks (use customer subnets via awsvpc network mode)

**Outside VPC (fully-managed AWS service plane):**
- S3, DynamoDB, SQS, SNS, EventBridge
- Bedrock, SageMaker endpoint (unless VPC-attached), SageMaker Studio
- Quick Suite, QuickSight
- CloudWatch, X-Ray, CloudTrail
- API Gateway (regional/edge-optimized), AppSync
- Amplify, CloudFront, Route 53
- CodeCommit, CodePipeline, CodeBuild, CodeDeploy
- Secrets Manager, IAM, KMS, STS
- Bedrock AgentCore, Bedrock Data Automation
- Step Functions, Glue, Athena

**Rule of thumb**: if the service has a public/regional endpoint and no
`subnet_ids` in its CloudFormation/CDK config, it belongs OUTSIDE the VPC box.

### VPC Connection Pattern (Quick Suite, Redshift Federated, etc.)

When a managed service outside the VPC needs to read data inside the VPC (like
Quick Suite reading from Aurora, or Bedrock Knowledge Base reading from RDS),
draw it as a **VPC Connection bridge icon** between them — don't draw a direct
arrow that punches through the VPC boundary unexplained.

Use `resIcon=mxgraph.aws4.vpc_privatelink` (AWS PrivateLink service icon) as
the bridge. The `vpc_privatelink` icon is AWS's authoritative representation
for VPC PrivateLink, which is the underlying mechanism for Quick Suite VPC
Connections, AppFlow, AWS Glue Connections, and similar cross-boundary access.

```xml
<!-- Bridge icon sitting between VPC and managed service -->
<mxCell id="vpc_conn" parent="1" style="sketch=0;outlineConnect=0;fontColor=#232F3E;fillColor=#8C4FFF;strokeColor=#ffffff;shape=mxgraph.aws4.resourceIcon;resIcon=mxgraph.aws4.vpc_privatelink;fontFamily=Arial;verticalLabelPosition=bottom;verticalAlign=top;align=center;html=1;fontSize=12;aspect=fixed;" value="VPC Connection&#xa;AWS PrivateLink" vertex="1">
  <mxGeometry height="48" width="48" x="..." y="..." as="geometry" />
</mxCell>

<!-- Arrows: aurora → vpc_conn → quick_suite -->
```

Do NOT draw `aurora → quick_suite` as a direct arrow crossing the VPC boundary.
That misrepresents the architecture — Aurora cannot be reached from outside its
VPC without an explicit bridge.

### Custom Dashed Containers for Operational Concerns

Not every grouping is a VPC/subnet/region. Real architectures need to group
**functional concerns** like delivery pipelines and observability, which cross
VPC and account boundaries. For these, use a **plain dashed rectangle** (no
grIcon) with a color that matches the AWS category of the services inside:

| Concern | Services Inside | Stroke Color | Rationale |
|---------|-----------------|--------------|-----------|
| Delivery pipeline | CodeCommit, CodePipeline, CodeBuild, CodeDeploy, CodeArtifact | `#C925D1` (Developer Tools) or `#E7157B` (Mgmt & Governance) | Match Dev Tools color or pink if mixed |
| Observability | CloudWatch, X-Ray, CloudTrail, Managed Grafana, Managed Prometheus | `#7D8998` (Gray / generic) or `#E7157B` (CloudWatch color) | Gray is neutral when the group spans multiple categories |
| Security & Compliance | GuardDuty, Security Hub, Macie, Detective | `#DD344C` (Security red) | Use security red |
| Data Platform | Glue, Lake Formation, Athena, EMR | `#8C4FFF` (Analytics purple) | Match analytics color |
| Edge / CDN | CloudFront, Route 53, Shield, WAF, Global Accelerator | `#8C4FFF` (Networking purple) | Match networking color |

**Style for operational-concern containers**:
```xml
<mxCell id="pipeline_box" parent="1" style="rounded=0;whiteSpace=wrap;html=1;dashed=1;strokeColor=#E7157B;fillColor=none;verticalAlign=top;align=left;spacingLeft=12;spacingTop=6;fontColor=#E7157B;fontSize=12;fontFamily=Arial;" value="Delivery pipeline" vertex="1">
  <mxGeometry height="140" width="540" x="..." y="..." as="geometry" />
</mxCell>
```

Key rules for custom containers:
- **Always dashed** (`dashed=1`) to distinguish from AWS Group containers
- **Always `fillColor=none`** — same rule as every AWS container
- **12pt Arial regular label**, colored same as stroke
- **Title in top-left** via `verticalAlign=top;align=left;spacingLeft=12;spacingTop=6`
- **No grIcon** — these are not AWS-native groupings
- **Size to contents + 30px padding** on every side

---


## Special Shapes (Users, Clients, etc.)

These are in the "General Resources" and "Illustrations" palettes, not a service
category. They use dark navy fill, no stroke.

| Shape | Style |
|-------|-------|
| Users | `shape=mxgraph.aws4.users;fillColor=#232F3D;strokeColor=none` |
| Mobile Client | `shape=mxgraph.aws4.mobile;fillColor=#232F3D;strokeColor=none` |
| Client | `shape=mxgraph.aws4.client;fillColor=#232F3D;strokeColor=none` |
| Traditional Server | `shape=mxgraph.aws4.traditional_server;fillColor=#232F3D;strokeColor=none` |
| Corporate Data Center (icon) | `shape=mxgraph.aws4.corporate_data_center;fillColor=#232F3D;strokeColor=none` |
| Servers | `shape=mxgraph.aws4.servers;fillColor=#232F3D;strokeColor=none` |

Illustrations (larger decorative versions) use `illustration_users`,
`illustration_notification`, `illustration_devices`, `illustration_desktop`,
`illustration_office_building` with `fillColor=#879196;fontColor=#545B64`.

---

## Name-Change Gotchas

Stencil names drift from service branding and from older skill docs. These are
the confirmed correct names (verified against `aws4.xml`):

| Service / display name | **Correct resIcon** | Common wrong guesses |
|-------------------------|---------------------|----------------------|
| CloudWatch | `cloudwatch_2` | `cloudwatch` (legacy) |
| CloudSearch | `cloudsearch2` | `cloudsearch` (legacy) |
| Data Firehose | `kinesis_data_firehose` | `data_firehose`, `firehose` |
| SNS | `sns` | `simple_notification_service` |
| SQS | `sqs` | `simple_queue_service` |
| SES | `ses` | `simple_email_service` |
| IAM | `identity_and_access_management` | `iam` |
| IAM Identity Center | `single_sign_on` | `iam_identity_center`, `sso` |
| KMS | `key_management_service` | `kms` |
| EBS | `elastic_block_store` | `ebs` |
| EFS | `elastic_file_system` | `efs` |
| ECR | `ecr` | `elastic_container_registry` |
| ECS | `ecs` | `elastic_container_service` |
| EKS | `eks` | `elastic_kubernetes_service` |
| X-Ray | `xray` | `x_ray`, `x-ray` |
| AppStream 2.0 | `appstream_20` | `appstream_2_0` |
| S3 Glacier | `glacier` | `s3_glacier` |
| OpenSearch Service | `elasticsearch_service` | `opensearch_service`, `opensearch` |
| IoT Greengrass | `greengrass` | `iot_greengrass` |
| EC2 Auto Scaling | `auto_scaling2` | `ec2_auto_scaling`, `auto_scaling` |
| AWS Auto Scaling | `auto_scaling` | — (distinct service) |
| Application Migration Service | `cloudendure_migration` | `mgn`, `application_migration_service` |
| Elastic Disaster Recovery | `cloudendure_disaster_recovery` | `elastic_disaster_recovery`, `drs` |
| Snow Family | `snowball` / `snowball_edge` / `snowcone` | `snow_family` |
| AWS SAM | `serverless_application_repository` | `sam`, `serverless_application_model` |
| VPN Gateway (resource) | use `site_to_site_vpn` or `client_vpn` | `virtual_private_gateway` |
| MSK | `managed_streaming_for_kafka` | `msk` |
| MWAA | `managed_workflows_for_apache_airflow` | `mwaa` |
| Managed Grafana | `managed_service_for_grafana` | `managed_grafana` |
| Managed Prometheus | `managed_service_for_prometheus` | `managed_prometheus` |
| Express Workflows | `express_workflow` | `express_workflows` |
| AWS Budgets | `budgets` | `aws_budgets` |
| PrivateLink | `privatelink` | `vpc_privatelink` |
| DevOps Guru | `devops_guru` | `devops_agent` (newer name, not in all stencils) |

Stencil XML internally uses spaces (`cloudwatch 2`) but every `resIcon` style
reference uses underscores (`cloudwatch_2`).

### Names That Exist in Sidebar but Not in Older Stencils

These are registered in the drawio v29+ sidebar but may not be present in older
bundled `aws4.xml` files. If an icon renders blank, update drawio or use the
fallback suggested.

| Sidebar-only name | Fallback |
|-------------------|----------|
| `bedrock_agentcore` | `bedrock` |
| `sagemaker_ai` | `sagemaker` |
| `devops_agent` | `devops_guru` |
| `security_agent` | `security_hub` |
| `multicloud_and_hybrid` | no fallback — use a Generic group |
| `partner_central` | no fallback — use Generic |
| `q_developer` | use `q` |
| `quick_suite` | no fallback — use Generic |
| `nova` | use `bedrock` |

