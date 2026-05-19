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

from gba_kor_tool.translation_normalization import PROFILE_PATH, build_default_profile, normalize_translation_text
DATA_ROOT = ROOT / "confirmed_data"
WORKSPACE_ROOT = DATA_ROOT / "localization_workbench"
TRANSLATION_WORKSETS = DATA_ROOT / "translation_worksets"
TRANSLATION_WORKSPACE = DATA_ROOT / "translation_workspace"
DIALOGUE_METADATA = DATA_ROOT / "dialogue_metadata"
IMAGE_INVENTORY = DATA_ROOT / "image_inventory"
EXTRACTED_TEXTS = DATA_ROOT / "extracted_texts"
FONT_PROFILE = DATA_ROOT / "font_assets" / "active_hangul_font_profile.json"

OUT_DATASET = WORKSPACE_ROOT / "workbench_dataset.json"
OUT_SPEAKERS = WORKSPACE_ROOT / "speaker_aliases.json"
OUT_SPEAKER_REGISTRY = WORKSPACE_ROOT / "speaker_registry.json"
OUT_PROGRESS = WORKSPACE_ROOT / "progress_state.json"
OUT_IMAGE = WORKSPACE_ROOT / "image_replacements.json"
OUT_README = WORKSPACE_ROOT / "README.md"

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
        {
            "id": "image_review_units",
            "label": "이미지 작업",
            "type": "image",
            "sort_order": 7,
            "path": "confirmed_data/image_inventory/image_text_inventory.json",
            "description": "이미지에 구워진 텍스트 자산 검토/교체",
            "build_enabled": False,
        },
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
    items.extend(build_runtime_rle_image_items())
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


