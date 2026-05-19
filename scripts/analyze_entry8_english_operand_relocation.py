#!/usr/bin/env python3

from __future__ import annotations

import json
import struct
from collections import Counter, defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ENTRY8_OFFSET = 0x6B594C
JP_ROM = ROOT / "Hagane no Renkinjutsushi - Meisou no Rondo (Japan).gba"
EN_ROM = ROOT / "local_roms/english_patched/Fullmetal Alchemist Stray Rondo (English Patched v0.02).gba"
EXTRACTED = ROOT / "confirmed_data/extracted_texts/registry_a_entry8_prefixed_texts.json"
POSITION_MAP = ROOT / "analysis/entry8_english_record_position_map.json"
VM_STRUCTURE = ROOT / "analysis/entry8_vm_structure.json"
OUT_JSON = ROOT / "analysis/entry8_english_operand_relocation.json"
OUT_MD = ROOT / "analysis/entry8_english_operand_relocation.md"


def u16(data: bytes, offset: int) -> int:
    return struct.unpack_from("<H", data, offset)[0]


def read_counted_raw_len(data: bytes, local_header: int) -> int:
    count = u16(data, ENTRY8_OFFSET + local_header + 2)
    return 4 + count * 2


def load_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def stable_opcode_lengths() -> dict[int, int]:
    payload = load_json(VM_STRUCTURE)
    result = {}
    for raw_opcode, item in payload["opcode_lengths"].items():
        if item.get("stable"):
            opcode = int(raw_opcode)
            result[opcode] = int(item["best_length"])
    return result


def parse_commands(data: bytes, start: int, end: int, lengths: dict[int, int]) -> tuple[list[dict], bool]:
    commands = []
    pos = start
    while pos + 1 < end:
        if data[ENTRY8_OFFSET + pos + 1] != 0xFF:
            pos += 2
            continue
        opcode = data[ENTRY8_OFFSET + pos]
        length = lengths.get(opcode)
        if length is None or pos + length > end:
            return commands, False
        operands = data[ENTRY8_OFFSET + pos + 2:ENTRY8_OFFSET + pos + length]
        commands.append(
            {
                "local": pos,
                "opcode": opcode,
                "length": length,
                "operands": operands,
            }
        )
        pos += length
    return commands, True


def build_segment_records(jp: bytes, en: bytes, mappings: list[dict], extracted_by_offset: dict[int, dict]) -> dict[int, list[dict]]:
    by_table: dict[int, list[dict]] = defaultdict(list)
    for item in mappings:
        offset = int(item["offset"])
        source = extracted_by_offset.get(offset)
        if not source:
            continue
        old_header = int(item["old_header_local"])
        new_header = int(item["new_header_local"])
        old_len = 4 + int(source["byte_length"])
        new_len = read_counted_raw_len(en, new_header)
        by_table[int(item["table_rel"])].append(
            {
                "offset": offset,
                "old_header": old_header,
                "old_end": old_header + old_len,
                "new_header": new_header,
                "new_end": new_header + new_len,
                "text": source.get("text", ""),
            }
        )
    for records in by_table.values():
        records.sort(key=lambda record: record["old_header"])
    return by_table


def build_gaps(records: list[dict], *, old_segment_start: int, old_segment_end: int, new_segment_start: int, new_segment_end: int) -> list[dict]:
    gaps = []
    prev_old_end = old_segment_start
    prev_new_end = new_segment_start
    for record in records:
        if prev_old_end <= record["old_header"] and prev_new_end <= record["new_header"]:
            gaps.append(
                {
                    "old_start": prev_old_end,
                    "old_end": record["old_header"],
                    "new_start": prev_new_end,
                    "new_end": record["new_header"],
                    "next_text": record["text"],
                }
            )
        prev_old_end = max(prev_old_end, record["old_end"])
        prev_new_end = max(prev_new_end, record["new_end"])
    if prev_old_end < old_segment_end and prev_new_end < new_segment_end:
        gaps.append(
            {
                "old_start": prev_old_end,
                "old_end": old_segment_end,
                "new_start": prev_new_end,
                "new_end": new_segment_end,
                "next_text": None,
            }
        )
    return gaps


