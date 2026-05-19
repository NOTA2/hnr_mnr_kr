#!/usr/bin/env python3

from __future__ import annotations

import json
import struct
from collections import Counter, defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ROM_BASE = 0x08000000
REGISTRY_A_TABLE_OFFSET = 0x17C2F4
REGISTRY_A_ENTRY8_INDEX = 8
SEGMENT_TABLE_START = 0x20
SEGMENT_TABLE_END = 0x16C

JP_ROM = ROOT / "Hagane no Renkinjutsushi - Meisou no Rondo (Japan).gba"
EXTRACTED = ROOT / "confirmed_data/extracted_texts/registry_a_entry8_prefixed_texts.json"
OUT_JSON = ROOT / "analysis/entry8_vm_structure.json"
OUT_MD = ROOT / "analysis/entry8_vm_structure.md"


def u32(data: bytes, offset: int) -> int:
    return struct.unpack_from("<I", data, offset)[0]


def read_entry8_segments(data: bytes) -> tuple[int, int, list[dict]]:
    entry_offset = u32(data, REGISTRY_A_TABLE_OFFSET + REGISTRY_A_ENTRY8_INDEX * 8) - ROM_BASE
    entry_length = u32(data, REGISTRY_A_TABLE_OFFSET + REGISTRY_A_ENTRY8_INDEX * 8 + 4)
    segments = []
    seen = set()
    for table_local in range(SEGMENT_TABLE_START, SEGMENT_TABLE_END, 4):
        value = u32(data, entry_offset + table_local)
        if value == 0xFFFFFFFF or value in seen or not (0 <= value < entry_length):
            continue
        seen.add(value)
        segments.append({"table_local": table_local, "old_start": value})
    segments.sort(key=lambda item: item["old_start"])
    for index, segment in enumerate(segments):
        segment["old_end"] = segments[index + 1]["old_start"] if index + 1 < len(segments) else entry_length
    return entry_offset, entry_length, segments


def load_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def find_segment(segments: list[dict], local: int) -> dict | None:
    for segment in segments:
        if segment["old_start"] <= local < segment["old_end"]:
            return segment
    return None


def build_text_records(entry_offset: int, segments: list[dict]) -> dict[int, list[dict]]:
    records_by_segment = defaultdict(list)
    for record in load_json(EXTRACTED):
        header_local = int(record["header_offset"]) - entry_offset
        payload_local = int(record["offset"]) - entry_offset
        raw_end = payload_local + int(record["byte_length"])
        segment = find_segment(segments, header_local)
        if segment is None:
            continue
        records_by_segment[int(segment["old_start"])].append(
            {
                "header_local": header_local,
                "payload_local": payload_local,
                "raw_end": raw_end,
                "byte_length": int(record["byte_length"]),
                "char_count": int(record.get("char_count", 0)),
                "offset": int(record["offset"]),
                "text": record.get("text", ""),
            }
        )
    for values in records_by_segment.values():
        values.sort(key=lambda item: item["header_local"])
    return records_by_segment


def iter_control_gaps(records_by_segment: dict[int, list[dict]], segments: list[dict]) -> list[dict]:
    gaps = []
    for segment in segments:
        segment_start = int(segment["old_start"])
        segment_end = int(segment["old_end"])
        cursor = segment_start
        records = records_by_segment.get(segment_start, [])
        for record in records:
            start = int(record["header_local"])
            if cursor < start:
                gaps.append(
                    {
                        "segment_table_local": int(segment["table_local"]),
                        "segment_start": segment_start,
                        "start": cursor,
                        "end": start,
                        "kind": "before_text",
                        "next_text_offset": int(record["offset"]),
                    }
                )
            cursor = max(cursor, int(record["raw_end"]))
        # The tail can contain large binary tables. Keep it in the report, but
        # do not use it to infer opcode lengths unless it is small.
        if cursor < segment_end:
            gaps.append(
                {
                    "segment_table_local": int(segment["table_local"]),
                    "segment_start": segment_start,
                    "start": cursor,
                    "end": segment_end,
                    "kind": "tail",
                    "next_text_offset": None,
                }
            )
    return gaps


def command_starts(blob: bytes, start: int, end: int) -> list[int]:
    return [
        pos
        for pos in range(start, max(start, end - 1), 2)
        if blob[pos + 1] == 0xFF
    ]


def infer_opcode_lengths(entry: bytes, gaps: list[dict]) -> dict[int, dict]:
    counts: dict[int, Counter[int]] = defaultdict(Counter)
    total_seen: Counter[int] = Counter()
    for gap in gaps:
        if gap["kind"] == "tail" and gap["end"] - gap["start"] > 512:
            continue
        starts = command_starts(entry, int(gap["start"]), int(gap["end"]))
        if not starts:
            continue
        boundaries = starts + [int(gap["end"])]
        for index, pos in enumerate(starts):
            opcode = entry[pos]
            length = boundaries[index + 1] - pos
            if length <= 0 or length > 64 or length % 2:
                continue
            counts[opcode][length] += 1
            total_seen[opcode] += 1

    inferred = {}
    for opcode, length_counts in sorted(counts.items()):
        best_length, best_count = length_counts.most_common(1)[0]
        total = total_seen[opcode]
        stable = best_count >= 3 and best_count / total >= 0.65
        inferred[opcode] = {
            "opcode_hex": f"{opcode:02X} FF",
            "best_length": best_length,
            "best_count": best_count,
            "total_observations": total,
            "stability": round(best_count / total, 3),
            "stable": stable,
            "length_counts": dict(sorted(length_counts.items())),
        }
    return inferred


