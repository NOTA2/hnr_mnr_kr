#!/usr/bin/env python3

from __future__ import annotations

import json
import re
import sys
from collections import defaultdict
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
if str(ROOT / "scripts") not in sys.path:
    sys.path.insert(0, str(ROOT / "scripts"))
if str(ROOT / ".vendor") not in sys.path:
    sys.path.append(str(ROOT / ".vendor"))

from gba_kor_tool.cli import decompress_lz77
from gba_kor_tool.translation_normalization import PROFILE_PATH, build_default_profile, normalize_translation_text
from extract_rle_image_tiles import decompress_gba_rle
from registry_b_zp import decompress_zp_resource, gba_pointer_to_file_offset
DATA_ROOT = ROOT / "confirmed_data"
WORKSPACE_ROOT = DATA_ROOT / "localization_workbench"
TRANSLATION_WORKSETS = DATA_ROOT / "translation_worksets"
TRANSLATION_WORKSPACE = DATA_ROOT / "translation_workspace"
DIALOGUE_METADATA = DATA_ROOT / "dialogue_metadata"
IMAGE_INVENTORY = DATA_ROOT / "image_inventory"
EXTRACTED_TEXTS = DATA_ROOT / "extracted_texts"
FONT_PROFILE = DATA_ROOT / "font_assets" / "active_hangul_font_profile.json"
SOURCE_ROM = ROOT / "Hagane no Renkinjutsushi - Meisou no Rondo (Japan).gba"

OUT_DATASET = WORKSPACE_ROOT / "workbench_dataset.json"
OUT_SPEAKERS = WORKSPACE_ROOT / "speaker_aliases.json"
OUT_SPEAKER_REGISTRY = WORKSPACE_ROOT / "speaker_registry.json"
OUT_PROGRESS = WORKSPACE_ROOT / "progress_state.json"
OUT_IMAGE = WORKSPACE_ROOT / "image_replacements.json"
OUT_README = WORKSPACE_ROOT / "README.md"
UPLOADED_IMAGE_REPLACEMENTS = WORKSPACE_ROOT / "uploaded_image_replacements"

REGISTRY_B_ZP_CATEGORY_ID = "registry_b_zp01_resources"
PAGE_TURN_RLE_TILE_CATEGORY_IDS = {f"page_turn_rle_{order:02d}_tiles" for order in range(5, 13)}
HIDDEN_IMAGE_GROUP_IDS = {"card_book_ui", "reference_candidates", "other"}
HIDDEN_IMAGE_CATEGORY_IDS = {"page_turn_rle_12_tiles"}
IMAGE_GROUP_CATEGORY_PREFIX = "image_group_"
SPECIAL_IMAGE_GROUP_CATEGORY_IDS = {
    "common_hud_tiles",
    "alchemy_tiles",
    REGISTRY_B_ZP_CATEGORY_ID,
    *PAGE_TURN_RLE_TILE_CATEGORY_IDS,
}
IMAGE_CATEGORY_IDS = {
    "image_review_units",
    "common_hud_tiles",
    "alchemy_tiles",
    REGISTRY_B_ZP_CATEGORY_ID,
    *PAGE_TURN_RLE_TILE_CATEGORY_IDS,
}


def is_image_item(item: dict) -> bool:
    return item.get("category_id") in IMAGE_CATEGORY_IDS

PORTRAIT_VARIANT_TOKEN_RE = re.compile(r"^(?P<prefix>[^:]+):(?P<person>\d+)(?P<variant>[A-Z])$")

DEFAULT_SPEAKER_REGISTRY = [
    {
        "speaker_id": "edward_elric",
        "speaker_name": "에드워드 엘릭",
        "speaker_role": "주인공 / 국가 연금술사",
        "notes": "애칭: 에드. 기본 반말, 짧고 직설적이며 자신감 있는 말투.",
    },
    {
        "speaker_id": "alphonse_elric",
        "speaker_name": "알폰스 엘릭",
        "speaker_role": "주인공 / 에드워드의 동생",
        "notes": "애칭: 알. 형에게는 '형'이라고 부르며, 부드럽고 차분한 말투.",
    },
    {
        "speaker_id": "roy_mustang",
        "speaker_name": "로이 머스탱",
        "speaker_role": "군부 / 대령",
        "notes": "대사에서는 '머스탱 대령' 가능. 군인답게 단정하고 냉정한 말투.",
    },
    {
        "speaker_id": "riza_hawkeye",
        "speaker_name": "리자 호크아이",
        "speaker_role": "군부 / 중위",
        "notes": "대사에서는 '호크아이 중위' 가능. 절제되고 정중한 군인 말투.",
    },
    {
        "speaker_id": "alex_louis_armstrong",
        "speaker_name": "알렉스 루이 암스트롱",
        "speaker_role": "군부 / 소령",
        "notes": "대사에서는 '암스트롱 소령' 가능. 장중하고 과장된 말투.",
    },
    {
        "speaker_id": "king_bradley",
        "speaker_name": "킹 브래드레이",
        "speaker_role": "아메스트리스 / 대총통",
        "notes": "대사에서는 '브래드레이 대총통' 가능. '브래들리' 표기 금지.",
    },
    {
        "speaker_id": "winry_rockbell",
        "speaker_name": "윈리 록벨",
        "speaker_role": "오토메일 정비사",
        "notes": "원작 캐릭터 표기 기준.",
    },
    {
        "speaker_id": "rose_thomas",
        "speaker_name": "로제 토마스",
        "speaker_role": "리올 관련 인물",
        "notes": "원작 캐릭터 표기 기준.",
    },
    {
        "speaker_id": "cornello",
        "speaker_name": "코넬로",
        "speaker_role": "리올 / 교주",
        "notes": "리올 종교 문맥의 인물.",
    },
    {
        "speaker_id": "scar",
        "speaker_name": "스카",
        "speaker_role": "이슈발 관련 인물",
        "notes": "원작 캐릭터 표기 기준.",
    },
    {
        "speaker_id": "lust",
        "speaker_name": "러스트",
        "speaker_role": "호문쿨루스",
        "notes": "원작 캐릭터 표기 기준.",
    },
    {
        "speaker_id": "gluttony",
        "speaker_name": "글러트니",
        "speaker_role": "호문쿨루스",
        "notes": "원작 캐릭터 표기 기준.",
    },
    {
        "speaker_id": "jean_havoc",
        "speaker_name": "쟝 하보크",
        "speaker_role": "군부",
        "notes": "원작 캐릭터 표기 기준. 성만 나올 때는 '하보크'.",
    },
    {
        "speaker_id": "sheska",
        "speaker_name": "셰스카",
        "speaker_role": "원작 캐릭터",
        "notes": "원작 캐릭터 표기 기준.",
    },
    {
        "speaker_id": "elysia",
        "speaker_name": "엘리시아",
        "speaker_role": "원작 캐릭터",
        "notes": "원작 캐릭터 표기 기준.",
    },
    {
        "speaker_id": "black_hayate",
        "speaker_name": "블랙 하야테 호",
        "speaker_role": "원작 캐릭터 / 군견",
        "notes": "화자 후보로 쓰일 가능성은 낮지만, 배경지식의 원작 캐릭터 표에 포함된 항목.",
    },
    {
        "speaker_id": "corniche_lois",
        "speaker_name": "코니슈 로이스",
        "speaker_role": "게임 오리지널 / 히로인",
        "notes": "원문 후보: コーニッシュ・ロイス / コニシュ・ロイス. 애칭: 코니. 초반에는 밝고 상냥한 말투.",
    },
    {
        "speaker_id": "seraphy_lois",
        "speaker_name": "세라피 로이스",
        "speaker_role": "게임 오리지널 / 코니슈의 오빠",
        "notes": "로이스 대령은 세라피 로이스를 가리키는 군 계급 호칭.",
    },
    {
        "speaker_id": "linker",
        "speaker_name": "링커",
        "speaker_role": "게임 오리지널 / 최종보스 호칭",
        "notes": "차갑고 압박감 있는 말투. 설명을 과하게 늘리지 않는다.",
    },
    {
        "speaker_id": "last_linker",
        "speaker_name": "라스트 링커",
        "speaker_role": "게임 오리지널 / 최종 형태",
        "notes": "링커의 최종 형태 호칭. 장면에 따라 링커/세라피와 구분해 선택.",
    },
    {
        "speaker_id": "aston_martins",
        "speaker_name": "아스턴 마틴스",
        "speaker_role": "게임 오리지널 / 중령",
        "notes": "대사에서는 '마틴스 중령' 우선. 반항적이고 거친 면이 있지만 동료애가 강한 군인.",
    },
    {
        "speaker_id": "kate_lam",
        "speaker_name": "케이트 람",
        "speaker_role": "게임 오리지널",
        "notes": "천진난만하지만 고집 세고 자존심 강한 말투.",
    },
    {
        "speaker_id": "randy_rover",
        "speaker_name": "랜디 로버",
        "speaker_role": "게임 오리지널",
        "notes": "투박하고 단순한 말투. 과도한 비속어와 현대 밈은 금지.",
    },
    {
        "speaker_id": "dart_daimler",
        "speaker_name": "다트 다이무라",
        "speaker_role": "게임 오리지널",
        "notes": "PDF 기준 표기. '다임러' 금지.",
    },
    {
        "speaker_id": "bald",
        "speaker_name": "발드",
        "speaker_role": "게임 오리지널 / 적의 단 두목",
        "notes": "적의 단 관련 인물.",
    },
    {
        "speaker_id": "black_ed",
        "speaker_name": "흑색의 에드",
        "speaker_role": "게임 오리지널 / 에필로그 문맥",
        "notes": "원문 후보: 黒色のエド / 黒いエド 계열.",
    },
]


def load_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def load_json_if_exists(path: Path, fallback):
    if path.exists():
        return load_json(path)
    return fallback


def existing_relative_path(path: str) -> str:
    return path if path and (ROOT / path).is_file() else ""


def native_image_source_path(path: str) -> str:
    if not path:
        return ""
    path_obj = Path(path)
    name = path_obj.name
    candidates: list[str] = []
    if name == "matched_tiles_screen_order_4x.png":
        candidates.append(str(path_obj.with_name("matched_tiles_screen_order.png")))
    if name.endswith("__advanced_edit_4x.png"):
        candidates.append(str(path_obj.with_name(name.replace("__advanced_edit_4x.png", "__source.png"))))
    if name.endswith("__edit_4x.png"):
        candidates.append(str(path_obj.with_name(name.replace("__edit_4x.png", "__source.png"))))
    if name.endswith("_4x.png"):
        candidates.append(str(path_obj.with_name(name.replace("_4x.png", ".png"))))
        candidates.append(path.replace("_4x.png", ".png.1x.png"))
    for candidate in candidates:
        if candidate != path and existing_relative_path(candidate):
            return candidate
    return path


def build_image_native_source_path_map() -> dict[str, str]:
    source_by_item: dict[str, str] = {}

    def record(item_id: str | None, source_path: str | None) -> None:
        if not item_id or not source_path:
            return
        native_path = native_image_source_path(source_path)
        if existing_relative_path(native_path):
            source_by_item[item_id] = native_path

    for manifest_path in (
        IMAGE_INVENTORY / "edit_packs" / "field_menu_labels" / "manifest.json",
        IMAGE_INVENTORY / "edit_packs" / "title_screen" / "manifest.json",
    ):
        payload = load_json_if_exists(manifest_path, [])
        if isinstance(payload, list):
            for entry in payload:
                record(entry.get("item_id"), entry.get("source_path"))

    battle_manifest = load_json_if_exists(
        IMAGE_INVENTORY / "edit_packs" / "battle_command_buttons" / "manifest.json",
        {},
    )
    for entry in battle_manifest.get("items", []):
        record(entry.get("item_id"), entry.get("source_path"))

    card_tabs_manifest = load_json_if_exists(
        IMAGE_INVENTORY / "edit_packs" / "card_book_right_tabs" / "manifest.json",
        {},
    )
    record(card_tabs_manifest.get("item_id"), card_tabs_manifest.get("source_path"))
    for entry in card_tabs_manifest.get("individual_tabs", []):
        record(entry.get("item_id"), entry.get("source_path"))

    card_list_labels_manifest = load_json_if_exists(
        IMAGE_INVENTORY / "edit_packs" / "card_list_labels" / "manifest.json",
        {},
    )
    record(card_list_labels_manifest.get("item_id"), card_list_labels_manifest.get("source_path"))
    card_list_power_manifest = load_json_if_exists(
        IMAGE_INVENTORY / "edit_packs" / "card_list_power_labels" / "manifest.json",
        {},
    )
    for entry in card_list_power_manifest.get("items", []):
        record(entry.get("item_id"), entry.get("source_path"))

    card_page_manifest = load_json_if_exists(
        IMAGE_INVENTORY / "edit_packs" / "card_page_count" / "manifest.json",
        {},
    )
    record(card_page_manifest.get("item_id"), card_page_manifest.get("source_path"))

    common_hud_manifest = load_json_if_exists(
        IMAGE_INVENTORY / "edit_packs" / "common_hud_tiles_00534874" / "manifest.json",
        {},
    )
    for tile in common_hud_manifest.get("tiles", []):
        try:
            tile_index = int(tile["tile_index"])
        except (KeyError, TypeError, ValueError):
            continue
        record(f"image:lz77_tile:00534874:tile_{tile_index:03X}", tile.get("source_1x"))

    alchemy_manifest = load_json_if_exists(
        IMAGE_INVENTORY / "edit_packs" / "alchemy_tiles_003A206C" / "manifest.json",
        {},
    )
    for tile in alchemy_manifest.get("tiles", []):
        try:
            tile_index = int(tile["tile_index"])
        except (KeyError, TypeError, ValueError):
            continue
        record(f"image:rle_tile:003A206C:tile_{tile_index:03X}", tile.get("source_1x"))

    registry_b_manifest = load_json_if_exists(
        IMAGE_INVENTORY / "edit_packs" / "registry_b_zp01_resources" / "manifest.json",
        {},
    )
    for resource in registry_b_manifest.get("resources", []):
        try:
            offset = int(resource["file_offset"])
            entry = int(resource["entry"])
        except (KeyError, TypeError, ValueError):
            continue
        record(f"image:registry_b_zp01:{offset:08X}:entry_{entry:02X}", resource.get("source_1x"))

    return source_by_item


def normalize_image_source_paths(items: list[dict]) -> None:
    source_by_item = build_image_native_source_path_map()
    for item in items:
        if not is_image_item(item):
            continue
        preferred_source = source_by_item.get(item.get("item_id"))
        if not preferred_source:
            preferred_source = native_image_source_path(item.get("source_download_path", ""))
        if not preferred_source or not existing_relative_path(preferred_source):
            preferred_source = native_image_source_path(item.get("source_preview_path", ""))
        if not preferred_source or not existing_relative_path(preferred_source):
            continue
        item["source_preview_path"] = preferred_source
        item["source_download_path"] = preferred_source


