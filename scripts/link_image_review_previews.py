#!/usr/bin/env python3

from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
WORKBENCH = ROOT / "confirmed_data" / "localization_workbench"
DATASET_PATH = WORKBENCH / "workbench_dataset.json"
IMAGE_REPLACEMENTS_PATH = WORKBENCH / "image_replacements.json"
CONTACT_INDEX = ROOT / "confirmed_data" / "image_inventory" / "workspaces" / "workspace_contact_sheets.json"


def read_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, payload) -> None:
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def main() -> int:
    contact_by_unit = {
        item["review_unit"]: item["path"]
        for item in read_json(CONTACT_INDEX)
        if item.get("review_unit") and item.get("path")
    }

    image_items = read_json(IMAGE_REPLACEMENTS_PATH)
    linked = 0
    for item in image_items:
        unit = item.get("group_id")
        preview = contact_by_unit.get(unit)
        if not preview:
            continue
        item["source_preview_path"] = preview
        item["source_download_path"] = preview
        if item.get("progress_status") in ("", "todo"):
            item["progress_status"] = "candidate_review"
        linked += 1
    write_json(IMAGE_REPLACEMENTS_PATH, image_items)

    dataset = read_json(DATASET_PATH)
    image_map = {item["item_id"]: item for item in image_items}
    for item in dataset.get("items", []):
        if item.get("category_id") != "image_review_units":
            continue
        sidecar = image_map.get(item["item_id"])
        if not sidecar:
            continue
        for field in ("source_preview_path", "source_download_path", "progress_status", "status"):
            if field in sidecar:
                item[field] = sidecar[field]
    write_json(DATASET_PATH, dataset)

    print(f"linked image preview paths: {linked}")
    print(f"image sidecar: {IMAGE_REPLACEMENTS_PATH}")
    print(f"dataset      : {DATASET_PATH}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
