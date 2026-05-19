#!/usr/bin/env python3

from __future__ import annotations

import json
import struct
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
ROM_BASE = 0x08000000
REGISTRY_A_TABLE_OFFSET = 0x17C2F4
REGISTRY_A_ENTRY8_INDEX = 8
ENTRY8_SEGMENT_TABLE_START = 0x20
ENTRY8_SEGMENT_TABLE_END = 0x16C
PROTECTED_SEGMENT_TABLES = {0x150, 0x15C}

SOURCE_ROM = ROOT / "Hagane no Renkinjutsushi - Meisou no Rondo (Japan).gba"
DATASET = ROOT / "confirmed_data/localization_workbench/workbench_dataset.json"
APPLY_REPORT = ROOT / "patched_roms/current_review/current_review_apply_report.json"
REPOINT_CANDIDATES = ROOT / "analysis/entry8_repoint_candidates.json"
OUT_JSON = ROOT / "analysis/entry8_segment_capability_map.json"
OUT_MD = ROOT / "analysis/entry8_segment_capability_map.md"


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, payload: Any) -> None:
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def read_pointer_length_entry(data: bytes, *, table_offset: int, index: int) -> tuple[int, int]:
    rom_address, length = struct.unpack_from("<II", data, table_offset + index * 8)
    return rom_address - ROM_BASE, length


def read_entry8_segments(data: bytes, *, entry_offset: int, entry_length: int) -> list[dict[str, int]]:
    segments: list[dict[str, int]] = []
    seen: set[int] = set()
    for table_local in range(ENTRY8_SEGMENT_TABLE_START, ENTRY8_SEGMENT_TABLE_END, 4):
        value = struct.unpack_from("<I", data, entry_offset + table_local)[0]
        if value == 0xFFFFFFFF or value in seen or not (0 <= value < entry_length):
            continue
        seen.add(value)
        segments.append({"table_local": table_local, "old_start": value})
    segments.sort(key=lambda item: item["old_start"])
    for index, segment in enumerate(segments):
        segment["old_end"] = segments[index + 1]["old_start"] if index + 1 < len(segments) else entry_length
    return segments


def segment_for_local(segments: list[dict[str, int]], local_offset: int) -> dict[str, int] | None:
    for segment in segments:
        if segment["old_start"] <= local_offset < segment["old_end"]:
            return segment
    return None


def source_group(record: dict[str, Any]) -> str:
    return str(record.get("source_group", ""))


def record_local_start(record: dict[str, Any], *, entry_offset: int) -> int | None:
    if record.get("header_offset") is not None:
        return int(record["header_offset"]) - entry_offset
    if record.get("offset") is not None:
        return int(record["offset"]) - entry_offset
    return None


def action_delta(row: dict[str, Any]) -> int:
    action = str(row.get("action", ""))
    encoded = row.get("encoded_payload_length")
    if encoded is None:
        return 0
    encoded = int(encoded)
    if row.get("source_group") == "registry_a_entry8_prefixed_texts":
        old_raw = int(row.get("byte_length") or 0) + 4
        return encoded - old_raw
    capacity = row.get("capacity_bytes")
    if capacity is None:
        return 0
    return encoded - int(capacity)


def classify_segment(
    *,
    table_local: int,
    action_counts: Counter[str],
    candidate: dict[str, Any] | None,
) -> tuple[str, str]:
    if table_local in PROTECTED_SEGMENT_TABLES:
        return "protected", "보호 세그먼트. 오프닝/민감 제어 흐름 가능성이 있어 기본 확장 금지."
    if action_counts.get("entry8_segment_repointed"):
        if action_counts.get("entry8_overlay_in_place_length_preserved"):
            return "active_repoint_overlay", "현재 세그먼트 repoint와 별도 overlay가 함께 필요했던 검증 대상."
        return "active_repoint", "현재 빌드에서 segment repoint가 실제 적용된 대상."
    if candidate and int(candidate.get("variable_candidate_count") or 0):
        if int(candidate.get("tail_safe_offset_count") or 0):
            return "candidate_tail_safe", "후보 중 tail-safe 항목이 있어 우선 확장 실험 가치가 높음."
        return "candidate_structural", "구조상 variable 후보는 있으나 tail-safe 검증은 부족함."
    if action_counts:
        return "fixed_or_overlay", "현재는 원위치 고정/overlay만 적용됨."
    return "unknown_or_unused", "현재 번역 적용에서 건드리지 않은 세그먼트."


