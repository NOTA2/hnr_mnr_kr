#!/usr/bin/env python3

from __future__ import annotations

import json
import struct
import sys
from collections import Counter
from datetime import datetime
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from gba_kor_tool.translation_normalization import display_units

SOURCE_ROM = ROOT / "Hagane no Renkinjutsushi - Meisou no Rondo (Japan).gba"
EXTRACTED_TEXTS_DIR = ROOT / "confirmed_data" / "extracted_texts"
OUTPUT_DIR = ROOT / "confirmed_data" / "text_layout"
OUTPUT_JSON = OUTPUT_DIR / "text_layout_metadata_candidate_audit.json"
OUTPUT_MD = OUTPUT_DIR / "text_layout_metadata_candidate_audit.md"

FIELD_DELTAS = tuple(range(4, 0x24, 4))
STRICT_SMALL_S32_RATIO = 0.95
STRICT_CONSTANT_RATIO = 0.95
SUSPICIOUS_SMALL_S32_RATIO = 0.90
SUSPICIOUS_CONSTANT_RATIO = 0.50


def load_records(path: Path) -> list[dict[str, Any]]:
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, list):
        return []
    return [row for row in data if isinstance(row, dict) and isinstance(row.get("offset"), int)]


def signed32_at(data: bytes, offset: int) -> int | None:
    if offset < 0 or offset + 4 > len(data):
        return None
    return struct.unpack_from("<i", data, offset)[0]


def audit_field(records: list[dict[str, Any]], rom: bytes, delta: int) -> dict[str, Any] | None:
    rows: list[dict[str, Any]] = []
    constants: list[int] = []
    small_count = 0
    for record in records:
        offset = int(record["offset"])
        value = signed32_at(rom, offset + delta)
        if value is None:
            continue
        text = str(record.get("text", ""))
        visible_px = display_units(text) * 6
        constant = value - visible_px
        is_small_s32 = -512 <= value <= 512
        if is_small_s32:
            small_count += 1
            constants.append(constant)
        if len(rows) < 8:
            rows.append(
                {
                    "offset": offset,
                    "offset_hex": f"0x{offset:06X}",
                    "text": text,
                    "visible_px": visible_px,
                    "value": value,
                    "constant": constant,
                    "is_small_s32": is_small_s32,
                }
            )
    if not rows:
        return None
    total = len(records)
    small_ratio = small_count / total if total else 0.0
    top_constant = None
    top_constant_count = 0
    if constants:
        top_constant, top_constant_count = Counter(constants).most_common(1)[0]
    constant_ratio = top_constant_count / total if total else 0.0
    status = "none"
    if small_ratio >= STRICT_SMALL_S32_RATIO and constant_ratio >= STRICT_CONSTANT_RATIO:
        status = "strict_candidate"
    elif small_ratio >= SUSPICIOUS_SMALL_S32_RATIO and constant_ratio >= SUSPICIOUS_CONSTANT_RATIO:
        status = "suspicious"
    return {
        "field_delta": delta,
        "field_delta_hex": f"0x{delta:02X}",
        "small_s32_ratio": round(small_ratio, 4),
        "top_constant": top_constant,
        "top_constant_count": top_constant_count,
        "constant_ratio": round(constant_ratio, 4),
        "status": status,
        "sample_rows": rows,
    }


def audit_source_group(path: Path, rom: bytes) -> dict[str, Any]:
    records = load_records(path)
    offsets = [int(row["offset"]) for row in records]
    diffs = [b - a for a, b in zip(offsets, offsets[1:])]
    common_stride = None
    if diffs:
        common_stride, common_stride_count = Counter(diffs).most_common(1)[0]
    else:
        common_stride_count = 0
    field_reports = [
        report
        for delta in FIELD_DELTAS
        if (report := audit_field(records, rom, delta)) is not None
    ]
    candidates = [row for row in field_reports if row["status"] != "none"]
    return {
        "source_group": path.stem,
        "record_count": len(records),
        "offset_min_hex": f"0x{min(offsets):06X}" if offsets else None,
        "offset_max_hex": f"0x{max(offsets):06X}" if offsets else None,
        "common_stride": common_stride,
        "common_stride_count": common_stride_count,
        "candidate_fields": candidates,
    }


