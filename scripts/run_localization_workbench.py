#!/usr/bin/env python3

from __future__ import annotations

import argparse
import base64
import json
import mimetypes
import shutil
import subprocess
import sys
import urllib.parse
from datetime import datetime
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from io import BytesIO
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
if str(ROOT / ".vendor") not in sys.path:
    sys.path.append(str(ROOT / ".vendor"))

from gba_kor_tool.translation_normalization import normalize_translation_text

HTML = ROOT / "tools" / "localization_workbench.html"
WORKBENCH_DIR = ROOT / "confirmed_data" / "localization_workbench"
DATASET_PATH = WORKBENCH_DIR / "workbench_dataset.json"
SPEAKERS_PATH = WORKBENCH_DIR / "speaker_aliases.json"
SPEAKER_REGISTRY_PATH = WORKBENCH_DIR / "speaker_registry.json"
PROGRESS_PATH = WORKBENCH_DIR / "progress_state.json"
IMAGE_REPLACEMENTS_PATH = WORKBENCH_DIR / "image_replacements.json"
UPLOADS_ROOT = WORKBENCH_DIR / "uploaded_image_replacements"
IMAGE_RESTORE_REPORT_PATH = WORKBENCH_DIR / "image_restore_report.json"
ACTUAL_IMAGE_TARGETS_PATH = ROOT / "confirmed_data" / "image_inventory" / "localization_targets" / "actual_localization_targets.json"
IMPORT_REPORT_DIR = WORKBENCH_DIR / "import_reports"
AGENT_INBOX_DIR = WORKBENCH_DIR / "agent_inbox"
IMPORTED_AGENT_RESULTS_DIR = WORKBENCH_DIR / "imported_agent_results"
EXPANSION_OPPORTUNITIES_PATH = ROOT / "confirmed_data" / "translation_workspace" / "translation_expansion_opportunities.json"
BATTLE_HUD_NAME_TABLE_PATH = ROOT / "confirmed_data" / "font_assets" / "battle_hud_name_table.json"
BATTLE_HUD_NAME_TRANSLATIONS_PATH = ROOT / "confirmed_data" / "font_assets" / "battle_hud_name_translations.json"
BATTLE_HUD_NAME_CATEGORY_ID = "battle_hud_name_table"
BATTLE_HUD_NAME_ITEM_PREFIX = "battle_hud_name:"
PAGE_TURN_RLE_TILE_CATEGORY_IDS = {f"page_turn_rle_{order:02d}_tiles" for order in range(5, 13)}
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
    *PAGE_TURN_RLE_TILE_CATEGORY_IDS,
}
COMMON_HUD_TILE_CATEGORY_ID = "common_hud_tiles"
ALCHEMY_TILE_CATEGORY_ID = "alchemy_tiles"
HUD_TILE_CATEGORY_IDS = {COMMON_HUD_TILE_CATEGORY_ID, ALCHEMY_TILE_CATEGORY_ID, *PAGE_TURN_RLE_TILE_CATEGORY_IDS}
COMMON_HUD_TILE_SIZE = 8
COMMON_HUD_RESERVED_ITEM_IDS = {"image:lz77_tile:00534874:tile_000"}
COMMON_HUD_TILE_MANIFEST_PATH = (
    ROOT
    / "confirmed_data"
    / "image_inventory"
    / "edit_packs"
    / "common_hud_tiles_00534874"
    / "manifest.json"
)

COUNTED_SCRIPT_SOURCE_GROUPS = {
    "registry_a_entry8_prefixed_texts",
    "inline_event_texts",
    "startup_intro_texts",
    "save_menu_texts",
    "choice_yes_no_texts",
}

TEXT_SAVE_FIELDS = (
    "translation",
    "agent_draft",
    "agent_comment",
    "manual_locked",
    "notes",
    "progress_status",
    "review_status",
)


def is_image_item(item: dict[str, Any]) -> bool:
    return item.get("category_id") in IMAGE_CATEGORY_IDS or str(item.get("item_id", "")).startswith("image:")


def common_hud_tile_asset_defaults() -> dict[str, dict[str, Any]]:
    if not COMMON_HUD_TILE_MANIFEST_PATH.exists():
        return {}
    manifest = load_json(COMMON_HUD_TILE_MANIFEST_PATH)
    defaults: dict[str, dict[str, Any]] = {}
    for tile in manifest.get("tiles", []):
        try:
            tile_index = int(tile.get("tile_index"))
        except (TypeError, ValueError):
            continue
        item_id = f"image:lz77_tile:00534874:tile_{tile_index:03X}"
        source_1x = tile.get("source_1x", "")
        preview_8x = tile.get("preview_8x", "")
        defaults[item_id] = {
            "source_preview_path": source_1x,
            "source_download_path": source_1x,
            "candidate_gallery": [
                {
                    "index": "tile_1x",
                    "offset": 0x00534874,
                    "source": "lz77_tile_4bpp_source_1x",
                    "png_path": source_1x,
                    "preview_path": source_1x,
                    "tile_index": tile_index,
                    "tile_index_hex": f"0x{tile_index:03X}",
                    "decompressed_size": 32,
                },
                {
                    "index": "tile_8x",
                    "offset": 0x00534874,
                    "source": "lz77_tile_4bpp_preview_8x",
                    "png_path": preview_8x,
                    "preview_path": preview_8x,
                    "tile_index": tile_index,
                    "tile_index_hex": f"0x{tile_index:03X}",
                    "decompressed_size": 32,
                },
            ],
        }
    return defaults


def apply_common_hud_tile_asset_defaults(item: dict[str, Any], defaults: dict[str, dict[str, Any]]) -> None:
    if item.get("category_id") != COMMON_HUD_TILE_CATEGORY_ID:
        return
    values = defaults.get(str(item.get("item_id")))
    if not values:
        return
    for field in ("source_preview_path", "source_download_path", "candidate_gallery"):
        if not item.get(field):
            item[field] = values[field]


def ensure_image_apply_defaults(item: dict[str, Any]) -> None:
    item_id = str(item.get("item_id", ""))
    if not (
        item_id.startswith("image:rle_screen_order:")
        or item_id.startswith("image:rle_screen_order_focus:")
    ):
        return
    if not item.get("tile_map_path"):
        return
    if item.get("replacement_payload_base") in ("", None):
        item["replacement_payload_base"] = "source_raw"
    if item.get("replacement_source_color_map") in ("", None):
        item["replacement_source_color_map"] = True
    if item.get("replacement_verify_source_noop") in ("", None):
        item["replacement_verify_source_noop"] = True


