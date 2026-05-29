#!/usr/bin/env python3
"""
draw.io Diagram Validator
Checks XML correctness AND layout anti-patterns.
Usage: python3 validate_drawio.py <file.drawio>
"""
import xml.etree.ElementTree as ET
import re
import sys
from collections import defaultdict

PASS = "\033[92mPASS\033[0m"
FAIL = "\033[91mFAIL\033[0m"
WARN = "\033[93mWARN\033[0m"

fails = 0
warns = 0


def fail(msg):
    global fails
    fails += 1
    print(f"  [{FAIL}] {msg}")


def warn(msg):
    global warns
    warns += 1
    print(f"  [{WARN}] {msg}")


def ok(msg):
    print(f"  [{PASS}] {msg}")


def parse_style(style_str):
    """Parse a draw.io style string into a dict."""
    if not style_str:
        return {}
    result = {}
    for part in style_str.split(";"):
        if "=" in part:
            k, v = part.split("=", 1)
            result[k.strip()] = v.strip()
        elif part.strip():
            result[part.strip()] = True
    return result


def get_geometry(cell):
    """Extract x, y, width, height from mxGeometry child."""
    geo = cell.find("mxGeometry")
    if geo is None:
        return None
    return {
        "x": float(geo.get("x", 0)),
        "y": float(geo.get("y", 0)),
        "width": float(geo.get("width", 0)),
        "height": float(geo.get("height", 0)),
    }


