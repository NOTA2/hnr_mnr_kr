#!/usr/bin/env python3

from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DATA_ROOT = ROOT / "confirmed_data"
OUT_DIR = DATA_ROOT / "image_inventory"
OUT_JSON = OUT_DIR / "image_text_inventory.json"
OUT_MD = OUT_DIR / "image_text_inventory.md"
OUT_README = OUT_DIR / "README.md"


def build() -> dict:
    return {
        "version": 1,
        "last_updated": "2026-05-17",
        "status": "started",
        "note": "This is an inventory/status layer, not a completed extraction of image-baked text.",
        "confirmed_non_image_text_contexts": [
            {
                "context": "startup_intro_card",
                "reason": "Handled as fixed-slot text records in startup_intro_texts.json, not baked image text.",
            },
            {
                "context": "dialogue_box_payloads",
                "reason": "Entry8 and Registry D dialogue strings are extracted as script records; portraits are separate image assets.",
            },
            {
                "context": "world_map_location_labels",
                "reason": "Location names are extracted in location_texts.json and rendered by the world-map text path.",
            },
            {
                "context": "save_menu_prompts",
                "reason": "Save/menu prompts are extracted as 01 FF command-stream records, not image-baked labels.",
            },
            {
                "context": "credits_strings",
                "reason": "Credits are extracted as padded plain text records, not confirmed image text.",
            },
        ],
        "review_buckets": [
            {
                "id": "title_logo_and_static_title_graphics",
                "status": "pending_review",
                "notes": [
                    "Potential baked-text candidate bucket.",
                    "No canonical extracted source currently maps this bucket."
                ],
            },
            {
                "id": "event_illustration_overlays_or_cutscene_cards",
                "status": "pending_review",
                "notes": [
                    "Potential baked-text candidate bucket for story/event presentation assets.",
                    "Not yet inventoried structurally."
                ],
            },
            {
                "id": "ui_icons_badges_or_panels_with_embedded_labels",
                "status": "pending_review",
                "notes": [
                    "Potential baked-text candidate bucket for non-dialogue UI art.",
                    "Needs later asset review."
                ],
            },
            {
                "id": "portrait_assets",
                "status": "review_started",
                "notes": [
                    "Portraits are confirmed image assets.",
                    "Current evidence suggests speaker text itself is not baked into portraits, but portrait/image inventory still matters for localization QA."
                ],
            },
        ],
        "operational_reading": [
            "Image text inventory is now started as a separate audit track.",
            "Several important text contexts are already confirmed to be non-image text and should not block translation.",
            "The remaining work is asset-side review of review_buckets rather than reopening canonical text extraction."
        ],
    }


def render_md(data: dict) -> str:
    lines = [
        "# Image Text Inventory",
        "",
        f"- status: `{data['status']}`",
        f"- last_updated: `{data['last_updated']}`",
        "",
        "## Confirmed Non-Image Text Contexts",
        "",
    ]
    for item in data["confirmed_non_image_text_contexts"]:
        lines.append(f"- `{item['context']}`: {item['reason']}")
    lines.extend(["", "## Review Buckets", ""])
    for item in data["review_buckets"]:
        lines.append(f"- `{item['id']}` (`{item['status']}`)")
        for note in item["notes"]:
            lines.append(f"  {note}")
    lines.extend(["", "## Operational Reading", ""])
    for note in data["operational_reading"]:
        lines.append(f"- {note}")
    lines.append("")
    return "\n".join(lines)


def render_readme() -> str:
    return "\n".join(
        [
            "# Image Inventory",
            "",
            "이 폴더는 **이미지에 구워진 텍스트 inventory / 이미지 자산 검토 상태**를 모아두는 곳이다.",
            "",
            "## 현재 파일",
            "",
            "- `image_text_inventory.json`",
            "- `image_text_inventory.md`",
            "",
            "## 사용 원칙",
            "",
            "- canonical extracted text 와 baked image text 는 분리해서 관리한다.",
            "- 이 inventory 는 실제 image-side review 가 진행되기 전까지는 `review bucket` 중심으로 유지한다.",
            "",
            "## 재생성",
            "",
            "```bash",
            "python3 scripts/build_image_text_inventory.py",
            "```",
            "",
        ]
    )


def main() -> int:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    data = build()
    OUT_JSON.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    OUT_MD.write_text(render_md(data), encoding="utf-8")
    OUT_README.write_text(render_readme(), encoding="utf-8")
    print(f"wrote {OUT_JSON}")
    print(f"wrote {OUT_MD}")
    print(f"wrote {OUT_README}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