def analyze_operands() -> dict:
    jp = JP_ROM.read_bytes()
    en = EN_ROM.read_bytes()
    position_map = load_json(POSITION_MAP)
    extracted = load_json(EXTRACTED)
    extracted_by_offset = {int(record["offset"]): record for record in extracted}
    lengths = stable_opcode_lengths()

    segments = {int(segment["rel"]): segment for segment in position_map["segments"]}
    records_by_table = build_segment_records(jp, en, position_map["record_mappings"], extracted_by_offset)

    role_stats: dict[str, Counter[str]] = defaultdict(Counter)
    segment_summaries = []
    total_aligned_gaps = 0
    total_compared_gaps = 0
    total_command_pairs = 0

    for table_rel, records in sorted(records_by_table.items()):
        segment = segments.get(table_rel)
        if not segment:
            continue
        old_segment_start = int(segment["old_start"])
        old_segment_end = int(segment["old_end"])
        new_segment_start = int(segment["new_start"])
        new_segment_end = int(segment["new_end"])

        text_target_map = {record["old_header"]: record["new_header"] for record in records}
        command_target_map: dict[int, int] = {}
        compared_gaps = 0
        aligned_gaps = 0
        command_pairs = 0
        gaps = build_gaps(
            records,
            old_segment_start=old_segment_start,
            old_segment_end=old_segment_end,
            new_segment_start=new_segment_start,
            new_segment_end=new_segment_end,
        )
        parsed_gap_pairs = []
        for gap in gaps:
            if gap["old_end"] - gap["old_start"] > 0x1000 or gap["new_end"] - gap["new_start"] > 0x1000:
                continue
            old_commands, old_ok = parse_commands(jp, gap["old_start"], gap["old_end"], lengths)
            new_commands, new_ok = parse_commands(en, gap["new_start"], gap["new_end"], lengths)
            compared_gaps += 1
            if not old_ok or not new_ok or len(old_commands) != len(new_commands):
                continue
            if [command["opcode"] for command in old_commands] != [command["opcode"] for command in new_commands]:
                continue
            aligned_gaps += 1
            command_pairs += len(old_commands)
            for old_command, new_command in zip(old_commands, new_commands):
                command_target_map[int(old_command["local"])] = int(new_command["local"])
            parsed_gap_pairs.append((old_commands, new_commands))

        for old_commands, new_commands in parsed_gap_pairs:
            for old_command, new_command in zip(old_commands, new_commands):
                operands_old = old_command["operands"]
                operands_new = new_command["operands"]
                opcode_hex = f"{old_command['opcode']:02X} FF"
                for rel in range(0, min(len(operands_old), len(operands_new)) - 1, 2):
                    old_value = struct.unpack_from("<H", operands_old, rel)[0]
                    new_value = struct.unpack_from("<H", operands_new, rel)[0]
                    old_target = old_segment_start + old_value
                    expected = None
                    target_kind = None
                    if old_target in text_target_map:
                        expected = text_target_map[old_target] - new_segment_start
                        target_kind = "text_header"
                    elif old_target in command_target_map:
                        expected = command_target_map[old_target] - new_segment_start
                        target_kind = "command_start"
                    if expected is None:
                        continue
                    key = f"{opcode_hex}:u16:{rel // 2}:{target_kind}"
                    role_stats[key]["total"] += 1
                    if new_value == expected:
                        role_stats[key]["match"] += 1
                    else:
                        role_stats[key]["mismatch"] += 1

                for rel in range(0, min(len(operands_old), len(operands_new)) - 3, 4):
                    old_value = struct.unpack_from("<I", operands_old, rel)[0]
                    new_value = struct.unpack_from("<I", operands_new, rel)[0]
                    expected = None
                    target_kind = None
                    if old_value in text_target_map:
                        expected = text_target_map[old_value]
                        target_kind = "text_header"
                    elif old_value in command_target_map:
                        expected = command_target_map[old_value]
                        target_kind = "command_start"
                    if expected is None:
                        continue
                    key = f"{opcode_hex}:u32:{rel // 4}:{target_kind}"
                    role_stats[key]["total"] += 1
                    if new_value == expected:
                        role_stats[key]["match"] += 1
                    else:
                        role_stats[key]["mismatch"] += 1

        total_compared_gaps += compared_gaps
        total_aligned_gaps += aligned_gaps
        total_command_pairs += command_pairs
        segment_summaries.append(
            {
                "table_rel": table_rel,
                "record_count": len(records),
                "gap_count": len(gaps),
                "compared_gap_count": compared_gaps,
                "aligned_gap_count": aligned_gaps,
                "command_pair_count": command_pairs,
            }
        )

    roles = []
    for key, counts in sorted(role_stats.items()):
        total = counts["total"]
        match = counts["match"]
        roles.append(
            {
                "role": key,
                "total": total,
                "match": match,
                "mismatch": counts["mismatch"],
                "match_ratio": round(match / total, 3) if total else 0,
                "relocatable": total >= 3 and match / total >= 0.8,
            }
        )

    return {
        "summary": {
            "segments_with_mapped_records": len(records_by_table),
            "compared_gap_count": total_compared_gaps,
            "aligned_gap_count": total_aligned_gaps,
            "aligned_gap_ratio": round(total_aligned_gaps / total_compared_gaps, 3) if total_compared_gaps else 0,
            "command_pair_count": total_command_pairs,
            "operand_role_count": len(roles),
            "relocatable_role_count": sum(1 for role in roles if role["relocatable"]),
        },
        "roles": sorted(roles, key=lambda role: (-role["relocatable"], -role["match_ratio"], -role["total"], role["role"])),
        "segments": segment_summaries,
    }


def main() -> int:
    payload = analyze_operands()
    OUT_JSON.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    lines = [
        "# Entry8 English Operand Relocation",
        "",
        f"- Compared gaps: `{payload['summary']['compared_gap_count']}`",
        f"- Aligned gaps: `{payload['summary']['aligned_gap_count']}`",
        f"- Aligned gap ratio: `{payload['summary']['aligned_gap_ratio']}`",
        f"- Command pairs: `{payload['summary']['command_pair_count']}`",
        f"- Relocatable operand roles: `{payload['summary']['relocatable_role_count']}`",
        "",
        "## Relocatable Roles",
        "",
        "| role | total | match | mismatch | ratio |",
        "|---|---:|---:|---:|---:|",
    ]
    for role in [role for role in payload["roles"] if role["relocatable"]][:80]:
        lines.append(
            f"| `{role['role']}` | {role['total']} | {role['match']} | "
            f"{role['mismatch']} | {role['match_ratio']} |"
        )
    lines.extend(
        [
            "",
            "## Top Non-Relocatable Evidence",
            "",
            "| role | total | match | mismatch | ratio |",
            "|---|---:|---:|---:|---:|",
        ]
    )
    for role in [role for role in payload["roles"] if not role["relocatable"] and role["total"] >= 3][:40]:
        lines.append(
            f"| `{role['role']}` | {role['total']} | {role['match']} | "
            f"{role['mismatch']} | {role['match_ratio']} |"
        )
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")

    print(f"wrote {OUT_JSON}")
    print(f"wrote {OUT_MD}")
    print(json.dumps(payload["summary"], ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
