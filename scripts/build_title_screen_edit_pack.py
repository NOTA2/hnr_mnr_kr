#!/usr/bin/env python3
"""Build a user-facing title screen image edit pack.

This pack is deliberately separate from analysis outputs. The GUI should expose
these friendly PNGs as the source downloads, while the item metadata keeps the
ROM offset needed for automatic RLE application.
"""

from __future__ import annotations

import json
import shutil
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SOURCE_DIR = ROOT / "confirmed_data/image_inventory/runtime_rle_patch_previews/single_rle_layouts"
OUT_DIR = ROOT / "confirmed_data/image_inventory/edit_packs/title_screen"


TITLE_ITEMS = [
    {
        "item_id": "image:rle:007E9158",
        "offset": 0x007E9158,
        "label": "PUSH START",
        "role": "title_menu_push_start",
        "source": "rle_007E9158_rle_8cols_4x.png",
        "editable": "01_push_start__007E9158__edit_4x.png",
        "suggested_korean": "PRESS START는 영어 유지도 가능. 한글화 시 '시작' 또는 '눌러 시작'.",
    },
    {
        "item_id": "image:rle:007E9404",
        "offset": 0x007E9404,
        "label": "はじめから",
        "role": "title_menu_new_game",
        "source": "rle_007E9404_rle_8cols_4x.png",
        "editable": "02_new_game__007E9404__edit_4x.png",
        "suggested_korean": "처음부터",
    },
    {
        "item_id": "image:rle:007E95E0",
        "offset": 0x007E95E0,
        "label": "つづきから",
        "role": "title_menu_continue",
        "source": "rle_007E95E0_rle_8cols_4x.png",
        "editable": "03_continue__007E95E0__edit_4x.png",
        "suggested_korean": "이어하기",
    },
    {
        "item_id": "image:rle:007E97A4",
        "offset": 0x007E97A4,
        "label": "通信",
        "role": "title_menu_link",
        "source": "rle_007E97A4_rle_8cols_4x.png",
        "editable": "04_link__007E97A4__edit_4x.png",
        "suggested_korean": "통신",
    },
    {
        "item_id": "image:rle:007E0000",
        "offset": 0x007E0000,
        "label": "타이틀 로고/저작권",
        "role": "title_logo_copyright_advanced",
        "source": "rle_007E0000_rle_8cols_4x.png",
        "editable": "90_logo_copyright__007E0000__advanced_edit_4x.png",
        "suggested_korean": "고급 항목. 로고 전체는 화면 배치 재조립 후 편집하는 편이 안전.",
    },
]


def main() -> int:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    manifest = []
    for item in TITLE_ITEMS:
        source = SOURCE_DIR / item["source"]
        if not source.exists():
            raise FileNotFoundError(source)
        destination = OUT_DIR / item["editable"]
        shutil.copyfile(source, destination)
        manifest.append(
            {
                **item,
                "editable_path": str(destination.relative_to(ROOT)),
                "source_path": str(source.relative_to(ROOT)),
                "scale": 4,
                "columns": 8,
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
        "각 PNG는 8-column RLE 타일을 4배 확대해 만든 편집용 이미지이며, 수정 후 같은 항목에 업로드하면 자동 RLE 적용 대상이 된다.",
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
