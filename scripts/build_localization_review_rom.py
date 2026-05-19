#!/usr/bin/env python3

from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from gba_kor_tool.translation_normalization import normalize_translation_text

SOURCE_ROM = ROOT / "Hagane no Renkinjutsushi - Meisou no Rondo (Japan).gba"
WORKBENCH_ROOT = ROOT / "confirmed_data" / "localization_workbench"
TRANSLATION_WORKSETS = ROOT / "confirmed_data" / "translation_worksets"
TRANSLATION_WORKSPACE = ROOT / "confirmed_data" / "translation_workspace"
DATASET_PATH = WORKBENCH_ROOT / "workbench_dataset.json"
PROGRESS_PATH = WORKBENCH_ROOT / "progress_state.json"
OUT_DIR = ROOT / "patched_roms" / "current_review"
FIXED_ROM = OUT_DIR / "hnr_localization_review.gba"
TEMP_JSON = OUT_DIR / "current_review_translations.json"
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


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="현재 localization workbench 초안으로 고정 이름 review ROM 을 재빌드합니다.")
    parser.add_argument("--category-id", help="디버그용 선택 카테고리. 기본값은 전체 텍스트 항목 적용")
    parser.add_argument("--exclude-risky-dialogue", action="store_true", help="디버그용: runtime family 가 아직 완전히 닫히지 않은 대사 계열을 제외")
    parser.add_argument("--exclude-entry8", action="store_true", help="디버그용: Entry8 counted script 조각 레코드를 review ROM 에서 제외")
    return parser.parse_args()


def load_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def build_entry8_repoint_env() -> dict[str, str]:
    env = os.environ.copy()
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
    if item.get("manual_locked") and item.get("translation"):
        return item["translation"], "manual_locked_translation"
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


def build_translation_json(
    dataset: dict,
    category_id: str | None,
    *,
    exclude_risky_dialogue: bool,
    include_entry8: bool,
) -> list[dict]:
    items = []
    metadata_index = load_reinsertion_metadata()
    for item in dataset["items"]:
        hydrate_reinsertion_metadata(item, metadata_index)
        if item.get("offset") is None:
            continue
        if item["category_id"] == "image_review_units":
            continue
        if category_id and item["category_id"] != category_id:
            continue
        if item.get("source_group") == "registry_a_entry8_prefixed_texts" and not include_entry8:
            continue
        if exclude_risky_dialogue and item.get("default_review_included") is False:
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
    return payload


def main() -> int:
    args = parse_args()
    dataset = load_json(DATASET_PATH)
    payload = build_translation_json(
        dataset,
        args.category_id,
        exclude_risky_dialogue=args.exclude_risky_dialogue,
        include_entry8=not args.exclude_entry8,
    )
    if not payload:
        if args.category_id:
            raise SystemExit(f"no text items found for category: {args.category_id}")
        raise SystemExit("no translated text items found for full review build")
    DATASET_PATH.write_text(json.dumps(dataset, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    TEMP_JSON.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
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
    english_hud_font_source = ROOT / "local_roms" / "english_patched" / "Fullmetal Alchemist Stray Rondo (English Patched v0.02).gba"
    if english_hud_font_source.exists():
        subprocess.run(
            [
                "python3",
                "scripts/apply_english_battle_hud_font.py",
                "--source",
                str(english_hud_font_source),
                "--target",
                str(FIXED_ROM),
            ],
            cwd=ROOT,
            check=True,
        )
    else:
        print(f"skipped english battle HUD font patch: missing {english_hud_font_source}")
    print(f"built fixed review rom: {FIXED_ROM}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
