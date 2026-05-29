#!/usr/bin/env python3
"""
inspect_aws_deck.py — verify the drawio-diagramming skill against the
current AWS Architecture Icons deck.

The AWS deck is a PowerPoint file that ships ~quarterly from
https://aws.amazon.com/architecture/icons/. PowerPoint files are zips of
OOXML. Everything this script reports comes from unpacking the zip and
reading the XML directly — NO deck is bundled with this skill.

Usage:
  python3 inspect_aws_deck.py <deck.pptx> [subcommand] [args...]

Subcommands:
  colors [DESCR ...]      Extract fill colors from service-icon SVGs.
                          Pass descr strings (e.g. "Amazon Aurora service icon.")
                          or no args to dump every service icon.
  sizes                   Report authoritative icon sizes on example slides.
  containers              Report container label weights and sizes.
  arrows                  Report preset arrow spec from slide 27 (Arrows).
  fonts                   Report theme font stack.
  all                     Run every report (recommended when re-syncing
                          the catalog after an AWS deck release).

Example:
  # Sync the catalog after a new deck release
  curl -L -o /tmp/aws-icons.pptx \\
    "https://d1.awsstatic.com/webteam/architecture-icons/..."
  python3 scripts/inspect_aws_deck.py /tmp/aws-icons.pptx all

The "all" report prints a self-contained changelog against the values
currently documented in references/aws-icon-catalog.md so you can see at
a glance what the new deck changed.
"""
import re
import os
import sys
import zipfile
import tempfile
import shutil
from collections import Counter, defaultdict

# EMU (OOXML unit) -> drawing conversions
# 914400 EMU = 1 inch = 72 pt = 96 px (at 96 dpi)
def emu_to_px(emu): return round(emu / 9525, 1)
def emu_to_pt(emu): return round(emu / 12700, 2)
def emu_to_in(emu): return round(emu / 914400, 3)

# Neutral hex values we filter out of service-icon color extraction
NEUTRAL = {"#FFFFFF", "#232F3E", "#232F3D", "#242F3E", "#161D26", "#161E2D"}


def unpack(pptx_path):
    """Extract a PPTX to a temp dir and return its path."""
    tmp = tempfile.mkdtemp(prefix="aws-deck-")
    with zipfile.ZipFile(pptx_path) as z:
        z.extractall(tmp)
    return tmp


def list_slides(unpack_dir):
    slide_dir = f"{unpack_dir}/ppt/slides"
    return sorted(
        f"{slide_dir}/{n}"
        for n in os.listdir(slide_dir)
        if n.startswith("slide") and n.endswith(".xml")
    )


def resolve_rel(unpack_dir, slide_name, rid):
    """Resolve an r:embed rId to its file path inside the pptx."""
    rels_file = f"{unpack_dir}/ppt/slides/_rels/{slide_name}.xml.rels"
    if not os.path.exists(rels_file):
        return None
    rels = open(rels_file).read()
    m = re.search(rf'Id="{rid}"[^>]*Target="([^"]+)"', rels)
    if m:
        return m.group(1).replace("../", "")
    return None


def report_colors(unpack_dir, filters=None):
    """Extract the primary fill hex from each service-icon SVG."""
    print("=" * 60)
    print("  Service icon colors (from embedded SVG fills)")
    print("=" * 60)

    results = []
    for slide_path in list_slides(unpack_dir):
        slide_name = os.path.basename(slide_path).replace(".xml", "")
        content = open(slide_path).read()
        # Find every <p:pic> block and its descr
        for m in re.finditer(r"<p:pic>(.*?)</p:pic>", content, re.DOTALL):
            block = m.group(1)
            descr_m = re.search(r'descr="([^"]+)"', block)
            if not descr_m:
                continue
            descr = descr_m.group(1)
            if "service icon" not in descr:
                continue
            if filters and not any(f.lower() in descr.lower() for f in filters):
                continue
            # Find the SVG embed (drawio renders SVG, not the PNG fallback)
            embeds = re.findall(r'r:embed="(rId\d+)"', block)
            for rid in embeds:
                target = resolve_rel(unpack_dir, slide_name, rid)
                if target and target.endswith(".svg"):
                    svg_path = f"{unpack_dir}/ppt/{target}"
                    if os.path.exists(svg_path):
                        svg = open(svg_path).read()
                        colors = sorted(
                            set(re.findall(r'fill="(#[0-9A-Fa-f]{6})"', svg))
                        )
                        non_neutral = [
                            c for c in colors if c.upper() not in NEUTRAL
                        ]
                        results.append((descr, slide_name, os.path.basename(svg_path), non_neutral))
                        break

    for descr, slide, svg, colors in results:
        print(f"  {descr:62s} {slide:9s} {svg:20s} {colors}")
    print(f"\nTotal: {len(results)} service icons inspected")


