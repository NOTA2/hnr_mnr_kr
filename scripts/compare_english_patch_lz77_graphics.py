#!/usr/bin/env python3

from __future__ import annotations

import argparse
import json
import math
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
    sys.path.insert(0, str(ROOT / "scripts"))

from build_tile_contact_sheets import write_png_gray
from gba_kor_tool.cli import decompress_lz77


DEFAULT_JP_ROM = ROOT / "Hagane no Renkinjutsushi - Meisou no Rondo (Japan).gba"
DEFAULT_EN_ROM = (
    ROOT
    / "local_roms"
    / "english_patched"
    / "Fullmetal Alchemist Stray Rondo (English Patched v0.02).gba"
)
LZ77_BLOCKS = ROOT / "confirmed_data" / "image_inventory" / "lz77_blocks.json"
OUT_DIR = ROOT / "confirmed_data" / "image_inventory" / "english_patch_diff"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="일판/영문판 동일 오프셋 LZ77 그래픽 블록을 비교해 변경 후보만 PNG로 추출합니다."
    )
    parser.add_argument("--jp-rom", type=Path, default=DEFAULT_JP_ROM)
    parser.add_argument("--en-rom", type=Path, default=DEFAULT_EN_ROM)
    parser.add_argument("--columns", type=int, default=32)
    parser.add_argument("--thumb-width", type=int, default=128)
    parser.add_argument("--thumb-height", type=int, default=128)
    parser.add_argument("--contact-columns", type=int, default=3)
    parser.add_argument("--limit", type=int, default=0)
    return parser.parse_args()


