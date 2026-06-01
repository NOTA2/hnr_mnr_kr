#!/usr/bin/env python3
"""Build focused edit packs for POWER labels in card-list RLE variants."""

from __future__ import annotations

import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT / ".vendor") not in sys.path:
    sys.path.insert(0, str(ROOT / ".vendor"))

from PIL import Image


SOURCE_ROOT = (
    ROOT
    / "confirmed_data"
    / "image_inventory"
    / "runtime_rle_screen_order"
    / "no_entry8_latest_ss3"
)
OUT_DIR = ROOT / "confirmed_data" / "image_inventory" / "edit_packs" / "card_list_power_labels"

VARIANT_OFFSETS = [
    ("variant_1", 0x003A5E50, "화면순 RLE 편집 - 카드 리스트 いいえ UI 변형 1"),
    ("variant_2", 0x003A6E24, "화면순 RLE 편집 - 카드 리스트 いいえ UI 변형 2"),
    ("variant_3", 0x003A7C3C, "화면순 RLE 편집 - 카드 리스트 いいえ UI 변형 3"),
    ("variant_4", 0x003A8894, "화면순 RLE 편집 - 카드 리스트 いいえ UI 변형 4"),
    ("variant_5", 0x003A9624, "화면순 RLE 편집 - 카드 리스트 いいえ UI 변형 5"),
    ("variant_6", 0x003AA4C0, "화면순 RLE 편집 - 카드 리스트 いいえ UI 변형 6"),
]

SCENE = "no_entry8_latest_ss3"
FRAME = "frame_009730"
BG = 1
SCALE = 4

# User-selected 1x source box around the POWER label.
CROP_X = 60
CROP_Y = 82
CROP_W = 46
CROP_H = 28
CROP_TILE_MIN_X = CROP_X // 8
CROP_TILE_MIN_Y = CROP_Y // 8
CROP_TILE_MAX_X = (CROP_X + CROP_W - 1) // 8
CROP_TILE_MAX_Y = (CROP_Y + CROP_H - 1) // 8


def main() -> int:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    items = []
    for index, (key, offset, label) in enumerate(VARIANT_OFFSETS, start=1):
        source_dir = SOURCE_ROOT / f"frame_009730_bg1_rle_{offset:08X}"
        source_image_path = source_dir / "matched_tiles_screen_order.png"
        source_tile_map_path = source_dir / "tile_map.json"
        if not source_image_path.is_file() or not source_tile_map_path.is_file():
            raise FileNotFoundError(f"missing source workspace for 0x{offset:08X}: {source_dir}")

        source_image = Image.open(source_image_path).convert("RGBA")
        source_tile_map = json.loads(source_tile_map_path.read_text(encoding="utf-8"))
        crop = source_image.crop((CROP_X, CROP_Y, CROP_X + CROP_W, CROP_Y + CROP_H))

        source_path = OUT_DIR / f"card_list_power__{key}__source.png"
        edit_path = OUT_DIR / f"card_list_power__{key}__edit_4x.png"
        tile_map_path = OUT_DIR / f"card_list_power__{key}__tile_map.json"
        crop.save(source_path)
        crop.resize((CROP_W * SCALE, CROP_H * SCALE), Image.Resampling.NEAREST).save(edit_path)

        matches = [
            match
            for match in source_tile_map["matches"]
            if CROP_TILE_MIN_X <= int(match["screen_tile_x"]) <= CROP_TILE_MAX_X
            and CROP_TILE_MIN_Y <= int(match["screen_tile_y"]) <= CROP_TILE_MAX_Y
        ]
        focused_tile_map = {
            **source_tile_map,
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
            "rle_runtime_tile_layout": None,
            "focus_note": "Focused card-list POWER label box only.",
        }
        tile_map_path.write_text(json.dumps(focused_tile_map, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

        items.append(
            {
                "key": key,
                "item_id": f"image:rle_screen_order:{SCENE}:{FRAME}:bg{BG}:{offset:08X}",
                "offset": offset,
                "offset_hex": f"0x{offset:08X}",
                "label": label,
                "source_text": "POWER",
                "suggested_korean": "파워",
                "source_path": str(source_path.relative_to(ROOT)),
                "editable_path": str(edit_path.relative_to(ROOT)),
                "tile_map_path": str(tile_map_path.relative_to(ROOT)),
                "source_screen_order_path": str(source_image_path.relative_to(ROOT)),
                "source_tile_map_path": str(source_tile_map_path.relative_to(ROOT)),
                "width": CROP_W,
                "height": CROP_H,
                "scale": SCALE,
                "crop_pixels": {"x": CROP_X, "y": CROP_Y, "width": CROP_W, "height": CROP_H},
                "crop_screen_tiles": {
                    "min_x": CROP_TILE_MIN_X,
                    "min_y": CROP_TILE_MIN_Y,
                    "max_x": CROP_TILE_MAX_X,
                    "max_y": CROP_TILE_MAX_Y,
                },
                "replacement_payload_base": "source_raw",
                "replacement_source_color_map": True,
                "replacement_verify_source_noop": False,
                "review_order": 4070 + index * 10,
                "matched_tile_count": len(matches),
            }
        )

    manifest = {
        "source_text": "POWER",
        "suggested_korean": "파워",
        "crop_pixels": {"x": CROP_X, "y": CROP_Y, "width": CROP_W, "height": CROP_H},
        "crop_screen_tiles": {
            "min_x": CROP_TILE_MIN_X,
            "min_y": CROP_TILE_MIN_Y,
            "max_x": CROP_TILE_MAX_X,
            "max_y": CROP_TILE_MAX_Y,
        },
        "items": items,
    }
    (OUT_DIR / "manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    (OUT_DIR / "README.md").write_text(
        "\n".join(
            [
                "# Card List POWER Label Edit Packs",
                "",
                "카드 리스트 RLE 변형 1~6에서 POWER 라벨 주변 46x28px 박스만 분리한 편집용 PNG다.",
                "기존 전체 화면순 RLE 항목보다 훨씬 작은 crop/tile_map을 사용한다.",
                "",
                f"- crop: x={CROP_X}, y={CROP_Y}, width={CROP_W}, height={CROP_H}",
            ]
        )
        + "\n",
        encoding="utf-8",
    )
    print(f"wrote {OUT_DIR}")
    print(f"items {len(items)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
