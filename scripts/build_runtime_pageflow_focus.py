#!/usr/bin/env python3

from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DATA_ROOT = ROOT / "confirmed_data"
DIALOGUE = DATA_ROOT / "dialogue_metadata"
TEXT_LAYOUT = DATA_ROOT / "text_layout"

ENTRY8_RUNS_PATH = DIALOGUE / "entry8_dialogue_state_runs.json"
REGD_RUNS_PATH = DIALOGUE / "registry_d_dialogue_state_runs.json"
SUBPROFILE_PATH = TEXT_LAYOUT / "runtime_dialogue_subprofiles.json"

OUT_JSON = TEXT_LAYOUT / "runtime_pageflow_focus.json"
OUT_MD = TEXT_LAYOUT / "runtime_pageflow_focus.md"


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


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


def build() -> dict:
    entry8 = load_json(ENTRY8_RUNS_PATH)
    regd = load_json(REGD_RUNS_PATH)
    sub = load_json(SUBPROFILE_PATH)

    heavy_indexes = {
        item["cluster_index"] for item in sub["entry8"]["top_chain_heavy_clusters"]
    }
    heavy_clusters = []
    for cluster in entry8["clusters"]:
        if cluster["cluster_index"] not in heavy_indexes:
            continue
        multi_runs = [run for run in cluster["runs"] if run["record_count"] >= 3]
        heavy_clusters.append(
            {
                "cluster_index": cluster["cluster_index"],
                "primary_tag": cluster["primary_tag"],
                "record_count": cluster["record_count"],
                "run_count": cluster["run_count"],
                "focus_reason": (
                    "high_chain_density"
                    if len(multi_runs) >= 40 or max((r["record_count"] for r in cluster["runs"]), default=0) >= 10
                    else "moderate_chain_density"
                ),
                "sample_chain_runs": [
                    {
                        "dialogue_state_token": run["dialogue_state_token"],
                        "record_count": run["record_count"],
                        "sample_texts": run["sample_texts"][:3],
                    }
                    for run in multi_runs[:5]
                ],
            }
        )

    heavy_clusters.sort(key=lambda item: (-item["record_count"], item["cluster_index"]))

    long_runs = []
    for idx, run in enumerate(regd["runs"]):
        if classify_regd_run(run) != "long_multiline":
            continue
        max_newlines = max(text.count("\n") for text in run["sample_texts"])
        max_chars = max(len(text) for text in run["sample_texts"])
        long_runs.append(
            {
                "focus_index": idx,
                "dialogue_state_token": run["dialogue_state_token"],
                "record_count": run["record_count"],
                "max_chars": max_chars,
                "max_explicit_newlines": max_newlines,
                "sample_texts": run["sample_texts"][:2],
            }
        )

    return {
        "version": 1,
        "last_updated": "2026-05-17",
        "entry8_focus": {
            "focus_cluster_count": len(heavy_clusters),
            "recommended_audit_order": heavy_clusters[:12],
            "current_reading": [
                "Entry8 page-flow work should focus first on chain-heavy clusters with many multi-record runs, because that is where external sequencing pressure is highest.",
                "Clusters dominated by null-token multi-runs are especially strong candidates for script-driven chaining rather than self-contained one-record boxes.",
            ],
        },
        "registry_d_focus": {
            "long_multiline_focus_count": len(long_runs),
            "recommended_audit_order": long_runs,
            "current_reading": [
                "Registry D page-flow work should focus first on the very small long-multiline tier.",
                "The rest of Registry D is already narrow enough that translation can proceed conservatively with newline preservation.",
            ],
        },
        "operational_reading": [
            "This file is the practical next-step layer above the general family/subprofile reports.",
            "Use it to decide which concrete entry8 clusters and Registry D runs deserve runtime/page QA first.",
        ],
    }


def render_md(data: dict) -> str:
    lines = [
        "# Runtime Pageflow Focus",
        "",
        f"- last_updated: `{data['last_updated']}`",
        "",
        "## Entry8 Focus",
        "",
        f"- focus_cluster_count: `{data['entry8_focus']['focus_cluster_count']}`",
        "",
    ]
    for item in data["entry8_focus"]["recommended_audit_order"][:10]:
        lines.append(
            f"- cluster `{item['cluster_index']}` `{item['primary_tag']}` "
            f"(`records={item['record_count']}`, `runs={item['run_count']}`, `{item['focus_reason']}`)"
        )
    lines.extend(["", "### Entry8 Reading", ""])
    for note in data["entry8_focus"]["current_reading"]:
        lines.append(f"- {note}")

    lines.extend(["", "## Registry D Focus", ""])
    lines.append(f"- long_multiline_focus_count: `{data['registry_d_focus']['long_multiline_focus_count']}`")
    lines.append("")
    for item in data["registry_d_focus"]["recommended_audit_order"]:
        lines.append(
            f"- run `{item['focus_index']}` token `{item['dialogue_state_token']}` "
            f"(`records={item['record_count']}`, `chars={item['max_chars']}`, `newlines={item['max_explicit_newlines']}`)"
        )
    lines.extend(["", "### Registry D Reading", ""])
    for note in data["registry_d_focus"]["current_reading"]:
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
