#!/usr/bin/env python3

from __future__ import annotations

import json
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BATCH_DIR = ROOT / "confirmed_data" / "translation_workspace" / "entry8_full_retranslation" / "batches"
OUT_JSON = ROOT / "confirmed_data" / "translation_workspace" / "entry8_full_retranslation" / "audit.json"
OUT_MD = ROOT / "confirmed_data" / "translation_workspace" / "entry8_full_retranslation" / "audit.md"


def load_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def normalized_len(text: str) -> int:
    return len(text.replace("\r\n", "\n").replace("\r", "\n"))


def build() -> dict:
    part_summaries = []
    issues = []
    totals = Counter()
    policy_counts = Counter()
    for path in sorted(BATCH_DIR.glob("part_[0-9][0-9].json")):
        payload = load_json(path)
        part_counter = Counter()
        for unit in payload.get("units", []):
            if not unit.get("translation_text"):
                issues.append(
                    {
                        "part": payload.get("part"),
                        "unit_id": unit.get("unit_id"),
                        "kind": "missing_unit_translation_text",
                        "source_text": unit.get("source_text", ""),
                    }
                )
                part_counter["missing_unit_translation_text"] += 1
            for record in unit.get("records", []):
                totals["records"] += 1
                policy_counts[record.get("length_policy", "")] += 1
                translation = record.get("translation", "")
                if not translation:
                    issues.append(
                        {
                            "part": payload.get("part"),
                            "unit_id": unit.get("unit_id"),
                            "offset": record.get("offset_hex"),
                            "kind": "missing_record_translation",
                            "text": record.get("text", ""),
                        }
                    )
                    part_counter["missing_record_translation"] += 1
                    continue
                max_chars = record.get("max_korean_chars")
                if max_chars is not None and normalized_len(translation) > int(max_chars):
                    issues.append(
                        {
                            "part": payload.get("part"),
                            "unit_id": unit.get("unit_id"),
                            "offset": record.get("offset_hex"),
                            "kind": "translation_too_long",
                            "max_korean_chars": max_chars,
                            "translation_len": normalized_len(translation),
                            "text": record.get("text", ""),
                            "translation": translation,
                        }
                    )
                    part_counter["translation_too_long"] += 1
        part_summaries.append(
            {
                "part": payload.get("part"),
                "path": str(path.relative_to(ROOT)),
                "status": payload.get("status", ""),
                "unit_count": payload.get("unit_count", 0),
                "record_count": payload.get("record_count", 0),
                "issues": dict(part_counter),
            }
        )
    return {
        "summary": {
            "record_count": totals["records"],
            "issue_count": len(issues),
            "policy_counts": dict(policy_counts),
        },
        "parts": part_summaries,
        "issues": issues,
    }


def render_md(report: dict) -> str:
    lines = [
        "# Entry8 Retranslation Batch Audit",
        "",
        f"- Records: `{report['summary']['record_count']}`",
        f"- Issues: `{report['summary']['issue_count']}`",
        f"- Policies: `{report['summary']['policy_counts']}`",
        "",
        "## Parts",
        "",
        "| Part | Status | Units | Records | Issues |",
        "|---:|---|---:|---:|---|",
    ]
    for part in report["parts"]:
        lines.append(
            f"| {part['part']} | {part['status']} | {part['unit_count']} | {part['record_count']} | `{part['issues']}` |"
        )
    lines.extend(["", "## First Issues", ""])
    for issue in report["issues"][:200]:
        offset = issue.get("offset", "")
        lines.append(f"- part `{issue.get('part')}` {offset} `{issue['kind']}`: {issue.get('text')!r}")
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
