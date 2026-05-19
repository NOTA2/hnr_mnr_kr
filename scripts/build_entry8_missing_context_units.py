#!/usr/bin/env python3

from __future__ import annotations

import json
from bisect import bisect_right
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
AUDIT_JSON = ROOT / "analysis" / "entry8_missing_prefixed_records_audit.json"
EXTRACTED = ROOT / "confirmed_data" / "extracted_texts" / "registry_a_entry8_prefixed_texts.json"
OUT_JSON = ROOT / "analysis" / "entry8_missing_context_units.json"
OUT_MD = ROOT / "analysis" / "entry8_missing_context_units.md"


def load_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def control_gap(record: dict, next_record: dict) -> int:
    return int(next_record["header_offset"]) - (int(record["offset"]) + int(record["byte_length"]))


def confidence_for_gap(gap: int | None) -> str:
    if gap is None:
        return "none"
    if gap <= 8:
        return "high"
    if gap <= 32:
        return "medium"
    return "low"


def build() -> dict:
    audit = load_json(AUDIT_JSON)
    missing = sorted(audit["missing_candidates"], key=lambda record: int(record["offset"]))
    existing = sorted(load_json(EXTRACTED), key=lambda record: int(record["offset"]))
    existing_offsets = [int(record["offset"]) for record in existing]

    units = []
    for record in missing:
        offset = int(record["offset"])
        index = bisect_right(existing_offsets, offset)
        next_record = existing[index] if index < len(existing) else None
        gap = control_gap(record, next_record) if next_record else None
        confidence = confidence_for_gap(gap)
        unit_text = record["text"]
        next_payload = None
        if next_record:
            next_payload = {
                "offset": int(next_record["offset"]),
                "offset_hex": f"0x{int(next_record['offset']):06X}",
                "header_offset": int(next_record["header_offset"]),
                "text": next_record.get("text", ""),
                "translation": next_record.get("translation", ""),
            }
            if confidence in {"high", "medium"}:
                unit_text = f"{record['text']}\n{next_record.get('text', '')}"

        units.append(
            {
                "unit_id": f"entry8_missing_context:{offset:06X}",
                "merge_confidence": confidence,
                "control_gap_length": gap,
                "source_text_for_translation": unit_text,
                "missing_record": {
                    "offset": offset,
                    "offset_hex": f"0x{offset:06X}",
                    "header_offset": int(record["header_offset"]),
                    "char_count": int(record["char_count"]),
                    "byte_length": int(record["byte_length"]),
                    "text": record["text"],
                    "translation": "",
                    "before_bytes": record.get("before_bytes"),
                    "after_bytes": record.get("after_bytes"),
                },
                "next_existing_record": next_payload,
                "notes": (
                    "번역/검수에서는 source_text_for_translation 단위로 보고, ROM 적용은 missing_record 와 "
                    "next_existing_record 를 별도 counted 레코드로 나눠 반영한다."
                ),
            }
        )

    return {
        "last_updated": datetime.now(timezone.utc).isoformat(),
        "source_audit": str(AUDIT_JSON.relative_to(ROOT)),
        "summary": {
            "unit_count": len(units),
            "by_merge_confidence": dict(sorted(Counter(unit["merge_confidence"] for unit in units).items())),
        },
        "notes": [
            "짧은 누락 Entry8 레코드를 번역자가 문맥과 함께 볼 수 있도록 뒤쪽 기존 레코드와 묶은 작업용 단위다.",
            "이 파일은 ROM 구조를 합치는 것이 아니다. 실제 ROM에는 01 FF counted 레코드가 분리되어 있으므로 삽입 단계에서는 다시 나눠야 한다.",
            "high 는 제어 gap 이 8바이트 이하라 바로 뒤 문장과 함께 보는 것이 자연스러운 후보, medium 은 32바이트 이하라 문맥 참고 가능 후보, low/none 은 자동 병합하지 않는 후보로 본다.",
        ],
        "units": units,
    }


def render_md(report: dict) -> str:
    lines = [
        "# Entry8 Missing Context Units",
        "",
        f"- Last updated: `{report['last_updated']}`",
        f"- Unit count: `{report['summary']['unit_count']}`",
        f"- By merge confidence: `{report['summary']['by_merge_confidence']}`",
        "",
        "## Reading",
        "",
    ]
    lines.extend(f"- {note}" for note in report["notes"])
    for confidence in ("high", "medium", "low", "none"):
        subset = [unit for unit in report["units"] if unit["merge_confidence"] == confidence]
        if not subset:
            continue
        lines.extend(["", f"## {confidence.title()} Confidence Examples", ""])
        for unit in subset[:80]:
            missing = unit["missing_record"]
            next_record = unit.get("next_existing_record") or {}
            next_text = next_record.get("text", "")
            next_offset = next_record.get("offset_hex", "")
            lines.append(
                f"- `{missing['offset_hex']}` {missing['text']!r} "
                f"gap `{unit['control_gap_length']}` -> `{next_offset}` {next_text!r}"
            )
    return "\n".join(lines).rstrip() + "\n"


def main() -> int:
    report = build()
    OUT_JSON.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    OUT_MD.write_text(render_md(report), encoding="utf-8")
    print(f"written: {OUT_JSON}")
    print(f"written: {OUT_MD}")
    print(json.dumps(report["summary"], ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
