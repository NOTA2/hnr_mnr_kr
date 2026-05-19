#!/usr/bin/env python3

from __future__ import annotations

import argparse
import json
import struct
from pathlib import Path


ROM_BASE = 0x08000000
REGISTRY_A_TABLE_OFFSET = 0x17C2F4
REGISTRY_A_ENTRY8_INDEX = 8
ENTRY8_SEGMENT_TABLE_START = 0x20
ENTRY8_SEGMENT_TABLE_END = 0x16C
ENTRY8_SOURCE_GROUP = "registry_a_entry8_prefixed_texts"


def read_pointer_length_entry(data: bytes, table_offset: int, index: int) -> tuple[int, int]:
    rom_address, length = struct.unpack_from("<II", data, table_offset + index * 8)
    return rom_address - ROM_BASE, length


def read_entry8_segments(data: bytes, entry_offset: int, entry_length: int) -> list[dict]:
    segments: list[dict] = []
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


def load_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def build_raw_ranges(extracted_records: list[dict], entry_offset: int) -> dict[int, list[tuple[int, int]]]:
    ranges_by_segment: dict[int, list[tuple[int, int]]] = {}
    segments_for_lookup: list[dict] = []
    # Filled by caller after segment starts are known through report entries.
    return ranges_by_segment


def map_offset(local: int, deltas: list[tuple[int, int]]) -> int:
    shifted = local
    for change_at, delta in sorted(deltas):
        if local >= change_at:
            shifted += delta
    return shifted


def in_any_range(value: int, ranges: list[tuple[int, int]]) -> bool:
    return any(start <= value < end for start, end in ranges)


def build_text_ranges(
    extracted_records: list[dict],
    *,
    entry_offset: int,
    segments: list[dict],
) -> dict[int, list[tuple[int, int]]]:
    ranges_by_start: dict[int, list[tuple[int, int]]] = {}
    for record in extracted_records:
        if record.get("source_group") != ENTRY8_SOURCE_GROUP:
            continue
        header_offset = record.get("header_offset")
        offset = record.get("offset")
        byte_length = record.get("byte_length")
        if header_offset is None or offset is None or byte_length is None:
            continue
        raw_start = int(header_offset) - entry_offset
        raw_end = int(offset) + int(byte_length) - entry_offset
        for segment in segments:
            if segment["old_start"] <= raw_start < segment["old_end"]:
                ranges_by_start.setdefault(segment["old_start"], []).append((raw_start, raw_end))
                break
    for ranges in ranges_by_start.values():
        ranges.sort()
    return ranges_by_start


