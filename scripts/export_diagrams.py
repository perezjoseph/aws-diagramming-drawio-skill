#!/usr/bin/env python3
"""Export all .drawio files in a directory to SVG and PNG,
then post-process SVGs to fix light-dark() CSS bugs.

Usage: python export_diagrams.py [directory]
Default directory: static/
"""

import glob
import os
import re
import subprocess
import sys

DRAWIO = "drawio"


def find_drawio_binary() -> str:
    """Locate the draw.io CLI binary across platforms."""
    candidates = [
        "/Applications/draw.io.app/Contents/MacOS/draw.io",  # macOS
        os.path.expandvars(r"%LOCALAPPDATA%\Programs\draw.io\draw.io.exe"),  # Windows per-user
        os.path.expandvars(r"%PROGRAMFILES%\draw.io\draw.io.exe"),  # Windows system
        "/usr/bin/drawio",  # Linux deb
        "/snap/bin/drawio",  # Linux snap
    ]
    # Check PATH first
    for name in ("drawio", "draw.io"):
        from shutil import which
        if which(name):
            return name
    # Fall back to known install locations
    for path in candidates:
        if os.path.isfile(path):
            return path
    print("Error: draw.io CLI not found. Install it or add it to PATH.", file=sys.stderr)
    sys.exit(1)


def export_diagram(drawio_bin: str, src_file: str, out_dir: str) -> None:
    """Export a single .drawio file to SVG and PNG."""
    name = os.path.splitext(os.path.basename(src_file))[0]
    svg_out = os.path.join(out_dir, f"{name}.svg")
    png_out = os.path.join(out_dir, f"{name}.png")

    subprocess.run(
        [drawio_bin, "--export", "--format", "svg", "--embed-svg-images", "--output", svg_out, src_file],
        check=True,
    )
    subprocess.run(
        [drawio_bin, "--export", "--format", "png", "--output", png_out, src_file],
        check=True,
    )


def postprocess_svg(filepath: str) -> None:
    """Strip light-dark() CSS and color-scheme declarations from an SVG."""
    try:
        with open(filepath) as f:
            content = f.read()
    except OSError as e:
        print(f"Error reading '{filepath}': {e}", file=sys.stderr)
        raise

    content = re.sub(r"light-dark\((rgb\([^)]+\))\s*,\s*rgb\([^)]+\)\)", r"\1", content)
    content = re.sub(r"light-dark\(([^,()]+)\s*,\s*[^)]+\)", r"\1", content)
    content = re.sub(r"color-scheme:\s*[^;\"]*;?\s*", "", content)

    try:
        with open(filepath, "w") as f:
            f.write(content)
    except OSError as e:
        print(f"Error writing '{filepath}': {e}", file=sys.stderr)
        raise


def main() -> None:
    src_dir = sys.argv[1] if len(sys.argv) > 1 else "static"

    if not os.path.isdir(src_dir):
        print(f"Error: directory '{src_dir}' not found.", file=sys.stderr)
        sys.exit(1)

    drawio_bin = find_drawio_binary()
    drawio_files = sorted(glob.glob(os.path.join(src_dir, "*.drawio")))

    if not drawio_files:
        print(f"No .drawio files found in {src_dir}")
        return

    print(f"Exporting diagrams from {src_dir}...")
    for f in drawio_files:
        name = os.path.basename(f)
        print(f"  {name} -> SVG + PNG")
        export_diagram(drawio_bin, f, src_dir)

    print("Post-processing SVGs...")
    for svg in sorted(glob.glob(os.path.join(src_dir, "*.svg"))):
        postprocess_svg(svg)
        print(f"  Post-processed: {svg}")

    print("Done.")


if __name__ == "__main__":
    main()
