#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import sys
from collections import Counter, defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from gba_kor_tool.translation_normalization import display_units, normalize_translation_text

DEFAULT_WORKSET = ROOT / "confirmed_data/translation_worksets/translation_workset_gameplay_terms.json"
DEFAULT_OUT_DIR = ROOT / "analysis/generated_workbenches/ability_texts_layout_audit"


def escaped(text: str) -> str:
    return text.replace("\x0b", "\\x0B").replace("\n", "\\n")


def split_saved_translation(text: str) -> tuple[str, str, str | None]:
    if "\x0b" in text:
        left, right = text.split("\x0b", 1)
        return left, right, "\x0b"
    if "\n" in text:
        left, right = text.split("\n", 1)
        return left, right, "\n"
    return text, "", None


def audit_rows(rows: list[dict]) -> list[dict]:
    items: list[dict] = []
    for order, row in enumerate(rows):
        if row.get("source_group") != "ability_texts":
            continue
        source = row.get("text", "")
        saved = row.get("translation", "")
        normalized = normalize_translation_text(
            saved,
            source_group="ability_texts",
            reference_text=source,
        )
        entry = {
            "rom_address": row.get("rom_address"),
            "rom_address_hex": f"0x{int(row.get('rom_address', 0)):08X}",
            "offset": row.get("offset"),
            "offset_hex": f"0x{int(row.get('offset', 0)):08X}",
            "order_in_ability": order,
            "source_text": source,
            "saved_translation": saved,
            "normalized_translation": normalized,
            "agent_draft": row.get("agent_draft", ""),
            "byte_length": row.get("byte_length"),
            "notes": [],
            "severity": "ok",
        }
        if "\x0b" not in source:
            if "\x0b" in saved:
                entry["notes"].append("translation_added_0x0b_to_single_line_source")
                entry["severity"] = "medium"
            elif "\n" in saved:
                entry["notes"].append("translation_added_newline_to_single_line_source")
                entry["severity"] = "low"
            items.append(entry)
            continue

        ref_name, ref_desc = source.split("\x0b", 1)
        raw_name, raw_desc, separator = split_saved_translation(saved)
        if separator is None:
            entry["notes"].append("translation_lost_separator")
        elif separator == "\n":
            entry["notes"].append("uses_newline_instead_of_0x0b")

        norm_name, norm_desc, _norm_sep = split_saved_translation(normalized)
        meaning_name = raw_name.replace("　", " ").strip()
        ref_name_units = display_units(ref_name)
        raw_name_units = display_units(meaning_name)
        ref_desc_units = display_units(ref_desc.strip())
        tr_desc_units = display_units(norm_desc.strip())
        entry.update(
            {
                "ref_name": ref_name,
                "ref_desc": ref_desc,
                "ref_name_units": ref_name_units,
                "raw_name": meaning_name,
                "raw_name_units": raw_name_units,
                "raw_desc": raw_desc.strip(),
                "tr_name": norm_name,
                "tr_name_meaning_units": display_units(norm_name.rstrip(" 　")),
                "tr_desc": norm_desc.strip(),
                "tr_desc_units": tr_desc_units,
                "ref_desc_units": ref_desc_units,
                "name_units_remaining_before_padding": ref_name_units - raw_name_units,
            }
        )

        if raw_name_units > ref_name_units:
            entry["notes"].append("name_field_overflow")
            entry["severity"] = "high"
        elif raw_name_units == ref_name_units:
            entry["notes"].append("name_field_exact_no_visual_margin")
            entry["severity"] = "high"
        elif raw_name_units >= ref_name_units - 1:
            entry["notes"].append("name_field_tight_1_unit_margin")
            entry["severity"] = "medium"
        elif raw_name_units >= ref_name_units - 2:
            entry["notes"].append("name_field_tight_2_unit_margin")
            entry["severity"] = "medium"

        if "　" in raw_name or "  " in raw_name:
            entry["notes"].append("manual_padding_before_separator")
            if entry["severity"] == "ok":
                entry["severity"] = "low"

        if tr_desc_units > max(32, ref_desc_units + 8):
            entry["notes"].append("description_much_longer_than_reference")
            if entry["severity"] == "ok":
                entry["severity"] = "low"

        draft = row.get("agent_draft", "")
        if draft:
            normalized_draft = normalize_translation_text(
                draft,
                source_group="ability_texts",
                reference_text=source,
            )
            if normalized_draft != normalized:
                entry["normalized_agent_draft"] = normalized_draft
                if entry["severity"] in {"high", "medium"}:
                    entry["notes"].append("agent_draft_differs")

        items.append(entry)
    return items