def estimated_encoded_length(text: str) -> int:
    total = 0
    for ch in text:
        try:
            total += len(ch.encode("cp932"))
        except UnicodeEncodeError:
            total += 2
    return total


def terminator_length(item: dict[str, Any]) -> int:
    counted = item.get("source_group") in COUNTED_SCRIPT_SOURCE_GROUPS and item.get("char_count") is not None
    return 0 if counted or item.get("append_terminator") is False else 1


def capacity_bytes(item: dict[str, Any]) -> int | None:
    if item.get("byte_length") is None:
        return None
    return int(item["byte_length"]) + terminator_length(item)


def length_overflow_allowed(item: dict[str, Any]) -> bool:
    mode = item.get("expansion_mode") or item.get("length_policy") or ""
    if item.get("source_group") == "registry_a_entry8_prefixed_texts":
        return mode == "confirmed_repoint"
    if mode in {"packed_repoint_available", "direct_repoint_available"}:
        return True
    if (
        item.get("source_group") == "registry_d_fc_script_texts"
        and item.get("anchor_offset") is not None
        and item.get("raw_byte_length") is not None
    ):
        return True
    return bool(item.get("repoint_allowed") or item.get("can_repoint") or item.get("length_policy") == "repoint")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="로컬라이제이션 workbench 서버")
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=8766)
    return parser.parse_args()


def load_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, payload: Any) -> None:
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


