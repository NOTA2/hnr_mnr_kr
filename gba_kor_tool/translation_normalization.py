from __future__ import annotations

import json
import re
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

UNICODE_COMPAT_REPLACEMENTS = {
    "·": "・",
    "’": "'",
    "‘": "'",
    "“": '"',
    "”": '"',
}

FULLWIDTH_LATIN_ABBREVIATIONS = {
    "HP": "ＨＰ",
    "AS": "ＡＳ",
    "R 버튼": "Ｒ 버튼",
}

NARROW_PUNCTUATION_SOURCE_GROUPS = {
    "registry_d_fc_script_texts",
    "item_texts",
    "material_texts",
    "battle_texts",
    "ability_texts",
    "registry_a_entry12_texts",
    "ui_skill_texts",
    "system_messages",
    "credits_texts",
    "registry_a_map_labels",
    "duplicate_text_slots",
}

FULLWIDTH_PUNCTUATION_SOURCE_GROUPS = {
    "startup_intro_texts",
    "save_menu_texts",
    "choice_yes_no_texts",
    "registry_a_entry8_prefixed_texts",
    "inline_event_texts",
}

FULLWIDTH_SPACE_SOURCE_GROUPS = {
    "startup_intro_texts",
    "save_menu_texts",
    "choice_yes_no_texts",
    "credits_texts",
    "inline_event_texts",
    "registry_a_entry8_prefixed_texts",
}

FULLWIDTH_DIGIT_SOURCE_GROUPS = {
    # These renderers/counted slots have shown halfwidth instability or are
    # fixed-width enough that keeping the original fullwidth path is safer.
    "startup_intro_texts",
    "inline_event_texts",
    "save_menu_texts",
    "choice_yes_no_texts",
    "registry_a_entry8_prefixed_texts",
}

ENTRY8_FIXED_WIDTH_SOURCE_GROUPS = {
    "registry_a_entry8_prefixed_texts",
    "inline_event_texts",
}

COMMA_FOLLOWING_SPACE_RE = re.compile(r"([,、，])[\u3000 ]+")

TERM_DESCRIPTION_SOURCE_GROUPS = {
    "battle_texts",
    "ability_texts",
    "material_texts",
}

JAPANESE_TEXT_RE = re.compile(
    r"[\u3041-\u3096\u309d-\u309f\u30a1-\u30fa\u30fd-\u30ff\u3400-\u9fff]"
)


def is_japanese_or_han(ch: str) -> bool:
    return bool(JAPANESE_TEXT_RE.fullmatch(ch)) or ch == "々"


def contains_japanese_text(text: str | None) -> bool:
    """True only for real kana/kanji text, not preserved Japanese punctuation."""
    return bool(text and JAPANESE_TEXT_RE.search(text))


def japanese_text_ratio(text: str | None) -> float:
    if not text:
        return 0.0
    return sum(1 for ch in text if is_japanese_or_han(ch)) / len(text)


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
        ]
        if ch in safe_chars
    ]
    replacements = {
        "...": "…" if "…" in safe_chars else "...",
        " ": "　" if "　" in safe_chars else " ",
    }
    for src, dst in ASCII_TO_FULLWIDTH.items():
        replacements[src] = dst if dst in safe_chars else src
    for digit in range(10):
        replacements[str(digit)] = str(digit)
        replacements[chr(ord("０") + digit)] = str(digit)
    replacements.update(
        {
            "，": ",",
            "、": ",",
            "’": "'",
            "‘": "'",
            "“": '"',
            "”": '"',
        }
    )
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


def display_units(text: str) -> int:
    units = 0
    for ch in text:
        if ch == " ":
            units += 1
        else:
            units += 2
    return units


def pad_term_name_field(name: str, *, reference_text: str | None = None) -> str:
    if not reference_text or "\x0b" not in reference_text:
        return name
    reference_name = reference_text.split("\x0b", 1)[0]
    target_units = display_units(reference_name)
    current_units = display_units(name)
    if current_units >= target_units:
        return name
    padding_units = target_units - current_units
    fullwidth_spaces, halfwidth_spaces = divmod(padding_units, 2)
    return f"{name}{'　' * fullwidth_spaces}{' ' * halfwidth_spaces}"


