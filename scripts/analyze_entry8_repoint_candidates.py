#!/usr/bin/env python3

from __future__ import annotations

import json
import struct
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from gba_kor_tool.cli import TableCodec, encode_text
from gba_kor_tool.translation_normalization import normalize_translation_text


ROM_BASE = 0x08000000
REGISTRY_A_TABLE_OFFSET = 0x17C2F4
REGISTRY_A_ENTRY8_INDEX = 8
ENTRY8_SEGMENT_TABLE_START = 0x20
ENTRY8_SEGMENT_TABLE_END = 0x16C
ENTRY8_SOURCE_GROUP = "registry_a_entry8_prefixed_texts"

DEFAULT_ROM = ROOT / "Hagane no Renkinjutsushi - Meisou no Rondo (Japan).gba"
DEFAULT_TRANSLATIONS = ROOT / "patched_roms/current_review/current_review_translations.json"
DEFAULT_EXTRACTED = ROOT / "confirmed_data/extracted_texts/registry_a_entry8_prefixed_texts.json"
DEFAULT_TABLE = ROOT / "analysis/generated_workbenches/current_review/prepared.tbl"
OUT_JSON = ROOT / "analysis/entry8_repoint_candidates.json"
OUT_MD = ROOT / "analysis/entry8_repoint_candidates.md"


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


def find_segment(segments: list[dict], raw_start: int) -> dict | None:
    for segment in segments:
        if segment["old_start"] <= raw_start < segment["old_end"]:
            return segment
    return None


def in_any_range(value: int, ranges: list[tuple[int, int]]) -> bool:
    return any(start <= value < end for start, end in ranges)


def map_offset(local: int, deltas: list[tuple[int, int]]) -> int:
    shifted = local
    for change_at, delta in sorted(deltas):
        if local >= change_at:
            shifted += delta
    return shifted


def build_text_ranges(extracted: list[dict], *, entry_offset: int, segments: list[dict]) -> dict[int, list[tuple[int, int]]]:
    ranges_by_start: dict[int, list[tuple[int, int]]] = {}
    for record in extracted:
        header_offset = record.get("header_offset")
        offset = record.get("offset")
        byte_length = record.get("byte_length")
        if header_offset is None or offset is None or byte_length is None:
            continue
        raw_start = int(header_offset) - entry_offset
        raw_end = int(offset) + int(byte_length) - entry_offset
        segment = find_segment(segments, raw_start)
        if segment is not None:
            ranges_by_start.setdefault(segment["old_start"], []).append((raw_start, raw_end))
    for ranges in ranges_by_start.values():
        ranges.sort()
    return ranges_by_start


def encode_entry8_payload_length(record: dict, translation: str, table: TableCodec) -> tuple[int, str]:
    normalized = normalize_translation_text(
        translation,
        source_group=record.get("source_group"),
        reference_text=record.get("text"),
    )
    encoded = encode_text(normalized, encoding="cp932", table=table)
    raw_length = 4 + len(encoded)
    if raw_length % 2:
        normalized = normalized + " "
        encoded = encode_text(normalized, encoding="cp932", table=table)
        raw_length = 4 + len(encoded)
    return raw_length, normalized


def scan_reference_risk(
    data: bytes,
    *,
    entry_offset: int,
    segment: dict,
    deltas: list[tuple[int, int]],
    text_ranges: list[tuple[int, int]],
) -> dict:
    old_start = int(segment["old_start"])
    old_end = int(segment["old_end"])
    old_blob = data[entry_offset + old_start:entry_offset + old_end]
    first_change = min((change_at for change_at, delta in deltas if delta), default=old_end)
    u32_refs = []
    u16_refs = []

    for pos in range(0, len(old_blob) - 3, 4):
        abs_pos = old_start + pos
        if in_any_range(abs_pos, text_ranges):
            continue
        value = struct.unpack_from("<I", old_blob, pos)[0]
        if old_start <= value < old_end and value >= first_change:
            u32_refs.append(
                {
                    "field_rel": pos,
                    "old_value_rel": value - old_start,
                    "expected_value_rel": map_offset(value, deltas) - old_start,
                }
            )

    for pos in range(0, len(old_blob) - 1, 2):
        abs_pos = old_start + pos
        if in_any_range(abs_pos, text_ranges):
            continue
        value = struct.unpack_from("<H", old_blob, pos)[0]
        target = old_start + value
        if value % 2 == 0 and old_start <= target < old_end and target >= first_change:
            expected = map_offset(target, deltas) - old_start
            if 0 <= expected <= 0xFFFF and expected != value:
                u16_refs.append(
                    {
                        "field_rel": pos,
                        "old_value_rel": value,
                        "expected_value_rel": expected,
                    }
                )

    return {
        "u32_reference_count": len(u32_refs),
        "u32_references": u32_refs[:100],
        "u16_warning_count": len(u16_refs),
        "u16_warnings": u16_refs[:100],
    }


