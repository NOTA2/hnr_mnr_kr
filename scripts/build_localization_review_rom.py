#!/usr/bin/env python3

from __future__ import annotations

import argparse
import json
import os
import shutil
import struct
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from gba_kor_tool.translation_normalization import display_units, normalize_translation_text

SOURCE_ROM = ROOT / "Hagane no Renkinjutsushi - Meisou no Rondo (Japan).gba"
WORKBENCH_ROOT = ROOT / "confirmed_data" / "localization_workbench"
TRANSLATION_WORKSETS = ROOT / "confirmed_data" / "translation_worksets"
TRANSLATION_WORKSPACE = ROOT / "confirmed_data" / "translation_workspace"
DATASET_PATH = WORKBENCH_ROOT / "workbench_dataset.json"
PROGRESS_PATH = WORKBENCH_ROOT / "progress_state.json"
OUT_DIR = ROOT / "patched_roms" / "current_review"
FIXED_ROM = OUT_DIR / "hnr_localization_review.gba"
TEMP_JSON = OUT_DIR / "current_review_translations.json"
FAST_TRANSLATED_ROM = OUT_DIR / "current_review_text_fast_translated.gba"
FAST_APPLY_REPORT = OUT_DIR / "current_review_text_fast_apply_report.json"
OVERLAPPED_TEXT_SKIP_REPORT = OUT_DIR / "current_review_overlapped_text_skips.json"
LOCATION_LABEL_REPORT = OUT_DIR / "current_review_location_label_offsets.json"
TEXT_LAYOUT_METADATA_REPORT = OUT_DIR / "current_review_text_layout_metadata_patches.json"
PREPARED_WORKBENCH_DIR = ROOT / "analysis" / "generated_workbenches" / "current_review"
PREPARED_TBL = PREPARED_WORKBENCH_DIR / "prepared.tbl"
FONT_READY_ROM = OUT_DIR / "current_review_font_ready.gba"
ENTRY8_REPOINT_SETS = ROOT / "analysis" / "entry8_structural_repoint_sets.json"
REINSERTION_METADATA_FIELDS = (
    "anchor_offset",
    "anchor_rom_address",
    "anchor",
    "stop_byte",
    "raw_byte_length",
    "raw_bytes",
    "before_bytes",
    "after_bytes",
)
COUNTED_SCRIPT_SOURCE_GROUPS = {
    "save_menu_texts",
    "registry_a_entry8_prefixed_texts",
}
OVERLAY_CANDIDATE_SOURCE_GROUPS = {
    "inline_event_texts",
}
IMAGE_CATEGORY_IDS = {
    "image_review_units",
    "image_group_field_menu_labels",
    "image_group_battle_command_buttons",
    "image_group_battle_popups_panels",
    "image_group_card_book_ui",
    "image_group_title_screen",
    "image_group_reference_candidates",
    "image_group_other",
    "common_hud_tiles",
    "alchemy_tiles",
    "registry_b_zp01_resources",
}
IMAGE_ITEM_COMPRESSIONS = {
    "lz77_tile",
    "rle_tile",
    "raw4bpp",
    "registry_b_zp00",
    "registry_b_zp01",
    "registry_b_raw4bpp",
}
IMAGE_ITEM_SOURCES = {
    "lz77_tile",
    "lz77_tile_4bpp",
    "rle_tile",
    "rle_tile_4bpp",
    "raw4bpp",
    "raw_4bpp",
    "raw_tile_4bpp",
    "registry_b_raw4bpp",
    "registry_b_zp01",
    "registry_b_zp01_4bpp",
}


