#!/usr/bin/env python3

from __future__ import annotations

import json
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
EXTRACTED = ROOT / "confirmed_data" / "extracted_texts" / "registry_a_entry8_prefixed_texts.json"
OUT_JSON = ROOT / "analysis" / "entry8_missing_prefixed_records_audit.json"
OUT_MD = ROOT / "analysis" / "entry8_missing_prefixed_records_audit.md"


def load_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def read_entry8_bounds(data: bytes) -> tuple[int, int]:
    table = REGISTRY_A_TABLE_OFFSET + REGISTRY_A_ENTRY8_INDEX * 8
    entry_offset = struct.unpack_from("<I", data, table)[0] - ROM_BASE
    entry_length = struct.unpack_from("<I", data, table + 4)[0]
    return entry_offset, entry_offset + entry_length


def build() -> dict:
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
    existing = load_json(EXTRACTED)
    existing_offsets = {int(record["offset"]) for record in existing}
    missing = [record for record in scanned if int(record["offset"]) not in existing_offsets]

    return {
        "last_updated": datetime.now(timezone.utc).isoformat(),
        "rom": str(JP_ROM.relative_to(ROOT)),
        "entry8": {
            "start_offset": start,
            "end_offset_exclusive": end,
            "start_offset_hex": f"0x{start:06X}",
            "end_offset_exclusive_hex": f"0x{end:06X}",
        },
        "scanner": {
            "prefix": "01 FF",
            "count_size": 2,
            "count_endian": "little",
            "encoding": "cp932",
            "min_chars": 1,
            "max_chars": 128,
        },
        "summary": {
            "existing_extracted_records": len(existing_offsets),
            "rescanned_candidates": len(scanned),
            "missing_candidates": len(missing),
            "missing_by_char_count": dict(sorted(Counter(record["char_count"] for record in missing).items())),
        },
        "notes": [
            "기존 Entry8 추출은 4글자 이상 위주로 잡힌 것으로 보이며, 1~3글자 접두/감탄사 레코드가 대량 누락되었다.",
            "이 파일의 missing_candidates 는 ROM 구조상 01 FF <u16 char_count> 로 읽히는 후보 목록이다. 대부분 실제 대사 조각으로 보이나, 전체 자동 반영 전에는 짧은 샘플 검수가 필요하다.",
        ],
        "missing_candidates": missing,
    }


def render_md(report: dict) -> str:
    summary = report["summary"]
    lines = [
        "# Entry8 Missing Prefixed Records Audit",
        "",
        f"- Last updated: `{report['last_updated']}`",
        f"- Entry8 range: `{report['entry8']['start_offset_hex']}` - `{report['entry8']['end_offset_exclusive_hex']}`",
        f"- Existing extracted records: `{summary['existing_extracted_records']}`",
        f"- Rescanned candidates with min_chars=1: `{summary['rescanned_candidates']}`",
        f"- Missing candidates: `{summary['missing_candidates']}`",
        f"- Missing by char_count: `{summary['missing_by_char_count']}`",
        "",
        "## Reading",
        "",
    ]
    lines.extend(f"- {note}" for note in report["notes"])
    lines.extend(["", "## First Missing Candidates", ""])
    for record in report["missing_candidates"][:160]:
        lines.append(
            f"- `0x{int(record['offset']):06X}` "
            f"header `0x{int(record['header_offset']):06X}` "
            f"chars `{record['char_count']}`: {record['text']!r}"
        )
    return "\n".join(lines).rstrip() + "\n"


def main() -> int:
    report = build()
    OUT_JSON.parent.mkdir(parents=True, exist_ok=True)
    OUT_JSON.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    OUT_MD.write_text(render_md(report), encoding="utf-8")
    print(f"written: {OUT_JSON}")
    print(f"written: {OUT_MD}")
    print(json.dumps(report["summary"], ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