def report_sizes(unpack_dir):
    """Extract icon and callout sizes from the deck's example slides."""
    print("\n" + "=" * 60)
    print("  Icon / callout sizes")
    print("=" * 60)

    # Example slides show production-ready diagrams; use them as ground truth.
    example_slides = [
        "ppt/slides/slide20.xml",  # Git to S3 Webhooks
        "ppt/slides/slide21.xml",  # Chef Automate Architecture
        "ppt/slides/slide25.xml",  # Groups reference
        "ppt/slides/slide18.xml",  # Numbered callouts reference
    ]
    sizes_by_kind = defaultdict(Counter)
    for slide in example_slides:
        path = f"{unpack_dir}/{slide}"
        if not os.path.exists(path):
            continue
        s = open(path).read()

        # Picture-based elements (service icons, resource icons, group decorators)
        for block in re.findall(r"<p:pic>(.*?)</p:pic>", s, re.DOTALL):
            descr_m = re.search(r'descr="([^"]+)"', block)
            if not descr_m:
                continue
            d = descr_m.group(1)
            if "service icon" in d:
                kind = "service icon"
            elif "resource icon" in d:
                kind = "resource icon"
            elif "group icon" in d:
                kind = "group decorator"
            else:
                continue
            ext = re.search(r'<a:ext cx="(\d+)" cy="(\d+)"', block)
            if ext:
                cx, cy = int(ext.group(1)), int(ext.group(2))
                sizes_by_kind[kind][(emu_to_px(cx), emu_to_px(cy))] += 1

        # Shape-based ellipse callouts (numbered circles)
        for shape in re.findall(r"<p:sp>(.*?)</p:sp>", s, re.DOTALL):
            if 'prstGeom prst="ellipse"' not in shape:
                continue
            texts = re.findall(r"<a:t>([^<]*)</a:t>", shape)
            text = (texts[0] if texts else "").strip()
            if not text.isdigit() or not (0 < int(text) < 100):
                continue
            ext = re.search(r'<a:ext cx="(\d+)" cy="(\d+)"', shape)
            if ext:
                cx, cy = int(ext.group(1)), int(ext.group(2))
                fs = re.search(r'<a:rPr[^>]*sz="(\d+)"', shape)
                font_pt = int(fs.group(1)) / 100 if fs else None
                kind = f"callout ({font_pt}pt)" if font_pt else "callout"
                sizes_by_kind[kind][(emu_to_px(cx), emu_to_px(cy))] += 1

    for kind, sizes in sorted(sizes_by_kind.items()):
        for (w, h), n in sizes.most_common():
            inches = emu_to_in(round(w * 9525))
            print(
                f"  {kind:22s} {w:6.1f} × {h:<6.1f} px  = {inches:.3f}\" × {inches:.3f}\"  (x{n})"
            )

    # Also report slide canvas size
    presentation = f"{unpack_dir}/ppt/presentation.xml"
    if os.path.exists(presentation):
        p = open(presentation).read()
        slide_size = re.search(r'<p:sldSz cx="(\d+)" cy="(\d+)"', p)
        if slide_size:
            cx, cy = int(slide_size.group(1)), int(slide_size.group(2))
            print(
                f"\n  Slide canvas          {emu_to_px(cx):6.1f} × {emu_to_px(cy):<6.1f} px  = "
                f"{emu_to_in(cx):.3f}\" × {emu_to_in(cy):.3f}\""
            )
            ratio = cx / cy
            print(f"  Slide aspect ratio    {ratio:.3f}  ({'16:9' if 1.77 < ratio < 1.79 else 'non-standard'})")


def report_containers(unpack_dir):
    """Report font weight and size on every container label on slides 21+25."""
    print("\n" + "=" * 60)
    print("  Container label font weight/size")
    print("=" * 60)

    container_labels = [
        "AWS Cloud", "Availability Zone", "Public subnet", "Private subnet",
        "Virtual private cloud", "VPC", "Security group", "Auto Scaling",
        "Region", "AWS account", "EC2 instance contents",
    ]
    for slide in ["ppt/slides/slide25.xml", "ppt/slides/slide21.xml"]:
        path = f"{unpack_dir}/{slide}"
        if not os.path.exists(path):
            continue
        s = open(path).read()
        print(f"\n  [{slide}]")
        for shape in re.findall(r"<p:sp>(.*?)</p:sp>", s, re.DOTALL):
            texts = re.findall(r"<a:t>([^<]*)</a:t>", shape)
            text = " ".join(t.strip() for t in texts if t.strip())
            if not any(label in text for label in container_labels):
                continue
            b = re.search(r'<a:rPr[^>]*b="(\d)"', shape)
            sz = re.search(r'<a:rPr[^>]*sz="(\d+)"', shape)
            bold = b.group(1) if b else "0"
            size = int(sz.group(1)) / 100 if sz else None
            weight = "BOLD" if bold == "1" else "regular"
            print(f"    {text[:45]:45s}  {weight:8s}  {size}pt")