def build_map() -> dict[str, Any]:
    original = SOURCE_ROM.read_bytes()
    entry_offset, entry_length = read_pointer_length_entry(
        original,
        table_offset=REGISTRY_A_TABLE_OFFSET,
        index=REGISTRY_A_ENTRY8_INDEX,
    )
    segments = read_entry8_segments(original, entry_offset=entry_offset, entry_length=entry_length)
    dataset = load_json(DATASET)
    report = load_json(APPLY_REPORT)
    candidates_payload = load_json(REPOINT_CANDIDATES) if REPOINT_CANDIDATES.exists() else {"rows": []}
    candidates_by_table = {
        int(row["table_local"]): row
        for row in candidates_payload.get("rows", [])
        if row.get("table_local") is not None
    }

    records_by_segment: dict[int, list[dict[str, Any]]] = defaultdict(list)
    for item in dataset.get("items", []):
        offset = item.get("offset")
        if offset is None:
            continue
        local_start = record_local_start(item, entry_offset=entry_offset)
        if local_start is None:
            continue
        segment = segment_for_local(segments, local_start)
        if segment is None:
            continue
        records_by_segment[segment["table_local"]].append(item)

    report_by_segment: dict[int, list[dict[str, Any]]] = defaultdict(list)
    for row in report:
        table_local = row.get("segment_table_local")
        if table_local is None:
            continue
        report_by_segment[int(table_local)].append(row)

    segment_rows: list[dict[str, Any]] = []
    totals = Counter()
    for segment in segments:
        table_local = segment["table_local"]
        records = records_by_segment.get(table_local, [])
        report_rows = report_by_segment.get(table_local, [])
        candidate = candidates_by_table.get(table_local)
        action_counts = Counter(str(row.get("action", "")) for row in report_rows)
        source_counts = Counter(source_group(record) for record in records)
        source_apply_counts = Counter(source_group(row) for row in report_rows)
        delta_total = sum(action_delta(row) for row in report_rows)
        changed_delta_count = sum(1 for row in report_rows if action_delta(row) != 0)
        capability, reason = classify_segment(
            table_local=table_local,
            action_counts=action_counts,
            candidate=candidate,
        )
        totals[capability] += 1
        segment_rows.append(
            {
                "table_local": table_local,
                "table_local_hex": f"0x{table_local:X}",
                "old_start": segment["old_start"],
                "old_start_hex": f"0x{segment['old_start']:X}",
                "old_end": segment["old_end"],
                "old_end_hex": f"0x{segment['old_end']:X}",
                "size": segment["old_end"] - segment["old_start"],
                "protected": table_local in PROTECTED_SEGMENT_TABLES,
                "capability": capability,
                "capability_reason": reason,
                "record_count": len(records),
                "source_counts": dict(sorted(source_counts.items())),
                "applied_record_count": len(report_rows),
                "source_apply_counts": dict(sorted(source_apply_counts.items())),
                "action_counts": dict(sorted(action_counts.items())),
                "delta_total": delta_total,
                "changed_delta_count": changed_delta_count,
                "variable_candidate_count": int(candidate.get("variable_candidate_count") or 0) if candidate else 0,
                "tail_safe_offset_count": int(candidate.get("tail_safe_offset_count") or 0) if candidate else 0,
                "u32_reference_count": int(candidate.get("u32_reference_count") or 0) if candidate else 0,
                "u16_warning_count": int(candidate.get("u16_warning_count") or 0) if candidate else 0,
                "sample_offsets": [
                    f"0x{int(record['offset']):06X}"
                    for record in sorted(records, key=lambda item: int(item.get("offset") or 0))[:6]
                    if record.get("offset") is not None
                ],
                "sample_texts": [
                    str(record.get("text", "")).replace("\n", " / ")[:60]
                    for record in sorted(records, key=lambda item: int(item.get("offset") or 0))[:4]
                ],
            }
        )

    action_totals = Counter()
    for row in segment_rows:
        action_totals.update(row["action_counts"])

    next_candidates = [
        row
        for row in segment_rows
        if row["capability"] in {"candidate_tail_safe", "candidate_structural"}
        and not row["protected"]
    ]
    next_candidates.sort(
        key=lambda row: (
            row["capability"] != "candidate_tail_safe",
            -row["tail_safe_offset_count"],
            row["u16_warning_count"],
            -row["variable_candidate_count"],
        )
    )

    return {
        "entry_offset": entry_offset,
        "entry_offset_hex": f"0x{entry_offset:X}",
        "entry_length": entry_length,
        "segment_count": len(segment_rows),
        "capability_counts": dict(sorted(totals.items())),
        "action_counts": dict(sorted(action_totals.items())),
        "next_candidate_segments": [
            {
                "table_local_hex": row["table_local_hex"],
                "capability": row["capability"],
                "variable_candidate_count": row["variable_candidate_count"],
                "tail_safe_offset_count": row["tail_safe_offset_count"],
                "u16_warning_count": row["u16_warning_count"],
                "record_count": row["record_count"],
                "sample_offsets": row["sample_offsets"],
                "sample_texts": row["sample_texts"],
            }
            for row in next_candidates[:20]
        ],
        "segments": segment_rows,
    }


