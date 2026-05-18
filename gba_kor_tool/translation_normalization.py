from __future__ import annotations

import json
from pathlib import Path
from typing import Iterable

ROOT = Path(__file__).resolve().parents[1]
PROFILE_PATH = ROOT / "confirmed_data" / "font_assets" / "translation_normalization_profile.json"

ASCII_TO_FULLWIDTH = {
    "!": "！",
    "?": "？",
    "~": "～",
    "(": "（",
    ")": "）",
    "/": "／",
    "-": "－",
    "@": "＠",
    "$": "＄",
}

for digit in range(10):
    ASCII_TO_FULLWIDTH[str(digit)] = chr(ord("０") + digit)


def is_japanese_or_han(ch: str) -> bool:
    return (
        "\u3040" <= ch <= "\u30ff"
        or "\u3400" <= ch <= "\u9fff"
        or ch == "々"
    )


def extract_safe_chars_from_texts(texts: Iterable[str]) -> list[str]:
    chars = set()
    for text in texts:
        for ch in text:
            if not is_japanese_or_han(ch):
                chars.add(ch)
    return sorted(chars)


def build_default_profile(texts: Iterable[str]) -> dict:
    safe_chars = extract_safe_chars_from_texts(texts)
    preferred_chars = [
        ch
        for ch in [
            "　",
            "…",
            "！",
            "？",
            "～",
            "（",
            "）",
            "／",
            "－",
            "＠",
            "＄",
            "０",
            "１",
            "２",
            "３",
            "４",
            "５",
            "６",
            "７",
            "８",
            "９",
        ]
        if ch in safe_chars
    ]
    replacements = {
        "...": "…" if "…" in safe_chars else "...",
        " ": "　" if "　" in safe_chars else " ",
    }
    for src, dst in ASCII_TO_FULLWIDTH.items():
        replacements[src] = dst if dst in safe_chars else src
    return {
        "version": 1,
        "safe_chars": safe_chars,
        "preferred_chars": preferred_chars,
        "replacements": replacements,
        "notes": [
            "현재 추출본에서 실제로 확인된 비일본어/비한자 문자 기준 프로필",
            "GUI 저장, 에이전트 결과 병합, ROM 적용 전에 같은 정규화를 적용한다",
        ],
    }


def load_profile() -> dict:
    if PROFILE_PATH.exists():
        return json.loads(PROFILE_PATH.read_text(encoding="utf-8"))
    return build_default_profile([])


def normalize_translation_text(text: str, *, profile: dict | None = None) -> str:
    if not text:
        return text
    if profile is None:
        profile = load_profile()
    replacements = dict(profile.get("replacements", {}))

    normalized = text.replace("\r\n", "\n").replace("\r", "\n").replace("\t", " ")

    if "..." in replacements:
        normalized = normalized.replace("...", replacements["..."])

    out = []
    for ch in normalized:
        out.append(replacements.get(ch, ch))
    return "".join(out)
