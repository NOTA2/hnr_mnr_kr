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
    parser.add_argument("--category-id", help="디버그용 선택 카테고리. 기본값은 전체 텍스트 항목 적용")
    return parser.parse_args()


def load_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def resolve_effective_translation(item: dict) -> tuple[str, str]:
    if item.get("manual_locked") and item.get("translation"):
        return item["translation"], "manual_locked_translation"
    if item.get("agent_draft"):
        return item["agent_draft"], "agent_draft"
    if item.get("translation"):
        return item["translation"], "saved_translation"
    return item["text"], "original_text"


def build_translation_json(dataset: dict, category_id: str | None) -> list[dict]:
    items = []
    for item in dataset["items"]:
        if item.get("offset") is None:
            continue
        if item["category_id"] == "image_review_units":
            continue
        if category_id and item["category_id"] != category_id:
            continue
        items.append(item)
    items.sort(key=lambda item: item["offset"])
    payload = []
    for item in items:
        effective_translation, source = resolve_effective_translation(item)
        item["effective_translation"] = effective_translation
        item["translation_source"] = source
        payload.append(
            {
                "offset": item["offset"],
                "rom_address": item["rom_address"],
                "byte_length": item["byte_length"],
                "terminator": item.get("terminator"),
                "append_terminator": item.get("append_terminator"),
                "unknown_tokens": item.get("unknown_tokens", 0),
                "text": item["text"],
                "translation": effective_translation,
                "notes": item.get("notes", ""),
                "source_file": item["source_file"],
                "source_group": item["source_group"],
                "source_order": item["source_order"],
            }
        )
    return payload


def main() -> int:
    args = parse_args()
    dataset = load_json(DATASET_PATH)
    payload = build_translation_json(dataset, args.category_id)
    if not payload:
        if args.category_id:
            raise SystemExit(f"no text items found for category: {args.category_id}")
        raise SystemExit("no text items found for full review build")
    DATASET_PATH.write_text(json.dumps(dataset, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

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
