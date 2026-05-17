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
            "layout_family": "unresolved_plain_terminated",
            "assignment_status": "unresolved",
            "notes": [
                "Records are 0x00-terminated and include explicit newlines in some messages.",
                "Exact runtime box family is not yet tied to a specific renderer caller set.",
            ],
        },
        "save_menu_texts": {
            "layout_family": "save_menu_prefixed_01ff",
            "assignment_status": "partially_confirmed",
            "notes": [
                "Uses 01 FF <u16 char_count> command-stream records.",
                "Byte length is explicit, but full box/page behavior is not yet globally locked.",
            ],
        },
        "ui_skill_texts": {
            "layout_family": "unresolved_ui_text",
            "assignment_status": "unresolved",
            "notes": [
                "Likely uses the shared text object family, but the specific caller/window family is not yet pinned down objectively."
            ],
        },
        "item_texts": {
            "layout_family": "unresolved_ui_text",
            "assignment_status": "unresolved",
            "notes": ["Translation should stay concise until a concrete box family is linked."],
        },
        "battle_texts": {
            "layout_family": "unresolved_battle_text",
            "assignment_status": "unresolved",
            "notes": ["Translation should stay concise until a concrete battle window family is linked."],
        },
        "ability_texts": {
            "layout_family": "unresolved_ui_text",
            "assignment_status": "unresolved",
            "notes": ["Likely short UI/battle descriptions, but the actual box family is still unresolved."],
        },
        "material_texts": {
            "layout_family": "unresolved_ui_text",
            "assignment_status": "unresolved",
            "notes": ["Likely short UI descriptions, but the actual box family is still unresolved."],
        },
        "registry_d_fc_script_texts": {
            "layout_family": "unresolved_dialogue_event",
            "assignment_status": "unresolved",
            "notes": [
                "Event/dialogue script extraction is stable, but runtime box/page/control-token family is not yet fully mapped."
            ],
        },
        "registry_a_entry8_prefixed_texts": {
            "layout_family": "unresolved_dialogue_event",
            "assignment_status": "unresolved",
            "notes": [
                "Large mixed story/event command-stream bank.",
                "Needs further per-scene runtime family linking before hard line limits can be assigned.",
            ],
        },
        "registry_a_entry12_texts": {
            "layout_family": "unresolved_ui_text",
            "assignment_status": "unresolved",
            "notes": ["Gameplay/item-adjacent texts extracted, but display family remains unresolved."],
        },
        "credits_texts": {
            "layout_family": "unresolved_credits",
            "assignment_status": "unresolved",
            "notes": ["Credits extraction is stable, but runtime layout family is not yet mapped."],
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
                "system_messages": "unresolved_plain_terminated",
                "save_menu_texts": "save_menu_prefixed_01ff",
                "location_texts": "world_map_location_r3_12",
                "ui_skill_texts": "unresolved_ui_text",
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
                "item_texts": "unresolved_ui_text",
                "ability_texts": "unresolved_ui_text",
                "material_texts": "unresolved_ui_text",
                "battle_texts": "unresolved_battle_text",
                "registry_a_entry12_texts": "unresolved_ui_text",
            },
            "notes": [
                "Mostly concise UI/term content, but runtime family links are not yet fully pinned down."
            ],
        },
        "translation_workset_registry_d_dialogue": {
            "kind": "uniform",
            "layout_family": "unresolved_dialogue_event",
            "assignment_status": "unresolved",
            "notes": ["Stable extraction, unresolved runtime dialogue box family."],
        },
        "translation_workset_intro_full_test": {
            "kind": "mixed",
            "assignment_status": "mixed",
            "by_source_group": {
                "startup_intro_texts": "startup_intro_fixed_slots",
                "location_texts": "world_map_location_r3_12",
                "registry_a_entry8_prefixed_texts": "unresolved_dialogue_event",
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
                "registry_a_entry8_prefixed_texts": "unresolved_dialogue_event",
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
            "Unresolved families should stay concise until runtime family mapping is confirmed.",
        ],
    }


def main() -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    index = build_index()
    OUTPUT_PATH.write_text(json.dumps(index, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"wrote {OUTPUT_PATH}")


if __name__ == "__main__":
    main()
