#!/usr/bin/env python3

from __future__ import annotations

import json
import re
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
WORKSET = ROOT / "confirmed_data" / "translation_worksets" / "translation_workset_gameplay_terms.json"

FORBIDDEN_FIRST_LINES = {
    "말 석상",
    "석상 연성",
    "대기연성",
    "물 연성",
    "대량의 물",
    "지면 분쇄",
    "벽에서 창 발사",
    "지진 발생",
    "지면 파동",
    "음의 흐름",
    "나무촉수",
    "벽에서 손",
    "꿈틀가시",
    "고양이들",
    "지면펀치",
}

ACTION_SECOND_LINES = {
    "돌진시킨다",
    "관통",
    "관통공격",
    "전체 관통",
    "조여 공격",
    "나와 공격",
    "충격파 공격",
    "파도 공격",
    "해일 공격",
    "부딪혀 공격",
    "전체 공격",
    "발사 공격",
    "공격한다",
    "공격",
    "아래서 공격",
    "알을 위해 공격",
}

GOOD_ENDING_RE = re.compile(r"(을|를|이|가|로|으로|해|해서|켜|쳐|숴|어|서)$")
BAD_TRANSLATION_PATTERNS = {
    "　": "translation contains fullwidth spacing",
    "내리꽂": "overlong iron-giant wording should use 꽂음/꽂는다",
    "말 석상\n": "horse statue wording must include 을 before the break",
}


def clean_line(text: str) -> str:
    return text.replace("　", " ").strip()


def main() -> int:
    rows = json.loads(WORKSET.read_text(encoding="utf-8"))
    findings: list[str] = []
    for record in rows:
        translation = record.get("translation") or ""
        source_group = str(record.get("source_group", ""))
        source_text = record.get("text") or ""
        if re.search(r"[０-９／]", translation):
            findings.append(
                f"0x{int(record['offset']):06X}: digits/slash must stay halfwidth: {translation!r} "
                f"source={source_text!r}"
            )
        if (
            source_group in {"ability_texts", "battle_texts", "material_texts"}
            and "\x0b" not in source_text
            and "\x0b" in translation
        ):
            findings.append(
                f"0x{int(record['offset']):06X}: native single-line term split must use newline, not 0x0B: "
                f"{translation!r} source={source_text!r}"
            )
        for pattern, reason in BAD_TRANSLATION_PATTERNS.items():
            if pattern in translation.replace("\x0b", "\n"):
                findings.append(
                    f"0x{int(record['offset']):06X}: {reason}: {translation!r} "
                    f"source={source_text!r}"
                )
        if "\x0b" not in translation:
            continue
        first, second = translation.split("\x0b", 1)
        first = clean_line(first)
        second = clean_line(second)
        if first in FORBIDDEN_FIRST_LINES:
            findings.append(
                f"0x{int(record['offset']):06X}: forbidden first line {first!r} / {second!r} "
                f"source={record.get('text')!r}"
            )
            continue
        if second in ACTION_SECOND_LINES and first and not GOOD_ENDING_RE.search(first):
            findings.append(
                f"0x{int(record['offset']):06X}: suspicious first line {first!r} / {second!r} "
                f"source={record.get('text')!r}"
            )

    if findings:
        print("gameplay term particle/style audit failed:")
        for finding in findings:
            print(f"- {finding}")
        return 1
    print("gameplay term particle/style audit passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
