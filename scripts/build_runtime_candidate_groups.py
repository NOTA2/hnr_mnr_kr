#!/usr/bin/env python3

from __future__ import annotations

import json
from datetime import date
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DATA_ROOT = ROOT / "confirmed_data"
DIALOGUE = DATA_ROOT / "dialogue_metadata"
TEXT_LAYOUT = DATA_ROOT / "text_layout"

ENTRY8_RUNS_PATH = DIALOGUE / "entry8_dialogue_state_runs.json"
REGD_RUNS_PATH = DIALOGUE / "registry_d_dialogue_state_runs.json"
PAGEFLOW_PATH = TEXT_LAYOUT / "runtime_pageflow_focus.json"

OUT_JSON = TEXT_LAYOUT / "runtime_candidate_groups.json"
OUT_MD = TEXT_LAYOUT / "runtime_candidate_groups.md"


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def classify_entry8_candidate(cluster: dict) -> str:
    null_runs = sum(1 for r in cluster["runs"] if r["dialogue_state_token"] is None)
    token_runs = cluster["run_count"] - null_runs
    max_run = max((r["record_count"] for r in cluster["runs"]), default=0)
    if null_runs > token_runs and max_run >= 5:
        return "null_dominant_script_chain"
    if token_runs >= null_runs:
        return "token_mixed_chain"
    return "mixed_short_chain"


def classify_regd_candidate(run: dict) -> str:
    if run["dialogue_state_token"] is None:
        return "null_token_manual_or_tutorial_chain"
    return "named_token_long_multiline"


def build() -> dict:
    entry8 = load_json(ENTRY8_RUNS_PATH)
    regd = load_json(REGD_RUNS_PATH)
    page = load_json(PAGEFLOW_PATH)

    focus_clusters = {item["cluster_index"] for item in page["entry8_focus"]["recommended_audit_order"]}
    entry8_groups = []
    for cluster in entry8["clusters"]:
        if cluster["cluster_index"] not in focus_clusters:
            continue
        group = classify_entry8_candidate(cluster)
        entry8_groups.append(
            {
                "cluster_index": cluster["cluster_index"],
                "primary_tag": cluster["primary_tag"],
                "candidate_group": group,
                "record_count": cluster["record_count"],
                "run_count": cluster["run_count"],
                "sample_chain_run": next(
                    (
                        {
                            "dialogue_state_token": run["dialogue_state_token"],
                            "record_count": run["record_count"],
                            "sample_texts": run["sample_texts"][:3],
                        }
                        for run in cluster["runs"]
                        if run["record_count"] >= 3
                    ),
                    None,
                ),
            }
        )

    entry8_groups.sort(key=lambda x: (x["candidate_group"], -x["record_count"], x["cluster_index"]))

    regd_groups = []
    for item in page["registry_d_focus"]["recommended_audit_order"]:
        run = regd["runs"][item["focus_index"]]
        regd_groups.append(
            {
                "focus_index": item["focus_index"],
                "candidate_group": classify_regd_candidate(run),
                "dialogue_state_token": run["dialogue_state_token"],
                "record_count": run["record_count"],
                "sample_texts": run["sample_texts"][:2],
            }
        )

    return {
        "version": 1,
        "last_updated": date.today().isoformat(),
        "entry8_focus_groups": entry8_groups,
        "registry_d_focus_groups": regd_groups,
        "operational_reading": [
            "이 목록은 남은 runtime/page-flow 작업을 위한 객관적 후보군이다.",
            "화자 이름을 붙이는 것이 아니라, 남은 미확정 집합을 더 작은 제어 동작 family 로 줄이는 역할만 한다.",
        ],
    }


def render_md(data: dict) -> str:
    lines = [
        "# runtime 후보군",
        "",
        f"- 마지막 갱신: `{data['last_updated']}`",
        "",
        "## Entry8 집중 후보군",
        "",
    ]
    for item in data["entry8_focus_groups"]:
        lines.append(
            f"- cluster `{item['cluster_index']}` `{item['primary_tag']}` -> `{item['candidate_group']}` "
            f"(`records={item['record_count']}`, `runs={item['run_count']}`)"
        )
    lines.extend(["", "## Registry D 집중 후보군", ""])
    for item in data["registry_d_focus_groups"]:
        lines.append(
            f"- run `{item['focus_index']}` token `{item['dialogue_state_token']}` -> `{item['candidate_group']}` "
            f"(`records={item['record_count']}`)"
        )
    lines.extend(["", "## 현재 해석", ""])
    for note in data["operational_reading"]:
        lines.append(f"- {note}")
    lines.append("")
    return "\n".join(lines)


def main() -> int:
    data = build()
    OUT_JSON.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    OUT_MD.write_text(render_md(data), encoding="utf-8")
    print(f"wrote {OUT_JSON}")
    print(f"wrote {OUT_MD}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
