#!/usr/bin/env python3
"""Compare same-offset GBA RLE graphics between JP/current and English patch ROMs."""

from __future__ import annotations

import argparse
import json
import math
from pathlib import Path

from build_rle_layout_variant_sheets import render_4bpp_gray, write_png_gray
from extract_rle_image_tiles import decompress_gba_rle


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_JP_ROM = ROOT / "patched_roms/current_review/hnr_localization_review_no_entry8_stable.gba"
DEFAULT_EN_ROM = (
    ROOT
    / "local_roms"
    / "english_patched"
    / "Fullmetal Alchemist Stray Rondo (English Patched v0.02).gba"
)
DEFAULT_RLE_REPORT = ROOT / "confirmed_data/image_inventory/rle_tile_extraction/notes/rle_tile_extraction_report.json"
DEFAULT_OUT_DIR = ROOT / "confirmed_data/image_inventory/english_patch_diff/rle_same_offset"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--jp-rom", type=Path, default=DEFAULT_JP_ROM)
    parser.add_argument("--en-rom", type=Path, default=DEFAULT_EN_ROM)
    parser.add_argument("--rle-report", type=Path, default=DEFAULT_RLE_REPORT)
    parser.add_argument("--out-dir", type=Path, default=DEFAULT_OUT_DIR)
    parser.add_argument("--columns", type=int, default=8)
    parser.add_argument("--scale", type=int, default=4)
    parser.add_argument("--contact-columns", type=int, default=2)
    parser.add_argument("--thumb-width", type=int, default=192)
    parser.add_argument("--thumb-height", type=int, default=112)
    parser.add_argument("--offset", action="append", default=[], help="Optional RLE offset filter, e.g. 0x003ABB9C")
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


def make_thumbnail(src: bytes, width: int, height: int, thumb_w: int, thumb_h: int) -> bytes:
    out = bytearray(thumb_w * thumb_h)
    if width <= 0 or height <= 0:
        return bytes(out)
    scale = min(thumb_w / width, thumb_h / height)
    scaled_w = max(1, int(width * scale))
    scaled_h = max(1, int(height * scale))
    x0 = (thumb_w - scaled_w) // 2
    y0 = (thumb_h - scaled_h) // 2
    for y in range(scaled_h):
        sy = min(height - 1, int(y / scale))
        for x in range(scaled_w):
            sx = min(width - 1, int(x / scale))
            out[(y0 + y) * thumb_w + x0 + x] = src[sy * width + sx]
    return bytes(out)