def is_image_item(item: dict) -> bool:
    return (
        item.get("category_id") in IMAGE_CATEGORY_IDS
        or str(item.get("item_id", "")).startswith("image:")
        or item.get("compression") in IMAGE_ITEM_COMPRESSIONS
        or item.get("source") in IMAGE_ITEM_SOURCES
    )


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="현재 localization workbench 초안으로 고정 이름 review ROM 을 재빌드합니다.")
    parser.add_argument("--category-id", help="디버그용 선택 카테고리. 기본값은 전체 텍스트 항목 적용")
    parser.add_argument("--exclude-risky-dialogue", action="store_true", help="디버그용: runtime family 가 아직 완전히 닫히지 않은 대사 계열을 제외")
    parser.add_argument("--exclude-entry8", action="store_true", help="디버그용: Entry8 counted script 조각 레코드를 review ROM 에서 제외")
    parser.add_argument(
        "--apply-english-hud-font",
        action="store_true",
        help="디버그용: 영어판 0x00534874 HUD 블록을 통째로 적용합니다. 기본 재빌드는 일본판 블록을 유지합니다.",
    )
    parser.add_argument(
        "--apply-common-hud-name-slots",
        action="store_true",
        help=(
            "위험 실험용: 공유 0x00534874 HUD 타일셋의 AA-BE/CA-DD 슬롯을 직접 한글로 덮습니다. "
            "기본 재빌드에서는 상태창/숫자 UI 공유 타일 깨짐을 막기 위해 적용하지 않습니다."
        ),
    )
    parser.add_argument(
        "--reuse-prepared-font",
        action="store_true",
        help=(
            "빠른 텍스트 적용용: 이전 전체 빌드의 current_review_font_ready.gba 와 prepared.tbl 을 "
            "재사용해 폰트 재생성 없이 텍스트만 다시 삽입합니다. 새 글리프가 필요하면 전체 재빌드가 필요합니다."
        ),
    )
    return parser.parse_args()


def load_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def python_has_pillow(python_path: str) -> bool:
    try:
        completed = subprocess.run(
            [python_path, "-c", "from PIL import Image"],
            cwd=ROOT,
            text=True,
            capture_output=True,
            env={key: value for key, value in os.environ.items() if key != "PYTHONPATH"},
            check=False,
        )
    except OSError:
        return False
    return completed.returncode == 0


def select_pillow_python() -> str:
    candidates = [
        os.environ.get("PYTHON"),
        sys.executable,
        str(Path.home() / ".cache/codex-runtimes/codex-primary-runtime/dependencies/python/bin/python3"),
        "python3",
    ]
    seen: set[str] = set()
    for candidate in candidates:
        if not candidate or candidate in seen:
            continue
        seen.add(candidate)
        if python_has_pillow(candidate):
            return candidate
    return sys.executable


def build_entry8_repoint_env() -> dict[str, str]:
    env = os.environ.copy()
    env["PYTHON"] = select_pillow_python()
    env.setdefault("ENTRY8_ALLOW_BOUNDARY_CROSSING_IN_PLACE", "1")
    # Entry8 segment relocation can preserve more long translations, but it
    # also changes event/script segment locations. Runtime testing found that
    # later area transitions can load the wrong map/sprite state after segment
    # relocation, even when early smoke tests pass. Keep review builds on the
    # conservative length-preserved path by default; opt into relocation only
    # with explicit environment variables during isolated experiments.
    env.setdefault("ENTRY8_ALLOW_STRUCTURAL_REPOINT", "0")
    env.setdefault("ENTRY8_VARIABLE_OFFSETS", "")
    if env.get("ENTRY8_ALLOW_STRUCTURAL_REPOINT") == "1" and not env.get("ENTRY8_VARIABLE_OFFSETS") and ENTRY8_REPOINT_SETS.exists():
        repoint_sets = load_json(ENTRY8_REPOINT_SETS)
        offsets = repoint_sets.get("safe_tail_baseline", {}).get("offsets", [])
        env["ENTRY8_VARIABLE_OFFSETS"] = ",".join(f"0x{int(offset):06X}" for offset in offsets)
    return env


def build_record_key(record: dict) -> tuple[str, int]:
    return record.get("source_group", ""), int(record["offset"])


