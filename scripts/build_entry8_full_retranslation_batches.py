#!/usr/bin/env python3

from __future__ import annotations

import json
import math
import struct
import sys
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from gba_kor_tool.cli import scan_prefixed_text_records

ROM_BASE = 0x08000000
REGISTRY_A_TABLE_OFFSET = 0x17C2F4
REGISTRY_A_ENTRY8_INDEX = 8

JP_ROM = ROOT / "Hagane no Renkinjutsushi - Meisou no Rondo (Japan).gba"
CLUSTER_MANIFEST = ROOT / "confirmed_data" / "translation_workspace" / "registry_a_entry8_clusters_manifest.json"
WORKBENCH_DATASET = ROOT / "confirmed_data" / "localization_workbench" / "workbench_dataset.json"
REPOINT_SETS = ROOT / "analysis" / "entry8_structural_repoint_sets.json"
STATE_INDEX = ROOT / "confirmed_data" / "dialogue_metadata" / "entry8_dialogue_state_index.json"
OUT_DIR = ROOT / "confirmed_data" / "translation_workspace" / "entry8_full_retranslation"
BATCH_DIR = OUT_DIR / "batches"
MANIFEST = OUT_DIR / "manifest.json"
README = OUT_DIR / "README.md"


def load_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, payload: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def read_entry8_bounds(data: bytes) -> tuple[int, int]:
    table = REGISTRY_A_TABLE_OFFSET + REGISTRY_A_ENTRY8_INDEX * 8
    entry_offset = struct.unpack_from("<I", data, table)[0] - ROM_BASE
    entry_length = struct.unpack_from("<I", data, table + 4)[0]
    return entry_offset, entry_offset + entry_length


def load_existing_translation_index() -> dict[int, str]:
    index: dict[int, str] = {}
    dataset = load_json(WORKBENCH_DATASET)
    for item in dataset.get("items", []):
        if item.get("source_group") != "registry_a_entry8_prefixed_texts" or item.get("offset") is None:
            continue
        translation = item.get("translation") or item.get("agent_draft") or ""
        if translation:
            index[int(item["offset"])] = translation
    return index


def load_cluster_index() -> list[dict]:
    clusters = load_json(CLUSTER_MANIFEST)["clusters"]
    return sorted(clusters, key=lambda item: int(item["range"]["start_offset"]))


def find_cluster(record_offset: int, clusters: list[dict]) -> dict | None:
    for cluster in clusters:
        start = int(cluster["range"]["start_offset"])
        end = int(cluster["range"]["end_offset_exclusive"])
        if start <= record_offset < end:
            return cluster
    return None


def load_state_tokens() -> dict[int, str | None]:
    if not STATE_INDEX.exists():
        return {}
    state = load_json(STATE_INDEX)
    return {int(record["offset"]): record.get("dialogue_state_token") for record in state.get("records", [])}


def control_gap(left: dict, right: dict) -> int:
    return int(right["header_offset"]) - (int(left["offset"]) + int(left["byte_length"]))


def should_join(left: dict, right: dict, unit: list[dict]) -> bool:
    gap = control_gap(left, right)
    if gap < 0 or gap > 32:
        return False
    if len(unit) >= 4:
        return False
    left_short = int(left["char_count"]) <= 3
    right_short = int(right["char_count"]) <= 3
    if left_short or right_short:
        return True
    if gap <= 8:
        return True
    if left.get("dialogue_state_token") and left.get("dialogue_state_token") == right.get("dialogue_state_token"):
        return True
    return False


def classify_length_policy(offset: int, safe_repoint_offsets: set[int], candidate_repoint_offsets: set[int]) -> str:
    if offset in safe_repoint_offsets:
        return "confirmed_repoint"
    if offset in candidate_repoint_offsets:
        return "candidate_repoint_keep_conservative"
    return "fixed_slot"