def build_runtime_rle_screen_order_items() -> list[dict]:
    manifest_path = IMAGE_INVENTORY / "runtime_rle_screen_order" / "screen_order_manifest.json"
    if not manifest_path.exists():
        return []

    include_keys = {
        ("no_entry8_latest_ss1", "frame_007084", 0, 0x003AF23C),
        ("no_entry8_latest_ss1", "frame_007084", 1, 0x003A206C),
        ("timeline_with_rle", "frame_001200", 0, 0x007E0000),
    }
    labels = {
        0x003AF23C: "화면순 RLE 편집 - 연성/사용/버리기/돌아가기 팝업",
        0x003A206C: "화면순 RLE 편집 - 전투 카드/ALCHEMY 패널",
        0x003A3540: "화면순 RLE 편집 - 카드 리스트/BACK/NEXT UI",
        0x00186AE8: "화면순 RLE 편집 - 전투 HUD 소형 숫자",
        0x007E0000: "화면순 RLE 편집 - 타이틀 로고/저작권",
    }
    goals = {
        0x003AF23C: "실제 화면 배치로 재조립된 팝업 본문을 한국어 이미지로 교체",
        0x003A206C: "전투 카드/ALCHEMY 패널의 이미지 워드마크와 UI 문구를 화면순으로 검토",
        0x003A3540: "카드 리스트 프레임/BACK/NEXT/ID 주변 UI 타일을 화면순으로 검토",
        0x00186AE8: "작은 HUD 숫자/표시 타일을 한글화 또는 영문판 유지 기준으로 검토",
        0x007E0000: "타이틀 로고와 저작권 영역을 실제 배치에 가까운 PNG로 편집",
    }

    items: list[dict] = []
    for order, block in enumerate(load_json(manifest_path), start=1):
        offset = int(block["offset"])
        key = (block.get("scene", ""), block.get("frame", ""), int(block.get("bg", -1)), offset)
        if key not in include_keys:
            continue
        preview_path = block.get("context_preview_path", "")
        download_path = block.get("source_download_path") or block.get("editable_preview_path", "")
        tile_map_path = block.get("tile_map_path", "")
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
                    "원본 다운로드는 화면순으로 재조립된 편집용 PNG다. 업로드 시 tile_map.json을 사용해 "
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
                "tile_map_path": tile_map_path,
                "replacement_path": "",
                "comparison_notes": "",
                "candidate_gallery": [
                    {
                        "index": "context",
                        "offset": offset,
                        "source": "runtime_screen_order_context",
                        "png_path": preview_path,
                        "preview_path": preview_path,
                        "decompressed_size": block.get("matched_tile_count"),
                    },
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

    curated_blocks = [
        {
            "item_id": "image:field_label_0053257C",
            "group_id": "field_label_0053257C",
            "label": "필드/카드 라벨 アセやし 이미지 블록",
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
            "first_action": "일본어 라벨의 실제 의미와 화면 배치를 확인한 뒤 한국어 교체 이미지 준비",
        },
        {
            "item_id": "image:battle_menu_wordmarks_003A206C",
            "group_id": "battle_menu_wordmarks_003A206C",
            "label": "전투 메뉴 워드마크 ALCHEMY/SKILL/ITEM/CARD/NETWORK 블록",
            "priority": "medium",
            "review_order": 8492,
            "review_goal": "ss3 런타임 매칭으로 확인된 전투 메뉴 이미지 워드마크의 한글화 가능성 검토",
            "recommended_probe_method": "mGBA savestate runtime match / RLE offset 0x003A206C",
            "expected_text_kind": "battle_menu_wordmark",
            "notes": (
                "사용자 ss3 기준 실제 전투 화면에서 쓰이는 RLE 이미지 블록. "
                "현재는 영문 워드마크라 일본어 누락은 아니지만, 한글화 대상 후보로 따로 식별해 둔다."
            ),
            "offset": 0x003A206C,
            "source": "rle",
            "preview_path": "confirmed_data/image_inventory/runtime_tile_matches/no_entry8_ss3/matched_previews/rle_0831_off_003A206C.png",
            "display_preview_path": "confirmed_data/image_inventory/gui_display_previews/rle_0831_off_003A206C_display.png",
            "subunit_id": "rle_003A206C",
            "subunit_label": "ROM offset 0x003A206C",
            "first_action": "영문 워드마크를 유지할지 한국어 축약 타일로 바꿀지 결정",
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
                "decompressed_size": "",
            }
        ]
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
        items.append(
            {
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
                "comparison_notes": "",
                "candidate_gallery": candidate_gallery,
                "progress_status": "candidate_found",
                "default_review_included": False,
            }
        )
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
        0x003A3540: "전투 카드 리스트/BACK/NEXT UI 조각",
        0x003A4FCC: "전투 카드 패널 UI 조각",
        0x003A5E50: "전투 카드 패널 UI 조각",
        0x003A6E24: "전투 카드 패널 UI 조각",
        0x003A7C3C: "전투 카드 패널/BACK/NEXT UI 조각",
        0x003A8894: "전투 카드 패널/BACK/NEXT UI 조각",
        0x003A9624: "전투 카드 패널/BACK/NEXT UI 조각",
        0x003AA4C0: "전투 카드 패널/BACK/NEXT UI 조각",
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
            "그래도 BACK/NEXT, OK?, 일본어 설명, 카드 패널 라벨처럼 번역 가능한 글자 타일이 섞여 있어 선별 후보로 유지한다."
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
            "label": "ss3 BG1 카드 리스트 프레임/BACK/NEXT tilemap 레이어",
            "review_order": 8513,
            "expected_text_kind": "runtime_bg_tilemap_ui_layer",
            "preview_path": "confirmed_data/image_inventory/runtime_tilemaps/no_entry8_latest_ss3/frame_009730/bg1_viewport.png",
            "notes": "BG1 screenblock 재배치 결과. 카드 리스트 프레임, BACK/NEXT, 버튼 영역이 정상 배치로 보인다.",
            "subunit_id": "no_entry8_latest_ss3_bg1",
            "first_action": "BACK/NEXT 같은 워드마크를 유지할지 한글화할지 검토",
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
            "label": "기존 ss2 OBJ アセやし 필드 라벨 tilemap 레이어",
            "review_order": 8515,
            "expected_text_kind": "runtime_obj_text_layer",
            "preview_path": "confirmed_data/image_inventory/runtime_tilemaps/no_entry8_ss2/frame_018570/obj_sprites.png",
            "notes": "기존 ss2를 tilemap/OAM 기준으로 재렌더링한 결과. アセやし 필드 라벨이 OBJ sprite 레이어에 정상 배치로 보인다.",
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
            "easy_note": "고급 항목. 로고 전체는 화면 배치 재조립본을 더 만든 뒤 편집하는 편이 안전하다.",
            "replacement_target": True,
            "replacement_target_reason": "",
        },
        0x007E9158: {
            "label": "타이틀 화면 - PUSH START",
            "display_preview_path": "confirmed_data/image_inventory/edit_packs/title_screen/01_push_start__007E9158__edit_4x.png",
            "editable_preview_path": "confirmed_data/image_inventory/edit_packs/title_screen/01_push_start__007E9158__edit_4x.png",
            "easy_note": "원본 다운로드 PNG를 수정한 뒤 이 항목에 업로드하면 된다.",
            "replacement_target": True,
            "replacement_target_reason": "",
        },
        0x007E9404: {
            "label": "타이틀 화면 - 처음부터",
            "display_preview_path": "confirmed_data/image_inventory/edit_packs/title_screen/02_new_game__007E9404__edit_4x.png",
            "editable_preview_path": "confirmed_data/image_inventory/edit_packs/title_screen/02_new_game__007E9404__edit_4x.png",
            "easy_note": "권장 문구: 처음부터. 원본 다운로드 PNG를 수정한 뒤 이 항목에 업로드하면 된다.",
            "replacement_target": True,
            "replacement_target_reason": "",
        },
        0x007E95E0: {
            "label": "타이틀 화면 - 이어하기",
            "display_preview_path": "confirmed_data/image_inventory/edit_packs/title_screen/03_continue__007E95E0__edit_4x.png",
            "editable_preview_path": "confirmed_data/image_inventory/edit_packs/title_screen/03_continue__007E95E0__edit_4x.png",
            "easy_note": "권장 문구: 이어하기. 원본 다운로드 PNG를 수정한 뒤 이 항목에 업로드하면 된다.",
            "replacement_target": True,
            "replacement_target_reason": "",
        },
        0x007E97A4: {
            "label": "타이틀 화면 - 통신",
            "display_preview_path": "confirmed_data/image_inventory/edit_packs/title_screen/04_link__007E97A4__edit_4x.png",
            "editable_preview_path": "confirmed_data/image_inventory/edit_packs/title_screen/04_link__007E97A4__edit_4x.png",
            "easy_note": "권장 문구: 통신. 원본 다운로드 PNG를 수정한 뒤 이 항목에 업로드하면 된다.",
            "replacement_target": True,
            "replacement_target_reason": "",
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
            display_preview_path = localizable_rle_offsets[offset].get("display_preview_path", "")
            if display_preview_path and not (ROOT / display_preview_path).exists():
                display_preview_path = ""
            editable_preview_path = localizable_rle_offsets[offset].get("editable_preview_path", "")
            if editable_preview_path and not (ROOT / editable_preview_path).exists():
                editable_preview_path = ""
            source_preview_path = display_preview_path or preview_path
            source_download_path = editable_preview_path or preview_path
            label = localizable_rle_offsets[offset]["label"]
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
                        "source": "editable_8cols_4x",
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
                        "원본 다운로드 PNG를 수정하고 같은 항목에 업로드하면 자동 RLE 적용 대상이 된다. "
                        + localizable_rle_offsets[offset].get("easy_note", "")
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
                    "tile_columns": 8,
                    "replacement_path": "",
                    "replacement_target": localizable_rle_offsets[offset].get("replacement_target", True),
                    "replacement_target_reason": localizable_rle_offsets[offset].get("replacement_target_reason", ""),
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
            "comparison_notes",
            "status",
        ]
        if item.get("category_id") != "image_review_units":
            preserved_fields.append("notes")
        if item.get("category_id") != "image_review_units":
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
        if item.get("translation") and not item.get("agent_draft"):
            item["agent_draft"] = item["translation"]


def attach_image_candidate_assets(items: list[dict]) -> None:
    for item in items:
        if item.get("category_id") != "image_review_units":
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
    image_items = [item for item in dataset["items"] if item["category_id"] == "image_review_units"]

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
