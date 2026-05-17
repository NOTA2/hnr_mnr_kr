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
        "last_updated": "2026-05-17",
        "scope": "High-priority dialogue/page-flow sources on the shared r3=20 candidate family.",
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
                    "Payloads are overwhelmingly short counted lines and currently contain no explicit newline bytes in extracted text.",
                    "The dominant remaining uncertainty is not record boundary, but how these short lines chain into visible dialogue boxes/pages at runtime.",
                    "Until runtime page-flow is visually locked, translations should assume concise single-line records that may be sequenced externally by script controls.",
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
                    "Many payloads already contain explicit newlines, so part of the visible box/page flow is embedded directly in the extracted text rather than only in adjacent controls.",
                    "The source still shares the same r3=20 candidate renderer family, but its runtime behavior is materially different from entry8 because multiline payloads are common.",
                    "Until runtime page-turn behavior is visually locked, translators should preserve existing newlines and avoid inventing extra ones.",
                ],
            },
        ],
        "operational_reading": [
            "High-priority dialogue runtime work is no longer a single unresolved blob.",
            "It is narrowed to two profiles on the shared r3=20 candidate family: single-line counted script lines (entry8) and multiline FC-delimited dialogue payloads (Registry D).",
            "This reduces the remaining runtime blocker to visual/page confirmation rather than record-boundary discovery.",
        ],
    }


def render_md(report: dict) -> str:
    lines = [
        "# Runtime Dialogue Family Report",
        "",
        f"- last_updated: `{report['last_updated']}`",
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
                f"- runtime candidate: `{profile['runtime_candidate_family']}`",
                f"- record_count: `{payload['record_count']}`",
                f"- max_chars: `{payload['max_chars']}`",
                f"- p95_chars: `{payload['p95_chars']}`",
                f"- newline_record_count: `{payload['newline_record_count']}`",
                f"- max_explicit_newlines: `{payload['max_explicit_newlines']}`",
                f"- max_rendered_lines_if_newline_split: `{payload['max_rendered_lines_if_newline_split']}`",
                "",
            ]
        )
        for note in profile["current_reading"]:
            lines.append(f"- {note}")
        lines.append("")
    lines.append("## Operational Reading")
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