def build_report(items: list[dict]) -> dict:
    summary = Counter(item["severity"] for item in items)
    note_counts = Counter(note for item in items for note in item["notes"])
    groups: dict[str, list[dict]] = defaultdict(list)
    for item in items:
        if item["severity"] in {"high", "medium"}:
            groups[item["saved_translation"]].append(item)
    repeated = []
    for translation, grouped_items in groups.items():
        if len(grouped_items) > 1:
            repeated.append(
                {
                    "translation": translation,
                    "count": len(grouped_items),
                    "severity_counts": dict(Counter(item["severity"] for item in grouped_items)),
                    "items": grouped_items,
                }
            )
    repeated.sort(key=lambda group: (-group["count"], group["translation"]))
    return {
        "summary": dict(summary),
        "note_counts": dict(note_counts),
        "total": len(items),
        "with_0x0b_source": sum("\x0b" in item["source_text"] for item in items),
        "candidates": [item for item in items if item["severity"] != "ok"],
        "repeated_risky_translations": repeated,
    }


def write_markdown(report: dict, path: Path) -> None:
    candidates = [item for item in report["candidates"] if item["severity"] in {"high", "medium"}]
    lines = [
        "# ability_texts Layout Candidate Audit",
        "",
        "Criterion: compare the meaningful text before the inline 0x0B separator against the original fixed name-field width. Padding is synthesized by the build normalization, so manual spacing is reported separately.",
        "",
        "## Summary",
        "",
        f"- total ability_texts: {report['total']}",
        f"- source has 0x0B: {report['with_0x0b_source']}",
    ]
    summary = report["summary"]
    for severity in ["high", "medium", "low", "ok"]:
        lines.append(f"- {severity}: {summary.get(severity, 0)}")
    lines.extend(["", "## Note Counts", ""])
    for note, count in sorted(report["note_counts"].items(), key=lambda item: (-item[1], item[0])):
        lines.append(f"- {note}: {count}")
    lines.extend(["", "## High / Medium Candidates", ""])
    for item in candidates:
        lines.append(f"### {item['severity'].upper()} {item['offset_hex']} / {item['rom_address_hex']}")
        lines.append(f"- source: `{escaped(item['source_text'])}`")
        lines.append(f"- saved: `{escaped(item['saved_translation'])}`")
        lines.append(f"- normalized: `{escaped(item['normalized_translation'])}`")
        if "raw_name_units" in item:
            lines.append(
                f"- name units: {item['raw_name_units']} / {item['ref_name_units']} "
                f"(remaining {item['name_units_remaining_before_padding']})"
            )
            lines.append(f"- desc units: {item.get('tr_desc_units')} / ref {item.get('ref_desc_units')}")
        lines.append(f"- notes: {', '.join(item['notes'])}")
        if item.get("normalized_agent_draft"):
            lines.append(f"- agent draft: `{escaped(item['normalized_agent_draft'])}`")
        lines.append("")
    path.write_text("\n".join(lines), encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--workset", type=Path, default=DEFAULT_WORKSET)
    parser.add_argument("--out-dir", type=Path, default=DEFAULT_OUT_DIR)
    args = parser.parse_args()

    rows = json.loads(args.workset.read_text(encoding="utf-8"))
    items = audit_rows(rows)
    report = build_report(items)
    args.out_dir.mkdir(parents=True, exist_ok=True)
    json_path = args.out_dir / "ability_texts_layout_candidates.json"
    md_path = args.out_dir / "ability_texts_layout_candidates.md"
    json_path.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    write_markdown(report, md_path)
    print(f"wrote {json_path}")
    print(f"wrote {md_path}")
    print(f"summary {report['summary']}")
    print(f"high_medium {sum(1 for item in report['candidates'] if item['severity'] in {'high', 'medium'})}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
