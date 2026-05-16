#!/usr/bin/env python3

from __future__ import annotations

import argparse
import json
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_SOURCE = REPO_ROOT / "analysis" / "registry_a_entry8_prefixed_texts.json"
DEFAULT_CATALOG = REPO_ROOT / "analysis" / "registry_a_entry8_cluster_catalog.json"
DEFAULT_OUTPUT_DIR = REPO_ROOT / "analysis" / "translation_workspace" / "registry_a_entry8_clusters"
DEFAULT_MANIFEST = REPO_ROOT / "analysis" / "translation_workspace" / "registry_a_entry8_clusters_manifest.json"


def slugify(value: str) -> str:
    cleaned = "".join(ch.lower() if ch.isalnum() else "_" for ch in value)
    return cleaned.strip("_") or "untagged"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Registry A entry 8 추출본을 cluster 단위 번역 workset으로 분할합니다.")
    parser.add_argument("--source", default=str(DEFAULT_SOURCE))
    parser.add_argument("--catalog", default=str(DEFAULT_CATALOG))
    parser.add_argument("--output-dir", default=str(DEFAULT_OUTPUT_DIR))
    parser.add_argument("--manifest", default=str(DEFAULT_MANIFEST))
    return parser.parse_args()


def load_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def ensure_translation_record(record: dict[str, object], cluster: dict[str, object], source_name: str) -> dict[str, object]:
    entry = dict(record)
    entry.setdefault("translation", "")
    entry.setdefault("notes", "")
    entry["source_file"] = source_name
    entry["source_group"] = "registry_a_entry8_prefixed_texts"
    entry["cluster_index"] = cluster["cluster_index"]
    entry["cluster_primary_tag"] = cluster.get("primary_tag", "")
    entry["cluster_tags"] = cluster.get("tags", [])
    return entry


def main() -> int:
    args = parse_args()
    source_path = Path(args.source)
    catalog_path = Path(args.catalog)
    output_dir = Path(args.output_dir)
    manifest_path = Path(args.manifest)
    output_dir.mkdir(parents=True, exist_ok=True)
    manifest_path.parent.mkdir(parents=True, exist_ok=True)

    source_records = load_json(source_path)
    catalog = load_json(catalog_path)
    clusters = catalog["clusters"]
    source_name = source_path.name

    manifest_clusters: list[dict[str, object]] = []
    primary_tag_index: dict[str, list[str]] = {}

    for cluster in clusters:
        start = int(cluster["start_offset"])
        end = int(cluster["end_offset_exclusive"])
        members = [
            ensure_translation_record(record, cluster, source_name)
            for record in source_records
            if start <= int(record["offset"]) < end
        ]
        primary_tag = str(cluster.get("primary_tag", "untagged") or "untagged")
        slug = f"cluster_{int(cluster['cluster_index']):02d}_{slugify(primary_tag)}"
        output_path = output_dir / f"{slug}.json"
        output_path.write_text(json.dumps(members, ensure_ascii=False, indent=2), encoding="utf-8")

        primary_tag_index.setdefault(primary_tag, []).append(output_path.name)
        manifest_clusters.append(
            {
                "cluster_index": cluster["cluster_index"],
                "primary_tag": primary_tag,
                "tags": cluster.get("tags", []),
                "record_count": len(members),
                "range": {
                    "start_offset": start,
                    "end_offset_exclusive": end,
                },
                "first_text": cluster.get("first_text", ""),
                "last_text": cluster.get("last_text", ""),
                "sample_texts": cluster.get("sample_texts", []),
                "output_file": str(output_path.relative_to(REPO_ROOT)),
            }
        )

    payload = {
        "source": str(source_path.relative_to(REPO_ROOT)),
        "catalog": str(catalog_path.relative_to(REPO_ROOT)),
        "cluster_count": len(manifest_clusters),
        "output_dir": str(output_dir.relative_to(REPO_ROOT)),
        "clusters": manifest_clusters,
        "primary_tag_index": primary_tag_index,
    }
    manifest_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"cluster worksets: {output_dir}")
    print(f"manifest       : {manifest_path}")
    print(f"cluster_count  : {len(manifest_clusters)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
