#!/usr/bin/env python3
"""Render RLE candidates with several tile-column layouts for human review."""

from __future__ import annotations

import argparse
import binascii
import json
import math
import struct
import zlib
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_REPORT = ROOT / "confirmed_data/image_inventory/rle_tile_extraction/notes/rle_tile_extraction_report.json"
DEFAULT_OUT_DIR = ROOT / "confirmed_data/image_inventory/rle_tile_extraction/layout_variant_sheets"
TILE_SIZE = 32


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--report", type=Path, default=DEFAULT_REPORT)
    parser.add_argument("--out-dir", type=Path, default=DEFAULT_OUT_DIR)
    parser.add_argument("--batch-size", type=int, default=24)
    parser.add_argument("--candidate-columns", type=int, default=3)
    parser.add_argument("--layouts", default="16,32,64,128")
    parser.add_argument("--thumb-width", type=int, default=192)
    parser.add_argument("--thumb-height", type=int, default=112)
    parser.add_argument("--min-size", type=lambda x: int(x, 0), default=0x200)
    return parser.parse_args()


def read_4bpp_tiles(path: Path) -> bytes:
    data = path.read_bytes()
    return data[: len(data) - (len(data) % TILE_SIZE)]


def render_4bpp_gray(data: bytes, *, columns: int) -> tuple[int, int, bytes]:
    tile_count = len(data) // TILE_SIZE
    rows = max(1, math.ceil(tile_count / columns))
    width = columns * 8
    height = rows * 8
    pixels = bytearray(width * height)
    for tile_index in range(tile_count):
        tile_x = (tile_index % columns) * 8
        tile_y = (tile_index // columns) * 8
        tile = data[tile_index * TILE_SIZE : tile_index * TILE_SIZE + TILE_SIZE]
        for y in range(8):
            row = tile[y * 4 : y * 4 + 4]
            for pair_index, byte in enumerate(row):
                pos = (tile_y + y) * width + tile_x + pair_index * 2
                pixels[pos] = (byte & 0x0F) * 17
                pixels[pos + 1] = (byte >> 4) * 17
    return width, height, bytes(pixels)


def scale_gray(src: bytes, width: int, height: int, out_w: int, out_h: int) -> bytes:
    out = bytearray(out_w * out_h)
    for y in range(out_h):
        sy = min(height - 1, int(y * height / out_h))
        for x in range(out_w):
            sx = min(width - 1, int(x * width / out_w))
            out[y * out_w + x] = src[sy * width + sx]
    return bytes(out)


def png_chunk(kind: bytes, payload: bytes) -> bytes:
    return (
        struct.pack(">I", len(payload))
        + kind
        + payload
        + struct.pack(">I", binascii.crc32(kind + payload) & 0xFFFFFFFF)
    )


def write_png_gray(path: Path, width: int, height: int, pixels: bytes) -> None:
    rows = bytearray()
    for y in range(height):
        rows.append(0)
        rows.extend(pixels[y * width : (y + 1) * width])
    path.write_bytes(
        b"".join(
            [
                b"\x89PNG\r\n\x1a\n",
                png_chunk(b"IHDR", struct.pack(">IIBBBBB", width, height, 8, 0, 0, 0, 0)),
                png_chunk(b"IDAT", zlib.compress(bytes(rows), level=6)),
                png_chunk(b"IEND", b""),
            ]
        )
    )


def draw_border(canvas: bytearray, width: int, x: int, y: int, w: int, h: int, color: int = 72) -> None:
    for xx in range(x, x + w):
        if 0 <= xx < width:
            canvas[y * width + xx] = color
            canvas[(y + h - 1) * width + xx] = color
    for yy in range(y, y + h):
        canvas[yy * width + x] = color
        canvas[yy * width + x + w - 1] = color


def compose_candidate_variants(item: dict, layouts: list[int], *, thumb_w: int, thumb_h: int) -> tuple[int, int, bytes]:
    raw_path = ROOT / item["raw_path"]
    data = read_4bpp_tiles(raw_path)
    gap = 4
    width = len(layouts) * thumb_w + (len(layouts) - 1) * gap
    height = thumb_h
    canvas = bytearray([18] * width * height)
    for layout_index, columns in enumerate(layouts):
        src_w, src_h, pixels = render_4bpp_gray(data, columns=columns)
        thumb = scale_gray(pixels, src_w, src_h, thumb_w, thumb_h)
        x0 = layout_index * (thumb_w + gap)
        for y in range(thumb_h):
            canvas[y * width + x0 : y * width + x0 + thumb_w] = thumb[y * thumb_w : y * thumb_w + thumb_w]
        draw_border(canvas, width, x0, 0, thumb_w, thumb_h)
    return width, height, bytes(canvas)


def batched(items: list[dict], size: int) -> list[list[dict]]:
    return [items[index : index + size] for index in range(0, len(items), size)]


def compose_sheet(items: list[dict], output: Path, layouts: list[int], *, thumb_w: int, thumb_h: int, candidate_columns: int) -> None:
    gap = 8
    cand_w = len(layouts) * thumb_w + (len(layouts) - 1) * 4
    cand_h = thumb_h
    rows = math.ceil(len(items) / candidate_columns)
    width = candidate_columns * cand_w + (candidate_columns - 1) * gap
    height = rows * cand_h + (rows - 1) * gap
    sheet = bytearray([10] * width * height)
    for index, item in enumerate(items):
        cand_width, cand_height, cand = compose_candidate_variants(item, layouts, thumb_w=thumb_w, thumb_h=thumb_h)
        x0 = (index % candidate_columns) * (cand_w + gap)
        y0 = (index // candidate_columns) * (cand_h + gap)
        for y in range(cand_height):
            dst = (y0 + y) * width + x0
            sheet[dst : dst + cand_width] = cand[y * cand_width : y * cand_width + cand_width]
    write_png_gray(output, width, height, bytes(sheet))


def main() -> int:
    args = parse_args()
    out_dir = args.out_dir.resolve()
    out_dir.mkdir(parents=True, exist_ok=True)
    layouts = [int(part) for part in args.layouts.split(",") if part.strip()]
    report = json.loads(args.report.resolve().read_text(encoding="utf-8"))
    blocks = [
        item
        for item in report.get("blocks", [])
        if int(item.get("decompressed_size", 0)) >= args.min_size
    ]
    blocks.sort(key=lambda item: int(item["offset"]))

    sheets = []
    for batch_index, items in enumerate(batched(blocks, args.batch_size), start=1):
        output = out_dir / f"rle_layout_variants_{batch_index:03d}.png"
        compose_sheet(
            items,
            output,
            layouts,
            thumb_w=args.thumb_width,
            thumb_h=args.thumb_height,
            candidate_columns=args.candidate_columns,
        )
        sheets.append(
            {
                "batch": batch_index,
                "count": len(items),
                "layouts": layouts,
                "first_offset": int(items[0]["offset"]),
                "last_offset": int(items[-1]["offset"]),
                "first_offset_hex": f"0x{int(items[0]['offset']):08X}",
                "last_offset_hex": f"0x{int(items[-1]['offset']):08X}",
                "path": str(output.relative_to(ROOT)),
                "candidates": [
                    {
                        "index": item["index"],
                        "offset": int(item["offset"]),
                        "decompressed_size": int(item["decompressed_size"]),
                        "raw_path": item["raw_path"],
                    }
                    for item in items
                ],
            }
        )

    (out_dir / "rle_layout_variant_sheets.json").write_text(
        json.dumps(sheets, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    lines = ["# RLE Layout Variant Sheets", "", f"- layouts: `{layouts}`", ""]
    for sheet in sheets:
        lines.append(
            f"- #{sheet['batch']}: `{sheet['path']}` "
            f"({sheet['count']} candidates, `{sheet['first_offset_hex']}`-`{sheet['last_offset_hex']}`)"
        )
    (out_dir / "rle_layout_variant_sheets.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"candidates: {len(blocks)}")
    print(f"sheets    : {len(sheets)}")
    print(f"index     : {out_dir / 'rle_layout_variant_sheets.md'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
