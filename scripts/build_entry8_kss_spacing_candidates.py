#!/usr/bin/env python3
"""Build Entry8 spacing suggestions with KSS correct_spacing.

KSS decides where spaces should go. This script only filters unsafe results and
trims the suggested spaces to the Entry8 byte capacity. It never changes
non-space characters.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterable

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from gba_kor_tool.cli import TableCodec, encode_text
from gba_kor_tool.translation_normalization import normalize_translation_text

INPUT_JSON = (
    ROOT
    / "confirmed_data"
    / "translation_workspace"
    / "audits"
    / "entry8_no_space_slack_candidates.json"
)
OUT_JSON = (
    ROOT
    / "confirmed_data"
    / "translation_workspace"
    / "audits"
    / "entry8_kss_spacing_candidates.json"
)
OUT_MD = OUT_JSON.with_suffix(".md")
TABLE_PATH = ROOT / "analysis" / "generated_workbenches" / "current_review" / "prepared.tbl"

ENTRY8_SOURCE_GROUP = "registry_a_entry8_prefixed_texts"
FULLWIDTH_SPACE = "\u3000"
SPACE_CHARS = {" ", FULLWIDTH_SPACE}
HANGUL_RE = re.compile(r"[가-힣]")


def load_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def compact_spaces(text: str) -> str:
    return "".join(ch for ch in text if ch not in SPACE_CHARS)


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


def spacing_boundaries(original: str, spaced: str) -> list[int] | None:
    compact = compact_spaces(original)
    if compact_spaces(spaced) != compact:
        return None

    boundaries: list[int] = []
    index = 0
    for ch in spaced:
        if ch in SPACE_CHARS:
            if 0 < index < len(compact):
                boundaries.append(index)
            continue
        if index >= len(compact) or ch != compact[index]:
            return None
        index += 1
    if index != len(compact):
        return None
    return sorted(set(boundaries))


def center_first_boundary_order(length: int, boundaries: Iterable[int]) -> list[int]:
    available = sorted({b for b in boundaries if 0 < b < length})
    order: list[int] = []
    selected: set[int] = set()
    queue: list[tuple[int, int]] = [(0, length)]

    while queue and len(selected) < len(available):
        left, right = queue.pop(0)
        choices = [b for b in available if left < b < right and b not in selected]
        if not choices:
            continue
        middle = (left + right) / 2
        chosen = min(choices, key=lambda b: (abs(b - middle), b))
        selected.add(chosen)
        order.append(chosen)
        queue.append((left, chosen))
        queue.append((chosen, right))
    return order


def choose_boundaries(text: str, boundaries: Iterable[int], max_spaces: int) -> list[int]:
    available = sorted({b for b in boundaries if 0 < b < len(text)})
    if max_spaces == 1 and len(available) == 2:
        return [available[0]]
    ordered = center_first_boundary_order(len(text), available)
    return sorted(ordered[:max_spaces])


def insert_fullwidth_spaces(text: str, boundaries: Iterable[int]) -> str:
    selected = set(boundaries)
    out: list[str] = []
    for index, ch in enumerate(text, start=1):
        out.append(ch)
        if index in selected:
            out.append(FULLWIDTH_SPACE)
    return "".join(out)


def load_kss_spacing():
    try:
        from kss import Kss
    except Exception as exc:
        raise SystemExit(
            "KSS가 설치되어 있지 않습니다. 전용 venv 예: "
            "python3 -m venv .venv-kss && .venv-kss/bin/python -m pip install kss"
        ) from exc
    return Kss("correct_spacing")


def call_spacing(module, text: str) -> str:
    try:
        result = module(text, num_workers=1)
    except TypeError:
        result = module(text)
    if isinstance(result, list):
        return str(result[0] if result else "")
    return str(result)


def build_candidates(args: argparse.Namespace) -> tuple[list[dict], dict]:
    input_rows = load_json(args.input)
    if args.limit:
        input_rows = input_rows[: args.limit]
    codec = TableCodec.from_path(TABLE_PATH) if TABLE_PATH.exists() else None
    spacing = load_kss_spacing()
    rows: list[dict] = []
    skipped: Counter[str] = Counter()

    for source_row in input_rows:
        current = str(source_row.get("current") or "")
        if not current or not HANGUL_RE.search(current):
            skipped["no_hangul"] += 1
            continue

        capacity = int(source_row["capacity"])
        used = int(source_row["used"])
        max_spaces = (capacity - used) // 2
        if max_spaces <= 0:
            skipped["no_capacity_for_space"] += 1
            continue

        try:
            spaced = call_spacing(spacing, current)
        except Exception:
            skipped["kss_error"] += 1
            if args.stop_on_error:
                raise
            continue

        boundaries = spacing_boundaries(current, spaced)
        if boundaries is None:
            skipped["kss_changed_non_space_text"] += 1
            continue
        if not boundaries:
            skipped["kss_no_spacing"] += 1
            continue

        selected = choose_boundaries(current, boundaries, max_spaces)
        if not selected:
            skipped["no_selected_boundary"] += 1
            continue

        suggested = insert_fullwidth_spaces(current, selected)
        normalized = normalize_translation_text(
            suggested,
            source_group=ENTRY8_SOURCE_GROUP,
            reference_text=source_row.get("source"),
        )
        suggested_used = estimate_encoded_length(normalized, codec)
        if suggested_used > capacity:
            skipped["overflow_after_selection"] += 1
            continue
        if compact_spaces(suggested) != compact_spaces(current):
            skipped["changed_non_space_after_selection"] += 1
            continue

        omitted = [b for b in boundaries if b not in selected]
        out = dict(source_row)
        out.update(
            {
                "suggested": suggested,
                "suggestedUsed": suggested_used,
                "suggestedSpare": capacity - suggested_used,
                "added_spaces": len(selected),
                "kss_checked": spaced,
                "kss_boundaries": boundaries,
                "selected_boundaries": selected,
                "omitted_boundaries": omitted,
                "classification": "entry8_kss_spacing_only",
                "requires_manual_edit": False,
                "reason": (
                    "KSS correct_spacing 기반 띄어쓰기 후보; "
                    f"{len(boundaries)}개 공백 후보 중 {len(selected)}개 적용"
                    + (f", byte 한계로 {len(omitted)}개 생략" if omitted else "")
                ),
            }
        )
        rows.append(out)

    rows.sort(key=lambda row: (len(row["omitted_boundaries"]), int(row["suggestedSpare"]), int(row["offset"])))
    return rows, dict(skipped)


def write_outputs(rows: list[dict], skipped: dict, args: argparse.Namespace) -> None:
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(rows, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    now = datetime.now(timezone.utc).isoformat(timespec="seconds")
    lines = [
        "# Entry8 KSS Spacing Candidates",
        "",
        f"- generated_at: `{now}`",
        f"- input: `{args.input.relative_to(ROOT)}`",
        f"- total_candidates: `{len(rows)}`",
        f"- skipped: `{skipped}`",
        "",
        "KSS `correct_spacing` 결과에서 비공백 문자가 바뀐 항목은 제외했다.",
        "Entry8 byte 한도 때문에 모든 공백이 들어가지 못하면 중앙/왼쪽/오른쪽 우선순위로 일부만 선택한다.",
        "",
        "| offset | item | used -> suggested/cap | current | kss | suggested |",
        "| --- | --- | ---: | --- | --- | --- |",
    ]
    for row in rows[:200]:
        current = str(row["current"]).replace("|", "\\|")
        kss_checked = str(row["kss_checked"]).replace("|", "\\|")
        suggested = str(row["suggested"]).replace("|", "\\|")
        lines.append(
            f"| {row['hex']} | `{row['item_id']}` | "
            f"{row['used']} -> {row['suggestedUsed']}/{row['capacity']} | "
            f"{current} | {kss_checked} | {suggested} |"
        )
    if len(rows) > 200:
        lines.append("")
        lines.append(f"... first 200 shown of {len(rows)} rows. Full list: `{args.output.relative_to(ROOT)}`")
    args.markdown.write_text("\n".join(lines) + "\n", encoding="utf-8")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", type=Path, default=INPUT_JSON)
    parser.add_argument("--output", type=Path, default=OUT_JSON)
    parser.add_argument("--markdown", type=Path, default=OUT_MD)
    parser.add_argument("--limit", type=int, default=0)
    parser.add_argument("--stop-on-error", action="store_true")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    args.input = args.input.resolve()
    args.output = args.output.resolve()
    args.markdown = args.markdown.resolve()
    rows, skipped = build_candidates(args)
    write_outputs(rows, skipped, args)
    print(f"wrote {len(rows)} candidates -> {args.output.relative_to(ROOT)}")
    print(f"skipped: {skipped}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
