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

ASCII_DIGIT_TO_FULLWIDTH = {
    str(digit): chr(ord("０") + digit)
    for digit in range(10)
}
FULLWIDTH_DIGIT_TO_ASCII = {
    chr(ord("０") + digit): str(digit)
    for digit in range(10)
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
    "ui_status_texts",
    "registry_a_entry8_prefixed_texts",
    "inline_event_texts",
}

FULLWIDTH_SPACE_SOURCE_GROUPS = {
    "startup_intro_texts",
    "save_menu_texts",
    "choice_yes_no_texts",
    "ui_status_texts",
    "credits_texts",
    "inline_event_texts",
    "registry_a_entry8_prefixed_texts",
}

FULLWIDTH_DIGIT_SOURCE_GROUPS = {
    # Fallback only when a caller has no reference text. If the original/source
    # text contains digits, its digit width wins over this group default.
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
DIGIT_RUN_RE = re.compile(r"[0-9０-９]+")

TERM_DESCRIPTION_SOURCE_GROUPS = {
    "battle_texts",
    "ability_texts",
    "material_texts",
}

RECOVERY_MEDICINE_BATTLE_DESCRIPTION_RE = re.compile(r"^体力を[０-９]+[\u3000 ]*\x0b回復する薬$")
RECOVERY_MEDICINE_NUMBER_RE = re.compile(r"^回復薬[0-9０-９](?:$|体力を)")
CERTIFICATE_PROGRESS_LABEL_RE = re.compile(r"^証[\u3000 ](?:[０-９]{2}／１０|ＦＩＮＳＨ)$")
SPEAR_ALCHEMY_ATTACK_SOURCE_TEXT = "槍を錬成して攻撃"

TEXT_LAYOUT_METADATA_SOURCE_GROUPS = {
    "location_texts",
}

WORLD_MAP_LOCATION_SOURCE_GROUPS = TEXT_LAYOUT_METADATA_SOURCE_GROUPS

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
        fullwidth_digit = chr(ord("０") + digit)
        replacements[str(digit)] = str(digit)
        replacements[fullwidth_digit] = fullwidth_digit
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
            "숫자/숫자 주변 슬래시는 원문 폭을 따른다. 프로필 기본값은 숫자 모양을 보존하고, 실제 정규화 단계가 reference_text 를 보고 폭을 결정한다.",
        ],
    }


def preferred_digit_width(reference_text: str | None, source_group: str | None = None) -> str | None:
    reference = reference_text or ""
    has_ascii = bool(re.search(r"[0-9]", reference))
    has_fullwidth = bool(re.search(r"[０-９]", reference))
    if has_ascii and not has_fullwidth:
        return "ascii"
    if has_fullwidth and not has_ascii:
        return "fullwidth"
    if has_ascii and has_fullwidth:
        return None
    if source_group in FULLWIDTH_DIGIT_SOURCE_GROUPS:
        return "fullwidth"
    return None


def preferred_slash_width(reference_text: str | None) -> str | None:
    reference = reference_text or ""
    has_ascii = "/" in reference
    has_fullwidth = "／" in reference
    if has_ascii and not has_fullwidth:
        return "ascii"
    if has_fullwidth and not has_ascii:
        return "fullwidth"
    if has_ascii and has_fullwidth:
        return None
    return None


def digit_run_width(text: str) -> str | None:
    has_ascii = bool(re.search(r"[0-9]", text))
    has_fullwidth = bool(re.search(r"[０-９]", text))
    if has_ascii and not has_fullwidth:
        return "ascii"
    if has_fullwidth and not has_ascii:
        return "fullwidth"
    return None


def convert_digit_run_width(text: str, width: str) -> str:
    if width == "ascii":
        return "".join(FULLWIDTH_DIGIT_TO_ASCII.get(ch, ch) for ch in text)
    if width == "fullwidth":
        return "".join(ASCII_DIGIT_TO_FULLWIDTH.get(ch, ch) for ch in text)
    return text


def normalize_digit_width_runs(
    text: str,
    *,
    reference_text: str | None = None,
    source_group: str | None = None,
) -> str:
    reference = reference_text or ""
    reference_runs = list(DIGIT_RUN_RE.finditer(reference))
    text_runs = list(DIGIT_RUN_RE.finditer(text))
    if reference_runs and len(reference_runs) == len(text_runs):
        widths = [digit_run_width(match.group(0)) for match in reference_runs]
        if all(widths):
            pieces: list[str] = []
            cursor = 0
            for match, width in zip(text_runs, widths):
                pieces.append(text[cursor:match.start()])
                pieces.append(convert_digit_run_width(match.group(0), str(width)))
                cursor = match.end()
            pieces.append(text[cursor:])
            return "".join(pieces)
    digit_width = preferred_digit_width(reference_text, source_group)
    if digit_width:
        return convert_digit_run_width(text, digit_width)
    return text


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


