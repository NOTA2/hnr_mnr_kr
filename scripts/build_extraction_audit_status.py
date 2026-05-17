#!/usr/bin/env python3

from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DATA_ROOT = ROOT / "confirmed_data"
WORKSPACE = DATA_ROOT / "translation_workspace"
OUTPUT_PATH = DATA_ROOT / "translation_workspace" / "extraction_audit_status.json"


def main() -> int:
    index = json.loads((WORKSPACE / "index.json").read_text(encoding="utf-8"))
    status = {
        "version": 1,
        "last_updated": "2026-05-17",
        "known_source_count": int(index["master"]["source_count"]),
        "known_record_count": int(index["master"]["record_count"]),
        "major_sources_closed": [
            "startup_intro_texts",
            "system_messages",
            "location_texts",
            "save_menu_prefixed_texts",
            "registry_d_fc_script_texts",
            "registry_a_entry8_prefixed_texts",
            "registry_a_entry12_texts",
            "battle_texts",
            "ability_texts",
            "material_texts",
            "item_texts",
            "ui_skill_texts",
            "credits_texts",
        ],
        "record_structure_families_closed_or_partially_closed": [
            "startup_intro_fixed_slots",
            "system_messages_plain_newline_00",
            "save_menu_prefixed_01ff",
            "entry8_prefixed_01ff_script_line",
            "registry_d_fc_stop_script_line",
            "ui_or_item_plain_00_record",
            "term_description_plain_00_optional_0b",
            "credits_padded_plain_00_record",
        ],
        "remaining_audit_items": [
            {
                "id": "runtime_dialogue_box_family_mapping",
                "status": "in_progress",
                "notes": "Record structures for the major extracted sources are mostly closed, but runtime box/page family for general dialogue and several UI/battle windows is not fully tied yet."
            },
            {
                "id": "live_playthrough_text_audit",
                "status": "pending",
                "notes": "Operational 100% still requires at least one real playthrough-style audit for unseen Japanese strings."
            },
            {
                "id": "image_text_inventory",
                "status": "pending",
                "notes": "Text baked into images is not part of extracted text completion."
            },
        ],
        "operational_reading": "Large unknown text banks and per-source record structures are no longer the main risk; the remaining work is runtime family confirmation, playthrough audit, and image text inventory.",
    }
    OUTPUT_PATH.write_text(json.dumps(status, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"wrote {OUTPUT_PATH}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
