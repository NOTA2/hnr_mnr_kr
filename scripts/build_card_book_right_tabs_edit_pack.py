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
        "source_dir": SOURCE_DIR,
        "tile_min_y": 0,
        "tile_max_y": 3,
    },
    {
        "key": "stone",
        "label_jp": "石",
        "label_ko": "돌",
        "source_dir": (
            ROOT
            / "confirmed_data"
            / "image_inventory"
            / "runtime_rle_screen_order"
            / "current_review_ss6"
            / "frame_000006_bg1_rle_003A3540"
        ),
        "tile_min_y": 3,
        "tile_max_y": 6,
    },
    {
        "key": "nature",
        "label_jp": "自然",
        "label_ko": "자연",
        "source_dir": (
            ROOT
            / "confirmed_data"
            / "image_inventory"
            / "runtime_rle_screen_order"
            / "current_review_ss7"
            / "frame_000007_bg1_rle_003A3540"
        ),
        "tile_min_y": 5,
        "tile_max_y": 8,
    },
    {
        "key": "inorganic",
        "label_jp": "無機",
        "label_ko": "무기",
        "source_dir": (
            ROOT
            / "confirmed_data"
            / "image_inventory"
            / "runtime_rle_screen_order"
            / "current_review_ss9"
            / "frame_000009_bg1_rle_003A3540"
        ),
        "tile_min_y": 7,
        "tile_max_y": 10,
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
        tab_source_dir = Path(tab["source_dir"])
        tab_source_image = tab_source_dir / "matched_tiles_screen_order.png"
        tab_source_tile_map_path = tab_source_dir / "tile_map.json"
        if not tab_source_image.exists() or not tab_source_tile_map_path.exists():
            raise FileNotFoundError(f"missing active tab source: {tab_source_dir}")
        tab_image = Image.open(tab_source_image).convert("RGBA")
        tab_source_tile_map = json.loads(tab_source_tile_map_path.read_text(encoding="utf-8"))
        stable_palette_path = json.loads(SOURCE_TILE_MAP.read_text(encoding="utf-8")).get("runtime_palette_path", "")
        tab_min_y = int(tab["tile_min_y"])
        tab_max_y = int(tab["tile_max_y"])
        tab_y = tab_min_y * 8
        tab_h = (tab_max_y - tab_min_y + 1) * 8
        tab_crop = tab_image.crop((CROP_X, tab_y, CROP_X + CROP_W, tab_y + tab_h))
        source_name = f"card_book_right_tabs__{tab['key']}__source.png"
        edit_name = f"card_book_right_tabs__{tab['key']}__edit_4x.png"
        tab_source_path = individual_dir / source_name
        tab_edit_path = individual_dir / edit_name
        tab_crop.save(tab_source_path)
        tab_crop.resize((CROP_W * SCALE, tab_h * SCALE), Image.Resampling.NEAREST).save(tab_edit_path)

        tab_matches = [
            match
            for match in tab_source_tile_map["matches"]
            if CROP_TILE_MIN_X <= int(match["screen_tile_x"]) <= CROP_TILE_MAX_X
            and tab_min_y <= int(match["screen_tile_y"]) <= tab_max_y
        ]
        tab_tile_map = {
            **tab_source_tile_map,
            "runtime_palette_path": stable_palette_path or tab_source_tile_map.get("runtime_palette_path", ""),
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
            "focus_note": (
                f"Focused card book right-side front tab only: {tab['label_jp']}. "
                "This crop is taken from a savestate where that bookmark is in front, "
                "so the label is not occluded by another tab."
            ),
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
                "source_screen_order_path": str(tab_source_image.relative_to(ROOT)),
                "source_tile_map_path": str(tab_source_tile_map_path.relative_to(ROOT)),
                "rle_offset": OFFSET,
                "rle_offset_hex": f"0x{OFFSET:08X}",
                "width": CROP_W,
                "height": tab_h,
                "scale": SCALE,
                "tile_rows": [tab_min_y, tab_max_y],
                "replacement_payload_base": "current",
                "replacement_verify_source_noop": False,
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
