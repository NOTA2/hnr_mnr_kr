#!/usr/bin/env python3

from __future__ import annotations

import argparse
import json
import unicodedata
from pathlib import Path


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="현재 번역 기준 문자 집합 리포트를 생성합니다.")
    parser.add_argument("output_json")
    parser.add_argument("output_non_hangul_txt")
    parser.add_argument("inputs", nargs="+")
    parser.add_argument("--field", default="translation")
    return parser.parse_args()


def iter_strings(value):
    if isinstance(value, str):
        yield value
    elif isinstance(value, list):
        for item in value:
            yield from iter_strings(item)
    elif isinstance(value, dict):
        for item in value.values():
            yield from iter_strings(item)


def main() -> int:
    args = parse_args()
    chars: set[str] = set()

    for item in args.inputs:
        path = Path(item)
        payload = json.loads(path.read_text(encoding="utf-8"))
        if isinstance(payload, list):
            for row in payload:
                if isinstance(row, dict):
                    for text in iter_strings(row.get(args.field)):
                        chars.update(text)

    hangul = sorted([c for c in chars if 0xAC00 <= ord(c) <= 0xD7A3])
    digits = sorted([c for c in chars if c.isdigit()])
    spaces = sorted([c for c in chars if c.isspace()])
    latin = sorted([c for c in chars if "LATIN" in unicodedata.name(c, "")])
    other = sorted(
        [
            c
            for c in chars
            if c not in hangul and c not in digits and c not in spaces and c not in latin
        ]
    )

    report = {
        "input_files": args.inputs,
        "field": args.field,
        "unique_char_count": len(chars),
        "hangul_count": len(hangul),
        "digits_count": len(digits),
        "latin_count": len(latin),
        "space_count": len(spaces),
        "other_count": len(other),
        "hangul": "".join(hangul),
        "digits": "".join(digits),
        "latin": "".join(latin),
        "spaces": "".join(spaces),
        "other": "".join(other),
    }

    Path(args.output_json).write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")

    non_hangul = []
    if digits:
        non_hangul.append("".join(digits))
    if spaces:
        non_hangul.append("".join(spaces))
    if latin:
        non_hangul.append("".join(latin))
    if other:
        non_hangul.append("".join(other))
    Path(args.output_non_hangul_txt).write_text("\n".join(non_hangul) + "\n", encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
