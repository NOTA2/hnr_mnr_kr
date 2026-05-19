#!/usr/bin/env python3

from __future__ import annotations

import json
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

import sys

if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from gba_kor_tool.cli import ROM_BASE, TableCodec, encode_text
from gba_kor_tool.translation_normalization import normalize_translation_text

DATASET_PATH = ROOT / "confirmed_data" / "localization_workbench" / "workbench_dataset.json"
OUT_JSON = ROOT / "confirmed_data" / "translation_workspace" / "translation_expansion_opportunities.json"
OUT_MD = ROOT / "confirmed_data" / "translation_workspace" / "translation_expansion_opportunities.md"
TABLE_PATH = ROOT / "analysis" / "generated_workbenches" / "current_review" / "prepared.tbl"
ROM_CANDIDATES = [
    ROOT / "patched_roms" / "current_review" / "current_review_font_ready.gba",
    ROOT / "Hagane no Renkinjutsushi - Meisou no Rondo (Japan).gba",
]

PACKED_REPOINT_SOURCE_GROUPS = {"registry_d_fc_script_texts"}


def load_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def load_rom() -> tuple[Path, bytes]:
    for path in ROM_CANDIDATES:
        if path.exists():
            return path, path.read_bytes()
    raise SystemExit("no ROM available for pointer audit")


def estimate_encoded_length(text: str, codec: TableCodec | None) -> int:
    if codec is not None:
        try:
            return len(encode_text(text, encoding="cp932", table=codec))
        except Exception:
            pass
    total = 0
    for ch in text:
        try:
            total += len(ch.encode("cp932"))
        except UnicodeEncodeError:
            total += 2
    return total


def build_aligned_pointer_index(rom: bytes) -> dict[int, list[int]]:
    pointers: dict[int, list[int]] = defaultdict(list)
    rom_size = len(rom)
    for offset in range(0, rom_size - 3, 4):
        value = int.from_bytes(rom[offset:offset + 4], "little")
        if ROM_BASE <= value < ROM_BASE + rom_size:
            target = value - ROM_BASE
            if len(pointers[target]) < 8:
                pointers[target].append(offset)
    return pointers


def append_terminator(item: dict) -> bool:
    return item.get("source_group") != "save_menu_texts" and item.get("append_terminator") is not False


def original_capacity(item: dict) -> int:
    return int(item["byte_length"]) + (1 if append_terminator(item) else 0)


def current_translation(item: dict) -> str:
    return item.get("effective_translation") or item.get("translation") or item.get("agent_draft") or item.get("text") or ""


def classify(item: dict, pointer_count: int, slack: int) -> str:
    source_group = item.get("source_group")
    if source_group in PACKED_REPOINT_SOURCE_GROUPS:
        return "packed_repoint_available"
    if pointer_count:
        return "direct_repoint_available"
    if slack > 0:
        return "in_place_slack_only"
    if slack == 0:
        return "fixed_capacity_exact"
    return "too_long_without_pointer"


def main() -> int:
    dataset = load_json(DATASET_PATH)
    rom_path, rom = load_rom()
    pointer_index = build_aligned_pointer_index(rom)
    codec = TableCodec.from_path(TABLE_PATH) if TABLE_PATH.exists() else None

    records = []
    by_group = defaultdict(Counter)
    examples = defaultdict(list)

    seen_offsets: set[tuple[str, int]] = set()
    for item in dataset.get("items", []):
        if item.get("offset") is None or item.get("category_id") == "image_review_units":
            continue
        source_group = item.get("source_group") or ""
        offset = int(item["offset"])
        key = (source_group, offset)
        if key in seen_offsets:
            continue
        seen_offsets.add(key)

        text = current_translation(item)
        normalized = normalize_translation_text(
            text,
            source_group=source_group,
            reference_text=item.get("text"),
        )
        payload_length = estimate_encoded_length(normalized, codec) + (1 if append_terminator(item) else 0)
        capacity = original_capacity(item)
        slack = capacity - payload_length
        pointers = pointer_index.get(offset, [])
        mode = classify(item, len(pointers), slack)

        record = {
            "item_id": item.get("item_id"),
            "source_group": source_group,
            "offset": offset,
            "offset_hex": f"0x{offset:06X}",
            "text": item.get("text"),
            "translation": normalized,
            "payload_length": payload_length,
            "original_capacity": capacity,
            "slack_bytes": slack,
            "direct_pointer_count": len(pointers),
            "direct_pointer_offsets": [f"0x{ptr:06X}" for ptr in pointers],
            "expansion_mode": mode,
        }
        records.append(record)
        by_group[source_group][mode] += 1
        if len(examples[(source_group, mode)]) < 8:
            examples[(source_group, mode)].append(record)

    summary = {
        source_group: dict(counter)
        for source_group, counter in sorted(by_group.items())
    }
    payload = {
        "last_updated": datetime.now(timezone.utc).isoformat(),
        "dataset": str(DATASET_PATH.relative_to(ROOT)),
        "rom_used_for_pointer_scan": str(rom_path.relative_to(ROOT)),
        "reading": [
            "packed_repoint_available: Registry D처럼 청크/entry 재패킹이 가능하므로 원문 byte 슬롯보다 긴 번역을 허용한다.",
            "direct_repoint_available: 문자열 직접 포인터가 확인되어, 현재 슬롯을 넘으면 새 위치에 쓰고 포인터를 갱신할 수 있다.",
            "in_place_slack_only: 직접 포인터는 없지만 현재 슬롯에 남은 byte 여유가 있으므로 그 범위 안에서 자연스럽게 늘릴 수 있다.",
            "fixed_capacity_exact: 직접 포인터가 없고 현재 번역이 슬롯을 정확히 채운다. 더 늘리면 원문 잔류/skipped 위험이 있다.",
            "too_long_without_pointer: 현재 번역이 슬롯을 넘는데 직접 포인터가 없다. 반드시 줄이거나 별도 구조 분석이 필요하다.",
        ],
        "summary": summary,
        "records": records,
    }
    OUT_JSON.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    lines = [
        "# Translation Expansion Opportunities",
        "",
        f"- Last updated: `{payload['last_updated']}`",
        f"- Dataset: `{payload['dataset']}`",
        f"- ROM used for pointer scan: `{payload['rom_used_for_pointer_scan']}`",
        "",
        "## Reading",
        "",
    ]
    for note in payload["reading"]:
        lines.append(f"- {note}")
    lines += ["", "## Source Summary", "", "| Source | Expansion modes |", "|---|---|"]
    for source_group, counter in summary.items():
        joined = ", ".join(f"`{mode}: {count}`" for mode, count in sorted(counter.items()))
        lines.append(f"| {source_group} | {joined} |")
    lines += ["", "## Examples", ""]
    for (source_group, mode), rows in sorted(examples.items()):
        lines.append(f"### `{source_group}` / `{mode}`")
        lines.append("")
        lines.append("| Offset | Original | Current | Payload/Capacity | Pointers |")
        lines.append("|---|---|---|---:|---:|")
        for row in rows:
            original = str(row["text"]).replace("\n", "\\n")
            translation = str(row["translation"]).replace("\n", "\\n")
            lines.append(
                f"| `{row['offset_hex']}` | {original} | {translation} | "
                f"{row['payload_length']}/{row['original_capacity']} | {row['direct_pointer_count']} |"
            )
        lines.append("")

    OUT_MD.write_text("\n".join(lines), encoding="utf-8")
    print(f"written: {OUT_JSON}")
    print(f"written: {OUT_MD}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
