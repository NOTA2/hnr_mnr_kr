#!/usr/bin/env python3
"""Extract the battle HUD 8x8 name table.

The battle HUD mini-font renderer consumes a compact one-byte stream that is
close to CP932 halfwidth katakana. The enemy/actor table is resource `0x0933`
in the main pointer-length table and contains 0x1A-byte records followed by
null-terminated HUD-name strings.
"""

from __future__ import annotations

import json
import struct
import unicodedata
from copy import deepcopy
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ROM = ROOT / "Hagane no Renkinjutsushi - Meisou no Rondo (Japan).gba"
OUT_JSON = ROOT / "confirmed_data" / "font_assets" / "battle_hud_name_table.json"
OUT_MD = ROOT / "confirmed_data" / "font_assets" / "battle_hud_name_table.md"
OUT_TRANSLATIONS = ROOT / "confirmed_data" / "font_assets" / "battle_hud_name_translations.json"

RESOURCE_TABLE = 0x0017785C
RESOURCE_INDEX = 0x0933
RECORD_SIZE = 0x1A

DEFAULT_TRANSLATION_DRAFTS: dict[str, dict[str, object]] = {
    "ヌル": {
        "korean": "널",
        "basis": "placeholder",
        "needs_review": False,
        "note": "Placeholder/null-style entry; likely not meant to be visible.",
    },
    "エド": {"korean": "에드", "basis": "common_glossary"},
    "アル": {"korean": "알", "basis": "common_glossary"},
    "マスタング": {"korean": "머스탱", "basis": "common_glossary"},
    "ホークアイ": {"korean": "호크아이", "basis": "common_glossary"},
    "アームストロング": {"korean": "암스트롱", "basis": "common_glossary"},
    "マーティンス": {"korean": "마틴스", "basis": "common_glossary"},
    "コニィ": {"korean": "코니", "basis": "common_glossary"},
    "コーネロ": {"korean": "코넬로", "basis": "common_glossary"},
    "バルド": {"korean": "발드", "basis": "common_glossary"},
    "ランディ": {"korean": "랜디", "basis": "common_glossary"},
    "ケイト": {"korean": "케이트", "basis": "common_glossary"},
    "ブリストル": {"korean": "브리스톨", "basis": "common_glossary"},
    "リンカー": {"korean": "링커", "basis": "common_glossary"},
    "ラストリンカー": {"korean": "라스트 링커", "basis": "common_glossary"},
    "アザーズ": {"korean": "아더즈", "basis": "localized_transliteration"},
    "ティアーズ": {"korean": "티어즈", "basis": "localized_transliteration"},
    "キョウト": {
        "korean": "쿄우토",
        "basis": "localized_transliteration",
        "needs_review": False,
        "note": "Phonetic draft from the confirmed HUD source ｷｮｳﾄ.",
    },
    "トウゾク": {"korean": "도적", "basis": "semantic_enemy_type"},
    "ゴウトウ": {"korean": "강도", "basis": "semantic_enemy_type"},
    "ボマー": {"korean": "봄버", "basis": "localized_transliteration"},
    "サンゾク": {"korean": "산적", "basis": "semantic_enemy_type"},
    "マッチョ1": {"korean": "마초1", "basis": "localized_transliteration"},
    "マッチョ2": {"korean": "마초2", "basis": "localized_transliteration"},
    "マッチョ3": {"korean": "마초3", "basis": "localized_transliteration"},
    "マッチョ4": {"korean": "마초4", "basis": "localized_transliteration"},
    "メインビースト": {"korean": "메인비스트", "basis": "confirmed_runtime_target"},
    "ワイルドファング": {"korean": "와일드팽", "basis": "localized_transliteration"},
    "ダークブリング": {"korean": "다크브링", "basis": "localized_transliteration"},
    "シシオウ": {"korean": "사자왕", "basis": "semantic_enemy_name"},
    "エルフラッター": {"korean": "엘플러터", "basis": "localized_transliteration"},
    "バーンフラッター": {"korean": "번플러터", "basis": "localized_transliteration"},
    "グリフォン": {"korean": "그리폰", "basis": "localized_transliteration"},
    "デスフラッター": {"korean": "데스플러터", "basis": "localized_transliteration"},
    "ホーンバイソン": {"korean": "혼바이슨", "basis": "localized_transliteration"},
    "クリムゾンテラー": {"korean": "크림슨테러", "basis": "localized_transliteration"},
    "アンデットホーン": {"korean": "언데드혼", "basis": "localized_transliteration"},
    "ブレイドバイソン": {"korean": "블레이드바이슨", "basis": "localized_transliteration"},
    "サイキョウト": {
        "korean": "사이쿄우토",
        "basis": "localized_transliteration",
        "needs_review": False,
        "note": "Phonetic draft from the confirmed HUD source ｻｲｷｮｳﾄ.",
    },
    "キメラ5": {"korean": "키메라5", "basis": "common_glossary"},
    "アーマーゲーター": {"korean": "아머게이터", "basis": "localized_transliteration"},
    "スパイクカイマン": {"korean": "스파이크카이만", "basis": "localized_transliteration"},
    "ヴェノムスピン": {"korean": "베놈스핀", "basis": "localized_transliteration"},
    "デモンズカイマン": {"korean": "데몬즈카이만", "basis": "localized_transliteration"},
    "ウルフスナッフ": {"korean": "울프스너프", "basis": "localized_transliteration"},
    "ナックルウルフ": {"korean": "너클울프", "basis": "localized_transliteration"},
    "フェンリルニー": {"korean": "펜리르니", "basis": "localized_transliteration"},
    "ウルヴァリン": {"korean": "울버린", "basis": "localized_transliteration"},
    "キメラ7": {"korean": "키메라7", "basis": "common_glossary"},
    "ドリルホース": {"korean": "드릴호스", "basis": "localized_transliteration"},
    "ユニコーンヘッド": {"korean": "유니콘헤드", "basis": "localized_transliteration"},
    "スピードスター": {"korean": "스피드스타", "basis": "localized_transliteration"},
    "スレイプニール": {"korean": "슬레이프니르", "basis": "localized_transliteration"},
    "ライノスロス": {"korean": "라이노슬로스", "basis": "common_glossary"},
    "グランディス": {"korean": "그랜디스", "basis": "localized_transliteration"},
    "ディルヴァス": {
        "korean": "딜바스",
        "basis": "localized_transliteration",
        "needs_review": True,
        "note": "Game/original monster name not found in the shared glossary.",
    },
    "エクスクライム": {
        "korean": "엑스크라임",
        "basis": "localized_transliteration",
        "needs_review": True,
        "note": "Game/original monster name not found in the shared glossary.",
    },
    "スネークバインド": {"korean": "스네이크바인드", "basis": "localized_transliteration"},
    "ヒドラ": {"korean": "히드라", "basis": "common_glossary"},
    "ゴーゴンリップ": {"korean": "고르곤립", "basis": "localized_transliteration"},
    "ダークネスヘブン": {"korean": "다크니스헤븐", "basis": "localized_transliteration"},
    "スカー": {"korean": "스카", "basis": "common_glossary"},
    "ラスト": {"korean": "러스트", "basis": "common_glossary"},
    "グラトニー": {"korean": "글러트니", "basis": "common_glossary"},
}


