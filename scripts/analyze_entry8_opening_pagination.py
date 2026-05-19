#!/usr/bin/env python3

from __future__ import annotations

import json
import struct
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
JP_ROM = ROOT / "Hagane no Renkinjutsushi - Meisou no Rondo (Japan).gba"
EN_ROM = ROOT / "local_roms" / "english_patched" / "Fullmetal Alchemist Stray Rondo (English Patched v0.02).gba"
MAPPING_PATH = ROOT / "analysis" / "entry8_english_record_position_map.json"
EXTRACTED_PATH = ROOT / "confirmed_data" / "extracted_texts" / "registry_a_entry8_prefixed_texts.json"
OUT_JSON = ROOT / "analysis" / "entry8_opening_pagination_analysis.json"
OUT_MD = ROOT / "analysis" / "entry8_opening_pagination_analysis.md"

ENTRY8_OFFSET = 0x6B594C
SEG150_TABLE_REL = 0x150
SEG15C_TABLE_REL = 0x15C
OPENING_MIN = 0x76B1F8
OPENING_MAX = 0x76B430


def u32(data: bytes, offset: int) -> int:
    return struct.unpack_from("<I", data, offset)[0]


def read_header(data: bytes, file_offset: int) -> dict:
    prefix = data[file_offset:file_offset + 2].hex(" ")
    count = struct.unpack_from("<H", data, file_offset + 2)[0]
    return {"prefix": prefix, "char_count": count}


def hex_bytes(data: bytes, start: int, end: int, *, limit: int = 96) -> str:
    payload = data[start:min(end, start + limit)]
    suffix = " ..." if end - start > limit else ""
    return payload.hex(" ") + suffix


def main() -> int:
    jp = JP_ROM.read_bytes()
    en = EN_ROM.read_bytes()
    mapping = json.loads(MAPPING_PATH.read_text(encoding="utf-8"))["record_mappings"]
    extracted_records = json.loads(EXTRACTED_PATH.read_text(encoding="utf-8"))
    extracted_by_offset = {int(record["offset"]): record for record in extracted_records}

    jp_seg150 = u32(jp, ENTRY8_OFFSET + SEG150_TABLE_REL)
    jp_seg15c = u32(jp, ENTRY8_OFFSET + SEG15C_TABLE_REL)
    en_seg150 = u32(en, ENTRY8_OFFSET + SEG150_TABLE_REL)
    en_seg15c = u32(en, ENTRY8_OFFSET + SEG15C_TABLE_REL)

    rows = []
    for item in mapping:
        offset = int(item["offset"])
        if not (OPENING_MIN <= offset <= OPENING_MAX):
            continue
        source = extracted_by_offset.get(offset, {})
        old_header_local = int(item["old_header_local"])
        new_header_local = int(item["new_header_local"])
        old_segment = jp_seg150 if old_header_local < jp_seg15c else jp_seg15c
        new_segment = en_seg150 if int(item["table_rel"]) == SEG150_TABLE_REL else en_seg15c
        old_file = ENTRY8_OFFSET + old_header_local
        new_file = ENTRY8_OFFSET + new_header_local
        rows.append(
            {
                "offset": offset,
                "offset_hex": f"0x{offset:06X}",
                "text": source.get("text", ""),
                "translation": source.get("translation", ""),
                "table_rel": int(item["table_rel"]),
                "jp_header_local": old_header_local,
                "jp_segment_rel": old_header_local - old_segment,
                "jp_header": read_header(jp, old_file),
                "en_header_local": new_header_local,
                "en_segment_rel": new_header_local - new_segment,
                "en_header": read_header(en, new_file),
            }
        )

    rows.sort(key=lambda row: (row["table_rel"], row["jp_header_local"]))
    for index, row in enumerate(rows):
        next_row = rows[index + 1] if index + 1 < len(rows) and rows[index + 1]["table_rel"] == row["table_rel"] else None
        jp_record_end = row["jp_header_local"] + 4 + int(extracted_by_offset[row["offset"]]["byte_length"])
        if next_row:
            row["jp_control_gap_after"] = next_row["jp_header_local"] - jp_record_end
            row["en_control_gap_after"] = next_row["en_header_local"] - (row["en_header_local"] + 4 + row["en_header"]["char_count"] * 2)
        else:
            row["jp_control_gap_after"] = None
            row["en_control_gap_after"] = None

    snippets = []
    interesting_ranges = [
        ("jp_seg150_opening_text_area", jp, ENTRY8_OFFSET + jp_seg150 + 0xE70, ENTRY8_OFFSET + jp_seg150 + 0x1090),
        ("en_seg150_early_first_line_area", en, ENTRY8_OFFSET + en_seg150 + 0x260, ENTRY8_OFFSET + en_seg150 + 0x320),
        ("en_seg150_opening_text_area", en, ENTRY8_OFFSET + en_seg150 + 0xEF0, ENTRY8_OFFSET + en_seg150 + 0x1010),
        ("en_seg15c_start_area", en, ENTRY8_OFFSET + en_seg15c, ENTRY8_OFFSET + en_seg15c + 0x120),
    ]
    for name, data, start, end in interesting_ranges:
        snippets.append({"name": name, "file_start": start, "file_end": end, "bytes": hex_bytes(data, start, end)})

    payload = {
        "summary": {
            "jp_seg150": jp_seg150,
            "jp_seg15c": jp_seg15c,
            "en_seg150": en_seg150,
            "en_seg15c": en_seg15c,
            "jp_seg150_block_len": u32(jp, ENTRY8_OFFSET + jp_seg150 + 0xE88),
            "en_seg150_block_len": u32(en, ENTRY8_OFFSET + en_seg150 + 0xE88),
            "record_count": len(rows),
        },
        "records": rows,
        "snippets": snippets,
    }
    OUT_JSON.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    lines = [
        "# Entry8 Opening Pagination Analysis",
        "",
        "## Summary",
        "",
        f"- JP segment 0x150: `0x{jp_seg150:X}`",
        f"- JP segment 0x15C: `0x{jp_seg15c:X}`",
        f"- EN segment 0x150: `0x{en_seg150:X}`",
        f"- EN segment 0x15C: `0x{en_seg15c:X}`",
        f"- JP opening block length: `0x{payload['summary']['jp_seg150_block_len']:X}`",
        f"- EN opening block length: `0x{payload['summary']['en_seg150_block_len']:X}`",
        "",
        "## Record Map",
        "",
        "| JP offset | JP rel | EN rel | JP cnt | EN cnt | JP gap | EN gap | Text |",
        "|---:|---:|---:|---:|---:|---:|---:|---|",
    ]
    for row in rows:
        lines.append(
            f"| `{row['offset_hex']}` | `0x{row['jp_segment_rel']:X}` | `0x{row['en_segment_rel']:X}` | "
            f"{row['jp_header']['char_count']} | {row['en_header']['char_count']} | "
            f"{'' if row['jp_control_gap_after'] is None else row['jp_control_gap_after']} | "
            f"{'' if row['en_control_gap_after'] is None else row['en_control_gap_after']} | "
            f"{row['text']} |"
        )
    lines.extend(
        [
            "",
            "## Notes",
            "",
            "- EN does not preserve JP relative positions. The first alchemy line is moved far earlier inside segment `0x150`.",
            "- EN expands the opening block length and redistributes later lines across the rebuilt segment.",
            "- This should be treated as event-script pagination, not as a simple text repoint template.",
            "",
        ]
    )
    OUT_MD.write_text("\n".join(lines), encoding="utf-8")
    print(f"wrote {OUT_JSON}")
    print(f"wrote {OUT_MD}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
