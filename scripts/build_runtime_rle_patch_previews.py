#!/usr/bin/env python3
"""Build human-readable screen-order previews for runtime-matched RLE tiles.

Raw RLE tile sheets are often unreadable because the game reorders tiles through
BG screenblocks. This tool uses a pymgba runtime dump to place only the tiles
that also exist in a selected RLE block back into their on-screen positions.
The result is a practical review/edit reference plus a JSON tile map.
"""

from __future__ import annotations

import argparse
import json
import struct
from pathlib import Path

from render_runtime_tilemaps import (
    SCREEN_H,
    SCREEN_W,
    TILE_BYTES_4BPP,
    bgr555_to_rgb,
    bg_size_pixels,
    crop_viewport,
    read_palette,
    render_bg_map,
    render_tile_4bpp,
    screen_entry_offset,
    write_png_rgb,
)


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_PROBE_DIR = ROOT / "confirmed_data/image_inventory/runtime_user_captures/no_entry8_latest_ss1"
DEFAULT_RLE_REPORT = ROOT / "confirmed_data/image_inventory/rle_tile_extraction/notes/rle_tile_extraction_report.json"
DEFAULT_OUT_DIR = ROOT / "confirmed_data/image_inventory/runtime_rle_patch_previews"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--probe-dir", type=Path, default=DEFAULT_PROBE_DIR)
    parser.add_argument("--frame", default="")
    parser.add_argument("--bg", type=int, default=0)
    parser.add_argument("--rle-offset", type=lambda value: int(value, 0), required=True)
    parser.add_argument("--rle-report", type=Path, default=DEFAULT_RLE_REPORT)
    parser.add_argument("--out-dir", type=Path, default=DEFAULT_OUT_DIR)
    parser.add_argument("--padding-tiles", type=int, default=1)
    return parser.parse_args()


def is_blank_tile(tile: bytes) -> bool:
    return not tile or all(byte == tile[0] for byte in tile)


def frame_prefix(probe_dir: Path, requested: str) -> str:
    if requested:
        return requested
    matches = sorted(probe_dir.glob("frame_*_vram_06000000.bin"))
    if not matches:
        raise FileNotFoundError(f"no VRAM dump found in {probe_dir}")
    return matches[0].name.removesuffix("_vram_06000000.bin")


def find_rle_block(report_path: Path, offset: int) -> dict:
    report = json.loads(report_path.read_text(encoding="utf-8"))
    for block in report.get("blocks", []):
        if int(block["offset"]) == offset:
            return block
    raise KeyError(f"RLE offset not found in report: 0x{offset:08X}")


def read_bg_control(ioreg: bytes, bg: int) -> dict:
    bgcnt = struct.unpack_from("<H", ioreg, 0x8 + bg * 2)[0]
    return {
        "bg": bg,
        "bgcnt": bgcnt,
        "char_base": ((bgcnt >> 2) & 0x3) * 0x4000,
        "screen_base": (bgcnt >> 8) & 0x1F,
        "is_8bpp": bool(bgcnt & 0x80),
        "size": (bgcnt >> 14) & 0x3,
        "scroll_x": struct.unpack_from("<H", ioreg, 0x10 + bg * 4)[0] & 0x1FF,
        "scroll_y": struct.unpack_from("<H", ioreg, 0x12 + bg * 4)[0] & 0x1FF,
    }


def rle_tile_index(raw: bytes) -> dict[bytes, list[int]]:
    index: dict[bytes, list[int]] = {}
    usable = len(raw) - (len(raw) % TILE_BYTES_4BPP)
    for tile_index, start in enumerate(range(0, usable, TILE_BYTES_4BPP)):
        tile = raw[start : start + TILE_BYTES_4BPP]
        if is_blank_tile(tile):
            continue
        index.setdefault(tile, []).append(tile_index)
    return index


