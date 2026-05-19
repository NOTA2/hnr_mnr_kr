from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
LAYOUT_INDEX_PATH = ROOT / "confirmed_data" / "text_layout" / "text_layout_assignment_index.json"
AUDIT_PATH = ROOT / "confirmed_data" / "translation_workspace" / "extraction_audit_status.json"
OUTPUT_MD = ROOT / "confirmed_data" / "text_layout" / "runtime_family_focus_report.md"
OUTPUT_JSON = ROOT / "confirmed_data" / "text_layout" / "runtime_family_focus_report.json"


def load_json(path: Path):
    return json.loads(path.read_text())


def main() -> None:
    layout = load_json(LAYOUT_INDEX_PATH)
    audit = load_json(AUDIT_PATH)
    source_assignments = layout["source_assignments"]
    buckets = {"high": [], "medium": [], "low": []}
    for source, meta in source_assignments.items():
        priority = meta.get("runtime_resolution_priority")
        if priority in buckets:
            buckets[priority].append(
                {
                    "source_group": source,
                    "layout_family": meta["layout_family"],
                    "translation_risk": meta.get("translation_risk"),
                    "runtime_candidate_family": meta.get("runtime_candidate_family"),
                    "notes": meta.get("notes", []),
                }
            )

    report = {
        "version": 1,
        "last_updated": "2026-05-18",
        "structural_extraction_status": audit.get("structural_extraction_status"),
        "runtime_resolution_scope": audit.get("runtime_resolution_scope"),
        "operational_note": (
            "Registry D is no longer byte-slot blocked because packed relocation is supported; "
            "its remaining focus is visual page-flow QA. system_messages/save_menu are now "
            "treated as operationally bounded rather than major blockers."
        ),
        "priority_buckets": buckets,
    }
    OUTPUT_JSON.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n")

    lines = [
        "# Runtime Family Focus Report",
        "",
        f"- structural extraction status: `{audit.get('structural_extraction_status')}`",
        "",
        "## High priority",
        "",
    ]
    for item in buckets["high"]:
        lines.append(
            f"- `{item['source_group']}` -> `{item['layout_family']}` "
            f"(risk={item['translation_risk']}, candidate={item.get('runtime_candidate_family')})"
        )
    lines += ["", "## Medium priority", ""]
    for item in buckets["medium"]:
        lines.append(
            f"- `{item['source_group']}` -> `{item['layout_family']}` "
            f"(risk={item['translation_risk']})"
        )
    lines += ["", "## Low priority", ""]
    for item in buckets["low"]:
        lines.append(
            f"- `{item['source_group']}` -> `{item['layout_family']}` "
            f"(risk={item['translation_risk']})"
        )
    lines += [
        "",
        "## Reading",
        "",
        "- High priority items are runtime QA focus areas, not automatically byte-slot blockers.",
        "- `registry_d_fc_script_texts` supports packed relocation, so translate naturally and validate line width/page-flow visually.",
        "- `registry_a_entry8_prefixed_texts` is still a counted script family without equivalent packed relocation, so keep it concise.",
        "- Medium/low groups are structurally extracted and can already be translated with source-family-specific constraints.",
        "- `system_messages` / `save_menu` are operationally bounded: residual uncertainty remains, but they are no longer treated as major runtime blockers.",
        "- This report is meant to keep runtime-family work focused instead of treating all unresolved families as equally risky.",
        "",
    ]
    OUTPUT_MD.write_text("\n".join(lines))
    print(f"Wrote {OUTPUT_MD}")
    print(f"Wrote {OUTPUT_JSON}")


if __name__ == "__main__":
    main()
