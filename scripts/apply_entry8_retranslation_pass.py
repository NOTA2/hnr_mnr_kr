#!/usr/bin/env python3
"""Validate and apply Entry8 retranslation pass proposals.

The proposal files are produced by translation agents and are intentionally kept
separate from the workbench until this script validates them.  This protects
manual edits and fixed Entry8 byte spans.
"""

from __future__ import annotations

import argparse
import json
import re
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
PASS_ROOT = ROOT / "confirmed_data/translation_workspace/entry8_spacing_retranslation_pass"
OUTPUT_DIR = PASS_ROOT / "agent_outputs"
WORKBENCH_PATH = ROOT / "confirmed_data/localization_workbench/workbench_dataset.json"
CLUSTER_DIR = ROOT / "confirmed_data/translation_workspace/registry_a_entry8_clusters"
REPORT_JSON = PASS_ROOT / "apply_report.json"
REPORT_MD = PASS_ROOT / "apply_report.md"

ENTRY8_SOURCE_GROUP = "registry_a_entry8_prefixed_texts"

UNSPLITTABLE_TERMS = [
    "코넬로",
    "레돈드",
    "솔링",
    "다이무라",
    "마틴스",
    "아스턴",
    "호크아이",
    "머스탱",
    "암스트롱",
    "브래드레이",
    "알폰스",
    "에드워드",
    "엘릭",
    "윈리",
    "피나코",
    "휴즈",
    "코니슈",
    "링커",
    "리젠블",
    "리올",
    "센트럴",
    "이스트",
    "키메라",
    "오토메일",
]

JAPANESE_RE = re.compile(r"[\u3040-\u30ff\u3400-\u4dbf\u4e00-\u9fff]")
ASCII_SPACE_RE = re.compile(r" ")
SPACE_AFTER_PUNCT_RE = re.compile(r"[、。！？…「」『』（）]\u3000")


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, data: Any) -> None:
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def used_bytes(text: str) -> int:
    return len(text.encode("utf-8"))


def compact_spaces(text: str) -> str:
    return text.replace(" ", "").replace("\u3000", "")


def term_is_split(text: str, term: str) -> bool:
    if term not in compact_spaces(text):
        return False
    pattern = "[ \u3000]*".join(re.escape(ch) for ch in term)
    match = re.search(pattern, text)
    return bool(match and match.group(0) != term)


def item_capacity(item: dict[str, Any]) -> int:
    capacity = item.get("byte_capacity")
    if capacity is None:
        capacity = item.get("byte_length")
    if capacity is None:
        raise ValueError(f"missing capacity for {item.get('item_id')}")
    return int(capacity)


def load_proposals() -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    proposals: list[dict[str, Any]] = []
    load_errors: list[dict[str, Any]] = []
    for path in sorted(OUTPUT_DIR.glob("*.proposals.json")):
        try:
            data = load_json(path)
            if not isinstance(data, list):
                raise TypeError("proposal file must be a JSON array")
            for row in data:
                if isinstance(row, dict):
                    row = dict(row)
                    row["_proposal_file"] = str(path.relative_to(ROOT))
                    proposals.append(row)
                else:
                    load_errors.append({"file": str(path), "reason": "proposal row is not an object"})
        except Exception as exc:  # noqa: BLE001 - report all malformed agent output.
            load_errors.append({"file": str(path), "reason": str(exc)})
    return proposals, load_errors


def validate_proposal(
    proposal: dict[str, Any],
    item_by_id: dict[str, dict[str, Any]],
    seen: dict[str, str],
) -> tuple[bool, str, dict[str, Any] | None]:
    item_id = proposal.get("item_id")
    if not isinstance(item_id, str) or not item_id:
        return False, "missing_item_id", None

    proposed = proposal.get("proposed_translation")
    current_seen = proposal.get("current_translation")
    if not isinstance(proposed, str):
        return False, "missing_proposed_translation", None
    if not isinstance(current_seen, str):
        return False, "missing_current_translation", None

    item = item_by_id.get(item_id)
    if item is None:
        return False, "unknown_item", None
    if item.get("source_group") != ENTRY8_SOURCE_GROUP:
        return False, "not_entry8", None

    current = item.get("translation") or item.get("effective_translation") or ""
    if current != current_seen:
        return False, "stale_current_value", None
    if proposed == current:
        return False, "unchanged", None
    if item_id in seen and seen[item_id] != proposed:
        return False, "duplicate_conflict", None
    seen[item_id] = proposed

    if ASCII_SPACE_RE.search(proposed):
        return False, "halfwidth_space", None
    if SPACE_AFTER_PUNCT_RE.search(proposed):
        return False, "space_after_punctuation", None
    if JAPANESE_RE.search(proposed):
        return False, "japanese_remaining", None
    if compact_spaces(proposed) != compact_spaces(current):
        return False, "non_spacing_change", None

    capacity = item_capacity(item)
    proposed_used = used_bytes(proposed)
    if proposed_used > capacity:
        return False, "byte_overflow", None

    for term in UNSPLITTABLE_TERMS:
        if term_is_split(proposed, term):
            return False, f"split_term:{term}", None

    accepted = {
        "item_id": item_id,
        "group_id": item.get("group_id"),
        "offset": item.get("offset"),
        "current_translation": current,
        "proposed_translation": proposed,
        "capacity_bytes": capacity,
        "current_used_bytes": used_bytes(current),
        "proposed_used_bytes": proposed_used,
        "reason": proposal.get("reason", ""),
        "proposal_file": proposal.get("_proposal_file"),
    }
    return True, "accepted", accepted


