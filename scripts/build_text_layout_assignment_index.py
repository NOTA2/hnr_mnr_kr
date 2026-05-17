from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
WORKSPACE_INDEX_PATH = ROOT / "confirmed_data" / "translation_workspace" / "index.json"
OUTPUT_DIR = ROOT / "confirmed_data" / "text_layout"
OUTPUT_PATH = OUTPUT_DIR / "text_layout_assignment_index.json"


def build_index() -> dict:
    workspace_index = json.loads(WORKSPACE_INDEX_PATH.read_text(encoding="utf-8"))

    source_assignments = {
        "startup_intro_texts": {
            "layout_family": "startup_intro_fixed_slots",
            "assignment_status": "confirmed",
            "notes": [
                "All 4 startup intro records are fixed slots with append_terminator=false.",
                "Use exact byte_length and do not inject manual line breaks.",
            ],
        },
        "location_texts": {
            "layout_family": "world_map_location_r3_12",
            "assignment_status": "confirmed",
            "notes": [
                "World-map location renderer directly reads the location-name field path tied to this source.",
                "This family has code-derived capacity 18 mixed-width units.",
            ],
        },
        "system_messages": {
            "layout_family": "system_messages_plain_newline_00",
            "assignment_status": "partially_confirmed",
            "runtime_resolution_priority": "medium",
            "translation_risk": "medium",
            "notes": [
                "Records are 0x00-terminated and include explicit newlines in some messages.",
                "Exact runtime box family is not yet tied to a specific renderer caller set.",
            ],
        },
        "save_menu_texts": {
            "layout_family": "save_menu_prefixed_01ff",
            "assignment_status": "partially_confirmed",
            "runtime_resolution_priority": "medium",
            "translation_risk": "medium",
            "notes": [
                "Uses 01 FF <u16 char_count> command-stream records.",
                "Byte length is explicit, but full box/page behavior is not yet globally locked.",
            ],
        },
        "registry_d_fc_script_texts": {
            "layout_family": "registry_d_fc_stop_script_line",
            "assignment_status": "partially_confirmed",
            "runtime_candidate_family": "shared_text_object_r3_20",
            "runtime_resolution_priority": "high",
            "translation_risk": "high",
            "notes": [
                "FC stop-byte delimited script lines are objectively extracted.",
                "Runtime dialogue box/page family is still unresolved, but record boundary/control-stream handling is no longer unknown.",
            ],
        },
        "registry_a_entry8_prefixed_texts": {
            "layout_family": "entry8_prefixed_01ff_script_line",
            "assignment_status": "partially_confirmed",
            "runtime_candidate_family": "shared_text_object_r3_20",
            "runtime_resolution_priority": "high",
            "translation_risk": "high",
            "notes": [
                "Large mixed story/event script bank using 01 FF <u16 char_count> counted records.",
                "Runtime dialogue box/page family still needs further tying, but counted-record structure is objective.",
            ],
        },
        "ui_skill_texts": {
            "layout_family": "ui_or_item_plain_00_record",
            "assignment_status": "partially_confirmed",
            "runtime_resolution_priority": "low",
            "translation_risk": "low",
            "notes": [
                "Short 0x00-terminated UI records with no counted header are already objective.",
                "A direct pointer-indexed local UI/data table is confirmed, but the runtime window family is still unresolved.",
            ],
        },
        "item_texts": {
            "layout_family": "ui_or_item_plain_00_record",
            "assignment_status": "partially_confirmed",
            "runtime_resolution_priority": "low",
            "translation_risk": "low",
            "notes": [
                "Short 0x00-terminated item/event strings are objective.",
                "A direct pointer-indexed local table is confirmed, but the runtime window family is still unresolved.",
            ],
        },
        "battle_texts": {
            "layout_family": "term_description_plain_00_optional_0b",
            "assignment_status": "partially_confirmed",
            "runtime_resolution_priority": "medium",
            "translation_risk": "low",
            "notes": [
                "Plain 0x00-terminated battle term/description records are objective.",
                "Some description rows contain inline 0x0B separators and ideographic padding that must be preserved.",
                "Runtime battle box family is still unresolved.",
            ],
        },
        "ability_texts": {
            "layout_family": "term_description_plain_00_optional_0b",
            "assignment_status": "partially_confirmed",
            "runtime_resolution_priority": "medium",
            "translation_risk": "low",
            "notes": [
                "Plain 0x00-terminated term/description records are objective.",
                "Many rows contain inline 0x0B separators and ideographic padding that must be preserved.",
                "Runtime display family is still unresolved.",
            ],
        },
        "material_texts": {
            "layout_family": "term_description_plain_00_optional_0b",
            "assignment_status": "partially_confirmed",
            "runtime_resolution_priority": "medium",
            "translation_risk": "low",
            "notes": [
                "Plain 0x00-terminated term/description records are objective.",
                "A local resource-table section is confirmed and rows preserve inline 0x0B separators.",
                "Runtime display family is still unresolved.",
            ],
        },
        "registry_a_entry12_texts": {
            "layout_family": "ui_or_item_plain_00_record",
            "assignment_status": "partially_confirmed",
            "runtime_resolution_priority": "low",
            "translation_risk": "low",
            "notes": [
                "Gameplay/item-adjacent short plain records are objective.",
                "Display family remains unresolved, so translations should stay concise.",
            ],
        },
        "credits_texts": {
            "layout_family": "credits_padded_plain_00_record",
            "assignment_status": "partially_confirmed",
            "runtime_resolution_priority": "low",
            "translation_risk": "low",
            "notes": [
                "Credits records are plain 0x00-terminated strings padded with ideographic spaces.",
                "Runtime credits layout family is not yet mapped, so spacing-sensitive edits should stay conservative.",
            ],
        },
    }

    workset_assignments = {
        "translation_workset_startup_font_showcase": {
            "kind": "uniform",
            "layout_family": "startup_intro_fixed_slots",
            "assignment_status": "confirmed",
            "notes": ["All records come from startup_intro_texts."],
        },
        "translation_workset_core_ui": {
            "kind": "mixed",
            "assignment_status": "mixed",
            "by_source_group": {
                "system_messages": "system_messages_plain_newline_00",
                "save_menu_texts": "save_menu_prefixed_01ff",
                "location_texts": "world_map_location_r3_12",
                "ui_skill_texts": "ui_or_item_plain_00_record",
            },
            "notes": [
                "This workset must not be treated as a single box family.",
                "Apply the source_group-specific family first.",
            ],
        },
        "translation_workset_gameplay_terms": {
            "kind": "mixed",
            "assignment_status": "mixed",
            "by_source_group": {
                "item_texts": "ui_or_item_plain_00_record",
                "ability_texts": "term_description_plain_00_optional_0b",
                "material_texts": "term_description_plain_00_optional_0b",
                "battle_texts": "term_description_plain_00_optional_0b",
                "registry_a_entry12_texts": "ui_or_item_plain_00_record",
            },
            "notes": [
                "Record structures are now mostly objective even though runtime box families are still unresolved."
            ],
        },
        "translation_workset_registry_d_dialogue": {
            "kind": "uniform",
            "layout_family": "registry_d_fc_stop_script_line",
            "assignment_status": "partially_confirmed",
            "runtime_candidate_family": "shared_text_object_r3_20",
            "notes": [
                "Record boundary/control-stream handling is confirmed at the FC stop-byte level.",
                "General dialogue box/page family remains unresolved, so translations should still stay concise.",
            ],
        },
        "translation_workset_intro_full_test": {
            "kind": "mixed",
            "assignment_status": "mixed",
            "by_source_group": {
                "startup_intro_texts": "startup_intro_fixed_slots",
                "location_texts": "world_map_location_r3_12",
                "registry_a_entry8_prefixed_texts": "entry8_prefixed_01ff_script_line",
            },
            "notes": [
                "This is a QA test set spanning multiple families.",
                "Do not infer a single hard line limit from this workset.",
            ],
        },
        "translation_workset_intro_full_compact_test": {
            "kind": "mixed",
            "assignment_status": "mixed",
            "by_source_group": {
                "startup_intro_texts": "startup_intro_fixed_slots",
                "location_texts": "world_map_location_r3_12",
                "registry_a_entry8_prefixed_texts": "entry8_prefixed_01ff_script_line",
            },
            "notes": [
                "Compact QA test set spanning multiple families."
            ],
        },
    }

    return {
        "version": 1,
        "last_updated": "2026-05-17",
        "source_assignments": source_assignments,
        "workset_assignments": workset_assignments,
        "workspace_priority_worksets": workspace_index.get("priority_worksets", []),
        "usage_note": [
            "Use source_group-specific layout families first.",
            "When a workset is mixed, do not invent a single global char limit.",
            "Partially confirmed record-structure families still need concise translation until runtime box/page family is confirmed.",
            "Even when record structure is objective, unresolved runtime families should stay concise until runtime family mapping is confirmed.",
        ],
    }


def main() -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    index = build_index()
    OUTPUT_PATH.write_text(json.dumps(index, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"wrote {OUTPUT_PATH}")


if __name__ == "__main__":
    main()
