#!/usr/bin/env python3

from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
WORKBENCH_DATASET = ROOT / "confirmed_data" / "localization_workbench" / "workbench_dataset.json"
TRANSLATION_WORKSETS = ROOT / "confirmed_data" / "translation_worksets"
TRANSLATION_WORKSPACE = ROOT / "confirmed_data" / "translation_workspace"


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


def build_source_index(items: list[dict]) -> dict[tuple[str, int, str, int], dict]:
    index: dict[tuple[str, int, str, int], dict] = {}
    for item in items:
        if item.get("offset") is None or not item.get("source_file"):
            continue
        key = (
            item["source_file"],
            *build_record_key(item),
        )
        index[key] = item
    return index


def build_workset_index(items: list[dict]) -> dict[str, dict[tuple[int, str, int], dict]]:
    index: dict[str, dict[tuple[int, str, int], dict]] = {}
    for item in items:
        workset_id = item.get("origin_workset_id")
        if not workset_id:
            continue
        index.setdefault(workset_id, {})[build_record_key(item)] = item
    return index


def build_cluster_index(items: list[dict]) -> dict[str, dict[tuple[int, str, int], dict]]:
    index: dict[str, dict[tuple[int, str, int], dict]] = {}
    for item in items:
        if item.get("category_id") != "registry_a_entry8_clusters_manifest" or not item.get("group_id"):
            continue
        index.setdefault(item["group_id"], {})[build_record_key(item)] = item
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
        new_translation = item.get("translation", "")
        if record.get("translation", "") != new_translation:
            record["translation"] = new_translation
            changed += 1
    if changed:
        write_json(path, payload)
    return changed


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
        new_translation = item.get("translation", "")
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
        path = ROOT / source_file
        changed = sync_record_list(path, source_file, source_index)
        if changed:
            changed_files[source_file] = changed

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
        changed = sync_record_list_by_group(path, cluster_id, cluster_index)
        if changed:
            changed_files[source_file] = changed

    print(f"synced_files={len(changed_files)}")
    for filename, changed in sorted(changed_files.items()):
        print(f"{filename}: {changed}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
