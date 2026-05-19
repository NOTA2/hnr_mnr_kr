#!/usr/bin/env python3

from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DATA_ROOT = ROOT / "confirmed_data"
EXTRACTED = DATA_ROOT / "extracted_texts"
DIALOGUE = DATA_ROOT / "dialogue_metadata"
TEXT_LAYOUT = DATA_ROOT / "text_layout"

ENTRY8_PATH = EXTRACTED / "registry_a_entry8_prefixed_texts.json"
REGD_PATH = EXTRACTED / "registry_d_fc_script_texts.json"
REGD_SUMMARY_PATH = DIALOGUE / "registry_d_dialogue_state_summary.json"
ENTRY8_CLUSTER_PATH = DIALOGUE / "entry8_dialogue_state_cluster_summary.json"
OUT_JSON = TEXT_LAYOUT / "runtime_dialogue_family_report.json"
OUT_MD = TEXT_LAYOUT / "runtime_dialogue_family_report.md"


def percentile(values: list[int], q: float) -> int:
    if not values:
        return 0
    idx = max(0, min(len(values) - 1, int(len(values) * q) - 1))
    return sorted(values)[idx]


def summarize_records(records: list[dict]) -> dict:
    char_lengths = [len(r["text"]) for r in records]
    newline_counts = [r["text"].count("\n") for r in records]
    return {
        "record_count": len(records),
        "max_chars": max(char_lengths) if char_lengths else 0,
        "p95_chars": percentile(char_lengths, 0.95),
        "newline_record_count": sum(1 for n in newline_counts if n > 0),
        "max_explicit_newlines": max(newline_counts) if newline_counts else 0,
        "max_rendered_lines_if_newline_split": (
            max((n + 1) for n in newline_counts) if newline_counts else 0
        ),
    }


def build() -> dict:
    entry8_records = json.loads(ENTRY8_PATH.read_text(encoding="utf-8"))
    regd_records = json.loads(REGD_PATH.read_text(encoding="utf-8"))
    regd_summary = json.loads(REGD_SUMMARY_PATH.read_text(encoding="utf-8"))
    entry8_cluster_summary = json.loads(ENTRY8_CLUSTER_PATH.read_text(encoding="utf-8"))

    entry8_stats = summarize_records(entry8_records)
    regd_stats = summarize_records(regd_records)

    return {
        "version": 1,
        "last_updated": "2026-05-18",
        "scope": "공유 r3=20 후보 family 위에 놓인 상위 우선순위 대사/page-flow source 요약.",
        "profiles": [
            {
                "id": "entry8_singleline_counted_dialogue_profile",
                "source_group": "registry_a_entry8_prefixed_texts",
                "record_structure_family": "entry8_prefixed_01ff_script_line",
                "runtime_candidate_family": "shared_text_object_r3_20",
                "observed_payload_profile": {
                    **entry8_stats,
                    "explicit_multiline_payload_observed": False,
                },
                "state_profile": {
                    "cluster_count": len(entry8_cluster_summary.get("clusters", [])),
                    "top_cluster_examples": [
                        {
                            "cluster_index": c["cluster_index"],
                            "primary_tag": c["primary_tag"],
                            "record_count": c["record_count"],
                            "top_token": (
                                c["top_tokens_by_records"][0]["dialogue_state_token"]
                                if c.get("top_tokens_by_records")
                                else None
                            ),
                        }
                        for c in entry8_cluster_summary.get("clusters", [])[:5]
                    ],
                },
                "current_reading": [
                    "payload 대부분이 짧은 counted line 이며, 현재 추출 텍스트 안에는 명시적 개행 바이트가 없다.",
                    "남은 핵심 불확실성은 record 경계가 아니라, 이 짧은 줄들이 runtime 에서 어떻게 이어져 보이는가이다.",
                    "runtime page-flow 가 시각적으로 확인되기 전까지는 외부 script control 로 이어질 수 있는 짧은 단일 줄 record 로 보고 번역을 짧게 유지한다.",
                ],
            },
            {
                "id": "registry_d_multiline_fc_dialogue_profile",
                "source_group": "registry_d_fc_script_texts",
                "record_structure_family": "registry_d_fc_stop_script_line",
                "runtime_candidate_family": "shared_text_object_r3_20",
                "observed_payload_profile": {
                    **regd_stats,
                    "explicit_multiline_payload_observed": True,
                },
                "state_profile": {
                    "top_tokens_by_records": regd_summary.get("top_tokens_by_records", [])[:6],
                    "top_transitions": regd_summary.get("top_transitions", [])[:8],
                    "longest_runs": regd_summary.get("longest_runs", [])[:6],
                },
                "current_reading": [
                    "많은 payload 가 이미 명시적 개행을 포함하므로, 보이는 박스/page 흐름 일부는 인접 제어코드뿐 아니라 추출 텍스트 내부에도 직접 들어 있다.",
                    "이 source 도 같은 r3=20 후보 렌더러 family 를 공유하지만, multiline payload 가 흔하기 때문에 runtime 동작은 entry8 과 실질적으로 다르다.",
                    "현재 삽입기는 Registry D entry 단위 packed relocation 을 지원하므로, 원문 byte 슬롯 길이에 맞추려고 번역을 과도하게 줄일 필요는 없다.",
                    "runtime page-turn 동작은 시각 QA 로 확인하고, 화면 잘림이 보이면 의미 삭제보다 줄바꿈/문장 분할로 조정한다.",
                ],
            },
        ],
        "operational_reading": [
            "상위 우선순위 대사 runtime 작업은 더 이상 하나의 큰 미해결 덩어리가 아니다.",
            "이제 shared r3=20 후보 family 위의 두 profile, 즉 entry8 의 단일 줄 counted script line 과 Registry D 의 multiline FC 구분 payload 로 좁혀졌다.",
            "따라서 남은 blocker 는 record 경계 탐색이 아니라 시각적 page 확인이다.",
        ],
    }


def render_md(report: dict) -> str:
    lines = [
        "# runtime 대사 family 보고서",
        "",
        f"- 마지막 갱신: `{report['last_updated']}`",
        "",
    ]
    for profile in report["profiles"]:
        payload = profile["observed_payload_profile"]
        lines.extend(
            [
                f"## {profile['id']}",
                "",
                f"- source_group: `{profile['source_group']}`",
                f"- record family: `{profile['record_structure_family']}`",
                f"- runtime 후보: `{profile['runtime_candidate_family']}`",
                f"- record 수: `{payload['record_count']}`",
                f"- 최대 글자 수: `{payload['max_chars']}`",
                f"- 글자 수 95퍼센타일: `{payload['p95_chars']}`",
                f"- 개행 포함 record 수: `{payload['newline_record_count']}`",
                f"- 최대 명시적 개행 수: `{payload['max_explicit_newlines']}`",
                f"- 개행 기준 최대 렌더 줄 수: `{payload['max_rendered_lines_if_newline_split']}`",
                "",
            ]
        )
        for note in profile["current_reading"]:
            lines.append(f"- {note}")
        lines.append("")
    lines.append("## 현재 해석")
    lines.append("")
    for note in report["operational_reading"]:
        lines.append(f"- {note}")
    lines.append("")
    return "\n".join(lines)


def main() -> int:
    TEXT_LAYOUT.mkdir(parents=True, exist_ok=True)
    report = build()
    OUT_JSON.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    OUT_MD.write_text(render_md(report), encoding="utf-8")
    print(f"wrote {OUT_JSON}")
    print(f"wrote {OUT_MD}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
