#!/usr/bin/env python3
"""Validate and apply Entry8 suspect-cluster retranslation proposals."""

from __future__ import annotations

import argparse
import json
import re
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
PASS_ROOT = ROOT / "confirmed_data/translation_workspace/entry8_suspect_retranslation_v2"
OUTPUT_DIR = PASS_ROOT / "agent_outputs"
WORKBENCH_PATH = ROOT / "confirmed_data/localization_workbench/workbench_dataset.json"
CLUSTER_DIR = ROOT / "confirmed_data/translation_workspace/registry_a_entry8_clusters"
REPORT_JSON = PASS_ROOT / "apply_report.json"
REPORT_MD = PASS_ROOT / "apply_report.md"

ENTRY8_SOURCE_GROUP = "registry_a_entry8_prefixed_texts"
JAPANESE_RE = re.compile(r"[\u3040-\u30ff\u3400-\u4dbf\u4e00-\u9fff]")
ASCII_SPACE_RE = re.compile(r" ")
SPACE_AFTER_PUNCT_RE = re.compile(r"[、。！？…「」『』（）]\u3000")

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

SPACED_TERM_RESTORES = [
    ("현자의돌", "현자의\u3000돌"),
    ("국가연금술사", "국가\u3000연금술사"),
    ("마틴스중령", "마틴스\u3000중령"),
    ("호크아이중위", "호크아이\u3000중위"),
    ("머스탱대령", "머스탱\u3000대령"),
    ("로이스대령", "로이스\u3000대령"),
    ("암스트롱소령", "암스트롱\u3000소령"),
]


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, data: Any) -> None:
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def display_chars(text: str) -> int:
    return len(text)


def compact_spaces(text: str) -> str:
    return text.replace(" ", "").replace("\u3000", "")


def max_chars(item: dict[str, Any]) -> int:
    value = item.get("max_korean_chars") or item.get("char_count")
    if value is None:
        value = (item.get("byte_length") or 0) // 2
    return int(value)


def term_is_split(text: str, term: str) -> bool:
    if term not in compact_spaces(text):
        return False
    pattern = "[ \u3000]*".join(re.escape(ch) for ch in term)
    match = re.search(pattern, text)
    return bool(match and match.group(0) != term)


def load_proposals() -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    rows: list[dict[str, Any]] = []
    errors: list[dict[str, Any]] = []
    for path in sorted(OUTPUT_DIR.glob("*.proposals.json")):
        try:
            data = load_json(path)
            if not isinstance(data, list):
                raise TypeError("proposal file must be a JSON array")
            for row in data:
                if not isinstance(row, dict):
                    errors.append({"file": str(path), "reason": "row_not_object"})
                    continue
                item = dict(row)
                item["_proposal_file"] = str(path.relative_to(ROOT))
                rows.append(item)
        except Exception as exc:  # noqa: BLE001
            errors.append({"file": str(path), "reason": str(exc)})
    return rows, errors


def validate(
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

    limit = max_chars(item)
    chars = display_chars(proposed)
    if chars > limit:
        return False, "char_overflow", None
    if ASCII_SPACE_RE.search(proposed):
        return False, "halfwidth_space", None
    if SPACE_AFTER_PUNCT_RE.search(proposed):
        return False, "space_after_punctuation", None
    if JAPANESE_RE.search(proposed):
        return False, "japanese_remaining", None
    for compact, spaced in SPACED_TERM_RESTORES:
        if compact in proposed and len(proposed.replace(compact, spaced, 1)) <= max_chars(item):
            return False, f"missing_term_space:{compact}", None
    for term in UNSPLITTABLE_TERMS:
        if term_is_split(proposed, term):
            return False, f"split_term:{term}", None

    return True, "accepted", {
        "item_id": item_id,
        "group_id": item.get("group_id"),
        "offset": item.get("offset"),
        "source": item.get("text", ""),
        "current_translation": current,
        "proposed_translation": proposed,
        "max_korean_chars": limit,
        "proposed_chars": chars,
        "reason": proposal.get("reason", ""),
        "proposal_file": proposal.get("_proposal_file", ""),
    }


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
        item["translation_source"] = "entry8_suspect_retranslation_v2"


def apply_to_clusters(accepted: list[dict[str, Any]]) -> dict[str, int]:
    by_group: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in accepted:
        by_group[row["group_id"]].append(row)

    counts: dict[str, int] = {}
    for group_id, rows in sorted(by_group.items()):
        path = CLUSTER_DIR / f"{group_id}.json"
        data = load_json(path)
        by_offset = {int(row["offset"]): row for row in data}
        count = 0
        for row in rows:
            record = by_offset.get(int(row["offset"]))
            if record is None:
                raise KeyError(f"missing cluster row {group_id}:{row['offset']}")
            if record.get("translation") != row["current_translation"]:
                raise ValueError(f"stale cluster row {row['item_id']}")
            record["translation"] = row["proposed_translation"]
            count += 1
        write_json(path, data)
        counts[group_id] = count
    return counts


def render_report(report: dict[str, Any]) -> str:
    lines = [
        "# Entry8 Suspect Retranslation V2 Apply Report",
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
            f"`{row['proposed_translation']}` ({row['proposed_chars']}/{row['max_korean_chars']} chars)"
        )
    lines.extend(["", "## Rejected Samples"])
    for row in report["rejected_samples"]:
        lines.append(f"- `{row.get('item_id')}` `{row.get('reason')}`: `{row.get('proposed_translation', '')}`")
    lines.append("")
    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--apply", action="store_true")
    args = parser.parse_args()

    workbench = load_json(WORKBENCH_PATH)
    item_by_id = {item["item_id"]: item for item in workbench["items"]}
    proposals, load_errors = load_proposals()

    seen: dict[str, str] = {}
    accepted: list[dict[str, Any]] = []
    rejected: list[dict[str, Any]] = []
    reasons: Counter[str] = Counter()
    for proposal in proposals:
        ok, reason, row = validate(proposal, item_by_id, seen)
        if ok and row:
            accepted.append(row)
        else:
            reasons[reason] += 1
            rejected.append({
                "item_id": proposal.get("item_id"),
                "reason": reason,
                "current_translation": proposal.get("current_translation"),
                "proposed_translation": proposal.get("proposed_translation"),
                "proposal_file": proposal.get("_proposal_file"),
            })
    for err in load_errors:
        reasons["load_error"] += 1
        rejected.append({"item_id": err.get("file"), "reason": err.get("reason")})

    applied_by_group: dict[str, int]
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
        "accepted_samples": accepted[:50],
        "rejected_samples": rejected[:50],
    }
    write_json(REPORT_JSON, report)
    REPORT_MD.write_text(render_report(report), encoding="utf-8")
    print(json.dumps({k: report[k] for k in ["mode", "total_proposals", "accepted_count", "rejected_count", "reject_reasons", "applied_by_group"]}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