def normalize_world_map_location_layout(text: str, *, reference_text: str | None = None) -> str:
    # World-map label width is computed by the runtime from the string itself.
    # Keep translator-facing text clean: no leading/trailing alignment spaces,
    # and only deliberate internal spaces as fullwidth.
    return text.replace(" ", "　").strip("　")


def normalize_item_popup_medicine_layout(text: str, *, reference_text: str | None = None) -> str:
    separator = "\x0b" if "\x0b" in text else "\n" if "\n" in text else None
    if separator is None:
        return re.sub(r"[\u3000 ]+", " ", text).strip()
    name, description = text.split(separator, 1)
    normalized_name_field = name.replace("　", " ")
    leading_name_space = re.match(r"^ *", normalized_name_field).group(0)
    normalized_name = leading_name_space + re.sub(r" +", " ", normalized_name_field).strip()
    # Keep intentional leading/trailing spaces after the inline separator so
    # the GUI can tune this awkward battle ITEM popup manually. Trailing spaces
    # can be useful as blank glyphs to clear pixels left by a previous item.
    normalized_description = description.replace("　", " ")
    padded_name = pad_term_name_field(normalized_name, reference_text=reference_text)
    return f"{padded_name}\x0b{normalized_description}"


def normalize_recovery_medicine_number_spacing(text: str, *, reference_text: str | None = None) -> str:
    # Item names are fixed-size records such as 回復薬１. A stray visible space
    # before the number makes 회복약１ exceed the original 8-byte slot.
    if not reference_text or not RECOVERY_MEDICINE_NUMBER_RE.search(reference_text):
        return text
    return re.sub(r"회복약[\u3000 ]+(?=[0-9０-９])", "회복약", text)


def normalize_certificate_progress_label_spacing(text: str, *, reference_text: str | None = None) -> str:
    if not reference_text or not CERTIFICATE_PROGRESS_LABEL_RE.fullmatch(reference_text):
        return text
    return text.replace(" ", "　")


def normalize_user_confirmed_fixed_slot_phrases(text: str, *, reference_text: str | None = None) -> str:
    if reference_text == SPEAR_ALCHEMY_ATTACK_SOURCE_TEXT:
        return text.replace("창을 연성해 공격", "창을연성해 공격").replace("창을 연성해\n공격", "창을연성해 공격")
    return text


def normalize_term_description_layout(
    text: str,
    *,
    source_group: str | None = None,
    reference_text: str | None = None,
) -> str:
    if source_group == "battle_texts" and reference_text and RECOVERY_MEDICINE_BATTLE_DESCRIPTION_RE.fullmatch(reference_text):
        return normalize_item_popup_medicine_layout(text, reference_text=reference_text)
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
        fullwidth_digit = chr(ord("０") + digit)
        replacements[str(digit)] = str(digit)
        replacements[fullwidth_digit] = fullwidth_digit
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
                "/": "／",
                "／": "／",
            }
        )
    if source_group == "credits_texts":
        # Keep the staff/company divider as the fullwidth slash used by the
        # original font instead of the narrow ASCII slash.
        replacements.update({"/": "／", "／": "／"})
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
                "%": "％",
                "％": "％",
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
            fullwidth_digit = chr(ord("０") + digit)
            replacements[str(digit)] = fullwidth_digit
            replacements[fullwidth_digit] = fullwidth_digit

    digit_width = preferred_digit_width(reference_text, source_group)
    if digit_width == "ascii":
        for digit in range(10):
            fullwidth_digit = chr(ord("０") + digit)
            replacements[str(digit)] = str(digit)
            replacements[fullwidth_digit] = str(digit)
    elif digit_width == "fullwidth":
        for digit in range(10):
            fullwidth_digit = chr(ord("０") + digit)
            replacements[str(digit)] = fullwidth_digit
            replacements[fullwidth_digit] = fullwidth_digit

    slash_width = preferred_slash_width(reference_text)
    if slash_width == "ascii":
        replacements["/"] = "/"
        replacements["／"] = "/"
    elif slash_width == "fullwidth":
        replacements["/"] = "／"
        replacements["／"] = "／"

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
    normalized = normalize_digit_width_runs(
        normalized,
        reference_text=reference_text,
        source_group=source_group,
    )
    normalized = normalize_recovery_medicine_number_spacing(
        normalized,
        reference_text=reference_text,
    )
    normalized = normalize_certificate_progress_label_spacing(
        normalized,
        reference_text=reference_text,
    )
    normalized = normalize_user_confirmed_fixed_slot_phrases(
        normalized,
        reference_text=reference_text,
    )
    if source_group in ENTRY8_FIXED_WIDTH_SOURCE_GROUPS:
        normalized = COMMA_FOLLOWING_SPACE_RE.sub(r"\1", normalized)
    if source_group in TERM_DESCRIPTION_SOURCE_GROUPS:
        normalized = normalize_term_description_layout(
            normalized,
            source_group=source_group,
            reference_text=reference_text,
        )
    if source_group in WORLD_MAP_LOCATION_SOURCE_GROUPS:
        normalized = normalize_world_map_location_layout(normalized, reference_text=reference_text)
    return normalized
