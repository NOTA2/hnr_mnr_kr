#!/usr/bin/env python3
"""Render GBA runtime BG tilemaps and OBJ sprites from pymgba dumps.

Raw tile previews are useful for finding compressed graphics blocks, but many
UI assets only become readable when the runtime screenblock/OAM placement is
applied. This script uses the dumped IO registers, VRAM, palette, and OAM to
make per-BG viewport/full-map previews plus a simple OBJ preview.
"""

from __future__ import annotations

import argparse
import binascii
import json
import math
import struct
import zlib
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_PROBE_DIR = ROOT / "confirmed_data/image_inventory/runtime_user_captures/no_entry8_latest_ss1"
DEFAULT_OUT_DIR = ROOT / "confirmed_data/image_inventory/runtime_tilemaps"
SCREEN_W = 240
SCREEN_H = 160
TILE_BYTES_4BPP = 32
TILE_BYTES_8BPP = 64


OBJ_SIZE_TABLE = {
    0: [(8, 8), (16, 16), (32, 32), (64, 64)],
    1: [(16, 8), (32, 8), (32, 16), (64, 32)],
    2: [(8, 16), (8, 32), (16, 32), (32, 64)],
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--probe-dir", type=Path, default=DEFAULT_PROBE_DIR)
    parser.add_argument("--out-dir", type=Path, default=DEFAULT_OUT_DIR)
    return parser.parse_args()


def png_chunk(kind: bytes, payload: bytes) -> bytes:
    return (
        struct.pack(">I", len(payload))
        + kind
        + payload
        + struct.pack(">I", binascii.crc32(kind + payload) & 0xFFFFFFFF)
    )


def write_png_rgb(path: Path, width: int, height: int, pixels: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
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


def read_palette(data: bytes, *, obj: bool = False) -> list[tuple[int, int, int]]:
    base = 0x200 if obj else 0
    colors = []
    for offset in range(base, base + 0x200, 2):
        colors.append(bgr555_to_rgb(struct.unpack_from("<H", data, offset)[0]))
    return colors


def render_tile_4bpp(vram: bytes, tile_addr: int, palette: list[tuple[int, int, int]], palette_bank: int) -> list[int]:
    out = [0] * 64
    if tile_addr < 0 or tile_addr + TILE_BYTES_4BPP > len(vram):
        return out
    for y in range(8):
        row = vram[tile_addr + y * 4 : tile_addr + y * 4 + 4]
        for pair_index, byte in enumerate(row):
            indexes = (byte & 0x0F, byte >> 4)
            for nibble_index, color_index in enumerate(indexes):
                x = pair_index * 2 + nibble_index
                if color_index:
                    out[y * 8 + x] = palette_bank * 16 + color_index
    return out


def render_tile_8bpp(vram: bytes, tile_addr: int) -> list[int]:
    if tile_addr < 0 or tile_addr + TILE_BYTES_8BPP > len(vram):
        return [0] * 64
    return list(vram[tile_addr : tile_addr + TILE_BYTES_8BPP])


def bg_size_pixels(size: int) -> tuple[int, int]:
    return [(256, 256), (512, 256), (256, 512), (512, 512)][size]


def screen_entry_offset(screen_base: int, x_tile: int, y_tile: int, size: int) -> int:
    block = screen_base
    local_x = x_tile
    local_y = y_tile
    if size == 1 and x_tile >= 32:
        block += 1
        local_x -= 32
    elif size == 2 and y_tile >= 32:
        block += 1
        local_y -= 32
    elif size == 3:
        if x_tile >= 32:
            block += 1
            local_x -= 32
        if y_tile >= 32:
            block += 2
            local_y -= 32
    return block * 0x800 + (local_y * 32 + local_x) * 2


def render_bg_map(vram: bytes, palette: list[tuple[int, int, int]], bgcnt: int) -> tuple[int, int, bytearray]:
    char_base = ((bgcnt >> 2) & 0x3) * 0x4000
    is_8bpp = bool(bgcnt & 0x80)
    screen_base = (bgcnt >> 8) & 0x1F
    size = (bgcnt >> 14) & 0x3
    width, height = bg_size_pixels(size)
    pixels = bytearray([16, 18, 20] * width * height)
    tiles_x = width // 8
    tiles_y = height // 8

    for ty in range(tiles_y):
        for tx in range(tiles_x):
            entry_addr = screen_entry_offset(screen_base, tx, ty, size)
            if entry_addr + 2 > len(vram):
                continue
            entry = struct.unpack_from("<H", vram, entry_addr)[0]
            tile_index = entry & 0x3FF
            hflip = bool(entry & 0x400)
            vflip = bool(entry & 0x800)
            palette_bank = (entry >> 12) & 0xF
            if is_8bpp:
                tile_pixels = render_tile_8bpp(vram, char_base + tile_index * TILE_BYTES_8BPP)
            else:
                tile_pixels = render_tile_4bpp(vram, char_base + tile_index * TILE_BYTES_4BPP, palette, palette_bank)
            for py in range(8):
                sy = 7 - py if vflip else py
                for px in range(8):
                    sx = 7 - px if hflip else px
                    color_index = tile_pixels[sy * 8 + sx]
                    if not color_index:
                        continue
                    rgb = palette[color_index % len(palette)]
                    out = ((ty * 8 + py) * width + (tx * 8 + px)) * 3
                    pixels[out : out + 3] = bytes(rgb)
    return width, height, pixels


def crop_viewport(map_pixels: bytearray, map_w: int, map_h: int, scroll_x: int, scroll_y: int) -> bytes:
    out = bytearray([16, 18, 20] * SCREEN_W * SCREEN_H)
    for y in range(SCREEN_H):
        sy = (scroll_y + y) % map_h
        for x in range(SCREEN_W):
            sx = (scroll_x + x) % map_w
            src = (sy * map_w + sx) * 3
            dst = (y * SCREEN_W + x) * 3
            out[dst : dst + 3] = map_pixels[src : src + 3]
    return bytes(out)


def blend_layer(base: bytearray, layer: bytes) -> None:
    for pos in range(0, len(layer), 3):
        if layer[pos : pos + 3] != bytes([16, 18, 20]):
            base[pos : pos + 3] = layer[pos : pos + 3]


def render_obj_preview(vram: bytes, obj_palette: list[tuple[int, int, int]], oam: list[dict], dispcnt: int) -> bytes:
    one_dimensional = bool(dispcnt & 0x40)
    pixels = bytearray([16, 18, 20] * SCREEN_W * SCREEN_H)
    obj_base = 0x10000
    for obj in sorted(oam, key=lambda item: ((item["attr2"] >> 10) & 0x3), reverse=True):
        attr0 = int(obj["attr0"])
        attr1 = int(obj["attr1"])
        attr2 = int(obj["attr2"])
        mode = (attr0 >> 8) & 0x3
        if mode == 2:
            continue
        color_8bpp = bool(attr0 & 0x2000)
        shape = (attr0 >> 14) & 0x3
        size = (attr1 >> 14) & 0x3
        if shape not in OBJ_SIZE_TABLE:
            continue
        width, height = OBJ_SIZE_TABLE[shape][size]
        x0 = attr1 & 0x1FF
        y0 = attr0 & 0xFF
        if x0 >= 256:
            x0 -= 512
        if y0 >= 160:
            y0 -= 256
        hflip = bool(attr1 & 0x1000)
        vflip = bool(attr1 & 0x2000)
        tile_index = attr2 & 0x3FF
        palette_bank = (attr2 >> 12) & 0xF
        tiles_per_row = width // 8
        tiles_per_col = height // 8
        for ty in range(tiles_per_col):
            for tx in range(tiles_per_row):
                if one_dimensional:
                    current_tile = tile_index + ty * tiles_per_row + tx
                else:
                    current_tile = tile_index + ty * 32 + tx
                if color_8bpp:
                    tile_pixels = render_tile_8bpp(vram, obj_base + current_tile * TILE_BYTES_8BPP)
                else:
                    tile_pixels = render_tile_4bpp(vram, obj_base + current_tile * TILE_BYTES_4BPP, obj_palette, palette_bank)
                for py in range(8):
                    sy = 7 - py if vflip else py
                    for px in range(8):
                        sx = 7 - px if hflip else px
                        color_index = tile_pixels[sy * 8 + sx]
                        if not color_index:
                            continue
                        x = x0 + tx * 8 + px
                        y = y0 + ty * 8 + py
                        if not (0 <= x < SCREEN_W and 0 <= y < SCREEN_H):
                            continue
                        rgb = obj_palette[color_index % len(obj_palette)]
                        out = (y * SCREEN_W + x) * 3
                        pixels[out : out + 3] = bytes(rgb)
    return bytes(pixels)


def frame_prefix_from_vram(path: Path) -> str:
    return path.name.removesuffix("_vram_06000000.bin")


def render_probe_dir(probe_dir: Path, out_dir: Path) -> list[dict]:
    entries: list[dict] = []
    for vram_path in sorted(probe_dir.glob("frame_*_vram_06000000.bin")):
        frame = frame_prefix_from_vram(vram_path)
        palette_path = vram_path.with_name(f"{frame}_palette_05000000.bin")
        ioreg_path = vram_path.with_name(f"{frame}_ioreg_04000000.bin")
        oam_path = vram_path.with_name(f"{frame}_oam_07000000.json")
        if not palette_path.exists() or not ioreg_path.exists():
            continue
        vram = vram_path.read_bytes()
        palette_data = palette_path.read_bytes()
        bg_palette = read_palette(palette_data)
        obj_palette = read_palette(palette_data, obj=True)
        ioreg = ioreg_path.read_bytes()
        dispcnt = struct.unpack_from("<H", ioreg, 0)[0]
        mode = dispcnt & 0x7
        frame_dir = out_dir / frame
        frame_dir.mkdir(parents=True, exist_ok=True)
        composite = bytearray([16, 18, 20] * SCREEN_W * SCREEN_H)

        for bg in range(4):
            if not (dispcnt & (1 << (8 + bg))):
                continue
            if mode > 1 and bg < 2:
                # Bitmap/affine modes need different handling. Current probes
                # are mode 0, but keep this guard explicit.
                continue
            bgcnt = struct.unpack_from("<H", ioreg, 0x8 + bg * 2)[0]
            scroll_x = struct.unpack_from("<H", ioreg, 0x10 + bg * 4)[0] & 0x1FF
            scroll_y = struct.unpack_from("<H", ioreg, 0x12 + bg * 4)[0] & 0x1FF
            map_w, map_h, map_pixels = render_bg_map(vram, bg_palette, bgcnt)
            full_path = frame_dir / f"bg{bg}_full.png"
            view_path = frame_dir / f"bg{bg}_viewport.png"
            viewport = crop_viewport(map_pixels, map_w, map_h, scroll_x, scroll_y)
            write_png_rgb(full_path, map_w, map_h, bytes(map_pixels))
            write_png_rgb(view_path, SCREEN_W, SCREEN_H, viewport)
            blend_layer(composite, viewport)
            entries.append(
                {
                    "frame": frame,
                    "layer": f"bg{bg}",
                    "mode": mode,
                    "bgcnt": bgcnt,
                    "char_base": (bgcnt >> 2) & 0x3,
                    "screen_base": (bgcnt >> 8) & 0x1F,
                    "size": (bgcnt >> 14) & 0x3,
                    "scroll_x": scroll_x,
                    "scroll_y": scroll_y,
                    "full_path": str(full_path.relative_to(ROOT)),
                    "viewport_path": str(view_path.relative_to(ROOT)),
                }
            )

        if oam_path.exists():
            oam = json.loads(oam_path.read_text(encoding="utf-8"))
            obj_pixels = render_obj_preview(vram, obj_palette, oam, dispcnt)
            obj_path = frame_dir / "obj_sprites.png"
            write_png_rgb(obj_path, SCREEN_W, SCREEN_H, obj_pixels)
            blend_layer(composite, obj_pixels)
            entries.append(
                {
                    "frame": frame,
                    "layer": "obj",
                    "path": str(obj_path.relative_to(ROOT)),
                }
            )

        composite_path = frame_dir / "composite_layers.png"
        write_png_rgb(composite_path, SCREEN_W, SCREEN_H, bytes(composite))
        entries.append(
            {
                "frame": frame,
                "layer": "composite",
                "path": str(composite_path.relative_to(ROOT)),
            }
        )
    return entries


def main() -> int:
    args = parse_args()
    probe_dir = args.probe_dir.resolve()
    scene_name = probe_dir.name
    out_dir = (args.out_dir / scene_name).resolve()
    entries = render_probe_dir(probe_dir, out_dir)
    (out_dir / "runtime_tilemaps.json").write_text(
        json.dumps(entries, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    print(f"entries: {len(entries)}")
    print(f"out    : {out_dir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