class WorkbenchStore:
    def __init__(self) -> None:
        self.last_auto_import_summary = {
            "imported_count": 0,
            "imported_files": [],
            "report_paths": [],
        }
        self.reload()
        self.auto_import_agent_results()

    def reload(self) -> None:
        self.dataset = load_json(DATASET_PATH)
        self.speakers = load_json(SPEAKERS_PATH)
        self.speaker_registry = load_json(SPEAKER_REGISTRY_PATH)
        self.progress = load_json(PROGRESS_PATH)
        self.image_replacements = load_json(IMAGE_REPLACEMENTS_PATH)
        common_hud_defaults = common_hud_tile_asset_defaults()
        for item in self.dataset.get("items", []):
            if is_image_item(item):
                apply_common_hud_tile_asset_defaults(item, common_hud_defaults)
                ensure_image_apply_defaults(item)
        for item in self.image_replacements:
            apply_common_hud_tile_asset_defaults(item, common_hud_defaults)
            ensure_image_apply_defaults(item)
        self.image_target_prompts = self.load_image_target_prompts()
        self.expansion_opportunities = self.load_expansion_opportunities()
        self.battle_hud_name_table = self.load_battle_hud_name_table()

    def load_battle_hud_name_table(self) -> dict[str, Any]:
        if not BATTLE_HUD_NAME_TABLE_PATH.exists():
            return {"unique_names": []}
        return load_json(BATTLE_HUD_NAME_TABLE_PATH)

    def load_image_target_prompts(self) -> dict[str, dict[str, Any]]:
        if not ACTUAL_IMAGE_TARGETS_PATH.exists():
            return {}
        targets = load_json(ACTUAL_IMAGE_TARGETS_PATH)
        prompts: dict[str, dict[str, Any]] = {}
        for target in targets:
            item_id = target.get("workbench_item_id")
            if not item_id:
                continue
            prompts[str(item_id)] = {
                "localization_target_id": target.get("target_id", ""),
                "prompt_source_text": target.get("text_seen", ""),
                "prompt_korean_text": target.get("korean_goal", ""),
                "prompt_target_label": target.get("label", ""),
            }
        return prompts

    def load_expansion_opportunities(self) -> dict[tuple[str, int], dict[str, Any]]:
        if not EXPANSION_OPPORTUNITIES_PATH.exists():
            return {}
        payload = load_json(EXPANSION_OPPORTUNITIES_PATH)
        index: dict[tuple[str, int], dict[str, Any]] = {}
        for record in payload.get("records", []):
            source_group = record.get("source_group")
            offset = record.get("offset")
            if source_group is None or offset is None:
                continue
            index[(str(source_group), int(offset))] = {
                "expansion_mode": record.get("expansion_mode", ""),
                "direct_pointer_count": record.get("direct_pointer_count", 0),
                "slack_bytes": record.get("slack_bytes", 0),
                "payload_length": record.get("payload_length"),
                "original_capacity": record.get("original_capacity"),
            }
        return index

    def reload_sidecars(self) -> None:
        self.speakers = load_json(SPEAKERS_PATH)
        self.speaker_registry = load_json(SPEAKER_REGISTRY_PATH)
        self.progress = load_json(PROGRESS_PATH)
        self.image_replacements = load_json(IMAGE_REPLACEMENTS_PATH)
        common_hud_defaults = common_hud_tile_asset_defaults()
        for item in self.image_replacements:
            apply_common_hud_tile_asset_defaults(item, common_hud_defaults)
            ensure_image_apply_defaults(item)
        self.image_target_prompts = self.load_image_target_prompts()

    def bundle(self) -> dict[str, Any]:
        self.reload_sidecars()
        dataset = json.loads(json.dumps(self.dataset, ensure_ascii=False))
        self.inject_battle_hud_name_items(dataset)
        image_map = {item["item_id"]: item for item in self.image_replacements}
        for item in dataset["items"]:
            expansion = self.expansion_opportunities.get((item.get("source_group", ""), int(item.get("offset") or -1)))
            if expansion:
                item.update(expansion)
            if is_image_item(item):
                ensure_image_apply_defaults(item)
                prompt_info = self.image_target_prompts.get(item["item_id"])
                if prompt_info:
                    item.update(prompt_info)
                sidecar = image_map.get(item["item_id"])
                if sidecar:
                    ensure_image_apply_defaults(sidecar)
                    for field in (
                        "source_preview_path",
                        "source_download_path",
                        "reference_preview_path",
                        "replacement_path",
                        "previous_replacement_path",
                        "replacement_history",
                        "last_restore_report",
                        "last_restore_summary",
                        "comparison_notes",
                        "notes",
                        "progress_status",
                        "status",
                        "candidate_gallery",
                        "replacement_target",
                        "replacement_target_reason",
                        "image_group_id",
                        "image_group_label",
                        "image_group_order",
                        "tile_map_path",
                        "tile_columns",
                        "replacement_payload_base",
                        "replacement_source_color_map",
                        "replacement_verify_source_noop",
                        "replacement_direct_rle_tiles",
                        "replacement_native_patch_bbox",
                        "replacement_native_clear_bbox",
                        "replacement_tile_splits",
                        "screen_entry_manual_raw_patch_offsets",
                        "screen_entry_patch_tile_map_path",
                    ):
                        if field in sidecar:
                            item[field] = sidecar[field]
        return {
            "dataset": dataset,
            "speakers": self.speakers,
            "speaker_registry": self.speaker_registry,
            "progress": self.progress,
            "image_replacements": self.image_replacements,
            "auto_import_summary": self.last_auto_import_summary,
        }

    def inject_battle_hud_name_items(self, dataset: dict[str, Any]) -> None:
        categories = dataset.setdefault("categories", [])
        if not any(category.get("id") == BATTLE_HUD_NAME_CATEGORY_ID for category in categories):
            categories.append(
                {
                    "id": BATTLE_HUD_NAME_CATEGORY_ID,
                    "label": "전투 HUD 이름 테이블",
                    "description": "전투 화면 오른쪽 소형 8x8 폰트 이름 리소스",
                    "type": "hud_name_table",
                    "build_enabled": False,
                }
            )
        dataset.setdefault("items", []).extend(self.battle_hud_name_items())

    def battle_hud_name_item_id(self, item: dict[str, Any]) -> str:
        return f"{BATTLE_HUD_NAME_ITEM_PREFIX}{int(item.get('first_record_index', 0)):04d}"

    def battle_hud_name_items(self) -> list[dict[str, Any]]:
        output: list[dict[str, Any]] = []
        for item in self.battle_hud_name_table.get("unique_names", []):
            first_offset = item.get("first_name_offset_hex", "")
            try:
                offset = int(str(first_offset), 16)
            except ValueError:
                offset = None
            output.append(
                {
                    "item_id": self.battle_hud_name_item_id(item),
                    "category_id": BATTLE_HUD_NAME_CATEGORY_ID,
                    "group_id": item.get("translation_basis") or "battle_hud_name",
                    "source_group": BATTLE_HUD_NAME_CATEGORY_ID,
                    "source_order": item.get("first_record_index", 0),
                    "order_in_category": item.get("first_record_index", 0),
                    "offset": offset,
                    "text": item.get("decoded_name", ""),
                    "translation": item.get("korean_translation", ""),
                    "effective_translation": item.get("korean_translation", ""),
                    "agent_draft": "",
                    "agent_comment": "",
                    "manual_locked": False,
                    "notes": item.get("translation_note", ""),
                    "progress_status": item.get("progress_status") or ("done" if item.get("korean_translation") else "todo"),
                    "review_status": item.get("review_status") or ("issue" if item.get("translation_needs_review") else "checked"),
                    "expected_text_kind": "battle_hud_mini_font_name",
                    "translation_source": item.get("translation_basis", ""),
                    "translation_basis": item.get("translation_basis", ""),
                    "translation_needs_review": item.get("translation_needs_review", False),
                    "raw_bytes_hex": item.get("raw_bytes_hex", ""),
                    "record_indexes": item.get("record_indexes", []),
                    "first_record_index": item.get("first_record_index", 0),
                    "first_name_offset_hex": first_offset,
                    "byte_length": None,
                    "append_terminator": False,
                }
            )
        return output

    def save_battle_hud_name_item(self, item_id: str, updates: dict[str, Any]) -> dict[str, Any]:
        current_items = self.battle_hud_name_items()
        current = next((item for item in current_items if item["item_id"] == item_id), None)
        if not current:
            raise KeyError(item_id)

        payload_items: list[dict[str, Any]] = []
        if BATTLE_HUD_NAME_TRANSLATIONS_PATH.exists():
            payload = load_json(BATTLE_HUD_NAME_TRANSLATIONS_PATH)
            raw_items = payload.get("items", [])
            if isinstance(raw_items, list):
                payload_items = raw_items
        override_by_name = {
            item.get("decoded_name"): dict(item)
            for item in payload_items
            if isinstance(item, dict) and item.get("decoded_name")
        }

        for source in self.battle_hud_name_table.get("unique_names", []):
            name = source.get("decoded_name", "")
            if not name:
                continue
            entry = override_by_name.get(name) or {
                "decoded_name": name,
                "korean_translation": source.get("korean_translation", ""),
                "translation_basis": source.get("translation_basis", ""),
                "translation_needs_review": source.get("translation_needs_review", False),
                "translation_note": source.get("translation_note", ""),
                "progress_status": source.get("progress_status", "done" if source.get("korean_translation") else "todo"),
                "review_status": source.get("review_status", "issue" if source.get("translation_needs_review") else "checked"),
            }
            if self.battle_hud_name_item_id(source) == item_id:
                entry["korean_translation"] = updates.get("translation", current.get("translation", ""))
                entry["translation_note"] = updates.get("notes", current.get("notes", ""))
                entry["progress_status"] = updates.get("progress_status", current.get("progress_status", "done"))
                entry["review_status"] = updates.get("review_status", current.get("review_status", "checked"))
                entry["translation_needs_review"] = entry["review_status"] == "issue"
                if entry.get("translation_basis") in {"", "missing"} or entry["korean_translation"] != current.get("translation", ""):
                    entry["translation_basis"] = "gui_override"
            override_by_name[name] = entry

        ordered_items = [
            override_by_name[item.get("decoded_name")]
            for item in self.battle_hud_name_table.get("unique_names", [])
            if item.get("decoded_name") in override_by_name
        ]
        write_json(
            BATTLE_HUD_NAME_TRANSLATIONS_PATH,
            {
                "version": 1,
                "source_table": str(BATTLE_HUD_NAME_TABLE_PATH.relative_to(ROOT)),
                "items": ordered_items,
            },
        )
        subprocess.run(
            [sys.executable, "scripts/extract_battle_hud_name_table.py"],
            cwd=ROOT,
            text=True,
            capture_output=True,
            check=True,
        )
        self.battle_hud_name_table = self.load_battle_hud_name_table()
        saved = next((item for item in self.battle_hud_name_items() if item["item_id"] == item_id), None)
        if not saved:
            raise KeyError(item_id)
        return saved

    def merged_expansion_item(self, item: dict[str, Any]) -> dict[str, Any]:
        merged = dict(item)
        offset = item.get("offset")
        source_group = item.get("source_group", "")
        if offset is not None:
            expansion = self.expansion_opportunities.get((source_group, int(offset)))
            if expansion:
                merged.update(expansion)
        return merged

    def validate_translation_capacity(self, item: dict[str, Any], translation: str) -> None:
        if is_image_item(item) or not translation:
            return
        merged = self.merged_expansion_item(item)
        capacity = capacity_bytes(merged)
        if capacity is None or length_overflow_allowed(merged):
            return
        normalized = normalize_translation_text(
            translation,
            source_group=merged.get("source_group"),
            reference_text=merged.get("text"),
        )
        used = estimated_encoded_length(normalized) + terminator_length(merged)
        if used > capacity:
            item_id = merged.get("item_id", "<unknown>")
            raise ValueError(
                f"{item_id} 번역문이 고정 슬롯 용량을 초과했습니다: "
                f"{used}/{capacity} bytes "
                f"(종료 {terminator_length(merged)} byte 포함)."
            )

    def prepare_text_item_updates(self, item: dict[str, Any], updates: dict[str, Any]) -> dict[str, Any]:
        previous_translation = item.get("translation", "")
        source_group = item.get("source_group")
        item_updates = dict(updates)
        if "translation" in item_updates and isinstance(item_updates["translation"], str):
            item_updates["translation"] = normalize_translation_text(
                item_updates["translation"],
                source_group=source_group,
                reference_text=item.get("text"),
            )
        if "agent_draft" in item_updates and isinstance(item_updates["agent_draft"], str):
            item_updates["agent_draft"] = normalize_translation_text(
                item_updates["agent_draft"],
                source_group=source_group,
                reference_text=item.get("text"),
            )
            compact_agent_draft = item_updates["agent_draft"].replace(" ", "").replace("　", "")
            if "확인필요" in compact_agent_draft or "에군군의에" in item_updates["agent_draft"]:
                item_updates["agent_draft"] = item_updates.get("translation") or item.get("translation") or ""
        if "translation" in item_updates:
            candidate_item = dict(item)
            candidate_item.update(item_updates)
            self.validate_translation_capacity(candidate_item, item_updates.get("translation", ""))

        prepared: dict[str, Any] = {}
        current_agent_draft = item_updates.get("agent_draft", item.get("agent_draft", ""))
        for field in TEXT_SAVE_FIELDS:
            if field in item_updates:
                prepared[field] = item_updates[field]
        new_translation = prepared.get("translation", item.get("translation", ""))
        if (
            "translation" in item_updates
            and new_translation
            and new_translation != previous_translation
            and new_translation != current_agent_draft
            and not item_updates.get("manual_locked", False)
        ):
            prepared["manual_locked"] = True
        return prepared

    def apply_text_item_updates(self, item: dict[str, Any], prepared: dict[str, Any]) -> None:
        for field, value in prepared.items():
            item[field] = value

    def save_item(self, item_id: str, updates: dict[str, Any], sync_sources: bool = True) -> dict[str, Any]:
        if item_id.startswith(BATTLE_HUD_NAME_ITEM_PREFIX):
            return self.save_battle_hud_name_item(item_id, updates)
        items = self.dataset["items"]
        prepared_items: list[tuple[dict[str, Any], dict[str, Any]]] = []
        for item in items:
            if item["item_id"] == item_id:
                prepared_items.append((item, self.prepare_text_item_updates(item, updates)))
        if prepared_items:
            before_dataset = json.loads(json.dumps(self.dataset, ensure_ascii=False))
            for item, prepared in prepared_items:
                self.apply_text_item_updates(item, prepared)
            write_json(DATASET_PATH, self.dataset)
            try:
                if sync_sources:
                    self.sync_sources()
            except Exception:
                self.dataset = before_dataset
                write_json(DATASET_PATH, self.dataset)
                raise
            return prepared_items[0][0]
        raise KeyError(item_id)

    def save_items_batch(self, updates_list: list[dict[str, Any]], sync_sources: bool = True) -> list[dict[str, Any]]:
        if not updates_list:
            return []

        saved_special_items: list[dict[str, Any]] = []
        regular_updates: list[dict[str, Any]] = []
        for updates in updates_list:
            item_id = updates.get("item_id")
            if item_id and str(item_id).startswith(BATTLE_HUD_NAME_ITEM_PREFIX):
                saved_special_items.append(self.save_battle_hud_name_item(str(item_id), updates))
            else:
                regular_updates.append(updates)

        if not regular_updates:
            return saved_special_items

        before_dataset = json.loads(json.dumps(self.dataset, ensure_ascii=False))
        working_dataset = json.loads(json.dumps(self.dataset, ensure_ascii=False))
        saved_items: list[dict[str, Any]] = []

        for updates in regular_updates:
            item_id = updates.get("item_id")
            if not item_id:
                raise ValueError("item_id is required")
            matched = False
            first_saved: dict[str, Any] | None = None
            for item in working_dataset["items"]:
                if item["item_id"] != item_id:
                    continue
                matched = True
                prepared = self.prepare_text_item_updates(item, updates)
                self.apply_text_item_updates(item, prepared)
                if first_saved is None:
                    first_saved = item
            if not matched:
                raise KeyError(item_id)
            if first_saved is not None:
                saved_items.append(first_saved)

        self.dataset = working_dataset
        write_json(DATASET_PATH, self.dataset)
        try:
            if sync_sources:
                self.sync_sources()
        except Exception:
            self.dataset = before_dataset
            write_json(DATASET_PATH, self.dataset)
            raise
        return saved_items + saved_special_items

    def save_speaker(self, token: str, updates: dict[str, Any]) -> dict[str, Any]:
        for item in self.speakers:
            if item["dialogue_state_token"] == token:
                for field in ("speaker_id", "notes", "confirmed", "speaker_name", "speaker_role"):
                    if field in updates:
                        item[field] = updates[field]
                write_json(SPEAKERS_PATH, self.speakers)
                return item
        raise KeyError(token)

    def save_speaker_registry(self, payload: dict[str, Any]) -> dict[str, Any]:
        speaker_id = payload.get("speaker_id", "").strip()
        speaker_name = payload.get("speaker_name", "").strip()
        if not speaker_name:
            raise ValueError("speaker_name is required")
        if not speaker_id:
            speaker_id = f"speaker_{len(self.speaker_registry) + 1:03d}"

        for item in self.speaker_registry:
            if item["speaker_id"] == speaker_id:
                item["speaker_name"] = speaker_name
                item["speaker_role"] = payload.get("speaker_role", "")
                item["notes"] = payload.get("notes", "")
                write_json(SPEAKER_REGISTRY_PATH, self.speaker_registry)
                return item

        new_item = {
            "speaker_id": speaker_id,
            "speaker_name": speaker_name,
            "speaker_role": payload.get("speaker_role", ""),
            "notes": payload.get("notes", ""),
        }
        self.speaker_registry.append(new_item)
        write_json(SPEAKER_REGISTRY_PATH, self.speaker_registry)
        return new_item

    def save_progress(self, updates: dict[str, Any]) -> dict[str, Any]:
        for field in ("current_category_id", "current_item_id", "last_built_rom"):
            if field in updates:
                self.progress[field] = updates[field]
        write_json(PROGRESS_PATH, self.progress)
        return self.progress

    def save_image_item(self, item_id: str, updates: dict[str, Any]) -> dict[str, Any]:
        for item in self.image_replacements:
            if item["item_id"] == item_id:
                for field in (
                    "source_preview_path",
                    "source_download_path",
                    "reference_preview_path",
                    "replacement_path",
                    "previous_replacement_path",
                    "replacement_history",
                    "last_restore_report",
                    "last_restore_summary",
                    "comparison_notes",
                    "notes",
                    "progress_status",
                    "status",
                    "candidate_gallery",
                    "replacement_target",
                    "replacement_target_reason",
                    "image_group_id",
                    "image_group_label",
                    "image_group_order",
                    "tile_map_path",
                    "tile_columns",
                    "replacement_payload_base",
                    "replacement_source_color_map",
                    "replacement_verify_source_noop",
                    "replacement_direct_rle_tiles",
                    "replacement_native_patch_bbox",
                    "replacement_native_clear_bbox",
                    "replacement_tile_splits",
                    "screen_entry_manual_raw_patch_offsets",
                    "screen_entry_patch_tile_map_path",
                ):
                    if field in updates:
                        item[field] = updates[field]
                ensure_image_apply_defaults(item)
                write_json(IMAGE_REPLACEMENTS_PATH, self.image_replacements)
                for dataset_item in self.dataset["items"]:
                    if dataset_item["item_id"] == item_id:
                        dataset_item.update(item)
                        break
                write_json(DATASET_PATH, self.dataset)
                return item
        raise KeyError(item_id)

    def upload_image_item(self, item_id: str, filename: str, content_base64: str) -> dict[str, Any]:
        data = base64.b64decode(content_base64)
        item = next((entry for entry in self.image_replacements if entry["item_id"] == item_id), None)
        if not item:
            raise KeyError(item_id)
        if item_id in COMMON_HUD_RESERVED_ITEM_IDS:
            raise ValueError("0x00534874 tile 000 is a global blank/background tile and is protected from ROM replacement")

        dataset_item = next(
            (entry for entry in self.dataset["items"] if entry["item_id"] == item_id),
            None,
        )
        if not dataset_item:
            raise KeyError(item_id)

        safe_dir = UPLOADS_ROOT / item_id.replace(":", "_")
        safe_dir.mkdir(parents=True, exist_ok=True)
        output_path = safe_dir / Path(filename).name
        output_path.write_bytes(data)
        relative = str(output_path.relative_to(ROOT))
        previous = item.get("replacement_path", "")
        if previous and previous != relative:
            item["previous_replacement_path"] = previous
            history = item.setdefault("replacement_history", [])
            if isinstance(history, list):
                history.append(previous)
                del history[:-12]
        item["replacement_path"] = relative
        item["progress_status"] = "edited"
        ensure_image_apply_defaults(item)
        write_json(IMAGE_REPLACEMENTS_PATH, self.image_replacements)
        for dataset_item in self.dataset["items"]:
            if dataset_item["item_id"] == item_id:
                if previous and previous != relative:
                    dataset_item["previous_replacement_path"] = previous
                    history = dataset_item.setdefault("replacement_history", [])
                    if isinstance(history, list):
                        history.append(previous)
                        del history[:-12]
                dataset_item["replacement_path"] = relative
                dataset_item["progress_status"] = "edited"
                ensure_image_apply_defaults(dataset_item)
                break
        write_json(DATASET_PATH, self.dataset)
        apply_result = self.apply_image_replacements(item_id)
        item["last_apply_report"] = apply_result.get("report_path", "")
        item["last_apply_summary"] = apply_result.get("summary", {})
        write_json(IMAGE_REPLACEMENTS_PATH, self.image_replacements)
        return item

    def safe_upload_stem(self, filename: str, fallback: str) -> str:
        stem = Path(filename or fallback).stem or fallback
        safe = "".join(ch if ch.isalnum() or ch in "._-" else "_" for ch in stem)
        return (safe[:80] or fallback).strip("._-") or fallback

    def update_image_replacement_path(self, item: dict[str, Any], relative: str) -> None:
        previous = item.get("replacement_path", "")
        if previous and previous != relative:
            item["previous_replacement_path"] = previous
            history = item.setdefault("replacement_history", [])
            if isinstance(history, list):
                history.append(previous)
                del history[:-12]
        item["replacement_path"] = relative
        item["progress_status"] = "edited"
        ensure_image_apply_defaults(item)

    def upload_common_hud_tile_sheet(
        self,
        filename: str,
        content_base64: str,
        tile_ids: list[str],
        columns: int = 20,
        rows: int = 5,
    ) -> dict[str, Any]:
        from PIL import Image

        columns = int(columns or 20)
        rows = int(rows or 5)
        if columns <= 0 or rows <= 0:
            raise ValueError("columns/rows must be positive")
        slot_count = columns * rows
        if len(tile_ids) != slot_count:
            raise ValueError(f"tile_ids must contain exactly {slot_count} entries")

        expected_size = (columns * COMMON_HUD_TILE_SIZE, rows * COMMON_HUD_TILE_SIZE)
        data = base64.b64decode(content_base64)
        image = Image.open(BytesIO(data)).convert("RGBA")
        original_size = image.size
        active_slots = [
            {
                "slot_index": slot_index,
                "item_id": item_id,
                "column": slot_index % columns,
                "row": slot_index // columns,
            }
            for slot_index, item_id in enumerate(tile_ids)
            if item_id
        ]
        source_columns = columns
        source_rows = rows
        slot_source_indexes = {slot_index: slot_index for slot_index in range(slot_count)}
        upload_origin = {"column": 0, "row": 0}

        def image_matches_size(size: tuple[int, int]) -> tuple[bool, int, bool]:
            if image.size == size:
                return True, 1, False
            scale_x = image.size[0] // size[0] if size[0] else 0
            scale_y = image.size[1] // size[1] if size[1] else 0
            if (
                scale_x > 1
                and scale_x == scale_y
                and image.size[0] == size[0] * scale_x
                and image.size[1] == size[1] * scale_y
            ):
                return True, scale_x, True
            return False, 1, False

        if image.size != expected_size:
            matched, scale, resized = image_matches_size(expected_size)
            if not matched and active_slots:
                min_column = min(slot["column"] for slot in active_slots)
                max_column = max(slot["column"] for slot in active_slots)
                min_row = min(slot["row"] for slot in active_slots)
                max_row = max(slot["row"] for slot in active_slots)
                compact_columns = max_column - min_column + 1
                compact_rows = max_row - min_row + 1
                compact_size = (
                    compact_columns * COMMON_HUD_TILE_SIZE,
                    compact_rows * COMMON_HUD_TILE_SIZE,
                )
                compact_matched, compact_scale, compact_resized = image_matches_size(compact_size)
                if compact_matched:
                    source_columns = compact_columns
                    source_rows = compact_rows
                    expected_size = compact_size
                    upload_origin = {"column": min_column, "row": min_row}
                    slot_source_indexes = {
                        int(slot["slot_index"]): (int(slot["row"]) - min_row) * compact_columns
                        + (int(slot["column"]) - min_column)
                        for slot in active_slots
                    }
                    scale = compact_scale
                    resized = compact_resized
                    matched = True
            if not matched:
                raise ValueError(
                    f"sheet image size must be {expected_size[0]}x{expected_size[1]} or an integer scale of it"
                )
            if resized:
                image = image.resize(expected_size, Image.Resampling.NEAREST)

        sidecar_by_id = {item["item_id"]: item for item in self.image_replacements}
        dataset_by_id = {item["item_id"]: item for item in self.dataset.get("items", [])}
        upload_stem = self.safe_upload_stem(filename, "common_hud_tile_sheet")
        stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        updated_ids: list[str] = []
        updated_id_set: set[str] = set()
        skipped_ids: list[str] = []

        for slot_index, item_id in enumerate(tile_ids):
            if not item_id:
                continue
            if item_id in COMMON_HUD_RESERVED_ITEM_IDS:
                skipped_ids.append(item_id)
                continue
            item = sidecar_by_id.get(item_id)
            dataset_item = dataset_by_id.get(item_id)
            if not item or not dataset_item:
                raise KeyError(item_id)
            if item.get("category_id") not in HUD_TILE_CATEGORY_IDS:
                raise ValueError(f"{item_id} is not a HUD tile item")
            safe_dir = UPLOADS_ROOT / item_id.replace(":", "_")
            safe_dir.mkdir(parents=True, exist_ok=True)
            tile_hex = str(item.get("tile_index_hex") or "").replace("0x", "").replace("0X", "").upper()
            if not tile_hex:
                tile_hex = f"{int(item.get('tile_index', 0)):03X}"
            output_path = safe_dir / f"{upload_stem}_{stamp}_slot_{slot_index:03d}_tile_{tile_hex}.png"
            source_index = slot_source_indexes.get(slot_index)
            if source_index is None:
                continue
            x = (source_index % source_columns) * COMMON_HUD_TILE_SIZE
            y = (source_index // source_columns) * COMMON_HUD_TILE_SIZE
            tile = image.crop((x, y, x + COMMON_HUD_TILE_SIZE, y + COMMON_HUD_TILE_SIZE))
            tile.save(output_path)
            relative = str(output_path.relative_to(ROOT))
            self.update_image_replacement_path(item, relative)
            dataset_item.update(item)
            if item_id not in updated_id_set:
                updated_ids.append(item_id)
                updated_id_set.add(item_id)

        write_json(IMAGE_REPLACEMENTS_PATH, self.image_replacements)
        write_json(DATASET_PATH, self.dataset)
        apply_result = (
            self.apply_image_replacements(item_ids=updated_ids)
            if updated_ids
            else self.empty_image_apply_result()
        )
        report_path = apply_result.get("report_path", "")
        summary = apply_result.get("summary", {})
        for item_id in updated_ids:
            item = sidecar_by_id[item_id]
            item["last_apply_report"] = report_path
            item["last_apply_summary"] = summary
            dataset_by_id[item_id].update(item)
        write_json(IMAGE_REPLACEMENTS_PATH, self.image_replacements)
        write_json(DATASET_PATH, self.dataset)
        return {
            "ok": True,
            "updated_count": len(updated_ids),
            "skipped_count": len(set(skipped_ids)),
            "skipped_ids": sorted(set(skipped_ids)),
            "items": [sidecar_by_id[item_id] for item_id in updated_ids],
            "image_apply": apply_result,
            "expected_size": {"width": expected_size[0], "height": expected_size[1]},
            "original_size": {"width": original_size[0], "height": original_size[1]},
            "upload_layout": {
                "columns": source_columns,
                "rows": source_rows,
                "origin": upload_origin,
                "full_board_columns": columns,
                "full_board_rows": rows,
            },
        }

    def empty_image_apply_result(self) -> dict[str, Any]:
        return {
            "ok": True,
            "report_path": "",
            "summary": {
                "applied_count": 0,
                "stability_checks": {},
                "results": [],
            },
            "stdout": "",
            "stderr": "",
            "returncode": 0,
        }

    def apply_image_replacements(
        self,
        item_id: str | None = None,
        item_ids: list[str] | None = None,
    ) -> dict[str, Any]:
        report_path = WORKBENCH_DIR / "image_apply_report.json"
        command = [
            sys.executable,
            "scripts/apply_image_replacements.py",
            "--report",
            str(report_path),
        ]
        filters: list[str] = []
        if item_id:
            filters.append(item_id)
        if item_ids:
            filters.extend(str(value) for value in item_ids if value)
        if filters:
            for filtered_item_id in dict.fromkeys(filters):
                command.extend(["--item-id", filtered_item_id])
        completed = subprocess.run(
            command,
            cwd=ROOT,
            text=True,
            capture_output=True,
            check=False,
        )
        summary = load_json(report_path) if report_path.exists() else {}
        return {
            "ok": completed.returncode == 0,
            "report_path": str(report_path.relative_to(ROOT)),
            "summary": summary,
            "stdout": completed.stdout,
            "stderr": completed.stderr,
            "returncode": completed.returncode,
        }

    def restore_image_replacements(self, item_id: str | None = None) -> dict[str, Any]:
        before_dataset = json.loads(json.dumps(self.dataset, ensure_ascii=False))
        before_image_replacements = json.loads(json.dumps(self.image_replacements, ensure_ascii=False))
        before_progress = json.loads(json.dumps(self.progress, ensure_ascii=False))

        if item_id and not any(item["item_id"] == item_id for item in self.image_replacements):
            raise KeyError(item_id)

        restored: list[dict[str, Any]] = []
        restored_ids: set[str] = set()
        for item in self.image_replacements:
            if item_id and item["item_id"] != item_id:
                continue
            if item.get("replacement_target") is False:
                continue
            previous = str(item.get("replacement_path") or "").strip()
            if not previous:
                continue
            item["previous_replacement_path"] = previous
            history = item.setdefault("replacement_history", [])
            if isinstance(history, list):
                history.append(previous)
                del history[:-12]
            item["replacement_path"] = ""
            if item.get("progress_status") in {"edited", "ready_to_insert"}:
                item["progress_status"] = "candidate_found"
            ensure_image_apply_defaults(item)
            restored.append({"item_id": item["item_id"], "previous_replacement_path": previous})
            restored_ids.add(item["item_id"])

        for dataset_item in self.dataset["items"]:
            if dataset_item["item_id"] not in restored_ids:
                continue
            sidecar = next((item for item in self.image_replacements if item["item_id"] == dataset_item["item_id"]), None)
            if sidecar:
                dataset_item.update(sidecar)

        should_rebuild = bool(restored) or item_id is None
        if restored:
            write_json(IMAGE_REPLACEMENTS_PATH, self.image_replacements)
            write_json(DATASET_PATH, self.dataset)

        if not should_rebuild:
            return {
                "ok": True,
                "restored_count": 0,
                "restored": [],
                "rom_path": self.progress.get("last_built_rom", ""),
                "image_apply": {},
                "report_path": "",
            }

        try:
            rebuild_result = self.rebuild(None)
        except Exception:
            self.dataset = before_dataset
            self.image_replacements = before_image_replacements
            self.progress = before_progress
            write_json(DATASET_PATH, self.dataset)
            write_json(IMAGE_REPLACEMENTS_PATH, self.image_replacements)
            write_json(PROGRESS_PATH, self.progress)
            raise

        report = {
            "ok": True,
            "restored_count": len(restored),
            "restored": restored,
            "rom_path": rebuild_result.get("rom_path", self.progress.get("last_built_rom", "")),
            "image_apply": rebuild_result.get("image_apply", {}),
        }
        write_json(IMAGE_RESTORE_REPORT_PATH, report)
        report_relative = str(IMAGE_RESTORE_REPORT_PATH.relative_to(ROOT))
        summary = {
            "restored_count": len(restored),
            "rom_path": report["rom_path"],
            "remaining_image_apply": (report["image_apply"] or {}).get("summary", {}),
        }
        for item in self.image_replacements:
            if item["item_id"] in restored_ids:
                item["last_restore_report"] = report_relative
                item["last_restore_summary"] = summary
        for dataset_item in self.dataset["items"]:
            if dataset_item["item_id"] in restored_ids:
                sidecar = next((item for item in self.image_replacements if item["item_id"] == dataset_item["item_id"]), None)
                if sidecar:
                    dataset_item.update(sidecar)
        if restored:
            write_json(IMAGE_REPLACEMENTS_PATH, self.image_replacements)
            write_json(DATASET_PATH, self.dataset)
        report["report_path"] = report_relative
        return report

    def sync_sources(self) -> None:
        subprocess.run(
            [sys.executable, "scripts/sync_workbench_to_sources.py"],
            cwd=ROOT,
            text=True,
            capture_output=True,
            check=True,
        )

    def rebuild(self, category_id: str | None) -> dict[str, Any]:
        command = [sys.executable, "scripts/build_localization_review_rom.py"]
        if category_id:
            command.extend(["--category-id", category_id])
        completed = subprocess.run(
            command,
            cwd=ROOT,
            text=True,
            capture_output=True,
            check=True,
        )
        self.progress["last_built_rom"] = "patched_roms/current_review/hnr_localization_review.gba"
        image_apply = self.apply_image_replacements()
        write_json(PROGRESS_PATH, self.progress)
        return {
            "ok": True,
            "rom_path": self.progress["last_built_rom"],
            "stdout": completed.stdout,
            "image_apply": image_apply,
        }

    def import_translation_results(self, filename: str, content_base64: str) -> dict[str, Any]:
        data = base64.b64decode(content_base64)
        IMPORT_REPORT_DIR.mkdir(parents=True, exist_ok=True)
        import_path = IMPORT_REPORT_DIR / Path(filename).name
        import_path.write_bytes(data)
        report_path = IMPORT_REPORT_DIR / f"{import_path.stem}_import_report.json"
        command = [
            sys.executable,
            "scripts/import_translation_agent_results.py",
            str(import_path),
            "--report",
            str(report_path),
        ]
        completed = subprocess.run(
            command,
            cwd=ROOT,
            text=True,
            capture_output=True,
            check=True,
        )
        self.reload()
        report = load_json(report_path)
        return {
            "ok": True,
            "import_path": str(import_path.relative_to(ROOT)),
            "report_path": str(report_path.relative_to(ROOT)),
            "summary": report,
            "stdout": completed.stdout,
        }

    def auto_import_agent_results(self) -> dict[str, Any]:
        AGENT_INBOX_DIR.mkdir(parents=True, exist_ok=True)
        IMPORTED_AGENT_RESULTS_DIR.mkdir(parents=True, exist_ok=True)
        IMPORT_REPORT_DIR.mkdir(parents=True, exist_ok=True)

        imported_files: list[str] = []
        report_paths: list[str] = []

        for import_path in sorted(AGENT_INBOX_DIR.glob("*.json")):
            report_path = IMPORT_REPORT_DIR / f"{import_path.stem}_import_report.json"
            command = [
                sys.executable,
                "scripts/import_translation_agent_results.py",
                str(import_path),
                "--report",
                str(report_path),
            ]
            subprocess.run(
                command,
                cwd=ROOT,
                text=True,
                capture_output=True,
                check=True,
            )
            destination = IMPORTED_AGENT_RESULTS_DIR / import_path.name
            if destination.exists():
                destination.unlink()
            shutil.move(str(import_path), str(destination))
            imported_files.append(str(destination.relative_to(ROOT)))
            report_paths.append(str(report_path.relative_to(ROOT)))

        if imported_files:
            self.reload()

        self.last_auto_import_summary = {
            "imported_count": len(imported_files),
            "imported_files": imported_files,
            "report_paths": report_paths,
        }
        return self.last_auto_import_summary


def make_handler(store: WorkbenchStore):
    class Handler(BaseHTTPRequestHandler):
        def _json(self, payload: Any, status: int = 200) -> None:
            body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
            self.send_response(status)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)

        def _json_error(self, message: str, status: int = 400, **extra: Any) -> None:
            payload = {"ok": False, "error": message}
            payload.update(extra)
            self._json(payload, status)

        def do_GET(self) -> None:
            parsed = urllib.parse.urlparse(self.path)
            if parsed.path in ("/", "/index.html"):
                body = HTML.read_bytes()
                self.send_response(HTTPStatus.OK)
                self.send_header("Content-Type", "text/html; charset=utf-8")
                self.send_header("Content-Length", str(len(body)))
                self.end_headers()
                self.wfile.write(body)
                return
            if parsed.path == "/favicon.ico":
                self.send_response(HTTPStatus.NO_CONTENT)
                self.send_header("Content-Length", "0")
                self.end_headers()
                return
            if parsed.path == "/bundle":
                store.reload()
                self._json(store.bundle())
                return
            if parsed.path == "/workspace-file":
                params = urllib.parse.parse_qs(parsed.query)
                raw_path = params.get("path", [""])[0]
                if not raw_path:
                    self.send_error(HTTPStatus.BAD_REQUEST, "missing path")
                    return
                file_path = (ROOT / raw_path).resolve()
                if not file_path.is_file() or ROOT not in file_path.parents:
                    self.send_error(HTTPStatus.NOT_FOUND, "file not found")
                    return
                body = file_path.read_bytes()
                content_type, _ = mimetypes.guess_type(file_path.name)
                self.send_response(HTTPStatus.OK)
                self.send_header("Content-Type", content_type or "application/octet-stream")
                self.send_header("Content-Length", str(len(body)))
                self.end_headers()
                self.wfile.write(body)
                return
            self.send_error(HTTPStatus.NOT_FOUND, "not found")

        def do_POST(self) -> None:
            parsed = urllib.parse.urlparse(self.path)
            length = int(self.headers.get("Content-Length", "0"))
            try:
                payload = json.loads(self.rfile.read(length).decode("utf-8")) if length else {}
                if parsed.path == "/item":
                    result = store.save_item(
                        payload["item_id"],
                        payload,
                        sync_sources=payload.get("_sync_sources", True) is not False,
                    )
                    self._json(result)
                    return
                if parsed.path == "/items-batch":
                    result = store.save_items_batch(
                        payload.get("items", []),
                        sync_sources=payload.get("_sync_sources", True) is not False,
                    )
                    self._json({"ok": True, "items": result})
                    return
                if parsed.path == "/sync-sources":
                    store.sync_sources()
                    self._json({"ok": True})
                    return
                if parsed.path == "/speaker":
                    result = store.save_speaker(payload["dialogue_state_token"], payload)
                    self._json(result)
                    return
                if parsed.path == "/speaker-registry":
                    result = store.save_speaker_registry(payload)
                    self._json(result)
                    return
                if parsed.path == "/progress":
                    result = store.save_progress(payload)
                    self._json(result)
                    return
                if parsed.path == "/image-item":
                    result = store.save_image_item(payload["item_id"], payload)
                    self._json(result)
                    return
                if parsed.path == "/image-upload":
                    result = store.upload_image_item(
                        payload["item_id"],
                        payload["filename"],
                        payload["content_base64"],
                    )
                    self._json(result)
                    return
                if parsed.path == "/common-hud-tile-sheet-upload":
                    result = store.upload_common_hud_tile_sheet(
                        payload.get("filename", "common_hud_tile_sheet.png"),
                        payload["content_base64"],
                        payload.get("tile_ids", []),
                        int(payload.get("columns", 20)),
                        int(payload.get("rows", 5)),
                    )
                    self._json(result)
                    return
                if parsed.path == "/apply-images":
                    result = store.apply_image_replacements(payload.get("item_id"))
                    self._json(result)
                    return
                if parsed.path == "/restore-images":
                    result = store.restore_image_replacements(payload.get("item_id"))
                    self._json(result)
                    return
                if parsed.path == "/rebuild":
                    result = store.rebuild(payload.get("category_id"))
                    self._json(result)
                    return
                if parsed.path == "/import-translation-results":
                    result = store.import_translation_results(
                        payload["filename"],
                        payload["content_base64"],
                    )
                    self._json(result)
                    return
            except json.JSONDecodeError as exc:
                self._json_error(f"JSON 요청을 해석하지 못했습니다: {exc}", HTTPStatus.BAD_REQUEST)
                return
            except subprocess.CalledProcessError as exc:
                self._json_error(
                    exc.stderr or str(exc),
                    HTTPStatus.INTERNAL_SERVER_ERROR,
                    stdout=exc.stdout,
                    returncode=exc.returncode,
                )
                return
            except Exception as exc:
                self._json_error(str(exc), HTTPStatus.BAD_REQUEST)
                return

            self._json_error("not found", HTTPStatus.NOT_FOUND)

        def log_message(self, format: str, *args: Any) -> None:
            return

    return Handler


def main() -> int:
    args = parse_args()
    store = WorkbenchStore()
    server = ThreadingHTTPServer((args.host, args.port), make_handler(store))
    print(f"localization workbench: http://{args.host}:{args.port}")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
