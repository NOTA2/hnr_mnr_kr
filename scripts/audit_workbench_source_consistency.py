#!/usr/bin/env python3
"""Audit that saved GUI translations match their source JSON records."""

from __future__ import annotations

import json
import sys
from collections import Counter
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from gba_kor_tool.translation_normalization import normalize_translation_text


WORKBENCH_DATASET = ROOT / "confirmed_data" / "localization_workbench" / "workbench_dataset.json"
TRANSLATION_WORKSETS = ROOT / "confirmed_data" / "translation_worksets"
ENTRY8_CLUSTER_MANIFEST = ROOT / "confirmed_data" / "translation_workspace" / "registry_a_entry8_clusters_manifest.json"


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def record_key(record: dict[str, Any]) -> tuple[int, str, int]:
    return (
        int(record.get("offset", 0)),
        str(record.get("source_group", "")),
        int(record.get("source_order", 0)),
    )


def normalize(record: dict[str, Any], text: str) -> str:
    return normalize_translation_text(
        text,
        source_group=record.get("source_group"),
        reference_text=record.get("text"),
    )


def source_record_index() -> dict[tuple[str, tuple[int, str, int]], dict[str, Any]]:
    index: dict[tuple[str, tuple[int, str, int]], dict[str, Any]] = {}
    for path in sorted(TRANSLATION_WORKSETS.glob("translation_workset_*.json")):
        workset_id = path.stem
        payload = load_json(path)
        if not isinstance(payload, list):
            continue
        for record in payload:
            if isinstance(record, dict):
                index[(workset_id, record_key(record))] = record

    if ENTRY8_CLUSTER_MANIFEST.exists():
        manifest = load_json(ENTRY8_CLUSTER_MANIFEST)
        for cluster in manifest.get("clusters", []):
            output_file = cluster.get("output_file")
            if not output_file:
                continue
            cluster_id = Path(output_file).stem
            cluster_path = ROOT / output_file
            if not cluster_path.exists():
                continue
            payload = load_json(cluster_path)
            if not isinstance(payload, list):
                continue
            for record in payload:
                if isinstance(record, dict):
                    index[(cluster_id, record_key(record))] = record
    return index


def main() -> int:
    dataset = load_json(WORKBENCH_DATASET)
    source_index = source_record_index()
    issues: list[dict[str, Any]] = []
    for item in dataset.get("items", []):
        if not isinstance(item, dict):
            continue
        if item.get("type") == "image" or item.get("offset") is None:
            continue
        origin_id = item.get("origin_workset_id") or item.get("group_id")
        if not origin_id:
            continue
        source = source_index.get((str(origin_id), record_key(item)))
        if not source:
            continue
        gui_translation = normalize(item, item.get("translation", ""))
        source_translation = normalize(source, source.get("translation", ""))
        if gui_translation != source_translation:
            issues.append(
                {
                    "item_id": item.get("item_id"),
                    "origin": origin_id,
                    "source_group": item.get("source_group"),
                    "offset": int(item.get("offset", 0)),
                    "gui_translation": gui_translation,
                    "source_translation": source_translation,
                }
            )

    counts = Counter(issue["source_group"] for issue in issues)
    print(f"checked_items={len(dataset.get('items', []))}")
    print(f"source_mismatch_count={len(issues)}")
    for group, count in sorted(counts.items()):
        print(f"{group}={count}")
    for issue in issues[:50]:
        print(
            "MISMATCH\t"
            f"{issue['item_id']}\t"
            f"0x{issue['offset']:06X}\t"
            f"{issue['source_group']}\t"
            f"gui={issue['gui_translation']!r}\t"
            f"source={issue['source_translation']!r}"
        )
    return 1 if issues else 0


if __name__ == "__main__":
    raise SystemExit(main())