def audit(
    *,
    original_rom: Path,
    translated_rom: Path,
    apply_report: Path,
    extracted_entry8: Path,
    output: Path,
) -> dict:
    original = original_rom.read_bytes()
    translated = translated_rom.read_bytes()
    report = load_json(apply_report)
    extracted = load_json(extracted_entry8)

    old_entry_offset, old_entry_length = read_pointer_length_entry(
        original,
        REGISTRY_A_TABLE_OFFSET,
        REGISTRY_A_ENTRY8_INDEX,
    )
    new_entry_offset, new_entry_length = read_pointer_length_entry(
        translated,
        REGISTRY_A_TABLE_OFFSET,
        REGISTRY_A_ENTRY8_INDEX,
    )
    segments = read_entry8_segments(original, old_entry_offset, old_entry_length)
    segments_by_table = {segment["table_local"]: segment for segment in segments}
    text_ranges = build_text_ranges(extracted, entry_offset=old_entry_offset, segments=segments)

    touched_by_segment: dict[int, list[dict]] = {}
    changed_by_segment: dict[int, list[dict]] = {}
    for item in report:
        if item.get("source_group") != ENTRY8_SOURCE_GROUP:
            continue
        if item.get("action") != "entry8_segment_repointed":
            continue
        table_local = item.get("segment_table_local")
        encoded_len = item.get("encoded_payload_length")
        byte_length = item.get("byte_length")
        offset = item.get("offset")
        if table_local is None or encoded_len is None or byte_length is None or offset is None:
            continue
        old_raw_len = int(byte_length) + 4
        new_raw_len = int(encoded_len)
        segment = segments_by_table[int(table_local)]
        raw_start = int(offset) - 4 - old_entry_offset
        change = {
            "offset": int(offset),
            "raw_start": raw_start,
            "raw_start_rel": raw_start - segment["old_start"],
            "old_raw_len": old_raw_len,
            "new_raw_len": new_raw_len,
            "delta": new_raw_len - old_raw_len,
            "even_aligned": new_raw_len % 2 == 0,
            "text": item.get("text"),
            "translation": item.get("translation"),
        }
        touched_by_segment.setdefault(segment["old_start"], []).append(change)
        if old_raw_len != new_raw_len:
            changed_by_segment.setdefault(segment["old_start"], []).append(change)

    segment_results = []
    total_unresolved = 0
    total_u16_warnings = 0
    total_odd = 0
    for old_start, touched_records in sorted(touched_by_segment.items()):
        segment = next(item for item in segments if item["old_start"] == old_start)
        old_end = segment["old_end"]
        table_local = segment["table_local"]
        new_start = struct.unpack_from("<I", translated, new_entry_offset + table_local)[0]
        changes = changed_by_segment.get(old_start, [])
        if new_start == old_start:
            segment_results.append(
                {
                    "table_local": table_local,
                    "old_start": old_start,
                    "status": "not_relocated",
                    "touched_records": touched_records,
                    "changes": changes,
                    "unresolved_reference_candidates": [],
                }
            )
            continue

        old_blob = original[old_entry_offset + old_start:old_entry_offset + old_end]
        new_blob = translated[new_entry_offset + new_start:new_entry_offset + new_start + len(old_blob) + 0x4000]
        deltas = [(change["raw_start"], change["delta"]) for change in changes]
        ranges = text_ranges.get(old_start, [])
        unresolved = []
        u16_warnings = []

        first_change = min((change["raw_start"] for change in changes), default=old_end)
        # u32 entry-local offsets.
        for pos in range(0, len(old_blob) - 3, 4):
            abs_pos = old_start + pos
            if in_any_range(abs_pos, ranges):
                continue
            value = struct.unpack_from("<I", old_blob, pos)[0]
            if old_start <= value < old_end:
                expected = map_offset(value, deltas)
                if new_start != old_start:
                    expected = new_start + (expected - old_start)
                new_pos = map_offset(abs_pos, deltas) - old_start
                if 0 <= new_pos <= len(new_blob) - 4:
                    actual = struct.unpack_from("<I", new_blob, new_pos)[0]
                    if actual != expected:
                        unresolved.append(
                            {
                                "kind": "u32_entry_local",
                                "field_old_rel": pos,
                                "old_value": value,
                                "expected_value": expected,
                                "actual_value": actual,
                            }
                        )

        # u16 segment-relative offsets. These are noisy, but excluding known text
        # payload ranges makes the remaining list a useful "do not ship blindly"
        # gate for Entry8 variable repoints.
        for pos in range(0, len(old_blob) - 1, 2):
            abs_pos = old_start + pos
            if in_any_range(abs_pos, ranges):
                continue
            value = struct.unpack_from("<H", old_blob, pos)[0]
            target = old_start + value
            if value % 2 == 0 and old_start <= target < old_end and target >= first_change:
                expected = map_offset(target, deltas) - old_start
                if not (0 <= expected <= 0xFFFF):
                    continue
                new_pos = map_offset(abs_pos, deltas) - old_start
                if 0 <= new_pos <= len(new_blob) - 2:
                    actual = struct.unpack_from("<H", new_blob, new_pos)[0]
                    if actual != expected:
                        u16_warnings.append(
                            {
                                "kind": "u16_segment_rel",
                                "field_old_rel": pos,
                                "old_value": value,
                                "expected_value": expected,
                                "actual_value": actual,
                            }
                        )

        odd_records = [change for change in changes if not change["even_aligned"]]
        total_odd += len(odd_records)
        total_unresolved += len(unresolved)
        total_u16_warnings += len(u16_warnings)
        segment_results.append(
            {
                "table_local": table_local,
                "old_start": old_start,
                "old_end": old_end,
                "new_start": new_start,
                "delta_total": sum(change["delta"] for change in changes),
                "touched_records": touched_records,
                "changes": changes,
                "odd_length_records": odd_records,
                "unresolved_reference_candidate_count": len(unresolved),
                "unresolved_reference_candidates": unresolved[:200],
                "u16_warning_candidate_count": len(u16_warnings),
                "u16_warning_candidates": u16_warnings[:200],
            }
        )

    payload = {
        "status": "safe" if total_odd == 0 and total_unresolved == 0 else "unsafe",
        "total_odd_length_records": total_odd,
        "total_unresolved_reference_candidates": total_unresolved,
        "total_u16_warning_candidates": total_u16_warnings,
        "segments": segment_results,
    }
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return payload


def main() -> int:
    parser = argparse.ArgumentParser(description="Audit Entry8 variable repoints for unresolved internal references.")
    parser.add_argument("--original-rom", default="Hagane no Renkinjutsushi - Meisou no Rondo (Japan).gba")
    parser.add_argument("--translated-rom", default="patched_roms/current_review/hnr_localization_review_entry8_test.gba")
    parser.add_argument("--apply-report", default="patched_roms/current_review/current_review_apply_report.json")
    parser.add_argument("--extracted-entry8", default="confirmed_data/extracted_texts/registry_a_entry8_prefixed_texts.json")
    parser.add_argument("--output", default="analysis/entry8_repoint_safety_audit.json")
    args = parser.parse_args()

    result = audit(
        original_rom=Path(args.original_rom),
        translated_rom=Path(args.translated_rom),
        apply_report=Path(args.apply_report),
        extracted_entry8=Path(args.extracted_entry8),
        output=Path(args.output),
    )
    print(json.dumps({k: result[k] for k in ("status", "total_odd_length_records", "total_unresolved_reference_candidates", "total_u16_warning_candidates")}, ensure_ascii=False))
    return 0 if result["status"] == "safe" else 2


if __name__ == "__main__":
    raise SystemExit(main())
