#!/usr/bin/env python3

from __future__ import annotations

import json
import re
import sys
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from gba_kor_tool.translation_normalization import contains_japanese_text

EXTRACTED_DIR = ROOT / "confirmed_data" / "extracted_texts"
WORKBENCH_DATASET = ROOT / "confirmed_data" / "localization_workbench" / "workbench_dataset.json"
CURRENT_TRANSLATIONS = ROOT / "patched_roms" / "current_review" / "current_review_translations.json"
APPLY_REPORT = ROOT / "patched_roms" / "current_review" / "current_review_apply_report.json"
OUT_JSON = ROOT / "confirmed_data" / "translation_workspace" / "current_review_text_coverage_audit.json"
OUT_MD = ROOT / "confirmed_data" / "translation_workspace" / "current_review_text_coverage_audit.md"

LOCKED_UNKNOWN_RE = re.compile(r"^\s*[?？]+(?:\s*[?？]+)*\s*$")


def load_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def is_japanese(text: str | None) -> bool:
    return contains_japanese_text(text)


def is_locked_unknown(text: str | None) -> bool:
    return bool(text and LOCKED_UNKNOWN_RE.match(text))


def load_extracted_counts() -> Counter:
    counts: Counter[str] = Counter()
    for path in sorted(EXTRACTED_DIR.glob("*.json")):
        payload = load_json(path)
        records = payload.get("records") if isinstance(payload, dict) else payload
        if not isinstance(records, list):
            continue
        source_group = path.stem
        if source_group == "save_menu_prefixed_texts":
            source_group = "save_menu_texts"
        counts[source_group] += len(records)
    return counts


def build() -> dict:
    extracted_counts = load_extracted_counts()
    dataset = load_json(WORKBENCH_DATASET)["items"]
    translations = load_json(CURRENT_TRANSLATIONS)
    apply_report = load_json(APPLY_REPORT)

    dataset_counts = Counter(item.get("source_group") for item in dataset if item.get("offset") is not None)
    translated_counts = Counter(item.get("source_group") for item in translations)
    action_counts = Counter(item.get("action") for item in apply_report)

    action_by_source: dict[str, Counter] = defaultdict(Counter)
    skipped_examples: dict[str, list[dict]] = defaultdict(list)
    for item in apply_report:
        source_group = item.get("source_group") or "(unknown)"
        action = item.get("action")
        action_by_source[source_group][action] += 1
        if action in {"skipped_no_pointer", "skipped_too_long"} and len(skipped_examples[source_group]) < 12:
            skipped_examples[source_group].append(
                {
                    "offset": item.get("offset"),
                    "capacity_bytes": item.get("capacity_bytes"),
                    "required_bytes": item.get("required_bytes") or item.get("encoded_payload_length"),
                    "text": item.get("text"),
                    "translation": item.get("translation"),
                }
            )

    untranslated_japanese = []
    for item in dataset:
        text = item.get("text")
        translation = item.get("translation") or item.get("agent_draft") or ""
        if is_locked_unknown(text):
            continue
        if is_japanese(text) and (not translation or is_japanese(translation)):
            untranslated_japanese.append(
                {
                    "offset": item.get("offset"),
                    "source_group": item.get("source_group"),
                    "category_id": item.get("category_id"),
                    "text": text,
                    "translation": translation,
                }
            )

    source_summary = []
    for source_group in sorted(set(extracted_counts) | set(dataset_counts) | set(translated_counts) | set(action_by_source)):
        actions = dict(action_by_source.get(source_group, Counter()))
        source_summary.append(
            {
                "source_group": source_group,
                "extracted_records": extracted_counts.get(source_group, 0),
                "workbench_records": dataset_counts.get(source_group, 0),
                "current_review_translations": translated_counts.get(source_group, 0),
                "applied_actions": actions,
            }
        )

    return {
        "last_updated": datetime.now(timezone.utc).isoformat(),
        "notes": [
            "??????/????? 형태의 잠금 또는 미확인 표시는 원본 상태로 간주해 미번역 후보에서 제외한다.",
            "`・`, `・・・`, `ー` 같은 보존 대상 일본식 기호는 일본어 잔존으로 보지 않는다. 실제 가나/한자만 후보로 잡는다.",
            "skipped_no_pointer 는 추출은 되었지만 원래 슬롯을 초과했고, 이 레코드에 대한 직접 포인터를 찾지 못해 ROM 확장 repoint 가 불가능했던 항목이다.",
        ],
        "totals": {
            "extracted_records": sum(extracted_counts.values()),
            "workbench_text_records": sum(dataset_counts.values()),
            "current_review_translations": len(translations),
            "apply_actions": dict(action_counts),
            "untranslated_japanese_candidates": len(untranslated_japanese),
        },
        "source_summary": source_summary,
        "skipped_examples": dict(skipped_examples),
        "untranslated_japanese_candidates": untranslated_japanese[:200],
    }


def render_md(report: dict) -> str:
    lines = [
        "# Current Review Text Coverage Audit",
        "",
        f"- Last updated: `{report['last_updated']}`",
        f"- Extracted records: `{report['totals']['extracted_records']}`",
        f"- Workbench text records: `{report['totals']['workbench_text_records']}`",
        f"- Current review translations: `{report['totals']['current_review_translations']}`",
        f"- Apply actions: `{report['totals']['apply_actions']}`",
        f"- Untranslated Japanese candidates, excluding locked ??????: `{report['totals']['untranslated_japanese_candidates']}`",
        "",
        "## Reading",
        "",
    ]
    for note in report["notes"]:
        lines.append(f"- {note}")

    lines.extend(["", "## Source Summary", ""])
    lines.append("| Source | Extracted | Workbench | Review translations | Apply actions |")
    lines.append("|---|---:|---:|---:|---|")
    for item in report["source_summary"]:
        lines.append(
            "| {source_group} | {extracted_records} | {workbench_records} | {current_review_translations} | `{applied_actions}` |".format(
                **item
            )
        )

    lines.extend(["", "## Skipped Examples", ""])
    for source_group, examples in report["skipped_examples"].items():
        lines.append(f"### {source_group}")
        for item in examples:
            lines.append(
                f"- `0x{int(item['offset']):06X}` cap `{item.get('capacity_bytes')}` req `{item.get('required_bytes')}`: "
                f"{item.get('text')!r} -> {item.get('translation')!r}"
            )
        lines.append("")

    lines.extend(["## Untranslated Japanese Candidates", ""])
    for item in report["untranslated_japanese_candidates"][:80]:
        offset = item.get("offset")
        offset_text = "(no offset)" if offset is None else f"0x{int(offset):06X}"
        lines.append(f"- `{offset_text}` `{item.get('source_group')}`: {item.get('text')!r}")
    return "\n".join(lines).rstrip() + "\n"


def main() -> int:
    report = build()
    OUT_JSON.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    OUT_MD.write_text(render_md(report), encoding="utf-8")
    print(f"written: {OUT_JSON}")
    print(f"written: {OUT_MD}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
