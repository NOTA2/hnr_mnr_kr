#!/usr/bin/env python3
"""Render pymgba runtime VRAM dumps into palette-aware tile sheet PNGs."""

from __future__ import annotations

import argparse
import binascii
import json
import math
import struct
import zlib
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_PROBE_DIR = ROOT / "confirmed_data/image_inventory/pymgba_runtime_timeline"
DEFAULT_OUT_DIR = ROOT / "confirmed_data/image_inventory/runtime_tile_sheets"

TILE_BYTES_4BPP = 32
CHARBLOCK_BYTES = 0x4000
TILES_PER_CHARBLOCK = CHARBLOCK_BYTES // TILE_BYTES_4BPP


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--probe-dir", type=Path, default=DEFAULT_PROBE_DIR)
    parser.add_argument("--out-dir", type=Path, default=DEFAULT_OUT_DIR)
    parser.add_argument("--columns", type=int, default=32)
    parser.add_argument("--palettes", default="all", help="all or comma-separated palette indexes, e.g. 0,1,7")
    parser.add_argument("--include-blank", action="store_true", help="write sheets even when a charblock is blank")
    return parser.parse_args()


def png_chunk(kind: bytes, payload: bytes) -> bytes:
    return (
        struct.pack(">I", len(payload))
        + kind
        + payload
        + struct.pack(">I", binascii.crc32(kind + payload) & 0xFFFFFFFF)
    )


def write_png_rgb(path: Path, width: int, height: int, pixels: bytes) -> None:
    rows = bytearray()
    for y in range(height):
        rows.append(0)
        rows.extend(pixels[y * width * 3 : (y + 1) * width * 3])
    path.write_bytes(
        b"".join(
            [
                b"\x89PNG\r\n\x1a\n",
                png_chunk(b"IHDR", struct.pack(">IIBBBBB", width, height, 8, 2, 0, 0, 0)),
                png_chunk(b"IDAT", zlib.compress(bytes(rows), level=6)),
                png_chunk(b"IEND", b""),
            ]
        )
    )


def bgr555_to_rgb(value: int) -> tuple[int, int, int]:
    r = value & 0x1F
    g = (value >> 5) & 0x1F
    b = (value >> 10) & 0x1F
    return ((r << 3) | (r >> 2), (g << 3) | (g >> 2), (b << 3) | (b >> 2))


def read_palettes(path: Path) -> list[list[tuple[int, int, int]]]:
    data = path.read_bytes()
    colors = [
        bgr555_to_rgb(struct.unpack_from("<H", data, offset)[0])
        for offset in range(0, min(len(data), 0x200), 2)
    ]
    while len(colors) < 256:
        colors.append((0, 0, 0))
    return [colors[index * 16 : index * 16 + 16] for index in range(16)]


def render_tile_sheet(tile_data: bytes, palette: list[tuple[int, int, int]], columns: int) -> tuple[int, int, bytes]:
    usable = len(tile_data) - (len(tile_data) % TILE_BYTES_4BPP)
    tile_count = usable // TILE_BYTES_4BPP
    rows = max(1, math.ceil(tile_count / columns))
    width = columns * 8
    height = rows * 8
    pixels = bytearray(width * height * 3)

    for tile_index in range(tile_count):
        tile_x = (tile_index % columns) * 8
        tile_y = (tile_index // columns) * 8
        tile = tile_data[tile_index * TILE_BYTES_4BPP : tile_index * TILE_BYTES_4BPP + TILE_BYTES_4BPP]
        for y in range(8):
            row = tile[y * 4 : y * 4 + 4]
            for pair_index, byte in enumerate(row):
                for nibble_index, color_index in enumerate((byte & 0x0F, byte >> 4)):
                    x = tile_x + pair_index * 2 + nibble_index
                    out = ((tile_y + y) * width + x) * 3
                    pixels[out : out + 3] = bytes(palette[color_index])
    return width, height, bytes(pixels)


def is_blank_charblock(data: bytes) -> bool:
    return not data or all(byte == data[0] for byte in data)


def parse_palette_indexes(text: str) -> list[int]:
    if text == "all":
        return list(range(16))
    indexes = sorted({int(part, 0) for part in text.split(",") if part.strip()})
    for index in indexes:
        if index < 0 or index > 15:
            raise SystemExit(f"palette index out of range: {index}")
    return indexes


def frame_prefix_from_vram(path: Path) -> str:
    return path.name.removesuffix("_vram_06000000.bin")


def build_sheet_set(vram_path: Path, out_root: Path, *, columns: int, palette_indexes: list[int], include_blank: bool) -> list[dict]:
    prefix = frame_prefix_from_vram(vram_path)
    palette_path = vram_path.with_name(f"{prefix}_palette_05000000.bin")
    if not palette_path.exists():
        raise FileNotFoundError(f"missing palette dump for {vram_path}: {palette_path}")

    vram = vram_path.read_bytes()
    palettes = read_palettes(palette_path)
    frame_dir = out_root / prefix
    frame_dir.mkdir(parents=True, exist_ok=True)
    entries: list[dict] = []

    for charblock in range(len(vram) // CHARBLOCK_BYTES):
        start = charblock * CHARBLOCK_BYTES
        payload = vram[start : start + CHARBLOCK_BYTES]
        if not include_blank and is_blank_charblock(payload):
            continue
        for palette_index in palette_indexes:
            width, height, pixels = render_tile_sheet(payload, palettes[palette_index], columns)
            output = frame_dir / f"charblock_{charblock:02d}_palette_{palette_index:02d}.png"
            write_png_rgb(output, width, height, pixels)
            entries.append(
                {
                    "frame": prefix,
                    "charblock": charblock,
                    "vram_offset": start,
                    "palette": palette_index,
                    "tile_count": len(payload) // TILE_BYTES_4BPP,
                    "path": str(output.relative_to(ROOT)),
                }
            )
    return entries


def write_index(out_dir: Path, entries: list[dict]) -> None:
    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / "runtime_tile_sheets.json").write_text(
        json.dumps(entries, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    lines = ["# Runtime Tile Sheets", ""]
    current_frame = None
    for entry in entries:
        if entry["frame"] != current_frame:
            current_frame = entry["frame"]
            lines.extend(["", f"## `{current_frame}`", ""])
        lines.append(
            f"- charblock `{entry['charblock']}` palette `{entry['palette']}`: `{entry['path']}`"
        )
    (out_dir / "runtime_tile_sheets.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    args = parse_args()
    probe_dir = args.probe_dir.resolve()
    out_dir = args.out_dir.resolve()
    palette_indexes = parse_palette_indexes(args.palettes)

    vram_paths = sorted(probe_dir.glob("frame_*_vram_06000000.bin"))
    if not vram_paths:
        raise SystemExit(f"no runtime VRAM dumps found in {probe_dir}")

    entries: list[dict] = []
    for vram_path in vram_paths:
        entries.extend(
            build_sheet_set(
                vram_path,
                out_dir,
                columns=args.columns,
                palette_indexes=palette_indexes,
                include_blank=args.include_blank,
            )
        )
    write_index(out_dir, entries)
    print(f"frames: {len(vram_paths)}")
    print(f"sheets: {len(entries)}")
    print(f"index : {out_dir / 'runtime_tile_sheets.md'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
