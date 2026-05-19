#!/usr/bin/env python3

from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from gba_kor_tool.translation_normalization import normalize_translation_text

WORKBENCH_DATASET = ROOT / "confirmed_data" / "localization_workbench" / "workbench_dataset.json"
TRANSLATION_WORKSETS = ROOT / "confirmed_data" / "translation_worksets"
TRANSLATION_WORKSPACE = ROOT / "confirmed_data" / "translation_workspace"
EXTRACTED_TEXTS = ROOT / "confirmed_data" / "extracted_texts"


def load_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, payload) -> None:
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def build_record_key(record: dict) -> tuple[int, str, int]:
    return (
        int(record.get("offset", 0)),
        record.get("source_group", ""),
        int(record.get("source_order", 0)),
    )


def build_cluster_record_key(record: dict) -> tuple[int, str]:
    return (
        int(record.get("offset", 0)),
        record.get("source_group", ""),
    )


def build_source_index(items: list[dict]) -> dict[tuple[str, int, str, int], dict]:
    index: dict[tuple[str, int, str, int], dict] = {}
    for item in items:
        if item.get("offset") is None or not item.get("source_file"):
            continue
        source_file = item["source_file"]
        source_basename = Path(source_file).name
        key = (
            source_file,
            *build_record_key(item),
        )
        index[key] = item
        if item.get("source_group") == "registry_a_entry8_prefixed_texts":
            index[
                (
                    source_file,
                    int(item.get("offset", 0)),
                    item.get("source_group", ""),
                    0,
                )
            ] = item
        if source_basename != source_file:
            continue
        canonical_path = EXTRACTED_TEXTS / source_basename
        if canonical_path.exists():
            canonical_key = (
                str(canonical_path.relative_to(ROOT)),
                *build_record_key(item),
            )
            index.setdefault(canonical_key, item)
            if item.get("source_group") == "registry_a_entry8_prefixed_texts":
                index.setdefault(
                    (
                        str(canonical_path.relative_to(ROOT)),
                        int(item.get("offset", 0)),
                        item.get("source_group", ""),
                        0,
                    ),
                    item,
                )
    return index


def build_workset_index(items: list[dict]) -> dict[str, dict[tuple[int, str, int], dict]]:
    index: dict[str, dict[tuple[int, str, int], dict]] = {}
    for item in items:
        workset_id = item.get("origin_workset_id")
        if not workset_id:
            continue
        index.setdefault(workset_id, {})[build_record_key(item)] = item
    return index


def build_cluster_index(items: list[dict]) -> dict[str, dict[tuple[int, str], dict]]:
    index: dict[str, dict[tuple[int, str], dict]] = {}
    for item in items:
        if item.get("category_id") != "registry_a_entry8_clusters_manifest" or not item.get("group_id"):
            continue
        index.setdefault(item["group_id"], {})[build_cluster_record_key(item)] = item
    return index


def sync_record_list(path: Path, source_file_key: str, index: dict[tuple[str, int, str, int], dict]) -> int:
    if not path.exists():
        return 0

    payload = load_json(path)
    if not isinstance(payload, list):
        return 0

    changed = 0
    for record in payload:
        key = (
            source_file_key,
            *build_record_key(record),
        )
        item = index.get(key)
        if not item:
            continue
        new_translation = normalize_translation_text(
            item.get("translation", ""),
            source_group=item.get("source_group"),
            reference_text=record.get("text") or item.get("text"),
        )
        if record.get("translation", "") != new_translation:
            record["translation"] = new_translation
            changed += 1
    if changed:
        write_json(path, payload)
    return changed


def resolve_source_file(source_file: str) -> tuple[Path, str]:
    path = ROOT / source_file
    if path.exists():
        return path, source_file
    extracted_path = EXTRACTED_TEXTS / Path(source_file).name
    if extracted_path.exists():
        return extracted_path, str(extracted_path.relative_to(ROOT))
    return path, source_file


def sync_record_list_by_group(path: Path, group_key: str, index: dict[str, dict[tuple[int, str, int], dict]]) -> int:
    if not path.exists():
        return 0

    payload = load_json(path)
    if not isinstance(payload, list):
        return 0

    group_index = index.get(group_key, {})
    changed = 0
    for record in payload:
        item = group_index.get(build_record_key(record))
        if not item:
            continue
        new_translation = normalize_translation_text(
            item.get("translation", ""),
            source_group=item.get("source_group"),
            reference_text=record.get("text") or item.get("text"),
        )
        if record.get("translation", "") != new_translation:
            record["translation"] = new_translation
            changed += 1
    if changed:
        write_json(path, payload)
    return changed


def sync_cluster_record_list_by_group(path: Path, group_key: str, index: dict[str, dict[tuple[int, str], dict]]) -> int:
    if not path.exists():
        return 0

    payload = load_json(path)
    if not isinstance(payload, list):
        return 0

    group_index = index.get(group_key, {})
    changed = 0
    for record in payload:
        item = group_index.get(build_cluster_record_key(record))
        if not item:
            continue
        new_translation = normalize_translation_text(
            item.get("translation", ""),
            source_group=item.get("source_group"),
            reference_text=record.get("text") or item.get("text"),
        )
        if record.get("translation", "") != new_translation:
            record["translation"] = new_translation
            changed += 1
    if changed:
        write_json(path, payload)
    return changed


def main() -> int:
    dataset = load_json(WORKBENCH_DATASET)
    items = dataset.get("items", [])
    source_index = build_source_index(items)
    workset_index = build_workset_index(items)
    cluster_index = build_cluster_index(items)

    changed_files: dict[str, int] = {}

    source_files = sorted({item["source_file"] for item in items if item.get("source_file")})
    for source_file in source_files:
        path, source_file_key = resolve_source_file(source_file)
        changed = sync_record_list(path, source_file_key, source_index)
        if changed:
            changed_files[source_file_key] = changed

    workset_ids = sorted(
        {
            item["origin_workset_id"]
            for item in items
            if item.get("origin_workset_id")
            and (TRANSLATION_WORKSETS / f"{item['origin_workset_id']}.json").exists()
        }
    )
    for workset_id in workset_ids:
        source_file = f"confirmed_data/translation_worksets/{workset_id}.json"
        path = ROOT / source_file
        changed = sync_record_list_by_group(path, workset_id, workset_index)
        if changed:
            changed_files[source_file] = changed

    cluster_ids = sorted(
        {
            item["group_id"]
            for item in items
            if item.get("category_id") == "registry_a_entry8_clusters_manifest" and item.get("group_id")
        }
    )
    cluster_root = TRANSLATION_WORKSPACE / "registry_a_entry8_clusters"
    for cluster_id in cluster_ids:
        source_file = f"confirmed_data/translation_workspace/registry_a_entry8_clusters/{cluster_id}.json"
        path = cluster_root / f"{cluster_id}.json"
        changed = sync_cluster_record_list_by_group(path, cluster_id, cluster_index)
        if changed:
            changed_files[source_file] = changed

    print(f"synced_files={len(changed_files)}")
    for filename, changed in sorted(changed_files.items()):
        print(f"{filename}: {changed}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
