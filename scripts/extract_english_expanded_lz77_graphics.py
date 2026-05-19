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
from compare_english_patch_lz77_graphics import make_thumbnail, render_4bpp_pixels, write_contact_sheet
from gba_kor_tool.cli import decompress_lz77


DEFAULT_EN_ROM = (
    ROOT
    / "local_roms"
    / "english_patched"
    / "Fullmetal Alchemist Stray Rondo (English Patched v0.02).gba"
)
EN_LZ77_BLOCKS = ROOT / "confirmed_data" / "image_inventory" / "english_patch_diff" / "en_lz77_blocks.json"
OUT_DIR = ROOT / "confirmed_data" / "image_inventory" / "english_patch_diff" / "en_expanded_lz77"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="영문판 확장 영역 LZ77 그래픽 후보를 PNG/contact sheet 로 추출합니다.")
    parser.add_argument("--rom", type=Path, default=DEFAULT_EN_ROM)
    parser.add_argument("--blocks", type=Path, default=EN_LZ77_BLOCKS)
    parser.add_argument("--start-offset", type=lambda value: int(value, 0), default=0x800000)
    parser.add_argument("--min-size", type=int, default=0x400)
    parser.add_argument("--max-size", type=int, default=0x10000)
    parser.add_argument("--columns", type=int, default=32)
    parser.add_argument("--thumb-width", type=int, default=128)
    parser.add_argument("--thumb-height", type=int, default=128)
    parser.add_argument("--contact-columns", type=int, default=5)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    rom = args.rom.read_bytes()
    blocks = json.loads(args.blocks.read_text(encoding="utf-8"))
    blocks = [
        block
        for block in blocks
        if int(block["offset"]) >= args.start_offset
        and args.min_size <= int(block["decompressed_size"]) <= args.max_size
        and int(block["decompressed_size"]) % 32 == 0
    ]
    blocks.sort(key=lambda block: int(block["offset"]))

    png_dir = OUT_DIR / "png"
    notes_dir = OUT_DIR / "notes"
    png_dir.mkdir(parents=True, exist_ok=True)
    notes_dir.mkdir(parents=True, exist_ok=True)

    items: list[dict] = []
    for index, block in enumerate(blocks, start=1):
        offset = int(block["offset"])
        payload, consumed = decompress_lz77(rom, offset, max_output_size=4 * 1024 * 1024)
        width, height, pixels = render_4bpp_pixels(payload, columns=args.columns)
        stem = f"{index:03d}_off_{offset:08X}_size_{len(payload):06X}"
        png_path = png_dir / f"{stem}.png"
        write_png_gray(png_path, width, height, pixels)
        items.append(
            {
                "index": index,
                "offset": offset,
                "offset_hex": f"0x{offset:08X}",
                "compressed_size": consumed,
                "decompressed_size": len(payload),
                "png_path": str(png_path.relative_to(ROOT)),
                "thumb": make_thumbnail(width, height, pixels, args.thumb_width, args.thumb_height),
            }
        )

    # Reuse the paired contact helper by passing the same thumbnail on both sides,
    # which keeps the sheet writer simple while still giving compact previews.
    contact_items = [{**item, "jp_thumb": item["thumb"], "en_thumb": item["thumb"]} for item in items]
    contact_path = OUT_DIR / "expanded_lz77_contact.png"
    write_contact_sheet(
        contact_items,
        contact_path,
        thumb_w=args.thumb_width,
        thumb_h=args.thumb_height,
        columns=args.contact_columns,
    )

    report_items = [{key: value for key, value in item.items() if key != "thumb"} for item in items]
    report = {
        "rom": str(args.rom.relative_to(ROOT) if args.rom.is_relative_to(ROOT) else args.rom),
        "start_offset": args.start_offset,
        "count": len(items),
        "contact_sheet": str(contact_path.relative_to(ROOT)),
        "items": report_items,
    }
    report_path = notes_dir / "en_expanded_lz77_report.json"
    report_path.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    md_path = notes_dir / "en_expanded_lz77_report.md"
    lines = [
        "# English Expanded LZ77 Graphics",
        "",
        f"- count: `{len(items)}`",
        f"- contact sheet: `{report['contact_sheet']}`",
        "",
    ]
    for item in report_items:
        lines.append(
            f"- `{item['offset_hex']}` size=`{item['decompressed_size']}` png=`{item['png_path']}`"
        )
    md_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"count  : {len(items)}")
    print(f"contact: {contact_path}")
    print(f"report : {report_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
