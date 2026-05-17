#!/usr/bin/env python3

from __future__ import annotations

import argparse
import json
from datetime import datetime
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
WORKBENCH_DIR = ROOT / "confirmed_data" / "localization_workbench"
DATASET_PATH = WORKBENCH_DIR / "workbench_dataset.json"
SPEAKERS_PATH = WORKBENCH_DIR / "speaker_aliases.json"
IMPORT_REPORT_DIR = WORKBENCH_DIR / "import_reports"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="번역 에이전트 결과 JSON을 localization workbench dataset에 병합합니다."
    )
    parser.add_argument("input_json", help="번역 에이전트 결과 JSON 경로")
    parser.add_argument(
        "--report",
        help="기본값은 confirmed_data/localization_workbench/import_reports 아래 자동 생성",
    )
    return parser.parse_args()


def load_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, payload) -> None:
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def normalize_records(payload) -> list[dict]:
    if isinstance(payload, list):
        return payload
    if isinstance(payload, dict):
        for key in ("items", "records", "translations"):
            value = payload.get(key)
            if isinstance(value, list):
                return value
    raise ValueError("지원하지 않는 번역 결과 JSON 형식입니다.")


def item_match_key(item: dict) -> tuple[str | None, int | None, str | None]:
    return (
        item.get("item_id"),
        int(item["offset"]) if item.get("offset") is not None else None,
        item.get("source_group"),
    )


def source_label(record: dict) -> str:
    parts = []
    if record.get("item_id"):
        parts.append(f"item_id={record['item_id']}")
    if record.get("offset") is not None:
        parts.append(f"offset=0x{int(record['offset']):08X}")
    if record.get("source_group"):
        parts.append(f"source_group={record['source_group']}")
    return ", ".join(parts) or "<unknown>"


def build_index(items: list[dict]) -> tuple[dict[str, dict], dict[tuple[int, str], dict], dict[int, list[dict]]]:
    by_item_id: dict[str, dict] = {}
    by_offset_source: dict[tuple[int, str], dict] = {}
    by_offset_only: dict[int, list[dict]] = {}

    for item in items:
        if item.get("item_id"):
            by_item_id[item["item_id"]] = item
        if item.get("offset") is not None and item.get("source_group"):
            by_offset_source[(int(item["offset"]), item["source_group"])] = item
        if item.get("offset") is not None:
            by_offset_only.setdefault(int(item["offset"]), []).append(item)
    return by_item_id, by_offset_source, by_offset_only


def resolve_target(record: dict, by_item_id: dict[str, dict], by_offset_source: dict[tuple[int, str], dict], by_offset_only: dict[int, list[dict]]) -> dict | None:
    item_id = record.get("item_id")
    if item_id and item_id in by_item_id:
        return by_item_id[item_id]

    offset = record.get("offset")
    source_group = record.get("source_group")
    if offset is not None and source_group:
        return by_offset_source.get((int(offset), source_group))

    if offset is not None:
        candidates = by_offset_only.get(int(offset), [])
        if len(candidates) == 1:
            return candidates[0]
    return None


def merge_record(target: dict, record: dict) -> str:
    translation = record.get("translation", "")
    comment = record.get("agent_comment") or record.get("notes") or ""

    if target.get("manual_locked"):
        if translation:
            target["agent_draft"] = translation
            target["agent_comment"] = comment or "수동 잠금 항목: 에이전트 초안을 참고만 함"
        elif comment:
            target["agent_comment"] = comment
        return "locked_preserved"

    if translation:
        target["agent_draft"] = translation
        target["translation"] = translation
        target["effective_translation"] = translation
        target["translation_source"] = "agent_import"
    if comment:
        target["agent_comment"] = comment
    if record.get("progress_status"):
        target["progress_status"] = record["progress_status"]
    return "applied" if translation else "comment_only"


def main() -> int:
    args = parse_args()
    input_path = Path(args.input_json).resolve()
    dataset = load_json(DATASET_PATH)
    records = normalize_records(load_json(input_path))
    by_item_id, by_offset_source, by_offset_only = build_index(dataset["items"])

    summary = {
        "source_file": str(input_path.relative_to(ROOT) if input_path.is_relative_to(ROOT) else input_path),
        "imported_at": datetime.now().isoformat(timespec="seconds"),
        "record_count": len(records),
        "applied_count": 0,
        "locked_preserved_count": 0,
        "comment_only_count": 0,
        "unmatched_count": 0,
        "unmatched": [],
    }

    for record in records:
        target = resolve_target(record, by_item_id, by_offset_source, by_offset_only)
        if not target:
            summary["unmatched_count"] += 1
            summary["unmatched"].append(source_label(record))
            continue
        result = merge_record(target, record)
        if result == "applied":
            summary["applied_count"] += 1
        elif result == "locked_preserved":
            summary["locked_preserved_count"] += 1
        elif result == "comment_only":
            summary["comment_only_count"] += 1

    write_json(DATASET_PATH, dataset)

    IMPORT_REPORT_DIR.mkdir(parents=True, exist_ok=True)
    report_path = Path(args.report) if args.report else IMPORT_REPORT_DIR / f"{input_path.stem}_import_report.json"
    if not report_path.is_absolute():
        report_path = (ROOT / report_path).resolve()
    write_json(report_path, summary)

    print(f"dataset updated: {DATASET_PATH}")
    print(f"report written: {report_path}")
    print(
        "applied={applied_count} locked_preserved={locked_preserved_count} "
        "comment_only={comment_only_count} unmatched={unmatched_count}".format(**summary)
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
