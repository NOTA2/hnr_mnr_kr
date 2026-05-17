#!/usr/bin/env python3

from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SOURCE_ROM = ROOT / "Hagane no Renkinjutsushi - Meisou no Rondo (Japan).gba"
WORKBENCH_ROOT = ROOT / "confirmed_data" / "localization_workbench"
DATASET_PATH = WORKBENCH_ROOT / "workbench_dataset.json"
PROGRESS_PATH = WORKBENCH_ROOT / "progress_state.json"
OUT_DIR = ROOT / "patched_roms" / "current_review"
FIXED_ROM = OUT_DIR / "hnr_localization_review.gba"
TEMP_JSON = OUT_DIR / "current_review_translations.json"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="현재 localization workbench 초안으로 고정 이름 review ROM 을 재빌드합니다.")
    parser.add_argument("--category-id", help="기본값은 progress_state 의 current_review_scope")
    return parser.parse_args()


def load_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def resolve_category(args: argparse.Namespace) -> str:
    if args.category_id:
        return args.category_id
    progress = load_json(PROGRESS_PATH)
    return progress.get("current_review_scope", "translation_workset_core_ui")


def build_translation_json(dataset: dict, category_id: str) -> list[dict]:
    items = [
        item
        for item in dataset["items"]
        if item["category_id"] == category_id and item.get("offset") is not None
    ]
    items.sort(key=lambda item: (item.get("group_id") or "", item["offset"]))
    payload = []
    for item in items:
        payload.append(
            {
                "offset": item["offset"],
                "rom_address": item["rom_address"],
                "byte_length": item["byte_length"],
                "terminator": item.get("terminator"),
                "append_terminator": item.get("append_terminator"),
                "unknown_tokens": item.get("unknown_tokens", 0),
                "text": item["text"],
                "translation": item.get("translation") or item["text"],
                "notes": item.get("notes", ""),
                "source_file": item["source_file"],
                "source_group": item["source_group"],
                "source_order": item["source_order"],
            }
        )
    return payload


def main() -> int:
    args = parse_args()
    category_id = resolve_category(args)
    dataset = load_json(DATASET_PATH)
    payload = build_translation_json(dataset, category_id)
    if not payload:
        raise SystemExit(f"no text items found for category: {category_id}")

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    TEMP_JSON.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    slug = "current_review"
    command = [
        "zsh",
        "scripts/build_translated_rom_with_active_atlas.sh",
        str(SOURCE_ROM),
        str(TEMP_JSON),
        str(OUT_DIR),
        slug,
    ]
    subprocess.run(command, cwd=ROOT, check=True)
    built_rom = OUT_DIR / f"{slug}_translated.gba"
    shutil.copy2(built_rom, FIXED_ROM)
    print(f"built fixed review rom: {FIXED_ROM}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
