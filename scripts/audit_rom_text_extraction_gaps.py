#!/usr/bin/env python3

from __future__ import annotations

import argparse
import json
import sys
from bisect import bisect_right
from dataclasses import dataclass
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from gba_kor_tool.cli import ROM_BASE, contains_japanese, is_text_printable, japanese_ratio

DEFAULT_ROM = ROOT / "Hagane no Renkinjutsushi - Meisou no Rondo (Japan).gba"
EXTRACTED_DIR = ROOT / "confirmed_data" / "extracted_texts"
OUT_JSON = ROOT / "confirmed_data" / "translation_workspace" / "rom_text_extraction_gap_audit.json"
OUT_MD = ROOT / "confirmed_data" / "translation_workspace" / "rom_text_extraction_gap_audit.md"

SJIS_LEADS = set(range(0x81, 0xA0)) | set(range(0xE0, 0xFD))
SJIS_TRAILS = set(range(0x40, 0x7F)) | set(range(0x80, 0xFD))
TERMINATORS = {0x00, 0xFF}
INLINE_CONTROLS = {0x0B, 0x0C}


@dataclass(frozen=True)
class Candidate:
    offset: int
    byte_length: int
    terminator: int | None
    text: str

    @property
    def end(self) -> int:
        return self.offset + self.byte_length


def load_json(path: Path) -> list[dict]:
    return json.loads(path.read_text(encoding="utf-8"))


def iter_extracted_intervals() -> list[tuple[int, int, str, str]]:
    intervals: list[tuple[int, int, str, str]] = []
    for path in sorted(EXTRACTED_DIR.glob("*.json")):
        source_group = path.stem
        for record in load_json(path):
            offset = int(record.get("offset", -1))
            byte_length = int(record.get("byte_length", 0))
            text = record.get("text") or record.get("decoded_text") or ""
            if offset >= 0 and byte_length > 0:
                intervals.append((offset, offset + byte_length, source_group, text))
    intervals.sort()
    return intervals


def interval_cover_lookup(intervals: list[tuple[int, int, str, str]]):
    starts = [row[0] for row in intervals]

    def find(offset: int) -> tuple[int, int, str, str] | None:
        index = bisect_right(starts, offset) - 1
        if index < 0:
            return None
        row = intervals[index]
        return row if row[0] <= offset < row[1] else None

    return find


def decode_one(data: bytes, offset: int) -> tuple[str, int] | None:
    byte = data[offset]
    if byte in INLINE_CONTROLS:
        return chr(byte), 1
    if 0x20 <= byte <= 0x7E or 0xA1 <= byte <= 0xDF:
        try:
            return bytes([byte]).decode("cp932"), 1
        except UnicodeDecodeError:
            return None
    if byte in SJIS_LEADS and offset + 1 < len(data) and data[offset + 1] in SJIS_TRAILS:
        payload = data[offset:offset + 2]
        try:
            return payload.decode("cp932"), 2
        except UnicodeDecodeError:
            return None
    return None


def parse_candidate(data: bytes, start: int, max_bytes: int) -> Candidate | None:
    cursor = start
    chars: list[str] = []
    while cursor < len(data) and cursor - start < max_bytes:
        byte = data[cursor]
        if byte in TERMINATORS:
            break
        decoded = decode_one(data, cursor)
        if decoded is None:
            break
        char, size = decoded
        chars.append(char)
        cursor += size
    if cursor == start:
        return None
    terminator = data[cursor] if cursor < len(data) and data[cursor] in TERMINATORS else None
    return Candidate(start, cursor - start, terminator, "".join(chars))


def is_plausible_candidate(candidate: Candidate, *, min_chars: int, min_japanese: int, min_japanese_ratio: float) -> bool:
    text = candidate.text
    if len(text) < min_chars:
        return False
    if not contains_japanese(text):
        return False
    if sum(1 for char in text if contains_japanese(char)) < min_japanese:
        return False
    if japanese_ratio(text) < min_japanese_ratio:
        return False
    printable = sum(1 for char in text if is_text_printable(char)) / len(text)
    if printable < 0.95:
        return False
    if text.count("?") >= 3 and japanese_ratio(text) < 0.75:
        return False
    if any(token in text for token in ("主@", "&&", "||", "://")):
        return False
    return True


def remove_nested_candidates(candidates: list[Candidate]) -> list[Candidate]:
    kept: list[Candidate] = []
    for candidate in sorted(candidates, key=lambda row: (row.offset, -row.byte_length)):
        if kept and kept[-1].offset <= candidate.offset and candidate.end <= kept[-1].end:
            continue
        kept.append(candidate)
    return kept


def main() -> int:
    parser = argparse.ArgumentParser(description="Scan the source ROM for plausible Japanese text that is not in extracted_texts.")
    parser.add_argument("--rom", type=Path, default=DEFAULT_ROM)
    parser.add_argument("--max-bytes", type=int, default=96)
    parser.add_argument("--min-chars", type=int, default=4)
    parser.add_argument("--min-japanese", type=int, default=2)
    parser.add_argument("--min-japanese-ratio", type=float, default=0.35)
    parser.add_argument("--limit", type=int, default=300)
    args = parser.parse_args()

    data = args.rom.read_bytes()
    intervals = iter_extracted_intervals()
    find_cover = interval_cover_lookup(intervals)

    raw_candidates: list[Candidate] = []
    for offset in range(len(data)):
        if find_cover(offset) is not None:
            continue
        candidate = parse_candidate(data, offset, args.max_bytes)
        if candidate is None:
            continue
        if not is_plausible_candidate(
            candidate,
            min_chars=args.min_chars,
            min_japanese=args.min_japanese,
            min_japanese_ratio=args.min_japanese_ratio,
        ):
            continue
        raw_candidates.append(candidate)

    candidates = remove_nested_candidates(raw_candidates)
    rows = [
        {
            "offset": candidate.offset,
            "rom_address": ROM_BASE + candidate.offset,
            "byte_length": candidate.byte_length,
            "terminator": None if candidate.terminator is None else f"0x{candidate.terminator:02X}",
            "text": candidate.text,
            "japanese_ratio": round(japanese_ratio(candidate.text), 3),
        }
        for candidate in candidates
    ]

    report = {
        "version": 1,
        "rom": str(args.rom),
        "rom_size": len(data),
        "extracted_interval_count": len(intervals),
        "candidate_count": len(rows),
        "candidates": rows,
    }
    OUT_JSON.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    lines = [
        "# ROM Text Extraction Gap Audit",
        "",
        f"- ROM: `{args.rom}`",
        f"- extracted interval count: `{len(intervals)}`",
        f"- missing-candidate count: `{len(rows)}`",
        "",
        "## Candidates",
        "",
    ]
    for row in rows[: args.limit]:
        text = row["text"].replace("\x0b", "\\x0b").replace("\x0c", "\\x0c")
        lines.append(
            f"- `0x{row['offset']:06X}` `{row['byte_length']}` bytes term=`{row['terminator']}` jp=`{row['japanese_ratio']}`: {text}"
        )
    if len(rows) > args.limit:
        lines.append(f"- ... `{len(rows) - args.limit}` more candidates omitted from markdown preview.")
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")

    print(f"wrote {OUT_JSON}")
    print(f"wrote {OUT_MD}")
    print(f"candidate_count: {len(rows)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
