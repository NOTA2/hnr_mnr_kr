#!/usr/bin/env python3

from __future__ import annotations

import json
import re
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
DATASET_PATH = ROOT / "confirmed_data" / "localization_workbench" / "workbench_dataset.json"
OUT_DIR = ROOT / "analysis" / "generated_workbenches" / "translation_consistency"
JSON_REPORT = OUT_DIR / "source_translation_variants.json"
MD_REPORT = OUT_DIR / "source_translation_variants.md"

IMAGE_CATEGORY_IDS = {
    "image_review_units",
    "image_group_field_menu_labels",
    "image_group_battle_command_buttons",
    "image_group_battle_popups_panels",
    "image_group_card_book_ui",
    "image_group_title_screen",
    "image_group_reference_candidates",
    "image_group_other",
    "common_hud_tiles",
    "alchemy_tiles",
    "registry_b_zp01_resources",
}

JAPANESE_RE = re.compile(r"[\u3040-\u30ff\u3400-\u9fff]")
WHITESPACE_RE = re.compile(r"[ \t\r\n\u3000\x0b]+")


def has_japanese(text: str) -> bool:
    return bool(JAPANESE_RE.search(text))


def normalize_semantic_translation(text: str) -> str:
    text = text.replace("\\n", "\n").replace("\\x0B", "\x0b")
    text = WHITESPACE_RE.sub(" ", text)
    return text.strip()


def visible_text(text: str) -> str:
    return (
        text.replace("\x0b", "\\x0B")
        .replace("\n", "\\n")
        .replace("\u3000", "□")
        .replace(" ", "·")
    )


def is_image_item(item: dict[str, Any]) -> bool:
    return item.get("category_id") in IMAGE_CATEGORY_IDS or str(item.get("item_id", "")).startswith("image:")


def category_labels(dataset: dict[str, Any]) -> dict[str, str]:
    labels: dict[str, str] = {}
    for category in dataset.get("categories", []):
        if isinstance(category, dict) and category.get("id"):
            labels[str(category["id"])] = str(category.get("label") or category["id"])
    return labels


