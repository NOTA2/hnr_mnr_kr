#!/usr/bin/env python3

from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DATA_ROOT = ROOT / "confirmed_data"
EXTRACTED_ROOT = DATA_ROOT / "extracted_texts"
WORKSETS_ROOT = DATA_ROOT / "translation_worksets"
OUT_JSON = DATA_ROOT / "translation_workspace" / "workset_coverage_audit.json"
OUT_MD = DATA_ROOT / "translation_workspace" / "workset_coverage_audit.md"


def load_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


SOURCE_MAP = [
    ("startup_intro_texts", "startup_intro_texts", "translation_workset_opening_intro", "full_expected"),
    ("system_messages", "system_messages", "translation_workset_core_ui", "full_expected"),
    ("save_menu_prefixed_texts", "save_menu_texts", "translation_workset_core_ui", "full_expected"),
    ("location_texts", "location_texts", "translation_workset_core_ui", "full_expected"),
    ("ui_skill_texts", "ui_skill_texts", "translation_workset_core_ui", "full_expected"),
    ("item_texts", "item_texts", "translation_workset_gameplay_terms", "full_expected"),
    ("material_texts", "material_texts", "translation_workset_gameplay_terms", "full_expected"),
    ("battle_texts", "battle_texts", "translation_workset_gameplay_terms", "full_expected"),
    ("ability_texts", "ability_texts", "translation_workset_gameplay_terms", "full_expected"),
    ("registry_a_entry12_texts", "registry_a_entry12_texts", "translation_workset_gameplay_terms", "full_expected"),
    ("registry_d_fc_script_texts", "registry_d_fc_script_texts", "translation_workset_registry_d_dialogue", "full_expected"),
    ("credits_texts", "credits_texts", "translation_workset_credits", "full_expected"),
]


def main() -> int:
    workset_records: dict[str, list[dict]] = {}
    for path in WORKSETS_ROOT.glob("*.json"):
        workset_records[path.stem] = load_json(path)

    covered_by_group: dict[str, set[int]] = {}
    covered_by_group_and_workset: dict[tuple[str, str], set[int]] = {}
    for workset_id, records in workset_records.items():
        for record in records:
            group = record["source_group"]
            offset = int(record["offset"])
            covered_by_group.setdefault(group, set()).add(offset)
            covered_by_group_and_workset.setdefault((group, workset_id), set()).add(offset)

    rows = []
    for extracted_name, source_group, expected_workset, expectation in SOURCE_MAP:
        records = load_json(EXTRACTED_ROOT / f"{extracted_name}.json")
        extracted_offsets = {int(record["offset"]) for record in records}
        covered_offsets = covered_by_group.get(source_group, set())
        expected_offsets = covered_by_group_and_workset.get((source_group, expected_workset), set()) if expected_workset else set()
        missing_offsets = sorted(extracted_offsets - expected_offsets) if expected_workset else sorted(extracted_offsets - covered_offsets)
        missing_records = [
            {
                "offset": record["offset"],
                "text": record["text"],
            }
            for record in records
            if int(record["offset"]) in missing_offsets
        ]
        rows.append(
            {
                "extracted_name": extracted_name,
                "source_group": source_group,
                "expected_workset": expected_workset,
                "expectation": expectation,
                "extracted_count": len(extracted_offsets),
                "covered_count": len(expected_offsets) if expected_workset else len(covered_offsets),
                "missing_count": len(missing_offsets),
                "missing_records": missing_records,
            }
        )

    status = {
        "version": 1,
        "last_updated": "2026-05-18",
        "rows": rows,
    }
    OUT_JSON.write_text(json.dumps(status, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    lines = [
        "# Workset Coverage Audit",
        "",
        "- 마지막 갱신: `2026-05-18`",
        "- 목적: 추출본이 정식 번역 workset에 제대로 편입됐는지 확인한다.",
        "",
        "## source별 상태",
        "",
    ]
    for row in rows:
        lines.append(f"### `{row['extracted_name']}`")
        lines.append("")
        lines.append(f"- source_group: `{row['source_group']}`")
        lines.append(f"- 기대 workset: `{row['expected_workset'] or '없음'}`")
        lines.append(f"- 기대 상태: `{row['expectation']}`")
        lines.append(f"- 추출 수: `{row['extracted_count']}`")
        lines.append(f"- 편입 수: `{row['covered_count']}`")
        lines.append(f"- 누락 수: `{row['missing_count']}`")
        if row["missing_records"]:
            lines.append("- 누락 항목:")
            for record in row["missing_records"][:12]:
                lines.append(f"  - `0x{int(record['offset']):06X}` `{record['text']}`")
        lines.append("")
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"wrote {OUT_JSON}")
    print(f"wrote {OUT_MD}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