def build_translation_normalization_profile() -> None:
    texts: list[str] = []
    for path in sorted(EXTRACTED_TEXTS.glob("*.json")):
        payload = load_json(path)
        if not isinstance(payload, list):
            continue
        for record in payload:
            if isinstance(record, dict):
                text = record.get("text")
                if isinstance(text, str) and text:
                    texts.append(text)
    profile = build_default_profile(texts)
    PROFILE_PATH.write_text(json.dumps(profile, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def build_dialogue_token_map() -> dict[str, dict[int, str]]:
    result: dict[str, dict[int, str]] = {}
    for source_group, filename in (
        ("registry_a_entry8_prefixed_texts", "entry8_dialogue_state_index.json"),
        ("registry_d_fc_script_texts", "registry_d_dialogue_state_index.json"),
    ):
        payload = load_json(DIALOGUE_METADATA / filename)
        result[source_group] = {
            int(record["offset"]): record["dialogue_state_token"]
            for record in payload.get("records", [])
            if record.get("dialogue_state_token")
        }
    return result


def build_entry8_cluster_map() -> dict[int, str]:
    result: dict[int, str] = {}
    cluster_dir = TRANSLATION_WORKSPACE / "registry_a_entry8_clusters"
    for path in sorted(cluster_dir.glob("cluster_*.json")):
        cluster_id = path.stem
        records = load_json(path)
        for record in records:
            result[int(record["offset"])] = cluster_id
    return result


def build_image_group_categories() -> list[dict]:
    category_ids = [
        "field_menu_labels",
        "battle_command_buttons",
        "battle_popups_panels",
        "title_screen",
    ]
    categories: list[dict] = []
    for index, group_id in enumerate(category_ids):
        group_label, _ = IMAGE_GROUPS[group_id]
        categories.append(
            {
                "id": image_group_category_id(group_id),
                "label": group_label,
                "type": "image",
                "sort_order": 7 + index,
                "path": "confirmed_data/image_inventory/image_text_inventory.json",
                "description": IMAGE_GROUP_DESCRIPTIONS.get(group_id, group_label),
                "build_enabled": False,
            }
        )
    return categories


def build_categories() -> list[dict]:
    return [
        {
            "id": "translation_workset_opening_intro",
            "label": "오프닝/인트로",
            "type": "text",
            "sort_order": 0,
            "path": "confirmed_data/translation_worksets/translation_workset_opening_intro.json",
            "description": "게임 시작 직후 고정 카드와 오프닝 인트로 텍스트",
            "build_enabled": True,
        },
        {
            "id": "translation_workset_core_ui",
            "label": "코어 UI",
            "type": "text",
            "sort_order": 1,
            "path": "confirmed_data/translation_worksets/translation_workset_core_ui.json",
            "description": "시스템/세이브/지역명/UI 기술명",
            "build_enabled": True,
        },
        {
            "id": "translation_workset_gameplay_terms",
            "label": "게임 용어",
            "type": "text",
            "sort_order": 2,
            "path": "confirmed_data/translation_worksets/translation_workset_gameplay_terms.json",
            "description": "아이템/전투/능력/재료/설명",
            "build_enabled": True,
        },
        {
            "id": "translation_workset_credits",
            "label": "크레딧",
            "type": "text",
            "sort_order": 3,
            "path": "confirmed_data/translation_worksets/translation_workset_credits.json",
            "description": "엔딩 크레딧/스태프 표기",
            "build_enabled": True,
        },
        {
            "id": "translation_workset_registry_d_dialogue",
            "label": "대사 Registry D",
            "type": "dialogue",
            "sort_order": 4,
            "path": "confirmed_data/translation_worksets/translation_workset_registry_d_dialogue.json",
            "description": "튜토리얼/이벤트/전투 전후 대사",
            "build_enabled": True,
        },
        {
            "id": "registry_a_entry8_clusters_manifest",
            "label": "대사 Entry8",
            "type": "dialogue",
            "sort_order": 5,
            "path": "confirmed_data/translation_workspace/registry_a_entry8_clusters_manifest.json",
            "description": "대형 스토리/이벤트 뱅크 cluster 단위",
            "build_enabled": True,
        },
        {
            "id": "translation_workset_inline_event_texts",
            "label": "이벤트 연출 텍스트",
            "type": "dialogue",
            "sort_order": 6,
            "path": "confirmed_data/translation_worksets/translation_workset_inline_event_texts.json",
            "description": "이벤트 스크립트 내부에 직접 박힌 짧은 연출/선택지 텍스트",
            "build_enabled": True,
        },
        *build_image_group_categories(),
        {
            "id": "common_hud_tiles",
            "label": "공유 HUD 타일셋",
            "type": "image",
            "sort_order": 20,
            "path": "confirmed_data/image_inventory/edit_packs/common_hud_tiles_00534874/manifest.json",
            "description": "0x00534874 공유 HUD LZ77 블록을 8x8 타일 단위로 검토/교체",
            "build_enabled": False,
        },
        {
            "id": "alchemy_tiles",
            "label": "연금술 타일셋",
            "type": "image",
            "sort_order": 21,
            "path": "confirmed_data/image_inventory/edit_packs/alchemy_tiles_003A206C/manifest.json",
            "description": "0x003A206C 연금술/카드 UI RLE 블록을 8x8 타일 단위로 검토/교체",
            "build_enabled": False,
        },
        {
            "id": REGISTRY_B_ZP_CATEGORY_ID,
            "label": "Registry B ZP01",
            "type": "image",
            "sort_order": 22,
            "path": "confirmed_data/image_inventory/edit_packs/registry_b_zp01_resources/manifest.json",
            "description": "Registry B ZP01 압축 리소스를 디코드해 4bpp 타일 시트로 검토/교체",
            "build_enabled": False,
        },
        *build_page_turn_rle_tile_categories(),
    ]


def build_text_items(dialogue_tokens: dict[str, dict[int, str]], entry8_cluster_map: dict[int, str]) -> list[dict]:
    items: list[dict] = []
    workset_specs = [
        ("translation_workset_opening_intro.json", "translation_workset_opening_intro"),
        ("translation_workset_core_ui.json", "translation_workset_core_ui"),
        ("translation_workset_gameplay_terms.json", "translation_workset_gameplay_terms"),
        ("translation_workset_credits.json", "translation_workset_credits"),
        ("translation_workset_registry_d_dialogue.json", "translation_workset_registry_d_dialogue"),
        ("translation_workset_inline_event_texts.json", "translation_workset_inline_event_texts"),
    ]

    for filename, category_id in workset_specs:
        workset_id = filename.replace(".json", "")
        records = load_json(TRANSLATION_WORKSETS / filename)
        for order, record in enumerate(records):
            source_group = record["source_group"]
            offset = int(record["offset"])
            dialogue_state_token = dialogue_tokens.get(source_group, {}).get(offset)
            cluster_id = entry8_cluster_map.get(offset)
            item_id = f"{workset_id}:{offset:08X}"
            terminator = record.get("terminator")
            append_terminator = record.get("append_terminator")
            if source_group in {"save_menu_texts", "registry_a_entry8_prefixed_texts"}:
                terminator = None
                append_terminator = False
            translation = normalize_translation_text(
                record.get("translation", ""),
                source_group=source_group,
                reference_text=record.get("text"),
            )
            items.append(
                {
                    "item_id": item_id,
                    "category_id": category_id,
                    "origin_workset_id": workset_id,
                    "group_id": cluster_id,
                    "offset": offset,
                    "rom_address": int(record["rom_address"]),
                    "byte_length": int(record["byte_length"]),
                    "header_offset": record.get("header_offset"),
                    "header_rom_address": record.get("header_rom_address"),
                    "prefix": record.get("prefix"),
                    "char_count": record.get("char_count"),
                    "header_bytes": record.get("header_bytes"),
                    "source_group": source_group,
                    "source_file": record["source_file"],
                    "source_order": int(record.get("source_order", order)),
                    "order_in_category": order,
                    "text": record["text"],
                    "translation": translation,
                    "agent_draft": record.get("agent_draft") or translation,
                    "agent_comment": "",
                    "manual_locked": False,
                    "effective_translation": translation,
                    "translation_source": "seed" if translation else "original",
                    "notes": record.get("notes", ""),
                    "terminator": terminator,
                    "append_terminator": append_terminator,
                    "unknown_tokens": record.get("unknown_tokens"),
                    "anchor_offset": record.get("anchor_offset"),
                    "anchor_rom_address": record.get("anchor_rom_address"),
                    "anchor": record.get("anchor"),
                    "stop_byte": record.get("stop_byte"),
                    "raw_byte_length": record.get("raw_byte_length"),
                    "raw_bytes": record.get("raw_bytes"),
                    "before_bytes": record.get("before_bytes"),
                    "after_bytes": record.get("after_bytes"),
                    "dialogue_state_token": dialogue_state_token,
                    "progress_status": "todo",
                    "review_status": "unreviewed",
                    "image_overlap_risk": "low" if workset_id != "translation_workset_core_ui" else "medium",
                    "default_review_included": True,
                }
            )

    entry8_manifest = load_json(TRANSLATION_WORKSPACE / "registry_a_entry8_clusters_manifest.json")
    for cluster in entry8_manifest.get("clusters", []):
        cluster_id = Path(cluster["output_file"]).stem
        cluster_path = ROOT / cluster["output_file"]
        records = load_json(cluster_path)
        for order, record in enumerate(records):
            offset = int(record["offset"])
            item_id = f"{cluster_id}:{offset:08X}"
            terminator = record.get("terminator")
            append_terminator = record.get("append_terminator")
            if record["source_group"] in {"save_menu_texts", "registry_a_entry8_prefixed_texts"}:
                terminator = None
                append_terminator = False
            translation = normalize_translation_text(
                record.get("translation", ""),
                source_group=record["source_group"],
                reference_text=record.get("text"),
            )
            items.append(
                {
                    "item_id": item_id,
                    "category_id": "registry_a_entry8_clusters_manifest",
                    "group_id": cluster_id,
                    "offset": offset,
                    "rom_address": int(record["rom_address"]),
                    "byte_length": int(record["byte_length"]),
                    "header_offset": record.get("header_offset"),
                    "header_rom_address": record.get("header_rom_address"),
                    "prefix": record.get("prefix"),
                    "char_count": record.get("char_count"),
                    "header_bytes": record.get("header_bytes"),
                    "source_group": record["source_group"],
                    "source_file": record["source_file"],
                    "source_order": int(record.get("source_order", cluster.get("cluster_index", 0))),
                    "order_in_category": order,
                    "text": record["text"],
                    "translation": translation,
                    "agent_draft": record.get("agent_draft") or translation,
                    "agent_comment": "",
                    "manual_locked": False,
                    "effective_translation": translation,
                    "translation_source": "seed" if translation else "original",
                    "notes": record.get("notes", ""),
                    "terminator": terminator,
                    "append_terminator": append_terminator,
                    "unknown_tokens": record.get("unknown_tokens", 0),
                    "anchor_offset": record.get("anchor_offset"),
                    "anchor_rom_address": record.get("anchor_rom_address"),
                    "anchor": record.get("anchor"),
                    "stop_byte": record.get("stop_byte"),
                    "raw_byte_length": record.get("raw_byte_length"),
                    "raw_bytes": record.get("raw_bytes"),
                    "before_bytes": record.get("before_bytes"),
                    "after_bytes": record.get("after_bytes"),
                    "dialogue_state_token": dialogue_tokens.get("registry_a_entry8_prefixed_texts", {}).get(offset),
                    "progress_status": "todo",
                    "review_status": "unreviewed",
                    "cluster_primary_tag": cluster.get("primary_tag"),
                    "cluster_label": cluster_id,
                    "image_overlap_risk": "low",
                    "default_review_included": True,
                }
            )

    return items


def build_image_items() -> list[dict]:
    items: list[dict] = []
    # Keep the GUI image category strictly user-facing. Broad inventories,
    # runtime tilemap sheets, and raw RLE galleries are useful for us while
    # researching, but they create "downloaded but invisible/useless" items for
    # the user. Only expose concrete blocks or prepared edit packs here.
    items.extend(build_english_patch_image_items())
    items.extend(build_curated_runtime_image_items())
    items.extend(build_runtime_rle_screen_order_items())
    items.extend(build_card_list_label_items())
    items.extend(build_card_list_power_label_items())
    items.extend(build_card_book_right_tab_items())
    items.extend(build_runtime_rle_image_items())
    items.extend(build_expanded_nearby_gallery_items())
    items.extend(build_common_hud_tile_items())
    items.extend(build_alchemy_tile_items())
    items.extend(build_page_turn_rle_tile_items())
    items.extend(build_registry_b_zp_items())
    assign_image_item_groups(items)
    return [item for item in items if image_item_is_visible(item)]


IMAGE_GROUPS = {
    "field_menu_labels": ("필드/메뉴 라벨", 1000),
    "battle_command_buttons": ("전투 하단 버튼", 2000),
    "battle_popups_panels": ("전투 팝업/패널", 3000),
    "card_book_ui": ("카드/책자 UI", 4000),
    "title_screen": ("타이틀 화면", 5000),
    "common_hud_tiles": ("공유 HUD 타일셋", 6000),
    "alchemy_tiles": ("연금술 타일셋", 7000),
    "page_turn_rle_tiles": ("페이지 넘김 RLE 타일셋", 7500),
    "registry_b_zp01_resources": ("Registry B ZP01", 8000),
    "reference_candidates": ("참고/비대상/확장 후보", 9000),
    "other": ("기타 이미지 후보", 9500),
}

IMAGE_GROUP_DESCRIPTIONS = {
    "field_menu_labels": "필드/메뉴/카드 라벨처럼 작은 UI 글자가 구워진 이미지 블록",
    "battle_command_buttons": "전투 하단 버튼/명령 UI 이미지",
    "battle_popups_panels": "전투 중 팝업, 카드, ALCHEMY 패널 이미지",
    "card_book_ui": "카드 책자 오른쪽 탭과 카드 리스트/BACK/NEXT 계열 UI",
    "title_screen": "타이틀 로고와 시작 메뉴 이미지",
    "page_turn_rle_tiles": "카드 책자 페이지 넘김 애니메이션 RLE 후보를 8x8 타일 단위로 쪼갠 항목",
    "reference_candidates": "영문판 참고/비대상/확장 조사 후보",
    "other": "아직 분류가 확정되지 않은 이미지 후보",
}


def image_group_category_id(group_id: str) -> str:
    if group_id in SPECIAL_IMAGE_GROUP_CATEGORY_IDS:
        return group_id
    return f"{IMAGE_GROUP_CATEGORY_PREFIX}{group_id}"


IMAGE_GROUP_CATEGORY_IDS = {image_group_category_id(group_id) for group_id in IMAGE_GROUPS}
IMAGE_CATEGORY_IDS.update(IMAGE_GROUP_CATEGORY_IDS)


CARD_BOOK_RLE_OFFSETS = {
    "003A3540",
    "003A5E50",
    "003A6E24",
    "003A7C3C",
    "003A8894",
    "003A9624",
    "003AA4C0",
}


def classify_image_item_group(item: dict) -> str:
    item_id = str(item.get("item_id", ""))
    label = str(item.get("label", ""))

    if item_id.startswith("image:lz77_tile:"):
        return "common_hud_tiles"
    if item_id.startswith("image:rle_tile:003A206C:"):
        return "alchemy_tiles"
    if item.get("category_id") in PAGE_TURN_RLE_TILE_CATEGORY_IDS:
        return "page_turn_rle_tiles"
    if item_id.startswith("image:registry_b_zp01:"):
        return "registry_b_zp01_resources"
    if item_id.startswith("image:expanded_nearby:"):
        return "reference_candidates"
    if item_id.startswith("image:rle:007E") or (
        item_id.startswith("image:rle_screen_order:") and "007E0000" in item_id
    ):
        return "title_screen"
    if item_id.startswith("image:raw4bpp:"):
        return "battle_command_buttons"
    if item_id.startswith("image:rle_screen_order_focus:"):
        return "card_book_ui"
    if item_id.startswith("image:rle_screen_order:") and any(offset in item_id for offset in CARD_BOOK_RLE_OFFSETS):
        return "card_book_ui"
    if item_id.startswith("image:rle_screen_order:") and (
        "003ABB9C" in item_id or "003AF23C" in item_id or "003A206C" in item_id
    ):
        return "battle_popups_panels"
    if item_id.startswith("image:field_"):
        return "field_menu_labels"
    if item_id in {"image:battle_menu_wordmarks_003A206C", "image:english_battle_hud_small_font"}:
        return "reference_candidates"
    if item.get("replacement_target") is False or "영문" in label or "영어" in label:
        return "reference_candidates"
    return "other"


def assign_image_item_groups(items: list[dict]) -> None:
    grouped: dict[str, list[dict]] = defaultdict(list)
    original_order: dict[str, int] = {}
    for index, item in enumerate(items):
        group_id = classify_image_item_group(item)
        group_label, group_order = IMAGE_GROUPS[group_id]
        if item.get("category_id") == "image_review_units":
            item["category_id"] = image_group_category_id(group_id)
        item["image_group_id"] = group_id
        item["image_group_label"] = group_label
        item["image_group_order"] = group_order
        original_order[item["item_id"]] = index
        grouped[group_id].append(item)

    for group_id, members in grouped.items():
        _, group_order = IMAGE_GROUPS[group_id]
        members.sort(
            key=lambda item: (
                int(item.get("review_order") or 0),
                int(item.get("offset") or 0),
                original_order.get(item["item_id"], 0),
            )
        )
        for index, item in enumerate(members, start=1):
            item["review_order"] = group_order + index * 10

    items.sort(key=lambda item: (int(item.get("review_order") or 0), original_order.get(item["item_id"], 0)))


def image_item_is_visible(item: dict) -> bool:
    if item.get("category_id") in HIDDEN_IMAGE_CATEGORY_IDS:
        return False
    if item.get("image_group_id") in HIDDEN_IMAGE_GROUP_IDS:
        return False
    return True


COMMON_HUD_TILE_OFFSET = 0x00534874
COMMON_HUD_TILE_COUNT = 0x100
COMMON_HUD_TILE_OUT = IMAGE_INVENTORY / "edit_packs" / "common_hud_tiles_00534874"
ALCHEMY_TILE_OFFSET = 0x003A206C
ALCHEMY_TILE_OUT = IMAGE_INVENTORY / "edit_packs" / "alchemy_tiles_003A206C"
PAGE_TURN_RLE_TILE_MANIFEST = (
    IMAGE_INVENTORY
    / "edit_packs"
    / "page_turn_power_animation"
    / "numbered_rle_tiles_large"
    / "manifest.json"
)
PAGE_TURN_RLE_TILE_OUT_ROOT = IMAGE_INVENTORY / "edit_packs" / "page_turn_power_animation" / "tile_categories"
REGISTRY_B_TABLE_OFFSET = 0x00183D50
REGISTRY_B_ZP_OUT = IMAGE_INVENTORY / "edit_packs" / "registry_b_zp01_resources"
REGISTRY_B_ZP_TARGETS = [
    {
        "entry": 0x03,
        "label": "PARTY 캐릭터/이름 타일셋 - Edward Elric",
        "tile_columns": 12,
        "group_id": "registry_b_party_name_tiles",
        "priority": "high",
        "notes": "PARTY 화면 캐릭터 이름/초상화 조합에 쓰이는 Registry B 타일셋 후보. 12칸 단위로 붙인 source_1x를 편집한다.",
    },
    {
        "entry": 0x04,
        "label": "PARTY 캐릭터/이름 타일셋 - Alphonse Elric",
        "tile_columns": 12,
        "group_id": "registry_b_party_name_tiles",
        "priority": "high",
        "notes": "PARTY 화면 캐릭터 이름/초상화 조합에 쓰이는 Registry B 타일셋 후보. 12칸 단위로 붙인 source_1x를 편집한다.",
    },
    {
        "entry": 0x05,
        "label": "PARTY 캐릭터/이름 타일셋 - Roy Mustang",
        "tile_columns": 12,
        "group_id": "registry_b_party_name_tiles",
        "priority": "high",
        "notes": "PARTY 화면 캐릭터 이름/초상화 조합에 쓰이는 Registry B 타일셋 후보. 12칸 단위로 붙인 source_1x를 편집한다.",
    },
    {
        "entry": 0x06,
        "label": "PARTY 캐릭터/이름 타일셋 - B[06]",
        "tile_columns": 12,
        "group_id": "registry_b_party_name_tiles",
        "priority": "high",
        "notes": "PARTY 화면 캐릭터 이름/초상화 조합에 쓰이는 Registry B 타일셋 후보. 12칸 단위로 붙인 source_1x를 편집한다.",
    },
    {
        "entry": 0x07,
        "label": "PARTY 캐릭터/이름 타일셋 - B[07]",
        "tile_columns": 12,
        "group_id": "registry_b_party_name_tiles",
        "priority": "high",
        "notes": "PARTY 화면 캐릭터 이름/초상화 조합에 쓰이는 Registry B 타일셋 후보. 12칸 단위로 붙인 source_1x를 편집한다.",
    },
    {
        "entry": 0x08,
        "label": "PARTY 캐릭터/이름 타일셋 - B[08]",
        "tile_columns": 12,
        "group_id": "registry_b_party_name_tiles",
        "priority": "high",
        "notes": "PARTY 화면 캐릭터 이름/초상화 조합에 쓰이는 Registry B 타일셋 후보. 12칸 단위로 붙인 source_1x를 편집한다.",
    },
    {
        "entry": 0x09,
        "label": "PARTY 캐릭터/이름 타일셋 - B[09]",
        "tile_columns": 12,
        "group_id": "registry_b_party_name_tiles",
        "priority": "high",
        "notes": "PARTY 화면 캐릭터 이름/초상화 조합에 쓰이는 Registry B 타일셋 후보. 12칸 단위로 붙인 source_1x를 편집한다.",
    },
    {
        "entry": 0x0A,
        "label": "PARTY 캐릭터/이름 타일셋 - B[0A]",
        "tile_columns": 12,
        "group_id": "registry_b_party_name_tiles",
        "priority": "high",
        "notes": "PARTY 화면 캐릭터 이름/초상화 조합에 쓰이는 Registry B 타일셋 후보. 12칸 단위로 붙인 source_1x를 편집한다.",
    },
    {
        "entry": 0x0D,
        "label": "PARTY 이름/숫자/가나 보조 타일셋",
        "tile_columns": 12,
        "group_id": "registry_b_party_name_tiles",
        "priority": "high",
        "notes": "PARTY 화면 이름 표시 근처에서 참조되는 raw 4bpp Registry B 타일셋 후보. 12칸 단위로 붙인 source_1x를 편집한다.",
    },
    {
        "entry": 0x10,
        "label": "SUB 메뉴 타일셋 A - 錬成手帳",
        "destination": "0x06004000",
        "tile_columns": 16,
        "edit_tile_columns": 7,
        "edit_tile_indices": (
            list(range(0x01, 0x08))
            + list(range(0x21, 0x28))
            + list(range(0x41, 0x48))
            + list(range(0x61, 0x68))
        ),
        "group_id": "registry_b_sub_menu_tiles",
        "priority": "high",
        "notes": "ss4 화면의 오른쪽 SUB 메뉴 라벨 계열. 0x0653A8 호출에서 VRAM 0x06004000으로 로드된다.",
    },
    {
        "entry": 0x11,
        "label": "SUB 메뉴 타일셋 B - 入れ替え/必殺技",
        "destination": "0x06004000",
        "tile_columns": 16,
        "edit_tile_columns": 7,
        "edit_tile_indices": (
            list(range(0x01, 0x08))
            + list(range(0x21, 0x28))
            + list(range(0x41, 0x48))
            + list(range(0x61, 0x68))
            + list(range(0x81, 0x88))
            + list(range(0xA1, 0xA8))
        ),
        "group_id": "registry_b_sub_menu_tiles",
        "priority": "high",
        "notes": "ss5 화면의 오른쪽 SUB 메뉴 라벨 계열. 0x065412 호출에서 VRAM 0x06004000으로 로드된다.",
    },
    {
        "entry": 0x12,
        "label": "SUB 메뉴 타일셋 C",
        "destination": "0x06004000",
        "tile_columns": 16,
        "group_id": "registry_b_sub_menu_tiles",
        "notes": "관련 SUB/파티 화면 흐름. 0x0658DC 호출에서 VRAM 0x06004000으로 로드된다.",
        "replacement_target": False,
        "replacement_target_reason": "현재 확인된 일본어 텍스트가 없는 빈 패널/프레임 리소스라 번역 교체 대상에서 제외.",
    },
    {
        "entry": 0x13,
        "label": "SUB 메뉴 보조 타일셋",
        "destination": "0x06008000",
        "tile_columns": 16,
        "group_id": "registry_b_sub_menu_tiles",
        "notes": "entry 0x12와 같은 화면 흐름에서 0x0658FC 호출로 VRAM 0x06008000에 로드되는 보조 레이어 후보.",
        "replacement_target": False,
        "replacement_target_reason": "현재 확인된 일본어 텍스트가 없는 보조 프레임 리소스라 번역 교체 대상에서 제외.",
    },
]
CURRENT_REVIEW_ROM = ROOT / "patched_roms" / "current_review" / "hnr_localization_review.gba"
CARD_PAGE_COUNT_MANIFEST = IMAGE_INVENTORY / "edit_packs" / "card_page_count" / "manifest.json"


def tile_to_grayscale_image(tile: bytes):
    from PIL import Image

    image = Image.new("L", (8, 8), 0)
    pixels = image.load()
    for y in range(8):
        row = tile[y * 4 : y * 4 + 4]
        for pair, byte in enumerate(row):
            pixels[pair * 2, y] = (byte & 0x0F) * 17
            pixels[pair * 2 + 1, y] = ((byte >> 4) & 0x0F) * 17
    return image


def tiles_to_sheet_image(payload: bytes, columns: int):
    from PIL import Image

    tile_count = len(payload) // 32
    rows = (tile_count + columns - 1) // columns
    image = Image.new("L", (columns * 8, rows * 8), 0)
    for tile_index in range(tile_count):
        tile = payload[tile_index * 32 : tile_index * 32 + 32]
        tile_image = tile_to_grayscale_image(tile)
        x = (tile_index % columns) * 8
        y = (tile_index // columns) * 8
        image.paste(tile_image, (x, y))
    return image


def tiles_to_mapped_sheet_image(payload: bytes, tile_indices: list[int], columns: int):
    from PIL import Image

    rows = (len(tile_indices) + columns - 1) // columns
    image = Image.new("L", (columns * 8, rows * 8), 0)
    for edit_index, tile_index in enumerate(tile_indices):
        tile = payload[tile_index * 32 : tile_index * 32 + 32]
        tile_image = tile_to_grayscale_image(tile)
        x = (edit_index % columns) * 8
        y = (edit_index // columns) * 8
        image.paste(tile_image, (x, y))
    return image


def registry_b_entry_info(rom: bytes, entry: int) -> dict | None:
    table_offset = REGISTRY_B_TABLE_OFFSET + entry * 8
    if table_offset < 0 or table_offset + 8 > len(rom):
        return None
    pointer = int.from_bytes(rom[table_offset : table_offset + 4], "little")
    length = int.from_bytes(rom[table_offset + 4 : table_offset + 8], "little")
    file_offset = gba_pointer_to_file_offset(pointer, len(rom))
    if file_offset is None or length <= 0 or file_offset + 8 > len(rom):
        return None
    return {
        "entry": entry,
        "table_offset": table_offset,
        "rom_pointer": pointer,
        "file_offset": file_offset,
        "compressed_size": length,
    }


def decode_registry_b_tile_resource(rom: bytes, info: dict) -> dict:
    offset = int(info["file_offset"])
    size = int(info["compressed_size"])
    magic = rom[offset : offset + 4]
    if magic in {b"ZP00", b"ZP01"}:
        decoded = decompress_zp_resource(rom, offset, max_output_size=0x400000)
        return {
            "variant": decoded.variant,
            "payload": decoded.payload,
            "consumed_size": decoded.consumed,
            "stored_size": size,
            "compression": f"registry_b_{decoded.variant.lower()}",
        }
    if offset + size > len(rom):
        raise ValueError("raw Registry B resource exceeds ROM size")
    payload = rom[offset : offset + size]
    return {
        "variant": "raw",
        "payload": payload,
        "consumed_size": size,
        "stored_size": size,
        "compression": "registry_b_raw4bpp",
    }


def ensure_registry_b_zp_edit_pack() -> list[dict]:
    from PIL import Image, ImageDraw, ImageFont

    source_rom = CURRENT_REVIEW_ROM if CURRENT_REVIEW_ROM.exists() else SOURCE_ROM
    if not source_rom.exists():
        return []
    rom = source_rom.read_bytes()

    REGISTRY_B_ZP_OUT.mkdir(parents=True, exist_ok=True)
    raw_dir = REGISTRY_B_ZP_OUT / "decoded_raw"
    full_source_dir = REGISTRY_B_ZP_OUT / "full_source_1x"
    source_dir = REGISTRY_B_ZP_OUT / "source_1x"
    preview_dir = REGISTRY_B_ZP_OUT / "preview_4x"
    grid_dir = REGISTRY_B_ZP_OUT / "grid_4x"
    contact_dir = REGISTRY_B_ZP_OUT / "contact_sheets"
    for path in (raw_dir, full_source_dir, source_dir, preview_dir, grid_dir, contact_dir):
        path.mkdir(parents=True, exist_ok=True)

    try:
        label_font = ImageFont.truetype("/System/Library/Fonts/Monaco.ttf", 8)
    except Exception:
        label_font = None

    records: list[dict] = []
    for spec in REGISTRY_B_ZP_TARGETS:
        entry = int(spec["entry"])
        info = registry_b_entry_info(rom, entry)
        if not info:
            continue
        try:
            decoded = decode_registry_b_tile_resource(rom, info)
        except Exception as exc:
            records.append({**spec, **info, "status": "decode_error", "error": str(exc)})
            continue
        payload = decoded["payload"]
        if len(payload) % 32:
            records.append(
                {
                    **spec,
                    **info,
                    "status": "skipped",
                    "variant": decoded["variant"],
                    "decoded_size": len(payload),
                    "reason": "not a 4bpp-tile-aligned Registry B resource",
                }
            )
            continue

        tile_count = len(payload) // 32
        resource_columns = int(spec.get("tile_columns") or min(16, max(1, tile_count)))
        resource_columns = max(1, min(resource_columns, max(1, tile_count)))
        edit_tile_indices = [int(value) for value in spec.get("edit_tile_indices", [])]
        if edit_tile_indices:
            edit_tile_indices = [value for value in edit_tile_indices if 0 <= value < tile_count]
        edit_tile_count = len(edit_tile_indices) if edit_tile_indices else tile_count
        columns = int(spec.get("edit_tile_columns") or resource_columns)
        columns = max(1, min(columns, max(1, edit_tile_count)))
        rows = (edit_tile_count + columns - 1) // columns
        entry_hex = f"{entry:02X}"
        raw_path = raw_dir / f"registry_b_{entry_hex}_decoded.bin"
        full_source_path = full_source_dir / f"registry_b_{entry_hex}_{resource_columns}cols_full.png"
        source_path = source_dir / f"registry_b_{entry_hex}_{columns}cols.png"
        preview_path = preview_dir / f"registry_b_{entry_hex}_{columns}cols_4x.png"
        grid_path = grid_dir / f"registry_b_{entry_hex}_{columns}cols_grid_4x.png"
        contact_path = contact_dir / f"registry_b_{entry_hex}_contact.png"

        raw_path.write_bytes(payload)
        full_sheet = tiles_to_sheet_image(payload, resource_columns)
        full_sheet.save(full_source_path)
        if edit_tile_indices:
            sheet = tiles_to_mapped_sheet_image(payload, edit_tile_indices, columns)
        else:
            sheet = full_sheet
        sheet.save(source_path)
        preview = sheet.resize((sheet.width * 4, sheet.height * 4), Image.Resampling.NEAREST)
        preview.save(preview_path)

        grid = preview.convert("RGB")
        grid_draw = ImageDraw.Draw(grid)
        for x in range(0, grid.width + 1, 32):
            grid_draw.line((x, 0, x, grid.height), fill=(255, 96, 96))
        for y in range(0, grid.height + 1, 32):
            grid_draw.line((0, y, grid.width, y), fill=(255, 96, 96))
        grid.save(grid_path)

        cell = 44
        contact_cols = resource_columns
        contact_rows = (tile_count + contact_cols - 1) // contact_cols
        contact = Image.new("RGB", (contact_cols * cell, contact_rows * cell), (18, 20, 23))
        draw = ImageDraw.Draw(contact)
        for tile_index in range(tile_count):
            tile = payload[tile_index * 32 : tile_index * 32 + 32]
            tile_image = tile_to_grayscale_image(tile).resize((32, 32), Image.Resampling.NEAREST).convert("RGB")
            x = (tile_index % contact_cols) * cell
            y = (tile_index // contact_cols) * cell
            contact.paste(tile_image, (x + 6, y + 10))
            draw.text((x + 4, y + 1), f"{tile_index:03X}", fill=(245, 225, 90), font=label_font)
        contact.save(contact_path)

        records.append(
            {
                **spec,
                **info,
                "status": "decoded",
                "variant": decoded["variant"],
                "compression": decoded["compression"],
                "decoded_size": len(payload),
                "decoder_consumed_size": decoded["consumed_size"],
                "stored_size": decoded["stored_size"],
                "tile_count": tile_count,
                "resource_tile_count": tile_count,
                "edit_tile_count": edit_tile_count,
                "tile_columns": columns,
                "resource_tile_columns": resource_columns,
                "tile_rows": rows,
                "tile_indices": edit_tile_indices,
                "raw_path": str(raw_path.relative_to(ROOT)),
                "full_source_1x": str(full_source_path.relative_to(ROOT)),
                "source_1x": str(source_path.relative_to(ROOT)),
                "preview_4x": str(preview_path.relative_to(ROOT)),
                "grid_4x": str(grid_path.relative_to(ROOT)),
                "contact_sheet": str(contact_path.relative_to(ROOT)),
                "source_rom": str(source_rom.relative_to(ROOT)),
            }
        )

    manifest = {
        "table_offset": REGISTRY_B_TABLE_OFFSET,
        "table_offset_hex": f"0x{REGISTRY_B_TABLE_OFFSET:08X}",
        "source_rom": str(source_rom.relative_to(ROOT)),
        "notes": "Registry B tile resources decoded from the 0x08183D50 mirror table. ZP01/ZP00 resources are decompressed; raw 4bpp entries are exported directly. source_1x images are contiguous 8x8 tile sheets for editing.",
        "resources": records,
    }
    (REGISTRY_B_ZP_OUT / "manifest.json").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    return [record for record in records if record.get("status") == "decoded"]


def ensure_common_hud_tile_edit_pack() -> dict[int, dict[str, str]]:
    from PIL import Image, ImageDraw, ImageFont

    if not SOURCE_ROM.exists():
        return {}
    COMMON_HUD_TILE_OUT.mkdir(parents=True, exist_ok=True)
    source_dir = COMMON_HUD_TILE_OUT / "source_1x"
    preview_dir = COMMON_HUD_TILE_OUT / "preview_8x"
    source_dir.mkdir(parents=True, exist_ok=True)
    preview_dir.mkdir(parents=True, exist_ok=True)

    payload, _ = decompress_lz77(SOURCE_ROM.read_bytes(), COMMON_HUD_TILE_OFFSET, max_output_size=0x4000)
    tile_count = min(COMMON_HUD_TILE_COUNT, len(payload) // 32)
    paths: dict[int, dict[str, str]] = {}

    contact_cols = 16
    cell = 44
    contact = Image.new("RGB", (contact_cols * cell, ((tile_count + contact_cols - 1) // contact_cols) * cell), (18, 20, 23))
    draw = ImageDraw.Draw(contact)
    try:
        label_font = ImageFont.truetype("/System/Library/Fonts/Monaco.ttf", 8)
    except Exception:
        label_font = None

    for tile_index in range(tile_count):
        tile = payload[tile_index * 32 : tile_index * 32 + 32]
        image = tile_to_grayscale_image(tile)
        source_path = source_dir / f"tile_{tile_index:03X}.png"
        preview_path = preview_dir / f"tile_{tile_index:03X}_8x.png"
        image.save(source_path)
        image.resize((64, 64), Image.Resampling.NEAREST).save(preview_path)

        sheet_tile = image.resize((32, 32), Image.Resampling.NEAREST).convert("RGB")
        x = (tile_index % contact_cols) * cell
        y = (tile_index // contact_cols) * cell
        contact.paste(sheet_tile, (x + 6, y + 10))
        draw.text((x + 4, y + 1), f"{tile_index:03X}", fill=(245, 225, 90), font=label_font)

        paths[tile_index] = {
            "source_1x": str(source_path.relative_to(ROOT)),
            "preview_8x": str(preview_path.relative_to(ROOT)),
        }

    contact_path = COMMON_HUD_TILE_OUT / "common_hud_tiles_00534874_contact_sheet.png"
    contact.save(contact_path)
    manifest = {
        "offset": COMMON_HUD_TILE_OFFSET,
        "offset_hex": f"0x{COMMON_HUD_TILE_OFFSET:08X}",
        "tile_count": tile_count,
        "source_rom": str(SOURCE_ROM.relative_to(ROOT)),
        "contact_sheet": str(contact_path.relative_to(ROOT)),
        "notes": "0x00534874 is a shared LZ77 4bpp HUD tile block. Editing one tile changes every runtime tilemap reference to that tile number.",
        "tiles": [
            {
                "tile_index": tile_index,
                "tile_index_hex": f"0x{tile_index:03X}",
                **paths[tile_index],
            }
            for tile_index in range(tile_count)
        ],
    }
    (COMMON_HUD_TILE_OUT / "manifest.json").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    return paths


def build_common_hud_tile_items() -> list[dict]:
    paths = ensure_common_hud_tile_edit_pack()
    if not paths:
        return []
    items: list[dict] = []
    for tile_index, asset_paths in sorted(paths.items()):
        tile_hex = f"{tile_index:03X}"
        reserved_blank_tile = tile_index == 0
        items.append(
            {
                "item_id": f"image:lz77_tile:00534874:tile_{tile_hex}",
                "category_id": "common_hud_tiles",
                "group_id": "common_hud_tiles_00534874",
                "label": f"공유 HUD 타일 0x{tile_hex}",
                "status": "candidate_found",
                "priority": "debug",
                "offset": COMMON_HUD_TILE_OFFSET,
                "review_order": 6000 + tile_index,
                "review_goal": "0x00534874 LZ77 공유 HUD 타일셋을 8x8 타일 1개 단위로 교체",
                "recommended_probe_method": "공유 타일이므로 런타임 tilemap 사용 위치를 확인한 뒤 필요한 타일만 교체",
                "future_workspace": str(COMMON_HUD_TILE_OUT.relative_to(ROOT)),
                "expected_text_kind": "shared_lz77_4bpp_tile",
                "source": "lz77_tile_4bpp",
                "compression": "lz77_tile",
                "notes": (
                    "이 항목은 0x00534874 LZ77 블록 안의 8x8 타일 1개만 바꿉니다. "
                    "같은 타일 번호를 쓰는 모든 화면 위치가 함께 바뀌므로, 이름 전용이라고 확정된 경우에만 교체하세요."
                ),
                "subunits": [
                    {
                        "id": f"lz77_00534874_tile_{tile_hex}",
                        "label": f"ROM offset 0x00534874 / tile 0x{tile_hex}",
                        "first_action": "8x8 PNG 또는 정수배 PNG를 업로드하면 이 타일 하나만 적용",
                    }
                ],
                "source_preview_path": asset_paths["preview_8x"],
                "source_download_path": asset_paths["source_1x"],
                "replacement_path": "",
                "replacement_target": not reserved_blank_tile,
                "replacement_target_reason": (
                    "0x00534874 tile 000 is the global blank/background tile used by many BG maps."
                    if reserved_blank_tile
                    else ""
                ),
                "comparison_notes": "",
                "candidate_gallery": [
                    {
                        "index": "tile_1x",
                        "offset": COMMON_HUD_TILE_OFFSET,
                        "source": "lz77_tile_4bpp_source_1x",
                        "png_path": asset_paths["source_1x"],
                        "preview_path": asset_paths["source_1x"],
                        "tile_index": tile_index,
                        "tile_index_hex": f"0x{tile_hex}",
                        "decompressed_size": 32,
                    },
                    {
                        "index": "tile_8x",
                        "offset": COMMON_HUD_TILE_OFFSET,
                        "source": "lz77_tile_4bpp_preview_8x",
                        "png_path": asset_paths["preview_8x"],
                        "preview_path": asset_paths["preview_8x"],
                        "tile_index": tile_index,
                        "tile_index_hex": f"0x{tile_hex}",
                        "decompressed_size": 32,
                    },
                ],
                "progress_status": "candidate_found",
                "default_review_included": False,
                "tile_columns": 1,
                "tile_index": tile_index,
                "tile_index_hex": f"0x{tile_hex}",
                "raw_byte_length": 32,
            }
        )
    return items


def ensure_alchemy_tile_edit_pack() -> dict[int, dict[str, str]]:
    from PIL import Image, ImageDraw, ImageFont
    from apply_image_replacements import direct_rle_tiles_from_image

    source_rom = CURRENT_REVIEW_ROM if CURRENT_REVIEW_ROM.exists() else SOURCE_ROM
    if not source_rom.exists():
        return {}
    ALCHEMY_TILE_OUT.mkdir(parents=True, exist_ok=True)
    source_dir = ALCHEMY_TILE_OUT / "source_1x"
    preview_dir = ALCHEMY_TILE_OUT / "preview_8x"
    source_dir.mkdir(parents=True, exist_ok=True)
    preview_dir.mkdir(parents=True, exist_ok=True)

    payload, _ = decompress_gba_rle(source_rom.read_bytes(), ALCHEMY_TILE_OFFSET, max_output_size=0x400000)
    active_direct_patches: list[dict] = []
    if CARD_PAGE_COUNT_MANIFEST.exists():
        page_manifest = load_json(CARD_PAGE_COUNT_MANIFEST)
        direct_specs = page_manifest.get("replacement_direct_rle_tiles") or []
        replacement_path = page_manifest.get("replacement_path") or ""
        tile_map_path = page_manifest.get("tile_map_path") or ""
        if (
            int(page_manifest.get("offset", page_manifest.get("rle_offset", -1))) == ALCHEMY_TILE_OFFSET
            and direct_specs
            and replacement_path
            and tile_map_path
            and (ROOT / replacement_path).is_file()
            and (ROOT / tile_map_path).is_file()
        ):
            tile_map = load_json(ROOT / tile_map_path)
            payload_base = None
            if page_manifest.get("replacement_payload_base") == "source_raw":
                raw_path = tile_map.get("rle_raw_path", "")
                if raw_path and (ROOT / raw_path).is_file():
                    payload_base = (ROOT / raw_path).read_bytes()
            payload, meta = direct_rle_tiles_from_image(
                ROOT / replacement_path,
                tile_map,
                payload,
                direct_specs,
                payload_base,
            )
            active_direct_patches.append(
                {
                    "source_manifest": str(CARD_PAGE_COUNT_MANIFEST.relative_to(ROOT)),
                    "replacement_path": replacement_path,
                    "written_tile_indexes": meta.get("written_tile_indexes", []),
                    "replacement_payload_base": page_manifest.get("replacement_payload_base", ""),
                }
            )
    tile_count = len(payload) // 32
    paths: dict[int, dict[str, str]] = {}

    contact_cols = 16
    cell = 44
    contact = Image.new("RGB", (contact_cols * cell, ((tile_count + contact_cols - 1) // contact_cols) * cell), (18, 20, 23))
    draw = ImageDraw.Draw(contact)
    try:
        label_font = ImageFont.truetype("/System/Library/Fonts/Monaco.ttf", 8)
    except Exception:
        label_font = None

    for tile_index in range(tile_count):
        tile = payload[tile_index * 32 : tile_index * 32 + 32]
        image = tile_to_grayscale_image(tile)
        source_path = source_dir / f"tile_{tile_index:03X}.png"
        preview_path = preview_dir / f"tile_{tile_index:03X}_8x.png"
        image.save(source_path)
        image.resize((64, 64), Image.Resampling.NEAREST).save(preview_path)

        sheet_tile = image.resize((32, 32), Image.Resampling.NEAREST).convert("RGB")
        x = (tile_index % contact_cols) * cell
        y = (tile_index // contact_cols) * cell
        contact.paste(sheet_tile, (x + 6, y + 10))
        draw.text((x + 4, y + 1), f"{tile_index:03X}", fill=(245, 225, 90), font=label_font)

        paths[tile_index] = {
            "source_1x": str(source_path.relative_to(ROOT)),
            "preview_8x": str(preview_path.relative_to(ROOT)),
        }

    contact_path = ALCHEMY_TILE_OUT / "alchemy_tiles_003A206C_contact_sheet.png"
    contact.save(contact_path)
    manifest = {
        "offset": ALCHEMY_TILE_OFFSET,
        "offset_hex": f"0x{ALCHEMY_TILE_OFFSET:08X}",
        "decompressed_size": len(payload),
        "tile_count": tile_count,
        "source_rom": str(source_rom.relative_to(ROOT)),
        "contact_sheet": str(contact_path.relative_to(ROOT)),
        "active_direct_patches": active_direct_patches,
        "notes": (
            "0x003A206C is the RLE 4bpp tile block used by the alchemy/card UI tile graphics we have been editing. "
            "Editing one tile changes every runtime tilemap reference to that RLE tile number."
        ),
        "tiles": [
            {
                "tile_index": tile_index,
                "tile_index_hex": f"0x{tile_index:03X}",
                **paths[tile_index],
            }
            for tile_index in range(tile_count)
        ],
    }
    (ALCHEMY_TILE_OUT / "manifest.json").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    return paths


def build_alchemy_tile_items() -> list[dict]:
    paths = ensure_alchemy_tile_edit_pack()
    if not paths:
        return []
    manifest = load_json_if_exists(ALCHEMY_TILE_OUT / "manifest.json", {})
    direct_patch_tile_indexes: set[int] = set()
    for patch in manifest.get("active_direct_patches", []):
        for tile_index in patch.get("written_tile_indexes", []):
            try:
                direct_patch_tile_indexes.add(int(tile_index))
            except (TypeError, ValueError):
                continue
    items: list[dict] = []
    for tile_index, asset_paths in sorted(paths.items()):
        tile_hex = f"{tile_index:03X}"
        direct_patch_applied = tile_index in direct_patch_tile_indexes
        items.append(
            {
                "item_id": f"image:rle_tile:003A206C:tile_{tile_hex}",
                "category_id": "alchemy_tiles",
                "group_id": "alchemy_tiles_003A206C",
                "label": f"연금술 타일 {tile_index} (0x{tile_hex})",
                "status": "candidate_found",
                "priority": "debug",
                "offset": ALCHEMY_TILE_OFFSET,
                "review_order": 7000 + tile_index,
                "review_goal": "0x003A206C 연금술/카드 UI RLE 타일셋을 8x8 타일 1개 단위로 교체",
                "recommended_probe_method": "방금 수정한 장째/연금술 카드 UI와 같은 RLE 블록이므로 실제 사용 위치를 확인한 뒤 필요한 타일만 교체",
                "future_workspace": str(ALCHEMY_TILE_OUT.relative_to(ROOT)),
                "expected_text_kind": "alchemy_rle_4bpp_tile",
                "source": "rle_tile_4bpp",
                "compression": "rle_tile",
                "notes": (
                    "이 항목은 0x003A206C RLE 블록 안의 8x8 타일 1개만 바꿉니다. "
                    "같은 타일 번호를 쓰는 모든 화면 위치가 함께 바뀌므로, 실제 사용 위치를 확인한 뒤 교체하세요."
                ),
                "subunits": [
                    {
                        "id": f"rle_003A206C_tile_{tile_hex}",
                        "label": f"ROM offset 0x003A206C / tile 0x{tile_hex}",
                        "first_action": "8x8 PNG 또는 정수배 PNG를 업로드하면 이 타일 하나만 적용",
                    }
                ],
                "source_preview_path": asset_paths["preview_8x"],
                "source_download_path": asset_paths["source_1x"],
                "replacement_path": asset_paths["source_1x"] if direct_patch_applied else "",
                "replacement_target": True,
                "replacement_target_reason": "",
                "comparison_notes": (
                    "active_direct_patches에서 승격된 타일 교체입니다. 숨긴 화면 편집 항목에 의존하지 않고 "
                    "연금술 타일셋 자체 교체로 재적용됩니다."
                    if direct_patch_applied
                    else ""
                ),
                "candidate_gallery": [
                    {
                        "index": "tile_1x",
                        "offset": ALCHEMY_TILE_OFFSET,
                        "source": "rle_tile_4bpp_source_1x",
                        "png_path": asset_paths["source_1x"],
                        "preview_path": asset_paths["source_1x"],
                        "tile_index": tile_index,
                        "tile_index_hex": f"0x{tile_hex}",
                        "decompressed_size": 32,
                    },
                    {
                        "index": "tile_8x",
                        "offset": ALCHEMY_TILE_OFFSET,
                        "source": "rle_tile_4bpp_preview_8x",
                        "png_path": asset_paths["preview_8x"],
                        "preview_path": asset_paths["preview_8x"],
                        "tile_index": tile_index,
                        "tile_index_hex": f"0x{tile_hex}",
                        "decompressed_size": 32,
                    },
                ],
                "progress_status": "candidate_found",
                "default_review_included": False,
                "tile_columns": 1,
                "tile_index": tile_index,
                "tile_index_hex": f"0x{tile_hex}",
                "raw_byte_length": 32,
                "replacement_source": "active_direct_patch" if direct_patch_applied else "",
            }
        )
    return items


def page_turn_rle_tile_category_id(order: int) -> str:
    return f"page_turn_rle_{order:02d}_tiles"


def page_turn_rle_tile_entries() -> list[dict]:
    manifest = load_json_if_exists(PAGE_TURN_RLE_TILE_MANIFEST, {"items": []})
    entries = []
    for entry in manifest.get("items", []):
        try:
            order = int(entry.get("order"))
        except (TypeError, ValueError):
            continue
        if 5 <= order <= 12:
            entries.append(entry)
    return sorted(entries, key=lambda entry: int(entry["order"]))


def build_page_turn_rle_tile_categories() -> list[dict]:
    categories = []
    for entry in page_turn_rle_tile_entries():
        order = int(entry["order"])
        category_id = page_turn_rle_tile_category_id(order)
        if category_id in HIDDEN_IMAGE_CATEGORY_IDS:
            continue
        offset = int(entry.get("offset", 0))
        categories.append(
            {
                "id": category_id,
                "label": f"페이지 넘김 RLE {order:02d} 타일셋",
                "type": "image",
                "sort_order": 22 + order,
                "path": (
                    "confirmed_data/image_inventory/edit_packs/page_turn_power_animation/"
                    f"tile_categories/{category_id}_{offset:08X}/manifest.json"
                ),
                "description": f"카드 책자 페이지 넘김 애니메이션 RLE {order:02d} / 0x{offset:08X}를 8x8 타일 단위로 검토/교체",
                "build_enabled": False,
            }
        )
    return categories


def ensure_page_turn_rle_tile_edit_packs() -> dict[str, dict[int, dict[str, str]]]:
    from PIL import Image, ImageDraw, ImageFont

    if not SOURCE_ROM.exists():
        return {}
    rom = SOURCE_ROM.read_bytes()
    entries = page_turn_rle_tile_entries()
    if not entries:
        return {}

    try:
        label_font = ImageFont.truetype("/System/Library/Fonts/Monaco.ttf", 8)
    except Exception:
        label_font = None

    all_paths: dict[str, dict[int, dict[str, str]]] = {}
    for entry in entries:
        order = int(entry["order"])
        offset = int(entry["offset"])
        category_id = page_turn_rle_tile_category_id(order)
        out_dir = PAGE_TURN_RLE_TILE_OUT_ROOT / f"{category_id}_{offset:08X}"
        source_dir = out_dir / "source_1x"
        preview_dir = out_dir / "preview_8x"
        source_dir.mkdir(parents=True, exist_ok=True)
        preview_dir.mkdir(parents=True, exist_ok=True)

        payload, consumed = decompress_gba_rle(rom, offset, max_output_size=0x400000)
        if len(payload) % 32:
            continue
        tile_count = len(payload) // 32
        tile_columns = int(entry.get("tile_columns") or 32)
        tile_columns = max(1, min(tile_columns, max(1, tile_count)))
        paths: dict[int, dict[str, str]] = {}

        contact_cols = 16
        cell = 44
        contact_rows = (tile_count + contact_cols - 1) // contact_cols
        contact = Image.new("RGB", (contact_cols * cell, contact_rows * cell), (18, 20, 23))
        draw = ImageDraw.Draw(contact)

        for tile_index in range(tile_count):
            tile = payload[tile_index * 32 : tile_index * 32 + 32]
            image = tile_to_grayscale_image(tile)
            source_path = source_dir / f"tile_{tile_index:03X}.png"
            preview_path = preview_dir / f"tile_{tile_index:03X}_8x.png"
            image.save(source_path)
            image.resize((64, 64), Image.Resampling.NEAREST).save(preview_path)

            sheet_tile = image.resize((32, 32), Image.Resampling.NEAREST).convert("RGB")
            x = (tile_index % contact_cols) * cell
            y = (tile_index // contact_cols) * cell
            contact.paste(sheet_tile, (x + 6, y + 10))
            draw.text((x + 4, y + 1), f"{tile_index:03X}", fill=(245, 225, 90), font=label_font)

            paths[tile_index] = {
                "source_1x": str(source_path.relative_to(ROOT)),
                "preview_8x": str(preview_path.relative_to(ROOT)),
            }

        contact_path = out_dir / f"{category_id}_{offset:08X}_contact_sheet.png"
        contact.save(contact_path)
        manifest = {
            "order": order,
            "rle_index": entry.get("rle_index"),
            "offset": offset,
            "offset_hex": f"0x{offset:08X}",
            "decompressed_size": len(payload),
            "compressed_size": consumed,
            "tile_count": tile_count,
            "tile_columns": tile_columns,
            "source_rom": str(SOURCE_ROM.relative_to(ROOT)),
            "source_preview_path": entry.get("source_path", ""),
            "numbered_path": entry.get("numbered_path", ""),
            "contact_sheet": str(contact_path.relative_to(ROOT)),
            "notes": (
                "카드 책자 페이지 넘김 애니메이션 후보 RLE를 원본 ROM payload 기준으로 8x8 타일 단위 추출. "
                "이 카테고리의 타일 단위 적용은 앞선 full-image/repoint 변경을 누적 기준으로 삼지 않습니다."
            ),
            "tiles": [
                {
                    "tile_index": tile_index,
                    "tile_index_hex": f"0x{tile_index:03X}",
                    **paths[tile_index],
                }
                for tile_index in range(tile_count)
            ],
        }
        (out_dir / "manifest.json").write_text(
            json.dumps(manifest, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )
        all_paths[category_id] = paths
    return all_paths


def build_page_turn_rle_tile_items() -> list[dict]:
    paths_by_category = ensure_page_turn_rle_tile_edit_packs()
    if not paths_by_category:
        return []

    entry_by_category = {
        page_turn_rle_tile_category_id(int(entry["order"])): entry
        for entry in page_turn_rle_tile_entries()
    }
    items: list[dict] = []
    for category_id, paths in sorted(paths_by_category.items()):
        entry = entry_by_category.get(category_id)
        if not entry:
            continue
        order = int(entry["order"])
        offset = int(entry["offset"])
        offset_hex = f"{offset:08X}"
        group_id = f"{category_id}_{offset_hex}"
        for tile_index, asset_paths in sorted(paths.items()):
            tile_hex = f"{tile_index:03X}"
            items.append(
                {
                    "item_id": f"image:rle_tile:{offset_hex}:tile_{tile_hex}",
                    "category_id": category_id,
                    "group_id": group_id,
                    "label": f"페이지 넘김 RLE {order:02d} 타일 {tile_index} (0x{tile_hex})",
                    "status": "candidate_found",
                    "priority": "debug",
                    "offset": offset,
                    "review_order": 7600 + order * 1000 + tile_index,
                    "review_goal": f"페이지 넘김 애니메이션 RLE {order:02d} / 0x{offset_hex}를 8x8 타일 1개 단위로 교체",
                    "recommended_probe_method": "필요한 타일만 조합 보드에 배치하고, 선택 영역 PNG를 업로드해 해당 타일만 교체",
                    "future_workspace": str((PAGE_TURN_RLE_TILE_OUT_ROOT / group_id).relative_to(ROOT)),
                    "expected_text_kind": "page_turn_rle_4bpp_tile",
                    "source": "rle_tile_4bpp",
                    "compression": "rle_tile",
                    "replacement_payload_base": "source_rom",
                    "restore_repoint_to_original": True,
                    "notes": (
                        "이 항목은 원본 ROM의 RLE payload를 기준으로 타일을 다시 구성합니다. "
                        "앞서 같은 RLE 블록을 full-image로 repoint해 둔 변경은 타일 단위 적용 시 기준으로 삼지 않습니다."
                    ),
                    "subunits": [
                        {
                            "id": f"rle_{offset_hex}_tile_{tile_hex}",
                            "label": f"ROM offset 0x{offset_hex} / tile 0x{tile_hex}",
                            "first_action": "8x8 PNG 또는 선택 영역 조합 PNG를 업로드하면 이 타일만 적용",
                        }
                    ],
                    "source_preview_path": asset_paths["preview_8x"],
                    "source_download_path": asset_paths["source_1x"],
                    "replacement_path": "",
                    "replacement_target": True,
                    "replacement_target_reason": "",
                    "comparison_notes": "",
                    "candidate_gallery": [
                        {
                            "index": "tile_1x",
                            "offset": offset,
                            "source": "rle_tile_4bpp_source_1x",
                            "png_path": asset_paths["source_1x"],
                            "preview_path": asset_paths["source_1x"],
                            "tile_index": tile_index,
                            "tile_index_hex": f"0x{tile_hex}",
                            "decompressed_size": 32,
                        },
                        {
                            "index": "tile_8x",
                            "offset": offset,
                            "source": "rle_tile_4bpp_preview_8x",
                            "png_path": asset_paths["preview_8x"],
                            "preview_path": asset_paths["preview_8x"],
                            "tile_index": tile_index,
                            "tile_index_hex": f"0x{tile_hex}",
                            "decompressed_size": 32,
                        },
                    ],
                    "progress_status": "candidate_found",
                    "default_review_included": False,
                    "tile_columns": 1,
                    "tile_index": tile_index,
                    "tile_index_hex": f"0x{tile_hex}",
                    "raw_byte_length": 32,
                }
            )
    return items


def build_registry_b_zp_items() -> list[dict]:
    resources = ensure_registry_b_zp_edit_pack()
    if not resources:
        return []
    items: list[dict] = []
    for resource in sorted(resources, key=lambda record: int(record["entry"])):
        entry = int(resource["entry"])
        entry_hex = f"{entry:02X}"
        offset = int(resource["file_offset"])
        compressed_size = int(resource["compressed_size"])
        decoded_size = int(resource["decoded_size"])
        tile_count = int(resource["tile_count"])
        edit_tile_count = int(resource.get("edit_tile_count") or tile_count)
        columns = int(resource["tile_columns"])
        compression = str(resource.get("compression") or "registry_b_zp01")
        source_kind = "registry_b_raw4bpp" if compression == "registry_b_raw4bpp" else "registry_b_zp01_4bpp"
        expected_kind = "registry_b_raw4bpp_tiles" if compression == "registry_b_raw4bpp" else "registry_b_zp01_4bpp_tiles"
        group_id = str(resource.get("group_id") or "registry_b_zp01_sub_menu_labels")
        tile_indices = [int(value) for value in resource.get("tile_indices", [])]
        items.append(
            {
                "item_id": f"image:registry_b_zp01:{offset:08X}:entry_{entry_hex}",
                "category_id": REGISTRY_B_ZP_CATEGORY_ID,
                "group_id": group_id,
                "label": f"{resource['label']} (Registry B 0x{entry_hex})",
                "status": "candidate_found",
                "priority": str(resource.get("priority") or ("high" if entry in {0x10, 0x11} else "debug")),
                "offset": offset,
                "review_order": 8000 + entry * 10,
                "review_goal": "Registry B 4bpp 전체 타일 시트를 확인/교체",
                "recommended_probe_method": "0x068DF8 Registry B loader trace",
                "future_workspace": str(REGISTRY_B_ZP_OUT.relative_to(ROOT)),
                "expected_text_kind": expected_kind,
                "source": source_kind,
                "compression": compression,
                "notes": (
                    f"{resource.get('notes', '')} "
                    f"테이블 0x{int(resource['table_offset']):08X}, ROM 포인터 0x{int(resource['rom_pointer']):08X}, "
                    f"저장 {compressed_size} bytes, 해제/원본 {decoded_size} bytes, {tile_count} tiles, "
                    f"편집 시트 {edit_tile_count} tiles/{columns}칸 기준. 업로드할 경우 source_1x와 같은 타일 시트 크기/배치를 유지하면 "
                    "8x8 단위로 자동 분해해 같은 순서로 삽입한다."
                ).strip(),
                "subunits": [
                    {
                        "id": f"registry_b_entry_{entry_hex}",
                        "label": f"Registry B entry 0x{entry_hex} / ROM offset 0x{offset:08X}",
                        "first_action": "source_1x PNG를 기준으로 전체 타일 시트를 편집해서 업로드",
                    }
                ],
                "source_preview_path": resource["preview_4x"],
                "source_download_path": resource["source_1x"],
                "replacement_path": "",
                "replacement_target": resource.get("replacement_target", True),
                "replacement_target_reason": resource.get("replacement_target_reason", ""),
                "comparison_notes": "",
                "candidate_gallery": [
                    {
                        "index": "source_1x",
                        "offset": offset,
                        "source": f"{compression}_source_1x",
                        "png_path": resource["source_1x"],
                        "preview_path": resource["source_1x"],
                        "decompressed_size": decoded_size,
                    },
                    {
                        "index": "full_source_1x",
                        "offset": offset,
                        "source": f"{compression}_full_source_1x",
                        "png_path": resource["full_source_1x"],
                        "preview_path": resource["full_source_1x"],
                        "decompressed_size": decoded_size,
                    },
                    {
                        "index": "preview_4x",
                        "offset": offset,
                        "source": f"{compression}_preview_4x",
                        "png_path": resource["preview_4x"],
                        "preview_path": resource["preview_4x"],
                        "decompressed_size": decoded_size,
                    },
                    {
                        "index": "grid_4x",
                        "offset": offset,
                        "source": f"{compression}_grid_4x",
                        "png_path": resource["grid_4x"],
                        "preview_path": resource["grid_4x"],
                        "decompressed_size": decoded_size,
                    },
                    {
                        "index": "tile_contact",
                        "offset": offset,
                        "source": f"{compression}_indexed_contact",
                        "png_path": resource["contact_sheet"],
                        "preview_path": resource["contact_sheet"],
                        "decompressed_size": decoded_size,
                    },
                ],
                "progress_status": "candidate_found",
                "default_review_included": False,
                "tile_columns": columns,
                "tile_count": tile_count,
                "edit_tile_count": edit_tile_count,
                "resource_tile_count": int(resource.get("resource_tile_count") or tile_count),
                "resource_tile_columns": int(resource.get("resource_tile_columns") or columns),
                "tile_indices": tile_indices,
                "raw_byte_length": decoded_size,
                "compressed_size": compressed_size,
                "registry_b_entry": entry,
                "registry_b_entry_hex": f"0x{entry_hex}",
                "registry_b_table_offset": int(resource["table_offset"]),
                "registry_b_table_offset_hex": f"0x{int(resource['table_offset']):08X}",
                "registry_b_destination": resource.get("destination", ""),
                "raw_path": resource["raw_path"],
            }
        )
    return items


def build_expanded_nearby_gallery_items() -> list[dict]:
    summary_path = (
        IMAGE_INVENTORY
        / "runtime_tile_matches"
        / "expanded_nearby_image_candidates"
        / "expanded_nearby_image_candidates.json"
    )
    if not summary_path.exists():
        return []
    summary = load_json(summary_path)
    outputs = summary.get("outputs", {})
    specs = [
        (
            "image:expanded_nearby:screen_order_unique",
            "확장 추출 후보 - 화면순 RLE 요약",
            outputs.get("screen_order_unique", ""),
            f"화면순 RLE 후보 {summary.get('screen_order_unique_count', 0)}개 요약을 검토",
            "tilemap-aware RLE 후보를 offset별 대표 1개로 묶은 참고 시트. 일본어가 보이는 후보만 개별 적용 항목으로 승격한다.",
        ),
        (
            "image:expanded_nearby:field_menu_lz77_broad",
            "확장 추출 후보 - 필드/메뉴 LZ77 넓은 주변",
            outputs.get("field_menu_lz77_broad", ""),
            "0x005323AC/0x0053257C 주변 LZ77 후보를 더 넓게 검토",
            "원본 LZ77 블록을 넓게 훑은 참고 시트. 실제 화면/팔레트/타일맵 검증 후 일본어 이미지 후보만 개별 적용 항목으로 승격한다.",
        ),
    ]
    items: list[dict] = []
    for order, (item_id, label, preview_path, goal, notes) in enumerate(specs, start=1):
        if not preview_path or not (ROOT / preview_path).exists():
            continue
        items.append(
            {
                "item_id": item_id,
                "category_id": "image_review_units",
                "group_id": item_id.replace(":", "_"),
                "label": label,
                "status": "candidate_found",
                "priority": "medium",
                "review_order": 9900 + order,
                "review_goal": goal,
                "recommended_probe_method": "expanded nearby image candidate contact sheet",
                "future_workspace": "confirmed_data/image_inventory/runtime_tile_matches/expanded_nearby_image_candidates",
                "expected_text_kind": "reference_contact_sheet",
                "notes": notes,
                "replacement_target": False,
                "replacement_target_reason": "reference contact sheet; not a direct ROM image block",
                "subunits": [
                    {
                        "id": item_id.rsplit(":", 1)[-1],
                        "label": "확장 후보 시트",
                        "first_action": "일본어가 보이는 후보를 골라 개별 적용 항목으로 승격",
                    }
                ],
                "source_preview_path": preview_path,
                "source_download_path": preview_path,
                "replacement_path": "",
                "comparison_notes": "",
                "candidate_gallery": [
                    {
                        "index": "contact_sheet",
                        "offset": 0,
                        "source": "expanded_nearby_candidates",
                        "png_path": preview_path,
                        "preview_path": preview_path,
                        "decompressed_size": "",
                    }
                ],
                "progress_status": "candidate_found",
                "default_review_included": False,
            }
        )
    return items


def build_runtime_capture_image_items() -> list[dict]:
    capture_root = IMAGE_INVENTORY / "runtime_user_captures"
    match_root = IMAGE_INVENTORY / "runtime_tile_matches"
    if not capture_root.exists():
        return []

    items: list[dict] = []
    order = 8400
    for capture_dir in sorted(capture_root.glob("*")):
        if not capture_dir.is_dir():
            continue
        pngs = sorted(capture_dir.glob("frame_*.png"))
        pngs = [path for path in pngs if "_vram_" not in path.name and "_palette_" not in path.name and "_ioreg_" not in path.name]
        if not pngs:
            continue
        scene_id = capture_dir.name
        screenshot_rel = str(pngs[0].relative_to(ROOT))
        match_dir = match_root / scene_id
        gallery = match_dir / "top_matched_rom_blocks_gallery.png"
        gallery_rel = str(gallery.relative_to(ROOT)) if gallery.exists() else ""
        candidate_gallery = []
        if gallery_rel:
            candidate_gallery.append(
                {
                    "index": 1,
                    "offset": 0,
                    "source": "runtime_match_gallery",
                    "png_path": gallery_rel,
                    "preview_path": gallery_rel,
                    "decompressed_size": "",
                }
            )
        for preview in sorted((match_dir / "matched_previews").glob("*.png"))[:24]:
            candidate_gallery.append(
                {
                    "index": len(candidate_gallery) + 1,
                    "offset": parse_offset_from_preview_name(preview.name),
                    "source": "runtime_matched_block",
                    "png_path": str(preview.relative_to(ROOT)),
                    "preview_path": str(preview.relative_to(ROOT)),
                    "decompressed_size": "",
                }
            )
        items.append(
            {
                "item_id": f"image:runtime_capture:{scene_id}",
                "category_id": "image_review_units",
                "group_id": scene_id,
                "label": f"런타임 캡처 {scene_id}",
                "status": "candidate_found",
                "priority": "high",
                "review_order": order,
                "review_goal": "사용자 저장상태 기반 화면과 매칭된 이미지/타일 후보 검토",
                "recommended_probe_method": "mGBA savestate + pymgba runtime dump",
                "future_workspace": str((IMAGE_INVENTORY / "runtime_user_captures" / scene_id).relative_to(ROOT)),
                "expected_text_kind": "runtime_capture",
                "notes": (
                    "원본 스크린샷은 source_preview_path에, ROM 블록 매칭 갤러리는 후보 PNG 갤러리에 연결했다. "
                    "스크린샷에서 보이는 텍스트가 일반 폰트/런타임 텍스트인지 이미지 워드마크인지 구분한다."
                ),
                "subunits": [
                    {
                        "id": scene_id,
                        "label": "사용자 mGBA 저장상태 캡처",
                        "first_action": "스크린샷과 후보 갤러리를 비교해 이미지 교체 대상만 선별",
                    }
                ],
                "source_preview_path": screenshot_rel,
                "source_download_path": screenshot_rel,
                "replacement_path": "",
                "comparison_notes": "",
                "candidate_gallery": candidate_gallery,
                "progress_status": "candidate_found",
                "default_review_included": False,
            }
        )
        order += 1
    return items


def parse_offset_from_preview_name(name: str) -> int:
    match = re.search(r"_off_([0-9A-Fa-f]{8})", name)
    return int(match.group(1), 16) if match else 0


def build_card_list_label_items() -> list[dict]:
    manifest_path = IMAGE_INVENTORY / "edit_packs" / "card_list_labels" / "manifest.json"
    if not manifest_path.exists():
        return []
    manifest = load_json(manifest_path)
    source_path = manifest.get("source_path", "")
    tile_map_path = manifest.get("tile_map_path", "")
    if not source_path or not tile_map_path:
        return []
    if not (ROOT / source_path).exists() or not (ROOT / tile_map_path).exists():
        return []
    offset = int(manifest["offset"])
    return [
        {
            "item_id": manifest["item_id"],
            "category_id": "image_review_units",
            "group_id": f"card_list_labels_{offset:08X}",
            "label": manifest["label"],
            "status": "candidate_found",
            "priority": "high",
            "review_order": 8487,
            "review_goal": "카드 리스트 중단 ID/POWER 라벨만 한글화",
            "recommended_probe_method": "no_entry8_latest_ss3 BG1 RLE 0x003A3540 focused screen-order tile_map label crop",
            "future_workspace": str((IMAGE_INVENTORY / "edit_packs" / "card_list_labels").relative_to(ROOT)),
            "expected_text_kind": "card_list_id_power_labels",
            "source": "rle_screen_order_focus",
            "notes": (
                "카드 리스트 화면순 RLE 0x003A3540에서 ID/POWER 라벨 배너만 분리한 안전 편집 항목이다. "
                "같은 RLE 블록의 오른쪽 책갈피 편집과 함께 누적 적용되도록 현재 ROM payload를 기준으로 이 영역의 타일만 바꾼다."
            ),
            "subunits": [
                {
                    "id": f"rle_screen_order_focus_{offset:08X}_card_list_id_power",
                    "label": f"ROM offset 0x{offset:08X} / ID POWER",
                    "first_action": "ID/POWER 라벨을 필요한 한국어/영문 표기로 교체",
                }
            ],
            "source_preview_path": source_path,
            "source_download_path": source_path,
            "tile_map_path": tile_map_path,
            "replacement_path": manifest.get("replacement_path", ""),
            "replacement_target": True,
            "replacement_target_reason": "",
            "replacement_payload_base": manifest.get("replacement_payload_base", "current") or "current",
            "replacement_source_color_map": True,
            "replacement_verify_source_noop": bool(manifest.get("replacement_verify_source_noop", False)),
            "comparison_notes": "",
            "candidate_gallery": [
                {
                    "index": "source_1x",
                    "offset": offset,
                    "source": "focused_screen_order_card_list_labels_1x",
                    "png_path": source_path,
                    "preview_path": source_path,
                    "decompressed_size": manifest.get("matched_tile_count", ""),
                },
                {
                    "index": "editable_4x",
                    "offset": offset,
                    "source": "focused_screen_order_card_list_labels_4x",
                    "png_path": manifest.get("editable_path", ""),
                    "preview_path": manifest.get("editable_path", ""),
                    "decompressed_size": manifest.get("matched_tile_count", ""),
                },
            ],
            "source_text": manifest.get("source_text", "ID / POWER"),
            "suggested_korean": manifest.get("suggested_korean", "ID / 파워"),
            "progress_status": "candidate_found",
            "default_review_included": False,
        }
    ]


def build_card_list_power_label_items() -> list[dict]:
    manifest_path = IMAGE_INVENTORY / "edit_packs" / "card_list_power_labels" / "manifest.json"
    if not manifest_path.exists():
        return []
    manifest = load_json(manifest_path)
    items: list[dict] = []
    for entry in manifest.get("items", []):
        source_path = entry.get("source_path", "")
        tile_map_path = entry.get("tile_map_path", "")
        if not source_path or not tile_map_path:
            continue
        if not (ROOT / source_path).exists() or not (ROOT / tile_map_path).exists():
            continue
        offset = int(entry["offset"])
        items.append(
            {
                "item_id": entry["item_id"],
                "category_id": "image_review_units",
                "group_id": f"card_list_power_{offset:08X}",
                "label": entry["label"],
                "status": "candidate_found",
                "priority": "high",
                "review_order": int(entry.get("review_order", 4080)),
                "review_goal": "카드 리스트 POWER 라벨 주변 작은 영역만 한글화",
                "recommended_probe_method": "no_entry8_latest_ss3 BG1 card-list RLE focused POWER bbox",
                "future_workspace": str((IMAGE_INVENTORY / "edit_packs" / "card_list_power_labels").relative_to(ROOT)),
                "expected_text_kind": "card_list_power_label_focus",
                "source": "rle_screen_order_focus",
                "notes": (
                    "기존 전체 카드 리스트 RLE 변형 항목 대신 POWER 라벨 주변 46x28px 박스만 분리한 항목이다. "
                    "업로드/적용 속도를 줄이기 위해 이 작은 crop의 tile_map만 사용한다."
                ),
                "subunits": [
                    {
                        "id": f"rle_screen_order_focus_{offset:08X}_power",
                        "label": f"ROM offset 0x{offset:08X} / POWER",
                        "first_action": "POWER 라벨 영역만 수정해서 업로드",
                    }
                ],
                "source_preview_path": source_path,
                "source_download_path": source_path,
                "tile_map_path": tile_map_path,
                "replacement_path": entry.get("replacement_path", ""),
                "replacement_target": True,
                "replacement_target_reason": "",
                "replacement_payload_base": entry.get("replacement_payload_base", "source_raw") or "source_raw",
                "replacement_source_color_map": bool(entry.get("replacement_source_color_map", True)),
                "replacement_verify_source_noop": bool(entry.get("replacement_verify_source_noop", False)),
                "comparison_notes": "",
                "candidate_gallery": [
                    {
                        "index": "source_1x",
                        "offset": offset,
                        "source": "focused_card_list_power_1x",
                        "png_path": source_path,
                        "preview_path": source_path,
                        "decompressed_size": entry.get("matched_tile_count", ""),
                    },
                    {
                        "index": "editable_4x",
                        "offset": offset,
                        "source": "focused_card_list_power_4x",
                        "png_path": entry.get("editable_path", ""),
                        "preview_path": entry.get("editable_path", ""),
                        "decompressed_size": entry.get("matched_tile_count", ""),
                    },
                ],
                "source_text": entry.get("source_text", "POWER"),
                "suggested_korean": entry.get("suggested_korean", "파워"),
                "progress_status": "candidate_found",
                "default_review_included": False,
            }
        )
    return items


def build_card_book_right_tab_items() -> list[dict]:
    manifest_path = IMAGE_INVENTORY / "edit_packs" / "card_book_right_tabs" / "manifest.json"
    if not manifest_path.exists():
        return []
    manifest = load_json(manifest_path)
    source_path = manifest.get("editable_path", "")
    tile_map_path = manifest.get("tile_map_path", "")
    if not source_path or not tile_map_path:
        return []
    if not (ROOT / source_path).exists() or not (ROOT / tile_map_path).exists():
        return []
    offset = int(manifest["offset"])
    common = {
        "category_id": "image_review_units",
        "status": "candidate_found",
        "priority": "high",
        "future_workspace": str((IMAGE_INVENTORY / "edit_packs" / "card_book_right_tabs").relative_to(ROOT)),
        "expected_text_kind": "card_book_right_category_tabs",
        "source": "rle_screen_order_focus",
        "replacement_target": True,
        "replacement_target_reason": "",
        "comparison_notes": "",
        "replacement_payload_base": manifest.get("replacement_payload_base", "source_raw") or "source_raw",
        "replacement_source_color_map": True,
        "replacement_verify_source_noop": True,
        "replacement_direct_rle_tiles": manifest.get("replacement_direct_rle_tiles", []),
        "progress_status": "candidate_found",
        "default_review_included": False,
    }
    items = [
        {
            **common,
            "item_id": manifest["item_id"],
            "group_id": f"card_book_right_tabs_{offset:08X}",
            "label": manifest["label"],
            "review_order": 8488,
            "review_goal": "ss6~ss9 카드 책자 오른쪽 세로 탭 4개만 한글화",
            "recommended_probe_method": "current_review ss6~ss9 BG1 RLE 0x003A3540 focused screen-order tile_map",
            "notes": (
                "기존 카드 리스트 전체 항목 0x003A3540에서 오른쪽 책자 탭만 분리한 안전 편집 항목이다. "
                "같은 RLE 원본을 쓰므로 전체 카드 리스트 항목과 같이 업로드하면 이 오른쪽 탭 전용 항목이 뒤에서 다시 적용된다."
            ),
            "subunits": [
                {
                    "id": f"rle_screen_order_focus_{offset:08X}",
                    "label": f"ROM offset 0x{offset:08X}",
                    "first_action": "金属/石/自然/無機 탭을 금속/돌/자연/무기로 교체",
                }
            ],
            "source_preview_path": source_path,
            "source_download_path": source_path,
            "tile_map_path": tile_map_path,
            "replacement_path": manifest.get("replacement_path", ""),
            "candidate_gallery": [
                {
                    "index": "editable",
                    "offset": offset,
                    "source": "focused_screen_order_tabs",
                    "png_path": source_path,
                    "preview_path": source_path,
                    "decompressed_size": manifest.get("matched_tile_count", ""),
                },
                {
                    "index": "source_1x",
                    "offset": offset,
                    "source": "focused_screen_order_tabs_1x",
                    "png_path": manifest.get("source_path", ""),
                    "preview_path": manifest.get("source_path", ""),
                    "decompressed_size": manifest.get("matched_tile_count", ""),
                },
            ],
            "source_text": manifest.get("source_text", "金属 / 石 / 自然 / 無機"),
            "suggested_korean": manifest.get("suggested_korean", "금속 / 돌 / 자연 / 무기"),
        }
    ]
    for tab in manifest.get("individual_tabs", []):
        tab_source = tab.get("editable_path", "")
        tab_tile_map = tab.get("tile_map_path", "")
        if not tab_source or not tab_tile_map:
            continue
        if not (ROOT / tab_source).exists() or not (ROOT / tab_tile_map).exists():
            continue
        items.append(
            {
                **common,
                "item_id": tab["item_id"],
                "group_id": f"card_book_right_tabs_{offset:08X}_individual",
                "label": tab["label"],
                "review_order": int(tab.get("review_order", 8489)),
                "review_goal": "카드 책자 오른쪽 세로 탭을 개별 PNG로 한글화",
                "recommended_probe_method": "0x003A3540 active-bookmark screen-order tile_map individual front tab crop",
                "notes": (
                    "이 탭이 앞쪽으로 나온 세이브 상태에서 다시 추출한 개별 편집 항목이다. "
                    "뒤쪽 책갈피에 가려진 상태가 아니므로 글자가 잘리지 않는다. "
                    "같은 0x003A3540 RLE 블록에 누적 적용되도록 현재 ROM payload를 기준으로 이 영역의 타일만 바꾼다."
                ),
                "subunits": [
                    {
                        "id": f"rle_screen_order_focus_{offset:08X}_{tab['key']}",
                        "label": f"ROM offset 0x{offset:08X} / {tab['source_text']}",
                        "first_action": f"{tab['source_text']} 탭을 {tab.get('suggested_korean', '')}로 교체",
                    }
                ],
                "source_preview_path": tab_source,
                "source_download_path": tab_source,
                "tile_map_path": tab_tile_map,
                "replacement_path": tab.get("replacement_path", ""),
                "replacement_payload_base": tab.get("replacement_payload_base", "current"),
                "replacement_verify_source_noop": bool(tab.get("replacement_verify_source_noop", False)),
                "candidate_gallery": [
                    {
                        "index": "editable",
                        "offset": offset,
                        "source": "focused_screen_order_tab",
                        "png_path": tab_source,
                        "preview_path": tab_source,
                        "decompressed_size": tab.get("matched_tile_count", ""),
                    },
                    {
                        "index": "source_1x",
                        "offset": offset,
                        "source": "focused_screen_order_tab_1x",
                        "png_path": tab.get("source_path", ""),
                        "preview_path": tab.get("source_path", ""),
                        "decompressed_size": tab.get("matched_tile_count", ""),
                    },
                ],
                "source_text": tab.get("source_text", ""),
                "suggested_korean": tab.get("suggested_korean", ""),
            }
        )
    return items


def build_card_page_count_items() -> list[dict]:
    manifest_path = IMAGE_INVENTORY / "edit_packs" / "card_page_count" / "manifest.json"
    if not manifest_path.exists():
        return []
    manifest = load_json(manifest_path)
    source_path = manifest.get("editable_path", "")
    tile_map_path = manifest.get("tile_map_path", "")
    if not source_path or not tile_map_path:
        return []
    if not (ROOT / source_path).exists() or not (ROOT / tile_map_path).exists():
        return []
    offset = int(manifest["offset"])
    return [
        {
            "item_id": manifest["item_id"],
            "category_id": "image_review_units",
            "group_id": f"card_page_count_{offset:08X}",
            "label": manifest["label"],
            "status": "candidate_found",
            "priority": "high",
            "review_order": 8492,
            "review_goal": "ss6 카드 상세 화면의 작은 1枚目 페이지 표기만 한글화",
            "recommended_probe_method": "current_review ss6 BG1 RLE 0x003A206C focused screen-order tile_map",
            "future_workspace": str((IMAGE_INVENTORY / "edit_packs" / "card_page_count").relative_to(ROOT)),
            "expected_text_kind": "card_detail_page_count",
            "source": "rle_screen_order_focus",
            "notes": (
                "카드 상세 화면 왼쪽 카드 프레임 하단의 1枚目 부분만 분리한 안전 편집 항목이다. "
                "업로드 시 0x003A206C RLE에 화면순 tile_map으로 되돌려 적용한다."
            ),
            "subunits": [
                {
                    "id": f"rle_screen_order_focus_{offset:08X}",
                    "label": f"ROM offset 0x{offset:08X}",
                    "first_action": "1枚目을 1장째 등 한국어 표기로 교체",
                }
            ],
            "source_preview_path": source_path,
            "source_download_path": source_path,
            "tile_map_path": tile_map_path,
            "replacement_path": manifest.get("replacement_path", ""),
            "replacement_target": True,
            "replacement_target_reason": "",
            "comparison_notes": "",
            "replacement_payload_base": manifest.get("replacement_payload_base", ""),
            "replacement_direct_rle_tiles": manifest.get("replacement_direct_rle_tiles", []),
            "candidate_gallery": [
                {
                    "index": "editable",
                    "offset": offset,
                    "source": "focused_screen_order_page_count",
                    "png_path": source_path,
                    "preview_path": source_path,
                    "decompressed_size": manifest.get("matched_tile_count", ""),
                },
                {
                    "index": "source_1x",
                    "offset": offset,
                    "source": "focused_screen_order_page_count_1x",
                    "png_path": manifest.get("source_path", ""),
                    "preview_path": manifest.get("source_path", ""),
                    "decompressed_size": manifest.get("matched_tile_count", ""),
                },
            ],
            "source_text": manifest.get("source_text", "1枚目"),
            "suggested_korean": manifest.get("suggested_korean", "1장째"),
            "progress_status": "candidate_found",
            "default_review_included": False,
        }
    ]


def build_runtime_rle_screen_order_items() -> list[dict]:
    manifest_path = IMAGE_INVENTORY / "runtime_rle_screen_order" / "screen_order_manifest.json"
    if not manifest_path.exists():
        return []

    include_keys = {
        ("current_review_ss2", "frame_000002", 0, 0x003ABB9C),
        ("no_entry8_latest_ss1", "frame_007084", 0, 0x003AF23C),
        ("no_entry8_latest_ss3", "frame_009730", 1, 0x003A3540),
        ("timeline_with_rle", "frame_001200", 0, 0x007E0000),
    }
    labels = {
        0x003ABB9C: "화면순 RLE 편집 - OK?/はい/いいえ 확인 팝업",
        0x003AF23C: "화면순 RLE 편집 - 연성/사용/버리기/돌아가기 팝업",
        0x003A206C: "화면순 RLE 편집 - 전투 카드 2枚 UI",
        0x003A3540: "화면순 RLE 편집 - 카드 리스트 いいえ UI",
        0x003A5E50: "화면순 RLE 편집 - 카드 리스트 いいえ UI 변형 1",
        0x003A6E24: "화면순 RLE 편집 - 카드 리스트 いいえ UI 변형 2",
        0x003A7C3C: "화면순 RLE 편집 - 카드 리스트 いいえ UI 변형 3",
        0x003A8894: "화면순 RLE 편집 - 카드 리스트 いいえ UI 변형 4",
        0x003A9624: "화면순 RLE 편집 - 카드 리스트 いいえ UI 변형 5",
        0x003AA4C0: "화면순 RLE 편집 - 카드 리스트 いいえ UI 변형 6",
        0x00186AE8: "화면순 RLE 편집 - 전투 HUD 소형 숫자",
        0x007E0000: "화면순 RLE 편집 - 타이틀 로고/부제",
    }
    goals = {
        0x003ABB9C: "전투 확인 팝업의 일본어 はい/いいえ를 한국어 이미지로 교체",
        0x003AF23C: "실제 화면 배치로 재조립된 팝업 본문을 한국어 이미지로 교체",
        0x003A206C: "전투 카드 패널의 일본어 수량 표기 2枚를 화면순으로 검토",
        0x003A3540: "카드 리스트 프레임의 일본어 いいえ UI 타일을 화면순으로 검토",
        0x003A5E50: "카드 리스트 RLE 변형의 일본어 いいえ UI 타일을 화면순으로 검토",
        0x003A6E24: "카드 리스트 RLE 변형의 일본어 いいえ UI 타일을 화면순으로 검토",
        0x003A7C3C: "카드 리스트 RLE 변형의 일본어 いいえ UI 타일을 화면순으로 검토",
        0x003A8894: "카드 리스트 RLE 변형의 일본어 いいえ UI 타일을 화면순으로 검토",
        0x003A9624: "카드 리스트 RLE 변형의 일본어 いいえ UI 타일을 화면순으로 검토",
        0x003AA4C0: "카드 리스트 RLE 변형의 일본어 いいえ UI 타일을 화면순으로 검토",
        0x00186AE8: "작은 HUD 숫자/표시 타일을 한글화 또는 영문판 유지 기준으로 검토",
        0x007E0000: "타이틀 일본어 로고와 부제 영역을 실제 배치에 가까운 PNG로 편집",
    }
    source_texts = {
        0x003ABB9C: "OK? / はい / いいえ",
        0x003AF23C: "錬成 / つかう / すてる / もどる",
        0x003A206C: "2枚",
        0x003A3540: "いいえ",
        0x003A5E50: "いいえ",
        0x003A6E24: "いいえ",
        0x003A7C3C: "いいえ",
        0x003A8894: "いいえ",
        0x003A9624: "いいえ",
        0x003AA4C0: "いいえ",
        0x007E0000: "鋼の錬金術師 / 迷走の輪舞曲",
    }
    suggested_korean = {
        0x003ABB9C: "OK? / 예 / 아니요",
        0x003AF23C: "연성 / 사용 / 버리기 / 돌아가기",
        0x003A206C: "2장",
        0x003A3540: "아니요",
        0x003A5E50: "아니요",
        0x003A6E24: "아니요",
        0x003A7C3C: "아니요",
        0x003A8894: "아니요",
        0x003A9624: "아니요",
        0x003AA4C0: "아니요",
        0x007E0000: "강철의 연금술사 / 미주의 윤무곡",
    }

    items: list[dict] = []
    for order, block in enumerate(load_json(manifest_path), start=1):
        offset = int(block["offset"])
        key = (block.get("scene", ""), block.get("frame", ""), int(block.get("bg", -1)), offset)
        if key not in include_keys:
            continue
        if block.get("replacement_target") is False:
            continue
        reference_path = block.get("reference_preview_path") or block.get("context_preview_path", "")
        download_path = block.get("source_download_path") or block.get("editable_preview_path", "")
        tile_map_path = block.get("tile_map_path", "")
        preview_path = download_path
        if not preview_path or not download_path or not tile_map_path:
            continue
        if not (ROOT / preview_path).exists() or not (ROOT / download_path).exists() or not (ROOT / tile_map_path).exists():
            continue
        scene = block.get("scene", "")
        frame = block.get("frame", "")
        bg = int(block.get("bg", 0))
        items.append(
            {
                "item_id": f"image:rle_screen_order:{scene}:{frame}:bg{bg}:{offset:08X}",
                "category_id": "image_review_units",
                "group_id": f"rle_screen_order_{scene}_{frame}_bg{bg}_{offset:08X}",
                "label": labels.get(offset, f"화면순 RLE 편집 - 0x{offset:08X}"),
                "status": "candidate_found",
                "priority": "high",
                "review_order": 8550 + order,
                "review_goal": goals.get(offset, "실제 화면 tilemap 순서로 재조립된 RLE 타일을 편집"),
                "recommended_probe_method": "runtime BG tilemap screen-order rebuild + tile_map-aware RLE apply",
                "future_workspace": block.get("workspace", "confirmed_data/image_inventory/runtime_rle_screen_order"),
                "expected_text_kind": "rle_screen_order_editable_image",
                "notes": (
                    f"scene={scene}, frame={frame}, bg={bg}, matched_tiles={block.get('matched_tile_count')}. "
                    "원본/다운로드 PNG는 ROM RLE 타일을 화면순으로 재조립한 편집용 PNG다. "
                    f"런타임 context crop은 참고 전용이며 편집 원본에서 제외한다: {reference_path}. "
                    "업로드 시 tile_map.json을 사용해 "
                    "원래 RLE 타일 순서로 되돌려 압축하므로, 일반 분석용 스크린샷보다 실제 교체 가능성이 높다. "
                    "단, 같은 원본 타일이 여러 화면 위치에 반복 사용된 경우 각 위치를 서로 다르게 바꾸는 것은 아직 제한된다."
                ),
                "replacement_target": True,
                "replacement_target_reason": "",
                "subunits": [
                    {
                        "id": f"rle_screen_order_{offset:08X}",
                        "label": f"ROM offset 0x{offset:08X}",
                        "first_action": "다운로드 PNG를 수정해 업로드하고 리뷰 ROM에서 실제 화면 확인",
                    }
                ],
                "source_preview_path": preview_path,
                "source_download_path": download_path,
                "reference_preview_path": reference_path,
                "tile_map_path": tile_map_path,
                "source_text": source_texts.get(offset, ""),
                "suggested_korean": suggested_korean.get(offset, ""),
                "replacement_payload_base": "source_raw",
                "replacement_source_color_map": True,
                "replacement_verify_source_noop": True,
                "replacement_path": "",
                "comparison_notes": "",
                "candidate_gallery": [
                    {
                        "index": "editable",
                        "offset": offset,
                        "source": "runtime_screen_order_editable_tiles",
                        "png_path": download_path,
                        "preview_path": download_path,
                        "decompressed_size": block.get("matched_tile_count"),
                    },
                ],
                "progress_status": "candidate_found",
                "default_review_included": False,
            }
        )
    return items


def build_curated_runtime_image_items() -> list[dict]:
    english_rle_report_path = (
        IMAGE_INVENTORY
        / "english_patch_diff"
        / "rle_same_offset"
        / "notes"
        / "english_patch_rle_same_offset_diff.json"
    )
    english_rle_by_offset = {}
    if english_rle_report_path.exists():
        english_rle_by_offset = {
            int(item["offset"]): item
            for item in load_json(english_rle_report_path).get("items", [])
        }

    battle_command_manifest = load_json_if_exists(
        IMAGE_INVENTORY / "edit_packs" / "battle_command_buttons" / "manifest.json",
        {},
    )
    battle_command_blocks = []
    for index, command in enumerate(battle_command_manifest.get("items", []), start=1):
        offset = int(command["offset"])
        battle_command_blocks.append(
            {
                "item_id": command["item_id"],
                "group_id": f"battle_command_button_{offset:08X}",
                "label": command["label"],
                "priority": "high",
                "review_order": 8480 + index,
                "review_goal": "사용자 전투 저장상태에서 확인한 하단 커맨드 raw 타일 버튼 한글화",
                "recommended_probe_method": f"runtime BG1 tilemap slot 0x0211-0x021C exact ROM raw hit / offset 0x{offset:08X}",
                "expected_text_kind": "battle_command_raw4bpp_wordmark",
                "notes": (
                    "전투 하단 커맨드는 문자열이 아니라 48x16px raw 4bpp 타일 블록이다. "
                    "게임이 이 0x180바이트 블록을 BG1 VRAM 타일 슬롯 0x0211-0x021C에 복사한다."
                ),
                "offset": offset,
                "source": "raw4bpp",
                "preview_path": command["editable_path"],
                "source_1x_path": command["source_path"],
                "subunit_id": f"raw4bpp_{offset:08X}",
                "subunit_label": f"ROM offset 0x{offset:08X}",
                "first_action": f"{command['source_text']} 버튼을 {command['suggested_korean']} 픽셀 타일로 교체",
                "tile_columns": int(command["tile_columns"]),
                "raw_byte_length": int(command["raw_byte_length"]),
                "source_text": command["source_text"],
                "suggested_korean": command["suggested_korean"],
            }
        )

    curated_blocks = battle_command_blocks + [
        {
            "item_id": "image:field_label_0053257C",
            "group_id": "field_label_0053257C",
            "label": "필드/카드 라벨 アイテム 이미지 블록",
            "priority": "high",
            "review_order": 8491,
            "review_goal": "ss2 런타임 매칭으로 확인된 필드/카드 라벨 이미지 한글화 후보 검토",
            "recommended_probe_method": "mGBA savestate runtime match / offset 0x0053257C",
            "expected_text_kind": "field_card_label_wordmark",
            "notes": (
                "사용자 ss2 기준 runtime_tile_matches/no_entry8_ss2 갤러리 마지막 후보에서 확인한 LZ77 이미지 블록. "
                "텍스트가 폰트 문자열이 아니라 타일 이미지에 구워진 라벨로 보여, 캡처 화면이 아닌 ROM 블록 단위로 등록한다."
            ),
            "offset": 0x0053257C,
            "source": "lz77",
            "preview_path": "confirmed_data/image_inventory/runtime_tile_matches/no_entry8_ss2/matched_previews/lz77_0295_off_0053257C.png",
            "subunit_id": "lz77_0053257C",
            "subunit_label": "ROM offset 0x0053257C",
            "first_action": "アイテム 라벨의 실제 화면 배치를 확인한 뒤 한국어 교체 이미지 준비",
        },
        {
            "item_id": "image:battle_menu_wordmarks_003A206C",
            "group_id": "battle_menu_wordmarks_003A206C",
            "label": "전투 메뉴 워드마크 ALCHEMY/SKILL/ITEM/CARD/NETWORK 블록",
            "priority": "medium",
            "review_order": 8492,
            "review_goal": "ss3 런타임 매칭으로 확인된 전투 메뉴 영어 워드마크 참고",
            "recommended_probe_method": "mGBA savestate runtime match / RLE offset 0x003A206C",
            "expected_text_kind": "battle_menu_wordmark",
            "notes": (
                "사용자 ss3 기준 실제 전투 화면에서 쓰이는 RLE 이미지 블록. "
                "영어 워드마크는 번역 대상에서 제외하므로 참고용으로만 둔다. 일본어 `2枚`는 화면순 0x003A206C 항목에서 별도 처리한다."
            ),
            "offset": 0x003A206C,
            "source": "rle",
            "preview_path": "confirmed_data/image_inventory/runtime_tile_matches/no_entry8_ss3/matched_previews/rle_0831_off_003A206C.png",
            "display_preview_path": "confirmed_data/image_inventory/gui_display_previews/rle_0831_off_003A206C_display.png",
            "subunit_id": "rle_003A206C",
            "subunit_label": "ROM offset 0x003A206C",
            "first_action": "영어 워드마크는 유지하고 일본어가 있는 화면순 항목만 별도 검토",
            "replacement_target": False,
            "replacement_target_reason": "raw/runtime-match preview only; use the screen-order 0x003A206C item for actual editing",
        },
        {
            "item_id": "image:field_status_label_00532764",
            "group_id": "field_status_label_00532764",
            "label": "필드/메뉴 라벨 ステータス 이미지 블록",
            "priority": "high",
            "review_order": 8493,
            "review_goal": "ss 기반 후보 주변 탐색으로 발견한 ステータス 이미지 라벨 한글화 후보 검토",
            "recommended_probe_method": "neighbor scan around ss runtime matches / offset 0x00532764",
            "expected_text_kind": "field_menu_label_wordmark",
            "notes": (
                "0x005323AC/0x0053257C 주변 LZ77 블록을 함께 펼쳐 확인한 추가 후보. "
                "사용자 저장상태에서 하나가 걸리면 같은 근처 라벨 묶음도 함께 검토한다는 정책의 첫 적용 사례다."
            ),
            "offset": 0x00532764,
            "source": "lz77_neighbor_scan",
            "preview_path": "confirmed_data/image_inventory/runtime_tile_matches/curated_neighborhoods/lz77_0296_off_00532764.png",
            "subunit_id": "lz77_00532764",
            "subunit_label": "ROM offset 0x00532764",
            "first_action": "ステータス 라벨을 한국어 메뉴 라벨로 교체 가능한지 폭 확인",
        },
        {
            "item_id": "image:field_save_label_0053293C",
            "group_id": "field_save_label_0053293C",
            "label": "필드/메뉴 라벨 セーブ 이미지 블록",
            "priority": "high",
            "review_order": 8494,
            "review_goal": "ss 기반 후보 주변 탐색으로 발견한 セーブ 이미지 라벨 한글화 후보 검토",
            "recommended_probe_method": "neighbor scan around ss runtime matches / offset 0x0053293C",
            "expected_text_kind": "field_menu_label_wordmark",
            "notes": (
                "0x005323AC/0x0053257C 주변 LZ77 블록을 함께 펼쳐 확인한 추가 후보. "
                "GUI에는 대량 시트가 아니라 이처럼 실제 텍스트가 보이는 개별 ROM 블록만 등록한다."
            ),
            "offset": 0x0053293C,
            "source": "lz77_neighbor_scan",
            "preview_path": "confirmed_data/image_inventory/runtime_tile_matches/curated_neighborhoods/lz77_0297_off_0053293C.png",
            "subunit_id": "lz77_0053293C",
            "subunit_label": "ROM offset 0x0053293C",
            "first_action": "セーブ 라벨을 한국어 메뉴 라벨로 교체 가능한지 폭 확인",
        },
    ]

    items: list[dict] = []
    for order, block in enumerate(curated_blocks, start=1):
        preview_path = block["preview_path"]
        if not (ROOT / preview_path).exists():
            continue
        display_preview_path = block.get("display_preview_path", "")
        if display_preview_path and not (ROOT / display_preview_path).exists():
            display_preview_path = ""
        source_preview_path = display_preview_path or preview_path
        candidate_gallery = [
            {
                "index": order,
                "offset": block["offset"],
                "source": block["source"],
                "png_path": preview_path,
                "preview_path": preview_path,
                "decompressed_size": block.get("raw_byte_length", ""),
            }
        ]
        if block.get("source_1x_path") and (ROOT / block["source_1x_path"]).exists():
            candidate_gallery.append(
                {
                    "index": "source_1x",
                    "offset": block["offset"],
                    "source": f"{block['source']}_source_1x",
                    "png_path": block["source_1x_path"],
                    "preview_path": block["source_1x_path"],
                    "decompressed_size": block.get("raw_byte_length", ""),
                }
            )
        notes = block["notes"]
        english_reference = english_rle_by_offset.get(block["offset"]) if block["source"] == "rle" else None
        if english_reference:
            candidate_gallery.append(
                {
                    "index": "english_reference",
                    "offset": block["offset"],
                    "source": "english_patch_same_offset_rle",
                    "png_path": english_reference.get("en_scaled_png", english_reference.get("en_png", "")),
                    "preview_path": english_reference.get("en_scaled_png", english_reference.get("en_png", "")),
                    "decompressed_size": english_reference.get("en_decompressed_size"),
                    "jp_reference_path": english_reference.get("jp_scaled_png", english_reference.get("jp_png", "")),
                }
            )
            notes += " 영문판 same-offset RLE diff가 있으므로 영문판 배치/축약을 우선 참고한다."
        item_payload = {
                "item_id": block["item_id"],
                "category_id": "image_review_units",
                "group_id": block["group_id"],
                "label": block["label"],
                "status": "candidate_found",
                "priority": block["priority"],
                "review_order": block["review_order"],
                "review_goal": block["review_goal"],
                "recommended_probe_method": block["recommended_probe_method"],
                "future_workspace": str((IMAGE_INVENTORY / "runtime_tile_matches").relative_to(ROOT)),
                "expected_text_kind": block["expected_text_kind"],
                "source": block["source"],
                "notes": notes,
                "subunits": [
                    {
                        "id": block["subunit_id"],
                        "label": block["subunit_label"],
                        "first_action": block["first_action"],
                    }
                ],
                "source_preview_path": source_preview_path,
                "source_download_path": preview_path,
                "replacement_path": "",
                "replacement_target": block.get("replacement_target", True),
                "replacement_target_reason": block.get("replacement_target_reason", ""),
                "comparison_notes": "",
                "candidate_gallery": candidate_gallery,
                "progress_status": "candidate_found",
                "default_review_included": False,
            }
        if block.get("tile_columns"):
            item_payload["tile_columns"] = block["tile_columns"]
        if block.get("raw_byte_length"):
            item_payload["raw_byte_length"] = block["raw_byte_length"]
        if block.get("source_text"):
            item_payload["source_text"] = block["source_text"]
        if block.get("suggested_korean"):
            item_payload["suggested_korean"] = block["suggested_korean"]
        items.append(item_payload)
    return items


def build_english_patch_image_items() -> list[dict]:
    report_path = IMAGE_INVENTORY / "english_patch_diff" / "notes" / "english_patch_lz77_diff_report.json"
    if not report_path.exists():
        return []
    report = load_json(report_path)
    tracked_blocks = {
        0x005323AC: {
            "item_id": "image:field_alchemy_label_005323AC",
            "group_id": "field_alchemy_label_005323AC",
            "label": "필드/카드 라벨 錬成 이미지 블록",
            "priority": "high",
            "review_order": 8490,
            "review_goal": "ss1 런타임 매칭으로 확인된 錬成 이미지 블록을 한글화 후보로 검토",
            "recommended_probe_method": "mGBA savestate runtime match + English patch LZ77 diff / offset 0x005323AC",
            "expected_text_kind": "field_card_label_wordmark",
            "notes": (
                "사용자 ss1 기준 runtime_tile_matches/no_entry8_ss1 갤러리 마지막 후보에서 보인 실제 ROM 이미지 블록. "
                "일본판은 錬成, 영문판은 Item으로 바뀌어 있어 타일 이미지 교체 대상으로 확정한다. "
                "캡처 화면 자체를 등록하지 않고 이처럼 매칭된 ROM 블록만 GUI에 노출한다."
            ),
            "subunit_id": "lz77_005323AC",
            "subunit_label": "ROM offset 0x005323AC",
            "first_action": "일본판/영문판/ss1 매칭 PNG를 비교하고 한국어 라벨 배치 검토",
            "runtime_preview": "confirmed_data/image_inventory/runtime_tile_matches/no_entry8_ss1/matched_previews/lz77_0294_off_005323AC.png",
        },
        0x00534874: {
            "item_id": "image:english_battle_hud_small_font",
            "group_id": "english_battle_hud_small_font",
            "label": "영문판 전투 HUD 소형 글자 블록",
            "priority": "high",
            "review_order": 8500,
            "review_goal": "영문판에서 가져온 전투 HUD 소형 글자 블록을 한글화 가능 후보로 유지",
            "recommended_probe_method": "English patch LZ77 diff / offset 0x00534874",
            "expected_text_kind": "battle_hud_small_font",
            "notes": (
                "기존에 영문판 블록으로 대체한 전투 HUD 작은 글자 영역. "
                "공간이 매우 작아 영문판 유지가 안전하지만, 한글 축약 글꼴/타일 편집 가능성을 검토한다."
            ),
            "subunit_id": "lz77_00534874",
            "subunit_label": "ROM offset 0x00534874",
            "first_action": "영문판/일본판 PNG를 비교하고 한글화 가능 영역 확인",
            "runtime_preview": "",
            "replacement_target": False,
            "replacement_target_reason": "reference-only English patch small-font block; not a direct Korean image replacement target",
        },
    }
    items: list[dict] = []
    for diff in report.get("items", []):
        offset = int(diff["offset"])
        config = tracked_blocks.get(offset)
        if not config:
            continue
        en_png = diff.get("en_png", "")
        jp_png = diff.get("jp_png", "")
        runtime_preview = config.get("runtime_preview", "")
        if runtime_preview and not (ROOT / runtime_preview).exists():
            runtime_preview = ""
        preview_path = runtime_preview or (en_png if en_png and (ROOT / en_png).exists() else jp_png)
        candidate_gallery = []
        if runtime_preview:
            candidate_gallery.append(
                {
                    "index": 1,
                    "offset": offset,
                    "source": "runtime_matched_block",
                    "png_path": runtime_preview,
                    "preview_path": runtime_preview,
                    "decompressed_size": diff.get("jp_decompressed_size"),
                }
            )
        if jp_png and (ROOT / jp_png).exists():
            candidate_gallery.append(
                {
                    "index": len(candidate_gallery) + 1,
                    "offset": offset,
                    "source": "jp_original",
                    "png_path": jp_png,
                    "preview_path": jp_png,
                    "decompressed_size": diff.get("jp_decompressed_size"),
                }
            )
        if en_png and (ROOT / en_png).exists():
            candidate_gallery.append(
                {
                    "index": len(candidate_gallery) + 1,
                    "offset": offset,
                    "source": "english_patch",
                    "png_path": en_png,
                    "preview_path": en_png,
                    "decompressed_size": diff.get("en_decompressed_size"),
                }
            )
        items.append(
            {
                "item_id": config["item_id"],
                "category_id": "image_review_units",
                "group_id": config["group_id"],
                "label": config["label"],
                "status": "candidate_found",
                "priority": config["priority"],
                "review_order": config["review_order"],
                "review_goal": config["review_goal"],
                "recommended_probe_method": config["recommended_probe_method"],
                "future_workspace": "confirmed_data/image_inventory/english_patch_diff",
                "expected_text_kind": config["expected_text_kind"],
                "notes": config["notes"],
                "subunits": [
                    {
                        "id": config["subunit_id"],
                        "label": config["subunit_label"],
                        "first_action": config["first_action"],
                    }
                ],
                "source_preview_path": preview_path,
                "source_download_path": preview_path,
                "replacement_path": "",
                "replacement_target": config.get("replacement_target", True),
                "replacement_target_reason": config.get("replacement_target_reason", ""),
                "comparison_notes": "",
                "candidate_gallery": candidate_gallery,
                "progress_status": "candidate_found",
                "default_review_included": False,
            }
        )
    return items


def build_curated_rle_fragment_items() -> list[dict]:
    manifest_path = IMAGE_INVENTORY / "runtime_tile_matches" / "curated_rle_fragments" / "curated_rle_fragments.json"
    english_rle_report_path = (
        IMAGE_INVENTORY
        / "english_patch_diff"
        / "rle_same_offset"
        / "notes"
        / "english_patch_rle_same_offset_diff.json"
    )
    if not manifest_path.exists():
        return []
    english_rle_by_offset = {}
    if english_rle_report_path.exists():
        english_rle_report = load_json(english_rle_report_path)
        english_rle_by_offset = {
            int(item["offset"]): item
            for item in english_rle_report.get("items", [])
        }

    title_by_offset = {
        0x003A3540: "전투 카드 리스트 いいえ UI 조각",
        0x003A4FCC: "전투 카드 패널 UI 조각",
        0x003A5E50: "전투 카드 패널 UI 조각",
        0x003A6E24: "전투 카드 패널 UI 조각",
        0x003A7C3C: "전투 카드 패널 UI 조각",
        0x003A8894: "전투 카드 패널 UI 조각",
        0x003A9624: "전투 카드 패널 UI 조각",
        0x003AA4C0: "전투 카드 패널 UI 조각",
        0x003ABB9C: "OK? 예/아니요 팝업 UI 조각",
        0x003AC8BC: "연성 이펙트/전투 배경 UI 조각",
        0x003AD218: "연성 이펙트/전투 배경 UI 조각",
        0x003AF23C: "연성/사용/버리기/돌아가기 팝업 UI 조각",
        0x003AF644: "세로 스트라이프 UI 조각",
        0x003AFB20: "세로 스트라이프 UI 조각",
    }
    # 0x003A206C already has a hand-named battle wordmark item.
    skip_offsets = {0x003A206C}

    items: list[dict] = []
    for order, block in enumerate(load_json(manifest_path), start=1):
        offset = int(block["offset"])
        if offset in skip_offsets:
            continue
        preview_path = block.get("layout_preview_path", "")
        if not preview_path or not (ROOT / preview_path).exists():
            continue
        source_label = title_by_offset.get(offset, "RLE UI 조각")
        readable_preview_by_offset = {
            0x003ABB9C: "confirmed_data/image_inventory/runtime_rle_patch_previews/single_rle_layouts/rle_003ABB9C_ok_yes_no_8cols_4x.png",
            0x003AF23C: "confirmed_data/image_inventory/runtime_rle_patch_previews/single_rle_layouts/rle_003AF23C_alchemy_command_8cols_4x.png",
        }
        display_preview_path = readable_preview_by_offset.get(offset, preview_path)
        if not (ROOT / display_preview_path).exists():
            display_preview_path = preview_path
        notes = (
            "타일맵 없이 4bpp 타일을 여러 폭으로 재배열한 미리보기라 실제 화면과는 어긋날 수 있다. "
            "일본어 설명/라벨이 섞여 있는 경우만 번역 후보로 유지한다. 영어 워드마크는 번역 대상에서 제외한다."
        )
        if offset == 0x003ABB9C:
            notes += " 8-column 재배열 기준으로 `OK? / はい / いいえ` 확인 팝업이 보이며, 한국어 목표는 `예/아니요`다."
        elif offset == 0x003AF23C:
            notes += " no_entry8_latest_ss1 BG0 기준으로 `錬成 / つかう / すてる / もどる` 팝업 본체와 강하게 대응하며, 한국어 목표는 `연성/사용/버리기/돌아가기` 계열이다."

        candidate_gallery = [
            {
                "index": block.get("index"),
                "offset": offset,
                "source": "rle_layout_variants",
                "png_path": preview_path,
                "preview_path": display_preview_path,
                "decompressed_size": block.get("decompressed_size"),
                "layouts": block.get("layouts", []),
            }
        ]
        english_reference = english_rle_by_offset.get(offset)
        if english_reference:
            candidate_gallery.append(
                {
                    "index": "english_reference",
                    "offset": offset,
                    "source": "english_patch_same_offset_rle",
                    "png_path": english_reference.get("en_scaled_png", english_reference.get("en_png", "")),
                    "preview_path": english_reference.get("en_scaled_png", english_reference.get("en_png", "")),
                    "decompressed_size": english_reference.get("en_decompressed_size"),
                    "jp_reference_path": english_reference.get("jp_scaled_png", english_reference.get("jp_png", "")),
                }
            )
            notes += " 영문판 same-offset RLE diff가 있으므로 영문판 배치/축약을 우선 참고한다."

        items.append(
            {
                "item_id": f"image:rle_ui_fragment:{offset:08X}",
                "category_id": "image_review_units",
                "group_id": f"rle_ui_fragment_{offset:08X}",
                "label": f"RLE 0x{offset:08X} {source_label}",
                "status": "candidate_found",
                "priority": "medium",
                "review_order": 8520 + order,
                "review_goal": "ss 런타임 매칭에서 잡힌 어긋난 RLE UI/텍스트 조각의 한글화 가능성 검토",
                "recommended_probe_method": "mGBA savestate runtime match + focused RLE layout variants",
                "future_workspace": "confirmed_data/image_inventory/runtime_tile_matches/curated_rle_fragments",
                "expected_text_kind": "rle_ui_fragment",
                "notes": notes,
                "subunits": [
                    {
                        "id": f"rle_{offset:08X}",
                        "label": f"ROM offset 0x{offset:08X}",
                        "first_action": "여러 column 레이아웃 중 읽히는 부분을 기준으로 실제 화면 위치와 대조",
                    }
                ],
                "source_preview_path": display_preview_path,
                "source_download_path": preview_path,
                "replacement_path": "",
                "comparison_notes": "",
                "candidate_gallery": candidate_gallery,
                "progress_status": "candidate_found",
                "default_review_included": False,
            }
        )
    return items


def build_runtime_tilemap_layer_items() -> list[dict]:
    layer_items = [
        {
            "item_id": "image:runtime_tilemap:no_entry8_latest_ss1_bg0",
            "group_id": "runtime_tilemap_no_entry8_latest_ss1_bg0",
            "label": "ss1 BG0 카드 선택/연성 메뉴 tilemap 레이어",
            "review_order": 8510,
            "expected_text_kind": "runtime_bg_tilemap_text_layer",
            "preview_path": "confirmed_data/image_inventory/runtime_tilemaps/no_entry8_latest_ss1/frame_007084/bg0_viewport.png",
            "notes": "BG0 screenblock 재배치 결과. 錬成/つかう/すてる/もどる 및 카드명처럼 보이는 텍스트가 정상 배치로 보인다.",
            "subunit_id": "no_entry8_latest_ss1_bg0",
            "first_action": "이 레이어의 문자가 폰트 문자열인지, 전용 타일 라벨인지 추가 추적",
        },
        {
            "item_id": "image:runtime_tilemap:no_entry8_latest_ss2_bg1",
            "group_id": "runtime_tilemap_no_entry8_latest_ss2_bg1",
            "label": "ss2 BG1 錬成手帳 메뉴 라벨 tilemap 레이어",
            "review_order": 8511,
            "expected_text_kind": "runtime_bg_tilemap_text_layer",
            "preview_path": "confirmed_data/image_inventory/runtime_tilemaps/no_entry8_latest_ss2/frame_008774/bg1_viewport.png",
            "notes": "BG1 screenblock 재배치 결과. 파란 메뉴 라벨 錬成手帳이 정상 배치로 보인다.",
            "subunit_id": "no_entry8_latest_ss2_bg1",
            "first_action": "錬成手帳 라벨이 문자열/폰트인지 이미지 타일인지 추적",
        },
        {
            "item_id": "image:runtime_tilemap:no_entry8_latest_ss3_bg0",
            "group_id": "runtime_tilemap_no_entry8_latest_ss3_bg0",
            "label": "ss3 BG0 카드 리스트 텍스트 tilemap 레이어",
            "review_order": 8512,
            "expected_text_kind": "runtime_bg_tilemap_text_layer",
            "preview_path": "confirmed_data/image_inventory/runtime_tilemaps/no_entry8_latest_ss3/frame_009730/bg0_viewport.png",
            "notes": "BG0 screenblock 재배치 결과. 카드 리스트 번호/잠김 텍스트/설명 텍스트가 정상 배치로 보인다.",
            "subunit_id": "no_entry8_latest_ss3_bg0",
            "first_action": "리스트 텍스트가 일반 추출 텍스트/폰트 렌더러인지 대조",
        },
        {
            "item_id": "image:runtime_tilemap:no_entry8_latest_ss3_bg1",
            "group_id": "runtime_tilemap_no_entry8_latest_ss3_bg1",
            "label": "ss3 BG1 카드 리스트 いいえ tilemap 레이어",
            "review_order": 8513,
            "expected_text_kind": "runtime_bg_tilemap_ui_layer",
            "preview_path": "confirmed_data/image_inventory/runtime_tilemaps/no_entry8_latest_ss3/frame_009730/bg1_viewport.png",
            "notes": "BG1 screenblock 재배치 결과. 카드 리스트 프레임과 いいえ 버튼 영역이 정상 배치로 보인다. BACK/NEXT는 영어라 번역 대상에서 제외한다.",
            "subunit_id": "no_entry8_latest_ss3_bg1",
            "first_action": "일본어 いいえ 및 오른쪽 탭 후보만 한글화 대상으로 검토",
        },
        {
            "item_id": "image:runtime_tilemap:no_entry8_ss1_obj",
            "group_id": "runtime_tilemap_no_entry8_ss1_obj",
            "label": "기존 ss1 OBJ 錬成 필드 라벨 tilemap 레이어",
            "review_order": 8514,
            "expected_text_kind": "runtime_obj_text_layer",
            "preview_path": "confirmed_data/image_inventory/runtime_tilemaps/no_entry8_ss1/frame_018255/obj_sprites.png",
            "notes": "기존 ss1을 tilemap/OAM 기준으로 재렌더링한 결과. 錬成 필드 라벨이 OBJ sprite 레이어에 정상 배치로 보인다.",
            "subunit_id": "no_entry8_ss1_obj",
            "first_action": "이미 등록된 0x005323AC 이미지 블록과 실제 화면 배치를 대조",
        },
        {
            "item_id": "image:runtime_tilemap:no_entry8_ss2_obj",
            "group_id": "runtime_tilemap_no_entry8_ss2_obj",
            "label": "기존 ss2 OBJ アイテム 필드 라벨 tilemap 레이어",
            "review_order": 8515,
            "expected_text_kind": "runtime_obj_text_layer",
            "preview_path": "confirmed_data/image_inventory/runtime_tilemaps/no_entry8_ss2/frame_018570/obj_sprites.png",
            "notes": "기존 ss2를 tilemap/OAM 기준으로 재렌더링한 결과. アイテム 필드 라벨이 OBJ sprite 레이어에 정상 배치로 보인다.",
            "subunit_id": "no_entry8_ss2_obj",
            "first_action": "이미 등록된 0x0053257C 이미지 블록과 실제 화면 배치를 대조",
        },
        {
            "item_id": "image:runtime_tilemap:no_entry8_ss3_bg1",
            "group_id": "runtime_tilemap_no_entry8_ss3_bg1",
            "label": "기존 ss3 BG1 전투 HUD/こうげき tilemap 레이어",
            "review_order": 8516,
            "expected_text_kind": "runtime_bg_tilemap_ui_layer",
            "preview_path": "confirmed_data/image_inventory/runtime_tilemaps/no_entry8_ss3/frame_112458/bg1_viewport.png",
            "notes": "기존 ss3를 tilemap 기준으로 재렌더링한 결과. エド/アル HP UI와 こうげき 버튼 라벨이 정상 배치로 보인다.",
            "subunit_id": "no_entry8_ss3_bg1",
            "first_action": "전투 HUD 작은 라벨과 명령 버튼 워드마크의 한글화 가능성을 검토",
        },
    ]

    items: list[dict] = []
    for layer in layer_items:
        preview_path = layer["preview_path"]
        if not (ROOT / preview_path).exists():
            continue
        items.append(
            {
                "item_id": layer["item_id"],
                "category_id": "image_review_units",
                "group_id": layer["group_id"],
                "label": f"분석용: {layer['label']}",
                "status": "candidate_found",
                "priority": "high",
                "review_order": layer["review_order"],
                "review_goal": "런타임 BG/OAM tilemap을 적용해 실제 화면 배치의 텍스트/타일 후보를 검토",
                "recommended_probe_method": "mGBA savestate + BG screenblock tilemap render",
                "future_workspace": "confirmed_data/image_inventory/runtime_tilemaps",
                "expected_text_kind": layer["expected_text_kind"],
                "notes": (
                    "주의: 이 PNG는 직접 교체할 원본 이미지가 아니라 분석용 재조립 화면이다. "
                    "실제 교체는 이 레이어에서 확인한 글자 타일을 ROM LZ77/RLE 블록 또는 텍스트 렌더러로 역추적한 뒤 진행한다. "
                    + layer["notes"]
                ),
                "replacement_target": False,
                "replacement_target_reason": "runtime tilemap/OAM 분석용 레이어라 파일 교체 대상이 아니다.",
                "subunits": [
                    {
                        "id": layer["subunit_id"],
                        "label": "runtime BG viewport",
                        "first_action": layer["first_action"],
                    }
                ],
                "source_preview_path": preview_path,
                "source_download_path": preview_path,
                "replacement_path": "",
                "comparison_notes": "",
                "candidate_gallery": [
                    {
                        "index": layer["review_order"],
                        "offset": 0,
                        "source": "runtime_bg_tilemap",
                        "png_path": preview_path,
                        "preview_path": preview_path,
                        "decompressed_size": "",
                    }
                ],
                "progress_status": "candidate_found",
                "default_review_included": False,
            }
        )
    return items


def build_runtime_rle_image_items() -> list[dict]:
    match_path = IMAGE_INVENTORY / "runtime_tile_matches" / "timeline_with_rle" / "runtime_tile_matches.json"
    if not match_path.exists():
        return []

    localizable_rle_offsets = {
        0x007E0000: {
            "label": "타이틀 화면 - 로고/저작권 (고급)",
            "display_preview_path": "confirmed_data/image_inventory/edit_packs/title_screen/90_logo_copyright__007E0000__advanced_edit_4x.png",
            "editable_preview_path": "confirmed_data/image_inventory/edit_packs/title_screen/90_logo_copyright__007E0000__advanced_edit_4x.png",
            "easy_note": "참고 항목. 로고 전체는 화면순 RLE 항목(image:rle_screen_order:timeline_with_rle:frame_001200:bg0:007E0000)에서 편집한다.",
            "replacement_target": False,
            "replacement_target_reason": "raw 8-column title logo layout can drift; use the tilemap-aware screen-order title logo item",
        },
        0x007E9158: {
            "label": "타이틀 화면 - PUSH START (영어 참고)",
            "display_preview_path": "confirmed_data/image_inventory/edit_packs/title_screen/01_push_start__007E9158__edit_4x.png",
            "editable_preview_path": "confirmed_data/image_inventory/edit_packs/title_screen/01_push_start__007E9158__edit_4x.png",
            "easy_note": "영어 워드마크라 현재 한글화 대상에서 제외한다.",
            "replacement_target": False,
            "replacement_target_reason": "English wordmark; Korean image targets are limited to Japanese source text",
            "tile_columns": 32,
        },
        0x007E9404: {
            "label": "타이틀 화면 - 처음부터",
            "display_preview_path": "confirmed_data/image_inventory/edit_packs/title_screen/02_new_game__007E9404__edit_4x.png",
            "editable_preview_path": "confirmed_data/image_inventory/edit_packs/title_screen/02_new_game__007E9404__edit_4x.png",
            "easy_note": "권장 문구: 처음부터. 원본 다운로드 PNG를 수정한 뒤 이 항목에 업로드하면 된다.",
            "replacement_target": True,
            "replacement_target_reason": "",
            "tile_columns": 32,
        },
        0x007E95E0: {
            "label": "타이틀 화면 - 이어하기",
            "display_preview_path": "confirmed_data/image_inventory/edit_packs/title_screen/03_continue__007E95E0__edit_4x.png",
            "editable_preview_path": "confirmed_data/image_inventory/edit_packs/title_screen/03_continue__007E95E0__edit_4x.png",
            "easy_note": "권장 문구: 이어하기. 원본 다운로드 PNG를 수정한 뒤 이 항목에 업로드하면 된다.",
            "replacement_target": True,
            "replacement_target_reason": "",
            "tile_columns": 32,
        },
        0x007E97A4: {
            "label": "타이틀 화면 - 통신",
            "display_preview_path": "confirmed_data/image_inventory/edit_packs/title_screen/04_link__007E97A4__edit_4x.png",
            "editable_preview_path": "confirmed_data/image_inventory/edit_packs/title_screen/04_link__007E97A4__edit_4x.png",
            "easy_note": "권장 문구: 통신. 원본 다운로드 PNG를 수정한 뒤 이 항목에 업로드하면 된다.",
            "replacement_target": True,
            "replacement_target_reason": "",
            "tile_columns": 32,
        },
    }
    items: list[dict] = []
    payload = load_json(match_path)
    seen: set[tuple[str, int, int]] = set()
    order = 9010
    for runtime in payload:
        frame = runtime.get("frame", "")
        charblock = runtime.get("charblock")
        for match in runtime.get("matches", []):
            if match.get("source") != "rle":
                continue
            offset = int(match["offset"])
            if offset not in localizable_rle_offsets:
                continue
            key = (str(match.get("source")), int(match.get("candidate_index", 0)), offset)
            if key in seen:
                continue
            seen.add(key)
            preview_path = match.get("preview_png_path") or match.get("preview_path") or ""
            if preview_path and not (ROOT / preview_path).exists():
                continue
            rle_meta = localizable_rle_offsets[offset]
            display_preview_path = rle_meta.get("display_preview_path", "")
            if display_preview_path and not (ROOT / display_preview_path).exists():
                display_preview_path = ""
            editable_preview_path = rle_meta.get("editable_preview_path", "")
            if editable_preview_path and not (ROOT / editable_preview_path).exists():
                editable_preview_path = ""
            source_preview_path = display_preview_path or preview_path
            source_download_path = editable_preview_path or preview_path
            label = rle_meta["label"]
            apply_note = (
                "원본 다운로드 PNG를 수정하고 같은 항목에 업로드하면 자동 RLE 적용 대상이 된다. "
                if rle_meta.get("replacement_target", True)
                else "참고 전용 항목이라 자동 적용 대상에서 제외된다. "
            )
            candidate_gallery = [
                {
                    "index": match.get("candidate_index"),
                    "offset": offset,
                    "source": "rle_runtime_match",
                    "png_path": preview_path,
                    "preview_path": preview_path,
                    "decompressed_size": match.get("decompressed_size"),
                    "score": match.get("score"),
                    "shared_tiles": match.get("shared_tiles"),
                }
            ]
            if editable_preview_path:
                candidate_gallery.insert(
                    0,
                    {
                        "index": "editable_source",
                        "offset": offset,
                            "source": f"editable_{int(rle_meta.get('tile_columns', 8))}cols_4x",
                        "png_path": editable_preview_path,
                        "preview_path": editable_preview_path,
                        "decompressed_size": match.get("decompressed_size"),
                    },
                )
            items.append(
                {
                    "item_id": f"image:rle:{offset:08X}",
                    "category_id": "image_review_units",
                    "group_id": f"rle_{offset:08X}",
                    "label": label,
                    "status": "candidate_found",
                    "priority": "high" if offset >= 0x007E0000 else "medium",
                    "review_order": order,
                    "review_goal": "RLE 압축 이미지/타일의 한글화 필요 여부 검토 및 교체본 등록",
                    "recommended_probe_method": "GBA RLE decompress + pymgba runtime tile match",
                    "future_workspace": "confirmed_data/image_inventory/runtime_tile_matches/timeline_with_rle",
                    "expected_text_kind": "rle_runtime_image",
                    "notes": (
                        f"runtime frame={frame}, charblock={charblock}, "
                        f"score={match.get('score')}, shared_tiles={match.get('shared_tiles')}, "
                        f"run={match.get('longest_contiguous_tile_run')}. "
                        + apply_note
                        + rle_meta.get("easy_note", "")
                    ),
                    "subunits": [
                        {
                            "id": f"rle_{offset:08X}",
                            "label": f"ROM offset 0x{offset:08X}",
                            "first_action": "텍스트 포함 여부 확인 후 교체 PNG 준비",
                        }
                    ],
                    "source_preview_path": source_preview_path,
                    "source_download_path": source_download_path,
                    "tile_columns": int(rle_meta.get("tile_columns", 8)),
                    "replacement_path": "",
                    "replacement_target": rle_meta.get("replacement_target", True),
                    "replacement_target_reason": rle_meta.get("replacement_target_reason", ""),
                    "comparison_notes": "",
                    "candidate_gallery": candidate_gallery,
                    "progress_status": "candidate_found",
                    "default_review_included": False,
                }
            )
            order += 1
    return items


def build_speaker_aliases(text_items: list[dict]) -> list[dict]:
    tokens = sorted(
        {
            item["dialogue_state_token"]
            for item in text_items
            if item.get("dialogue_state_token")
        }
    )
    return [
        {
            "dialogue_state_token": token,
            **parse_dialogue_state_token(token),
            "speaker_id": "",
            "notes": "",
            "confirmed": False,
            "speaker_name": "",
            "speaker_role": "",
        }
        for token in tokens
    ]


def parse_dialogue_state_token(token: str) -> dict[str, str | bool]:
    match = PORTRAIT_VARIANT_TOKEN_RE.match(token)
    if match:
        person = str(int(match.group("person")))
        variant = match.group("variant")
        return {
            "speaker_family_token": f"{match.group('prefix')}:{person}",
            "portrait_variant": variant,
            "portrait_variant_candidate": True,
        }
    return {
        "speaker_family_token": token,
        "portrait_variant": "",
        "portrait_variant_candidate": False,
    }


def build_speaker_registry(existing: list[dict] | None) -> list[dict]:
    existing_by_id = {
        item.get("speaker_id"): item
        for item in (existing or [])
        if item.get("speaker_id")
    }
    merged: list[dict] = []
    used_ids: set[str] = set()
    for default_item in DEFAULT_SPEAKER_REGISTRY:
        speaker_id = default_item["speaker_id"]
        merged.append({**default_item, **existing_by_id.get(speaker_id, {})})
        used_ids.add(speaker_id)
    for item in existing or []:
        speaker_id = item.get("speaker_id")
        if speaker_id and speaker_id not in used_ids:
            merged.append(item)
            used_ids.add(speaker_id)
    return merged


def build_progress_state(categories: list[dict]) -> dict:
    return {
        "version": 1,
        "last_updated": date.today().isoformat(),
        "current_category_id": "translation_workset_core_ui",
        "current_item_id": "",
        "current_review_scope": "translation_workset_core_ui",
        "last_built_rom": "patched_roms/current_review/hnr_localization_review.gba",
        "category_progress": {
            category["id"]: {"done": 0, "total": 0}
            for category in categories
        },
    }


def merge_existing_item_state(items: list[dict], existing_dataset: dict | None, existing_images: list[dict] | None) -> None:
    existing_map: dict[str, dict] = {}
    if existing_dataset:
        existing_map.update({item["item_id"]: item for item in existing_dataset.get("items", [])})
    if existing_images:
        existing_map.update({item["item_id"]: item for item in existing_images})

    for item in items:
        existing = existing_map.get(item["item_id"])
        if not existing:
            continue

        preserved_fields = [
            "agent_draft",
            "agent_comment",
            "manual_locked",
            "progress_status",
            "review_status",
            "replacement_path",
            "previous_replacement_path",
            "replacement_history",
            "comparison_notes",
            "status",
            "last_apply_report",
            "last_apply_summary",
            "last_restore_report",
            "last_restore_summary",
            "replacement_payload_base",
            "replacement_source_color_map",
            "replacement_verify_source_noop",
            "replacement_direct_rle_tiles",
            "replacement_native_patch_bbox",
            "replacement_native_clear_bbox",
            "replacement_tile_splits",
            "screen_entry_manual_raw_patch_offsets",
            "screen_entry_patch_tile_map_path",
        ]
        if not is_image_item(item):
            preserved_fields.append("notes")
        if not is_image_item(item):
            preserved_fields.extend(
                [
                    "source_preview_path",
                    "source_download_path",
                    "candidate_gallery",
                ]
            )

        for field in preserved_fields:
            if field in existing and existing[field] not in ("", None):
                item[field] = existing[field]
        if item.get("category_id") == REGISTRY_B_ZP_CATEGORY_ID and not item.get("replacement_path"):
            latest_upload = latest_uploaded_image_replacement(item["item_id"])
            if latest_upload:
                item["replacement_path"] = latest_upload
        if item.get("translation") and not item.get("agent_draft"):
            item["agent_draft"] = item["translation"]


def latest_uploaded_image_replacement(item_id: str) -> str:
    upload_dirs = []
    direct_dir = UPLOADED_IMAGE_REPLACEMENTS / item_id.replace(":", "_")
    if direct_dir.is_dir():
        upload_dirs.append(direct_dir)
    registry_match = re.match(r"image:registry_b_zp01:[0-9A-Fa-f]+:entry_([0-9A-Fa-f]{2})$", item_id)
    if registry_match:
        entry_hex = registry_match.group(1).upper()
        upload_dirs.extend(
            path
            for path in UPLOADED_IMAGE_REPLACEMENTS.glob(f"image_registry_b_zp01_*_entry_{entry_hex}")
            if path.is_dir() and path not in upload_dirs
        )
    pngs = [
        path
        for upload_dir in upload_dirs
        for path in upload_dir.iterdir()
        if path.is_file() and path.suffix.lower() == ".png"
    ]
    if not pngs:
        return ""
    latest = max(pngs, key=lambda path: path.stat().st_mtime)
    return str(latest.relative_to(ROOT))


def attach_image_candidate_assets(items: list[dict]) -> None:
    for item in items:
        if not is_image_item(item):
            continue
        workspace_rel = item.get("future_workspace")
        if not workspace_rel:
            continue
        workspace = ROOT / workspace_rel
        contact_sheet = workspace / "contact_sheets" / "candidates.png"
        if contact_sheet.exists():
            contact_rel = str(contact_sheet.relative_to(ROOT))
            item["source_preview_path"] = contact_rel
            item["source_download_path"] = contact_rel

        gallery_path = workspace / "notes" / "candidate_gallery.json"
        if gallery_path.exists():
            item["candidate_gallery"] = load_json(gallery_path)


def merge_existing_speaker_aliases(speaker_aliases: list[dict], existing: list[dict] | None) -> list[dict]:
    if not existing:
        return speaker_aliases
    existing_map = {item["dialogue_state_token"]: item for item in existing}
    for item in speaker_aliases:
        prev = existing_map.get(item["dialogue_state_token"])
        if not prev:
            continue
        for field in ("speaker_id", "speaker_name", "speaker_role", "notes", "confirmed"):
            if field in prev and prev[field] not in ("", None, False):
                item[field] = prev[field]
    return speaker_aliases


def merge_existing_progress(progress_state: dict, existing: dict | None) -> dict:
    if not existing:
        return progress_state
    for field in ("current_category_id", "current_item_id", "current_review_scope", "last_built_rom"):
        if field in existing and existing[field]:
            progress_state[field] = existing[field]
    if "category_progress" in existing:
        for category_id, status in existing["category_progress"].items():
            if category_id in progress_state["category_progress"]:
                progress_state["category_progress"][category_id].update(status)
    return progress_state


def update_category_progress(progress_state: dict, categories: list[dict], items: list[dict]) -> None:
    category_progress: dict[str, dict[str, int]] = {}
    for category in categories:
        category_items = [item for item in items if item["category_id"] == category["id"]]
        done = sum(1 for item in category_items if item.get("progress_status") == "done")
        category_progress[category["id"]] = {"done": done, "total": len(category_items)}
    progress_state["category_progress"] = category_progress


def build_dataset() -> dict:
    dialogue_tokens = build_dialogue_token_map()
    entry8_cluster_map = build_entry8_cluster_map()
    categories = build_categories()
    text_items = build_text_items(dialogue_tokens, entry8_cluster_map)
    image_items = build_image_items()
    normalize_image_source_paths(image_items)
    font_profile = load_json(FONT_PROFILE)

    items = text_items + image_items
    category_counts = defaultdict(int)
    for item in items:
        category_counts[item["category_id"]] += 1
    for category in categories:
        category["item_count"] = category_counts.get(category["id"], 0)

    return {
        "version": 1,
        "last_updated": date.today().isoformat(),
        "active_font": font_profile,
        "categories": categories,
        "items": items,
        "review_rom": {
            "fixed_output_path": "patched_roms/current_review/hnr_localization_review.gba",
            "note": "현재 저장된 전체 적용 번역 기준으로 항상 같은 파일명을 덮어써서 재빌드한다.",
        },
        "notes": [
            "텍스트 item 은 workset/cluster 기준으로 관리한다.",
            "dialogue_state_token 은 객관적 제어 상태 토큰이며, 화자 이름 확정값은 아니다.",
            "이미지 item 은 실제 교체 파일 경로와 검토 메모를 함께 관리한다.",
            "translation 은 최종 적용 번역이다.",
            "agent_draft 는 번역 에이전트가 제안한 초안이다.",
            "manual_locked=true 인 항목은 에이전트가 translation 을 덮어쓰면 안 된다.",
            "시작 직후 고정 카드 4줄은 테스트용 코어 UI가 아니라 정식 오프닝/인트로 카테고리로 관리한다.",
        ],
    }


def render_readme(dataset: dict) -> str:
    lines = [
        "# Localization Workbench 데이터",
        "",
        "이 폴더는 사람이 직접 번역/수정/진행 상태/화자 라벨/이미지 교체 후보를 관리하기 위한 작업대 데이터다.",
        "",
        "## 핵심 파일",
        "",
        "- `workbench_dataset.json`",
        "- `speaker_aliases.json`",
        "- `speaker_registry.json`",
        "- `progress_state.json`",
        "- `image_replacements.json`",
        "",
        "## active 폰트",
        "",
        f"- `{dataset['active_font'].get('label', 'unknown')}`",
        "",
        "## 카테고리",
        "",
    ]
    for category in dataset["categories"]:
        lines.append(f"- `{category['id']}`: {category['label']} / {category['item_count']}개")
    lines.extend(
        [
            "",
            "## 사용 용도",
            "",
            "- 텍스트를 카테고리별로 나눠 본다.",
            "- 대사에는 dialogue_state_token 과 등록된 화자 선택값을 함께 본다.",
            "- 진행 상태를 저장하고, 현재 검토 중인 category 를 이어서 연다.",
            "- 이미지 교체 후보는 replacement_path 와 메모를 따로 관리한다.",
            "",
        ]
    )
    return "\n".join(lines)


def main() -> int:
    WORKSPACE_ROOT.mkdir(parents=True, exist_ok=True)
    build_translation_normalization_profile()
    existing_dataset = load_json_if_exists(OUT_DATASET, None)
    existing_speakers = load_json_if_exists(OUT_SPEAKERS, None)
    existing_speaker_registry = load_json_if_exists(OUT_SPEAKER_REGISTRY, None)
    existing_progress = load_json_if_exists(OUT_PROGRESS, None)
    existing_images = load_json_if_exists(OUT_IMAGE, None)
    dataset = build_dataset()
    merge_existing_item_state(dataset["items"], existing_dataset, existing_images)
    attach_image_candidate_assets(dataset["items"])
    normalize_image_source_paths(dataset["items"])
    speaker_aliases = merge_existing_speaker_aliases(
        build_speaker_aliases(dataset["items"]),
        existing_speakers,
    )
    speaker_registry = build_speaker_registry(existing_speaker_registry)
    progress_state = merge_existing_progress(
        build_progress_state(dataset["categories"]),
        existing_progress,
    )
    update_category_progress(progress_state, dataset["categories"], dataset["items"])
    image_items = [item for item in dataset["items"] if is_image_item(item)]

    OUT_DATASET.write_text(json.dumps(dataset, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    OUT_SPEAKERS.write_text(json.dumps(speaker_aliases, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    OUT_SPEAKER_REGISTRY.write_text(json.dumps(speaker_registry, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    OUT_PROGRESS.write_text(json.dumps(progress_state, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    OUT_IMAGE.write_text(json.dumps(image_items, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    OUT_README.write_text(render_readme(dataset), encoding="utf-8")
    print(f"wrote {OUT_DATASET}")
    print(f"wrote {OUT_SPEAKERS}")
    print(f"wrote {OUT_SPEAKER_REGISTRY}")
    print(f"wrote {OUT_PROGRESS}")
    print(f"wrote {OUT_IMAGE}")
    print(f"wrote {OUT_README}")
    print(f"wrote {PROFILE_PATH}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
