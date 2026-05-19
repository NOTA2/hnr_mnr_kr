#!/usr/bin/env python3
"""Build GUI-friendly contact sheets for all extracted RLE image candidates."""

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
DEFAULT_OUT_DIR = ROOT / "confirmed_data/image_inventory/rle_tile_extraction/contact_sheets"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--report", type=Path, default=DEFAULT_REPORT)
    parser.add_argument("--out-dir", type=Path, default=DEFAULT_OUT_DIR)
    parser.add_argument("--thumb-width", type=int, default=160)
    parser.add_argument("--thumb-height", type=int, default=96)
    parser.add_argument("--columns", type=int, default=5)
    parser.add_argument("--batch-size", type=int, default=60)
    parser.add_argument("--min-size", type=lambda x: int(x, 0), default=0)
    return parser.parse_args()


def read_pgm(path: Path) -> tuple[int, int, bytes]:
    data = path.read_bytes()
    if not data.startswith(b"P5\n"):
        raise ValueError(f"not a raw PGM: {path}")
    cursor = 3
    while data[cursor : cursor + 1] == b"#":
        cursor = data.index(b"\n", cursor) + 1
    next_newline = data.index(b"\n", cursor)
    width, height = map(int, data[cursor:next_newline].split())
    cursor = next_newline + 1
    next_newline = data.index(b"\n", cursor)
    max_value = int(data[cursor:next_newline])
    if max_value != 255:
        raise ValueError(f"unsupported PGM max value {max_value}: {path}")
    return width, height, data[next_newline + 1 :]


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


def batched(items: list[dict], size: int) -> list[list[dict]]:
    return [items[index : index + size] for index in range(0, len(items), size)]


def compose_sheet(items: list[dict], output: Path, *, thumb_w: int, thumb_h: int, columns: int) -> None:
    rows = math.ceil(len(items) / columns)
    gap = 4
    width = columns * thumb_w + (columns - 1) * gap
    height = rows * thumb_h + (rows - 1) * gap
    sheet = bytearray([24] * width * height)
    for index, item in enumerate(items):
        pgm_path = ROOT / item["preview_path"]
        src_w, src_h, pixels = read_pgm(pgm_path)
        thumb = scale_gray(pixels, src_w, src_h, thumb_w, thumb_h)
        x0 = (index % columns) * (thumb_w + gap)
        y0 = (index // columns) * (thumb_h + gap)
        for y in range(thumb_h):
            dst = (y0 + y) * width + x0
            sheet[dst : dst + thumb_w] = thumb[y * thumb_w : y * thumb_w + thumb_w]
    write_png_gray(output, width, height, bytes(sheet))


def write_reports(out_dir: Path, sheets: list[dict]) -> None:
    (out_dir / "rle_contact_sheets.json").write_text(
        json.dumps(sheets, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    lines = ["# RLE Contact Sheets", ""]
    for sheet in sheets:
        lines.append(
            f"- `{sheet['kind']}` #{sheet['batch']}: `{sheet['path']}` "
            f"({sheet['count']} candidates, offset `{sheet['first_offset_hex']}`-`{sheet['last_offset_hex']}`)"
        )
    (out_dir / "rle_contact_sheets.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    args = parse_args()
    out_dir = args.out_dir.resolve()
    out_dir.mkdir(parents=True, exist_ok=True)
    report = json.loads(args.report.resolve().read_text(encoding="utf-8"))
    blocks = [
        item
        for item in report.get("blocks", [])
        if int(item.get("decompressed_size", 0)) >= args.min_size
    ]
    blocks.sort(key=lambda item: int(item["offset"]))

    sheets: list[dict] = []
    for batch_index, items in enumerate(batched(blocks, args.batch_size), start=1):
        output = out_dir / f"rle_contact_{batch_index:03d}.png"
        compose_sheet(items, output, thumb_w=args.thumb_width, thumb_h=args.thumb_height, columns=args.columns)
        sheets.append(
            {
                "kind": "rle",
                "batch": batch_index,
                "count": len(items),
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
                        "preview_path": item["preview_path"],
                    }
                    for item in items
                ],
            }
        )

    write_reports(out_dir, sheets)
    print(f"rle candidates: {len(blocks)}")
    print(f"sheets        : {len(sheets)}")
    print(f"index         : {out_dir / 'rle_contact_sheets.md'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