def build_records() -> list[dict]:
    data = JP_ROM.read_bytes()
    start, end = read_entry8_bounds(data)
    scanned = scan_prefixed_text_records(
        data,
        start=start,
        end=end,
        prefix=bytes.fromhex("01 ff"),
        count_size=2,
        count_endian="little",
        encoding="cp932",
        min_chars=1,
        max_chars=128,
        require_non_ascii=True,
        require_japanese_text=False,
        min_japanese_ratio=0.5,
        limit=None,
        preview_bytes=12,
    )
    existing_translations = load_existing_translation_index()
    clusters = load_cluster_index()
    state_tokens = load_state_tokens()
    repoint_sets = load_json(REPOINT_SETS)
    safe_repoint_offsets = {int(offset) for offset in repoint_sets["safe_tail_baseline"]["offsets"]}
    candidate_repoint_offsets = {int(offset) for offset in repoint_sets["structural_all_unprotected"]["offsets"]}

    records = []
    for record in sorted(scanned, key=lambda item: int(item["offset"])):
        offset = int(record["offset"])
        cluster = find_cluster(offset, clusters)
        policy = classify_length_policy(offset, safe_repoint_offsets, candidate_repoint_offsets)
        records.append(
            {
                "offset": offset,
                "offset_hex": f"0x{offset:06X}",
                "header_offset": int(record["header_offset"]),
                "header_offset_hex": f"0x{int(record['header_offset']):06X}",
                "char_count": int(record["char_count"]),
                "byte_length": int(record["byte_length"]),
                "max_korean_chars": None if policy == "confirmed_repoint" else int(record["char_count"]),
                "length_guidance": (
                    "length_flexible_repoint_natural"
                    if policy == "confirmed_repoint"
                    else "use_available_capacity_preserve_meaning"
                ),
                "length_policy": policy,
                "text": record["text"],
                "previous_translation_reference": existing_translations.get(offset, ""),
                "translation": "",
                "notes": "",
                "cluster_index": None if cluster is None else int(cluster["cluster_index"]),
                "cluster_primary_tag": "" if cluster is None else cluster.get("primary_tag", ""),
                "dialogue_state_token": state_tokens.get(offset),
                "before_bytes": record.get("before_bytes", ""),
                "after_bytes": record.get("after_bytes", ""),
            }
        )
    return records


def build_units(records: list[dict]) -> list[dict]:
    units = []
    cursor = 0
    while cursor < len(records):
        unit_records = [records[cursor]]
        cursor += 1
        while cursor < len(records) and should_join(unit_records[-1], records[cursor], unit_records):
            unit_records.append(records[cursor])
            cursor += 1

        first = unit_records[0]
        last = unit_records[-1]
        units.append(
            {
                "unit_id": f"entry8_unit:{first['offset']:06X}",
                "cluster_index": first["cluster_index"],
                "cluster_primary_tag": first["cluster_primary_tag"],
                "record_count": len(unit_records),
                "offsets": [record["offset"] for record in unit_records],
                "offsets_hex": [record["offset_hex"] for record in unit_records],
                "source_text": "\n".join(record["text"] for record in unit_records),
                "translation_text": "",
                "length_policy_summary": dict(Counter(record["length_policy"] for record in unit_records)),
                "records": unit_records,
                "notes": (
                    "번역/검수는 source_text 단위로 자연스럽게 보고, ROM 적용은 records 배열의 각 counted record에 "
                    "나눠 넣는다. fixed_slot/candidate_repoint_keep_conservative 는 max_korean_chars를 넘기지 않되, "
                    "가능한 한 허용 길이를 활용해 의미와 말투를 보존한다."
                ),
                "next_gap_after_unit": None
                if cursor >= len(records)
                else int(records[cursor]["header_offset"]) - (int(last["offset"]) + int(last["byte_length"])),
            }
        )
    return units


