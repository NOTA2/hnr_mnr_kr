#!/usr/bin/env python3
"""Render Korean HUD text from the Galmuri7 9x9-cell atlas as 8x8 glyph tiles."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT / ".vendor") not in sys.path:
    sys.path.insert(0, str(ROOT / ".vendor"))

from PIL import Image


HANGUL_BASE = 0xAC00
HANGUL_COUNT = 11172
DEFAULT_ATLAS = ROOT / "third_party" / "font_atlases" / "finalists" / "Galmuri7_9x9.png"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("text")
    parser.add_argument("--atlas", type=Path, default=DEFAULT_ATLAS)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--width", type=int, help="fixed output width in pixels; text is centered")
    parser.add_argument("--scale", type=int, default=4)
    parser.add_argument("--cell-size", type=int, default=9)
    parser.add_argument("--glyph-size", type=int, default=8)
    parser.add_argument("--columns", type=int, default=64)
    return parser.parse_args()


def glyph_from_atlas(atlas: Image.Image, char: str, *, cell_size: int, glyph_size: int, columns: int) -> Image.Image:
    if char == " ":
        return Image.new("RGBA", (glyph_size, glyph_size), (0, 0, 0, 255))
    codepoint = ord(char)
    tile_index = codepoint - HANGUL_BASE
    if tile_index < 0 or tile_index >= HANGUL_COUNT:
        raise SystemExit(f"error: unsupported non-Hangul HUD glyph: {char!r} U+{codepoint:04X}")
    x = (tile_index % columns) * cell_size
    y = (tile_index // columns) * cell_size
    return atlas.crop((x, y, x + glyph_size, y + glyph_size))


def render_text(
    text: str,
    *,
    atlas: Image.Image,
    width: int | None,
    cell_size: int,
    glyph_size: int,
    columns: int,
) -> Image.Image:
    text_width = len(text) * glyph_size
    out_width = width or text_width
    if text_width > out_width:
        raise SystemExit(f"error: text is wider than output: {text_width}px > {out_width}px")
    image = Image.new("RGBA", (out_width, glyph_size), (0, 0, 0, 255))
    x = (out_width - text_width) // 2
    for char in text:
        image.alpha_composite(
            glyph_from_atlas(atlas, char, cell_size=cell_size, glyph_size=glyph_size, columns=columns),
            (x, 0),
        )
        x += glyph_size
    return image


def main() -> int:
    args = parse_args()
    atlas_path = args.atlas if args.atlas.is_absolute() else ROOT / args.atlas
    atlas = Image.open(atlas_path).convert("RGBA")
    image = render_text(
        args.text,
        atlas=atlas,
        width=args.width,
        cell_size=args.cell_size,
        glyph_size=args.glyph_size,
        columns=args.columns,
    )
    output = args.output if args.output.is_absolute() else ROOT / args.output
    output.parent.mkdir(parents=True, exist_ok=True)
    image.save(output)
    if args.scale > 1:
        scaled = image.resize((image.width * args.scale, image.height * args.scale), Image.Resampling.NEAREST)
        scaled.save(output.with_name(f"{output.stem}_{args.scale}x{output.suffix}"))
    print(f"wrote: {output} ({image.width}x{image.height})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
