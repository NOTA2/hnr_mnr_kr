#!/usr/bin/env python3
"""Build a focused edit pack for the card detail page count label."""

from __future__ import annotations

import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT / ".vendor") not in sys.path:
    sys.path.insert(0, str(ROOT / ".vendor"))

from PIL import Image


SOURCE_DIR = (
    ROOT
    / "confirmed_data"
    / "image_inventory"
    / "runtime_rle_screen_order"
    / "current_review_ss6"
    / "frame_000006_bg1_rle_003A206C"
)
SOURCE_IMAGE = SOURCE_DIR / "matched_tiles_screen_order.png"
SOURCE_TILE_MAP = SOURCE_DIR / "tile_map.json"
OUT_DIR = ROOT / "confirmed_data" / "image_inventory" / "edit_packs" / "card_page_count"

ITEM_ID = "image:rle_screen_order_focus:current_review_ss6:frame_000006:bg1:003A206C:card_page_count"
OFFSET = 0x003A206C
SCALE = 4

# In the screen-order crop this 8x4 tile region contains the small card page
# counter frame and the "1枚目" text.
CROP_TILE_MIN_X = 2
CROP_TILE_MAX_X = 9
CROP_TILE_MIN_Y = 7
CROP_TILE_MAX_Y = 10
CROP_X = 16
CROP_Y = 56
CROP_W = (CROP_TILE_MAX_X - CROP_TILE_MIN_X + 1) * 8
CROP_H = (CROP_TILE_MAX_Y - CROP_TILE_MIN_Y + 1) * 8


def main() -> int:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    image = Image.open(SOURCE_IMAGE).convert("RGBA")
    crop = image.crop((CROP_X, CROP_Y, CROP_X + CROP_W, CROP_Y + CROP_H))
    source_path = OUT_DIR / "card_page_count__source.png"
    edit_path = OUT_DIR / "card_page_count__edit_4x.png"
    crop.save(source_path)
    crop.resize((CROP_W * SCALE, CROP_H * SCALE), Image.Resampling.NEAREST).save(edit_path)

    tile_map = json.loads(SOURCE_TILE_MAP.read_text(encoding="utf-8"))
    matches = [
        match
        for match in tile_map["matches"]
        if CROP_TILE_MIN_X <= int(match["screen_tile_x"]) <= CROP_TILE_MAX_X
        and CROP_TILE_MIN_Y <= int(match["screen_tile_y"]) <= CROP_TILE_MAX_Y
    ]
    focused_tile_map = {
        **tile_map,
        "crop_screen_tiles": {
            "min_x": CROP_TILE_MIN_X,
            "min_y": CROP_TILE_MIN_Y,
            "max_x": CROP_TILE_MAX_X,
            "max_y": CROP_TILE_MAX_Y,
        },
        "crop_pixels": {
            "x": CROP_X,
            "y": CROP_Y,
            "width": CROP_W,
            "height": CROP_H,
        },
        "matched_tile_count": len(matches),
        "matches": matches,
        "focus_note": "Focused card detail page count label: 1枚目.",
    }
    tile_map_path = OUT_DIR / "card_page_count_tile_map.json"
    tile_map_path.write_text(json.dumps(focused_tile_map, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    manifest = {
        "item_id": ITEM_ID,
        "offset": OFFSET,
        "label": "카드 상세 페이지 표기 1枚目",
        "source_text": "1枚目",
        "suggested_korean": "1장째",
        "source_path": str(source_path.relative_to(ROOT)),
        "editable_path": str(edit_path.relative_to(ROOT)),
        "tile_map_path": str(tile_map_path.relative_to(ROOT)),
        "source_screen_order_path": str(SOURCE_IMAGE.relative_to(ROOT)),
        "source_tile_map_path": str(SOURCE_TILE_MAP.relative_to(ROOT)),
        "rle_offset": OFFSET,
        "rle_offset_hex": f"0x{OFFSET:08X}",
        "width": CROP_W,
        "height": CROP_H,
        "scale": SCALE,
        "matched_tile_count": len(matches),
        "upload_note": "이 PNG를 수정해 GUI에 업로드하면 0x003A206C RLE 중 카드 상세 1枚目 영역만 화면순 tile_map으로 적용한다.",
    }
    (OUT_DIR / "manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    (OUT_DIR / "README.md").write_text(
        "\n".join(
            [
                "# Card Page Count Edit Pack",
                "",
                "카드 상세 화면의 작은 페이지 표기만 분리한 편집용 PNG다.",
                "원문: 1枚目",
                "권장 번역: 1장째",
                "",
                f"- source: `{manifest['source_path']}`",
                f"- edit: `{manifest['editable_path']}`",
                f"- tile_map: `{manifest['tile_map_path']}`",
            ]
        )
        + "\n",
        encoding="utf-8",
    )
    print(f"wrote {OUT_DIR}")
    print(f"matches {len(matches)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
