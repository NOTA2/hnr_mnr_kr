#!/usr/bin/env python3

from __future__ import annotations

import argparse
import json
import math
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from gba_kor_tool.cli import decompress_lz77

ROM = ROOT / "Hagane no Renkinjutsushi - Meisou no Rondo (Japan).gba"
LZ77_BLOCKS = ROOT / "confirmed_data" / "image_inventory" / "lz77_blocks.json"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="review unit 후보용 LZ77/4bpp 덤프를 준비합니다.")
    parser.add_argument("review_unit", choices=["title_logo_wordmark"])
    parser.add_argument("--limit", type=int, default=12)
    return parser.parse_args()


def load_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, payload) -> None:
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def render_raw_4bpp(raw_path: Path, output_path: Path, *, columns: int = 32) -> dict[str, int]:
    data = raw_path.read_bytes()
    if len(data) % 32 != 0:
        raise ValueError(f"raw 4bpp size is not tile-aligned: {raw_path}")
    tile_count = len(data) // 32
    rows = math.ceil(tile_count / columns)
    width = columns * 8
    height = rows * 8
    image = bytearray(width * height)

    for tile_index in range(tile_count):
        tile_x = (tile_index % columns) * 8
        tile_y = (tile_index // columns) * 8
        tile = data[tile_index * 32 : (tile_index + 1) * 32]
        for row in range(8):
            row_data = tile[row * 4 : row * 4 + 4]
            for pair_index, byte in enumerate(row_data):
                lo = byte & 0x0F
                hi = (byte >> 4) & 0x0F
                image[(tile_y + row) * width + tile_x + pair_index * 2] = lo * 17
                image[(tile_y + row) * width + tile_x + pair_index * 2 + 1] = hi * 17

    output_path.write_bytes(
        f"P5\n{width} {height}\n255\n".encode("ascii") + bytes(image)
    )
    return {"tile_count": tile_count, "width": width, "height": height, "columns": columns, "rows": rows}


def candidate_blocks_for_title_logo(limit: int) -> list[dict]:
    blocks = load_json(LZ77_BLOCKS)
    candidates = [
        block
        for block in blocks
        if block["decompressed_size"] >= 0x8000 and block["decompressed_size"] % 32 == 0
    ]
    candidates.sort(key=lambda block: (block["decompressed_size"], block["compressed_size"]), reverse=True)
    return candidates[:limit]


def build_title_logo_candidates(limit: int) -> int:
    workspace = ROOT / "confirmed_data" / "image_inventory" / "workspaces" / "01_title_logo_wordmark"
    dumps_dir = workspace / "dumps"
    exports_dir = workspace / "exports"
    notes_dir = workspace / "notes"
    for path in (dumps_dir, exports_dir, notes_dir):
        path.mkdir(parents=True, exist_ok=True)

    rom_bytes = ROM.read_bytes()
    report = {"review_unit": "title_logo_wordmark", "candidates": []}
    for index, block in enumerate(candidate_blocks_for_title_logo(limit), start=1):
        stem = f"{index:02d}_off_{block['offset']:08X}"
        raw_path = dumps_dir / f"{stem}.bin"
        pgm_path = exports_dir / f"{stem}.pgm"
        payload, _ = decompress_lz77(rom_bytes, block["offset"], max_output_size=4 * 1024 * 1024)
        raw_path.write_bytes(payload)
        render_info = render_raw_4bpp(raw_path, pgm_path)
        report["candidates"].append(
            {
                **block,
                "raw_path": str(raw_path.relative_to(ROOT)),
                "preview_path": str(pgm_path.relative_to(ROOT)),
                **render_info,
            }
        )

    report_path = notes_dir / "title_logo_candidate_report.json"
    write_json(report_path, report)
    md_path = notes_dir / "title_logo_candidate_report.md"
    lines = [
        "# 타이틀 로고 후보 덤프",
        "",
        f"- 후보 수: `{len(report['candidates'])}`",
        "",
    ]
    for item in report["candidates"]:
        lines.extend(
            [
                f"## 0x{item['offset']:08X}",
                "",
                f"- 압축 크기: `{item['compressed_size']}`",
                f"- 복원 크기: `{item['decompressed_size']}`",
                f"- raw: `{item['raw_path']}`",
                f"- preview: `{item['preview_path']}`",
                f"- 타일 수: `{item['tile_count']}` / 크기: `{item['width']}x{item['height']}`",
                "",
            ]
        )
    md_path.write_text("\n".join(lines), encoding="utf-8")
    print(f"report: {report_path}")
    print(f"markdown: {md_path}")
    return 0


def main() -> int:
    args = parse_args()
    if args.review_unit == "title_logo_wordmark":
        return build_title_logo_candidates(args.limit)
    raise SystemExit("unsupported review unit")


if __name__ == "__main__":
    raise SystemExit(main())
