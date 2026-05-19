#!/usr/bin/env python3

from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts.build_localization_review_rom import DATASET_PATH, build_translation_json, load_json

CANONICAL_ENTRY8 = ROOT / "confirmed_data" / "extracted_texts" / "registry_a_entry8_prefixed_texts.json"
OUT_PATH = ROOT / "patched_roms" / "current_review" / "current_review_entry8_retranslated_translations.json"


def build_entry8_records() -> list[dict]:
    records: list[dict] = []
    seen: set[int] = set()
    payload = load_json(CANONICAL_ENTRY8)
    for source_order, record in enumerate(payload):
        offset = int(record["offset"])
        if offset in seen:
            raise SystemExit(f"duplicate Entry8 offset: 0x{offset:06X}")
        translation = record.get("translation", "")
        if not translation:
            raise SystemExit(f"missing Entry8 translation: 0x{offset:06X}")
        entry = dict(record)
        entry.update(
            {
                "terminator": None,
                "append_terminator": False,
                "unknown_tokens": record.get("unknown_tokens", 0),
                "source_file": CANONICAL_ENTRY8.name,
                "source_group": "registry_a_entry8_prefixed_texts",
                "source_order": source_order,
            }
        )
        records.append(entry)
        seen.add(offset)
    return records


def main() -> int:
    dataset = load_json(DATASET_PATH)
    base_payload = build_translation_json(
        dataset,
        None,
        exclude_risky_dialogue=False,
        include_entry8=False,
    )
    base_payload = [
        record
        for record in base_payload
        if record.get("source_group") != "registry_a_entry8_prefixed_texts"
    ]
    entry8_payload = build_entry8_records()
    combined = sorted(base_payload + entry8_payload, key=lambda record: int(record["offset"]))
    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUT_PATH.write_text(json.dumps(combined, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"written: {OUT_PATH}")
    print(f"base_records: {len(base_payload)}")
    print(f"entry8_records: {len(entry8_payload)}")
    print(f"total_records: {len(combined)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
