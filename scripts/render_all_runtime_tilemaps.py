#!/usr/bin/env python3
"""Render BG/OAM tilemap previews for every saved runtime capture directory."""

from __future__ import annotations

import argparse
from pathlib import Path

from render_runtime_tilemaps import ROOT, render_probe_dir


DEFAULT_CAPTURE_ROOT = ROOT / "confirmed_data/image_inventory/runtime_user_captures"
DEFAULT_OUT_DIR = ROOT / "confirmed_data/image_inventory/runtime_tilemaps"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--capture-root", type=Path, default=DEFAULT_CAPTURE_ROOT)
    parser.add_argument("--out-dir", type=Path, default=DEFAULT_OUT_DIR)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    capture_root = args.capture_root.resolve()
    out_root = args.out_dir.resolve()
    rendered = 0
    for probe_dir in sorted(path for path in capture_root.iterdir() if path.is_dir()):
        if not list(probe_dir.glob("frame_*_vram_06000000.bin")):
            continue
        out_dir = out_root / probe_dir.name
        entries = render_probe_dir(probe_dir, out_dir)
        (out_dir / "runtime_tilemaps.json").write_text(
            __import__("json").dumps(entries, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )
        rendered += 1
        print(f"{probe_dir.name}: {len(entries)} entries")
    print(f"rendered directories: {rendered}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