def write_markdown(payload: dict[str, Any]) -> None:
    lines = [
        "# Entry8 Segment Capability Map",
        "",
        f"- Entry8 offset: `{payload['entry_offset_hex']}`",
        f"- Entry8 length: `{payload['entry_length']}` bytes",
        f"- Segment count: `{payload['segment_count']}`",
        f"- Capability counts: `{payload['capability_counts']}`",
        f"- Apply action counts: `{payload['action_counts']}`",
        "",
        "## Meaning",
        "",
        "- `active_repoint`: 현재 빌드에서 segment repoint가 실제 사용됨.",
        "- `active_repoint_overlay`: segment repoint와 원위치 overlay가 함께 필요했던 구간.",
        "- `candidate_tail_safe`: 다음 확장 실험 우선 후보.",
        "- `candidate_structural`: 후보는 있으나 tail-safe 검증은 부족한 구간.",
        "- `fixed_or_overlay`: 현재는 원위치 고정/overlay 중심.",
        "- `protected`: 보호 세그먼트. 기본적으로 확장 금지.",
        "",
        "## Next Candidate Segments",
        "",
        "| segment | capability | variable | tail-safe | u16 warnings | records | samples |",
        "|---:|---|---:|---:|---:|---:|---|",
    ]
    for row in payload["next_candidate_segments"]:
        samples = "<br>".join(row["sample_texts"]) or "-"
        lines.append(
            f"| `{row['table_local_hex']}` | `{row['capability']}` | "
            f"{row['variable_candidate_count']} | {row['tail_safe_offset_count']} | "
            f"{row['u16_warning_count']} | {row['record_count']} | {samples} |"
        )

    lines.extend(
        [
            "",
            "## Segment Table",
            "",
            "| segment | capability | size | records | actions | variable | tail-safe | delta | sources |",
            "|---:|---|---:|---:|---|---:|---:|---:|---|",
        ]
    )
    for row in payload["segments"]:
        actions = ", ".join(f"{key}:{value}" for key, value in row["action_counts"].items()) or "-"
        sources = ", ".join(f"{key}:{value}" for key, value in row["source_counts"].items()) or "-"
        lines.append(
            f"| `{row['table_local_hex']}` | `{row['capability']}` | {row['size']} | "
            f"{row['record_count']} | {actions} | {row['variable_candidate_count']} | "
            f"{row['tail_safe_offset_count']} | {row['delta_total']} | {sources} |"
        )
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    payload = build_map()
    write_json(OUT_JSON, payload)
    write_markdown(payload)
    print(f"written: {OUT_JSON}")
    print(f"written: {OUT_MD}")
    print(json.dumps(payload["capability_counts"], ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
