#!/usr/bin/env python3

from __future__ import annotations

import json
from collections import Counter, defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DATA_ROOT = ROOT / "confirmed_data"
DIALOGUE = DATA_ROOT / "dialogue_metadata"
TEXT_LAYOUT = DATA_ROOT / "text_layout"

ENTRY8_RUNS_PATH = DIALOGUE / "entry8_dialogue_state_runs.json"
REGD_RUNS_PATH = DIALOGUE / "registry_d_dialogue_state_runs.json"
OUT_JSON = TEXT_LAYOUT / "runtime_dialogue_subprofiles.json"
OUT_MD = TEXT_LAYOUT / "runtime_dialogue_subprofiles.md"


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def classify_entry8_cluster(cluster: dict) -> str:
    multi_run_count = sum(1 for run in cluster["runs"] if run["record_count"] >= 2)
    max_run = max((run["record_count"] for run in cluster["runs"]), default=0)
    if multi_run_count >= 40 or max_run >= 10:
        return "chain_heavy_singleline"
    if multi_run_count >= 15 or max_run >= 5:
        return "chain_moderate_singleline"
    return "mostly_standalone_singleline"


def build_entry8_summary(entry8: dict) -> dict:
    clusters = []
    profile_counter = Counter()
    for cluster in entry8["clusters"]:
        multi_run_count = sum(1 for run in cluster["runs"] if run["record_count"] >= 2)
        null_run_count = sum(1 for run in cluster["runs"] if run["dialogue_state_token"] is None)
        token_run_count = cluster["run_count"] - null_run_count
        max_run = max((run["record_count"] for run in cluster["runs"]), default=0)
        profile = classify_entry8_cluster(cluster)
        profile_counter[profile] += 1
        clusters.append(
            {
                "cluster_index": cluster["cluster_index"],
                "primary_tag": cluster["primary_tag"],
                "record_count": cluster["record_count"],
                "run_count": cluster["run_count"],
                "multi_record_run_count": multi_run_count,
                "null_run_count": null_run_count,
                "token_run_count": token_run_count,
                "max_run_record_count": max_run,
                "runtime_chain_profile": profile,
                "sample_multi_runs": [
                    {
                        "dialogue_state_token": run["dialogue_state_token"],
                        "record_count": run["record_count"],
                        "sample_texts": run["sample_texts"][:3],
                    }
                    for run in cluster["runs"]
                    if run["record_count"] >= 2
                ][:5],
            }
        )

    clusters.sort(
        key=lambda item: (
            item["runtime_chain_profile"] != "chain_heavy_singleline",
            -item["multi_record_run_count"],
            -item["max_run_record_count"],
            -item["record_count"],
        )
    )

    return {
        "profile_counts": dict(profile_counter),
        "top_chain_heavy_clusters": [c for c in clusters if c["runtime_chain_profile"] == "chain_heavy_singleline"][:12],
        "top_chain_moderate_clusters": [c for c in clusters if c["runtime_chain_profile"] == "chain_moderate_singleline"][:12],
        "current_reading": [
            "Entry8 records are still single-line counted payloads, but runtime flow is not purely one-record-per-box.",
            "Many clusters contain multi-record contiguous state runs, so the remaining runtime question is chaining/page-flow across short records rather than multiline decoding.",
            "Translation should treat chain-heavy clusters as likely externally sequenced dialogue stretches and keep per-record lines concise.",
        ],
    }


def classify_regd_run(run: dict) -> str:
    max_newlines = max(text.count("\n") for text in run["sample_texts"])
    max_chars = max(len(text) for text in run["sample_texts"])
    if max_newlines == 0 and max_chars <= 20:
        return "single_line_short"
    if max_newlines <= 1 and max_chars <= 40:
        return "short_or_one_break"
    if max_newlines <= 2 and max_chars <= 70:
        return "mid_multiline"
    return "long_multiline"


def build_regd_summary(regd: dict) -> dict:
    groups: dict[str, list[dict]] = defaultdict(list)
    for run in regd["runs"]:
        groups[classify_regd_run(run)].append(run)

    order = ["single_line_short", "short_or_one_break", "mid_multiline", "long_multiline"]
    summaries = []
    for key in order:
        runs = groups.get(key, [])
        summaries.append(
            {
                "subprofile": key,
                "run_count": len(runs),
                "record_coverage": sum(run["record_count"] for run in runs),
                "sample_runs": [
                    {
                        "dialogue_state_token": run["dialogue_state_token"],
                        "record_count": run["record_count"],
                        "sample_texts": run["sample_texts"][:2],
                    }
                    for run in runs[:6]
                ],
            }
        )

    return {
        "subprofiles": summaries,
        "current_reading": [
            "Registry D is not one monolithic multiline family; it splits into short single-line battle/tutorial barks, one-break explanatory lines, mid multiline explanations, and a small long-multiline manual/tutorial tier.",
            "This narrows the remaining runtime risk from generic 'page-flow unknown' to a much smaller question: how the longest multiline tier turns pages inside the shared r3=20 candidate family.",
            "Translation should preserve existing newlines and avoid adding extra breaks until runtime page-turn QA is locked.",
        ],
    }


def build() -> dict:
    entry8 = load_json(ENTRY8_RUNS_PATH)
    regd = load_json(REGD_RUNS_PATH)
    return {
        "version": 1,
        "last_updated": "2026-05-17",
        "scope": "Refined runtime subprofiles for the two remaining high-priority dialogue/page-flow sources.",
        "entry8": build_entry8_summary(entry8),
        "registry_d": build_regd_summary(regd),
        "operational_reading": [
            "Entry8 remaining uncertainty is now concentrated in chain-heavy single-line clusters rather than the entire source.",
            "Registry D remaining uncertainty is now concentrated in a very small long-multiline tier plus page-turn behavior, not the whole source.",
        ],
    }


def render_md(data: dict) -> str:
    lines = [
        "# Runtime Dialogue Subprofiles",
        "",
        f"- last_updated: `{data['last_updated']}`",
        "",
        "## Entry8",
        "",
    ]
    for key, value in data["entry8"]["profile_counts"].items():
        lines.append(f"- `{key}`: `{value}` clusters")
    lines.extend(["", "### Entry8 Focus Clusters", ""])
    for cluster in data["entry8"]["top_chain_heavy_clusters"][:8]:
        lines.append(
            f"- cluster `{cluster['cluster_index']}` `{cluster['primary_tag']}`: "
            f"`records={cluster['record_count']}`, `runs={cluster['run_count']}`, "
            f"`multi_runs={cluster['multi_record_run_count']}`, `max_run={cluster['max_run_record_count']}`"
        )
    lines.extend(["", "### Entry8 Reading", ""])
    for note in data["entry8"]["current_reading"]:
        lines.append(f"- {note}")

    lines.extend(["", "## Registry D", ""])
    for group in data["registry_d"]["subprofiles"]:
        lines.append(
            f"- `{group['subprofile']}`: `runs={group['run_count']}`, `record_coverage={group['record_coverage']}`"
        )
    lines.extend(["", "### Registry D Reading", ""])
    for note in data["registry_d"]["current_reading"]:
        lines.append(f"- {note}")

    lines.extend(["", "## Operational Reading", ""])
    for note in data["operational_reading"]:
        lines.append(f"- {note}")
    lines.append("")
    return "\n".join(lines)


def main() -> int:
    TEXT_LAYOUT.mkdir(parents=True, exist_ok=True)
    data = build()
    OUT_JSON.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    OUT_MD.write_text(render_md(data), encoding="utf-8")
    print(f"wrote {OUT_JSON}")
    print(f"wrote {OUT_MD}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