def write_contact_sheet(items: list[dict], output: Path, *, thumb_w: int, thumb_h: int, columns: int) -> None:
    if not items:
        write_png_gray(output, 1, 1, b"\x00")
        return
    cell_w = thumb_w * 2
    cell_h = thumb_h
    rows = math.ceil(len(items) / columns)
    width = cell_w * columns
    height = cell_h * rows
    canvas = bytearray(width * height)
    for index, item in enumerate(items):
        x0 = (index % columns) * cell_w
        y0 = (index // columns) * cell_h
        for side, key in enumerate(("jp_thumb", "en_thumb")):
            thumb = item[key]
            side_x = x0 + side * thumb_w
            for y in range(thumb_h):
                src = y * thumb_w
                dst = (y0 + y) * width + side_x
                canvas[dst : dst + thumb_w] = thumb[src : src + thumb_w]
    write_png_gray(output, width, height, bytes(canvas))


def write_rendered(raw: bytes, output: Path, *, columns: int, scale: int) -> tuple[int, int, bytes, str, str]:
    width, height, pixels = render_4bpp_gray(raw, columns=columns)
    write_png_gray(output, width, height, pixels)
    scaled_w, scaled_h, scaled_pixels = scale_gray(pixels, width, height, scale)
    scaled = output.with_name(output.stem + f"_{scale}x.png")
    write_png_gray(scaled, scaled_w, scaled_h, scaled_pixels)
    return width, height, pixels, str(output.relative_to(ROOT)), str(scaled.relative_to(ROOT))


def block_offsets(report_path: Path, filters: list[str]) -> list[int]:
    if filters:
        return sorted({int(value, 0) for value in filters})
    report = json.loads(report_path.read_text(encoding="utf-8"))
    return [int(block["offset"]) for block in report.get("blocks", [])]


def main() -> int:
    args = parse_args()
    jp_rom = args.jp_rom.resolve().read_bytes()
    en_rom = args.en_rom.resolve().read_bytes()
    out_dir = args.out_dir.resolve()
    jp_dir = out_dir / "jp_png"
    en_dir = out_dir / "en_png"
    notes_dir = out_dir / "notes"
    for path in (jp_dir, en_dir, notes_dir):
        path.mkdir(parents=True, exist_ok=True)

    changed = []
    compared = 0
    skipped = 0
    for offset in block_offsets(args.rle_report.resolve(), args.offset):
        jp = decompress_gba_rle(jp_rom, offset, max_output_size=0x400000)
        en = decompress_gba_rle(en_rom, offset, max_output_size=0x400000)
        if not jp or not en:
            skipped += 1
            continue
        compared += 1
        jp_payload, jp_consumed = jp
        en_payload, en_consumed = en
        if jp_payload == en_payload:
            continue

        stem = f"off_{offset:08X}_size_{len(jp_payload):06X}_{args.columns}cols"
        jp_w, jp_h, jp_pixels, jp_png, jp_scaled = write_rendered(
            jp_payload,
            jp_dir / f"{stem}.png",
            columns=args.columns,
            scale=args.scale,
        )
        en_w, en_h, en_pixels, en_png, en_scaled = write_rendered(
            en_payload,
            en_dir / f"{stem}.png",
            columns=args.columns,
            scale=args.scale,
        )
        changed.append(
            {
                "offset": offset,
                "offset_hex": f"0x{offset:08X}",
                "jp_consumed": jp_consumed,
                "en_consumed": en_consumed,
                "jp_decompressed_size": len(jp_payload),
                "en_decompressed_size": len(en_payload),
                "jp_png": jp_png,
                "jp_scaled_png": jp_scaled,
                "en_png": en_png,
                "en_scaled_png": en_scaled,
                "jp_thumb": make_thumbnail(jp_pixels, jp_w, jp_h, args.thumb_width, args.thumb_height),
                "en_thumb": make_thumbnail(en_pixels, en_w, en_h, args.thumb_width, args.thumb_height),
            }
        )

    contact = out_dir / f"changed_rle_{args.columns}cols_contact.png"
    write_contact_sheet(
        changed,
        contact,
        thumb_w=args.thumb_width,
        thumb_h=args.thumb_height,
        columns=args.contact_columns,
    )
    report_items = [
        {key: value for key, value in item.items() if key not in {"jp_thumb", "en_thumb"}}
        for item in changed
    ]
    report = {
        "jp_rom": str(args.jp_rom),
        "en_rom": str(args.en_rom),
        "compared": compared,
        "changed_count": len(changed),
        "skipped": skipped,
        "columns": args.columns,
        "scale": args.scale,
        "contact_sheet": str(contact.relative_to(ROOT)),
        "items": report_items,
    }
    (notes_dir / "english_patch_rle_same_offset_diff.json").write_text(
        json.dumps(report, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    lines = [
        "# English Patch Same-Offset RLE Graphic Diff",
        "",
        f"- compared: `{compared}`",
        f"- changed: `{len(changed)}`",
        f"- skipped: `{skipped}`",
        f"- contact sheet: `{report['contact_sheet']}`",
        "",
    ]
    for item in report_items:
        lines.append(
            f"- `{item['offset_hex']}` jp=`{item['jp_decompressed_size']}` "
            f"en=`{item['en_decompressed_size']}` jp=`{item['jp_scaled_png']}` en=`{item['en_scaled_png']}`"
        )
    (notes_dir / "english_patch_rle_same_offset_diff.md").write_text("\n".join(lines) + "\n", encoding="utf-8")

    print(f"compared: {compared}")
    print(f"changed : {len(changed)}")
    print(f"contact : {contact}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