def normalize_term_description_layout(text: str, *, reference_text: str | None = None) -> str:
    separator = "\x0b" if "\x0b" in text else "\n" if "\n" in text else None
    if separator is None:
        return text
    name, description = text.split(separator, 1)
    reference_has_inline_separator = bool(reference_text and "\x0b" in reference_text)
    # These records use a fixed-width name field before the inline 0x0B
    # separator. The alchemy info panel relies on that field width for layout,
    # so synthesize the padding from the original Japanese record instead of
    # asking translators to insert manual spaces per item.
    normalized_name = name.replace("　", " ").strip()
    normalized_description = description.replace("　", " ").strip()
    if not reference_has_inline_separator:
        # A few short ability records have no native 0x0B separator. When we
        # split them for readability, use the renderer's real newline byte
        # instead of injecting the inline name/description separator.
        return f"{normalized_name}\n{normalized_description}"
    padded_name = pad_term_name_field(normalized_name, reference_text=reference_text)
    return f"{padded_name}\x0b{normalized_description}"


def normalize_translation_text(
    text: str,
    *,
    profile: dict | None = None,
    source_group: str | None = None,
    reference_text: str | None = None,
) -> str:
    if not text:
        return text
    if profile is None:
        profile = load_profile()
    replacements = dict(profile.get("replacements", {}))
    replacements.update(UNICODE_COMPAT_REPLACEMENTS)
    for digit in range(10):
        replacements[str(digit)] = str(digit)
        replacements[chr(ord("０") + digit)] = str(digit)
    if source_group in FULLWIDTH_DIGIT_SOURCE_GROUPS:
        for digit in range(10):
            replacements[str(digit)] = chr(ord("０") + digit)
            replacements[chr(ord("０") + digit)] = chr(ord("０") + digit)
    if source_group not in FULLWIDTH_SPACE_SOURCE_GROUPS:
        replacements[" "] = " "
        replacements["　"] = " "
    if source_group in NARROW_PUNCTUATION_SOURCE_GROUPS:
        replacements.update(
            {
                "!": "!",
                "！": "!",
                "?": "?",
                "？": "?",
                ",": ",",
                "，": ",",
                "、": ",",
                "'": "'",
                "’": "'",
                "‘": "'",
                '"': '"',
                "“": '"',
                "”": '"',
                "-": "-",
                "－": "-",
                "/": "/",
                "／": "/",
            }
        )
        for digit in range(10):
            replacements[str(digit)] = str(digit)
            replacements[chr(ord("０") + digit)] = str(digit)
    if source_group in FULLWIDTH_PUNCTUATION_SOURCE_GROUPS:
        replacements.update(
            {
                "!": "！",
                "！": "！",
                "?": "？",
                "？": "？",
                ".": "。",
                "。": "。",
                ",": "、",
                "，": "、",
                "、": "、",
                ":": "：",
                "：": "：",
                "-": "－",
                "－": "－",
                "/": "／",
                "／": "／",
                "~": "～",
                "～": "～",
                "(": "（",
                "（": "（",
                ")": "）",
                "）": "）",
            }
        )
    if source_group in ENTRY8_FIXED_WIDTH_SOURCE_GROUPS:
        replacements.update(
            {
                " ": "　",
                "　": "　",
                "!": "！",
                "！": "！",
                "?": "？",
                "？": "？",
                ".": "。",
                "。": "。",
                ",": "、",
                "，": "、",
                "、": "、",
                "~": "～",
                "～": "～",
                "(": "（",
                "（": "（",
                ")": "）",
                "）": "）",
                "-": "－",
                "－": "－",
                "/": "／",
                "／": "／",
            }
        )
        for digit in range(10):
            replacements[str(digit)] = chr(ord("０") + digit)
            replacements[chr(ord("０") + digit)] = chr(ord("０") + digit)

    normalized = text.replace("\r\n", "\n").replace("\r", "\n").replace("\t", " ")

    if source_group != "registry_d_fc_script_texts":
        for src, dst in FULLWIDTH_LATIN_ABBREVIATIONS.items():
            normalized = normalized.replace(src, dst)

    if "..." in replacements:
        normalized = normalized.replace("...", replacements["..."])

    for src, dst in UNICODE_COMPAT_REPLACEMENTS.items():
        normalized = normalized.replace(src, dst)

    out = []
    for ch in normalized:
        out.append(replacements.get(ch, ch))
    normalized = "".join(out)
    if source_group in ENTRY8_FIXED_WIDTH_SOURCE_GROUPS:
        normalized = COMMA_FOLLOWING_SPACE_RE.sub(r"\1", normalized)
    if source_group in TERM_DESCRIPTION_SOURCE_GROUPS:
        normalized = normalize_term_description_layout(normalized, reference_text=reference_text)
    return normalized