def main():
    global fails, warns

    if len(sys.argv) < 2:
        print("Usage: python3 validate_drawio.py <file.drawio>")
        sys.exit(1)

    filepath = sys.argv[1]
    print(f"\n{'='*60}")
    print(f"  Validating: {filepath}")
    print(f"{'='*60}")

    # --- Parse XML ---
    try:
        tree = ET.parse(filepath)
    except ET.ParseError as e:
        fail(f"XML parse error: {e}")
        sys.exit(1)

    root = tree.getroot()
    model = root.find(".//mxGraphModel")
    if model is None:
        fail("No mxGraphModel found")
        sys.exit(1)

    cells = model.findall(".//mxCell")

    # Read raw content for comment check
    with open(filepath) as f:
        raw = f.read()

    # =========================================================
    print("\n--- XML Correctness ---")
    # =========================================================

    # 1. Structural cells
    has_0 = any(c.get("id") == "0" for c in cells)
    has_1 = any(c.get("id") == "1" and c.get("parent") == "0" for c in cells)
    if has_0 and has_1:
        ok("Structural cells id=0 and id=1 present")
    else:
        fail(f"Missing structural cells (id=0: {has_0}, id=1 parent=0: {has_1})")

    # 2. Duplicate IDs
    ids = [c.get("id") for c in cells if c.get("id")]
    seen = set()
    dupes = set()
    for i in ids:
        if i in seen:
            dupes.add(i)
        seen.add(i)
    if dupes:
        fail(f"Duplicate IDs: {dupes}")
    else:
        ok(f"All {len(ids)} IDs are unique")

    # 3. Background and page
    bg = model.get("background")
    page = model.get("page")
    if bg == "#FFFFFF" and page == "1":
        ok("White background and page=1 set")
    else:
        fail(f"background={bg} (need #FFFFFF), page={page} (need 1)")

    # 4. XML comments
    comments = re.findall(r"<!--.*?-->", raw, re.DOTALL)
    if comments:
        fail(f"{len(comments)} XML comments found — remove all <!-- --> blocks")
    else:
        ok("No XML comments")

    # 5. Edge checks
    edges = [c for c in cells if c.get("edge") == "1"]
    vertices = [c for c in cells if c.get("vertex") == "1"]
    print(f"\n--- Edge Checks ({len(edges)} edges) ---")

    edge_issues = 0
    for e in edges:
        eid = e.get("id", "?")
        style = parse_style(e.get("style", ""))

        if e.get("parent") != "1":
            fail(f"Edge '{eid}' has parent={e.get('parent')} (must be '1')")
            edge_issues += 1

        if e.find("mxGeometry") is None:
            fail(f"Edge '{eid}' missing <mxGeometry> child element")
            edge_issues += 1

        if "edgeStyle" not in style:
            fail(f"Edge '{eid}' missing edgeStyle (need orthogonalEdgeStyle)")
            edge_issues += 1

        if "html" not in style:
            warn(f"Edge '{eid}' missing html=1 in style")

        # Corners at bends must be sharp (miter join). The PPTX uses <a:miter>
        # on every connector, and drawio's default for orthogonalEdgeStyle is
        # rounded corners unless rounded=0 is explicitly set.
        if style.get("rounded") != "0":
            warn(
                f"Edge '{eid}' missing rounded=0 — L-bends will render with rounded "
                f"corners instead of sharp corners. The 2026 PPTX preset uses miter "
                f"joins (sharp corners)."
            )

    if edge_issues == 0:
        ok("All edges have parent=1, mxGeometry, and edgeStyle")

    # 6. Vertex checks
    print(f"\n--- Vertex Checks ({len(vertices)} vertices) ---")

    vertex_issues = 0
    for v in vertices:
        vid = v.get("id", "?")
        style_str = v.get("style", "")
        style = parse_style(style_str)

        if style_str and "html=1" not in style_str and "html" not in style:
            fail(f"Vertex '{vid}' missing html=1 in style")
            vertex_issues += 1

    if vertex_issues == 0:
        ok("All vertices include html=1")

    # 7. Grid alignment
    print("\n--- Grid Alignment ---")
    off_grid = []
    # Callout sizes (16, 24) are inherently off-grid — exempt width/height for small circles
    CALLOUT_SIZES = {16, 24}
    MONITORING_SIZES = {48}  # 48×48 monitoring icons are allowed
    for c in cells:
        geo = c.find("mxGeometry")
        if geo is None:
            continue
        if geo.get("relative") == "1":
            continue  # edges use relative geometry
        w = geo.get("width")
        h = geo.get("height")
        is_callout = (
            w is not None
            and h is not None
            and float(w) in CALLOUT_SIZES
            and float(h) in CALLOUT_SIZES
        )
        is_monitoring = (
            w is not None
            and h is not None
            and float(w) in MONITORING_SIZES
            and float(h) in MONITORING_SIZES
        )
        for attr in ["x", "y", "width", "height"]:
            if (is_callout or is_monitoring) and attr in ("width", "height"):
                continue  # exempt callout/monitoring icon dimensions
            val = geo.get(attr)
            if val is not None:
                try:
                    fval = float(val)
                    if fval % 10 != 0:
                        off_grid.append(
                            f"{c.get('id', '?')}.{attr}={val}"
                        )
                except ValueError:
                    pass

    if off_grid:
        fail(f"{len(off_grid)} off-grid coordinates (must be multiples of 10):")
        for item in off_grid[:10]:
            print(f"      → {item}")
        if len(off_grid) > 10:
            print(f"      ... and {len(off_grid)-10} more")
    else:
        ok("All coordinates are grid-aligned (multiples of 10)")

    # 8. Line break check
    bad_newlines = []
    for c in cells:
        val = c.get("value", "")
        if "\\n" in val:
            bad_newlines.append(c.get("id", "?"))
    if bad_newlines:
        fail(f"Literal \\n in labels (use &#xa; instead): {bad_newlines}")
    else:
        ok("No literal \\n in labels")


    # =========================================================
    print("\n--- Layout Anti-Pattern Detection ---")
    # =========================================================

    # Build lookup maps
    id_to_cell = {c.get("id"): c for c in cells if c.get("id")}
    id_to_geo = {}
    for c in cells:
        cid = c.get("id")
        geo = get_geometry(c)
        if cid and geo:
            id_to_geo[cid] = geo

    # --- Anti-Pattern 1: Fan-out from single source ---
    # Count how many edges originate from each source
    source_targets = defaultdict(list)
    for e in edges:
        src = e.get("source")
        tgt = e.get("target")
        if src and tgt:
            source_targets[src].append(tgt)

    print("\n  Fan-out analysis:")
    for src, targets in source_targets.items():
        if len(targets) >= 4:
            src_geo = id_to_geo.get(src)
            if not src_geo:
                continue

            # Check if all targets are on the same row (same Y)
            target_geos = [id_to_geo.get(t) for t in targets if t in id_to_geo]
            if not target_geos:
                continue

            # Check if source and targets share the same Y (horizontal chain OK)
            src_y = src_geo["y"]
            same_row = all(abs(tg["y"] - src_y) < 20 for tg in target_geos)

            if same_row:
                # Check if edges go source→adjacent or source→distant
                # Sort targets by X
                sorted_targets = sorted(
                    [(t, id_to_geo[t]) for t in targets if t in id_to_geo],
                    key=lambda x: x[1]["x"],
                )
                src_x = src_geo["x"]

                # Check if any target is non-adjacent (another target sits between them)
                for i, (tid, tgeo) in enumerate(sorted_targets):
                    between_count = sum(
                        1
                        for _, og in sorted_targets
                        if og["x"] > src_x and og["x"] < tgeo["x"]
                    )
                    if between_count > 0:
                        style = parse_style(
                            next(
                                (
                                    e2.get("style", "")
                                    for e2 in edges
                                    if e2.get("source") == src
                                    and e2.get("target") == tid
                                ),
                                "",
                            )
                        )
                        # Check if edge has waypoints
                        edge_cell = next(
                            (
                                e2
                                for e2 in edges
                                if e2.get("source") == src
                                and e2.get("target") == tid
                            ),
                            None,
                        )
                        has_waypoints = (
                            edge_cell is not None
                            and edge_cell.find(".//Array") is not None
                        )
                        if not has_waypoints:
                            fail(
                                f"Fan-out: '{src}' connects directly to non-adjacent '{tid}' "
                                f"({between_count} icons between them on same row). "
                                f"Use chain pattern (A→B→C) instead of A→C skipping B."
                            )
            else:
                warn(
                    f"'{src}' fans out to {len(targets)} targets — verify edges don't cross icons"
                )

    # --- Anti-Pattern 2: Callouts in margin column ---
    print("\n  Callout placement analysis:")
    callouts = []
    non_callout_vertices = []
    for v in vertices:
        style = parse_style(v.get("style", ""))
        geo = id_to_geo.get(v.get("id"))
        if not geo:
            continue
        val = v.get("value", "")
        if (
            style.get("ellipse") is True
            and val.isdigit()
            and geo.get("width", 0) <= 24
        ):
            callouts.append((v.get("id"), geo, int(val)))
        elif v.get("id") not in ("0", "1"):
            non_callout_vertices.append((v.get("id"), geo))

    if callouts:
        # Check if callouts are all at similar X (margin column pattern)
        callout_xs = [g["x"] for _, g, _ in callouts]
        if len(callout_xs) >= 3:
            x_spread = max(callout_xs) - min(callout_xs)
            avg_x = sum(callout_xs) / len(callout_xs)

            # Get average X of non-callout icons
            icon_xs = [
                g["x"]
                for _, g in non_callout_vertices
                if g.get("width", 0) >= 48
            ]
            if icon_xs:
                avg_icon_x = sum(icon_xs) / len(icon_xs)

                if x_spread < 60 and avg_x < avg_icon_x - 200:
                    fail(
                        f"Callouts appear stacked in a margin column "
                        f"(avg callout X={avg_x:.0f}, avg icon X={avg_icon_x:.0f}). "
                        f"Place each callout adjacent to the icon it annotates."
                    )
                else:
                    ok("Callouts are distributed near their annotated icons")
        else:
            ok(f"{len(callouts)} callouts found (too few to check column pattern)")
    else:
        ok("No callouts to check")

    # --- Anti-Pattern 2b: Callout spacing / text-box overlap ---
    # Flag callouts whose text boxes visually collide (content overflow or bbox overlap).
    print("\n  Callout spacing (text-box overlap):")

    cb = []
    for v in vertices:
        style = parse_style(v.get("style", ""))
        geo = id_to_geo.get(v.get("id"))
        if not geo:
            continue
        val = (v.get("value", "") or "").strip()
        digit_only = val.rstrip(".").strip()
        if (
            style.get("ellipse") is True
            and digit_only.isdigit()
            and geo.get("width", 0) <= 28
        ):
            cb.append((v.get("id"), geo, digit_only))

    text_labels = []
    for v in vertices:
        style_str = v.get("style", "") or ""
        geo = id_to_geo.get(v.get("id"))
        if not geo:
            continue
        val = (v.get("value", "") or "").strip()
        if not val:
            continue
        if not style_str.lstrip().startswith("text;"):
            continue
        style = parse_style(style_str)
        text_labels.append((v.get("id"), geo, val, style))

    # Pair each callout bubble with its nearest text label to the right.
    callout_rects = []
    for cid, cgeo, num in cb:
        candidates = []
        for tid, tgeo, tval, tstyle in text_labels:
            if abs(tgeo["y"] - cgeo["y"]) <= 4 and tgeo["x"] >= cgeo["x"] + cgeo["width"] - 2:
                gap = tgeo["x"] - (cgeo["x"] + cgeo["width"])
                candidates.append((gap, tid, tgeo, tval, tstyle))
        if not candidates:
            continue
        candidates.sort()
        _, tid, tgeo, tval, tstyle = candidates[0]
        try:
            fs = int(tstyle.get("fontSize", "11") or "11")
        except ValueError:
            fs = 11
        callout_rects.append({
            "id": f"{cid}+{tid}", "num": num,
            "x": cgeo["x"], "y": cgeo["y"],
            "width": (tgeo["x"] + tgeo["width"]) - cgeo["x"],
            "height": max(cgeo["height"], tgeo["height"]),
            "text": tval, "text_x": tgeo["x"],
            "text_width": tgeo["width"], "font_size": fs,
        })

    # Arial at fs=N is ~0.55*N wide per char; use 0.50 to reduce false positives.
    overflow = []
    for cr in callout_rects:
        est_text_px = len(cr["text"]) * cr["font_size"] * 0.50
        if est_text_px > cr["text_width"] + 2:
            overflow.append(
                f"Callout {cr['num']}: text ~{est_text_px:.0f}px wide but box "
                f"is only {cr['text_width']:.0f}px — widen the text cell or "
                f"shorten the copy."
            )

    collisions = []
    for i in range(len(callout_rects)):
        for j in range(i + 1, len(callout_rects)):
            a = callout_rects[i]
            b = callout_rects[j]
            a_right = max(a["x"] + a["width"], a["text_x"] + len(a["text"]) * a["font_size"] * 0.50)
            b_right = max(b["x"] + b["width"], b["text_x"] + len(b["text"]) * b["font_size"] * 0.50)
            x_overlap = a["x"] < b_right and b["x"] < a_right
            y_overlap = a["y"] < b["y"] + b["height"] and b["y"] < a["y"] + a["height"]
            if x_overlap and y_overlap:
                collisions.append(
                    f"Callouts {a['num']} and {b['num']} overlap — move one "
                    f"row down, widen the column, or shorten the text."
                )

    issues = overflow + collisions
    if issues:
        fail(f"{len(issues)} callout spacing problems:")
        for issue in issues[:12]:
            print(f"      → {issue}")
    else:
        ok(f"Callout spacing clean ({len(callout_rects)} annotated callouts checked)")

    # --- Anti-Pattern 3: Vertical alignment of parent→child ---
    print("\n  Vertical column alignment:")
    misaligned = []
    for e in edges:
        src = e.get("source")
        tgt = e.get("target")
        style = parse_style(e.get("style", ""))

        if not src or not tgt:
            continue
        src_geo = id_to_geo.get(src)
        tgt_geo = id_to_geo.get(tgt)
        if not src_geo or not tgt_geo:
            continue

        # Check if this is a vertical connection (exitY=1, entryY=0)
        exit_y = style.get("exitY")
        entry_y = style.get("entryY")

        if exit_y == "1" and entry_y == "0":
            # This is a top-to-bottom connection — X should match
            src_center_x = src_geo["x"] + src_geo["width"] / 2
            tgt_center_x = tgt_geo["x"] + tgt_geo["width"] / 2
            x_diff = abs(src_center_x - tgt_center_x)

            if x_diff > 30:
                misaligned.append(
                    f"'{src}' (x={src_geo['x']:.0f}) → '{tgt}' (x={tgt_geo['x']:.0f}), "
                    f"center offset={x_diff:.0f}px"
                )

    if misaligned:
        for m in misaligned:
            warn(f"Vertical edge with X misalignment: {m}")
    else:
        ok("All vertical edges have aligned X centers")

    # --- Anti-Pattern 4: Overlapping elements ---
    print("\n  Overlap detection:")
    overlap_count = 0

    # Identify group/container cells — these intentionally contain children
    group_ids = set()
    for v in vertices:
        style_str = v.get("style", "")
        style = parse_style(style_str)
        if style.get("container") in ("0", "1"):
            group_ids.add(v.get("id"))
        if "swimlane" in style_str:
            group_ids.add(v.get("id"))
        # Also detect dashed boundary groups (rounded=1, fillColor=none, dashed=1)
        if (
            style.get("fillColor") == "none"
            and style.get("dashed") == "1"
            and v.get("id") in id_to_geo
            and id_to_geo[v.get("id")].get("width", 0) > 200
        ):
            group_ids.add(v.get("id"))
        # Detect large rectangles used as visual groups (width > 300, no resIcon)
        # Exclude text-only elements (labels, titles, subtitles)
        is_text_only = style_str.startswith("text;") or style.get("text") is True
        if (
            v.get("id") in id_to_geo
            and id_to_geo[v.get("id")].get("width", 0) > 300
            and "resIcon" not in style_str
            and "shape=mxgraph" not in style_str
            and not is_text_only
        ):
            group_ids.add(v.get("id"))

    icon_cells = [
        (v.get("id"), id_to_geo[v.get("id")])
        for v in vertices
        if v.get("id") in id_to_geo
        and id_to_geo[v.get("id")].get("width", 0) >= 20
        and v.get("id") not in ("0", "1")
        and v.get("parent") not in group_ids  # skip children inside containers (relative coords)
    ]

    # Identify callout IDs for gap enforcement
    callout_ids = {cid for cid, _, _ in callouts}
    # Minimum gap: callouts need clearance from icons to avoid visual collision
    CALLOUT_GAP = 10

    for i in range(len(icon_cells)):
        id_a, geo_a = icon_cells[i]
        ax1 = geo_a["x"]
        ay1 = geo_a["y"]
        ax2 = ax1 + geo_a["width"]
        ay2 = ay1 + geo_a["height"]

        for j in range(i + 1, len(icon_cells)):
            id_b, geo_b = icon_cells[j]

            # Skip if one is a group container — children inside groups is expected
            if id_a in group_ids or id_b in group_ids:
                continue

            bx1 = geo_b["x"]
            by1 = geo_b["y"]
            bx2 = bx1 + geo_b["width"]
            by2 = by1 + geo_b["height"]

            # Apply gap when a callout is involved
            gap = CALLOUT_GAP if (id_a in callout_ids or id_b in callout_ids) else 0

            # Check AABB overlap (with gap for callouts)
            if ax1 - gap < bx2 and ax2 + gap > bx1 and ay1 - gap < by2 and ay2 + gap > by1:
                fail(
                    f"Overlapping elements: '{id_a}' and '{id_b}' "
                    f"(A: {ax1:.0f},{ay1:.0f}-{ax2:.0f},{ay2:.0f} "
                    f"B: {bx1:.0f},{by1:.0f}-{bx2:.0f},{by2:.0f})"
                )
                overlap_count += 1

    if overlap_count == 0:
        ok("No overlapping elements detected")

    # --- Anti-Pattern 5: container=1 on groups ---
    print("\n  Container check:")
    bad_containers = []
    for v in vertices:
        style = parse_style(v.get("style", ""))
        if style.get("container") == "1":
            bad_containers.append(v.get("id", "?"))
    if bad_containers:
        warn(
            f"container=1 found on: {bad_containers}. "
            f"Use container=0 to avoid coordinate nesting."
        )
    else:
        ok("No container=1 groups (using container=0 correctly)")

    # --- Anti-Pattern 6: Arrow straightness ---
    # L-shape (one waypoint) OK. Flag 2+ waypoints (S/Z-bends), implicit Z-bends
    # (no waypoints but misaligned exit/entry), or diagonal segments.
    print("\n  Arrow straightness:")
    bent_edges = []
    crooked_edges = []
    for e in edges:
        eid = e.get("id", "?")
        arr = e.find(".//Array")
        if arr is not None and len(arr) > 2:
            bent_edges.append(eid)
            continue

        # Check for implicit Z-bends (no waypoints but misaligned same-axis exit/entry)
        src = e.get("source")
        tgt = e.get("target")
        style = parse_style(e.get("style", ""))
        if not src or not tgt:
            continue
        src_geo = id_to_geo.get(src)
        tgt_geo = id_to_geo.get(tgt)
        if not src_geo or not tgt_geo:
            continue

        ex = float(style.get("exitX", "1"))
        ey = float(style.get("exitY", "0.5"))
        nx = float(style.get("entryX", "0"))
        ny = float(style.get("entryY", "0.5"))

        sx = src_geo["x"] + src_geo["width"] * ex
        sy = src_geo["y"] + src_geo["height"] * ey
        tx = tgt_geo["x"] + tgt_geo["width"] * nx
        ty = tgt_geo["y"] + tgt_geo["height"] * ny

        # Vertical edge (exit top/bottom, enter top/bottom) but X misaligned
        exit_vertical = ey in (0, 1) or (ex == 0.5 and ey in (0, 1))
        entry_vertical = ny in (0, 1) or (nx == 0.5 and ny in (0, 1))
        if exit_vertical and entry_vertical and abs(sx - tx) > 3 and abs(sx - tx) < 60:
            bent_edges.append(f"{eid} (implicit Z-bend: exit x={sx:.0f}, entry x={tx:.0f}, Δ={abs(sx-tx):.0f}px)")
            continue

        # Horizontal edge (exit left/right, enter left/right) but Y misaligned
        exit_horizontal = ex in (0, 1) or (ey == 0.5 and ex in (0, 1))
        entry_horizontal = nx in (0, 1) or (ny == 0.5 and nx in (0, 1))
        if exit_horizontal and entry_horizontal and abs(sy - ty) > 3 and abs(sy - ty) < 60:
            bent_edges.append(f"{eid} (implicit Z-bend: exit y={sy:.0f}, entry y={ty:.0f}, Δ={abs(sy-ty):.0f}px)")
            continue

        # --- Crooked/diagonal segment detection ---
        # Build the full path of the edge and check every segment is axis-aligned.
        # SKIP edges with orthogonalEdgeStyle and no waypoints — the router creates
        # proper L-shaped segments automatically; the exit→entry line is NOT the actual path.
        has_orthogonal = style.get("edgeStyle") == "orthogonalEdgeStyle"
        has_waypoints = arr is not None and len(arr) > 0
        if has_orthogonal and not has_waypoints:
            pass  # orthogonal router handles L-shapes — not diagonal
        else:
            points = [(sx, sy)]
            if arr is not None:
                for pt in arr:
                    points.append((float(pt.get("x", 0)), float(pt.get("y", 0))))
            points.append((tx, ty))

            for k in range(len(points) - 1):
                px1, py1 = points[k]
                px2, py2 = points[k + 1]
                dx = abs(px1 - px2)
                dy = abs(py1 - py2)
                # A segment is crooked if it has significant movement on BOTH axes
                # (i.e., it's diagonal rather than purely horizontal or vertical)
                if dx > 3 and dy > 3:
                    crooked_edges.append(
                        f"{eid} segment {k+1}: ({px1:.0f},{py1:.0f})→({px2:.0f},{py2:.0f}) "
                        f"is diagonal (Δx={dx:.0f}, Δy={dy:.0f}). "
                        f"Align source/target so each segment is purely horizontal or vertical."
                    )
                    break  # one violation per edge is enough

    if bent_edges:
        fail(
            f"{len(bent_edges)} edges have S/Z-bends:"
        )
        for b in bent_edges[:8]:
            print(f"      → {b}")
    else:
        ok("All edges are straight or L-shaped (no S/Z-bends)")

    if crooked_edges:
        fail(
            f"{len(crooked_edges)} edges have crooked/diagonal segments "
            f"(every segment must be purely horizontal or vertical):"
        )
        for c in crooked_edges[:8]:
            print(f"      → {c}")
    else:
        ok("All edge segments are axis-aligned (no diagonal/crooked arrows)")

    # --- Anti-Pattern 7: Non-axis-aligned connections ---
    # Edges without explicit exit/entry must share X/Y centers for straight
    # routing. With explicit exit/entry, computed endpoints must be axis-aligned.
    print("\n  Axis alignment:")
    misaligned_edges = []
    for e in edges:
        eid = e.get("id", "?")
        src = e.get("source")
        tgt = e.get("target")
        if not src or not tgt:
            continue
        src_geo = id_to_geo.get(src)
        tgt_geo = id_to_geo.get(tgt)
        if not src_geo or not tgt_geo:
            continue
        # Skip edges to/from groups (group-to-group connections are abstract)
        if src in group_ids or tgt in group_ids:
            continue
        style = parse_style(e.get("style", ""))

        if style.get("exitX") and style.get("entryX"):
            # Edge has explicit exit/entry points — check that the computed
            # coordinates produce axis-aligned segments (not diagonal).
            # Skip edges with waypoints — they define their own path.
            if e.find(".//Array") is not None:
                continue
            ex = float(style.get("exitX", "1"))
            ey = float(style.get("exitY", "0.5"))
            nx = float(style.get("entryX", "0"))
            ny = float(style.get("entryY", "0.5"))
            sx = src_geo["x"] + src_geo["width"] * ex
            sy = src_geo["y"] + src_geo["height"] * ey
            tx = tgt_geo["x"] + tgt_geo["width"] * nx
            ty = tgt_geo["y"] + tgt_geo["height"] * ny
            x_diff = abs(sx - tx)
            y_diff = abs(sy - ty)
            # For a straight connection (no waypoints, no L-shape), exit and
            # entry must share X or Y within tolerance.
            # For an L-shape, the orthogonal router handles it — but if both
            # exit and entry are on the same axis (both horizontal or both
            # vertical), they MUST align to avoid a crooked segment.
            exit_is_side = ex in (0, 1) and ey not in (0, 1)
            entry_is_side = nx in (0, 1) and ny not in (0, 1)
            exit_is_tb = ey in (0, 1) and ex not in (0, 1)
            entry_is_tb = ny in (0, 1) and nx not in (0, 1)
            # Both exit from sides (horizontal connection) — Y must match
            if exit_is_side and entry_is_side and y_diff > 5:
                misaligned_edges.append(
                    f"'{eid}': {src}→{tgt} exits/enters sides but Y misaligned "
                    f"(exit y={sy:.0f}, entry y={ty:.0f}, Δy={y_diff:.0f}px). "
                    f"Align icons vertically or adjust exit/entry Y."
                )
            # Both exit from top/bottom (vertical connection) — X must match
            elif exit_is_tb and entry_is_tb and x_diff > 5:
                misaligned_edges.append(
                    f"'{eid}': {src}→{tgt} exits/enters top/bottom but X misaligned "
                    f"(exit x={sx:.0f}, entry x={tx:.0f}, Δx={x_diff:.0f}px). "
                    f"Align icons horizontally or adjust exit/entry X."
                )
        else:
            # No explicit exit/entry — check icon center alignment
            # Skip edges with waypoints — they are intentional L-shapes
            if e.find(".//Array") is not None:
                continue
            src_cx = src_geo["x"] + src_geo["width"] / 2
            src_cy = src_geo["y"] + src_geo["height"] / 2
            tgt_cx = tgt_geo["x"] + tgt_geo["width"] / 2
            tgt_cy = tgt_geo["y"] + tgt_geo["height"] / 2
            x_diff = abs(src_cx - tgt_cx)
            y_diff = abs(src_cy - tgt_cy)
            # Must share X center (vertical) or Y center (horizontal) within 5px
            if x_diff > 5 and y_diff > 5:
                misaligned_edges.append(
                    f"'{eid}': {src}→{tgt} (Δx={x_diff:.0f}, Δy={y_diff:.0f})"
                )
    if misaligned_edges:
        warn(
            f"{len(misaligned_edges)} edges connect non-axis-aligned icons "
            f"(should share X or Y center for straight arrows):"
        )
        for m in misaligned_edges[:8]:
            print(f"      → {m}")
    else:
        ok("All icon-to-icon edges are axis-aligned")

    # --- Anti-Pattern 8: Container padding ---
    print("\n  Container padding:")
    tight_containers = []
    # Identify legend containers — text items inside legends are intentionally tight
    legend_ids = set()
    for v in vertices:
        val = (v.get("value") or "").lower()
        vid = v.get("id", "")
        if "legend" in vid.lower() or "legend" in val:
            legend_ids.add(vid)
    for gid in group_ids:
        if gid in legend_ids:
            continue  # skip legend boxes — text items inside are intentionally tight
        g_geo = id_to_geo.get(gid)
        if not g_geo:
            continue
        gx1 = g_geo["x"]
        gy1 = g_geo["y"]
        gx2 = gx1 + g_geo["width"]
        gy2 = gy1 + g_geo["height"]
        for v in vertices:
            vid = v.get("id")
            if vid in group_ids or vid in ("0", "1"):
                continue
            v_geo = id_to_geo.get(vid)
            if not v_geo or v_geo.get("width", 0) < 48:
                continue
            vx1 = v_geo["x"]
            vy1 = v_geo["y"]
            vx2 = vx1 + v_geo["width"]
            vy2 = vy1 + v_geo["height"]
            # Check if icon is inside this group
            if vx1 >= gx1 and vy1 >= gy1 and vx2 <= gx2 and vy2 <= gy2:
                left_pad = vx1 - gx1
                top_pad = vy1 - gy1
                right_pad = gx2 - vx2
                bottom_pad = gy2 - vy2
                min_pad = min(left_pad, top_pad, right_pad, bottom_pad)
                if min_pad < 30:
                    tight_containers.append(
                        f"'{vid}' in '{gid}': min padding={min_pad:.0f}px (need ≥30)"
                    )
    if tight_containers:
        warn(f"{len(tight_containers)} icons too close to container edge:")
        for t in tight_containers[:5]:
            print(f"      → {t}")
    else:
        ok("All containers have adequate padding")

    # --- Anti-Pattern 9: Bare service labels ---
    print("\n  Label quality:")
    BARE_NAMES = {
        "lambda", "s3", "ec2", "dynamodb", "aurora", "rds", "sqs", "sns",
        "cloudfront", "api gateway", "ecs", "eks", "fargate", "elasticache",
        "cognito", "waf", "cloudwatch", "eventbridge", "kinesis", "redshift",
        "step functions", "glue", "athena", "opensearch", "elasticsearch",
    }
    bare_labels = []
    for v in vertices:
        val = (v.get("value") or "").strip().lower()
        style_str = v.get("style", "")
        if "resIcon" not in style_str and "shape=mxgraph.aws4" not in style_str:
            continue  # only check AWS service icons
        # Normalize: strip "aws " and "amazon " prefixes
        clean = val.replace("&#xa;", " ").replace("<br>", " ").strip()
        clean_lower = clean.lower().replace("aws ", "").replace("amazon ", "").strip()
        if clean_lower in BARE_NAMES:
            bare_labels.append(f"'{v.get('id', '?')}' = \"{clean}\"")
    if bare_labels:
        warn(
            f"{len(bare_labels)} icons have bare service names (add descriptive role):"
        )
        for b in bare_labels[:5]:
            print(f"      → {b}")
    else:
        ok("All AWS icons have descriptive labels")

    # --- Anti-Pattern 10: Icon size enforcement ---
    print("\n  Icon sizes:")
    VALID_SIZES = {60, 48}
    bad_sizes = []
    for v in vertices:
        style_str = v.get("style", "")
        if "resIcon" not in style_str and "shape=mxgraph.aws4" not in style_str:
            continue
        # Skip group containers — they use shape=mxgraph.aws4.group and are large by design
        if "group" in style_str or v.get("id") in group_ids:
            continue
        geo = id_to_geo.get(v.get("id"))
        if not geo:
            continue
        w, h = geo["width"], geo["height"]
        if w not in VALID_SIZES or h not in VALID_SIZES:
            bad_sizes.append(
                f"'{v.get('id', '?')}': {w:.0f}×{h:.0f} (must be 60×60 or 48×48)"
            )
    if bad_sizes:
        fail(f"{len(bad_sizes)} icons have non-standard sizes:")
        for b in bad_sizes:
            print(f"      → {b}")
    else:
        ok("All AWS icons are standard size (60×60 or 48×48)")

    # --- Anti-Pattern 11: Legend presence ---
    print("\n  Legend check:")
    # Collect distinct edge style signatures
    edge_styles = set()
    for e in edges:
        style = parse_style(e.get("style", ""))
        sig = (
            style.get("strokeWidth", "1"),
            style.get("dashed", "0"),
            style.get("strokeColor", "#232F3E"),
        )
        edge_styles.add(sig)
    has_legend = any(
        "legend" in (v.get("id") or "").lower()
        or "legend" in (v.get("value") or "").lower()
        for v in vertices
    )
    if len(edge_styles) > 1 and not has_legend:
        warn(
            f"{len(edge_styles)} distinct arrow styles used but no legend found. "
            f"Add a legend explaining each arrow type."
        )
    elif len(edge_styles) > 1 and has_legend:
        ok(f"Legend present for {len(edge_styles)} arrow styles")
    else:
        ok("Single arrow style — no legend needed")

    # --- Anti-Pattern 12: Edge padding (spacing between connected icons) ---
    print("\n  Edge padding:")
    MIN_EDGE_GAP = 60  # minimum gap in pixels between connected icons
    tight_edges = []
    for e in edges:
        eid = e.get("id", "?")
        src = e.get("source")
        tgt = e.get("target")
        if not src or not tgt:
            continue
        src_geo = id_to_geo.get(src)
        tgt_geo = id_to_geo.get(tgt)
        if not src_geo or not tgt_geo:
            continue
        # Skip edges to/from groups
        if src in group_ids or tgt in group_ids:
            continue

        # Calculate the gap between the two icons' bounding boxes
        sx1 = src_geo["x"]
        sy1 = src_geo["y"]
        sx2 = sx1 + src_geo["width"]
        sy2 = sy1 + src_geo["height"]
        tx1 = tgt_geo["x"]
        ty1 = tgt_geo["y"]
        tx2 = tx1 + tgt_geo["width"]
        ty2 = ty1 + tgt_geo["height"]

        # Horizontal gap (if icons are side by side)
        if sy1 < ty2 and sy2 > ty1:  # Y ranges overlap — horizontal neighbors
            h_gap = max(tx1 - sx2, sx1 - tx2)
            if 0 < h_gap < MIN_EDGE_GAP:
                tight_edges.append(
                    f"'{eid}': {src}→{tgt} horizontal gap={h_gap:.0f}px (need ≥{MIN_EDGE_GAP})"
                )

        # Vertical gap (if icons are above/below)
        if sx1 < tx2 and sx2 > tx1:  # X ranges overlap — vertical neighbors
            v_gap = max(ty1 - sy2, sy1 - ty2)
            if 0 < v_gap < MIN_EDGE_GAP:
                tight_edges.append(
                    f"'{eid}': {src}→{tgt} vertical gap={v_gap:.0f}px (need ≥{MIN_EDGE_GAP})"
                )

    if tight_edges:
        warn(f"{len(tight_edges)} edges have insufficient spacing between icons:")
        for t in tight_edges[:8]:
            print(f"      → {t}")
    else:
        ok(f"All connected icons have ≥{MIN_EDGE_GAP}px spacing")

    # --- Anti-Pattern 13: Arrows blocking labels ---
    # Vertical edge exiting/entering a side with a label below cuts through text.
    print("\n  Arrow-label conflicts:")
    label_conflicts = []
    LABEL_HEIGHT = 30

    for e in edges:
        eid = e.get("id", "?")
        src = e.get("source")
        tgt = e.get("target")
        style = parse_style(e.get("style", ""))
        if not src or not tgt:
            continue
        if src in group_ids or tgt in group_ids:
            continue
        src_cell = id_to_cell.get(src)
        tgt_cell = id_to_cell.get(tgt)
        src_geo = id_to_geo.get(src)
        tgt_geo = id_to_geo.get(tgt)
        if src_cell is None or tgt_cell is None or not src_geo or not tgt_geo:
            continue

        src_style = parse_style(src_cell.get("style", ""))
        tgt_style = parse_style(tgt_cell.get("style", ""))

        exit_y = style.get("exitY")
        entry_y = style.get("entryY")
        exit_x = style.get("exitX")
        entry_x = style.get("entryX")

        # Case 1: Vertical edge going DOWN from source — check if source has label below
        if exit_y == "1" and src_style.get("verticalLabelPosition") == "bottom":
            # The arrow exits the bottom of the icon and passes through the label zone
            label_conflicts.append(
                f"'{eid}': arrow exits bottom of '{src}' which has label below — "
                f"arrow crosses through label text. Move label to top or reroute."
            )

        # Case 2: Vertical edge going UP into target — check if target has label above
        if entry_y == "0" and tgt_style.get("verticalLabelPosition") == "top":
            # The arrow enters the top of the icon and passes through the label zone above
            label_conflicts.append(
                f"'{eid}': arrow enters top of '{tgt}' which has label above — "
                f"arrow crosses through label text. Move label to bottom or reroute."
            )

        # Case 3: Horizontal edge — check if it passes through a third icon's label zone
        if exit_y == "0.5" and entry_y == "0.5":
            arrow_y = src_geo["y"] + src_geo["height"] / 2
            arrow_x_min = min(
                src_geo["x"] + src_geo["width"],
                tgt_geo["x"] + tgt_geo["width"],
            )
            arrow_x_max = max(src_geo["x"], tgt_geo["x"])

            for v in vertices:
                vid = v.get("id")
                if vid in (src, tgt, "0", "1") or vid in group_ids:
                    continue
                v_geo = id_to_geo.get(vid)
                if not v_geo or v_geo.get("width", 0) < 48:
                    continue
                v_style = parse_style(v.get("style", ""))

                # Check if this icon sits between source and target horizontally
                v_cx = v_geo["x"] + v_geo["width"] / 2
                if not (arrow_x_min < v_cx < arrow_x_max):
                    continue

                # Check if the arrow Y passes through this icon's label zone
                if v_style.get("verticalLabelPosition") == "bottom":
                    label_top = v_geo["y"] + v_geo["height"]
                    label_bottom = label_top + LABEL_HEIGHT
                    if label_top <= arrow_y <= label_bottom:
                        label_conflicts.append(
                            f"'{eid}': horizontal arrow at y={arrow_y:.0f} crosses "
                            f"label zone of '{vid}' (label y={label_top:.0f}-{label_bottom:.0f})"
                        )
                elif v_style.get("verticalLabelPosition") == "top":
                    label_bottom = v_geo["y"]
                    label_top = label_bottom - LABEL_HEIGHT
                    if label_top <= arrow_y <= label_bottom:
                        label_conflicts.append(
                            f"'{eid}': horizontal arrow at y={arrow_y:.0f} crosses "
                            f"label zone of '{vid}' (label y={label_top:.0f}-{label_bottom:.0f})"
                        )

    if label_conflicts:
        warn(f"{len(label_conflicts)} arrows cross through label text:")
        for lc in label_conflicts[:8]:
            print(f"      → {lc}")
    else:
        ok("No arrows cross through label text")

    # --- Anti-Pattern 14: Overlapping edges ---
    # Flag edges that share the same routing corridor AND overlap in range.
    print("\n  Overlapping edges:")
    edge_paths = []
    for e in edges:
        eid = e.get("id", "?")
        src = e.get("source")
        tgt = e.get("target")
        style = parse_style(e.get("style", ""))
        if not src or not tgt:
            continue
        src_geo = id_to_geo.get(src)
        tgt_geo = id_to_geo.get(tgt)
        if not src_geo or not tgt_geo:
            continue

        exit_x = style.get("exitX", "1")
        exit_y = style.get("exitY", "0.5")
        entry_x = style.get("entryX", "0")
        entry_y = style.get("entryY", "0.5")

        # Compute the actual exit and entry points
        sx = src_geo["x"] + src_geo["width"] * float(exit_x)
        sy = src_geo["y"] + src_geo["height"] * float(exit_y)
        tx = tgt_geo["x"] + tgt_geo["width"] * float(entry_x)
        ty = tgt_geo["y"] + tgt_geo["height"] * float(entry_y)

        edge_paths.append((eid, sx, sy, tx, ty))

    overlapping = []
    for i in range(len(edge_paths)):
        for j in range(i + 1, len(edge_paths)):
            eid_a, sx_a, sy_a, tx_a, ty_a = edge_paths[i]
            eid_b, sx_b, sy_b, tx_b, ty_b = edge_paths[j]

            # Check horizontal corridor overlap: both edges run at similar Y
            a_horiz = abs(sy_a - ty_a) < 10  # edge A is horizontal
            b_horiz = abs(sy_b - ty_b) < 10  # edge B is horizontal
            if a_horiz and b_horiz and abs(sy_a - sy_b) < 5:
                # Same Y corridor — check if X ranges overlap
                a_xmin, a_xmax = min(sx_a, tx_a), max(sx_a, tx_a)
                b_xmin, b_xmax = min(sx_b, tx_b), max(sx_b, tx_b)
                if a_xmin < b_xmax and a_xmax > b_xmin:
                    overlapping.append(
                        f"'{eid_a}' and '{eid_b}' share horizontal corridor at y={sy_a:.0f}"
                    )

            # Check vertical corridor overlap: both edges run at similar X
            a_vert = abs(sx_a - tx_a) < 10  # edge A is vertical
            b_vert = abs(sx_b - tx_b) < 10  # edge B is vertical
            if a_vert and b_vert and abs(sx_a - sx_b) < 5:
                # Same X corridor — check if Y ranges overlap
                a_ymin, a_ymax = min(sy_a, ty_a), max(sy_a, ty_a)
                b_ymin, b_ymax = min(sy_b, ty_b), max(sy_b, ty_b)
                if a_ymin < b_ymax and a_ymax > b_ymin:
                    overlapping.append(
                        f"'{eid_a}' and '{eid_b}' share vertical corridor at x={sx_a:.0f}"
                    )

    if overlapping:
        fail(f"{len(overlapping)} pairs of edges overlap:")
        for o in overlapping[:8]:
            print(f"      → {o}")
    else:
        ok("No overlapping edges detected")

    # --- Anti-Pattern 15a: Arrows crossing through icons ---
    # Flag edges whose routing path passes through an icon that isn't source/target.
    print("\n  Arrow-through-icon detection:")
    crossing_violations = []

    # Build list of icon bounding boxes (exclude groups, callouts, text)
    icon_boxes = []
    for v in vertices:
        vid = v.get("id")
        if vid in ("0", "1") or vid in group_ids:
            continue
        geo = id_to_geo.get(vid)
        if not geo or geo.get("width", 0) < 48:
            continue
        icon_boxes.append((vid, geo["x"], geo["y"],
                           geo["x"] + geo["width"], geo["y"] + geo["height"]))

    def segment_crosses_box(sx, sy, tx, ty, bx1, by1, bx2, by2):
        """Check if a horizontal or vertical line segment crosses a box.
        Tolerates near-axis segments (within 15px) from orthogonal routing."""
        if abs(sy - ty) < 15:  # horizontal segment
            seg_y = (sy + ty) / 2
            seg_xmin, seg_xmax = min(sx, tx), max(sx, tx)
            if by1 < seg_y < by2 and seg_xmin < bx2 and seg_xmax > bx1:
                return True
        if abs(sx - tx) < 15:  # vertical segment
            seg_x = (sx + tx) / 2
            seg_ymin, seg_ymax = min(sy, ty), max(sy, ty)
            if bx1 < seg_x < bx2 and seg_ymin < by2 and seg_ymax > by1:
                return True
        return False

    for e in edges:
        eid = e.get("id", "?")
        src = e.get("source")
        tgt = e.get("target")
        style = parse_style(e.get("style", ""))
        if not src or not tgt:
            continue
        src_geo = id_to_geo.get(src)
        tgt_geo = id_to_geo.get(tgt)
        if not src_geo or not tgt_geo:
            continue

        exit_x = float(style.get("exitX", "1"))
        exit_y = float(style.get("exitY", "0.5"))
        entry_x = float(style.get("entryX", "0"))
        entry_y = float(style.get("entryY", "0.5"))

        sx = src_geo["x"] + src_geo["width"] * exit_x
        sy = src_geo["y"] + src_geo["height"] * exit_y
        tx = tgt_geo["x"] + tgt_geo["width"] * entry_x
        ty = tgt_geo["y"] + tgt_geo["height"] * entry_y

        # Build segment list from waypoints
        segments = []
        arr = e.find(".//Array")
        if arr is not None and len(arr) > 0:
            points = [(sx, sy)]
            for pt in arr:
                px = float(pt.get("x", 0))
                py = float(pt.get("y", 0))
                points.append((px, py))
            points.append((tx, ty))
            for k in range(len(points) - 1):
                segments.append((*points[k], *points[k + 1]))
        else:
            # Orthogonal edge with no waypoints — router creates an L-shape
            # if not axis-aligned, the midpoint bend is at (tx, sy) or (sx, ty)
            if abs(sx - tx) < 1 or abs(sy - ty) < 1:
                segments.append((sx, sy, tx, ty))
            else:
                # L-shape: horizontal then vertical
                segments.append((sx, sy, tx, sy))
                segments.append((tx, sy, tx, ty))

        for vid, bx1, by1, bx2, by2 in icon_boxes:
            if vid == src or vid == tgt:
                continue
            for seg in segments:
                if segment_crosses_box(*seg, bx1, by1, bx2, by2):
                    crossing_violations.append(
                        f"'{eid}' ({src}→{tgt}) crosses through icon '{vid}'"
                    )
                    break  # one violation per icon per edge

    if crossing_violations:
        fail(f"{len(crossing_violations)} arrows cross through icons:")
        for cv in crossing_violations[:8]:
            print(f"      → {cv}")
    else:
        ok("No arrows cross through icons")

    # --- Anti-Pattern 15b: Arrows crossing other arrows ---
    # Detect when a horizontal segment crosses a vertical segment (or vice versa).
    print("\n  Arrow-crossing-arrow detection:")

    def get_edge_segments(e):
        """Return list of (sx, sy, tx, ty) segments for an edge.
        Respects exit/entry perpendicular hints (exitY 0/1 → first segment
        vertical; exitX 0/1 → first segment horizontal). Previously this
        defaulted to horizontal-first, which produced false crossing reports
        when authors explicitly routed vertical-first via exitY=0/1.
        """
        src = e.get("source")
        tgt = e.get("target")
        style = parse_style(e.get("style", ""))
        if not src or not tgt:
            return []
        src_geo = id_to_geo.get(src)
        tgt_geo = id_to_geo.get(tgt)
        if not src_geo or not tgt_geo:
            return []
        ex = float(style.get("exitX", "1"))
        ey = float(style.get("exitY", "0.5"))
        nx = float(style.get("entryX", "0"))
        ny = float(style.get("entryY", "0.5"))
        sx = src_geo["x"] + src_geo["width"] * ex
        sy = src_geo["y"] + src_geo["height"] * ey
        tx = tgt_geo["x"] + tgt_geo["width"] * nx
        ty = tgt_geo["y"] + tgt_geo["height"] * ny

        arr = e.find(".//Array")
        if arr is not None and len(arr) > 0:
            points = [(sx, sy)]
            for pt in arr:
                points.append((float(pt.get("x", 0)), float(pt.get("y", 0))))
            points.append((tx, ty))
            return [(points[k][0], points[k][1], points[k+1][0], points[k+1][1])
                    for k in range(len(points) - 1)]

        # Single-segment (already axis-aligned)
        if abs(sx - tx) < 5 or abs(sy - ty) < 5:
            return [(sx, sy, tx, ty)]

        # Decide routing based on exit/entry perpendicular hints.
        # exitY 0 or 1 → exit top/bottom → first segment VERTICAL.
        # exitX 0 or 1 → exit left/right → first segment HORIZONTAL.
        exit_vertical = ey in (0.0, 1.0)
        entry_vertical = ny in (0.0, 1.0)
        if exit_vertical and not entry_vertical:
            # Vertical-then-horizontal: (sx, sy) → (sx, ty) → (tx, ty)
            return [(sx, sy, sx, ty), (sx, ty, tx, ty)]
        if not exit_vertical and entry_vertical:
            # Horizontal-then-vertical: (sx, sy) → (tx, sy) → (tx, ty)
            return [(sx, sy, tx, sy), (tx, sy, tx, ty)]
        if exit_vertical and entry_vertical:
            # Both ends vertical → need a 3-segment Z-bend through midpoint.
            mid_y = (sy + ty) / 2
            return [
                (sx, sy, sx, mid_y),
                (sx, mid_y, tx, mid_y),
                (tx, mid_y, tx, ty),
            ]
        # Both ends horizontal → 3-segment Z-bend through midpoint X.
        mid_x = (sx + tx) / 2
        return [
            (sx, sy, mid_x, sy),
            (mid_x, sy, mid_x, ty),
            (mid_x, ty, tx, ty),
        ]

    def segments_cross(s1, s2):
        """Check if a horizontal and vertical segment cross each other."""
        sx1, sy1, tx1, ty1 = s1
        sx2, sy2, tx2, ty2 = s2
        # s1 horizontal, s2 vertical
        if abs(sy1 - ty1) < 15 and abs(sx2 - tx2) < 15:
            h_y = (sy1 + ty1) / 2
            v_x = (sx2 + tx2) / 2
            h_xmin, h_xmax = min(sx1, tx1), max(sx1, tx1)
            v_ymin, v_ymax = min(sy2, ty2), max(sy2, ty2)
            if h_xmin <= v_x <= h_xmax and v_ymin <= h_y <= v_ymax:
                return True
        # s1 vertical, s2 horizontal
        if abs(sx1 - tx1) < 15 and abs(sy2 - ty2) < 15:
            v_x = (sx1 + tx1) / 2
            h_y = (sy2 + ty2) / 2
            v_ymin, v_ymax = min(sy1, ty1), max(sy1, ty1)
            h_xmin, h_xmax = min(sx2, tx2), max(sx2, tx2)
            if h_xmin <= v_x <= h_xmax and v_ymin <= h_y <= v_ymax:
                return True
        return False

    all_edge_segs = []
    for e in edges:
        eid = e.get("id", "?")
        segs = get_edge_segments(e)
        for seg in segs:
            all_edge_segs.append((eid, seg))

    crossing_arrows = []
    seen = set()
    for i in range(len(all_edge_segs)):
        for j in range(i + 1, len(all_edge_segs)):
            eid_a, seg_a = all_edge_segs[i]
            eid_b, seg_b = all_edge_segs[j]
            if eid_a == eid_b:
                continue
            pair = tuple(sorted([eid_a, eid_b]))
            if pair in seen:
                continue
            if segments_cross(seg_a, seg_b):
                crossing_arrows.append(f"'{eid_a}' and '{eid_b}' cross each other")
                seen.add(pair)

    if crossing_arrows:
        fail(f"{len(crossing_arrows)} pairs of arrows cross each other:")
        for ca in crossing_arrows[:8]:
            print(f"      → {ca}")
    else:
        ok("No arrows cross each other")

    # --- Anti-Pattern 15c: Arrows overlapping container boundary lines ---
    # Detect when an arrow segment runs along (overlaps) a container edge.
    print("\n  Arrow-on-container-line detection:")
    container_line_violations = []
    TOLERANCE = 10  # pixels — arrow within this distance of container edge counts as overlapping

    # Build container edge lines
    container_edges = []  # (gid, axis, coord, start, end) — axis='H' or 'V'
    for gid in group_ids:
        g_geo = id_to_geo.get(gid)
        if not g_geo:
            continue
        gx1 = g_geo["x"]
        gy1 = g_geo["y"]
        gx2 = gx1 + g_geo["width"]
        gy2 = gy1 + g_geo["height"]
        container_edges.append((gid, "H", gy1, gx1, gx2))  # top
        container_edges.append((gid, "H", gy2, gx1, gx2))  # bottom
        container_edges.append((gid, "V", gx1, gy1, gy2))  # left
        container_edges.append((gid, "V", gx2, gy1, gy2))  # right

    for e in edges:
        eid = e.get("id", "?")
        segs = get_edge_segments(e)
        for seg in segs:
            sx, sy, tx, ty = seg
            for gid, axis, coord, start, end in container_edges:
                if axis == "H" and abs(sy - ty) < 15:
                    # Horizontal arrow segment — check against horizontal container edge
                    seg_y = (sy + ty) / 2
                    if abs(seg_y - coord) < TOLERANCE:
                        seg_xmin, seg_xmax = min(sx, tx), max(sx, tx)
                        overlap = min(seg_xmax, end) - max(seg_xmin, start)
                        if overlap > 20:
                            container_line_violations.append(
                                f"'{eid}' overlaps {gid} {'top' if coord == id_to_geo[gid]['y'] else 'bottom'} edge at y={coord:.0f}"
                            )
                elif axis == "V" and abs(sx - tx) < 15:
                    # Vertical arrow segment — check against vertical container edge
                    seg_x = (sx + tx) / 2
                    if abs(seg_x - coord) < TOLERANCE:
                        seg_ymin, seg_ymax = min(sy, ty), max(sy, ty)
                        overlap = min(seg_ymax, end) - max(seg_ymin, start)
                        if overlap > 20:
                            container_line_violations.append(
                                f"'{eid}' overlaps {gid} {'left' if coord == id_to_geo[gid]['x'] else 'right'} edge at x={coord:.0f}"
                            )

    # Deduplicate
    container_line_violations = list(dict.fromkeys(container_line_violations))
    if container_line_violations:
        fail(f"{len(container_line_violations)} arrows overlap container boundary lines:")
        for cv in container_line_violations[:8]:
            print(f"      → {cv}")
    else:
        ok("No arrows overlap container boundary lines")

    # --- Anti-Pattern 15d: Unnecessary detour arrows ---
    # Flag edges using exit/entry that force a detour when a straight line exists.
    print("\n  Unnecessary detour detection:")
    detour_violations = []
    for e in edges:
        eid = e.get("id", "?")
        src = e.get("source")
        tgt = e.get("target")
        style = parse_style(e.get("style", ""))
        if not src or not tgt:
            continue
        if src in group_ids or tgt in group_ids:
            continue
        src_geo = id_to_geo.get(src)
        tgt_geo = id_to_geo.get(tgt)
        if not src_geo or not tgt_geo:
            continue

        src_cx = src_geo["x"] + src_geo["width"] / 2
        src_cy = src_geo["y"] + src_geo["height"] / 2
        tgt_cx = tgt_geo["x"] + tgt_geo["width"] / 2
        tgt_cy = tgt_geo["y"] + tgt_geo["height"] / 2

        ex = float(style.get("exitX", "-1"))
        ey = float(style.get("exitY", "-1"))
        nx = float(style.get("entryX", "-1"))
        ny = float(style.get("entryY", "-1"))
        if ex < 0 or nx < 0:
            continue

        # Icons share X center (vertical connection possible)
        if abs(src_cx - tgt_cx) <= 5:
            # Exit/entry should be top/bottom — not left/right
            exit_side = "left/right" if ey == 0.5 and ex in (0, 1) else None
            entry_side = "left/right" if ny == 0.5 and nx in (0, 1) else None
            if exit_side or entry_side:
                detour_violations.append(
                    f"'{eid}': {src} and {tgt} share X center — use top/bottom "
                    f"connection instead of {exit_side or ''}/{entry_side or ''} detour"
                )

        # Icons share Y center (horizontal connection possible)
        if abs(src_cy - tgt_cy) <= 5:
            exit_side = "top/bottom" if ex == 0.5 and ey in (0, 1) else None
            entry_side = "top/bottom" if nx == 0.5 and ny in (0, 1) else None
            if exit_side or entry_side:
                detour_violations.append(
                    f"'{eid}': {src} and {tgt} share Y center — use left/right "
                    f"connection instead of {exit_side or ''}/{entry_side or ''} detour"
                )

    if detour_violations:
        fail(f"{len(detour_violations)} arrows take unnecessary detours:")
        for dv in detour_violations[:8]:
            print(f"      → {dv}")
    else:
        ok("No unnecessary detour arrows")

    # --- Anti-Pattern 15: Callout presence ---
    # Every architecture diagram should have numbered callouts to tell the story.
    print("\n  Callout presence:")
    # Count AWS service icons (icons with resIcon or shape=mxgraph.aws4)
    aws_icons = [
        v for v in vertices
        if "resIcon" in v.get("style", "") or "shape=mxgraph.aws4" in v.get("style", "")
    ]
    if len(aws_icons) >= 3 and not callouts:
        warn(
            f"Diagram has {len(aws_icons)} AWS service icons but no numbered callouts. "
            f"Add callouts to show the request flow step by step."
        )
    elif len(aws_icons) >= 3 and callouts:
        ok(f"{len(callouts)} callouts present for {len(aws_icons)} AWS icons")
    else:
        ok("Small diagram — callouts optional")

    # =========================================================
    print("\n--- Visual Layout Quality ---")
    # =========================================================

    # --- Layout 1: Callout flow sequence ---
    # Inline arrow callouts AND legend callouts both use digit labels starting at 1.
    # Detect legend zone as Y beyond max icon Y + 40px and exclude those.
    print("\n  Flow sequence (callout spatial order):")
    if len(callouts) >= 2:
        icon_y_vals = [g["y"] + g["height"] for _id, g in non_callout_vertices
                       if g.get("width", 0) >= 40 and _id not in group_ids]
        max_icon_y = max(icon_y_vals) if icon_y_vals else 0
        LEGEND_Y_THRESHOLD = max_icon_y + 40

        diagram_callouts = [c for c in callouts if c[1]["y"] < LEGEND_Y_THRESHOLD]
        by_num = {}
        for cid, geo, num in diagram_callouts:
            if num not in by_num or geo["y"] < by_num[num][1]["y"]:
                by_num[num] = (cid, geo, num)
        sorted_callouts = sorted(by_num.values(), key=lambda c: c[2])

        sequence_issues = []
        for i in range(len(sorted_callouts) - 1):
            cid_a, geo_a, num_a = sorted_callouts[i]
            cid_b, geo_b, num_b = sorted_callouts[i + 1]
            ax = geo_a["x"]
            ay = geo_a["y"]
            bx = geo_b["x"]
            by = geo_b["y"]
            if bx < ax - 100 and by < ay - 50:
                sequence_issues.append(
                    f"Callout {num_b} (x={bx:.0f},y={by:.0f}) backtracks left+up "
                    f"from callout {num_a} (x={ax:.0f},y={ay:.0f})"
                )
        if sequence_issues:
            warn(f"{len(sequence_issues)} callouts break spatial reading order:")
            for si in sequence_issues[:8]:
                print(f"      → {si}")
        else:
            ok("Callout sequence follows spatial reading order")
    else:
        ok("Too few callouts to check sequence")

    # --- Layout 2: Container content centering ---
    # Children inside a container should be roughly centered (not bunched to one side).
    print("\n  Container content centering:")
    centering_issues = []
    for gid in group_ids:
        g_geo = id_to_geo.get(gid)
        if not g_geo or g_geo.get("width", 0) < 150:
            continue
        gx1 = g_geo["x"]
        gy1 = g_geo["y"]
        gx2 = gx1 + g_geo["width"]
        gy2 = gy1 + g_geo["height"]
        g_cx = (gx1 + gx2) / 2
        g_cy = (gy1 + gy2) / 2

        # Collect children inside this container
        children_geos = []
        for v in vertices:
            vid = v.get("id")
            if vid in ("0", "1") or vid in group_ids:
                continue
            v_geo = id_to_geo.get(vid)
            if not v_geo or v_geo.get("width", 0) < 20:
                continue
            vx1 = v_geo["x"]
            vy1 = v_geo["y"]
            vx2 = vx1 + v_geo["width"]
            vy2 = vy1 + v_geo["height"]
            # Check if inside this container
            if vx1 >= gx1 and vy1 >= gy1 and vx2 <= gx2 and vy2 <= gy2:
                children_geos.append(v_geo)

        if len(children_geos) < 1:
            continue

        # Compute bounding box of all children
        child_min_x = min(cg["x"] for cg in children_geos)
        child_max_x = max(cg["x"] + cg["width"] for cg in children_geos)
        child_min_y = min(cg["y"] for cg in children_geos)
        child_max_y = max(cg["y"] + cg["height"] for cg in children_geos)
        child_cx = (child_min_x + child_max_x) / 2
        child_cy = (child_min_y + child_max_y) / 2

        # Allow some offset for the container title (top ~30px)
        effective_gy1 = gy1 + 30
        effective_g_cy = (gx1 + gx2) / 2  # X center unchanged
        effective_g_cy_y = (effective_gy1 + gy2) / 2

        x_offset = abs(child_cx - g_cx)
        y_offset = abs(child_cy - effective_g_cy_y)

        # Threshold: children center should be within 15% of container dimension
        x_threshold = g_geo["width"] * 0.15
        y_threshold = (gy2 - effective_gy1) * 0.15

        if x_offset > x_threshold:
            centering_issues.append(
                f"'{gid}': children off-center horizontally by {x_offset:.0f}px "
                f"(threshold {x_threshold:.0f}px)"
            )
        if y_offset > y_threshold and (gy2 - effective_gy1) > 100:
            centering_issues.append(
                f"'{gid}': children off-center vertically by {y_offset:.0f}px "
                f"(threshold {y_threshold:.0f}px)"
            )

    if centering_issues:
        warn(f"{len(centering_issues)} containers have off-center content:")
        for ci in centering_issues[:8]:
            print(f"      → {ci}")
    else:
        ok("All container content is reasonably centered")

    # --- Layout 3: Container spacing uniformity ---
    # Containers at the same hierarchy level should have consistent gaps between them.
    print("\n  Container spacing uniformity:")
    container_geos = []
    for gid in group_ids:
        g_geo = id_to_geo.get(gid)
        if g_geo and g_geo.get("width", 0) > 150:
            container_geos.append((gid, g_geo))

    if len(container_geos) >= 2:
        # Find horizontal neighbors (overlapping Y ranges)
        h_gaps = []
        for i in range(len(container_geos)):
            gid_a, ga = container_geos[i]
            for j in range(i + 1, len(container_geos)):
                gid_b, gb = container_geos[j]
                # Check Y overlap
                ay1, ay2 = ga["y"], ga["y"] + ga["height"]
                by1, by2 = gb["y"], gb["y"] + gb["height"]
                if ay1 < by2 and ay2 > by1:
                    # Horizontal gap
                    ax2 = ga["x"] + ga["width"]
                    bx1 = gb["x"]
                    bx2 = gb["x"] + gb["width"]
                    ax1 = ga["x"]
                    gap = max(bx1 - ax2, ax1 - bx2)
                    if gap > 0:
                        h_gaps.append((gid_a, gid_b, gap))

        # Find vertical neighbors (overlapping X ranges)
        v_gaps = []
        for i in range(len(container_geos)):
            gid_a, ga = container_geos[i]
            for j in range(i + 1, len(container_geos)):
                gid_b, gb = container_geos[j]
                ax1, ax2 = ga["x"], ga["x"] + ga["width"]
                bx1, bx2 = gb["x"], gb["x"] + gb["width"]
                if ax1 < bx2 and ax2 > bx1:
                    ay2 = ga["y"] + ga["height"]
                    by1 = gb["y"]
                    by2 = gb["y"] + gb["height"]
                    ay1 = ga["y"]
                    gap = max(by1 - ay2, ay1 - by2)
                    if gap > 0:
                        v_gaps.append((gid_a, gid_b, gap))

        spacing_issues = []
        # Check horizontal gap consistency
        if len(h_gaps) >= 2:
            gap_values = [g for _, _, g in h_gaps]
            avg_gap = sum(gap_values) / len(gap_values)
            for gid_a, gid_b, gap in h_gaps:
                if abs(gap - avg_gap) > avg_gap * 0.5 and abs(gap - avg_gap) > 30:
                    spacing_issues.append(
                        f"'{gid_a}' ↔ '{gid_b}': horizontal gap={gap:.0f}px "
                        f"(avg={avg_gap:.0f}px)"
                    )

        # Check vertical gap consistency
        if len(v_gaps) >= 2:
            gap_values = [g for _, _, g in v_gaps]
            avg_gap = sum(gap_values) / len(gap_values)
            for gid_a, gid_b, gap in v_gaps:
                if abs(gap - avg_gap) > avg_gap * 0.5 and abs(gap - avg_gap) > 30:
                    spacing_issues.append(
                        f"'{gid_a}' ↔ '{gid_b}': vertical gap={gap:.0f}px "
                        f"(avg={avg_gap:.0f}px)"
                    )

        if spacing_issues:
            warn(f"{len(spacing_issues)} container pairs have inconsistent spacing:")
            for si in spacing_issues[:8]:
                print(f"      → {si}")
        else:
            ok("Container spacing is consistent")
    else:
        ok("Fewer than 2 containers — spacing check skipped")

    # --- Layout 4: Nested container format standardization ---
    # Inner containers should have consistent border/radius/font styling.
    print("\n  Nested container standardization:")
    nested_containers = []
    for gid in group_ids:
        g_geo = id_to_geo.get(gid)
        if not g_geo:
            continue
        gx1, gy1 = g_geo["x"], g_geo["y"]
        gx2, gy2 = gx1 + g_geo["width"], gy1 + g_geo["height"]
        # Check if this container is inside another container
        for pid in group_ids:
            if pid == gid:
                continue
            p_geo = id_to_geo.get(pid)
            if not p_geo:
                continue
            px1, py1 = p_geo["x"], p_geo["y"]
            px2, py2 = px1 + p_geo["width"], py1 + p_geo["height"]
            if gx1 >= px1 and gy1 >= py1 and gx2 <= px2 and gy2 <= py2:
                # gid is nested inside pid
                cell = id_to_cell.get(gid)
                if cell is not None:
                    nested_containers.append((gid, parse_style(cell.get("style", ""))))
                break

    if len(nested_containers) >= 2:
        # Compare key style properties across nested containers
        style_signatures = []
        for gid, style in nested_containers:
            sig = {
                "dashed": style.get("dashed", "0"),
                "rounded": style.get("rounded", "0"),
                "fillColor": style.get("fillColor", "none"),
                "fontSize": style.get("fontSize", "12"),
            }
            style_signatures.append((gid, sig))

        # Check if all nested containers share the same format
        reference = style_signatures[0][1]
        format_issues = []
        for gid, sig in style_signatures[1:]:
            diffs = []
            for key in reference:
                if sig[key] != reference[key]:
                    diffs.append(f"{key}={sig[key]} vs {reference[key]}")
            if diffs:
                format_issues.append(
                    f"'{gid}' differs from '{style_signatures[0][0]}': {', '.join(diffs)}"
                )

        if format_issues:
            warn(f"{len(format_issues)} nested containers have inconsistent formatting:")
            for fi in format_issues[:8]:
                print(f"      → {fi}")
        else:
            ok("All nested containers have consistent formatting")
    else:
        ok("Fewer than 2 nested containers — format check skipped")

    # --- Layout 5: Arrow direction consistency ---
    # Primary flow is left-to-right. Flag if >40% arrows go backwards.
    print("\n  Arrow direction consistency:")
    forward_count = 0
    backward_count = 0
    for e in edges:
        src = e.get("source")
        tgt = e.get("target")
        if not src or not tgt:
            continue
        src_geo = id_to_geo.get(src)
        tgt_geo = id_to_geo.get(tgt)
        if not src_geo or not tgt_geo:
            continue
        if src in group_ids or tgt in group_ids:
            continue
        src_cx = src_geo["x"] + src_geo["width"] / 2
        tgt_cx = tgt_geo["x"] + tgt_geo["width"] / 2
        # Only count horizontal movement (ignore purely vertical edges)
        if abs(src_cx - tgt_cx) > 30:
            if tgt_cx > src_cx:
                forward_count += 1
            else:
                backward_count += 1

    total_directional = forward_count + backward_count
    if total_directional > 0:
        backward_pct = backward_count / total_directional * 100
        if backward_pct > 40:
            warn(
                f"{backward_count}/{total_directional} arrows ({backward_pct:.0f}%) go right-to-left. "
                f"Primary flow should be left-to-right. Reorganize layout to reduce backtracking."
            )
        else:
            ok(f"Arrow direction: {forward_count} forward, {backward_count} backward ({backward_pct:.0f}% reverse)")
    else:
        ok("No directional arrows to check")

    # --- Layout 6: Edge exit/entry point consistency ---
    # Multiple edges leaving same side should use evenly distributed exit points.
    print("\n  Edge exit/entry distribution:")
    exit_points_by_cell = defaultdict(list)  # cell_id -> [(edge_id, side, point)]
    for e in edges:
        eid = e.get("id", "?")
        src = e.get("source")
        style = parse_style(e.get("style", ""))
        if not src:
            continue
        ex = style.get("exitX")
        ey = style.get("exitY")
        if ex is not None and ey is not None:
            # Determine which side: right(1,*), left(0,*), top(*,0), bottom(*,1)
            ex_f, ey_f = float(ex), float(ey)
            if ex_f == 1:
                side = "right"
                point = ey_f
            elif ex_f == 0:
                side = "left"
                point = ey_f
            elif ey_f == 0:
                side = "top"
                point = ex_f
            elif ey_f == 1:
                side = "bottom"
                point = ex_f
            else:
                side = "other"
                point = 0
            exit_points_by_cell[src].append((eid, side, point))

    distribution_issues = []
    for cell_id, exits in exit_points_by_cell.items():
        # Group by side
        by_side = defaultdict(list)
        for eid, side, point in exits:
            by_side[side].append((eid, point))
        for side, points in by_side.items():
            if len(points) >= 3:
                # Check if all points are the same (all at 0.5)
                point_values = [p for _, p in points]
                if len(set(point_values)) == 1:
                    distribution_issues.append(
                        f"'{cell_id}' {side} side: {len(points)} edges all exit at "
                        f"same point ({point_values[0]}). Distribute across 0.25/0.5/0.75."
                    )

    if distribution_issues:
        warn(f"{len(distribution_issues)} icons have stacked edge exit points:")
        for di in distribution_issues[:8]:
            print(f"      → {di}")
    else:
        ok("Edge exit/entry points are well distributed")

    # --- Layout 7: Container size vs content ---
    # Flag too-small (child packed into box) AND too-large (icons lost in space).
    print("\n  Container minimum size:")
    size_issues_small = []
    size_issues_large = []
    for gid in group_ids:
        g_geo = id_to_geo.get(gid)
        if not g_geo:
            continue
        gx1, gy1 = g_geo["x"], g_geo["y"]
        gx2, gy2 = gx1 + g_geo["width"], gy1 + g_geo["height"]
        child_boxes = []
        for v in vertices:
            vid = v.get("id")
            if vid in ("0", "1") or vid in group_ids:
                continue
            v_geo = id_to_geo.get(vid)
            if not v_geo or v_geo.get("width", 0) < 20:
                continue
            if (v_geo["x"] >= gx1 and v_geo["y"] >= gy1 and
                    v_geo["x"] + v_geo["width"] <= gx2 and
                    v_geo["y"] + v_geo["height"] <= gy2):
                child_boxes.append(v_geo)
        n = len(child_boxes)
        if n == 0:
            continue
        w = g_geo["width"]
        h = g_geo["height"]
        if w < 120 or h < 80:
            size_issues_small.append(f"'{gid}': {w:.0f}×{h:.0f}px with {n} children — too small")
            continue
        # Oversize check: tight bbox + padding
        bx1 = min(b["x"] for b in child_boxes)
        by1 = min(b["y"] for b in child_boxes)
        bx2 = max(b["x"] + b["width"] for b in child_boxes)
        by2 = max(b["y"] + b["height"] for b in child_boxes)
        expected_w = (bx2 - bx1) + 80
        expected_h = (by2 - by1) + 120  # +80 padding, +40 label strip
        if w > expected_w * 1.6 or h > expected_h * 1.6:
            size_issues_large.append(
                f"'{gid}': {w:.0f}×{h:.0f}px but {n} icons only need ~{expected_w:.0f}×{expected_h:.0f}px — compact it"
            )

    if size_issues_small:
        warn(f"{len(size_issues_small)} containers too small:")
        for si in size_issues_small[:6]:
            print(f"      → {si}")
    if size_issues_large:
        warn(f"{len(size_issues_large)} containers oversized for content:")
        for si in size_issues_large[:6]:
            print(f"      → {si}")
    if not size_issues_small and not size_issues_large:
        ok("All container sizes match content")

    # --- Layout 7c: Corner-exit arrows ---
    # Edges exiting/entering at actual corners (both axes at 0 or 1) look ragged.
    # Prefer centered (0.5) or quarter-offset (0.25/0.75) connections.
    print("\n  Corner-exit arrows:")
    corner_issues = []
    for e in edges:
        eid = e.get("id", "?")
        style = parse_style(e.get("style", ""))
        try:
            ex = float(style.get("exitX", "1"))
            ey = float(style.get("exitY", "0.5"))
            nx = float(style.get("entryX", "0"))
            ny = float(style.get("entryY", "0.5"))
        except ValueError:
            continue
        if ex in (0.0, 1.0) and ey in (0.0, 1.0):
            corner_issues.append(
                f"'{eid}': exits at corner ({ex},{ey}) — prefer centered exit"
            )
        if nx in (0.0, 1.0) and ny in (0.0, 1.0):
            corner_issues.append(
                f"'{eid}': enters at corner ({nx},{ny}) — prefer centered entry"
            )
    if corner_issues:
        warn(f"{len(corner_issues)} edges use corner connection points:")
        for ci in corner_issues[:6]:
            print(f"      → {ci}")
    else:
        ok("All edges use center or quarter-offset connection points")

    # --- Anti-Pattern 16: Arrow penetrating node body ---
    # Flag edges whose entry/exit lands inside the node bbox instead of at perimeter.
    print("\n  Arrow-penetrating-node detection:")
    penetration_violations = []

    for e in edges:
        eid = e.get("id", "?")
        src = e.get("source")
        tgt = e.get("target")
        style = parse_style(e.get("style", ""))
        if not src or not tgt:
            continue
        src_geo = id_to_geo.get(src)
        tgt_geo = id_to_geo.get(tgt)
        if not src_geo or not tgt_geo:
            continue
        # Skip edges involving groups — they intentionally span large areas
        if src in group_ids or tgt in group_ids:
            continue

        # Compute the actual exit point on the source
        ex = float(style.get("exitX", "-1"))
        ey = float(style.get("exitY", "-1"))
        nx = float(style.get("entryX", "-1"))
        ny = float(style.get("entryY", "-1"))

        # Check entry point: does the arrow's last segment approach the target
        # from a direction that would place the arrowhead inside the node body?
        # This happens when:
        # 1. The entry point is not on the perimeter (entryX/entryY not 0 or 1)
        # 2. OR the arrow approaches from a direction that causes it to cross
        #    through the node body before reaching the connection point.

        if nx >= 0 and ny >= 0:
            # Entry point in absolute coordinates
            entry_abs_x = tgt_geo["x"] + tgt_geo["width"] * nx
            entry_abs_y = tgt_geo["y"] + tgt_geo["height"] * ny

            # Check if entry point is strictly inside the node (not on perimeter)
            PERIMETER_TOLERANCE = 0.01
            is_on_left = abs(nx) < PERIMETER_TOLERANCE
            is_on_right = abs(nx - 1.0) < PERIMETER_TOLERANCE
            is_on_top = abs(ny) < PERIMETER_TOLERANCE
            is_on_bottom = abs(ny - 1.0) < PERIMETER_TOLERANCE
            on_perimeter = is_on_left or is_on_right or is_on_top or is_on_bottom

            if not on_perimeter and 0 < nx < 1 and 0 < ny < 1:
                penetration_violations.append(
                    f"'{eid}': arrow enters inside '{tgt}' body at "
                    f"entryX={nx}, entryY={ny} — arrowhead is buried in the node. "
                    f"Move entry point to a perimeter position (0 or 1 on one axis)."
                )

        if ex >= 0 and ey >= 0:
            # Check if exit point is strictly inside the source node
            PERIMETER_TOLERANCE = 0.01
            is_on_left = abs(ex) < PERIMETER_TOLERANCE
            is_on_right = abs(ex - 1.0) < PERIMETER_TOLERANCE
            is_on_top = abs(ey) < PERIMETER_TOLERANCE
            is_on_bottom = abs(ey - 1.0) < PERIMETER_TOLERANCE
            on_perimeter = is_on_left or is_on_right or is_on_top or is_on_bottom

            if not on_perimeter and 0 < ex < 1 and 0 < ey < 1:
                penetration_violations.append(
                    f"'{eid}': arrow exits from inside '{src}' body at "
                    f"exitX={ex}, exitY={ey} — arrow originates inside the node. "
                    f"Move exit point to a perimeter position (0 or 1 on one axis)."
                )

        # Also check: does the arrow's computed path enter the target node's
        # bounding box from a side other than where the entry point is?
        # This catches cases where the orthogonal router routes the arrow
        # through the node body to reach the connection point.
        if nx >= 0 and ny >= 0 and ex >= 0 and ey >= 0:
            # Get the last segment approaching the target
            arr = e.find(".//Array")
            if arr is not None and len(arr) > 0:
                # Last waypoint before target
                last_wp = arr[-1]
                last_x = float(last_wp.get("x", 0))
                last_y = float(last_wp.get("y", 0))
            else:
                # No waypoints — arrow comes directly from source exit
                last_x = src_geo["x"] + src_geo["width"] * ex
                last_y = src_geo["y"] + src_geo["height"] * ey

            entry_abs_x = tgt_geo["x"] + tgt_geo["width"] * nx
            entry_abs_y = tgt_geo["y"] + tgt_geo["height"] * ny

            # Check if the line from last point to entry point crosses through
            # the target node's interior (not just touching the edge)
            tgt_x1 = tgt_geo["x"]
            tgt_y1 = tgt_geo["y"]
            tgt_x2 = tgt_x1 + tgt_geo["width"]
            tgt_y2 = tgt_y1 + tgt_geo["height"]

            # Shrink the box slightly to avoid false positives at the perimeter
            SHRINK = 3
            inner_x1 = tgt_x1 + SHRINK
            inner_y1 = tgt_y1 + SHRINK
            inner_x2 = tgt_x2 - SHRINK
            inner_y2 = tgt_y2 - SHRINK

            # For orthogonal routing, the last segment is either horizontal or vertical
            if abs(last_y - entry_abs_y) < 5:
                # Horizontal approach — check if the arrow enters through the side
                # but the entry point is on top/bottom (arrow cuts through body)
                is_entry_on_side = is_on_left or is_on_right if (nx >= 0 and ny >= 0) else True
                if not is_entry_on_side:
                    # Entry is on top or bottom, but approach is horizontal
                    # Check if the horizontal line at last_y passes through the node body
                    if inner_y1 < last_y < inner_y2:
                        x_min = min(last_x, entry_abs_x)
                        x_max = max(last_x, entry_abs_x)
                        if x_min < inner_x2 and x_max > inner_x1:
                            penetration_violations.append(
                                f"'{eid}': arrow approaches '{tgt}' horizontally at y={last_y:.0f} "
                                f"but entry is on {'top' if ny < 0.5 else 'bottom'} — "
                                f"arrow cuts through node body. Reroute or change entry point."
                            )

            elif abs(last_x - entry_abs_x) < 5:
                # Vertical approach — check if the arrow enters through top/bottom
                # but the entry point is on left/right (arrow cuts through body)
                is_entry_on_tb = is_on_top or is_on_bottom if (nx >= 0 and ny >= 0) else True
                if not is_entry_on_tb:
                    # Entry is on left or right, but approach is vertical
                    if inner_x1 < last_x < inner_x2:
                        y_min = min(last_y, entry_abs_y)
                        y_max = max(last_y, entry_abs_y)
                        if y_min < inner_y2 and y_max > inner_y1:
                            penetration_violations.append(
                                f"'{eid}': arrow approaches '{tgt}' vertically at x={last_x:.0f} "
                                f"but entry is on {'left' if nx < 0.5 else 'right'} — "
                                f"arrow cuts through node body. Reroute or change entry point."
                            )

    # Deduplicate (same edge might trigger multiple sub-checks)
    seen_penetrations = set()
    unique_penetrations = []
    for pv in penetration_violations:
        edge_id = pv.split("'")[1]  # extract edge ID
        if edge_id not in seen_penetrations:
            seen_penetrations.add(edge_id)
            unique_penetrations.append(pv)

    if unique_penetrations:
        fail(f"{len(unique_penetrations)} arrows penetrate node bodies:")
        for pv in unique_penetrations[:8]:
            print(f"      → {pv}")
    else:
        ok("No arrows penetrate node bodies")

    # --- Anti-Pattern 17: Overlapping text / label zones ---
    # Flag when any two label zones or text-only cells overlap.
    print("\n  Text/label overlap detection:")
    text_overlap_violations = []

    # Estimate label height based on line count in the value
    def estimate_label_lines(value):
        """Count lines in a label value (split by &#xa; or <br>)."""
        if not value:
            return 0
        text = value.replace("&#xa;", "\n").replace("<br>", "\n").replace("<br/>", "\n")
        lines = [l for l in text.split("\n") if l.strip()]
        return max(len(lines), 1)

    def estimate_text_bbox(cell, geo, style):
        """Estimate the bounding box of a text-only cell based on fontSize and content."""
        if not geo:
            return None
        return (geo["x"], geo["y"], geo["x"] + geo["width"], geo["y"] + geo["height"])

    # Build list of all label zones: (id, x1, y1, x2, y2, description)
    label_zones = []
    LINE_HEIGHT = 16  # approximate pixels per line of label text
    LABEL_PAD = 4     # padding around label text

    for v in vertices:
        vid = v.get("id")
        if vid in ("0", "1"):
            continue
        style_str = v.get("style", "")
        style = parse_style(style_str)
        geo = id_to_geo.get(vid)
        value = v.get("value", "")
        if not geo or not value:
            continue

        is_text = style_str.startswith("text;") or style.get("text") is True

        if is_text:
            # Text-only element — its bounding box IS the text zone
            tx1 = geo["x"]
            ty1 = geo["y"]
            tx2 = tx1 + geo["width"]
            ty2 = ty1 + geo["height"]
            label_zones.append((vid, tx1, ty1, tx2, ty2, "text element"))
        elif vid not in group_ids:
            # Icon with a label — compute the label zone based on label position
            vlp = style.get("verticalLabelPosition", "")
            hlp = style.get("labelPosition", "")
            num_lines = estimate_label_lines(value)
            label_h = num_lines * LINE_HEIGHT + LABEL_PAD

            # Estimate label width: ~7px per character, capped at icon width * 2
            clean_text = value.replace("&#xa;", "\n").replace("<br>", "\n")
            max_line_len = max((len(l) for l in clean_text.split("\n") if l.strip()), default=0)
            label_w = max(max_line_len * 7, geo["width"])

            icon_cx = geo["x"] + geo["width"] / 2

            if vlp == "bottom":
                # Label below the icon
                lx1 = icon_cx - label_w / 2
                ly1 = geo["y"] + geo["height"]
                lx2 = icon_cx + label_w / 2
                ly2 = ly1 + label_h
                label_zones.append((vid, lx1, ly1, lx2, ly2, "label below"))
            elif vlp == "top":
                # Label above the icon
                lx1 = icon_cx - label_w / 2
                ly2 = geo["y"]
                ly1 = ly2 - label_h
                lx2 = icon_cx + label_w / 2
                label_zones.append((vid, lx1, ly1, lx2, ly2, "label above"))
            else:
                # Label inside the icon (default) or centered — use the icon's
                # own bounding box extended slightly for text overflow
                # Only flag if the text is wider than the icon
                if label_w > geo["width"] + 20:
                    lx1 = icon_cx - label_w / 2
                    ly1 = geo["y"]
                    lx2 = icon_cx + label_w / 2
                    ly2 = geo["y"] + geo["height"]
                    label_zones.append((vid, lx1, ly1, lx2, ly2, "label overflow"))

    # Treat container titles as label zones — catches title-vs-icon-label collisions.
    for v in vertices:
        vid = v.get("id")
        if vid not in group_ids:
            continue
        geo = id_to_geo.get(vid)
        value = v.get("value", "")
        if not geo or not value:
            continue
        style = parse_style(v.get("style", ""))
        # Default spacing if not specified
        spacing_left = int(style.get("spacingLeft", 0) or 0)
        spacing_top = int(style.get("spacingTop", 0) or 0)
        # Strip HTML out of the title to measure width
        clean_title = re.sub(r"<[^>]+>", "", value).replace("&#xa;", " ")
        title_w = max(len(clean_title) * 7, 40)  # ~7px per char, min 40px
        title_font_size = int(style.get("fontSize", 12) or 12)
        # Title text zone extends below the font baseline for descent + padding.
        # Use 1.5x font size to cover the full visual text box.
        title_h = int(title_font_size * 1.5) + LABEL_PAD
        # Include a buffer band above/below to catch near-misses where an icon
        # label skirts the title by 1-2px.
        title_buffer = 3
        tx1 = geo["x"] + spacing_left - title_buffer
        ty1 = geo["y"] + spacing_top - title_buffer
        tx2 = tx1 + title_w + 2 * title_buffer
        ty2 = ty1 + title_h + 2 * title_buffer
        label_zones.append((vid, tx1, ty1, tx2, ty2, "container title"))

    # Check label zones against each other
    OVERLAP_TOLERANCE = 2  # allow 2px of overlap before flagging
    for i in range(len(label_zones)):
        id_a, ax1, ay1, ax2, ay2, desc_a = label_zones[i]
        for j in range(i + 1, len(label_zones)):
            id_b, bx1, by1, bx2, by2, desc_b = label_zones[j]

            # Skip if same element
            if id_a == id_b:
                continue

            # Check AABB overlap
            overlap_x = min(ax2, bx2) - max(ax1, bx1)
            overlap_y = min(ay2, by2) - max(ay1, by1)

            if overlap_x > OVERLAP_TOLERANCE and overlap_y > OVERLAP_TOLERANCE:
                text_overlap_violations.append(
                    f"'{id_a}' ({desc_a}) overlaps '{id_b}' ({desc_b}) "
                    f"by {overlap_x:.0f}×{overlap_y:.0f}px"
                )

    # Check label zones against icon bodies (not their own icon)
    for lid, lx1, ly1, lx2, ly2, ldesc in label_zones:
        for v in vertices:
            vid = v.get("id")
            if vid == lid or vid in ("0", "1") or vid in group_ids:
                continue
            v_geo = id_to_geo.get(vid)
            if not v_geo or v_geo.get("width", 0) < 20:
                continue
            style_str = v.get("style", "")
            # Skip text-only elements (already checked above)
            if style_str.startswith("text;") or parse_style(style_str).get("text") is True:
                continue
            # Skip callouts (small circles)
            if vid in callout_ids:
                continue

            vx1 = v_geo["x"]
            vy1 = v_geo["y"]
            vx2 = vx1 + v_geo["width"]
            vy2 = vy1 + v_geo["height"]

            overlap_x = min(lx2, vx2) - max(lx1, vx1)
            overlap_y = min(ly2, vy2) - max(ly1, vy1)

            if overlap_x > OVERLAP_TOLERANCE and overlap_y > OVERLAP_TOLERANCE:
                text_overlap_violations.append(
                    f"'{lid}' ({ldesc}) overlaps icon '{vid}' body "
                    f"by {overlap_x:.0f}×{overlap_y:.0f}px"
                )

    # Deduplicate
    text_overlap_violations = list(dict.fromkeys(text_overlap_violations))

    if text_overlap_violations:
        fail(f"{len(text_overlap_violations)} text/label overlaps detected:")
        for tv in text_overlap_violations[:10]:
            print(f"      → {tv}")
        if len(text_overlap_violations) > 10:
            print(f"      ... and {len(text_overlap_violations) - 10} more")
    else:
        ok("No text/label overlaps detected")

    # --- Anti-Pattern 18: Nested container title clearance ---
    # Child container's top must not cover parent's top ~30px title strip.
    print("\n  Nested container title clearance:")
    title_clearance_violations = []
    group_cells = [v for v in vertices if v.get("id") in group_ids]
    # Build a list of (vid, geo, title_strip_rect)
    group_info = []
    for v in group_cells:
        vid = v.get("id")
        geo = id_to_geo.get(vid)
        value = v.get("value", "")
        if not geo or not value.strip():
            continue
        style = parse_style(v.get("style", ""))
        spacing_top = int(style.get("spacingTop", 0) or 0)
        font_size = int(style.get("fontSize", 12) or 12)
        # Title strip reserves the top spacingTop + ~1.5*font_size pixels.
        # Use a conservative 30px minimum so we catch ASG-covers-subnet-title.
        strip_h = max(spacing_top + int(font_size * 1.5) + 4, 30)
        strip = (geo["x"], geo["y"], geo["x"] + geo["width"], geo["y"] + strip_h)
        group_info.append((vid, geo, strip, value.strip()))

    for i, (id_a, geo_a, strip_a, val_a) in enumerate(group_info):
        ax1, ay1, ax2, ay2 = strip_a
        for j, (id_b, geo_b, _strip_b, val_b) in enumerate(group_info):
            if i == j:
                continue
            # B is a candidate child/sibling if its rectangle overlaps A's strip
            bx1, by1 = geo_b["x"], geo_b["y"]
            bx2, by2 = bx1 + geo_b["width"], by1 + geo_b["height"]
            # B must horizontally overlap A
            if bx2 <= ax1 or bx1 >= ax2:
                continue
            # B's top must sit inside A's title strip
            if by1 < ay1 or by1 > ay2:
                continue
            # Ignore if B wraps A entirely (B is the parent, not child)
            if bx1 <= ax1 and bx2 >= ax2 and by1 <= ay1 and by2 >= ay2:
                continue
            # Violation: B's top edge crosses A's title strip
            # (only flag if B's top is strictly inside A's strip, not at its bottom edge)
            penetration = ay2 - by1
            if penetration > 5:  # B pokes into A's title by more than 5px
                title_clearance_violations.append(
                    f"'{id_b}' ({val_b!r:.30}) top edge at y={by1:.0f} penetrates "
                    f"'{id_a}' ({val_a!r:.30}) title strip (y={ay1:.0f}-{ay2:.0f}) "
                    f"by {penetration:.0f}px"
                )

    title_clearance_violations = list(dict.fromkeys(title_clearance_violations))
    if title_clearance_violations:
        fail(f"{len(title_clearance_violations)} nested container title clearances violated:")
        for tv in title_clearance_violations[:8]:
            print(f"      → {tv}")
        if len(title_clearance_violations) > 8:
            print(f"      ... and {len(title_clearance_violations) - 8} more")
    else:
        ok("All nested containers clear their parent's title strip")

    # --- Anti-Pattern 19: Canvas oversized for content ---
    # The mxGraphModel pageWidth/Height should fit the content bounds + ~40px
    # margin. A 1600×900 canvas with 4 icons in the middle is empty.
    print("\n  Canvas fit-to-content:")
    model = tree.getroot().find(".//mxGraphModel")
    if model is not None and vertices:
        try:
            page_w = int(model.get("pageWidth", 0))
            page_h = int(model.get("pageHeight", 0))
        except ValueError:
            page_w = page_h = 0
        if page_w and page_h:
            xs = [id_to_geo[v.get("id")]["x"] for v in vertices if id_to_geo.get(v.get("id"))]
            ys = [id_to_geo[v.get("id")]["y"] for v in vertices if id_to_geo.get(v.get("id"))]
            right = [id_to_geo[v.get("id")]["x"] + id_to_geo[v.get("id")]["width"]
                     for v in vertices if id_to_geo.get(v.get("id"))]
            bot = [id_to_geo[v.get("id")]["y"] + id_to_geo[v.get("id")]["height"]
                   for v in vertices if id_to_geo.get(v.get("id"))]
            if xs and ys:
                content_w = max(right) - min(xs)
                content_h = max(bot) - min(ys)
                # Target canvas: content + 80px total margin (40 each side).
                target_w = content_w + 80
                target_h = content_h + 80
                w_waste = page_w - target_w
                h_waste = page_h - target_h
                # Allow 200px slack — above that, it's a waste
                if w_waste > 200 or h_waste > 200:
                    warn(
                        f"Canvas {page_w}×{page_h} is larger than content ({content_w:.0f}×{content_h:.0f} + 80px margin = "
                        f"{target_w:.0f}×{target_h:.0f}). "
                        f"Slack: {w_waste:.0f}×{h_waste:.0f} px. "
                        f"Consider shrinking pageWidth/pageHeight to fit content."
                    )
                else:
                    ok(f"Canvas {page_w}×{page_h} fits content {content_w:.0f}×{content_h:.0f} + margin")
        else:
            ok("Canvas check skipped (no pageWidth/pageHeight)")
    else:
        ok("Canvas check skipped (no model or no vertices)")

    # --- Anti-Pattern 20: Stretched spacing between connected icons ---
    # If two directly-connected icons have >200px gap and nothing else between
    # them, the layout is stretched.
    print("\n  Inter-icon spacing (connected pairs):")
    stretch_violations = []
    id_to_geo_full = id_to_geo
    for e in edges:
        src_id = e.get("source")
        tgt_id = e.get("target")
        if not src_id or not tgt_id:
            continue
        sg = id_to_geo_full.get(src_id)
        tg = id_to_geo_full.get(tgt_id)
        if not sg or not tg:
            continue
        # Only consider icon-to-icon (both should be leaf vertex cells, not containers)
        if src_id in group_ids or tgt_id in group_ids:
            continue
        # Only small icons (not canvas-spanning text)
        if sg["width"] > 120 or tg["width"] > 120:
            continue
        # Compute edge-to-edge gap (not center-to-center)
        # Horizontal if Y centers align within 40px
        s_cx, s_cy = sg["x"] + sg["width"]/2, sg["y"] + sg["height"]/2
        t_cx, t_cy = tg["x"] + tg["width"]/2, tg["y"] + tg["height"]/2
        if abs(s_cy - t_cy) < 40:  # horizontal edge
            gap = abs(t_cx - s_cx) - (sg["width"]/2 + tg["width"]/2)
            if gap > 200:
                stretch_violations.append(
                    f"'{src_id}' → '{tgt_id}' horizontal gap {gap:.0f}px (want ≤200px)"
                )
        elif abs(s_cx - t_cx) < 40:  # vertical edge
            gap = abs(t_cy - s_cy) - (sg["height"]/2 + tg["height"]/2)
            if gap > 200:
                stretch_violations.append(
                    f"'{src_id}' → '{tgt_id}' vertical gap {gap:.0f}px (want ≤200px)"
                )

    stretch_violations = list(dict.fromkeys(stretch_violations))
    if stretch_violations:
        warn(f"{len(stretch_violations)} connected icon pairs are stretched:")
        for sv in stretch_violations[:8]:
            print(f"      → {sv}")
    else:
        ok("All connected icons are within 200px gap")

    # --- Anti-Pattern 21: Edge labels used instead of callout ellipses ---
    # The AWS deck (slide 18) specifies numbered callouts as filled circles with
    # bold white numbers. Using edgeLabel elements (inline text on edges with
    # labelBackgroundColor) is a common LLM mistake — they look like badges, not
    # the official callout style.
    print("\n  Edge label vs callout check:")
    edge_label_violations = []

    for e in edges:
        eid = e.get("id", "?")
        # Check for child mxCell elements that are edge labels (connectable=0, parent=edge)
        # These are inline labels attached to the edge itself.
        pass  # handled below via parent scan

    # Scan all cells for edgeLabel-style elements: cells whose parent is an edge
    # and whose style contains "edgeLabel" or "labelBackgroundColor"
    edge_ids = {e.get("id") for e in edges}
    for c in cells:
        cid = c.get("id", "?")
        parent_id = c.get("parent", "")
        style_str = c.get("style", "") or ""
        value = (c.get("value", "") or "").strip()

        # Skip non-edge-label cells
        if parent_id not in edge_ids:
            continue

        # This cell is parented to an edge — it's an edge label
        style = parse_style(style_str)
        is_edge_label = (
            "edgeLabel" in style_str
            or style.get("labelBackgroundColor") is not None
            or c.get("connectable") == "0"
        )

        if not is_edge_label:
            continue

        # Check if the value looks like a step number (digits only)
        clean_val = value.rstrip(".")
        if clean_val.isdigit():
            edge_label_violations.append(
                f"Edge '{parent_id}' has numbered label '{value}' as an edgeLabel "
                f"(id='{cid}'). Use a separate callout ellipse "
                f"(fillColor=#232F3E, white bold number) positioned at the arrow "
                f"midpoint instead."
            )

    if edge_label_violations:
        fail(
            f"{len(edge_label_violations)} edges use edgeLabel for step numbers "
            f"instead of proper callout ellipses:"
        )
        for elv in edge_label_violations[:8]:
            print(f"      → {elv}")
        if len(edge_label_violations) > 8:
            print(f"      ... and {len(edge_label_violations) - 8} more")
    else:
        ok("No edgeLabel step numbers — callout ellipses used correctly")

    # --- AWS-Official Fidelity (moved to validate_aws_fidelity.py to
    # keep each file under the 100 KB tool ceiling) ---
    import importlib.util
    import os
    _mod_path = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                             "validate_aws_fidelity.py")
    _spec = importlib.util.spec_from_file_location(
        "validate_aws_fidelity", _mod_path)
    _fidelity = importlib.util.module_from_spec(_spec)
    _spec.loader.exec_module(_fidelity)

    class _Helpers:
        parse_style = staticmethod(parse_style)
        fail = staticmethod(fail)
        warn = staticmethod(warn)
        ok = staticmethod(ok)

    _fidelity.run_aws_fidelity_checks(vertices, edges, id_to_geo, _Helpers)

    # =========================================================
    print(f"\n{'='*60}")
    print(f"  Results: {fails} failures, {warns} warnings")
    if fails > 0:
        print(f"  Status: {FAIL} — fix all failures before exporting")
    elif warns > 0:
        print(f"  Status: {WARN} — review warnings")
    else:
        print(f"  Status: {PASS} — diagram looks good!")
    print(f"{'='*60}\n")

    sys.exit(1 if fails > 0 else 0)


if __name__ == "__main__":
    main()