def build_markdown(report: dict[str, Any]) -> str:
    lines = [
        "# Text Layout Metadata Candidate Audit",
        "",
        f"- generated_at: `{report['generated_at']}`",
        f"- source_rom: `{report['source_rom']}`",
        "",
        "This audit searches extracted text records for nearby signed 32-bit fields",
        "that match `field_value = display_units(original_text) * 6 + constant`.",
        "Strict candidates still need runtime confirmation before applying patches.",
        "",
        "## Strict Candidates",
        "",
    ]
    strict = report["strict_candidates"]
    if not strict:
        lines.append("- None")
    else:
        lines.append("| source_group | field_delta | formula | record_count | stride | evidence |")
        lines.append("|---|---:|---|---:|---:|---|")
        for row in strict:
            field = row["field"]
            formula = f"value = display_units(text) * 6 + {field['top_constant']}"
            lines.append(
                "| {source_group} | `{delta}` | `{formula}` | {count} | {stride} | "
                "small={small}, constant={constant} |".format(
                    source_group=row["source_group"],
                    delta=field["field_delta_hex"],
                    formula=formula,
                    count=row["record_count"],
                    stride=row.get("common_stride"),
                    small=field["small_s32_ratio"],
                    constant=field["constant_ratio"],
                )
            )
    lines.extend(["", "## Suspicious Fields", ""])
    suspicious = report["suspicious_fields"]
    if not suspicious:
        lines.append("- None")
    else:
        lines.append("| source_group | field_delta | top_constant | small_ratio | constant_ratio |")
        lines.append("|---|---:|---:|---:|---:|")
        for row in suspicious:
            field = row["field"]
            lines.append(
                "| {source_group} | `{delta}` | {constant} | {small} | {ratio} |".format(
                    source_group=row["source_group"],
                    delta=field["field_delta_hex"],
                    constant=field["top_constant"],
                    small=field["small_s32_ratio"],
                    ratio=field["constant_ratio"],
                )
            )
    lines.extend(["", "## Source Group Summary", ""])
    lines.append("| source_group | records | common_stride | candidates |")
    lines.append("|---|---:|---:|---:|")
    for group in report["groups"]:
        lines.append(
            "| {source_group} | {record_count} | {stride} | {candidates} |".format(
                source_group=group["source_group"],
                record_count=group["record_count"],
                stride=group.get("common_stride"),
                candidates=len(group["candidate_fields"]),
            )
        )
    return "\n".join(lines) + "\n"


def main() -> int:
    if not SOURCE_ROM.is_file():
        raise SystemExit(f"missing source ROM: {SOURCE_ROM}")
    rom = SOURCE_ROM.read_bytes()
    groups = [
        audit_source_group(path, rom)
        for path in sorted(EXTRACTED_TEXTS_DIR.glob("*.json"))
        if path.name != "README.md"
    ]
    strict_candidates = []
    suspicious_fields = []
    for group in groups:
        for field in group["candidate_fields"]:
            row = {
                "source_group": group["source_group"],
                "record_count": group["record_count"],
                "common_stride": group.get("common_stride"),
                "field": field,
            }
            if field["status"] == "strict_candidate":
                strict_candidates.append(row)
            elif field["status"] == "suspicious":
                suspicious_fields.append(row)
    report = {
        "generated_at": datetime.now().isoformat(timespec="seconds"),
        "source_rom": str(SOURCE_ROM.relative_to(ROOT)),
        "criteria": {
            "formula": "field_value = display_units(original_text) * 6 + constant",
            "strict_small_s32_ratio": STRICT_SMALL_S32_RATIO,
            "strict_constant_ratio": STRICT_CONSTANT_RATIO,
            "suspicious_small_s32_ratio": SUSPICIOUS_SMALL_S32_RATIO,
            "suspicious_constant_ratio": SUSPICIOUS_CONSTANT_RATIO,
        },
        "strict_candidates": strict_candidates,
        "suspicious_fields": suspicious_fields,
        "groups": groups,
    }
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    OUTPUT_JSON.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    OUTPUT_MD.write_text(build_markdown(report), encoding="utf-8")
    print(f"wrote {OUTPUT_JSON.relative_to(ROOT)}")
    print(f"wrote {OUTPUT_MD.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
