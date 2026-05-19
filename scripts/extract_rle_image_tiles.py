#!/usr/bin/env python3
"""Extract GBA BIOS RLE-compressed graphics candidates and render 4bpp previews."""

from __future__ import annotations

import argparse
import json
import math
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_ROM = ROOT / "Hagane no Renkinjutsushi - Meisou no Rondo (Japan).gba"
DEFAULT_OUT = ROOT / "confirmed_data/image_inventory/rle_tile_extraction"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--rom", type=Path, default=DEFAULT_ROM)
    parser.add_argument("--out-dir", type=Path, default=DEFAULT_OUT)
    parser.add_argument("--columns", type=int, default=32)
    parser.add_argument("--min-size", type=lambda x: int(x, 0), default=0x20)
    parser.add_argument("--max-size", type=lambda x: int(x, 0), default=0x20000)
    return parser.parse_args()


def decompress_gba_rle(data: bytes, offset: int, *, max_output_size: int) -> tuple[bytes, int] | None:
    if offset + 4 > len(data) or data[offset] != 0x30:
        return None
    expected = data[offset + 1] | (data[offset + 2] << 8) | (data[offset + 3] << 16)
    if expected <= 0 or expected > max_output_size:
        return None

    cursor = offset + 4
    out = bytearray()
    try:
        while len(out) < expected:
            flags = data[cursor]
            cursor += 1
            if flags & 0x80:
                count = (flags & 0x7F) + 3
                value = data[cursor]
                cursor += 1
                out.extend([value] * count)
            else:
                count = (flags & 0x7F) + 1
                out.extend(data[cursor : cursor + count])
                cursor += count
            if cursor > len(data) or len(out) > expected + 0x100:
                return None
    except IndexError:
        return None

    if len(out) != expected:
        out = out[:expected]
    return bytes(out), cursor - offset


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


def scan_rle_blocks(rom: bytes, *, min_size: int, max_size: int) -> list[dict]:
    blocks: list[dict] = []
    occupied_until = -1
    for offset, value in enumerate(rom):
        if offset < occupied_until or value != 0x30:
            continue
        result = decompress_gba_rle(rom, offset, max_output_size=max_size)
        if not result:
            continue
        payload, consumed = result
        if len(payload) < min_size:
            continue
        if len(payload) % 32 != 0:
            continue
        blocks.append(
            {
                "index": len(blocks) + 1,
                "offset": offset,
                "rom_address": 0x08000000 + offset,
                "compressed_size": consumed,
                "decompressed_size": len(payload),
            }
        )
        occupied_until = offset + consumed
    return blocks


def main() -> int:
    args = parse_args()
    out_dir = args.out_dir.resolve()
    raw_dir = out_dir / "rle_raw"
    pgm_dir = out_dir / "rle_pgm"
    notes_dir = out_dir / "notes"
    for path in (raw_dir, pgm_dir, notes_dir):
        path.mkdir(parents=True, exist_ok=True)

    rom = args.rom.resolve().read_bytes()
    blocks = scan_rle_blocks(rom, min_size=args.min_size, max_size=args.max_size)
    enriched: list[dict] = []
    for block in blocks:
        payload, consumed = decompress_gba_rle(rom, block["offset"], max_output_size=args.max_size) or (b"", 0)
        stem = f"{block['index']:04d}_off_{block['offset']:08X}_size_{block['decompressed_size']:06X}"
        raw_path = raw_dir / f"{stem}.bin"
        pgm_path = pgm_dir / f"{stem}.pgm"
        raw_path.write_bytes(payload)
        render = render_4bpp_pgm(payload, pgm_path, columns=args.columns)
        enriched.append(
            {
                **block,
                "compressed_size": consumed,
                "raw_path": str(raw_path.relative_to(ROOT)),
                "preview_path": str(pgm_path.relative_to(ROOT)),
                **render,
            }
        )

    report = {
        "rom": str(args.rom),
        "count": len(enriched),
        "blocks": enriched,
    }
    report_path = notes_dir / "rle_tile_extraction_report.json"
    report_path.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    lines = ["# RLE Tile Extraction", "", f"- count: `{len(enriched)}`", ""]
    for block in enriched:
        lines.append(
            f"- `0x{block['offset']:08X}` size=`{block['decompressed_size']}` "
            f"compressed=`{block['compressed_size']}` preview=`{block['preview_path']}`"
        )
    (notes_dir / "rle_tile_extraction_report.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"rle blocks: {len(enriched)}")
    print(f"report    : {report_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