def parse_gap(entry: bytes, gap: dict, opcode_lengths: dict[int, dict]) -> list[dict]:
    pos = int(gap["start"])
    end = int(gap["end"])
    commands = []
    while pos + 1 < end:
        if entry[pos + 1] != 0xFF:
            pos += 2
            continue
        opcode = entry[pos]
        inferred = opcode_lengths.get(opcode)
        if not inferred or not inferred.get("stable"):
            commands.append(
                {
                    "local": pos,
                    "rel": pos - int(gap["segment_start"]),
                    "opcode": f"{opcode:02X} FF",
                    "length": None,
                    "status": "unknown_length",
                }
            )
            break
        length = int(inferred["best_length"])
        if pos + length > end:
            commands.append(
                {
                    "local": pos,
                    "rel": pos - int(gap["segment_start"]),
                    "opcode": f"{opcode:02X} FF",
                    "length": length,
                    "status": "overruns_gap",
                }
            )
            break
        operands = entry[pos + 2:pos + length]
        commands.append(
            {
                "local": pos,
                "rel": pos - int(gap["segment_start"]),
                "opcode": f"{opcode:02X} FF",
                "length": length,
                "operands_hex": operands.hex(" "),
                "status": "parsed",
            }
        )
        pos += length
    return commands


def classify_operands(
    commands: list[dict],
    *,
    segment_start: int,
    segment_end: int,
    text_anchors: set[int],
    command_anchors: set[int],
) -> list[dict]:
    refs = []
    for command in commands:
        if command.get("status") != "parsed" or not command.get("operands_hex"):
            continue
        local = int(command["local"])
        operands = bytes.fromhex(command["operands_hex"])
        for rel in range(0, len(operands) - 1, 2):
            value = struct.unpack_from("<H", operands, rel)[0]
            target = segment_start + value
            if value % 2 == 0 and segment_start <= target < segment_end:
                refs.append(
                    {
                        "command_local": local,
                        "operand_at": local + 2 + rel,
                        "opcode": command["opcode"],
                        "operand_index": rel // 2,
                        "kind": "u16_segment_rel",
                        "value": value,
                        "target_local": target,
                        "target_is_text_header": target in text_anchors,
                        "target_is_command_start": target in command_anchors,
                        "target_is_boundary": target in text_anchors or target in command_anchors,
                    }
                )
        for rel in range(0, len(operands) - 3, 4):
            value = struct.unpack_from("<I", operands, rel)[0]
            if segment_start <= value < segment_end:
                refs.append(
                    {
                        "command_local": local,
                        "operand_at": local + 2 + rel,
                        "opcode": command["opcode"],
                        "operand_index": rel // 4,
                        "kind": "u32_entry_local",
                        "value": value,
                        "target_local": value,
                        "target_is_text_header": value in text_anchors,
                        "target_is_command_start": value in command_anchors,
                        "target_is_boundary": value in text_anchors or value in command_anchors,
                    }
                )
    return refs