def load_reinsertion_metadata() -> dict[tuple[str, int], dict]:
    """Load structural insertion metadata from canonical workset/cluster files.

    The GUI dataset can outlive extractor/schema changes. Hydrating from source
    files keeps full rebuilds from silently losing Registry D packed relocation
    metadata when an older dataset is still on disk.
    """
    metadata: dict[tuple[str, int], dict] = {}
    source_paths = sorted(TRANSLATION_WORKSETS.glob("translation_workset_*.json"))
    source_paths.extend(sorted((TRANSLATION_WORKSPACE / "registry_a_entry8_clusters").glob("cluster_*.json")))

    for path in source_paths:
        records = load_json(path)
        if not isinstance(records, list):
            continue
        for record in records:
            if not isinstance(record, dict) or "offset" not in record:
                continue
            source_group = record.get("source_group")
            if not source_group:
                continue
            payload = {
                field: record.get(field)
                for field in REINSERTION_METADATA_FIELDS
                if record.get(field) not in (None, "")
            }
            if payload:
                metadata[(source_group, int(record["offset"]))] = payload
    return metadata


def hydrate_reinsertion_metadata(item: dict, metadata_index: dict[tuple[str, int], dict]) -> None:
    if item.get("offset") is None or not item.get("source_group"):
        return
    source_meta = metadata_index.get((item["source_group"], int(item["offset"])))
    if not source_meta:
        return
    for field, value in source_meta.items():
        if item.get(field) in (None, ""):
            item[field] = value


def resolve_effective_translation(item: dict) -> tuple[str, str]:
    if item.get("translation"):
        return item["translation"], "saved_translation"
    if item.get("agent_draft"):
        return item["agent_draft"], "agent_draft"
    return item["text"], "original_text"


def estimated_encoded_length(text: str) -> int:
    total = 0
    for ch in text:
        try:
            total += len(ch.encode("cp932"))
        except UnicodeEncodeError:
            # Hangul and injected custom glyphs are encoded as two-byte table codes.
            total += 2
    return total


def estimated_payload_length(item: dict) -> int:
    text = normalize_translation_text(
        item["effective_translation"],
        source_group=item.get("source_group"),
        reference_text=item.get("text"),
    )
    if item.get("source_group") in COUNTED_SCRIPT_SOURCE_GROUPS and item.get("char_count") is not None:
        return estimated_encoded_length(text)
    terminator_len = 0
    if item.get("source_group") not in COUNTED_SCRIPT_SOURCE_GROUPS and item.get("append_terminator") is not False:
        terminator_len = 1
    return estimated_encoded_length(text) + terminator_len


def original_capacity(item: dict) -> int:
    terminator_len = 0
    if item.get("source_group") not in COUNTED_SCRIPT_SOURCE_GROUPS and item.get("append_terminator") is not False:
        terminator_len = 1
    return int(item["byte_length"]) + terminator_len


def item_text_range(item: dict) -> tuple[int, int] | None:
    if item.get("offset") is None or item.get("byte_length") is None:
        return None
    start = int(item["offset"])
    return start, start + int(item["byte_length"])


def collect_text_overlay_protection_ranges(dataset_items: list[dict]) -> list[dict]:
    ranges = []
    for item in dataset_items:
        if item.get("source_group") in OVERLAY_CANDIDATE_SOURCE_GROUPS:
            continue
        if is_image_item(item):
            continue
        if item.get("source_group") is None:
            continue
        text_range = item_text_range(item)
        if text_range is None:
            continue
        start, end = text_range
        ranges.append(
            {
                "start": start,
                "end": end,
                "item_id": item.get("item_id"),
                "text": item.get("text", ""),
                "source_group": item.get("source_group"),
            }
        )
    return sorted(ranges, key=lambda row: (row["start"], row["end"]))


def find_text_overlay_parent_range(item: dict, protection_ranges: list[dict]) -> dict | None:
    if item.get("source_group") not in OVERLAY_CANDIDATE_SOURCE_GROUPS:
        return None
    text_range = item_text_range(item)
    if text_range is None:
        return None
    start, end = text_range
    for parent in protection_ranges:
        if max(start, int(parent["start"])) < min(end, int(parent["end"])):
            return parent
    return None


