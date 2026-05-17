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
        "status": "in_progress",
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
        "review_units": [
            {
                "id": "title_logo_wordmark",
                "status": "pending_review",
                "notes": [
                    "Main title/logo style text is not mapped by current canonical extracted text sources.",
                    "Treat as a concrete review unit rather than a generic bucket."
                ],
            },
            {
                "id": "title_screen_static_menu_wordmarks",
                "status": "pending_review",
                "notes": [
                    "Static title-screen menu labels and mode wordmarks may be image-backed.",
                    "No canonical extracted source currently covers title-screen wordmark art."
                ],
            },
            {
                "id": "event_or_cutscene_text_cards",
                "status": "pending_review",
                "notes": [
                    "Story/event presentation cards or overlays are a higher-value image-text candidate than generic event illustrations.",
                    "Keep separate from dialogue payloads, which are already confirmed non-image text."
                ],
            },
            {
                "id": "dialogue_window_frame_art",
                "status": "review_started",
                "notes": [
                    "Dialogue text itself is extracted text, but the window frame art is a distinct visual asset family.",
                    "This unit matters for localization QA even if it contains no baked text."
                ],
            },
            {
                "id": "portrait_headshot_assets",
                "status": "review_started",
                "notes": [
                    "Portraits are confirmed image assets.",
                    "Speaker text itself is not baked into portraits, but portrait coverage matters for dialogue QA and future image tasks."
                ],
            },
            {
                "id": "ui_panel_label_art",
                "status": "pending_review",
                "notes": [
                    "Panels, tabs, or framed UI labels that may contain baked text should be reviewed as a distinct unit.",
                    "Keep separate from plain extracted save/menu/system strings."
                ],
            },
            {
                "id": "ui_icon_badge_wordmarks",
                "status": "pending_review",
                "notes": [
                    "Icon/badge-sized wordmarks should be reviewed separately from larger UI panels.",
                    "Useful to keep isolated because replacement strategy is likely different from panel art."
                ],
            },
            {
                "id": "battle_result_or_reward_banners",
                "status": "pending_review",
                "notes": [
                    "Result/reward banners are plausible baked-text candidates in battle or post-battle presentation.",
                    "Separate from dialogue and term-description sources, which are already extracted text."
                ],
            },
        ],
        "operational_reading": [
            "Image text inventory is now started as a separate audit track.",
            "Several important text contexts are already confirmed to be non-image text and should not block translation.",
            "The remaining work is asset-side review of concrete review_units rather than reopening canonical text extraction."
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
    lines.extend(["", "## Review Units", ""])
    for item in data["review_units"]:
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
            "- 이 inventory 는 막연한 bucket 이 아니라 실제 검토 단위에 가까운 `review_units` 중심으로 유지한다.",
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
