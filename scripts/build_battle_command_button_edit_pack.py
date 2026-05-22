#!/usr/bin/env python3
"""Build edit PNGs for raw 4bpp battle bottom command button blocks."""

from __future__ import annotations

import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT / ".vendor") not in sys.path:
    sys.path.insert(0, str(ROOT / ".vendor"))

from PIL import Image, ImageDraw


ROM = ROOT / "patched_roms" / "current_review" / "hnr_localization_review.gba"
OUT_DIR = ROOT / "confirmed_data" / "image_inventory" / "edit_packs" / "battle_command_buttons"
TILE_BYTES = 32
RAW_BYTE_LENGTH = 0x180
TILE_COLUMNS = 6
WIDTH = TILE_COLUMNS * 8
HEIGHT = (RAW_BYTE_LENGTH // TILE_BYTES // TILE_COLUMNS) * 8
SCALE = 4


ITEMS = [
    {
        "item_id": "image:raw4bpp:003ABF5C",
        "offset": 0x003ABF5C,
        "label": "전투 하단 커맨드 こうげき",
        "source_text": "こうげき",
        "suggested_korean": "공격",
        "stem": "01_battle_attack__003ABF5C",
    },
    {
        "item_id": "image:raw4bpp:003AC0DC",
        "offset": 0x003AC0DC,
        "label": "전투 하단 커맨드 てちょう",
        "source_text": "てちょう",
        "suggested_korean": "수첩",
        "stem": "02_battle_notebook__003AC0DC",
    },
    {
        "item_id": "image:raw4bpp:003AC25C",
        "offset": 0x003AC25C,
        "label": "전투 하단 커맨드 れんせい",
        "source_text": "れんせい",
        "suggested_korean": "연성",
        "stem": "03_battle_alchemy__003AC25C",
    },
    {
        "item_id": "image:raw4bpp:003AC3DC",
        "offset": 0x003AC3DC,
        "label": "전투 하단 커맨드 アイテム",
        "source_text": "アイテム",
        "suggested_korean": "아이템",
        "stem": "04_battle_item__003AC3DC",
    },
    {
        "item_id": "image:raw4bpp:003AC55C",
        "offset": 0x003AC55C,
        "label": "전투 하단 커맨드 ひっさつ",
        "source_text": "ひっさつ",
        "suggested_korean": "필살기",
        "stem": "05_battle_special__003AC55C",
    },
]


def raw_4bpp_to_image(raw: bytes) -> Image.Image:
    image = Image.new("L", (WIDTH, HEIGHT), 0)
    pixels = image.load()
    tile_count = RAW_BYTE_LENGTH // TILE_BYTES
    for tile_index in range(tile_count):
        tile_x = (tile_index % TILE_COLUMNS) * 8
        tile_y = (tile_index // TILE_COLUMNS) * 8
        tile = raw[tile_index * TILE_BYTES : tile_index * TILE_BYTES + TILE_BYTES]
        for y in range(8):
            for pair in range(4):
                byte = tile[y * 4 + pair]
                pixels[tile_x + pair * 2, tile_y + y] = (byte & 0x0F) * 17
                pixels[tile_x + pair * 2 + 1, tile_y + y] = (byte >> 4) * 17
    return image


def build_contact_sheet(manifest: list[dict]) -> str:
    thumbs: list[Image.Image] = []
    for item in manifest:
        image = Image.open(ROOT / item["editable_path"]).convert("RGB")
        canvas = Image.new("RGB", (image.width, image.height + 34), (16, 16, 18))
        canvas.paste(image, (0, 0))
        draw = ImageDraw.Draw(canvas)
        draw.text(
            (4, image.height + 6),
            f"{item['source_text']} -> {item['suggested_korean']}  0x{item['offset']:08X}",
            fill=(240, 240, 240),
        )
        thumbs.append(canvas)
    sheet_w = max(thumb.width for thumb in thumbs)
    sheet_h = sum(thumb.height for thumb in thumbs)
    sheet = Image.new("RGB", (sheet_w, sheet_h), (8, 8, 10))
    y = 0
    for thumb in thumbs:
        sheet.paste(thumb, (0, y))
        y += thumb.height
    out = OUT_DIR / "battle_command_buttons_contact_sheet.png"
    sheet.save(out)
    return str(out.relative_to(ROOT))


def main() -> int:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    rom = ROM.read_bytes()
    manifest: list[dict] = []
    for item in ITEMS:
        offset = item["offset"]
        raw = rom[offset : offset + RAW_BYTE_LENGTH]
        if len(raw) != RAW_BYTE_LENGTH:
            raise ValueError(f"short raw block at 0x{offset:08X}")

        raw_path = OUT_DIR / f"{item['stem']}.bin"
        source_path = OUT_DIR / f"{item['stem']}__source.png"
        edit_path = OUT_DIR / f"{item['stem']}__edit_4x.png"
        raw_path.write_bytes(raw)
        source = raw_4bpp_to_image(raw)
        source.save(source_path)
        source.resize((WIDTH * SCALE, HEIGHT * SCALE), Image.Resampling.NEAREST).save(edit_path)
        manifest.append(
            {
                **item,
                "raw_path": str(raw_path.relative_to(ROOT)),
                "source_path": str(source_path.relative_to(ROOT)),
                "editable_path": str(edit_path.relative_to(ROOT)),
                "raw_byte_length": RAW_BYTE_LENGTH,
                "tile_columns": TILE_COLUMNS,
                "width": WIDTH,
                "height": HEIGHT,
                "scale": SCALE,
                "upload_note": "이 PNG를 수정해 같은 GUI 항목에 업로드하면 raw 4bpp 타일 0x180바이트를 같은 오프셋에 직접 적용한다.",
            }
        )

    contact_sheet = build_contact_sheet(manifest)
    (OUT_DIR / "manifest.json").write_text(
        json.dumps(
            {
                "source_rom": str(ROM.relative_to(ROOT)),
                "raw_byte_length": RAW_BYTE_LENGTH,
                "tile_columns": TILE_COLUMNS,
                "width": WIDTH,
                "height": HEIGHT,
                "contact_sheet": contact_sheet,
                "items": manifest,
            },
            ensure_ascii=False,
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )
    lines = [
        "# Battle Command Button Edit Pack",
        "",
        "전투 하단 커맨드 버튼의 raw 4bpp 타일 블록이다.",
        "각 블록은 48x16px, 6x2 tiles, 0x180 bytes이며 GUI 업로드 시 같은 오프셋에 직접 적용된다.",
        "",
    ]
    for item in manifest:
        lines.append(
            f"- `{Path(item['editable_path']).name}`: {item['source_text']} -> {item['suggested_korean']} / 0x{item['offset']:08X}"
        )
    (OUT_DIR / "README.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"wrote {OUT_DIR}")
    print(f"items {len(manifest)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
