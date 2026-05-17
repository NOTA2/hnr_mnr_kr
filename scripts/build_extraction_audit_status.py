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
        "structural_extraction_status": "closed_for_known_sources",
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
        "runtime_resolution_scope": {
            "high_priority_dialogue_or_page_flow": [
                "registry_a_entry8_prefixed_texts",
                "registry_d_fc_script_texts",
            ],
            "operationally_bounded_ui_or_command_flow": [
                "system_messages",
                "save_menu_prefixed_texts",
            ],
            "lower_risk_runtime_unknowns": [
                "ui_skill_texts",
                "item_texts",
                "registry_a_entry12_texts",
                "battle_texts",
                "ability_texts",
                "material_texts",
                "credits_texts",
            ],
        },
        "remaining_audit_items": [
            {
                "id": "runtime_dialogue_box_family_mapping",
                "status": "in_progress",
                "notes": "Record structures for the major extracted sources are mostly closed. The remaining high-priority runtime risk is now narrowed to two shared-r3=20 dialogue profiles: entry8 short single-line counted records and Registry D multiline FC-delimited payloads."
            },
            {
                "id": "medium_ui_command_runtime_cleanup",
                "status": "mostly_closed",
                "notes": "system_messages and save_menu are short, structurally stable, and translation-ready with conservative rules. Residual runtime uncertainty remains documented, but they are no longer treated as major blockers."
            },
            {
                "id": "live_playthrough_text_audit",
                "status": "pending",
                "notes": "Operational 100% still requires at least one real playthrough-style audit for unseen Japanese strings, but canonical worksets are no longer blocked from starting translation before that audit."
            },
            {
                "id": "image_text_inventory",
                "status": "in_progress",
                "notes": "Image-side review is now started as a separate inventory track. Several important UI/dialogue contexts are already confirmed to be non-image text, but baked-image review buckets remain pending."
            },
        ],
        "operational_reading": "Large unknown text banks and per-source record structures are no longer the main risk. Structurally, known sources are closed; system/save are operationally bounded, and the remaining major work is dialogue/page runtime family confirmation for two narrowed high-priority profiles, playthrough audit, and image-side inventory review.",
    }
    OUTPUT_PATH.write_text(json.dumps(status, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"wrote {OUTPUT_PATH}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