def render_4bpp_pixels(data: bytes, *, columns: int) -> tuple[int, int, bytes]:
    usable = len(data) - (len(data) % 32)
    data = data[:usable]
    tile_count = usable // 32
    rows = max(1, math.ceil(tile_count / columns))
    width = columns * 8
    height = rows * 8
    image = bytearray(width * height)

    for tile_index in range(tile_count):
        tile_x = (tile_index % columns) * 8
        tile_y = (tile_index // columns) * 8
        tile = data[tile_index * 32 : tile_index * 32 + 32]
        for row in range(8):
            row_data = tile[row * 4 : row * 4 + 4]
            for pair_index, byte in enumerate(row_data):
                lo = byte & 0x0F
                hi = (byte >> 4) & 0x0F
                pos = (tile_y + row) * width + tile_x + pair_index * 2
                image[pos] = lo * 17
                image[pos + 1] = hi * 17
    return width, height, bytes(image)


def make_thumbnail(width: int, height: int, pixels: bytes, thumb_w: int, thumb_h: int) -> bytes:
    output = bytearray(thumb_w * thumb_h)
    if width <= 0 or height <= 0:
        return bytes(output)
    scale = min(thumb_w / width, thumb_h / height)
    scaled_w = max(1, int(width * scale))
    scaled_h = max(1, int(height * scale))
    x0 = (thumb_w - scaled_w) // 2
    y0 = (thumb_h - scaled_h) // 2
    for y in range(scaled_h):
        sy = min(height - 1, int(y / scale))
        for x in range(scaled_w):
            sx = min(width - 1, int(x / scale))
            output[(y0 + y) * thumb_w + x0 + x] = pixels[sy * width + sx]
    return bytes(output)


def write_contact_sheet(changed: list[dict], output_path: Path, *, thumb_w: int, thumb_h: int, columns: int) -> None:
    if not changed:
        write_png_gray(output_path, 1, 1, b"\x00")
        return
    cell_w = thumb_w * 2
    cell_h = thumb_h
    rows = math.ceil(len(changed) / columns)
    sheet_w = cell_w * columns
    sheet_h = cell_h * rows
    canvas = bytearray(sheet_w * sheet_h)
    for index, item in enumerate(changed):
        col = index % columns
        row = index // columns
        base_x = col * cell_w
        base_y = row * cell_h
        for side, key in enumerate(("jp_thumb", "en_thumb")):
            thumb = item[key]
            side_x = base_x + side * thumb_w
            for y in range(thumb_h):
                src = y * thumb_w
                dst = (base_y + y) * sheet_w + side_x
                canvas[dst : dst + thumb_w] = thumb[src : src + thumb_w]
    write_png_gray(output_path, sheet_w, sheet_h, bytes(canvas))


def load_blocks(limit: int) -> list[dict]:
    blocks = json.loads(LZ77_BLOCKS.read_text(encoding="utf-8"))
    blocks = [
        block
        for block in blocks
        if int(block.get("decompressed_size", 0)) >= 32
        and int(block.get("decompressed_size", 0)) % 32 == 0
    ]
    blocks.sort(key=lambda block: int(block["offset"]))
    if limit > 0:
        blocks = blocks[:limit]
    return blocks


def main() -> int:
    args = parse_args()
    jp_rom = args.jp_rom.read_bytes()
    en_rom = args.en_rom.read_bytes()
    (OUT_DIR / "jp_png").mkdir(parents=True, exist_ok=True)
    (OUT_DIR / "en_png").mkdir(parents=True, exist_ok=True)
    (OUT_DIR / "notes").mkdir(parents=True, exist_ok=True)

    changed: list[dict] = []
    skipped_invalid = 0
    compared = 0
    for block in load_blocks(args.limit):
        offset = int(block["offset"])
        try:
            jp_payload, jp_consumed = decompress_lz77(jp_rom, offset, max_output_size=4 * 1024 * 1024)
            en_payload, en_consumed = decompress_lz77(en_rom, offset, max_output_size=4 * 1024 * 1024)
        except Exception:
            skipped_invalid += 1
            continue
        compared += 1
        if jp_payload == en_payload:
            continue

        stem = f"off_{offset:08X}_size_{len(jp_payload):06X}"
        jp_w, jp_h, jp_pixels = render_4bpp_pixels(jp_payload, columns=args.columns)
        en_w, en_h, en_pixels = render_4bpp_pixels(en_payload, columns=args.columns)
        jp_png = OUT_DIR / "jp_png" / f"{stem}.png"
        en_png = OUT_DIR / "en_png" / f"{stem}.png"
        write_png_gray(jp_png, jp_w, jp_h, jp_pixels)
        write_png_gray(en_png, en_w, en_h, en_pixels)
        changed.append(
            {
                "offset": offset,
                "offset_hex": f"0x{offset:08X}",
                "jp_consumed": jp_consumed,
                "en_consumed": en_consumed,
                "jp_decompressed_size": len(jp_payload),
                "en_decompressed_size": len(en_payload),
                "jp_png": str(jp_png.relative_to(ROOT)),
                "en_png": str(en_png.relative_to(ROOT)),
                "jp_thumb": make_thumbnail(jp_w, jp_h, jp_pixels, args.thumb_width, args.thumb_height),
                "en_thumb": make_thumbnail(en_w, en_h, en_pixels, args.thumb_width, args.thumb_height),
            }
        )

    contact_path = OUT_DIR / "changed_lz77_contact.png"
    write_contact_sheet(
        changed,
        contact_path,
        thumb_w=args.thumb_width,
        thumb_h=args.thumb_height,
        columns=args.contact_columns,
    )

    report_items = [
        {key: value for key, value in item.items() if key not in {"jp_thumb", "en_thumb"}}
        for item in changed
    ]
    report = {
        "jp_rom": str(args.jp_rom.relative_to(ROOT) if args.jp_rom.is_relative_to(ROOT) else args.jp_rom),
        "en_rom": str(args.en_rom.relative_to(ROOT) if args.en_rom.is_relative_to(ROOT) else args.en_rom),
        "compared": compared,
        "changed_count": len(changed),
        "skipped_invalid": skipped_invalid,
        "contact_sheet": str(contact_path.relative_to(ROOT)),
        "items": report_items,
    }
    report_path = OUT_DIR / "notes" / "english_patch_lz77_diff_report.json"
    report_path.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    md_path = OUT_DIR / "notes" / "english_patch_lz77_diff_report.md"
    lines = [
        "# English Patch LZ77 Graphic Diff",
        "",
        f"- compared: `{compared}`",
        f"- changed: `{len(changed)}`",
        f"- skipped invalid: `{skipped_invalid}`",
        f"- contact sheet: `{report['contact_sheet']}`",
        "",
    ]
    for item in report_items:
        lines.append(
            f"- `{item['offset_hex']}` jp=`{item['jp_decompressed_size']}` "
            f"en=`{item['en_decompressed_size']}` jp_png=`{item['jp_png']}` en_png=`{item['en_png']}`"
        )
    md_path.write_text("\n".join(lines) + "\n", encoding="utf-8")

    print(f"compared: {compared}")
    print(f"changed : {len(changed)}")
    print(f"contact : {contact_path}")
    print(f"report  : {report_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