def read_resource_entry(rom: bytes, index: int) -> tuple[int, int]:
    table_offset = RESOURCE_TABLE + index * 8
    rom_address, length = struct.unpack_from("<II", rom, table_offset)
    return rom_address - 0x08000000, length


def decode_hud_name(raw: bytes) -> str:
    # Byte 0xA5 is not CP932 middle-dot in this HUD font. It is the custom
    # single-byte glyph used for "ヴ", as seen in names such as ヴェノムスピン.
    pieces: list[str] = []
    for byte in raw:
        if byte == 0xA5:
            pieces.append("ヴ")
            continue
        try:
            pieces.append(bytes([byte]).decode("cp932"))
        except UnicodeDecodeError:
            pieces.append(f"<{byte:02X}>")
    return unicodedata.normalize("NFKC", "".join(pieces))


def read_c_string(data: bytes, start: int) -> bytes:
    end = start
    while end < len(data) and data[end] != 0:
        end += 1
    return data[start:end]


def load_translation_drafts() -> dict[str, dict[str, object]]:
    drafts = deepcopy(DEFAULT_TRANSLATION_DRAFTS)
    if not OUT_TRANSLATIONS.exists():
        return drafts
    payload = json.loads(OUT_TRANSLATIONS.read_text(encoding="utf-8"))
    items = payload.get("items", [])
    if isinstance(items, dict):
        iterable = items.values()
    else:
        iterable = items
    for item in iterable:
        if not isinstance(item, dict):
            continue
        name = str(item.get("decoded_name") or item.get("source") or "")
        if not name:
            continue
        current = dict(drafts.get(name, {}))
        if "korean_translation" in item:
            current["korean"] = item.get("korean_translation", "")
        elif "korean" in item:
            current["korean"] = item.get("korean", "")
        if "translation_basis" in item:
            current["basis"] = item.get("translation_basis", "")
        elif "basis" in item:
            current["basis"] = item.get("basis", "")
        if "translation_needs_review" in item:
            current["needs_review"] = bool(item.get("translation_needs_review"))
        elif "needs_review" in item:
            current["needs_review"] = bool(item.get("needs_review"))
        if "translation_note" in item:
            current["note"] = item.get("translation_note", "")
        elif "note" in item:
            current["note"] = item.get("note", "")
        if "progress_status" in item:
            current["progress_status"] = item.get("progress_status", "")
        if "review_status" in item:
            current["review_status"] = item.get("review_status", "")
        drafts[name] = current
    return drafts


