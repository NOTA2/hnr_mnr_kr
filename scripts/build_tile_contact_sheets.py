#!/usr/bin/env python3

from __future__ import annotations

import argparse
import binascii
import json
import math
import struct
import zlib
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
REPORT = ROOT / "confirmed_data" / "image_inventory" / "global_tile_extraction" / "notes" / "global_tile_extraction_report.json"
OUT_DIR = ROOT / "confirmed_data" / "image_inventory" / "global_tile_extraction" / "contact_sheets"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="PGM tile preview contact sheet PNG를 생성합니다.")
    parser.add_argument("--thumb-width", type=int, default=128)
    parser.add_argument("--thumb-height", type=int, default=128)
    parser.add_argument("--columns", type=int, default=5)
    parser.add_argument("--batch-size", type=int, default=80)
    parser.add_argument("--raw-batch-size", type=int, default=100)
    return parser.parse_args()


def read_pgm(path: Path) -> tuple[int, int, bytes]:
    data = path.read_bytes()
    if not data.startswith(b"P5\n"):
        raise ValueError(f"not a raw PGM: {path}")
    cursor = 3
    while data[cursor:cursor + 1] == b"#":
        cursor = data.index(b"\n", cursor) + 1
    next_newline = data.index(b"\n", cursor)
    width, height = map(int, data[cursor:next_newline].split())
    cursor = next_newline + 1
    next_newline = data.index(b"\n", cursor)
    max_value = int(data[cursor:next_newline])
    if max_value != 255:
        raise ValueError(f"unsupported PGM max value {max_value}: {path}")
    pixels = data[next_newline + 1 :]
    return width, height, pixels


def scale_gray(src: bytes, width: int, height: int, out_w: int, out_h: int) -> bytes:
    out = bytearray(out_w * out_h)
    for y in range(out_h):
        sy = min(height - 1, int(y * height / out_h))
        src_row = sy * width
        dst_row = y * out_w
        for x in range(out_w):
            sx = min(width - 1, int(x * width / out_w))
            out[dst_row + x] = src[src_row + sx]
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
    payload = b"".join(
        [
            b"\x89PNG\r\n\x1a\n",
            png_chunk(b"IHDR", struct.pack(">IIBBBBB", width, height, 8, 0, 0, 0, 0)),
            png_chunk(b"IDAT", zlib.compress(bytes(rows), level=6)),
            png_chunk(b"IEND", b""),
        ]
    )
    path.write_bytes(payload)


def compose_sheet(items: list[dict], output: Path, *, thumb_w: int, thumb_h: int, columns: int) -> None:
    if not items:
        return
    rows = math.ceil(len(items) / columns)
    gap = 4
    width = columns * thumb_w + (columns - 1) * gap
    height = rows * thumb_h + (rows - 1) * gap
    sheet = bytearray([24] * (width * height))
    for idx, item in enumerate(items):
        pgm_path = ROOT / item["preview_path"]
        src_w, src_h, pixels = read_pgm(pgm_path)
        thumb = scale_gray(pixels, src_w, src_h, thumb_w, thumb_h)
        col = idx % columns
        row = idx // columns
        x0 = col * (thumb_w + gap)
        y0 = row * (thumb_h + gap)
        for y in range(thumb_h):
            dst = (y0 + y) * width + x0
            sheet[dst : dst + thumb_w] = thumb[y * thumb_w : (y + 1) * thumb_w]
    write_png_gray(output, width, height, bytes(sheet))


def batched(items: list[dict], size: int) -> list[list[dict]]:
    return [items[index : index + size] for index in range(0, len(items), size)]


def write_index(sheets: list[dict]) -> None:
    lines = ["# Tile Contact Sheets", ""]
    for sheet in sheets:
        lines.append(f"- `{sheet['kind']}` #{sheet['batch']}: `{sheet['path']}` ({sheet['count']} previews)")
    (OUT_DIR / "contact_sheets.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    (OUT_DIR / "contact_sheets.json").write_text(
        json.dumps(sheets, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )


def build_workspace_sheets(*, thumb_w: int, thumb_h: int, columns: int) -> list[dict]:
    workspace_root = ROOT / "confirmed_data" / "image_inventory" / "workspaces"
    workspace_sheets: list[dict] = []
    for report_path in sorted(workspace_root.glob("*/notes/*candidate_report.json")):
        report = json.loads(report_path.read_text(encoding="utf-8"))
        candidates = report.get("candidates", [])
        if not candidates:
            continue
        workspace = report_path.parent.parent
        contact_dir = workspace / "contact_sheets"
        contact_dir.mkdir(parents=True, exist_ok=True)
        output = contact_dir / "candidates.png"
        compose_sheet(candidates, output, thumb_w=thumb_w, thumb_h=thumb_h, columns=columns)
        entry = {
            "review_unit": report.get("review_unit"),
            "workspace": str(workspace.relative_to(ROOT)),
            "candidate_count": len(candidates),
            "path": str(output.relative_to(ROOT)),
        }
        workspace_sheets.append(entry)

    index_path = workspace_root / "workspace_contact_sheets.json"
    md_path = workspace_root / "workspace_contact_sheets.md"
    index_path.write_text(json.dumps(workspace_sheets, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    lines = ["# Workspace Contact Sheets", ""]
    for item in workspace_sheets:
        lines.append(
            f"- `{item['review_unit']}`: `{item['path']}` ({item['candidate_count']} candidates)"
        )
    md_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return workspace_sheets


def main() -> int:
    args = parse_args()
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    report = json.loads(REPORT.read_text(encoding="utf-8"))
    sheets: list[dict] = []

    lz77 = sorted(report["lz77"], key=lambda item: int(item["offset"]))
    raw = sorted(report["raw"], key=lambda item: int(item["offset"]))
    for batch_index, items in enumerate(batched(lz77, args.batch_size), start=1):
        output = OUT_DIR / f"lz77_contact_{batch_index:02d}.png"
        compose_sheet(items, output, thumb_w=args.thumb_width, thumb_h=args.thumb_height, columns=args.columns)
        sheets.append({"kind": "lz77", "batch": batch_index, "count": len(items), "path": str(output.relative_to(ROOT))})

    for batch_index, items in enumerate(batched(raw, args.raw_batch_size), start=1):
        output = OUT_DIR / f"raw_contact_{batch_index:02d}.png"
        compose_sheet(items, output, thumb_w=args.thumb_width, thumb_h=args.thumb_height, columns=args.columns)
        sheets.append({"kind": "raw", "batch": batch_index, "count": len(items), "path": str(output.relative_to(ROOT))})

    write_index(sheets)
    workspace_sheets = build_workspace_sheets(
        thumb_w=args.thumb_width,
        thumb_h=args.thumb_height,
        columns=args.columns,
    )
    print(f"sheets: {len(sheets)}")
    print(f"workspace sheets: {len(workspace_sheets)}")
    print(f"index : {OUT_DIR / 'contact_sheets.md'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
