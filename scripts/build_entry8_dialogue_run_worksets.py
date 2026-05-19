#!/usr/bin/env python3

from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
RUNS_PATH = ROOT / "confirmed_data" / "dialogue_metadata" / "entry8_dialogue_state_runs.json"
CLUSTER_MANIFEST_PATH = ROOT / "confirmed_data" / "translation_workspace" / "registry_a_entry8_clusters_manifest.json"
OUT_DIR = ROOT / "confirmed_data" / "translation_workspace" / "registry_a_entry8_runs"
OUT_MANIFEST = ROOT / "confirmed_data" / "translation_workspace" / "registry_a_entry8_runs_manifest.json"


def load_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, payload: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def join_lines(values: list[str]) -> str:
    return "\n".join(value for value in values if value)


def build_record_index(cluster_manifest: dict) -> dict[int, dict]:
    records_by_offset: dict[int, dict] = {}
    for cluster in cluster_manifest["clusters"]:
        cluster_path = ROOT / cluster["output_file"]
        for record in load_json(cluster_path):
            records_by_offset[int(record["offset"])] = record
    return records_by_offset


def build_run_record(cluster_index: int, run_index: int, run: dict, records_by_offset: dict[int, dict]) -> dict:
    records = []
    for compact in run["records"]:
        offset = int(compact["offset"])
        source = records_by_offset[offset]
        records.append(
            {
                "offset": offset,
                "header_offset": source.get("header_offset"),
                "char_count": source.get("char_count"),
                "byte_length": source.get("byte_length"),
                "control_gap_length": compact.get("control_gap_length"),
                "text": source.get("text", ""),
                "translation": source.get("translation", ""),
            }
        )

    return {
        "run_id": f"entry8_cluster_{cluster_index:02d}_run_{run_index:04d}",
        "cluster_index": cluster_index,
        "run_index": run_index,
        "dialogue_state_token": run.get("dialogue_state_token"),
        "record_count": len(records),
        "offsets": [record["offset"] for record in records],
        "source_text": join_lines([record["text"] for record in records]),
        "translation_text": join_lines([record["translation"] for record in records]),
        "records": records,
        "notes": "",
    }


def main() -> int:
    runs_data = load_json(RUNS_PATH)
    cluster_manifest = load_json(CLUSTER_MANIFEST_PATH)
    records_by_offset = build_record_index(cluster_manifest)

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    manifest_clusters = []
    total_runs = 0
    total_records = 0
    multi_record_runs = 0

    for cluster in runs_data["clusters"]:
        cluster_index = int(cluster["cluster_index"])
        primary_tag = cluster.get("primary_tag", "")
        run_records = [
            build_run_record(cluster_index, run_index, run, records_by_offset)
            for run_index, run in enumerate(cluster["runs"])
        ]
        output_file = OUT_DIR / f"cluster_{cluster_index:02d}_{primary_tag or 'untagged'}_runs.json"
        write_json(output_file, run_records)

        run_count = len(run_records)
        record_count = sum(run["record_count"] for run in run_records)
        cluster_multi = sum(1 for run in run_records if run["record_count"] >= 2)
        total_runs += run_count
        total_records += record_count
        multi_record_runs += cluster_multi
        manifest_clusters.append(
            {
                "cluster_index": cluster_index,
                "primary_tag": primary_tag,
                "run_count": run_count,
                "record_count": record_count,
                "multi_record_run_count": cluster_multi,
                "output_file": str(output_file.relative_to(ROOT)),
            }
        )

    write_json(
        OUT_MANIFEST,
        {
            "source": str(RUNS_PATH.relative_to(ROOT)),
            "cluster_manifest": str(CLUSTER_MANIFEST_PATH.relative_to(ROOT)),
            "output_dir": str(OUT_DIR.relative_to(ROOT)),
            "cluster_count": len(manifest_clusters),
            "run_count": total_runs,
            "record_count": total_records,
            "multi_record_run_count": multi_record_runs,
            "clusters": manifest_clusters,
            "notes": [
                "Entry8 조각 레코드를 dialogue_state run 단위로 묶은 번역 QA 산출물이다.",
                "ROM 삽입은 Registry A entry 8 packed relocation 이 담당하고, 이 파일들은 박스/체인 단위 검수에 쓴다.",
            ],
        },
    )
    print(f"wrote {OUT_MANIFEST}")
    print(f"runs={total_runs} records={total_records} multi_record_runs={multi_record_runs}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
