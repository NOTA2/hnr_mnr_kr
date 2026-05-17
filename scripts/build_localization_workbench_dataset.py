#!/usr/bin/env python3

from __future__ import annotations

import json
from collections import defaultdict
from datetime import date
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DATA_ROOT = ROOT / "confirmed_data"
WORKSPACE_ROOT = DATA_ROOT / "localization_workbench"
TRANSLATION_WORKSETS = DATA_ROOT / "translation_worksets"
TRANSLATION_WORKSPACE = DATA_ROOT / "translation_workspace"
DIALOGUE_METADATA = DATA_ROOT / "dialogue_metadata"
IMAGE_INVENTORY = DATA_ROOT / "image_inventory"
FONT_PROFILE = DATA_ROOT / "font_assets" / "active_hangul_font_profile.json"

OUT_DATASET = WORKSPACE_ROOT / "workbench_dataset.json"
OUT_SPEAKERS = WORKSPACE_ROOT / "speaker_aliases.json"
OUT_SPEAKER_REGISTRY = WORKSPACE_ROOT / "speaker_registry.json"
OUT_PROGRESS = WORKSPACE_ROOT / "progress_state.json"
OUT_IMAGE = WORKSPACE_ROOT / "image_replacements.json"
OUT_README = WORKSPACE_ROOT / "README.md"


def load_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def load_json_if_exists(path: Path, fallback):
    if path.exists():
        return load_json(path)
    return fallback


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
            "id": "translation_workset_core_ui",
            "label": "코어 UI",
            "type": "text",
            "sort_order": 0,
            "path": "confirmed_data/translation_worksets/translation_workset_core_ui.json",
            "description": "시스템/세이브/지역명/UI 기술명/시작 카드 고정 슬롯",
            "build_enabled": True,
        },
        {
            "id": "translation_workset_gameplay_terms",
            "label": "게임 용어",
            "type": "text",
            "sort_order": 1,
            "path": "confirmed_data/translation_worksets/translation_workset_gameplay_terms.json",
            "description": "아이템/전투/능력/재료/설명",
            "build_enabled": True,
        },
        {
            "id": "translation_workset_registry_d_dialogue",
            "label": "대사 Registry D",
            "type": "dialogue",
            "sort_order": 2,
            "path": "confirmed_data/translation_worksets/translation_workset_registry_d_dialogue.json",
            "description": "튜토리얼/이벤트/전투 전후 대사",
            "build_enabled": True,
        },
        {
            "id": "registry_a_entry8_clusters_manifest",
            "label": "대사 Entry8",
            "type": "dialogue",
            "sort_order": 3,
            "path": "confirmed_data/translation_workspace/registry_a_entry8_clusters_manifest.json",
            "description": "대형 스토리/이벤트 뱅크 cluster 단위",
            "build_enabled": True,
        },
        {
            "id": "image_review_units",
            "label": "이미지 작업",
            "type": "image",
            "sort_order": 4,
            "path": "confirmed_data/image_inventory/image_text_inventory.json",
            "description": "이미지에 구워진 텍스트 자산 검토/교체",
            "build_enabled": False,
        },
    ]