def collect_reference_targets(
    data: bytes,
    *,
    entry_offset: int,
    segment: dict,
    text_ranges: list[tuple[int, int]],
) -> dict:
    old_start = int(segment["old_start"])
    old_end = int(segment["old_end"])
    old_blob = data[entry_offset + old_start:entry_offset + old_end]
    u32_targets = []
    u16_targets = []

    for pos in range(0, len(old_blob) - 3, 4):
        abs_pos = old_start + pos
        if in_any_range(abs_pos, text_ranges):
            continue
        value = struct.unpack_from("<I", old_blob, pos)[0]
        if old_start <= value < old_end:
            u32_targets.append({"field_rel": pos, "target_rel": value - old_start})

    for pos in range(0, len(old_blob) - 1, 2):
        abs_pos = old_start + pos
        if in_any_range(abs_pos, text_ranges):
            continue
        value = struct.unpack_from("<H", old_blob, pos)[0]
        target = old_start + value
        if value % 2 == 0 and old_start <= target < old_end:
            u16_targets.append({"field_rel": pos, "target_rel": value})

    return {
        "u32_targets": u32_targets,
        "u16_targets": u16_targets,
    }


def main() -> int:
    rom = DEFAULT_ROM.read_bytes()
    translations = [
        item
        for item in load_json(DEFAULT_TRANSLATIONS)
        if item.get("source_group") == ENTRY8_SOURCE_GROUP and item.get("translation")
    ]
    extracted = load_json(DEFAULT_EXTRACTED)
    table = TableCodec.from_path(DEFAULT_TABLE)

    entry_offset, entry_length = read_pointer_length_entry(
        rom,
        REGISTRY_A_TABLE_OFFSET,
        REGISTRY_A_ENTRY8_INDEX,
    )
    segments = read_entry8_segments(rom, entry_offset, entry_length)
    text_ranges = build_text_ranges(extracted, entry_offset=entry_offset, segments=segments)

    segment_rows: dict[int, dict] = {}
    records_by_offset = {int(item["offset"]): item for item in translations}
    candidate_offsets: list[int] = []
    skipped_boundary_offsets: list[int] = []
    for record in sorted(translations, key=lambda item: int(item["offset"])):
        header_offset = int(record["header_offset"])
        payload_offset = int(record["offset"])
        old_payload_len = int(record["byte_length"])
        old_raw_len = old_payload_len + 4
        raw_start = header_offset - entry_offset
        raw_end = payload_offset + old_payload_len - entry_offset
        segment = find_segment(segments, raw_start)
        if segment is None:
            continue

        row = segment_rows.setdefault(
            int(segment["old_start"]),
            {
                "table_local": int(segment["table_local"]),
                "old_start": int(segment["old_start"]),
                "old_end": int(segment["old_end"]),
                "translated_record_count": 0,
                "length_preserved_count": 0,
                "too_long_count": 0,
                "boundary_crossing_count": 0,
                "variable_candidate_count": 0,
                "variable_delta_total": 0,
                "variable_offsets": [],
                "sample_candidates": [],
            },
        )
        row["translated_record_count"] += 1

        if raw_end > int(segment["old_end"]):
            row["boundary_crossing_count"] += 1
            skipped_boundary_offsets.append(payload_offset)
            continue

        new_raw_len, normalized = encode_entry8_payload_length(record, str(record["translation"]), table)
        if new_raw_len <= old_raw_len:
            row["length_preserved_count"] += 1
            continue

        delta = new_raw_len - old_raw_len
        row["too_long_count"] += 1
        row["variable_candidate_count"] += 1
        row["variable_delta_total"] += delta
        row["variable_offsets"].append(payload_offset)
        row.setdefault("variable_changes", []).append(
            {
                "offset": payload_offset,
                "raw_start": raw_start,
                "delta": delta,
            }
        )
        candidate_offsets.append(payload_offset)
        if len(row["sample_candidates"]) < 8:
            row["sample_candidates"].append(
                {
                    "offset": payload_offset,
                    "offset_hex": f"0x{payload_offset:06X}",
                    "raw_start_rel": raw_start - int(segment["old_start"]),
                    "old_raw_len": old_raw_len,
                    "new_raw_len": new_raw_len,
                    "delta": delta,
                    "text": record.get("text", ""),
                    "translation": normalized,
                }
            )

    rows = []
    for old_start, row in sorted(segment_rows.items(), key=lambda item: item[1]["table_local"]):
        deltas = []
        for sample_offset in row["variable_offsets"]:
            record = records_by_offset[sample_offset]
            raw_start = int(record["header_offset"]) - entry_offset
            old_raw_len = int(record["byte_length"]) + 4
            new_raw_len, _normalized = encode_entry8_payload_length(record, str(record["translation"]), table)
            deltas.append((raw_start, new_raw_len - old_raw_len))

        segment = next(item for item in segments if int(item["old_start"]) == old_start)
        risk = scan_reference_risk(
            rom,
            entry_offset=entry_offset,
            segment=segment,
            deltas=deltas,
            text_ranges=text_ranges.get(old_start, []),
        )
        row.update(risk)

        reference_targets = collect_reference_targets(
            rom,
            entry_offset=entry_offset,
            segment=segment,
            text_ranges=text_ranges.get(old_start, []),
        )
        all_target_rels = [
            int(item["target_rel"])
            for item in reference_targets["u32_targets"] + reference_targets["u16_targets"]
        ]
        tail_safe_offsets: list[int] = []
        for change in sorted(row.get("variable_changes", []), key=lambda item: item["raw_start"], reverse=True):
            change_rel = int(change["raw_start"]) - old_start
            if not any(target_rel >= change_rel for target_rel in all_target_rels):
                tail_safe_offsets.append(int(change["offset"]))
            else:
                break
        tail_safe_offsets.reverse()
        row["tail_safe_offset_count"] = len(tail_safe_offsets)
        row["tail_safe_offsets"] = tail_safe_offsets
        row["tail_safe_offsets_csv"] = ",".join(f"0x{offset:06X}" for offset in tail_safe_offsets)
        row["status"] = (
            "no_variable_needed"
            if row["variable_candidate_count"] == 0
            else "hard_ref_risky"
            if row["u32_reference_count"] > 0
            else "u16_review_needed"
            if row["u16_warning_count"] > 0
            else "candidate"
        )
        row["variable_offsets_csv"] = ",".join(f"0x{offset:06X}" for offset in row["variable_offsets"])
        rows.append(row)

    candidate_rows = [row for row in rows if row["status"] == "candidate"]
    tail_safe_offsets = [
        offset
        for row in rows
        for offset in row.get("tail_safe_offsets", [])
    ]
    payload = {
        "entry_offset": entry_offset,
        "entry_length": entry_length,
        "candidate_offset_count": len(candidate_offsets),
        "boundary_crossing_offset_count": len(skipped_boundary_offsets),
        "safe_candidate_segment_count": len(candidate_rows),
        "tail_safe_offset_count": len(tail_safe_offsets),
        "tail_safe_offsets_csv": ",".join(f"0x{offset:06X}" for offset in tail_safe_offsets),
        "rows": rows,
    }
    OUT_JSON.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    lines = [
        "# Entry8 Repoint Candidates",
        "",
        f"- Entry8 offset: `0x{entry_offset:06X}`",
        f"- Entry8 length: `0x{entry_length:X}`",
        f"- Variable candidate offsets: `{len(candidate_offsets)}`",
        f"- Boundary-crossing skipped offsets: `{len(skipped_boundary_offsets)}`",
        f"- Safe candidate segments: `{len(candidate_rows)}`",
        f"- Tail-safe offsets: `{len(tail_safe_offsets)}`",
        "",
        "## Candidate Segments",
        "",
        "| table | records | too long | delta | u32 refs | u16 warn | offsets |",
        "|---:|---:|---:|---:|---:|---:|---|",
    ]
    for row in sorted(candidate_rows, key=lambda item: (-item["variable_candidate_count"], item["table_local"]))[:40]:
        offsets_preview = ",".join(f"0x{offset:06X}" for offset in row["variable_offsets"][:8])
        if len(row["variable_offsets"]) > 8:
            offsets_preview += ",..."
        lines.append(
            f"| `0x{row['table_local']:X}` | {row['translated_record_count']} | "
            f"{row['too_long_count']} | {row['variable_delta_total']} | "
            f"{row['u32_reference_count']} | {row['u16_warning_count']} | `{offsets_preview}` |"
        )

    lines.extend(
        [
            "",
            "## Risk Summary",
            "",
            "| status | segments | too long records |",
            "|---|---:|---:|",
        ]
    )
    for status in ["candidate", "u16_review_needed", "hard_ref_risky", "no_variable_needed"]:
        selected = [row for row in rows if row["status"] == status]
        lines.append(f"| `{status}` | {len(selected)} | {sum(row['too_long_count'] for row in selected)} |")

    lines.extend(
        [
            "",
            "## Tail-Safe Offsets",
            "",
            "These offsets stay clear of detected segment-local command operands when accumulated from the end of each segment.",
            "",
            "| table | count | offsets |",
            "|---:|---:|---|",
        ]
    )
    for row in sorted((row for row in rows if row.get("tail_safe_offsets")), key=lambda item: (-item["tail_safe_offset_count"], item["table_local"]))[:40]:
        offsets_preview = ",".join(f"0x{offset:06X}" for offset in row["tail_safe_offsets"][:12])
        if len(row["tail_safe_offsets"]) > 12:
            offsets_preview += ",..."
        lines.append(f"| `0x{row['table_local']:X}` | {row['tail_safe_offset_count']} | `{offsets_preview}` |")

    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"wrote {OUT_JSON}")
    print(f"wrote {OUT_MD}")
    print(
        json.dumps(
            {
                "candidate_offset_count": len(candidate_offsets),
                "safe_candidate_segment_count": len(candidate_rows),
                "boundary_crossing_offset_count": len(skipped_boundary_offsets),
                "tail_safe_offset_count": len(tail_safe_offsets),
            },
            ensure_ascii=False,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
