from __future__ import annotations

import json
from collections import Counter
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ENTRY8_STATE_PATH = ROOT / "confirmed_data" / "dialogue_metadata" / "entry8_dialogue_state_index.json"
REGD_STATE_PATH = ROOT / "confirmed_data" / "dialogue_metadata" / "registry_d_dialogue_state_index.json"
ENTRY8_CLUSTERS_PATH = ROOT / "confirmed_data" / "translation_workspace" / "registry_a_entry8_clusters_manifest.json"
OUT_DIR = ROOT / "confirmed_data" / "dialogue_metadata"


def load_json(path: Path):
    return json.loads(path.read_text())


def push_run(runs: list[dict], run: dict | None) -> None:
    if run is None:
        return
    run["record_count"] = len(run["records"])
    run["first_text"] = run["records"][0]["text"]
    run["last_text"] = run["records"][-1]["text"]
    run["sample_texts"] = [r["text"] for r in run["records"][:4]]
    runs.append(run)


def compact_record(record: dict) -> dict:
    return {
        "offset": record["offset"],
        "text": record["text"],
        "dialogue_state_token": record.get("dialogue_state_token"),
        "control_gap_length": record.get("control_gap_length"),
    }


def build_entry8_runs() -> dict:
    state_data = load_json(ENTRY8_STATE_PATH)
    cluster_manifest = load_json(ENTRY8_CLUSTERS_PATH)
    records = state_data["records"]
    runs_by_cluster = []
    transition_counter = Counter()

    for cluster in cluster_manifest["clusters"]:
        start = cluster["range"]["start_offset"]
        end = cluster["range"]["end_offset_exclusive"]
        cluster_records = [r for r in records if start <= r["offset"] < end]
        runs = []
        current = None
        prev_token = None
        for record in cluster_records:
            token = record.get("dialogue_state_token")
            if current is None or token != current["dialogue_state_token"]:
                if current is not None:
                    push_run(runs, current)
                    old = current["dialogue_state_token"]
                    if old is not None and token is not None and old != token:
                        transition_counter[(old, token)] += 1
                current = {
                    "dialogue_state_token": token,
                    "records": [compact_record(record)],
                }
            else:
                current["records"].append(compact_record(record))
            prev_token = token
        push_run(runs, current)
        runs_by_cluster.append(
            {
                "cluster_index": cluster["cluster_index"],
                "primary_tag": cluster["primary_tag"],
                "record_count": cluster["record_count"],
                "run_count": len(runs),
                "runs": runs,
            }
        )

    transitions = [
        {"from": a, "to": b, "count": c}
        for (a, b), c in transition_counter.most_common()
    ]
    return {
        "source_group": "registry_a_entry8",
        "status": "objective_state_runs_only",
        "note": (
            "Runs group consecutive records inside each cluster by identical dialogue_state_token. "
            "These runs are candidate same-speaker/state stretches, not confirmed speaker IDs."
        ),
        "clusters": runs_by_cluster,
        "top_transitions": transitions[:100],
    }


def build_regd_runs() -> dict:
    state_data = load_json(REGD_STATE_PATH)
    records = state_data["records"]
    runs = []
    transition_counter = Counter()
    current = None
    for record in records:
        token = record.get("dialogue_state_token")
        compact = {
            "offset": record["offset"],
            "text": record["text"],
            "dialogue_state_token": token,
        }
        if current is None or token != current["dialogue_state_token"]:
            if current is not None:
                push_run(runs, current)
                old = current["dialogue_state_token"]
                if old is not None and token is not None and old != token:
                    transition_counter[(old, token)] += 1
            current = {"dialogue_state_token": token, "records": [compact]}
        else:
            current["records"].append(compact)
    push_run(runs, current)
    transitions = [
        {"from": a, "to": b, "count": c}
        for (a, b), c in transition_counter.most_common()
    ]
    return {
        "source_group": "registry_d_fc_script_texts",
        "status": "objective_state_runs_only",
        "note": (
            "Runs group consecutive records by identical dialogue_state_token. "
            "They help translation preserve same-turn tone without claiming exact speaker IDs."
        ),
        "run_count": len(runs),
        "runs": runs,
        "top_transitions": transitions[:100],
    }


def write_readme(entry8: dict, regd: dict) -> str:
    lines = [
        "# Dialogue Metadata",
        "",
        "이 폴더는 **화자 이름 추정**이 아니라, 대사 직전 제어군에서 뽑은 **객관적 state token** 과 **state run** 을 담는다.",
        "",
        "현재 원칙:",
        "",
        "- `dialogue_state_token` 은 confirmed speaker ID 가 아니다.",
        "- 같은 token 을 공유하는 줄은 같은 active portrait/state 후보로 묶어 볼 수 있다.",
        "- `state run` 은 연속된 동일 token 묶음이며, 번역 시 같은 톤/호흡을 유지할 후보군으로 본다.",
        "",
        "## Files",
        "",
        "- `entry8_dialogue_state_index.json`: Registry A entry 8 script-line state tokens",
        "- `registry_d_dialogue_state_index.json`: Registry D FC-script state tokens",
        "- `entry8_dialogue_state_runs.json`: Entry 8 cluster-local contiguous state runs",
        "- `registry_d_dialogue_state_runs.json`: Registry D contiguous state runs",
        "",
        f"- Entry8 clusters with runs: `{len(entry8['clusters'])}`",
        f"- Registry D total runs: `{regd['run_count']}`",
        "",
        "## Translation use",
        "",
        "- 같은 run 안의 줄들은 우선 같은 화자 상태 후보로 보고 말투 일관성을 체크한다.",
        "- run 이 바뀌면 speaker/state/portrait 전환 후보로 본다.",
        "- 확정 화자명은 별도 근거가 생기기 전까지 추가하지 않는다.",
        "",
    ]
    return "\n".join(lines)


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    entry8 = build_entry8_runs()
    regd = build_regd_runs()
    (OUT_DIR / "entry8_dialogue_state_runs.json").write_text(
        json.dumps(entry8, ensure_ascii=False, indent=2) + "\n"
    )
    (OUT_DIR / "registry_d_dialogue_state_runs.json").write_text(
        json.dumps(regd, ensure_ascii=False, indent=2) + "\n"
    )
    # refresh README to include run files too
    (OUT_DIR / "README.md").write_text(write_readme(entry8, regd))
    print("Wrote dialogue state run metadata")


if __name__ == "__main__":
    main()
