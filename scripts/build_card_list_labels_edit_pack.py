#!/usr/bin/env python3
"""Build a focused edit pack for the card list ID/POWER labels."""

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
    / "no_entry8_latest_ss3"
    / "frame_009730_bg1_rle_003A3540"
)
SOURCE_IMAGE = SOURCE_DIR / "matched_tiles_screen_order.png"
SOURCE_TILE_MAP = SOURCE_DIR / "tile_map.json"
OUT_DIR = ROOT / "confirmed_data" / "image_inventory" / "edit_packs" / "card_list_labels"

ITEM_ID = "image:rle_screen_order_focus:no_entry8_latest_ss3:frame_009730:bg1:003A3540:card_list_id_power"
OFFSET = 0x003A3540
SCALE = 4

# ID/POWER banners in the card list screen-order image.
CROP_TILE_MIN_X = 2
CROP_TILE_MAX_X = 12
CROP_TILE_MIN_Y = 0x0B
CROP_TILE_MAX_Y = 0x0C
CROP_X = CROP_TILE_MIN_X * 8
CROP_Y = CROP_TILE_MIN_Y * 8
CROP_W = (CROP_TILE_MAX_X - CROP_TILE_MIN_X + 1) * 8
CROP_H = (CROP_TILE_MAX_Y - CROP_TILE_MIN_Y + 1) * 8


def main() -> int:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    image = Image.open(SOURCE_IMAGE).convert("RGBA")
    tile_map = json.loads(SOURCE_TILE_MAP.read_text(encoding="utf-8"))

    crop = image.crop((CROP_X, CROP_Y, CROP_X + CROP_W, CROP_Y + CROP_H))
    source_path = OUT_DIR / "card_list_id_power__source.png"
    edit_path = OUT_DIR / "card_list_id_power__edit_4x.png"
    crop.save(source_path)
    crop.resize((CROP_W * SCALE, CROP_H * SCALE), Image.Resampling.NEAREST).save(edit_path)

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
        "focus_note": "Focused card list middle labels only: ID / POWER.",
    }
    tile_map_path = OUT_DIR / "card_list_id_power__tile_map.json"
    tile_map_path.write_text(json.dumps(focused_tile_map, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    manifest = {
        "item_id": ITEM_ID,
        "offset": OFFSET,
        "label": "카드 리스트 ID/POWER 라벨",
        "source_text": "ID / POWER",
        "suggested_korean": "ID / 파워",
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
        "tile_columns": CROP_TILE_MAX_X - CROP_TILE_MIN_X + 1,
        "tile_rows": CROP_TILE_MAX_Y - CROP_TILE_MIN_Y + 1,
        "replacement_payload_base": "current",
        "replacement_verify_source_noop": False,
        "matched_tile_count": len(matches),
        "upload_note": "이 PNG를 수정해 GUI에 업로드하면 0x003A3540 RLE 중 카드 리스트 ID/POWER 라벨 영역만 화면순 tile_map으로 적용한다.",
    }
    (OUT_DIR / "manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    (OUT_DIR / "README.md").write_text(
        "\n".join(
            [
                "# Card List ID/POWER Labels Edit Pack",
                "",
                "카드 리스트 중단의 ID / POWER 라벨만 분리한 편집용 PNG다.",
                "같은 0x003A3540 RLE 블록에 누적 적용되도록 current payload 기준으로 사용한다.",
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