def build_translation_json(
    dataset: dict,
    category_id: str | None,
    *,
    exclude_risky_dialogue: bool,
    include_entry8: bool,
) -> tuple[list[dict], list[dict]]:
    items = []
    overlapped_skips = []
    metadata_index = load_reinsertion_metadata()
    protection_ranges = collect_text_overlay_protection_ranges(dataset["items"])
    for item in dataset["items"]:
        hydrate_reinsertion_metadata(item, metadata_index)
        if item.get("offset") is None:
            continue
        if is_image_item(item):
            continue
        if category_id and item["category_id"] != category_id:
            continue
        if item.get("source_group") == "registry_a_entry8_prefixed_texts" and not include_entry8:
            continue
        if exclude_risky_dialogue and item.get("default_review_included") is False:
            continue
        overlay_parent = find_text_overlay_parent_range(item, protection_ranges)
        if overlay_parent is not None:
            item["default_review_included"] = False
            item["overlap_exclusion_parent"] = overlay_parent
            exclusion_note = f"review excluded: overlaps {overlay_parent.get('item_id')}"
            if exclusion_note not in item.get("notes", ""):
                item["notes"] = ((item.get("notes", "") + " / ") if item.get("notes") else "") + exclusion_note
            overlapped_skips.append(
                {
                    "item_id": item.get("item_id"),
                    "source_group": item.get("source_group"),
                    "offset": int(item["offset"]),
                    "offset_hex": f"0x{int(item['offset']):06X}",
                    "byte_length": int(item["byte_length"]),
                    "text": item.get("text", ""),
                    "translation": item.get("translation", ""),
                    "parent_item_id": overlay_parent.get("item_id"),
                    "parent_offset_hex": f"0x{int(overlay_parent['start']):06X}",
                    "parent_end_hex": f"0x{int(overlay_parent['end']):06X}",
                    "parent_source_group": overlay_parent.get("source_group"),
                    "parent_text": overlay_parent.get("text", ""),
                    "reason": "inline/event text candidate overlaps a canonical text record",
                }
            )
            continue
        effective_translation, source = resolve_effective_translation(item)
        item["effective_translation"] = effective_translation
        item["translation_source"] = source
        if effective_translation == item["text"]:
            continue
        if item.get("source_group") == "registry_a_entry8_prefixed_texts" and not include_entry8:
            if estimated_payload_length(item) > original_capacity(item):
                continue
        items.append(item)

    # 같은 offset 이 여러 workset 에 중복될 수 있으므로, 실제 번역이 있는 항목 중
    # 보다 일반적인 정식 workset 항목을 우선해 하나만 남긴다.
    priority = {
        "translation_workset_opening_intro": 0,
        "translation_workset_core_ui": 1,
        "translation_workset_gameplay_terms": 2,
        "translation_workset_credits": 3,
        "translation_workset_registry_d_dialogue": 4,
        "registry_a_entry8_clusters_manifest": 5,
        "translation_workset_inline_event_texts": 6,
    }
    deduped: dict[tuple[str, int], tuple[tuple[int, int, int, str, str], dict]] = {}
    for item in sorted(
        items,
        key=lambda item: (
            item["offset"],
            priority.get(item.get("category_id", ""), 99),
            item.get("origin_workset_id", ""),
            item.get("item_id", ""),
        ),
    ):
        payload_len = estimated_payload_length(item)
        capacity = original_capacity(item)
        rank = (
            0 if payload_len <= capacity else 1,
            priority.get(item.get("category_id", ""), 99),
            payload_len,
            item.get("origin_workset_id", ""),
            item.get("item_id", ""),
        )
        key = build_record_key(item)
        current = deduped.get(key)
        if current is None or rank < current[0]:
            deduped[key] = (rank, item)

    items = sorted((item for _, item in deduped.values()), key=lambda item: item["offset"])
    payload = []
    for item in items:
        effective_translation = normalize_translation_text(
            item["effective_translation"],
            source_group=item.get("source_group"),
            reference_text=item.get("text"),
        )
        source = item["translation_source"]
        terminator = item.get("terminator")
        append_terminator = item.get("append_terminator")
        if item.get("source_group") in COUNTED_SCRIPT_SOURCE_GROUPS:
            terminator = None
            append_terminator = False
        payload.append(
            {
                "offset": item["offset"],
                "rom_address": item["rom_address"],
                "byte_length": item["byte_length"],
                "header_offset": item.get("header_offset"),
                "header_rom_address": item.get("header_rom_address"),
                "prefix": item.get("prefix"),
                "char_count": item.get("char_count"),
                "header_bytes": item.get("header_bytes"),
                "anchor_offset": item.get("anchor_offset"),
                "anchor_rom_address": item.get("anchor_rom_address"),
                "anchor": item.get("anchor"),
                "stop_byte": item.get("stop_byte"),
                "raw_byte_length": item.get("raw_byte_length"),
                "raw_bytes": item.get("raw_bytes"),
                "before_bytes": item.get("before_bytes"),
                "after_bytes": item.get("after_bytes"),
                "terminator": terminator,
                "append_terminator": append_terminator,
                "unknown_tokens": item.get("unknown_tokens", 0),
                "text": item["text"],
                "translation": effective_translation,
                "notes": item.get("notes", ""),
                "source_file": item["source_file"],
                "source_group": item["source_group"],
                "source_order": item["source_order"],
            }
        )
    return payload, overlapped_skips


