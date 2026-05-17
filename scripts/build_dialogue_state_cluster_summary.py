from __future__ import annotations

import json
from collections import Counter
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ENTRY8_RUNS_PATH = ROOT / "confirmed_data" / "dialogue_metadata" / "entry8_dialogue_state_runs.json"
REGD_RUNS_PATH = ROOT / "confirmed_data" / "dialogue_metadata" / "registry_d_dialogue_state_runs.json"
OUT_DIR = ROOT / "confirmed_data" / "dialogue_metadata"


def load_json(path: Path):
    return json.loads(path.read_text())


def summarize_entry8(data: dict) -> dict:
    clusters = []
    for cluster in data["clusters"]:
        token_counter = Counter()
        token_run_counter = Counter()
        longest_runs = []
        for run in cluster["runs"]:
            token = run["dialogue_state_token"]
            if token is None:
                continue
            token_counter[token] += run["record_count"]
            token_run_counter[token] += 1
            longest_runs.append(
                {
                    "dialogue_state_token": token,
                    "record_count": run["record_count"],
                    "first_text": run["first_text"],
                    "last_text": run["last_text"],
                    "sample_texts": run["sample_texts"],
                }
            )
        longest_runs.sort(key=lambda x: (-x["record_count"], x["dialogue_state_token"]))
        clusters.append(
            {
                "cluster_index": cluster["cluster_index"],
                "primary_tag": cluster["primary_tag"],
                "record_count": cluster["record_count"],
                "run_count": cluster["run_count"],
                "top_tokens_by_records": [
                    {"dialogue_state_token": token, "record_count": count, "run_count": token_run_counter[token]}
                    for token, count in token_counter.most_common(8)
                ],
                "longest_runs": longest_runs[:8],
            }
        )
    return {
        "source_group": "registry_a_entry8",
        "note": "Per-cluster objective summary of dialogue_state_token distribution and longest contiguous runs.",
        "clusters": clusters,
    }


def summarize_regd(data: dict) -> dict:
    token_counter = Counter()
    token_run_counter = Counter()
    longest_runs = []
    for run in data["runs"]:
        token = run["dialogue_state_token"]
        if token is None:
            continue
        token_counter[token] += run["record_count"]
        token_run_counter[token] += 1
        longest_runs.append(
            {
                "dialogue_state_token": token,
                "record_count": run["record_count"],
                "first_text": run["first_text"],
                "last_text": run["last_text"],
                "sample_texts": run["sample_texts"],
            }
        )
    longest_runs.sort(key=lambda x: (-x["record_count"], x["dialogue_state_token"]))
    return {
        "source_group": "registry_d_fc_script_texts",
        "note": "Objective summary of dialogue_state_token distribution and longest contiguous runs.",
        "top_tokens_by_records": [
            {"dialogue_state_token": token, "record_count": count, "run_count": token_run_counter[token]}
            for token, count in token_counter.most_common(12)
        ],
        "longest_runs": longest_runs[:20],
        "top_transitions": data.get("top_transitions", [])[:20],
    }


def build_md(entry8_summary: dict, regd_summary: dict) -> str:
    lines = [
        "# Dialogue State Cluster Summary",
        "",
        "화자명 확정이 아니라, 번역 실무에서 바로 볼 수 있는 **cluster/run 요약**이다.",
        "",
        "## Entry8 clusters",
        "",
    ]
    for cluster in entry8_summary["clusters"][:15]:
        lines.append(
            f"### Cluster {cluster['cluster_index']:02d} `{cluster['primary_tag']}` "
            f"records={cluster['record_count']} runs={cluster['run_count']}"
        )
        lines.append("")
        for item in cluster["top_tokens_by_records"][:5]:
            lines.append(
                f"- `{item['dialogue_state_token']}`: {item['record_count']} records / {item['run_count']} runs"
            )
        if cluster["longest_runs"]:
            top = cluster["longest_runs"][0]
            lines.append(
                f"- longest run: `{top['dialogue_state_token']}` x{top['record_count']} "
                f"sample={top['sample_texts'][:2]}"
            )
        lines.append("")
    lines.extend(
        [
            "## Registry D",
            "",
        ]
    )
    for item in regd_summary["top_tokens_by_records"][:10]:
        lines.append(
            f"- `{item['dialogue_state_token']}`: {item['record_count']} records / {item['run_count']} runs"
        )
    lines.append("")
    lines.append("### Longest runs")
    lines.append("")
    for item in regd_summary["longest_runs"][:10]:
        lines.append(
            f"- `{item['dialogue_state_token']}` x{item['record_count']}: {item['sample_texts'][:2]}"
        )
    lines.append("")
    lines.append("### Top transitions")
    lines.append("")
    for item in regd_summary["top_transitions"][:10]:
        lines.append(f"- `{item['from']} -> {item['to']}`: {item['count']}")
    lines.append("")
    return "\n".join(lines)


def main() -> None:
    entry8_runs = load_json(ENTRY8_RUNS_PATH)
    regd_runs = load_json(REGD_RUNS_PATH)
    entry8_summary = summarize_entry8(entry8_runs)
    regd_summary = summarize_regd(regd_runs)
    (OUT_DIR / "entry8_dialogue_state_cluster_summary.json").write_text(
        json.dumps(entry8_summary, ensure_ascii=False, indent=2) + "\n"
    )
    (OUT_DIR / "registry_d_dialogue_state_summary.json").write_text(
        json.dumps(regd_summary, ensure_ascii=False, indent=2) + "\n"
    )
    (OUT_DIR / "dialogue_state_cluster_summary.md").write_text(
        build_md(entry8_summary, regd_summary)
    )
    print("Wrote dialogue state cluster summaries")


if __name__ == "__main__":
    main()
