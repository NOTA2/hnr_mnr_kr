#!/usr/bin/env python3
"""Audit high-risk normalization regressions in active localization data."""

from __future__ import annotations

import json
import re
from collections import Counter
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]

ACTIVE_PATHS = [
    ROOT / "confirmed_data" / "translation_worksets",
    ROOT / "confirmed_data" / "extracted_texts",
    ROOT / "confirmed_data" / "localization_workbench" / "workbench_dataset.json",
    ROOT / "confirmed_data" / "translation_workspace" / "all_extracted_texts_master.json",
    ROOT / "confirmed_data" / "translation_workspace" / "translation_expansion_opportunities.json",
    ROOT / "confirmed_data" / "translation_workspace" / "registry_a_entry8_clusters",
    ROOT / "confirmed_data" / "translation_workspace" / "registry_a_entry8_runs",
]

TEXT_FIELDS = (
    "translation",
    "agent_draft",
    "effective_translation",
    "translation_text",
    "current_translation",
    "proposed_translation",
)
REFERENCE_FIELDS = ("text", "source_text", "original_text", "source")

RECOVERY_ITEM_RE = re.compile(r"^回復薬[0-9０-９](?:$|体力を)")
ENTRY8_RECOVERY_ACQUISITION_RE = re.compile(r"^回復薬[0-9０-９]を手に入れた$")
SPEAR_SOURCE_TEXT = "槍を錬成して攻撃"


def iter_json_files() -> list[Path]:
    files: list[Path] = []
    for path in ACTIVE_PATHS:
        if path.is_dir():
            files.extend(sorted(path.glob("*.json")))
        elif path.exists():
            files.append(path)
    return files


def reference_text(item: dict[str, Any], inherited: str = "") -> str:
    for key in REFERENCE_FIELDS:
        value = item.get(key)
        if isinstance(value, str) and value:
            return value
    return inherited


def item_identifier(item: dict[str, Any]) -> str:
    value = item.get("item_id") or item.get("offset") or item.get("run_id") or item.get("cluster_id") or ""
    if isinstance(value, int):
        return f"0x{value:06X}"
    return str(value)


def walk(value: Any, path: Path, inherited_reference: str, issues: list[dict[str, str]]) -> None:
    if isinstance(value, dict):
        local_reference = reference_text(value, inherited_reference)
        for field in TEXT_FIELDS:
            text = value.get(field)
            if not isinstance(text, str):
                continue
            if RECOVERY_ITEM_RE.match(local_reference) and re.search(r"회복약[ 　]+[0-9０-９]", text):
                issues.append(
                    {
                        "kind": "bad_recovery_item_space",
                        "file": str(path.relative_to(ROOT)),
                        "id": item_identifier(value),
                        "source": local_reference,
                        "field": field,
                        "value": text,
                    }
                )
            if ENTRY8_RECOVERY_ACQUISITION_RE.match(local_reference) and re.search(r"회복약[0-9０-９]", text):
                issues.append(
                    {
                        "kind": "bad_entry8_acquisition_glued",
                        "file": str(path.relative_to(ROOT)),
                        "id": item_identifier(value),
                        "source": local_reference,
                        "field": field,
                        "value": text,
                    }
                )
            if local_reference == SPEAR_SOURCE_TEXT and (
                "창을 연성해 공격" in text or "창을 연성해\n공격" in text
            ):
                issues.append(
                    {
                        "kind": "bad_spear_spacing_regression",
                        "file": str(path.relative_to(ROOT)),
                        "id": item_identifier(value),
                        "source": local_reference,
                        "field": field,
                        "value": text,
                    }
                )
        for child in value.values():
            if isinstance(child, (dict, list)):
                walk(child, path, local_reference, issues)
    elif isinstance(value, list):
        for child in value:
            walk(child, path, inherited_reference, issues)


def main() -> int:
    issues: list[dict[str, str]] = []
    for path in iter_json_files():
        data = json.loads(path.read_text(encoding="utf-8"))
        walk(data, path, "", issues)

    counts = Counter(issue["kind"] for issue in issues)
    print(f"checked_files={len(iter_json_files())}")
    print(f"issue_count={len(issues)}")
    for kind, count in sorted(counts.items()):
        print(f"{kind}={count}")
    for issue in issues[:50]:
        value = issue["value"].replace("\x0b", "\\x0B")
        print(
            f"{issue['kind']}\t{issue['file']}\t{issue['id']}\t"
            f"{issue['field']}\t{issue['source']}\t{value}"
        )
    return 1 if issues else 0


if __name__ == "__main__":
    raise SystemExit(main())
