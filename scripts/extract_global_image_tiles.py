#!/usr/bin/env python3

from __future__ import annotations

import argparse
import json
import math
import os
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from typing import Iterable


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from gba_kor_tool.cli import decompress_lz77


ROM = ROOT / "Hagane no Renkinjutsushi - Meisou no Rondo (Japan).gba"
IMAGE_DIR = ROOT / "confirmed_data" / "image_inventory"
LZ77_BLOCKS = IMAGE_DIR / "lz77_blocks.json"
GLOBAL_DIR = IMAGE_DIR / "global_tile_extraction"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="전역 이미지/타일 후보를 병렬로 최대한 많이 덤프합니다."
    )
    parser.add_argument("--rom", type=Path, default=ROM)
    parser.add_argument("--workers", type=int, default=max(2, (os.cpu_count() or 4) - 1))
    parser.add_argument("--columns", type=int, default=32)
    parser.add_argument("--lz77-limit", type=int, default=0, help="0이면 전체 tile-aligned LZ77 후보")
    parser.add_argument("--raw-window", type=lambda x: int(x, 0), default=0x4000)
    parser.add_argument("--raw-stride", type=lambda x: int(x, 0), default=0x4000)
    parser.add_argument("--skip-raw", action="store_true")
    parser.add_argument("--skip-lz77", action="store_true")
    return parser.parse_args()


