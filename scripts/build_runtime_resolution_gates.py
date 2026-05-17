#!/usr/bin/env python3

from __future__ import annotations

import json
from datetime import date
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DATA_ROOT = ROOT / "confirmed_data"
TEXT_LAYOUT = DATA_ROOT / "text_layout"
WORKSPACE = DATA_ROOT / "translation_workspace"
IMAGE = DATA_ROOT / "image_inventory"

SUBPROFILE_PATH = TEXT_LAYOUT / "runtime_dialogue_subprofiles.json"
PAGEFLOW_PATH = TEXT_LAYOUT / "runtime_pageflow_focus.json"
AUDIT_PATH = WORKSPACE / "extraction_audit_status.json"
IMAGE_PATH = IMAGE / "image_text_inventory.json"

OUT_JSON = WORKSPACE / "runtime_resolution_gates.json"
OUT_MD = WORKSPACE / "runtime_resolution_gates.md"


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def build() -> dict:
    sub = load_json(SUBPROFILE_PATH)
    page = load_json(PAGEFLOW_PATH)
    audit = load_json(AUDIT_PATH)
    image = load_json(IMAGE_PATH)

    return {
        "version": 1,
        "last_updated": date.today().isoformat(),
        "structural_closure": {
            "status": audit["structural_extraction_status"],
            "known_source_count": audit["known_source_count"],
            "known_record_count": audit["known_record_count"],
        },
        "machine_closable_runtime_scope": {
            "status": "nearly_closed_except_visual_confirmation",
            "entry8_focus_cluster_count": page["entry8_focus"]["focus_cluster_count"],
            "entry8_chain_heavy_clusters": sub["entry8"]["profile_counts"]["chain_heavy_singleline"],
            "registry_d_long_multiline_focus_count": page["registry_d_focus"]["long_multiline_focus_count"],
            "notes": [
                "The remaining runtime scope is no longer source-wide; it is narrowed to a finite focus set.",
                "Entry8 is narrowed to chain-heavy externally sequenced short-line clusters.",
                "Registry D is narrowed to a small long-multiline tier plus page-turn behavior.",
            ],
        },
        "image_inventory_scope": {
            "status": image["status"],
            "review_unit_count": len(image["review_units"]),
            "highest_priority_units": [unit["id"] for unit in sorted(image["review_units"], key=lambda x: x["review_order"])[:4]],
        },
        "human_verification_blockers": [
            {
                "id": "live_playthrough_text_audit",
                "reason": "Only a real playthrough-style sweep can prove there are no unseen Japanese strings left in unvisited runtime branches.",
            },
            {
                "id": "visual_page_turn_confirmation",
                "reason": "Only runtime visual confirmation can fully close dialogue box/page-flow behavior for entry8 chaining and Registry D long-multiline cases.",
            },
            {
                "id": "baked_image_text_asset_review",
                "reason": "Actual image-backed text still needs asset-by-asset review and later extraction/replacement work.",
            },
        ],
        "operational_reading": [
            "Machine-closable structural extraction is effectively closed for known sources.",
            "What remains is dominated by human-visible runtime confirmation and image-side review, not unknown text-bank discovery.",
        ],
    }


def render_md(data: dict) -> str:
    lines = [
        "# Runtime Resolution Gates",
        "",
        f"- last_updated: `{data['last_updated']}`",
        "",
        "## Structural Closure",
        "",
        f"- status: `{data['structural_closure']['status']}`",
        f"- known_source_count: `{data['structural_closure']['known_source_count']}`",
        f"- known_record_count: `{data['structural_closure']['known_record_count']}`",
        "",
        "## Machine-Closable Runtime Scope",
        "",
        f"- status: `{data['machine_closable_runtime_scope']['status']}`",
        f"- entry8_focus_cluster_count: `{data['machine_closable_runtime_scope']['entry8_focus_cluster_count']}`",
        f"- entry8_chain_heavy_clusters: `{data['machine_closable_runtime_scope']['entry8_chain_heavy_clusters']}`",
        f"- registry_d_long_multiline_focus_count: `{data['machine_closable_runtime_scope']['registry_d_long_multiline_focus_count']}`",
        "",
        "## Image Inventory Scope",
        "",
        f"- status: `{data['image_inventory_scope']['status']}`",
        f"- review_unit_count: `{data['image_inventory_scope']['review_unit_count']}`",
    ]
    for unit in data["image_inventory_scope"]["highest_priority_units"]:
        lines.append(f"- priority_unit: `{unit}`")
    lines.extend(["", "## Human Verification Blockers", ""])
    for item in data["human_verification_blockers"]:
        lines.append(f"- `{item['id']}`: {item['reason']}")
    lines.extend(["", "## Operational Reading", ""])
    for note in data["operational_reading"]:
        lines.append(f"- {note}")
    lines.append("")
    return "\n".join(lines)


def main() -> int:
    data = build()
    OUT_JSON.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    OUT_MD.write_text(render_md(data), encoding="utf-8")
    print(f"wrote {OUT_JSON}")
    print(f"wrote {OUT_MD}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