def translation_entry(name: str, drafts: dict[str, dict[str, object]]) -> dict[str, object]:
    draft = drafts.get(
        name,
        {
            "korean": "",
            "basis": "missing",
            "needs_review": True,
            "note": "No translation draft has been assigned.",
        },
    )
    korean = str(draft.get("korean", ""))
    return {
        "korean_translation": korean,
        "korean_char_count": len(korean),
        "translation_basis": draft.get("basis", "missing"),
        "translation_needs_review": bool(draft.get("needs_review", False)),
        "translation_note": draft.get("note", ""),
        "progress_status": draft.get("progress_status", "done" if korean else "todo"),
        "review_status": draft.get(
            "review_status",
            "issue" if draft.get("needs_review", False) else ("checked" if korean else "unreviewed"),
        ),
    }


def extract() -> dict:
    rom = ROM.read_bytes()
    translation_drafts = load_translation_drafts()
    resource_offset, resource_length = read_resource_entry(rom, RESOURCE_INDEX)
    resource = rom[resource_offset : resource_offset + resource_length]

    records = []
    index = 0
    while index * RECORD_SIZE + RECORD_SIZE <= len(resource):
        record_offset = index * RECORD_SIZE
        if resource[record_offset] != index:
            break
        record = resource[record_offset : record_offset + RECORD_SIZE]
        name_rel = struct.unpack_from("<H", record, 1)[0]
        raw_name = read_c_string(resource, name_rel)
        decoded_name = decode_hud_name(raw_name)
        records.append(
            {
                "record_index": index,
                "record_offset": resource_offset + record_offset,
                "record_offset_hex": f"0x{resource_offset + record_offset:08X}",
                "name_offset": resource_offset + name_rel,
                "name_offset_hex": f"0x{resource_offset + name_rel:08X}",
                "name_rel": name_rel,
                "name_rel_hex": f"0x{name_rel:04X}",
                "raw_bytes_hex": raw_name.hex(),
                "hud_source_text": raw_name.decode("cp932", errors="replace"),
                "decoded_name": decoded_name,
                **translation_entry(decoded_name, translation_drafts),
            }
        )
        index += 1

    unique: list[dict] = []
    seen: dict[str, dict] = {}
    for record in records:
        name = record["decoded_name"]
        if name not in seen:
            seen[name] = {
                "decoded_name": name,
                "first_record_index": record["record_index"],
                "first_name_offset_hex": record["name_offset_hex"],
                "count": 0,
                "record_indexes": [],
                **translation_entry(name, translation_drafts),
            }
            unique.append(seen[name])
        seen[name]["count"] += 1
        seen[name]["record_indexes"].append(record["record_index"])

    return {
        "source_rom": str(ROM.relative_to(ROOT)),
        "resource_table": f"0x{RESOURCE_TABLE:08X}",
        "resource_index": f"0x{RESOURCE_INDEX:04X}",
        "resource_offset": f"0x{resource_offset:08X}",
        "resource_length": f"0x{resource_length:04X}",
        "record_size": f"0x{RECORD_SIZE:02X}",
        "translation_overrides": str(OUT_TRANSLATIONS.relative_to(ROOT)),
        "record_count": len(records),
        "unique_name_count": len(unique),
        "translation_draft_count": sum(
            1 for item in unique if item["korean_translation"]
        ),
        "translation_needs_review_count": sum(
            1 for item in unique if item["translation_needs_review"]
        ),
        "records": records,
        "unique_names": unique,
        "notes": [
            "Names are null-terminated HUD mini-font byte strings, not fullwidth CP932 text.",
            "The visible current_review_ss2 enemy name is メインビースト, encoded as d2 b2 dd cb de b0 bd c4.",
            "The renderer maps bytes roughly as glyph_index = byte - 0xA2, with 0xDE/0xDF dakuten marks modifying the previous glyph.",
            "Korean translations are drafts aligned with docs/translation_team/fma_translation_team_common_final_v4_1.md where available.",
        ],
    }