def runtime_matches(vram: bytes, control: dict, index: dict[bytes, list[int]]) -> list[dict]:
    matches: list[dict] = []
    map_w, map_h = bg_size_pixels(control["size"])
    map_tiles_w = map_w // 8
    map_tiles_h = map_h // 8
    visible_tiles_w = (SCREEN_W + (control["scroll_x"] % 8) + 7) // 8
    visible_tiles_h = (SCREEN_H + (control["scroll_y"] % 8) + 7) // 8
    for screen_y in range(visible_tiles_h):
        map_y = ((control["scroll_y"] // 8) + screen_y) % map_tiles_h
        for screen_x in range(visible_tiles_w):
            map_x = ((control["scroll_x"] // 8) + screen_x) % map_tiles_w
            entry_addr = screen_entry_offset(control["screen_base"], map_x, map_y, control["size"])
            entry = struct.unpack_from("<H", vram, entry_addr)[0]
            tile_index = entry & 0x3FF
            hflip = bool(entry & 0x400)
            vflip = bool(entry & 0x800)
            palette_bank = (entry >> 12) & 0xF
            if control["is_8bpp"]:
                continue
            tile_addr = control["char_base"] + tile_index * TILE_BYTES_4BPP
            tile = vram[tile_addr : tile_addr + TILE_BYTES_4BPP]
            if is_blank_tile(tile) or tile not in index:
                continue
            matches.append(
                {
                    "screen_tile_x": screen_x,
                    "screen_tile_y": screen_y,
                    "map_tile_x": map_x,
                    "map_tile_y": map_y,
                    "runtime_tile_index": tile_index,
                    "hflip": hflip,
                    "vflip": vflip,
                    "palette_bank": palette_bank,
                    "screen_entry": entry,
                    "rle_tile_indexes": index[tile],
                }
            )
    return matches


def bounds(matches: list[dict], padding: int) -> tuple[int, int, int, int]:
    min_x = max(0, min(item["screen_tile_x"] for item in matches) - padding)
    min_y = max(0, min(item["screen_tile_y"] for item in matches) - padding)
    max_x = max(item["screen_tile_x"] for item in matches) + padding
    max_y = max(item["screen_tile_y"] for item in matches) + padding
    return min_x, min_y, max_x, max_y


def alignment_adjustment(control: dict) -> tuple[int, int]:
    adjustment = control.get("alignment_adjustment_pixels") or {}
    return int(adjustment.get("x", 0)), int(adjustment.get("y", 0))


def tile_screen_origin(match: dict, control: dict) -> tuple[int, int]:
    shift_x, shift_y = alignment_adjustment(control)
    return (
        int(match["screen_tile_x"]) * 8 - (int(control.get("scroll_x", 0)) % 8) + shift_x,
        int(match["screen_tile_y"]) * 8 - (int(control.get("scroll_y", 0)) % 8) + shift_y,
    )


def crop_pixels_for_matches(
    matches: list[dict],
    control: dict,
    crop_box: tuple[int, int, int, int],
) -> tuple[int, int, int, int]:
    min_x, min_y, max_x, max_y = crop_box
    fine_x = int(control.get("scroll_x", 0)) % 8
    fine_y = int(control.get("scroll_y", 0)) % 8
    left = max(0, min_x * 8 - fine_x)
    top = max(0, min_y * 8 - fine_y)
    right = min(SCREEN_W, (max_x + 1) * 8 - fine_x)
    bottom = min(SCREEN_H, (max_y + 1) * 8 - fine_y)
    if right <= left or bottom <= top:
        raise ValueError("matched tile crop is outside the visible screen")
    return left, top, right - left, bottom - top


def draw_border_rgb(pixels: bytearray, width: int, height: int, x: int, y: int, w: int, h: int, color: tuple[int, int, int]) -> None:
    def put(px: int, py: int) -> None:
        if 0 <= px < width and 0 <= py < height:
            pos = (py * width + px) * 3
            pixels[pos : pos + 3] = bytes(color)

    for px in range(x, x + w):
        put(px, y)
        put(px, y + h - 1)
    for py in range(y, y + h):
        put(x, py)
        put(x + w - 1, py)


def crop_rgb(src: bytes | bytearray, src_w: int, x: int, y: int, w: int, h: int) -> bytes:
    out = bytearray(w * h * 3)
    for row in range(h):
        src_pos = ((y + row) * src_w + x) * 3
        dst_pos = row * w * 3
        out[dst_pos : dst_pos + w * 3] = src[src_pos : src_pos + w * 3]
    return bytes(out)


def scale_rgb(src: bytes | bytearray, width: int, height: int, factor: int) -> tuple[int, int, bytes]:
    out_w = width * factor
    out_h = height * factor
    out = bytearray(out_w * out_h * 3)
    for y in range(out_h):
        sy = y // factor
        for x in range(out_w):
            sx = x // factor
            src_pos = (sy * width + sx) * 3
            dst_pos = (y * out_w + x) * 3
            out[dst_pos : dst_pos + 3] = src[src_pos : src_pos + 3]
    return out_w, out_h, bytes(out)


def build_match_only_view(
    vram: bytes,
    palette: list[tuple[int, int, int]],
    control: dict,
    matches: list[dict],
    crop_box: tuple[int, int, int, int],
    crop_px: tuple[int, int, int, int] | None = None,
    *,
    draw_grid: bool = False,
) -> bytes:
    min_x, min_y, max_x, max_y = crop_box
    if crop_px is None:
        crop_px = crop_pixels_for_matches(matches, control, crop_box)
    crop_x, crop_y, out_w, out_h = crop_px
    pixels = bytearray([35, 35, 40] * out_w * out_h)
    by_pos = {(item["screen_tile_x"], item["screen_tile_y"]): item for item in matches}
    for screen_y in range(min_y, max_y + 1):
        for screen_x in range(min_x, max_x + 1):
            match = by_pos.get((screen_x, screen_y))
            if not match:
                continue
            tile = render_tile_4bpp(
                vram,
                control["char_base"] + match["runtime_tile_index"] * TILE_BYTES_4BPP,
                palette,
                match["palette_bank"],
            )
            origin_x, origin_y = tile_screen_origin(match, control)
            dst_x = origin_x - crop_x
            dst_y = origin_y - crop_y
            for py in range(8):
                out_y = dst_y + py
                if not (0 <= out_y < out_h):
                    continue
                for px in range(8):
                    out_x = dst_x + px
                    if not (0 <= out_x < out_w):
                        continue
                    sx = 7 - px if match.get("hflip") else px
                    sy = 7 - py if match.get("vflip") else py
                    color_index = tile[sy * 8 + sx]
                    if not color_index:
                        continue
                    rgb = palette[color_index % len(palette)]
                    pos = (out_y * out_w + out_x) * 3
                    pixels[pos : pos + 3] = bytes(rgb)
            if draw_grid:
                draw_border_rgb(pixels, out_w, out_h, dst_x, dst_y, 8, 8, (68, 160, 255))
    return bytes(pixels)


def write_summary(out_dir: Path, payload: dict) -> None:
    (out_dir / "tile_map.json").write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    lines = [
        "# Runtime RLE Patch Preview",
        "",
        f"- scene: `{payload['scene']}`",
        f"- frame: `{payload['frame']}`",
        f"- BG: `{payload['bg']}`",
        f"- RLE: `{payload['rle_offset_hex']}`",
        f"- matched screen tiles: `{payload['matched_tile_count']}`",
        "",
        "## Files",
        "",
        "- `context_crop.png`: 실제 BG 화면 배치 crop",
        "- `context_crop_grid.png`: 실제 BG 화면 배치 crop + RLE 매칭 타일 격자",
        "- `context_crop_4x.png`: 사람이 보기 좋은 4배 확대본",
        "- `matched_tiles_screen_order.png`: 해당 RLE에서 온 타일만 화면 순서대로 재조립",
        "- `matched_tiles_screen_order_grid.png`: 화면 순서 재조립 + 타일 격자",
        "- `matched_tiles_screen_order_4x.png`: 사람이 보기 좋은 4배 확대본",
        "- `tile_map.json`: 화면 타일 좌표와 RLE 원본 타일 index 매핑",
    ]
    (out_dir / "README.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    args = parse_args()
    probe_dir = args.probe_dir.resolve()
    frame = frame_prefix(probe_dir, args.frame)
    vram = (probe_dir / f"{frame}_vram_06000000.bin").read_bytes()
    ioreg = (probe_dir / f"{frame}_ioreg_04000000.bin").read_bytes()
    palette_data = (probe_dir / f"{frame}_palette_05000000.bin").read_bytes()
    palette = read_palette(palette_data)
    control = read_bg_control(ioreg, args.bg)
    if control["is_8bpp"]:
        raise ValueError("8bpp BG layers are not supported by this preview helper yet")

    rle_block = find_rle_block(args.rle_report.resolve(), args.rle_offset)
    rle_raw = (ROOT / rle_block["raw_path"]).read_bytes()
    matches = runtime_matches(vram, control, rle_tile_index(rle_raw))
    if not matches:
        raise ValueError(f"no runtime tiles matched RLE 0x{args.rle_offset:08X}")

    crop_box = bounds(matches, args.padding_tiles)
    min_x, min_y, max_x, max_y = crop_box
    crop_px = crop_pixels_for_matches(matches, control, crop_box)

    map_w, map_h, bg_pixels = render_bg_map(vram, palette, control["bgcnt"])
    viewport = crop_viewport(bg_pixels, map_w, map_h, control["scroll_x"], control["scroll_y"])
    context_plain = crop_rgb(viewport, SCREEN_W, *crop_px)
    context = bytearray(context_plain)
    for item in matches:
        if min_x <= item["screen_tile_x"] <= max_x and min_y <= item["screen_tile_y"] <= max_y:
            origin_x, origin_y = tile_screen_origin(item, control)
            draw_border_rgb(
                context,
                crop_px[2],
                crop_px[3],
                origin_x - crop_px[0],
                origin_y - crop_px[1],
                8,
                8,
                (255, 64, 64),
            )

    out_dir = args.out_dir.resolve() / f"{probe_dir.name}_{frame}_bg{args.bg}_rle_{args.rle_offset:08X}"
    out_dir.mkdir(parents=True, exist_ok=True)
    write_png_rgb(out_dir / "context_crop.png", crop_px[2], crop_px[3], context_plain)
    write_png_rgb(out_dir / "context_crop_grid.png", crop_px[2], crop_px[3], bytes(context))
    write_png_rgb(out_dir / "context_crop_4x.png", *scale_rgb(context_plain, crop_px[2], crop_px[3], 4))
    matched_plain = build_match_only_view(vram, palette, control, matches, crop_box, crop_px)
    matched_grid = build_match_only_view(vram, palette, control, matches, crop_box, crop_px, draw_grid=True)
    write_png_rgb(out_dir / "matched_tiles_screen_order.png", crop_px[2], crop_px[3], matched_plain)
    write_png_rgb(out_dir / "matched_tiles_screen_order_grid.png", crop_px[2], crop_px[3], matched_grid)
    write_png_rgb(out_dir / "matched_tiles_screen_order_4x.png", *scale_rgb(matched_plain, crop_px[2], crop_px[3], 4))

    payload = {
        "scene": probe_dir.name,
        "frame": frame,
        "bg": args.bg,
        "rle_offset": args.rle_offset,
        "rle_offset_hex": f"0x{args.rle_offset:08X}",
        "rle_raw_path": rle_block["raw_path"],
        "crop_screen_tiles": {
            "min_x": min_x,
            "min_y": min_y,
            "max_x": max_x,
            "max_y": max_y,
        },
        "crop_pixels": {
            "x": crop_px[0],
            "y": crop_px[1],
            "width": crop_px[2],
            "height": crop_px[3],
        },
        "scroll_pixels": {
            "x": int(control["scroll_x"]),
            "y": int(control["scroll_y"]),
        },
        "fine_scroll_pixels": {
            "x": int(control["scroll_x"]) % 8,
            "y": int(control["scroll_y"]) % 8,
        },
        "alignment_adjustment_pixels": {
            "x": alignment_adjustment(control)[0],
            "y": alignment_adjustment(control)[1],
        },
        "matched_tile_count": len(matches),
        "matches": matches,
    }
    write_summary(out_dir, payload)
    print(f"matched tiles: {len(matches)}")
    print(f"out: {out_dir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
