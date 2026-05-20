#!/usr/bin/env python3
"""Build Entry8 review candidates with no spaces and spare capacity.

The output is intentionally conservative: suggested text starts as the
current text. Reviewers can add fullwidth spaces manually in the workbench
candidate modal and then mark only those edited rows for apply.
"""

from __future__ import annotations

import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from gba_kor_tool.cli import TableCodec, encode_text
from gba_kor_tool.translation_normalization import normalize_translation_text

DATASET_PATH = ROOT / "confirmed_data" / "localization_workbench" / "workbench_dataset.json"
TABLE_PATH = ROOT / "analysis" / "generated_workbenches" / "current_review" / "prepared.tbl"
OUT_JSON = (
    ROOT
    / "confirmed_data"
    / "translation_workspace"
    / "audits"
    / "entry8_no_space_slack_candidates.json"
)
OUT_MD = OUT_JSON.with_suffix(".md")

ENTRY8_SOURCE_GROUP = "registry_a_entry8_prefixed_texts"
SPACE_CHARS = {" ", "\u3000"}
HANGUL_RE = re.compile(r"[가-힣]")


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def current_translation(item: dict) -> str:
    return (
        item.get("translation")
        or item.get("effective_translation")
        or item.get("agent_draft")
        or item.get("text")
        or ""
    )


def estimate_encoded_length(text: str, codec: TableCodec | None) -> int:
    if codec is not None:
        try:
            return len(encode_text(text, encoding="cp932", table=codec))
        except Exception:
            pass
    total = 0
    for ch in text:
        codepoint = ord(ch)
        if codepoint <= 0x7F or 0xFF61 <= codepoint <= 0xFF9F:
            total += 1
        else:
            total += 2
    return total


def no_space(text: str) -> bool:
    return not any(ch in text for ch in SPACE_CHARS)


def candidate_reason(spare: int, text: str) -> str:
    detail = "공백 없음"
    if len(text) <= 3:
        detail += ", 짧은 항목 포함"
    if not HANGUL_RE.search(text):
        detail += ", 한글 없음"
    return f"{detail}; {spare} bytes 여유. 필요 시 제안을 직접 수정해 전각 공백을 넣으세요."


def build_candidates() -> list[dict]:
    dataset = load_json(DATASET_PATH)
    codec = TableCodec.from_path(TABLE_PATH) if TABLE_PATH.exists() else None
    rows: list[dict] = []
    seen: set[tuple[str, int]] = set()

    for item in dataset.get("items", []):
        if item.get("source_group") != ENTRY8_SOURCE_GROUP:
            continue
        if item.get("offset") is None or item.get("byte_length") is None:
            continue
        offset = int(item["offset"])
        item_id = str(item.get("item_id") or "")
        key = (item_id, offset)
        if key in seen:
            continue
        seen.add(key)

        current = current_translation(item)
        if not current or not no_space(current):
            continue

        normalized = normalize_translation_text(
            current,
            source_group=ENTRY8_SOURCE_GROUP,
            reference_text=item.get("text"),
        )
        if not normalized or not no_space(normalized):
            continue

        capacity = int(item["byte_length"])
        used = estimate_encoded_length(normalized, codec)
        spare = capacity - used
        if spare <= 0:
            continue

        rows.append(
            {
                "item_id": item_id,
                "group_id": item.get("group_id") or "",
                "offset": offset,
                "hex": f"0x{offset:06X}",
                "capacity": capacity,
                "used": used,
                "suggestedUsed": used,
                "spare": spare,
                "suggestedSpare": spare,
                "source": item.get("text") or item.get("source") or "",
                "current": current,
                "suggested": current,
                "added_spaces": 0,
                "classification": "entry8_no_space_with_slack",
                "requires_manual_edit": True,
                "reason": candidate_reason(spare, normalized),
            }
        )

    rows.sort(key=lambda row: (row["offset"], row["item_id"]))
    return rows


def write_markdown(rows: list[dict]) -> None:
    hangul_count = sum(1 for row in rows if HANGUL_RE.search(row["current"]))
    short_count = sum(1 for row in rows if len(row["current"]) <= 3)
    total_spare = sum(int(row["spare"]) for row in rows)
    now = datetime.now(timezone.utc).isoformat(timespec="seconds")
    lines = [
        "# Entry8 No-Space Slack Candidates",
        "",
        f"- generated_at: `{now}`",
        f"- total: `{len(rows)}`",
        f"- contains_hangul: `{hangul_count}`",
        f"- short_items_len_3_or_less: `{short_count}`",
        f"- total_spare_bytes: `{total_spare}`",
        "",
        "이 목록은 현재 Entry8 번역문에 반각/전각 공백이 하나도 없고, 슬롯 byte 여유가 남은 항목입니다.",
        "제안값은 일부러 현재값과 같게 두었습니다. 후보 검수 모달에서 필요한 항목만 직접 전각 공백을 넣어 적용하세요.",
        "",
        "| offset | item | used/cap | spare | current |",
        "| --- | --- | ---: | ---: | --- |",
    ]
    for row in rows[:200]:
        current = str(row["current"]).replace("|", "\\|")
        lines.append(
            f"| {row['hex']} | `{row['item_id']}` | "
            f"{row['used']}/{row['capacity']} | {row['spare']} | {current} |"
        )
    if len(rows) > 200:
        lines.append("")
        lines.append(f"... first 200 shown of {len(rows)} rows. Full list: `{OUT_JSON.relative_to(ROOT)}`")
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    rows = build_candidates()
    OUT_JSON.parent.mkdir(parents=True, exist_ok=True)
    OUT_JSON.write_text(
        json.dumps(rows, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    write_markdown(rows)
    print(f"wrote {len(rows)} candidates -> {OUT_JSON.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