def write_json(path: Path, payload) -> None:
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def render_4bpp_pgm(data: bytes, output_path: Path, *, columns: int) -> dict[str, int]:
    usable = len(data) - (len(data) % 32)
    data = data[:usable]
    tile_count = usable // 32
    rows = max(1, math.ceil(tile_count / columns))
    width = columns * 8
    height = rows * 8
    image = bytearray(width * height)

    for tile_index in range(tile_count):
        tile_x = (tile_index % columns) * 8
        tile_y = (tile_index // columns) * 8
        tile = data[tile_index * 32 : tile_index * 32 + 32]
        for row in range(8):
            row_data = tile[row * 4 : row * 4 + 4]
            for pair_index, byte in enumerate(row_data):
                lo = byte & 0x0F
                hi = (byte >> 4) & 0x0F
                pos = (tile_y + row) * width + tile_x + pair_index * 2
                image[pos] = lo * 17
                image[pos + 1] = hi * 17

    output_path.write_bytes(f"P5\n{width} {height}\n255\n".encode("ascii") + bytes(image))
    return {"tile_count": tile_count, "width": width, "height": height, "columns": columns}


def load_lz77_blocks() -> list[dict]:
    blocks = json.loads(LZ77_BLOCKS.read_text(encoding="utf-8"))
    return [
        block
        for block in blocks
        if int(block["decompressed_size"]) >= 32 and int(block["decompressed_size"]) % 32 == 0
    ]


def extract_lz77_block(rom_bytes: bytes, block: dict, index: int, *, columns: int, root: Path) -> dict:
    stem = f"{index:04d}_off_{int(block['offset']):08X}_size_{int(block['decompressed_size']):06X}"
    raw_path = root / "lz77_raw" / f"{stem}.bin"
    pgm_path = root / "lz77_pgm" / f"{stem}.pgm"
    payload, consumed = decompress_lz77(
        rom_bytes,
        int(block["offset"]),
        max_output_size=max(4 * 1024 * 1024, int(block["decompressed_size"]) + 0x1000),
    )
    raw_path.write_bytes(payload)
    render = render_4bpp_pgm(payload, pgm_path, columns=columns)
    return {
        **block,
        "index": index,
        "consumed": consumed,
        "raw_path": str(raw_path.relative_to(ROOT)),
        "preview_path": str(pgm_path.relative_to(ROOT)),
        **render,
    }


def iter_raw_windows(rom_size: int, *, window: int, stride: int) -> Iterable[tuple[int, int]]:
    offset = 0
    while offset < rom_size:
        size = min(window, rom_size - offset)
        if size >= 32:
            yield offset, size
        offset += stride


def extract_raw_window(rom_bytes: bytes, offset: int, size: int, index: int, *, columns: int, root: Path) -> dict:
    stem = f"{index:04d}_off_{offset:08X}_len_{size:06X}"
    raw_path = root / "raw_windows" / f"{stem}.bin"
    pgm_path = root / "raw_pgm" / f"{stem}.pgm"
    payload = rom_bytes[offset : offset + size]
    raw_path.write_bytes(payload)
    render = render_4bpp_pgm(payload, pgm_path, columns=columns)
    return {
        "index": index,
        "offset": offset,
        "rom_address": 0x08000000 + offset,
        "raw_size": size,
        "raw_path": str(raw_path.relative_to(ROOT)),
        "preview_path": str(pgm_path.relative_to(ROOT)),
        **render,
    }


def run_lz77(rom_bytes: bytes, *, workers: int, columns: int, limit: int, root: Path) -> list[dict]:
    blocks = load_lz77_blocks()
    blocks.sort(key=lambda block: (int(block["offset"]), int(block["decompressed_size"])))
    if limit > 0:
        blocks = blocks[:limit]
    results: list[dict] = []
    with ThreadPoolExecutor(max_workers=workers) as executor:
        futures = [
            executor.submit(extract_lz77_block, rom_bytes, block, index, columns=columns, root=root)
            for index, block in enumerate(blocks, start=1)
        ]
        for future in as_completed(futures):
            results.append(future.result())
    return sorted(results, key=lambda item: item["index"])


def run_raw(rom_bytes: bytes, *, workers: int, columns: int, window: int, stride: int, root: Path) -> list[dict]:
    jobs = list(iter_raw_windows(len(rom_bytes), window=window, stride=stride))
    results: list[dict] = []
    with ThreadPoolExecutor(max_workers=workers) as executor:
        futures = [
            executor.submit(extract_raw_window, rom_bytes, offset, size, index, columns=columns, root=root)
            for index, (offset, size) in enumerate(jobs, start=1)
        ]
        for future in as_completed(futures):
            results.append(future.result())
    return sorted(results, key=lambda item: item["index"])


def write_markdown(path: Path, report: dict) -> None:
    lines = [
        "# 전역 이미지/타일 추출 결과",
        "",
        f"- ROM: `{report['rom']}`",
        f"- workers: `{report['workers']}`",
        f"- columns: `{report['columns']}`",
        f"- LZ77 tile-aligned 후보: `{report['lz77_count']}`",
        f"- raw window 후보: `{report['raw_count']}`",
        "",
        "## 출력",
        "",
        "- `lz77_raw/`: LZ77 복원 원본",
        "- `lz77_pgm/`: LZ77 4bpp grayscale preview",
        "- `raw_windows/`: ROM 원본 window raw",
        "- `raw_pgm/`: ROM 원본 window 4bpp grayscale preview",
        "",
        "## 큰 LZ77 후보 Top 40",
        "",
    ]
    for item in sorted(report["lz77"], key=lambda row: int(row["decompressed_size"]), reverse=True)[:40]:
        lines.append(
            f"- `0x{int(item['offset']):08X}` size=`{item['decompressed_size']}` "
            f"tiles=`{item['tile_count']}` preview=`{item['preview_path']}`"
        )
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    args = parse_args()
    output_root = GLOBAL_DIR
    for child in ("lz77_raw", "lz77_pgm", "raw_windows", "raw_pgm", "notes"):
        (output_root / child).mkdir(parents=True, exist_ok=True)

    rom_bytes = args.rom.read_bytes()
    lz77_results: list[dict] = []
    raw_results: list[dict] = []
    if not args.skip_lz77:
        lz77_results = run_lz77(
            rom_bytes,
            workers=args.workers,
            columns=args.columns,
            limit=args.lz77_limit,
            root=output_root,
        )
    if not args.skip_raw:
        raw_results = run_raw(
            rom_bytes,
            workers=args.workers,
            columns=args.columns,
            window=args.raw_window,
            stride=args.raw_stride,
            root=output_root,
        )

    report = {
        "rom": str(args.rom.relative_to(ROOT) if args.rom.is_relative_to(ROOT) else args.rom),
        "workers": args.workers,
        "columns": args.columns,
        "raw_window": args.raw_window,
        "raw_stride": args.raw_stride,
        "lz77_count": len(lz77_results),
        "raw_count": len(raw_results),
        "lz77": lz77_results,
        "raw": raw_results,
    }
    report_path = output_root / "notes" / "global_tile_extraction_report.json"
    md_path = output_root / "notes" / "global_tile_extraction_report.md"
    write_json(report_path, report)
    write_markdown(md_path, report)
    print(f"lz77: {len(lz77_results)}")
    print(f"raw : {len(raw_results)}")
    print(f"report: {report_path}")
    print(f"markdown: {md_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
