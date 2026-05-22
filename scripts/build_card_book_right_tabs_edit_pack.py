#!/usr/bin/env python3
"""Build a focused edit pack for the card book right-side category tabs."""

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
OUT_DIR = ROOT / "confirmed_data" / "image_inventory" / "edit_packs" / "card_book_right_tabs"

ITEM_ID = "image:rle_screen_order_focus:current_review_ss6:frame_000006:bg1:003A3540:book_right_tabs"
OFFSET = 0x003A3540
SCALE = 4

# The screen-order 0x003A3540 sheet is 17 tiles wide. The right tabs occupy
# tile columns 13-16 and rows 0-13; row 14 starts the vertical book spine.
CROP_TILE_MIN_X = 13
CROP_TILE_MAX_X = 16
CROP_TILE_MIN_Y = 0
CROP_TILE_MAX_Y = 13
CROP_X = CROP_TILE_MIN_X * 8
CROP_Y = CROP_TILE_MIN_Y * 8
CROP_W = (CROP_TILE_MAX_X - CROP_TILE_MIN_X + 1) * 8
CROP_H = (CROP_TILE_MAX_Y - CROP_TILE_MIN_Y + 1) * 8

TAB_DEFS = [
    {
        "key": "metal",
        "label_jp": "金属",
        "label_ko": "금속",
        "tile_min_y": 0,
        "tile_max_y": 3,
    },
    {
        "key": "stone",
        "label_jp": "石",
        "label_ko": "돌",
        "tile_min_y": 4,
        "tile_max_y": 5,
    },
    {
        "key": "nature",
        "label_jp": "自然",
        "label_ko": "자연",
        "tile_min_y": 6,
        "tile_max_y": 7,
    },
    {
        "key": "inorganic",
        "label_jp": "無機",
        "label_ko": "무기",
        "tile_min_y": 8,
        "tile_max_y": 9,
    },
]


def main() -> int:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    image = Image.open(SOURCE_IMAGE).convert("RGBA")
    crop = image.crop((CROP_X, CROP_Y, CROP_X + CROP_W, CROP_Y + CROP_H))
    source_path = OUT_DIR / "card_book_right_tabs__source.png"
    edit_path = OUT_DIR / "card_book_right_tabs__edit_4x.png"
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
        "focus_note": "Focused card book right-side tabs only: 金属 / 石 / 自然 / 無機.",
    }
    tile_map_path = OUT_DIR / "card_book_right_tabs_tile_map.json"
    tile_map_path.write_text(json.dumps(focused_tile_map, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    manifest = {
        "item_id": ITEM_ID,
        "offset": OFFSET,
        "label": "카드 책자 오른쪽 탭 金属/石/自然/無機",
        "source_text": "金属 / 石 / 自然 / 無機",
        "suggested_korean": "금속 / 돌 / 자연 / 무기",
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
        "upload_note": "이 PNG를 수정해 GUI에 업로드하면 0x003A3540 RLE 중 책자 오른쪽 탭 영역만 화면순 tile_map으로 적용한다.",
    }
    (OUT_DIR / "manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    (OUT_DIR / "README.md").write_text(
        "\n".join(
            [
                "# Card Book Right Tabs Edit Pack",
                "",
                "카드 책자 오른쪽 세로 탭 4개만 분리한 편집용 PNG다.",
                "원문: 金属 / 石 / 自然 / 無機",
                "권장 번역: 금속 / 돌 / 자연 / 무기",
                "",
                f"- source: `{manifest['source_path']}`",
                f"- edit: `{manifest['editable_path']}`",
                f"- tile_map: `{manifest['tile_map_path']}`",
            ]
        )
        + "\n",
        encoding="utf-8",
    )

    individual_dir = OUT_DIR / "individual_tabs"
    individual_dir.mkdir(parents=True, exist_ok=True)
    individual_tabs = []
    for index, tab in enumerate(TAB_DEFS):
        tab_min_y = int(tab["tile_min_y"])
        tab_max_y = int(tab["tile_max_y"])
        tab_y = tab_min_y * 8
        tab_h = (tab_max_y - tab_min_y + 1) * 8
        tab_crop = image.crop((CROP_X, tab_y, CROP_X + CROP_W, tab_y + tab_h))
        source_name = f"card_book_right_tabs__{tab['key']}__source.png"
        edit_name = f"card_book_right_tabs__{tab['key']}__edit_4x.png"
        tab_source_path = individual_dir / source_name
        tab_edit_path = individual_dir / edit_name
        tab_crop.save(tab_source_path)
        tab_crop.resize((CROP_W * SCALE, tab_h * SCALE), Image.Resampling.NEAREST).save(tab_edit_path)

        tab_matches = [
            match
            for match in tile_map["matches"]
            if CROP_TILE_MIN_X <= int(match["screen_tile_x"]) <= CROP_TILE_MAX_X
            and tab_min_y <= int(match["screen_tile_y"]) <= tab_max_y
        ]
        tab_tile_map = {
            **tile_map,
            "crop_screen_tiles": {
                "min_x": CROP_TILE_MIN_X,
                "min_y": tab_min_y,
                "max_x": CROP_TILE_MAX_X,
                "max_y": tab_max_y,
            },
            "crop_pixels": {
                "x": CROP_X,
                "y": tab_y,
                "width": CROP_W,
                "height": tab_h,
            },
            "matched_tile_count": len(tab_matches),
            "matches": tab_matches,
            "focus_note": f"Focused card book right-side tab only: {tab['label_jp']}.",
        }
        tab_tile_map_path = individual_dir / f"card_book_right_tabs__{tab['key']}__tile_map.json"
        tab_tile_map_path.write_text(
            json.dumps(tab_tile_map, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )
        individual_tabs.append(
            {
                "key": tab["key"],
                "item_id": f"{ITEM_ID}:{tab['key']}",
                "label": f"카드 책자 오른쪽 탭 {tab['label_jp']}",
                "source_text": tab["label_jp"],
                "suggested_korean": tab["label_ko"],
                "source_path": str(tab_source_path.relative_to(ROOT)),
                "editable_path": str(tab_edit_path.relative_to(ROOT)),
                "tile_map_path": str(tab_tile_map_path.relative_to(ROOT)),
                "rle_offset": OFFSET,
                "rle_offset_hex": f"0x{OFFSET:08X}",
                "width": CROP_W,
                "height": tab_h,
                "scale": SCALE,
                "tile_rows": [tab_min_y, tab_max_y],
                "review_order": 8489 + index,
                "matched_tile_count": len(tab_matches),
            }
        )

    manifest["individual_tabs"] = individual_tabs
    (OUT_DIR / "manifest.json").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    print(f"wrote {OUT_DIR}")
    print(f"matches {len(matches)}")
    print(f"individual tabs {len(individual_tabs)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