def apply_to_workbench(workbench: dict[str, Any], accepted: list[dict[str, Any]]) -> None:
    item_by_id = {item["item_id"]: item for item in workbench["items"]}
    for row in accepted:
        item = item_by_id[row["item_id"]]
        old = row["current_translation"]
        new = row["proposed_translation"]
        item["translation"] = new
        item["effective_translation"] = new
        if item.get("agent_draft") == old:
            item["agent_draft"] = new
        item["translation_source"] = "entry8_spacing_retranslation_pass"


def apply_to_clusters(accepted: list[dict[str, Any]]) -> dict[str, int]:
    by_group: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in accepted:
        by_group[row["group_id"]].append(row)

    updated_counts: dict[str, int] = {}
    for group_id, rows in sorted(by_group.items()):
        path = CLUSTER_DIR / f"{group_id}.json"
        records = load_json(path)
        by_offset = {int(record["offset"]): record for record in records}
        updated = 0
        for row in rows:
            record = by_offset.get(int(row["offset"]))
            if record is None:
                raise KeyError(f"cluster record missing: {group_id} offset {row['offset']}")
            if record.get("translation") != row["current_translation"]:
                raise ValueError(
                    f"cluster stale: {group_id} {row['item_id']} "
                    f"{record.get('translation')!r} != {row['current_translation']!r}"
                )
            record["translation"] = row["proposed_translation"]
            updated += 1
        write_json(path, records)
        updated_counts[group_id] = updated
    return updated_counts


def render_report(report: dict[str, Any]) -> str:
    lines = [
        "# Entry8 Retranslation Pass Apply Report",
        "",
        f"- Mode: `{report['mode']}`",
        f"- Proposal files: {report['proposal_files']}",
        f"- Total proposals: {report['total_proposals']}",
        f"- Accepted: {report['accepted_count']}",
        f"- Rejected: {report['rejected_count']}",
        "",
        "## Reject Reasons",
    ]
    for reason, count in sorted(report["reject_reasons"].items()):
        lines.append(f"- `{reason}`: {count}")
    lines.extend(["", "## Applied By Group"])
    for group_id, count in sorted(report["applied_by_group"].items()):
        lines.append(f"- `{group_id}`: {count}")
    lines.extend(["", "## Accepted Samples"])
    for row in report["accepted_samples"]:
        lines.append(
            f"- `{row['item_id']}`: `{row['current_translation']}` -> "
            f"`{row['proposed_translation']}` ({row['proposed_used_bytes']}/{row['capacity_bytes']} bytes)"
        )
    lines.extend(["", "## Rejected Samples"])
    for row in report["rejected_samples"]:
        lines.append(f"- `{row['item_id']}` `{row['reason']}`: {row.get('proposed_translation', '')}")
    lines.append("")
    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--apply", action="store_true", help="write accepted proposals into source data")
    args = parser.parse_args()

    workbench = load_json(WORKBENCH_PATH)
    item_by_id = {item["item_id"]: item for item in workbench["items"]}
    proposals, load_errors = load_proposals()

    seen: dict[str, str] = {}
    accepted: list[dict[str, Any]] = []
    rejected: list[dict[str, Any]] = []
    reasons: Counter[str] = Counter()

    for proposal in proposals:
        ok, reason, accepted_row = validate_proposal(proposal, item_by_id, seen)
        if ok and accepted_row:
            accepted.append(accepted_row)
        else:
            reasons[reason] += 1
            rejected.append(
                {
                    "item_id": proposal.get("item_id"),
                    "reason": reason,
                    "current_translation": proposal.get("current_translation"),
                    "proposed_translation": proposal.get("proposed_translation"),
                    "proposal_file": proposal.get("_proposal_file"),
                }
            )
    for error in load_errors:
        reasons["load_error"] += 1
        rejected.append({"item_id": error.get("file"), "reason": error.get("reason")})

    applied_by_group: dict[str, int] = {}
    if args.apply:
        apply_to_workbench(workbench, accepted)
        applied_by_group = apply_to_clusters(accepted)
        workbench["last_updated"] = datetime.now(timezone.utc).isoformat()
        write_json(WORKBENCH_PATH, workbench)
    else:
        applied_by_group = dict(Counter(row["group_id"] for row in accepted))

    report = {
        "mode": "apply" if args.apply else "dry-run",
        "proposal_files": len(list(OUTPUT_DIR.glob("*.proposals.json"))),
        "total_proposals": len(proposals),
        "accepted_count": len(accepted),
        "rejected_count": len(rejected),
        "reject_reasons": dict(reasons),
        "applied_by_group": applied_by_group,
        "accepted": accepted,
        "rejected": rejected,
        "accepted_samples": accepted[:30],
        "rejected_samples": rejected[:30],
    }
    write_json(REPORT_JSON, report)
    REPORT_MD.write_text(render_report(report), encoding="utf-8")
    print(json.dumps({k: report[k] for k in ["mode", "total_proposals", "accepted_count", "rejected_count", "reject_reasons", "applied_by_group"]}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
