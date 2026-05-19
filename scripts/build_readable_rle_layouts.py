#!/usr/bin/env python3
"""Render selected RLE tile blocks as readable enlarged layout variants."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from build_rle_layout_variant_sheets import render_4bpp_gray, write_png_gray


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_REPORT = ROOT / "confirmed_data/image_inventory/rle_tile_extraction/notes/rle_tile_extraction_report.json"
DEFAULT_RAW_DIR = ROOT / "confirmed_data/image_inventory/rle_tile_extraction/rle_raw"
DEFAULT_OUT_DIR = ROOT / "confirmed_data/image_inventory/runtime_rle_patch_previews/single_rle_layouts"
TILE_SIZE = 32


DEFAULT_NAMES = {
    0x003ABB9C: "ok_yes_no",
    0x003AF23C: "alchemy_command",
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--report", type=Path, default=DEFAULT_REPORT)
    parser.add_argument("--raw-dir", type=Path, default=DEFAULT_RAW_DIR)
    parser.add_argument("--out-dir", type=Path, default=DEFAULT_OUT_DIR)
    parser.add_argument("--offset", action="append", default=[], help="RLE ROM offset, e.g. 0x003ABB9C. May be repeated.")
    parser.add_argument("--layouts", default="8,16,24,32")
    parser.add_argument("--scale", type=int, default=4)
    return parser.parse_args()


def scale_gray(src: bytes, width: int, height: int, factor: int) -> tuple[int, int, bytes]:
    out_w = width * factor
    out_h = height * factor
    out = bytearray(out_w * out_h)
    for y in range(out_h):
        sy = y // factor
        for x in range(out_w):
            sx = x // factor
            out[y * out_w + x] = src[sy * width + sx]
    return out_w, out_h, bytes(out)


def find_raw_path(report: dict, raw_dir: Path, offset: int) -> Path:
    for block in report.get("blocks", []):
        if int(block["offset"]) == offset:
            path = ROOT / block["raw_path"]
            if path.exists():
                return path
    matches = sorted(raw_dir.glob(f"*_off_{offset:08X}_*.bin"))
    if matches:
        return matches[0]
    raise FileNotFoundError(f"RLE raw block not found: 0x{offset:08X}")


def main() -> int:
    args = parse_args()
    report = json.loads(args.report.resolve().read_text(encoding="utf-8"))
    offsets = [int(value, 0) for value in args.offset] if args.offset else sorted(DEFAULT_NAMES)
    layouts = [int(part) for part in args.layouts.split(",") if part.strip()]
    out_dir = args.out_dir.resolve()
    out_dir.mkdir(parents=True, exist_ok=True)

    manifest = []
    for offset in offsets:
        raw_path = find_raw_path(report, args.raw_dir.resolve(), offset)
        name = DEFAULT_NAMES.get(offset, "rle")
        raw = raw_path.read_bytes()
        raw = raw[: len(raw) - (len(raw) % TILE_SIZE)]
        entry = {
            "offset": offset,
            "offset_hex": f"0x{offset:08X}",
            "raw_path": str(raw_path.relative_to(ROOT)),
            "layouts": [],
        }
        for columns in layouts:
            width, height, pixels = render_4bpp_gray(raw, columns=columns)
            base = out_dir / f"rle_{offset:08X}_{name}_{columns}cols.png"
            scaled = out_dir / f"rle_{offset:08X}_{name}_{columns}cols_{args.scale}x.png"
            write_png_gray(base, width, height, pixels)
            scaled_w, scaled_h, scaled_pixels = scale_gray(pixels, width, height, args.scale)
            write_png_gray(scaled, scaled_w, scaled_h, scaled_pixels)
            entry["layouts"].append(
                {
                    "columns": columns,
                    "path": str(base.relative_to(ROOT)),
                    "scaled_path": str(scaled.relative_to(ROOT)),
                }
            )
        manifest.append(entry)

    (out_dir / "readable_rle_layouts.json").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    print(f"offsets: {len(offsets)}")
    print(f"out: {out_dir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
