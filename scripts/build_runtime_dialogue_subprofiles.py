#!/usr/bin/env python3

from __future__ import annotations

import json
from collections import Counter, defaultdict
from datetime import date
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
            "Entry8 record 는 여전히 단일 줄 counted payload 이지만, runtime 흐름이 순수하게 one-record-per-box 는 아니다.",
            "많은 cluster 가 multi-record 연속 상태 run 을 포함하므로, 남은 runtime 질문은 multiline 해독이 아니라 짧은 record 들이 어떻게 이어지는가이다.",
            "번역은 chain-heavy cluster 를 외부 script 로 이어지는 대사 구간으로 보고, record 단위 줄을 짧게 유지한다.",
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
            "Registry D 는 하나의 거대한 multiline family 가 아니라, 짧은 단일 줄 전투/튜토리얼 대사, 한 번만 끊기는 설명 줄, 중간 길이 multiline 설명, 소수의 장문 manual/tutorial 계층으로 나뉜다.",
            "Registry D 는 packed relocation 으로 원문 byte 슬롯보다 긴 번역도 적용 가능하므로, 남은 runtime 위험은 길이 수용 여부보다 가장 긴 multiline 계층이 어떻게 페이지를 넘기는가라는 질문으로 줄어든다.",
            "번역은 자연스러운 의미 보존과 기존 개행 보존을 우선하고, runtime page-turn QA 에서 잘림이 보이면 줄바꿈/문장 분할로 조정한다.",
        ],
    }


def build() -> dict:
    entry8 = load_json(ENTRY8_RUNS_PATH)
    regd = load_json(REGD_RUNS_PATH)
    return {
        "version": 1,
        "last_updated": date.today().isoformat(),
        "scope": "Refined runtime subprofiles for the two remaining high-priority dialogue/page-flow sources.",
        "entry8": build_entry8_summary(entry8),
        "registry_d": build_regd_summary(regd),
        "operational_reading": [
            "Entry8 의 남은 불확실성은 source 전체가 아니라 chain-heavy 단일 줄 cluster 에 집중돼 있다.",
            "Registry D 의 남은 불확실성은 source 전체나 원문 슬롯 길이가 아니라, 매우 작은 장문 multiline 계층과 page-turn 동작에 집중돼 있다.",
        ],
    }


def render_md(data: dict) -> str:
    lines = [
        "# runtime 대사 세부 profile",
        "",
        f"- 마지막 갱신: `{data['last_updated']}`",
        "",
        "## Entry8",
        "",
    ]
    for key, value in data["entry8"]["profile_counts"].items():
        lines.append(f"- `{key}`: `{value}` clusters")
    lines.extend(["", "### Entry8 집중 cluster", ""])
    for cluster in data["entry8"]["top_chain_heavy_clusters"][:8]:
        lines.append(
            f"- cluster `{cluster['cluster_index']}` `{cluster['primary_tag']}`: "
            f"`records={cluster['record_count']}`, `runs={cluster['run_count']}`, "
            f"`multi_runs={cluster['multi_record_run_count']}`, `max_run={cluster['max_run_record_count']}`"
        )
    lines.extend(["", "### Entry8 해석", ""])
    for note in data["entry8"]["current_reading"]:
        lines.append(f"- {note}")

    lines.extend(["", "## Registry D", ""])
    for group in data["registry_d"]["subprofiles"]:
        lines.append(
            f"- `{group['subprofile']}`: `runs={group['run_count']}`, `record_coverage={group['record_coverage']}`"
        )
    lines.extend(["", "### Registry D 해석", ""])
    for note in data["registry_d"]["current_reading"]:
        lines.append(f"- {note}")

    lines.extend(["", "## 현재 해석", ""])
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