def split_batches(units: list[dict], parts: int = 10) -> list[list[dict]]:
    total_records = sum(unit["record_count"] for unit in units)
    target = math.ceil(total_records / parts)
    batches: list[list[dict]] = []
    current: list[dict] = []
    current_records = 0
    remaining_parts = parts
    for unit in units:
        if current and current_records + unit["record_count"] > target and remaining_parts > 1:
            batches.append(current)
            remaining_parts -= 1
            current = []
            current_records = 0
            remaining_records = total_records - sum(sum(item["record_count"] for item in batch) for batch in batches)
            target = math.ceil(remaining_records / remaining_parts)
        current.append(unit)
        current_records += unit["record_count"]
    if current:
        batches.append(current)
    return batches


def render_readme(summary: dict) -> str:
    return "\n".join(
        [
            "# Entry8 Full Retranslation",
            "",
            "Entry8 전체 재번역 작업 패키지다.",
            "",
            "## Rules",
            "",
            "- `confirmed_repoint`: 현재 conservative build에서 repoint 허용된 레코드. 의미와 자연스러움을 우선한다.",
            "- `fixed_slot`: 원본 counted 슬롯 안에 들어가야 하는 레코드. `max_korean_chars` 이내로 번역하되, 허용 길이를 최대한 활용해 의미와 말투를 보존한다.",
            "- `candidate_repoint_keep_conservative`: 구조상 repoint 후보지만 아직 플레이 안정 검증이 충분하지 않다. 이번 번역에서는 `fixed_slot`처럼 다루며, 역시 허용 길이 안에서 의미를 최대한 살린다.",
            "- 짧은 접두/감탄사는 source_text에서 뒤 문장과 같은 unit으로 묶었지만, ROM 적용용 records는 분리되어 있다.",
            "- Entry8은 반각 공백/반각 쉼표가 깨질 수 있으므로 번역문은 일반 한국어로 쓰되 빌드 정규화가 전각 공백/구두점으로 맞춘다.",
            "",
            "## Summary",
            "",
            f"- Records: `{summary['record_count']}`",
            f"- Units: `{summary['unit_count']}`",
            f"- Batches: `{summary['batch_count']}`",
            f"- Length policies: `{summary['length_policy_counts']}`",
            "",
        ]
    )


def main() -> int:
    records = build_records()
    units = build_units(records)
    batches = split_batches(units, 10)
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    BATCH_DIR.mkdir(parents=True, exist_ok=True)

    batch_entries = []
    for index, batch in enumerate(batches, start=1):
        record_count = sum(unit["record_count"] for unit in batch)
        path = BATCH_DIR / f"part_{index:02d}.json"
        payload = {
            "part": index,
            "part_count": len(batches),
            "status": "todo",
            "record_count": record_count,
            "unit_count": len(batch),
            "instructions": [
                "translation_text 와 records[].translation 을 채운다.",
                "confirmed_repoint 는 자연스러운 번역을 우선한다.",
                "fixed_slot / candidate_repoint_keep_conservative 는 records[].max_korean_chars 이내로 맞추되, 가능한 한 허용 길이를 활용해 의미와 말투를 보존한다.",
                "source_text 가 여러 줄이면 문맥을 같이 보고, records 배열 순서대로 자연스럽게 나눠 담는다.",
            ],
            "units": batch,
        }
        write_json(path, payload)
        batch_entries.append(
            {
                "part": index,
                "path": str(path.relative_to(ROOT)),
                "record_count": record_count,
                "unit_count": len(batch),
                "first_offset": batch[0]["offsets_hex"][0],
                "last_offset": batch[-1]["offsets_hex"][-1],
            }
        )

    summary = {
        "last_updated": datetime.now(timezone.utc).isoformat(),
        "record_count": len(records),
        "unit_count": len(units),
        "batch_count": len(batches),
        "length_policy_counts": dict(Counter(record["length_policy"] for record in records)),
        "batches": batch_entries,
    }
    write_json(MANIFEST, summary)
    README.write_text(render_readme(summary), encoding="utf-8")
    print(f"written: {MANIFEST}")
    print(f"written: {README}")
    for entry in batch_entries:
        print(
            f"part {entry['part']:02d}: records={entry['record_count']} units={entry['unit_count']} "
            f"{entry['first_offset']}..{entry['last_offset']}"
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