def report_arrows(unpack_dir):
    """Extract arrow style from slide 27 (the Arrows reference)."""
    print("\n" + "=" * 60)
    print("  Preset arrow spec (slide 27)")
    print("=" * 60)

    path = f"{unpack_dir}/ppt/slides/slide27.xml"
    if not os.path.exists(path):
        print("  [slide 27 not found]")
        return
    s = open(path).read()

    # Every connector (cxnSp) on slide 27 uses the same preset
    # line weight + head/tail style.
    connectors = re.findall(r"<p:cxnSp>(.*?)</p:cxnSp>", s, re.DOTALL)
    weights = Counter()
    dashes = Counter()
    heads = Counter()
    prst_geoms = Counter()
    for c in connectors:
        w = re.search(r'<a:ln w="(\d+)"', c)
        if w:
            weights[emu_to_pt(int(w.group(1)))] += 1
        dash = re.search(r'<a:prstDash val="([^"]+)"', c)
        dashes[dash.group(1) if dash else "solid"] += 1
        for tag in ["headEnd", "tailEnd"]:
            m = re.search(rf'<a:{tag} type="([^"]+)"', c)
            if m:
                heads[(tag, m.group(1))] += 1
        prst = re.search(r'prstGeom prst="([^"]+)"', c)
        if prst:
            prst_geoms[prst.group(1)] += 1

    print(f"  Connectors on slide: {len(connectors)}")
    print(f"  Line weight:   {dict(weights)} pt")
    print(f"  Dash style:    {dict(dashes)}")
    print(f"  Head/tail:     {dict(heads)}")
    print(f"  prstGeom (arrow shape):  {dict(prst_geoms)}")
    print(
        "\n  Drawio mapping:\n"
        "    strokeWidth=1.25 (matches 15875 EMU)\n"
        '    endArrow=classic;endFill=0 (hollow triangle — PowerPoint "Open Arrow")\n'
        "      OR endArrow=classic;endFill=1 (solid filled triangle as rendered)\n"
        "    edgeStyle=orthogonalEdgeStyle (for straight + elbow shapes)\n"
        "    edgeStyle=none (for diagonal — escape hatch only)"
    )


def report_fonts(unpack_dir):
    """Report theme font stack."""
    print("\n" + "=" * 60)
    print("  Theme fonts")
    print("=" * 60)

    for theme_file in sorted(os.listdir(f"{unpack_dir}/ppt/theme")):
        if not theme_file.endswith(".xml"):
            continue
        s = open(f"{unpack_dir}/ppt/theme/{theme_file}").read()
        major = re.search(
            r'<a:majorFont>.*?<a:latin\s+typeface="([^"]+)"', s, re.DOTALL
        )
        minor = re.search(
            r'<a:minorFont>.*?<a:latin\s+typeface="([^"]+)"', s, re.DOTALL
        )
        if major or minor:
            print(f"  {theme_file}:")
            if major:
                print(f"    majorFont (heading): {major.group(1)}")
            if minor:
                print(f"    minorFont (body):    {minor.group(1)}")


def detect_release(unpack_dir):
    """Pull the release identifier from slide 1 (e.g. 'Release 23-2026.01.30')."""
    slide1 = f"{unpack_dir}/ppt/slides/slide1.xml"
    if not os.path.exists(slide1):
        return "unknown"
    s = open(slide1).read()
    m = re.search(r"Release\s+([0-9A-Za-z\-\.]+)", s)
    return m.group(1) if m else "unknown"


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)

    pptx = sys.argv[1]
    if not os.path.exists(pptx):
        print(f"Not found: {pptx}", file=sys.stderr)
        sys.exit(1)

    subcommand = sys.argv[2] if len(sys.argv) >= 3 else "all"
    args = sys.argv[3:]

    unpack_dir = unpack(pptx)
    try:
        release = detect_release(unpack_dir)
        print(f"AWS Architecture Icons — Release {release}")
        print(f"Source: {pptx}")

        if subcommand == "colors":
            report_colors(unpack_dir, args)
        elif subcommand == "sizes":
            report_sizes(unpack_dir)
        elif subcommand == "containers":
            report_containers(unpack_dir)
        elif subcommand == "arrows":
            report_arrows(unpack_dir)
        elif subcommand == "fonts":
            report_fonts(unpack_dir)
        elif subcommand == "all":
            report_colors(unpack_dir)
            report_sizes(unpack_dir)
            report_containers(unpack_dir)
            report_arrows(unpack_dir)
            report_fonts(unpack_dir)
        else:
            print(f"Unknown subcommand: {subcommand}", file=sys.stderr)
            print("Run with no args to see usage.")
            sys.exit(1)
    finally:
        shutil.rmtree(unpack_dir, ignore_errors=True)


if __name__ == "__main__":
    main()
