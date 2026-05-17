#!/usr/bin/env python3

from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
WORKSPACE = ROOT / "confirmed_data" / "translation_workspace"
LAYOUT = ROOT / "confirmed_data" / "text_layout"
OUT_JSON = WORKSPACE / "translation_readiness_report.json"
OUT_MD = WORKSPACE / "translation_readiness_report.md"


def build() -> dict:
    assignment = json.loads((LAYOUT / "text_layout_assignment_index.json").read_text(encoding="utf-8"))
    return {
        "version": 1,
        "last_updated": "2026-05-17",
        "worksets": [
            {
                "workset": "translation_workset_startup_font_showcase",
                "status": "ready_with_fixed_slot_rules",
                "notes": [
                    "All records belong to the confirmed startup_intro_fixed_slots family.",
                    "Use exact byte-length slots and append_terminator=false."
                ],
            },
            {
                "workset": "translation_workset_core_ui",
                "status": "ready_with_source_specific_rules",
                "notes": [
                    "Mixed workset; apply source_group-specific family rules first.",
                    "system_messages/save_menu still have some runtime uncertainty, but record structures are already usable."
                ],
            },
            {
                "workset": "translation_workset_gameplay_terms",
                "status": "ready_conservative",
                "notes": [
                    "Record structures are objective for item/ui/battle/ability/material families.",
                    "Keep translations concise and preserve 0x0B/padding where present."
                ],
            },
            {
                "workset": "translation_workset_registry_d_dialogue",
                "status": "ready_with_multiline_preservation",
                "notes": [
                    "Preserve existing explicit newlines.",
                    "Do not invent extra line breaks until runtime page-flow is visually confirmed."
                ],
            },
            {
                "workset": "registry_a_entry8_clusters_manifest",
                "status": "ready_with_singleline_conservatism",
                "notes": [
                    "Treat records as short counted single-line payloads unless source data explicitly says otherwise.",
                    "Do not insert manual newlines."
                ],
            },
        ],
        "live_playthrough_still_needed_for": [
            "final unseen-string sweep",
            "visual page-turn confirmation for dialogue runtime",
            "image-baked text discovery outside canonical extracted sources",
        ],
        "reading": [
            "Most canonical worksets are translation-ready before live playthrough, as long as source-specific layout rules are followed.",
            "Live playthrough is now primarily a final QA sweep, not a prerequisite for starting translation on known sources.",
            "This report exists to separate 'translation can start' from 'runtime/page QA is fully closed'.",
        ],
        "source_assignment_reference": assignment.get("source_assignments", {}),
    }


def render_md(report: dict) -> str:
    lines = [
        "# Translation Readiness Report",
        "",
        f"- last_updated: `{report['last_updated']}`",
        "",
        "## Worksets",
        "",
    ]
    for item in report["worksets"]:
        lines.append(f"- `{item['workset']}` (`{item['status']}`)")
        for note in item["notes"]:
            lines.append(f"  {note}")
    lines.extend(["", "## Live Playthrough Still Needed For", ""])
    for note in report["live_playthrough_still_needed_for"]:
        lines.append(f"- {note}")
    lines.extend(["", "## Reading", ""])
    for note in report["reading"]:
        lines.append(f"- {note}")
    lines.append("")
    return "\n".join(lines)


def main() -> int:
    report = build()
    OUT_JSON.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    OUT_MD.write_text(render_md(report), encoding="utf-8")
    print(f"wrote {OUT_JSON}")
    print(f"wrote {OUT_MD}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
