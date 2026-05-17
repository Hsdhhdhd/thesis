#!/usr/bin/env python3
"""Validate the copied 5.17 Canvas PPT without needing a browser."""
from __future__ import annotations

from html.parser import HTMLParser
from pathlib import Path
import re
import shutil
import subprocess
import sys
import tempfile

CANVAS_DIR = Path(__file__).resolve().parent
MATERIALS_ROOT = CANVAS_DIR.parent
REPO_ROOT = MATERIALS_ROOT.parent
INDEX = CANVAS_DIR / "index.html"
EXPECTED_SLIDES = 28
ASSET_BASES = {
    "A": MATERIALS_ROOT / "02_图片素材" / "实际PPT已用图片",
    "G": MATERIALS_ROOT / "02_图片素材" / "生成图片_image2_可选",
}


def read_index() -> str:
    if not INDEX.exists():
        raise FileNotFoundError(f"Missing {INDEX}")
    return INDEX.read_text(encoding="utf-8")


def extract_script(html: str) -> str:
    match = re.search(r"<script>(?P<script>.*?)</script>", html, flags=re.S)
    if not match:
        raise ValueError("Could not find inline <script> block")
    return match.group("script")


def check_html(html: str) -> None:
    HTMLParser().feed(html)


def check_node_syntax(script: str) -> None:
    node = shutil.which("node")
    if not node:
        print("WARN: node not found; skipped JavaScript syntax check")
        return
    with tempfile.NamedTemporaryFile("w", encoding="utf-8", suffix=".js", delete=False) as handle:
        handle.write(script)
        temp_name = handle.name
    try:
        subprocess.run([node, "--check", temp_name], check=True)
    finally:
        Path(temp_name).unlink(missing_ok=True)


def check_slide_count(script: str) -> None:
    slide_count = len(re.findall(r"\{part:", script))
    if slide_count != EXPECTED_SLIDES:
        raise AssertionError(f"Expected {EXPECTED_SLIDES} slides, found {slide_count}")


def check_assets(script: str) -> None:
    refs = re.findall(r"\b([AG])\+'([^']+)'", script)
    if not refs:
        raise AssertionError("No 5.17 image asset references found")
    missing: list[Path] = []
    for prefix, filename in refs:
        path = ASSET_BASES[prefix] / filename
        if not path.exists():
            missing.append(path)
    if missing:
        formatted = "\n".join(f"- {path.relative_to(REPO_ROOT)}" for path in missing)
        raise FileNotFoundError(f"Missing image assets:\n{formatted}")


def main() -> int:
    html = read_index()
    script = extract_script(html)
    check_html(html)
    check_node_syntax(script)
    check_slide_count(script)
    check_assets(script)
    print(f"OK: {INDEX.relative_to(REPO_ROOT)} has {EXPECTED_SLIDES} slides and all referenced 5.17 assets exist")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        raise SystemExit(1)
