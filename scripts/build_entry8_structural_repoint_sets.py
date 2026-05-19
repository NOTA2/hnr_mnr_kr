#!/usr/bin/env python3

from __future__ import annotations

import argparse
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CANDIDATES = ROOT / "analysis/entry8_repoint_candidates.json"
OUT_JSON = ROOT / "analysis/entry8_structural_repoint_sets.json"
OUT_MD = ROOT / "analysis/entry8_structural_repoint_sets.md"
PROTECTED = {0x150, 0x15C}


def load_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Build Entry8 structural repoint offset batches by segment.")
    parser.add_argument("--split-at", default="0x100", help="table_local split point for early/late batches")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    split_at = int(str(args.split_at), 0)
    data = load_json(CANDIDATES)
    rows = [
        row
        for row in data["rows"]
        if row.get("variable_offsets") and int(row["table_local"]) not in PROTECTED
    ]

    sets = {
        "safe_tail_baseline": {
            "description": "Previously working conservative tail-safe offset set.",
            "offsets": [
                offset
                for row in rows
                for offset in row.get("tail_safe_offsets", [])
            ],
        },
        "structural_early": {
            "description": f"All variable offsets in unprotected segments below 0x{split_at:X}.",
            "offsets": [
                offset
                for row in rows
                if int(row["table_local"]) < split_at
                for offset in row.get("variable_offsets", [])
            ],
        },
        "structural_late": {
            "description": f"All variable offsets in unprotected segments from 0x{split_at:X} upward.",
            "offsets": [
                offset
                for row in rows
                if int(row["table_local"]) >= split_at
                for offset in row.get("variable_offsets", [])
            ],
        },
        "structural_all_unprotected": {
            "description": "All variable offsets except protected opening segments.",
            "offsets": [
                offset
                for row in rows
                for offset in row.get("variable_offsets", [])
            ],
        },
    }

    for payload in sets.values():
        payload["offset_count"] = len(payload["offsets"])
        payload["offsets_csv"] = ",".join(f"0x{offset:06X}" for offset in payload["offsets"])

    OUT_JSON.write_text(json.dumps(sets, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    lines = [
        "# Entry8 Structural Repoint Sets",
        "",
        "| set | offsets | description |",
        "|---|---:|---|",
    ]
    for name, payload in sets.items():
        lines.append(f"| `{name}` | {payload['offset_count']} | {payload['description']} |")
    lines.extend(
        [
            "",
            "## Segment Counts",
            "",
            "| table | variable | tail-safe | bucket |",
            "|---:|---:|---:|---|",
        ]
    )
    for row in sorted(rows, key=lambda item: int(item["table_local"])):
        table = int(row["table_local"])
        bucket = "early" if table < split_at else "late"
        lines.append(
            f"| `0x{table:X}` | {len(row.get('variable_offsets', []))} | "
            f"{len(row.get('tail_safe_offsets', []))} | `{bucket}` |"
        )
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")

    print(f"wrote {OUT_JSON}")
    print(f"wrote {OUT_MD}")
    print(json.dumps({name: payload["offset_count"] for name, payload in sets.items()}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