def write_markdown(report: dict) -> None:
    lines = [
        "# Battle HUD Name Table",
        "",
        f"- resource table: `{report['resource_table']}`",
        f"- resource index: `{report['resource_index']}`",
        f"- resource offset: `{report['resource_offset']}`",
        f"- records: `{report['record_count']}`",
        f"- unique names: `{report['unique_name_count']}`",
        f"- translated names: `{report['translation_draft_count']}`",
        f"- needs review: `{report['translation_needs_review_count']}`",
        "",
        "## Unique Names",
        "",
        "| first record | count | decoded name | Korean draft | basis | review | first offset |",
        "| ---: | ---: | --- | --- | --- | --- | --- |",
    ]
    for item in report["unique_names"]:
        review = "yes" if item["translation_needs_review"] else ""
        lines.append(
            f"| {item['first_record_index']} | {item['count']} | {item['decoded_name']} | {item['korean_translation']} | {item['translation_basis']} | {review} | `{item['first_name_offset_hex']}` |"
        )
    review_notes = [
        item
        for item in report["unique_names"]
        if item["translation_needs_review"] and item["translation_note"]
    ]
    if review_notes:
        lines.extend(["", "## Review Notes", ""])
        for item in review_notes:
            lines.append(
                f"- `{item['decoded_name']}` -> `{item['korean_translation']}`: {item['translation_note']}"
            )
    lines.extend(
        [
            "",
            "## Records",
            "",
            "| record | decoded name | Korean draft | raw HUD bytes | name offset |",
            "| ---: | --- | --- | --- | --- |",
        ]
    )
    for item in report["records"]:
        lines.append(
            f"| {item['record_index']} | {item['decoded_name']} | {item['korean_translation']} | `{item['raw_bytes_hex']}` | `{item['name_offset_hex']}` |"
        )
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    report = extract()
    OUT_JSON.parent.mkdir(parents=True, exist_ok=True)
    OUT_JSON.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    write_markdown(report)
    print(f"records: {report['record_count']}")
    print(f"unique : {report['unique_name_count']}")
    print(f"json   : {OUT_JSON}")
    print(f"md     : {OUT_MD}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
