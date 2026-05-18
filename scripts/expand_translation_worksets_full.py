#!/usr/bin/env python3

from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
EXTRACTED = ROOT / "confirmed_data" / "extracted_texts"
WORKSETS = ROOT / "confirmed_data" / "translation_worksets"


def load_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, payload) -> None:
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def key(record: dict) -> tuple[int, str]:
    return int(record["offset"]), record["source_group"]


def merge_full_workset(existing_path: Path, source_paths: list[Path]) -> int:
    existing = load_json(existing_path) if existing_path.exists() else []
    existing_map = {key(record): record for record in existing}

    merged = list(existing)
    added = 0
    for source_path in source_paths:
        records = load_json(source_path)
        source_group = source_path.stem.replace("save_menu_prefixed_texts", "save_menu_texts")
        for source_order, record in enumerate(records):
            normalized = dict(record)
            normalized.setdefault("translation", "")
            normalized["source_file"] = f"{source_group}.json"
            normalized["source_group"] = source_group
            normalized.setdefault("source_order", source_order)
            if key(normalized) in existing_map:
                continue
            merged.append(normalized)
            existing_map[key(normalized)] = normalized
            added += 1

    merged.sort(key=lambda record: (record.get("source_order", 0), int(record["offset"])))
    write_json(existing_path, merged)
    return added


def main() -> int:
    gameplay_added = merge_full_workset(
        WORKSETS / "translation_workset_gameplay_terms.json",
        [
            EXTRACTED / "item_texts.json",
            EXTRACTED / "battle_texts.json",
            EXTRACTED / "ability_texts.json",
            EXTRACTED / "material_texts.json",
            EXTRACTED / "registry_a_entry12_texts.json",
        ],
    )
    credits_path = WORKSETS / "translation_workset_credits.json"
    credits_added = merge_full_workset(
        credits_path,
        [EXTRACTED / "credits_texts.json"],
    )
    print(f"gameplay_terms_added={gameplay_added}")
    print(f"credits_added={credits_added}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