def build_text_items(dialogue_tokens: dict[str, dict[int, str]], entry8_cluster_map: dict[int, str]) -> list[dict]:
    items: list[dict] = []
    workset_specs = [
        ("translation_workset_startup_font_showcase.json", "translation_workset_core_ui"),
        ("translation_workset_core_ui.json", "translation_workset_core_ui"),
        ("translation_workset_gameplay_terms.json", "translation_workset_gameplay_terms"),
        ("translation_workset_registry_d_dialogue.json", "translation_workset_registry_d_dialogue"),
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
            items.append(
                {
                    "item_id": item_id,
                    "category_id": category_id,
                    "origin_workset_id": workset_id,
                    "group_id": cluster_id,
                    "offset": offset,
                    "rom_address": int(record["rom_address"]),
                    "byte_length": int(record["byte_length"]),
                    "source_group": source_group,
                    "source_file": record["source_file"],
                    "source_order": int(record["source_order"]),
                    "order_in_category": order,
                    "text": record["text"],
                    "translation": record.get("translation", ""),
                    "agent_draft": "",
                    "agent_comment": "",
                    "manual_locked": False,
                    "effective_translation": record.get("translation", ""),
                    "translation_source": "seed" if record.get("translation") else "original",
                    "notes": record.get("notes", ""),
                    "terminator": record.get("terminator"),
                    "append_terminator": record.get("append_terminator"),
                    "unknown_tokens": record.get("unknown_tokens"),
                    "anchor": record.get("anchor"),
                    "before_bytes": record.get("before_bytes"),
                    "after_bytes": record.get("after_bytes"),
                    "dialogue_state_token": dialogue_state_token,
                    "progress_status": "todo",
                    "review_status": "unreviewed",
                    "image_overlap_risk": "low" if workset_id != "translation_workset_core_ui" else "medium",
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
            items.append(
                {
                    "item_id": item_id,
                    "category_id": "registry_a_entry8_clusters_manifest",
                    "group_id": cluster_id,
                    "offset": offset,
                    "rom_address": int(record["rom_address"]),
                    "byte_length": int(record["byte_length"]),
                    "source_group": record["source_group"],
                    "source_file": record["source_file"],
                    "source_order": int(record.get("source_order", cluster.get("cluster_index", 0))),
                    "order_in_category": order,
                    "text": record["text"],
                    "translation": record.get("translation", ""),
                    "agent_draft": "",
                    "agent_comment": "",
                    "manual_locked": False,
                    "effective_translation": record.get("translation", ""),
                    "translation_source": "seed" if record.get("translation") else "original",
                    "notes": record.get("notes", ""),
                    "terminator": record.get("terminator"),
                    "append_terminator": record.get("append_terminator"),
                    "unknown_tokens": record.get("unknown_tokens", 0),
                    "anchor": record.get("anchor"),
                    "before_bytes": record.get("before_bytes"),
                    "after_bytes": record.get("after_bytes"),
                    "dialogue_state_token": dialogue_tokens.get("registry_a_entry8_prefixed_texts", {}).get(offset),
                    "progress_status": "todo",
                    "review_status": "unreviewed",
                    "cluster_primary_tag": cluster.get("primary_tag"),
                    "cluster_label": cluster_id,
                    "image_overlap_risk": "low",
                }
            )

    return items


def build_image_items() -> list[dict]:
    inventory = load_json(IMAGE_INVENTORY / "image_text_inventory.json")
    items: list[dict] = []
    for unit in inventory["review_units"]:
        items.append(
            {
                "item_id": f"image:{unit['id']}",
                "category_id": "image_review_units",
                "group_id": unit["id"],
                "label": unit["id"],
                "status": unit["status"],
                "priority": unit["priority"],
                "review_order": unit["review_order"],
                "review_goal": unit["review_goal"],
                "recommended_probe_method": unit["recommended_probe_method"],
                "future_workspace": unit["future_workspace"],
                "expected_text_kind": unit["expected_text_kind"],
                "notes": "\n".join(unit["notes"]),
                "subunits": unit["subunits"],
                "future_workspace": unit["future_workspace"],
                "source_preview_path": "",
                "source_download_path": "",
                "replacement_path": "",
                "comparison_notes": "",
                "progress_status": "todo",
            }
        )
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
            "speaker_id": "",
            "notes": "",
            "confirmed": False,
            "speaker_name": "",
            "speaker_role": "",
        }
        for token in tokens
    ]


def build_speaker_registry(existing: list[dict] | None) -> list[dict]:
    if existing:
        return existing
    return []


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
        for field in (
            "translation",
            "agent_draft",
            "agent_comment",
            "manual_locked",
            "effective_translation",
            "translation_source",
            "notes",
            "progress_status",
            "review_status",
            "replacement_path",
            "source_preview_path",
            "source_download_path",
            "comparison_notes",
            "status",
        ):
            if field in existing and existing[field] not in ("", None):
                item[field] = existing[field]


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
            "시작 카드 4줄은 별도 카테고리로 분리하지 않고 코어 UI 안에서 함께 관리한다.",
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
    existing_dataset = load_json_if_exists(OUT_DATASET, None)
    existing_speakers = load_json_if_exists(OUT_SPEAKERS, None)
    existing_speaker_registry = load_json_if_exists(OUT_SPEAKER_REGISTRY, None)
    existing_progress = load_json_if_exists(OUT_PROGRESS, None)
    existing_images = load_json_if_exists(OUT_IMAGE, None)
    dataset = build_dataset()
    merge_existing_item_state(dataset["items"], existing_dataset, existing_images)
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
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