def main() -> int:
    data = JP_ROM.read_bytes()
    entry_offset, entry_length, segments = read_entry8_segments(data)
    entry = data[entry_offset:entry_offset + entry_length]
    records_by_segment = build_text_records(entry_offset, segments)
    gaps = iter_control_gaps(records_by_segment, segments)
    opcode_lengths = infer_opcode_lengths(entry, gaps)

    parsed_segments = []
    total_gaps = 0
    parsed_gap_count = 0
    total_refs = 0
    operand_role_stats: dict[str, Counter[str]] = defaultdict(Counter)
    for segment in segments:
        segment_start = int(segment["old_start"])
        segment_end = int(segment["old_end"])
        segment_gaps = [
            gap
            for gap in gaps
            if int(gap["segment_start"]) == segment_start and not (gap["kind"] == "tail" and gap["end"] - gap["start"] > 512)
        ]
        text_anchors = {int(record["header_local"]) for record in records_by_segment.get(segment_start, [])}
        parsed_gaps_without_refs = []
        command_anchors: set[int] = set()
        for gap in segment_gaps:
            commands = parse_gap(entry, gap, opcode_lengths)
            for command in commands:
                if command.get("status") == "parsed":
                    command_anchors.add(int(command["local"]))
            parsed_gaps_without_refs.append((gap, commands))

        parsed_gaps = []
        for gap, commands in parsed_gaps_without_refs:
            refs = classify_operands(
                commands,
                segment_start=segment_start,
                segment_end=segment_end,
                text_anchors=text_anchors,
                command_anchors=command_anchors,
            )
            for ref in refs:
                key = f"{ref['opcode']}:{ref['kind']}:{ref['operand_index']}"
                operand_role_stats[key]["total"] += 1
                if ref["target_is_text_header"]:
                    operand_role_stats[key]["text_header"] += 1
                if ref["target_is_command_start"]:
                    operand_role_stats[key]["command_start"] += 1
                if ref["target_is_boundary"]:
                    operand_role_stats[key]["boundary"] += 1
            total_refs += len(refs)
            total_gaps += 1
            if commands and all(command.get("status") == "parsed" for command in commands):
                parsed_gap_count += 1
            parsed_gaps.append(
                {
                    "start_rel": int(gap["start"]) - segment_start,
                    "end_rel": int(gap["end"]) - segment_start,
                    "length": int(gap["end"]) - int(gap["start"]),
                    "kind": gap["kind"],
                    "commands": commands[:80],
                    "reference_operands": refs[:80],
                    "reference_operand_count": len(refs),
                }
            )
        parsed_segments.append(
            {
                "table_local": int(segment["table_local"]),
                "old_start": segment_start,
                "old_end": segment_end,
                "record_count": len(records_by_segment.get(segment_start, [])),
                "gap_count": len(segment_gaps),
                "parsed_gap_count": sum(
                    1
                    for gap in parsed_gaps
                    if gap["commands"] and all(command.get("status") == "parsed" for command in gap["commands"])
                ),
                "reference_operand_count": sum(gap["reference_operand_count"] for gap in parsed_gaps),
                "gaps": parsed_gaps[:120],
            }
        )

    operand_roles = []
    for key, counts in sorted(operand_role_stats.items()):
        total = counts["total"]
        boundary = counts["boundary"]
        operand_roles.append(
            {
                "role": key,
                "total": total,
                "text_header": counts["text_header"],
                "command_start": counts["command_start"],
                "boundary": boundary,
                "boundary_ratio": round(boundary / total, 3) if total else 0,
                "probable_relocatable_offset": total >= 5 and boundary / total >= 0.65,
            }
        )

    payload = {
        "entry_offset": entry_offset,
        "entry_length": entry_length,
        "segment_count": len(segments),
        "opcode_lengths": opcode_lengths,
        "operand_roles": operand_roles,
        "gap_parse_summary": {
            "gap_count": total_gaps,
            "parsed_gap_count": parsed_gap_count,
            "coverage": round(parsed_gap_count / total_gaps, 3) if total_gaps else 0,
            "reference_operand_count": total_refs,
            "probable_relocatable_operand_roles": sum(1 for role in operand_roles if role["probable_relocatable_offset"]),
        },
        "segments": parsed_segments,
    }
    OUT_JSON.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    stable_opcodes = [item for item in opcode_lengths.values() if item["stable"]]
    lines = [
        "# Entry8 VM Structure",
        "",
        f"- Entry8 offset: `0x{entry_offset:06X}`",
        f"- Entry8 length: `0x{entry_length:X}`",
        f"- Segments: `{len(segments)}`",
        f"- Stable opcode formats: `{len(stable_opcodes)} / {len(opcode_lengths)}`",
        f"- Gap parse coverage: `{payload['gap_parse_summary']['coverage']}`",
        f"- Reference operands found: `{total_refs}`",
        f"- Probable relocatable operand roles: `{payload['gap_parse_summary']['probable_relocatable_operand_roles']}`",
        "",
        "## Stable Opcodes",
        "",
        "| opcode | len | observations | stability | length counts |",
        "|---|---:|---:|---:|---|",
    ]
    for item in sorted(stable_opcodes, key=lambda item: item["opcode_hex"]):
        counts = ", ".join(f"{length}:{count}" for length, count in item["length_counts"].items())
        lines.append(
            f"| `{item['opcode_hex']}` | {item['best_length']} | {item['total_observations']} | "
            f"{item['stability']} | `{counts}` |"
        )
    lines.extend(
        [
            "",
            "## Probable Relocatable Operands",
            "",
            "| role | total | text | command | boundary ratio |",
            "|---|---:|---:|---:|---:|",
        ]
    )
    for role in sorted(
        (role for role in operand_roles if role["probable_relocatable_offset"]),
        key=lambda item: (-item["boundary_ratio"], -item["total"], item["role"]),
    )[:80]:
        lines.append(
            f"| `{role['role']}` | {role['total']} | {role['text_header']} | "
            f"{role['command_start']} | {role['boundary_ratio']} |"
        )
    lines.extend(
        [
            "",
            "## Segment Reference Density",
            "",
            "| table | records | gaps | parsed | refs |",
            "|---:|---:|---:|---:|---:|",
        ]
    )
    for segment in sorted(parsed_segments, key=lambda item: (-item["reference_operand_count"], item["table_local"]))[:40]:
        lines.append(
            f"| `0x{segment['table_local']:X}` | {segment['record_count']} | "
            f"{segment['gap_count']} | {segment['parsed_gap_count']} | {segment['reference_operand_count']} |"
        )
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")

    print(f"wrote {OUT_JSON}")
    print(f"wrote {OUT_MD}")
    print(json.dumps(payload["gap_parse_summary"], ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
