#!/usr/bin/env python3
"""Build a user-facing title screen image edit pack.

This pack is deliberately separate from analysis outputs. The GUI should expose
these friendly PNGs as the source downloads, while the item metadata keeps the
ROM offset needed for automatic RLE application.
"""

from __future__ import annotations

import json
import shutil
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT / ".vendor") not in sys.path:
    sys.path.insert(0, str(ROOT / ".vendor"))

from PIL import Image


SOURCE_DIR = ROOT / "confirmed_data/image_inventory/runtime_rle_patch_previews/single_rle_layouts"
OUT_DIR = ROOT / "confirmed_data/image_inventory/edit_packs/title_screen"


TITLE_ITEMS = [
    {
        "item_id": "image:rle:007E9158",
        "offset": 0x007E9158,
        "label": "PUSH START",
        "role": "title_menu_push_start",
        "source_path": "confirmed_data/image_inventory/runtime_tile_matches/timeline_with_rle/matched_previews/rle_1077_off_007E9158.png",
        "editable": "01_push_start__007E9158__edit_4x.png",
        "columns": 32,
        "scale_source": 4,
        "suggested_korean": "PRESS START는 영어 유지도 가능. 한글화 시 '시작' 또는 '눌러 시작'.",
    },
    {
        "item_id": "image:rle:007E9404",
        "offset": 0x007E9404,
        "label": "はじめから",
        "role": "title_menu_new_game",
        "source_path": "confirmed_data/image_inventory/runtime_tile_matches/timeline_with_rle/matched_previews/rle_1078_off_007E9404.png",
        "editable": "02_new_game__007E9404__edit_4x.png",
        "columns": 32,
        "scale_source": 4,
        "suggested_korean": "처음부터",
    },
    {
        "item_id": "image:rle:007E95E0",
        "offset": 0x007E95E0,
        "label": "つづきから",
        "role": "title_menu_continue",
        "source_path": "confirmed_data/image_inventory/runtime_tile_matches/timeline_with_rle/matched_previews/rle_1079_off_007E95E0.png",
        "editable": "03_continue__007E95E0__edit_4x.png",
        "columns": 32,
        "scale_source": 4,
        "suggested_korean": "이어하기",
    },
    {
        "item_id": "image:rle:007E97A4",
        "offset": 0x007E97A4,
        "label": "通信",
        "role": "title_menu_link",
        "source_path": "confirmed_data/image_inventory/runtime_tile_matches/timeline_with_rle/matched_previews/rle_1080_off_007E97A4.png",
        "editable": "04_link__007E97A4__edit_4x.png",
        "columns": 32,
        "scale_source": 4,
        "suggested_korean": "통신",
    },
    {
        "item_id": "image:rle:007E0000",
        "offset": 0x007E0000,
        "label": "타이틀 로고/저작권",
        "role": "title_logo_copyright_advanced",
        "source": "rle_007E0000_rle_8cols_4x.png",
        "editable": "90_logo_copyright__007E0000__advanced_edit_4x.png",
        "columns": 8,
        "suggested_korean": "고급 항목. 로고 전체는 화면 배치 재조립 후 편집하는 편이 안전.",
    },
]


def source_path_for(item: dict) -> Path:
    if item.get("source_path"):
        return ROOT / item["source_path"]
    return SOURCE_DIR / item["source"]


def write_editable_source(source: Path, destination: Path, scale: int) -> None:
    if scale == 1:
        shutil.copyfile(source, destination)
        return
    image = Image.open(source).convert("RGBA")
    scaled = image.resize((image.width * scale, image.height * scale), Image.Resampling.NEAREST)
    scaled.save(destination)


def main() -> int:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    manifest = []
    for item in TITLE_ITEMS:
        source = source_path_for(item)
        if not source.exists():
            raise FileNotFoundError(source)
        destination = OUT_DIR / item["editable"]
        scale = int(item.get("scale_source", 1))
        write_editable_source(source, destination, scale)
        manifest.append(
            {
                **item,
                "editable_path": str(destination.relative_to(ROOT)),
                "source_path": str(source.relative_to(ROOT)),
                "scale": 4,
                "columns": int(item.get("columns", 8)),
                "upload_note": "이 PNG를 수정해 같은 GUI 항목에 업로드하면 자동 RLE 적용 대상이 된다.",
            }
        )

    (OUT_DIR / "manifest.json").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    lines = [
        "# Title Screen Edit Pack",
        "",
        "GUI에서 원본 다운로드로 제공하기 위한 사용자용 PNG 묶음이다.",
        "타이틀 메뉴 PNG는 실제 글자가 한 줄로 보이는 32-column RLE 타일 레이아웃을 4배 확대해 만든다.",
        "수정 후 같은 항목에 업로드하면 자동 RLE 적용 대상이 된다.",
        "",
        "주의: 이미지 크기와 4배 확대 비율을 유지하는 편이 가장 안전하다.",
        "",
    ]
    for item in manifest:
        lines.append(f"- `{item['editable']}`: {item['label']} / target={item['suggested_korean']}")
    (OUT_DIR / "README.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"wrote {OUT_DIR}")
    print(f"items {len(manifest)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
