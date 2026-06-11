#!/usr/bin/env python3
"""Build an item-level image source manifest for cleanup decisions."""

from __future__ import annotations

import argparse
import json
from collections import Counter
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_IMAGE_REPLACEMENTS = ROOT / "confirmed_data/localization_workbench/image_replacements.json"
DEFAULT_OUTPUT = ROOT / "confirmed_data/image_inventory/image_source_manifest.json"


def load_json(path: Path) -> Any:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def write_json(path: Path, data: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def project_path(value: str) -> Path:
    path = Path(value)
    return path if path.is_absolute() else ROOT / path


def exists(value: str) -> bool:
    return bool(value) and project_path(value).exists()


def path_family(value: str) -> str:
    if not value:
        return "none"
    parts = Path(value).parts
    if len(parts) >= 4 and parts[:3] == ("confirmed_data", "image_inventory", "edit_packs"):
        return "/".join(parts[:4])
    if len(parts) >= 4 and parts[:3] == ("confirmed_data", "image_inventory", "runtime_tile_matches"):
        return "/".join(parts[:4])
    if len(parts) >= 4 and parts[:3] == ("confirmed_data", "image_inventory", "runtime_rle_screen_order"):
        return "/".join(parts[:4])
    if len(parts) >= 4 and parts[:3] == ("confirmed_data", "image_inventory", "runtime_rle_patch_previews"):
        return "/".join(parts[:4])
    if len(parts) >= 3 and parts[:2] == ("confirmed_data", "localization_workbench"):
        return "/".join(parts[:3])
    return "/".join(parts[:3]) if len(parts) >= 3 else value


def classify_source(value: str) -> str:
    if not value:
        return "none"
    if value.startswith("confirmed_data/image_inventory/edit_packs/"):
        return "edit_pack_source"
    if value.startswith("confirmed_data/image_inventory/runtime_tile_matches/"):
        return "runtime_match_preview"
    if value.startswith("confirmed_data/image_inventory/runtime_rle_screen_order/"):
        return "runtime_screen_order_evidence"
    if value.startswith("confirmed_data/image_inventory/runtime_rle_patch_previews/"):
        return "runtime_patch_preview"
    return "unknown_source_role"


def classify_replacement(value: str) -> str:
    if not value:
        return "no_replacement_yet"
    if value.startswith("confirmed_data/localization_workbench/uploaded_image_replacements/"):
        return "uploaded_replacement"
    if value.startswith("confirmed_data/image_inventory/edit_packs/"):
        return "edit_pack_direct_patch_asset"
    return "unknown_replacement_role"


def keep_reason(item: dict[str, Any], source_role: str, replacement_role: str) -> str:
    status = item.get("progress_status")
    if replacement_role != "no_replacement_yet":
        return "active replacement asset referenced by GUI state"
    if status == "candidate_found":
        return f"candidate source/reference path for {source_role}"
    return "image workflow item referenced by GUI state"


def build_manifest(image_replacements: list[dict[str, Any]]) -> dict[str, Any]:
    items: list[dict[str, Any]] = []
    status_counts: Counter[str] = Counter()
    category_counts: Counter[str] = Counter()
    source_role_counts: Counter[str] = Counter()
    replacement_role_counts: Counter[str] = Counter()
    source_family_counts: Counter[str] = Counter()
    replacement_family_counts: Counter[str] = Counter()
    missing_paths: list[dict[str, str]] = []

    for item in sorted(image_replacements, key=lambda row: (str(row.get("category_id")), str(row.get("item_id")))):
        item_id = str(item.get("item_id") or "")
        category_id = str(item.get("category_id") or "")
        progress_status = str(item.get("progress_status") or "")
        replacement_path = str(item.get("replacement_path") or "").strip()
        source_download_path = str(item.get("source_download_path") or "").strip()
        source_preview_path = str(item.get("source_preview_path") or "").strip()
        source_role = classify_source(source_download_path or source_preview_path)
        replacement_role = classify_replacement(replacement_path)

        row = {
            "item_id": item_id,
            "category_id": category_id,
            "progress_status": progress_status,
            "replacement_target": item.get("replacement_target"),
            "replacement_path": replacement_path,
            "replacement_exists": exists(replacement_path) if replacement_path else None,
            "replacement_role": replacement_role,
            "source_download_path": source_download_path,
            "source_download_exists": exists(source_download_path) if source_download_path else None,
            "source_preview_path": source_preview_path,
            "source_preview_exists": exists(source_preview_path) if source_preview_path else None,
            "source_role": source_role,
            "source_family": path_family(source_download_path or source_preview_path),
            "replacement_family": path_family(replacement_path),
            "keep_reason": keep_reason(item, source_role, replacement_role),
        }
        items.append(row)

        status_counts[progress_status] += 1
        category_counts[category_id] += 1
        source_role_counts[source_role] += 1
        replacement_role_counts[replacement_role] += 1
        source_family_counts[row["source_family"]] += 1
        replacement_family_counts[row["replacement_family"]] += 1

        for field in ("replacement_path", "source_download_path", "source_preview_path"):
            value = row[field]
            exists_key = field.replace("_path", "_exists")
            if value and row[exists_key] is False:
                missing_paths.append({"item_id": item_id, "field": field, "path": value})

    summary = {
        "total_items": len(items),
        "status_counts": dict(sorted(status_counts.items())),
        "category_counts": dict(sorted(category_counts.items())),
        "source_role_counts": dict(sorted(source_role_counts.items())),
        "replacement_role_counts": dict(sorted(replacement_role_counts.items())),
        "source_family_counts": dict(sorted(source_family_counts.items())),
        "replacement_family_counts": dict(sorted(replacement_family_counts.items())),
        "missing_path_count": len(missing_paths),
        "missing_paths": missing_paths[:50],
    }
    return {
        "version": 1,
        "generated_from": [
            "confirmed_data/localization_workbench/image_replacements.json",
        ],
        "purpose": "cleanup safety manifest for active GUI image replacement paths",
        "summary": summary,
        "items": items,
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--image-replacements", type=Path, default=DEFAULT_IMAGE_REPLACEMENTS)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    image_replacements = load_json(args.image_replacements)
    if not isinstance(image_replacements, list):
        raise SystemExit(f"expected list: {args.image_replacements}")
    manifest = build_manifest(image_replacements)
    write_json(args.output, manifest)
    summary = manifest["summary"]
    print(f"wrote {args.output.relative_to(ROOT)}")
    print(f"items: {summary['total_items']}")
    print(f"missing paths: {summary['missing_path_count']}")
    return 0 if summary["missing_path_count"] == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
