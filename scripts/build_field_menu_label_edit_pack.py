#!/usr/bin/env python3
"""Build enlarged edit PNGs for confirmed field/menu LZ77 label blocks."""

from __future__ import annotations

import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT / ".vendor") not in sys.path:
    sys.path.insert(0, str(ROOT / ".vendor"))

from PIL import Image


OUT_DIR = ROOT / "confirmed_data" / "image_inventory" / "edit_packs" / "field_menu_labels"
SCALE = 4


ITEMS = [
    {
        "item_id": "image:field_alchemy_label_005323AC",
        "offset": 0x005323AC,
        "label": "필드 OBJ 라벨 錬成",
        "source_path": "confirmed_data/image_inventory/runtime_tile_matches/no_entry8_ss1/matched_previews/lz77_0294_off_005323AC.png",
        "editable": "01_field_alchemy__005323AC__edit_4x.png",
        "suggested_korean": "연성",
    },
    {
        "item_id": "image:field_label_0053257C",
        "offset": 0x0053257C,
        "label": "필드 OBJ 라벨 アイテム",
        "source_path": "confirmed_data/image_inventory/runtime_tile_matches/no_entry8_ss2/matched_previews/lz77_0295_off_0053257C.png",
        "editable": "02_field_item__0053257C__edit_4x.png",
        "suggested_korean": "아이템",
    },
    {
        "item_id": "image:field_status_label_00532764",
        "offset": 0x00532764,
        "label": "필드/메뉴 라벨 ステータス",
        "source_path": "confirmed_data/image_inventory/runtime_tile_matches/curated_neighborhoods/lz77_0296_off_00532764.png",
        "editable": "03_field_status__00532764__edit_4x.png",
        "suggested_korean": "상태",
    },
    {
        "item_id": "image:field_save_label_0053293C",
        "offset": 0x0053293C,
        "label": "필드/메뉴 라벨 セーブ",
        "source_path": "confirmed_data/image_inventory/runtime_tile_matches/curated_neighborhoods/lz77_0297_off_0053293C.png",
        "editable": "04_field_save__0053293C__edit_4x.png",
        "suggested_korean": "저장",
    },
]


def main() -> int:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    manifest = []
    for item in ITEMS:
        source_path = ROOT / item["source_path"]
        if not source_path.exists():
            raise FileNotFoundError(source_path)
        image = Image.open(source_path).convert("L")
        output_path = OUT_DIR / item["editable"]
        image.resize((image.width * SCALE, image.height * SCALE), Image.Resampling.NEAREST).save(output_path)
        manifest.append(
            {
                **item,
                "editable_path": str(output_path.relative_to(ROOT)),
                "scale": SCALE,
                "upload_note": "이 PNG를 수정해 같은 GUI 항목에 업로드하면 LZ77 블록으로 자동 적용된다.",
            }
        )

    (OUT_DIR / "manifest.json").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    lines = [
        "# Field/Menu Label Edit Pack",
        "",
        "확인된 LZ77 필드/메뉴 라벨을 4배 확대한 편집용 PNG 묶음이다.",
        "크기를 유지해서 수정한 뒤 GUI에 업로드하면 자동 LZ77 적용 대상이 된다.",
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