TEXT_LAYOUT_METADATA_PATCH_RULES = {
    "location_texts": {
        "rule_id": "world_map_location_label_offset",
        "metadata_delta": 0x14,
        "value_type": "s32",
        "unit_px": 6,
        "constant": -104,
        "description": (
            "World-map location labels keep their name string in a fixed slot, "
            "then store the label/scroll offset at name_offset+0x14. Original "
            "records follow value = visible_width_px - 104."
        ),
    },
}


def compute_text_layout_metadata_value(text: str, rule: dict) -> int:
    return display_units(text) * int(rule["unit_px"]) + int(rule["constant"])


def apply_text_layout_metadata_patches(payload: list[dict]) -> None:
    data = bytearray(FIXED_ROM.read_bytes())
    report = []
    for item in payload:
        source_group = item.get("source_group")
        rule = TEXT_LAYOUT_METADATA_PATCH_RULES.get(source_group)
        if not rule:
            continue
        translation = normalize_translation_text(
            item.get("translation", ""),
            source_group=source_group,
            reference_text=item.get("text"),
        )
        if not translation:
            continue
        metadata_offset = int(item["offset"]) + int(rule["metadata_delta"])
        if metadata_offset + 4 > len(data):
            raise SystemExit(
                f"{source_group} text layout metadata offset out of ROM: 0x{metadata_offset:06X}"
            )
        old_value = struct.unpack_from("<i", data, metadata_offset)[0]
        new_value = compute_text_layout_metadata_value(translation, rule)
        struct.pack_into("<i", data, metadata_offset, new_value)
        report.append(
            {
                "source_group": source_group,
                "rule_id": rule["rule_id"],
                "text": item.get("text"),
                "translation": translation,
                "offset": item.get("offset"),
                "metadata_offset": metadata_offset,
                "metadata_offset_hex": f"0x{metadata_offset:06X}",
                "old_value": old_value,
                "new_value": new_value,
                "display_units": display_units(translation),
                "unit_px": rule["unit_px"],
                "constant": rule["constant"],
            }
        )
    FIXED_ROM.write_bytes(data)
    TEXT_LAYOUT_METADATA_REPORT.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    # Keep the older report path for existing notes/tools that link to it.
    location_report = [row for row in report if row.get("source_group") == "location_texts"]
    LOCATION_LABEL_REPORT.write_text(
        json.dumps(location_report, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    if report:
        print(f"patched text layout metadata: {len(report)}")


def apply_cached_font_text_build(args: argparse.Namespace) -> None:
    missing = [
        path
        for path in (FONT_READY_ROM, PREPARED_TBL)
        if not path.is_file()
    ]
    if missing:
        missing_text = ", ".join(str(path.relative_to(ROOT)) for path in missing)
        raise SystemExit(
            "빠른 텍스트 적용 캐시가 없습니다. 먼저 전체 적용 ROM 재빌드를 한 번 실행해 주세요: "
            + missing_text
        )

    command = [
        sys.executable,
        "-m",
        "gba_kor_tool",
        "apply-translations",
        str(FONT_READY_ROM),
        str(TEMP_JSON),
        str(FAST_TRANSLATED_ROM),
        "--table",
        str(PREPARED_TBL),
        "--encoding",
        "cp932",
        "--report",
        str(FAST_APPLY_REPORT),
    ]
    subprocess.run(command, cwd=ROOT, check=True, env=build_entry8_repoint_env())
    shutil.copy2(FAST_TRANSLATED_ROM, FIXED_ROM)


def apply_review_post_text_patches(args: argparse.Namespace) -> None:
    pillow_python = select_pillow_python()
    english_hud_font_source = ROOT / "local_roms" / "english_patched" / "Fullmetal Alchemist Stray Rondo (English Patched v0.02).gba"
    if args.apply_english_hud_font and english_hud_font_source.exists():
        subprocess.run(
            [
                pillow_python,
                "scripts/apply_english_battle_hud_font.py",
                "--source",
                str(english_hud_font_source),
                "--target",
                str(FIXED_ROM),
            ],
            cwd=ROOT,
            check=True,
        )
    elif args.apply_english_hud_font:
        print(f"skipped english battle HUD font patch: missing {english_hud_font_source}")
    else:
        print("skipped english battle HUD font patch: keeping Japanese 0x00534874 base")
    if args.apply_common_hud_name_slots:
        subprocess.run(
            [
                pillow_python,
                "scripts/apply_common_hud_korean_slot_patch.py",
                "--target",
                str(FIXED_ROM),
                "--no-backup",
            ],
            cwd=ROOT,
            check=True,
        )
    else:
        print("skipped common HUD name-slot patch: 0x00534874 is shared by status/number UI")
    subprocess.run(
        [
            pillow_python,
            "scripts/apply_battle_hud_name_font.py",
            "--target",
            str(FIXED_ROM),
            "--no-backup",
        ],
        cwd=ROOT,
        check=True,
    )


def main() -> int:
    args = parse_args()
    dataset = load_json(DATASET_PATH)
    payload, overlapped_skips = build_translation_json(
        dataset,
        args.category_id,
        exclude_risky_dialogue=args.exclude_risky_dialogue,
        include_entry8=not args.exclude_entry8,
    )
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    OVERLAPPED_TEXT_SKIP_REPORT.write_text(
        json.dumps(overlapped_skips, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    if overlapped_skips:
        print(f"skipped overlapped text candidates: {len(overlapped_skips)}")
    if not payload:
        if args.category_id:
            raise SystemExit(f"no text items found for category: {args.category_id}")
        raise SystemExit("no translated text items found for full review build")
    DATASET_PATH.write_text(json.dumps(dataset, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    TEMP_JSON.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    if args.reuse_prepared_font:
        apply_cached_font_text_build(args)
        apply_text_layout_metadata_patches(payload)
        apply_review_post_text_patches(args)
        print(f"fast-applied text to fixed review rom: {FIXED_ROM}")
        return 0

    slug = "current_review"
    command = [
        "zsh",
        "scripts/build_translated_rom_with_active_atlas.sh",
        str(SOURCE_ROM),
        str(TEMP_JSON),
        str(OUT_DIR),
        slug,
    ]
    subprocess.run(command, cwd=ROOT, check=True, env=build_entry8_repoint_env())
    built_rom = OUT_DIR / f"{slug}_translated.gba"
    shutil.copy2(built_rom, FIXED_ROM)
    apply_text_layout_metadata_patches(payload)
    apply_review_post_text_patches(args)
    print(f"built fixed review rom: {FIXED_ROM}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