def main() -> int:
    dataset = json.loads(DATASET_PATH.read_text(encoding="utf-8"))
    labels = category_labels(dataset)
    by_source: dict[str, list[dict[str, Any]]] = defaultdict(list)

    for item in dataset.get("items", []):
        if not isinstance(item, dict) or is_image_item(item):
            continue
        source = item.get("text")
        if not isinstance(source, str) or not source or not has_japanese(source):
            continue
        effective = item.get("effective_translation") or item.get("translation") or item.get("agent_draft")
        if not isinstance(effective, str) or not effective:
            continue
        if effective == source:
            continue
        by_source[source].append(item)

    reports: list[dict[str, Any]] = []
    spacing_only_reports: list[dict[str, Any]] = []
    for source, items in by_source.items():
        translated = []
        raw_counter: Counter[str] = Counter()
        semantic_counter: Counter[str] = Counter()
        semantic_to_raw: dict[str, Counter[str]] = defaultdict(Counter)
        for item in items:
            effective = str(item.get("effective_translation") or item.get("translation") or item.get("agent_draft"))
            semantic = normalize_semantic_translation(effective)
            raw_counter[effective] += 1
            semantic_counter[semantic] += 1
            semantic_to_raw[semantic][effective] += 1
            translated.append(
                {
                    "item_id": item.get("item_id"),
                    "category_id": item.get("category_id"),
                    "category_label": labels.get(str(item.get("category_id")), str(item.get("category_id"))),
                    "source_group": item.get("source_group"),
                    "offset_hex": f"0x{int(item['offset']):06X}" if item.get("offset") is not None else None,
                    "effective_translation": effective,
                    "visible_translation": visible_text(effective),
                    "semantic_translation": semantic,
                    "translation_source": item.get("translation_source"),
                }
            )

        if len(raw_counter) <= 1:
            continue

        payload = {
            "source": source,
            "source_visible": visible_text(source),
            "occurrence_count": len(items),
            "raw_variant_count": len(raw_counter),
            "semantic_variant_count": len(semantic_counter),
            "semantic_variants": [
                {
                    "translation": semantic,
                    "visible_translation": visible_text(semantic),
                    "count": semantic_counter[semantic],
                    "raw_variants": [
                        {
                            "translation": raw,
                            "visible_translation": visible_text(raw),
                            "count": count,
                        }
                        for raw, count in semantic_to_raw[semantic].most_common()
                    ],
                }
                for semantic in sorted(semantic_counter, key=lambda value: (-semantic_counter[value], value))
            ],
            "items": sorted(
                translated,
                key=lambda row: (
                    row.get("category_label") or "",
                    row.get("source_group") or "",
                    row.get("offset_hex") or "",
                    row.get("item_id") or "",
                ),
            ),
        }
        if len(semantic_counter) > 1:
            reports.append(payload)
        else:
            spacing_only_reports.append(payload)

    reports.sort(key=lambda row: (-row["semantic_variant_count"], -row["occurrence_count"], row["source"]))
    spacing_only_reports.sort(key=lambda row: (-row["raw_variant_count"], -row["occurrence_count"], row["source"]))

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    JSON_REPORT.write_text(
        json.dumps(
            {
                "dataset": str(DATASET_PATH.relative_to(ROOT)),
                "semantic_variant_group_count": len(reports),
                "spacing_only_group_count": len(spacing_only_reports),
                "semantic_variant_groups": reports,
                "spacing_only_groups": spacing_only_reports,
            },
            ensure_ascii=False,
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )

    lines: list[str] = []
    lines.append("# 원문 동일 / 번역 분기 감사")
    lines.append("")
    lines.append(f"- dataset: `{DATASET_PATH.relative_to(ROOT)}`")
    lines.append(f"- 의미상 번역 분기 그룹: `{len(reports)}`")
    lines.append(f"- 공백/제어문자만 다른 그룹: `{len(spacing_only_reports)}`")
    lines.append("- 표기 규칙: `□`=전각 공백, `·`=반각 공백, `\\x0B`=인라인 구분자, `\\n`=개행")
    lines.append("")
    lines.append("## 의미상 번역 분기")
    lines.append("")
    for idx, group in enumerate(reports, 1):
        lines.append(f"### {idx}. {group['source_visible']}")
        lines.append("")
        lines.append(
            f"- 발생: `{group['occurrence_count']}` / 의미 변형: `{group['semantic_variant_count']}` / 원문: `{group['source']}`"
        )
        lines.append("- 번역 변형:")
        for variant in group["semantic_variants"]:
            raw_bits = ", ".join(
                f"`{raw['visible_translation']}` x{raw['count']}" for raw in variant["raw_variants"]
            )
            lines.append(f"  - `{variant['visible_translation']}` x{variant['count']} ({raw_bits})")
        lines.append("- 위치:")
        for row in group["items"][:20]:
            lines.append(
                "  - "
                f"`{row['offset_hex'] or row['item_id']}` "
                f"{row['category_label']} / {row['source_group']} / "
                f"`{row['visible_translation']}`"
            )
        if len(group["items"]) > 20:
            lines.append(f"  - ... {len(group['items']) - 20} more")
        lines.append("")

    if spacing_only_reports:
        lines.append("## 공백/제어문자만 다른 그룹")
        lines.append("")
        for idx, group in enumerate(spacing_only_reports[:100], 1):
            lines.append(f"### {idx}. {group['source_visible']}")
            lines.append("")
            lines.append(
                f"- 발생: `{group['occurrence_count']}` / raw 변형: `{group['raw_variant_count']}` / 정규화 번역: `{group['semantic_variants'][0]['visible_translation']}`"
            )
            for variant in group["semantic_variants"][0]["raw_variants"]:
                lines.append(f"  - `{variant['visible_translation']}` x{variant['count']}")
            lines.append("")
        if len(spacing_only_reports) > 100:
            lines.append(f"... {len(spacing_only_reports) - 100} more")
            lines.append("")

    MD_REPORT.write_text("\n".join(lines), encoding="utf-8")
    print(f"wrote {JSON_REPORT}")
    print(f"wrote {MD_REPORT}")
    print(f"semantic_variant_group_count {len(reports)}")
    print(f"spacing_only_group_count {len(spacing_only_reports)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
