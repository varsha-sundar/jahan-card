#!/usr/bin/env python3
"""
Build farewell-standalone.html — one HTML file you can email or open via file://
(images + notes work without a server).

Run from this folder:
  python3 build-standalone.py

Output: farewell-standalone.html (same directory)
"""

from __future__ import annotations

import base64
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent
OUT = ROOT / "farewell-standalone.html"


def data_uri(path: Path) -> str:
    raw = path.read_bytes()
    ext = path.suffix.lower()
    if ext in (".jpg", ".jpeg"):
        mime = "image/jpeg"
    elif ext == ".png":
        mime = "image/png"
    elif ext == ".webp":
        mime = "image/webp"
    elif ext == ".gif":
        mime = "image/gif"
    else:
        mime = "application/octet-stream"
    b64 = base64.standard_b64encode(raw).decode("ascii")
    return f"data:{mime};base64,{b64}"


def parse_opening_photos(team_text: str) -> list[dict[str, str]]:
    photos: list[dict[str, str]] = []
    parts = re.split(r"===\s*PHOTOS\s*===", team_text, maxsplit=1, flags=re.I)
    if len(parts) < 2:
        return photos
    block = parts[1]
    block = re.split(r"===\s*NOTES\s*===", block, maxsplit=1, flags=re.I)[0]
    for line in block.splitlines():
        line = line.strip()
        if not line or line.startswith("#") or line.startswith("==="):
            continue
        cols = [c.strip() for c in line.split("|")]
        if cols[0]:
            photos.append(
                {
                    "src": cols[0],
                    "alt": cols[1] if len(cols) > 1 else "",
                    "caption": cols[2] if len(cols) > 2 else "",
                }
            )
    return photos


def main() -> None:
    html_path = ROOT / "index.html"
    css_path = ROOT / "css" / "styles.css"
    embed_path = ROOT / "embedded-notes.js"
    team_path = ROOT / "team-source.txt"

    html = html_path.read_text(encoding="utf-8")
    css = css_path.read_text(encoding="utf-8")
    embed = embed_path.read_text(encoding="utf-8")
    team = team_path.read_text(encoding="utf-8")

    opening = []
    for entry in parse_opening_photos(team):
        rel = (ROOT / entry["src"].replace("\\", "/").lstrip("/")).resolve()
        if not rel.is_file():
            print(f"Warning: skip missing file for team-source line: {entry['src']}")
            continue
        opening.append(
            {
                "src": data_uri(rel),
                "alt": entry.get("alt") or "",
                "caption": (entry.get("caption") or "").strip(),
            }
        )

    photos_dir = ROOT / "photos"
    path_to_uri: dict[str, str] = {}
    if photos_dir.is_dir():
        for f in sorted(photos_dir.iterdir()):
            if f.suffix.lower() not in (".jpg", ".jpeg", ".png", ".webp", ".gif"):
                continue
            key = "photos/" + f.name
            path_to_uri[key] = data_uri(f)

    html = html.replace(
        '<link rel="stylesheet" href="css/styles.css" />',
        "<style>\n" + css + "\n    </style>",
        1,
    )
    html = html.replace(
        '<script src="embedded-notes.js"></script>',
        "<script>\n" + embed + "\n    </script>",
        1,
    )

    inject = (
        "<script>window.__STANDALONE_PHOTOS__="
        + json.dumps(opening, ensure_ascii=False)
        + ";</script>\n    "
    )
    marker = '    <script>\n      (function () {'
    if marker not in html:
        raise SystemExit("Could not find main script marker in index.html")
    html = html.replace(marker, inject + marker, 1)

    for path_key, uri in path_to_uri.items():
        html = html.replace(json.dumps(path_key), json.dumps(uri))

    OUT.write_text(html, encoding="utf-8")
    size_mb = OUT.stat().st_size / (1024 * 1024)
    print(f"Wrote {OUT} ({size_mb:.1f} MB)")
    print("Share this single file; open it in a browser (double-click or drag into Chrome).")


if __name__ == "__main__":
    main()
