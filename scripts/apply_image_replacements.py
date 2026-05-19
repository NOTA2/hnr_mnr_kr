#!/usr/bin/env python3
"""Apply uploaded image replacements to a review ROM.

The GUI only records which edited PNG the user uploaded. This script owns the
ROM-facing conversion: edited review PNG -> 4bpp tile payload -> compressed ROM
block. Initial support is intentionally focused on same-offset GBA RLE image
blocks, because those are the UI fragments currently exposed for editing.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT / ".vendor") not in sys.path:
    sys.path.insert(0, str(ROOT / ".vendor"))
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
if str(ROOT / "scripts") not in sys.path:
    sys.path.insert(0, str(ROOT / "scripts"))

from PIL import Image

from extract_rle_image_tiles import decompress_gba_rle
from render_runtime_tilemaps import read_palette


DEFAULT_ROM = ROOT / "patched_roms/current_review/hnr_localization_review.gba"
FALLBACK_ROM = ROOT / "patched_roms/current_review/hnr_localization_review_no_entry8_stable.gba"
DEFAULT_IMAGE_REPLACEMENTS = ROOT / "confirmed_data/localization_workbench/image_replacements.json"
DEFAULT_REPORT = ROOT / "confirmed_data/localization_workbench/image_apply_report.json"
TILE_BYTES = 32


OFFSET_RE = re.compile(r"(?:^|[:_])(?P<offset>[0-9A-Fa-f]{8})(?:$|[_:])")
COLS_RE = re.compile(r"_(?P<cols>\d+)cols(?:_|\\.)")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--rom", type=Path, default=DEFAULT_ROM)
    parser.add_argument("--image-replacements", type=Path, default=DEFAULT_IMAGE_REPLACEMENTS)
    parser.add_argument("--item-id", action="append", default=[], help="Optional image item id filter. May be repeated.")
    parser.add_argument("--report", type=Path, default=DEFAULT_REPORT)
    return parser.parse_args()


def compress_gba_rle(payload: bytes) -> bytes:
    if not (0 < len(payload) <= 0xFFFFFF):
        raise ValueError(f"invalid RLE payload size: {len(payload)}")
    # Dynamic programming avoids near-miss failures where a greedy encoder is a
    # few bytes larger than the game's original RLE block.
    n = len(payload)
    run_lengths = [1] * n
    for i in range(n - 2, -1, -1):
        if payload[i] == payload[i + 1]:
            run_lengths[i] = min(130, run_lengths[i + 1] + 1)

    inf = 1 << 60
    dp = [inf] * (n + 1)
    choices: list[tuple[str, int] | None] = [None] * n
    dp[n] = 0
    for i in range(n - 1, -1, -1):
        max_literal = min(128, n - i)
        for length in range(1, max_literal + 1):
            cost = 1 + length + dp[i + length]
            if cost < dp[i]:
                dp[i] = cost
                choices[i] = ("literal", length)
        max_run = min(130, run_lengths[i])
        for length in range(3, max_run + 1):
            cost = 2 + dp[i + length]
            if cost < dp[i]:
                dp[i] = cost
                choices[i] = ("run", length)

    out = bytearray([0x30, n & 0xFF, (n >> 8) & 0xFF, (n >> 16) & 0xFF])
    cursor = 0
    while cursor < n:
        choice = choices[cursor]
        if choice is None:
            raise ValueError("RLE compression failed to choose a packet")
        kind, length = choice
        if kind == "run":
            out.append(0x80 | (length - 3))
            out.append(payload[cursor])
        else:
            out.append(length - 1)
            out.extend(payload[cursor : cursor + length])
        cursor += length
    return bytes(out)


def rle_offset_from_item(item: dict) -> int | None:
    for value in (item.get("item_id", ""), item.get("group_id", "")):
        match = OFFSET_RE.search(str(value))
        if match:
            return int(match.group("offset"), 16)
    for subunit in item.get("subunits", []):
        for value in (subunit.get("id", ""), subunit.get("label", "")):
            match = OFFSET_RE.search(str(value))
            if match:
                return int(match.group("offset"), 16)
    return None


def columns_from_item(item: dict, tile_count: int) -> int:
    for field in ("tile_columns", "layout_columns"):
        value = item.get(field)
        if value not in ("", None):
            columns = int(value)
            if columns > 0:
                return min(columns, tile_count)
    paths = [
        item.get("source_preview_path", ""),
        item.get("source_download_path", ""),
        item.get("replacement_path", ""),
    ]
    for candidate in item.get("candidate_gallery", []):
        paths.extend([candidate.get("preview_path", ""), candidate.get("png_path", "")])
    for path in paths:
        match = COLS_RE.search(str(path))
        if match:
            return int(match.group("cols"))
    return min(32, max(1, tile_count))


def image_to_indices(path: Path, expected_w: int, expected_h: int) -> bytes:
    image = Image.open(path).convert("RGBA")
    if image.size != (expected_w, expected_h):
        if image.size[0] % expected_w or image.size[1] % expected_h:
            raise ValueError(
                f"{path} size {image.size} is not compatible with expected {expected_w}x{expected_h}"
            )
        image = image.resize((expected_w, expected_h), Image.Resampling.NEAREST)

    out = bytearray(expected_w * expected_h)
    pixels = image.load()
    for y in range(expected_h):
        for x in range(expected_w):
            r, g, b, a = pixels[x, y]
            if a == 0:
                value = 0
            else:
                value = round(((r + g + b) / 3) / 17)
            out[y * expected_w + x] = max(0, min(15, value))
    return bytes(out)


def indices_to_4bpp_tiles(indices: bytes, width: int, height: int, columns: int, tile_count: int) -> bytes:
    rows = height // 8
    payload = bytearray(tile_count * TILE_BYTES)
    for tile_index in range(tile_count):
        tile_x = (tile_index % columns) * 8
        tile_y = (tile_index // columns) * 8
        if tile_y + 8 > height:
            break
        base = tile_index * TILE_BYTES
        for y in range(8):
            for pair in range(4):
                x0 = tile_x + pair * 2
                lo = indices[(tile_y + y) * width + x0] & 0x0F
                hi = indices[(tile_y + y) * width + x0 + 1] & 0x0F
                payload[base + y * 4 + pair] = lo | (hi << 4)
    return bytes(payload)


def resize_replacement(path: Path, expected_w: int, expected_h: int) -> Image.Image:
    image = Image.open(path).convert("RGBA")
    if image.size != (expected_w, expected_h):
        if image.size[0] % expected_w or image.size[1] % expected_h:
            raise ValueError(
                f"{path} size {image.size} is not compatible with expected {expected_w}x{expected_h}"
            )
        image = image.resize((expected_w, expected_h), Image.Resampling.NEAREST)
    return image


def nearest_palette_nibble(rgb: tuple[int, int, int], palette: list[tuple[int, int, int]], palette_bank: int) -> int:
    start = palette_bank * 16
    choices = palette[start : start + 16]
    if not choices:
        return round(sum(rgb) / 3 / 17)
    best_index = 0
    best_score = 1 << 62
    for index, color in enumerate(choices):
        score = sum((rgb[channel] - color[channel]) ** 2 for channel in range(3))
        if score < best_score:
            best_score = score
            best_index = index
    return best_index & 0x0F


def rgba_to_nibble(
    rgba: tuple[int, int, int, int],
    *,
    palette: list[tuple[int, int, int]] | None = None,
    palette_bank: int = 0,
) -> int:
    r, g, b, a = rgba
    if a == 0:
        return 0
    if palette is None:
        return max(0, min(15, round(((r + g + b) / 3) / 17)))
    return nearest_palette_nibble((r, g, b), palette, palette_bank)


def tile_from_image(
    image: Image.Image,
    x0: int,
    y0: int,
    *,
    palette: list[tuple[int, int, int]] | None = None,
    palette_bank: int = 0,
    hflip: bool = False,
    vflip: bool = False,
) -> bytes:
    pixels = image.load()
    tile = bytearray(TILE_BYTES)
    for y in range(8):
        for pair in range(4):
            raw_x0 = pair * 2
            raw_x1 = raw_x0 + 1
            screen_x0 = 7 - raw_x0 if hflip else raw_x0
            screen_x1 = 7 - raw_x1 if hflip else raw_x1
            screen_y = 7 - y if vflip else y
            lo = rgba_to_nibble(pixels[x0 + screen_x0, y0 + screen_y], palette=palette, palette_bank=palette_bank)
            hi = rgba_to_nibble(pixels[x0 + screen_x1, y0 + screen_y], palette=palette, palette_bank=palette_bank)
            tile[y * 4 + pair] = lo | (hi << 4)
    return bytes(tile)


def load_tile_map(item: dict) -> dict | None:
    tile_map_path = item.get("tile_map_path", "")
    if not tile_map_path:
        return None
    path = (ROOT / tile_map_path).resolve()
    if not path.is_file() or ROOT not in path.parents:
        raise FileNotFoundError(f"tile_map_path not found: {tile_map_path}")
    return json.loads(path.read_text(encoding="utf-8"))


def palette_for_tile_map(tile_map: dict) -> list[tuple[int, int, int]] | None:
    palette_path = tile_map.get("runtime_palette_path", "")
    if not palette_path:
        return None
    path = (ROOT / palette_path).resolve()
    if not path.is_file() or ROOT not in path.parents:
        return None
    return read_palette(path.read_bytes())


def screen_order_image_to_rle_payload(path: Path, tile_map: dict, original_payload: bytes) -> bytes:
    crop = tile_map["crop_pixels"]
    expected_w = int(crop["width"])
    expected_h = int(crop["height"])
    image = resize_replacement(path, expected_w, expected_h)
    palette = palette_for_tile_map(tile_map)
    payload = bytearray(original_payload)
    min_x = int(tile_map["crop_screen_tiles"]["min_x"])
    min_y = int(tile_map["crop_screen_tiles"]["min_y"])
    written: set[int] = set()
    for match in tile_map.get("matches", []):
        rel_x = (int(match["screen_tile_x"]) - min_x) * 8
        rel_y = (int(match["screen_tile_y"]) - min_y) * 8
        palette_bank = int(match.get("palette_bank", 0))
        tile = tile_from_image(
            image,
            rel_x,
            rel_y,
            palette=palette,
            palette_bank=palette_bank,
            hflip=bool(match.get("hflip")),
            vflip=bool(match.get("vflip")),
        )
        for rle_tile_index in match.get("rle_tile_indexes", []):
            tile_index = int(rle_tile_index)
            if tile_index in written:
                continue
            start = tile_index * TILE_BYTES
            if start + TILE_BYTES <= len(payload):
                payload[start : start + TILE_BYTES] = tile
                written.add(tile_index)
    if not written:
        raise ValueError("tile_map did not map any replacement tiles")
    return bytes(payload)


def apply_rle_item(rom: bytearray, item: dict) -> dict:
    replacement = item.get("replacement_path", "")
    if not replacement:
        return {"item_id": item["item_id"], "status": "skipped", "reason": "no replacement_path"}
    replacement_path = (ROOT / replacement).resolve()
    if not replacement_path.is_file() or ROOT not in replacement_path.parents:
        return {"item_id": item["item_id"], "status": "error", "reason": "replacement file not found"}

    offset = rle_offset_from_item(item)
    if offset is None:
        return {"item_id": item["item_id"], "status": "skipped", "reason": "no RLE offset"}
    current = decompress_gba_rle(bytes(rom), offset, max_output_size=0x400000)
    if not current:
        return {"item_id": item["item_id"], "status": "error", "reason": "target is not a GBA RLE block"}
    original_payload, original_consumed = current
    if len(original_payload) % TILE_BYTES:
        return {"item_id": item["item_id"], "status": "error", "reason": "RLE payload is not 4bpp tile aligned"}

    tile_count = len(original_payload) // TILE_BYTES
    tile_map = load_tile_map(item)
    columns = None
    if tile_map:
        payload = screen_order_image_to_rle_payload(replacement_path, tile_map, original_payload)
    else:
        columns = columns_from_item(item, tile_count)
        rows = (tile_count + columns - 1) // columns
        width = columns * 8
        height = rows * 8
        indices = image_to_indices(replacement_path, width, height)
        payload = indices_to_4bpp_tiles(indices, width, height, columns, tile_count)
    compressed = compress_gba_rle(payload)
    if len(compressed) > original_consumed:
        return {
            "item_id": item["item_id"],
            "status": "error",
            "reason": f"compressed replacement too large: {len(compressed)} > {original_consumed}",
            "offset_hex": f"0x{offset:08X}",
        }

    rom[offset : offset + len(compressed)] = compressed
    if len(compressed) < original_consumed:
        rom[offset + len(compressed) : offset + original_consumed] = b"\x00" * (original_consumed - len(compressed))
    verify = decompress_gba_rle(bytes(rom), offset, max_output_size=0x400000)
    if not verify or verify[0] != payload:
        return {"item_id": item["item_id"], "status": "error", "reason": "verification failed"}
    return {
        "item_id": item["item_id"],
        "status": "applied",
        "offset": offset,
        "offset_hex": f"0x{offset:08X}",
        "columns": columns,
        "tile_map_path": item.get("tile_map_path", ""),
        "decompressed_size": len(payload),
        "compressed_size": len(compressed),
        "available_size": original_consumed,
    }


def main() -> int:
    args = parse_args()
    rom_path = args.rom.resolve()
    if not rom_path.exists() and args.rom == DEFAULT_ROM and FALLBACK_ROM.exists():
        rom_path = FALLBACK_ROM.resolve()
    items = json.loads(args.image_replacements.resolve().read_text(encoding="utf-8"))
    filters = set(args.item_id)
    rom = bytearray(rom_path.read_bytes())
    results = []
    for item in items:
        if filters and item["item_id"] not in filters:
            continue
        if item.get("replacement_target") is False:
            continue
        offset = rle_offset_from_item(item)
        if offset is None or not item.get("replacement_path"):
            continue
        try:
            results.append(apply_rle_item(rom, item))
        except Exception as exc:
            results.append(
                {
                    "item_id": item["item_id"],
                    "status": "error",
                    "reason": str(exc),
                }
            )

    applied = [item for item in results if item["status"] == "applied"]
    if applied:
        rom_path.write_bytes(rom)

    report = {
        "rom": str(rom_path.relative_to(ROOT) if rom_path.is_relative_to(ROOT) else rom_path),
        "applied_count": len(applied),
        "results": results,
    }
    args.report.resolve().parent.mkdir(parents=True, exist_ok=True)
    args.report.resolve().write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, ensure_ascii=False, indent=2))
    if any(item["status"] == "error" for item in results):
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
