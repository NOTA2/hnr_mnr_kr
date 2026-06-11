#!/usr/bin/env python3

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
VENDOR_DIR = REPO_ROOT / ".vendor"

try:
    from PIL import Image
except Exception as first_exc:  # pragma: no cover - runtime dependency guard
    if VENDOR_DIR.exists() and str(VENDOR_DIR) not in sys.path:
        sys.path.append(str(VENDOR_DIR))
    try:
        from PIL import Image
    except Exception as exc:
        raise SystemExit(
            "error: Pillow 가 필요합니다. 번들 Python 또는 `python3 -m pip install --target .vendor pillow` 로 실행하세요.\n"
            f"detail: {exc or first_exc}"
        )


HANGUL_BASE = 0xAC00
HANGUL_END = 0xD7A3
HANGUL_COUNT = HANGUL_END - HANGUL_BASE + 1


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="12x12 한글 음절 atlas PNG 를 glyph workbench 로 변환합니다."
    )
    parser.add_argument("--atlas", required=True, help="source atlas png path")
    parser.add_argument("--manifest", required=True, help="target seed manifest json path")
    parser.add_argument("--output-dir", required=True, help="output workbench dir")
    parser.add_argument("--tile-width", type=int, default=12)
    parser.add_argument("--tile-height", type=int, default=12)
    parser.add_argument(
        "--cell-width",
        type=int,
        help="atlas cell width when the source has spacing around each glyph; defaults to tile width",
    )
    parser.add_argument(
        "--cell-height",
        type=int,
        help="atlas cell height when the source has spacing around each glyph; defaults to tile height",
    )
    parser.add_argument("--glyph-offset-x", type=int, default=0)
    parser.add_argument("--glyph-offset-y", type=int, default=0)
    parser.add_argument("--expected-columns", type=int, help="expected atlas column count")
    parser.add_argument("--expected-rows", type=int, help="expected atlas row count")
    parser.add_argument("--order", choices=("unicode_hangul_syllables",), default="unicode_hangul_syllables")
    parser.add_argument("--report", help="output report json path")
    return parser.parse_args()


def write_pgm(path: Path, pixels: bytes, width: int, height: int) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    header = f"P5\n{width} {height}\n255\n".encode("ascii")
    path.write_bytes(header + pixels)


def normalize_rgba_tile_to_game_font_levels(tile: Image.Image) -> bytes:
    rgba = tile.convert("RGBA")
    out = bytearray()
    pixels = rgba.load()
    for y in range(rgba.height):
        for x in range(rgba.width):
            r, g, b, a = pixels[x, y]
            if a < 32:
                out.append(0)
                continue
            luminance = 0.2126 * r + 0.7152 * g + 0.0722 * b
            # Match the game's original intro glyph palette role:
            # in-game body is the brighter-looking stage, but it maps to nibble 1,
            # while the darker shadow maps to nibble 2 on this screen.
            if luminance >= 200:
                out.append(17)
            elif luminance >= 32:
                out.append(34)
            else:
                out.append(0)
    return bytes(out)


def hangul_index_for_char(char: str) -> int:
    if len(char) != 1:
        raise ValueError(f"expected single character, got {char!r}")
    codepoint = ord(char)
    if not (HANGUL_BASE <= codepoint <= HANGUL_END):
        raise ValueError(f"character out of Hangul syllables range: {char} U+{codepoint:04X}")
    return codepoint - HANGUL_BASE


def main() -> int:
    args = parse_args()
    atlas_path = Path(args.atlas).expanduser()
    manifest_path = Path(args.manifest)
    output_dir = Path(args.output_dir)

    if not atlas_path.exists():
        raise SystemExit(f"error: atlas not found: {atlas_path}")

    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    if not isinstance(manifest, list):
        raise SystemExit("error: manifest 는 JSON 배열이어야 합니다.")

    atlas = Image.open(atlas_path)
    cell_width = args.cell_width or args.tile_width
    cell_height = args.cell_height or args.tile_height
    if args.glyph_offset_x < 0 or args.glyph_offset_y < 0:
        raise SystemExit("error: glyph offsets must be non-negative")
    if args.glyph_offset_x + args.tile_width > cell_width or args.glyph_offset_y + args.tile_height > cell_height:
        raise SystemExit("error: glyph crop is outside the atlas cell")

    if atlas.width % cell_width or atlas.height % cell_height:
        raise SystemExit(
            f"error: atlas size {atlas.width}x{atlas.height} is not divisible by "
            f"{cell_width}x{cell_height}"
        )

    columns = atlas.width // cell_width
    rows = atlas.height // cell_height
    if args.expected_columns is not None and columns != args.expected_columns:
        raise SystemExit(f"error: expected {args.expected_columns} columns, got {columns}")
    if args.expected_rows is not None and rows != args.expected_rows:
        raise SystemExit(f"error: expected {args.expected_rows} rows, got {rows}")
    tile_count = columns * rows
    if tile_count < HANGUL_COUNT:
        raise SystemExit(
            f"error: atlas tile count {tile_count} is smaller than required Hangul syllables {HANGUL_COUNT}"
        )

    output_dir.mkdir(parents=True, exist_ok=True)
    prepared_manifest = []
    table_lines = []
    report_entries = []

    for index, item in enumerate(manifest):
        code = str(item["code"])
        char = str(item["char"])
        name = str(item.get("name") or f"glyph_{code}")

        tile_index = hangul_index_for_char(char)
        cell_x = (tile_index % columns) * cell_width
        cell_y = (tile_index // columns) * cell_height
        tile_x = cell_x + args.glyph_offset_x
        tile_y = cell_y + args.glyph_offset_y
        tile = atlas.crop((tile_x, tile_y, tile_x + args.tile_width, tile_y + args.tile_height))
        pixels = normalize_rgba_tile_to_game_font_levels(tile)

        pgm_path = output_dir / f"{name}.pgm"
        write_pgm(pgm_path, pixels, args.tile_width, args.tile_height)

        prepared_manifest.append(
            {
                "code": code,
                "char": char,
                "pgm": str(pgm_path),
            }
        )
        table_lines.append(f"{code.replace('0x', '').upper()}={char}")
        report_entries.append(
            {
                "index": index,
                "code": code,
                "char": char,
                "name": name,
                "tile_index": tile_index,
                "cell_x": cell_x,
                "cell_y": cell_y,
                "tile_x": tile_x,
                "tile_y": tile_y,
                "nonzero_pixels": sum(1 for value in pixels if value),
                "pgm": str(pgm_path),
            }
        )

    prepared_manifest_path = output_dir / "prepared_manifest.json"
    table_path = output_dir / "prepared.tbl"
    prepared_manifest_path.write_text(json.dumps(prepared_manifest, ensure_ascii=False, indent=2), encoding="utf-8")
    table_path.write_text("\n".join(table_lines) + "\n", encoding="utf-8")

    result = {
        "atlas": str(atlas_path),
        "manifest": str(manifest_path),
        "output_dir": str(output_dir),
        "prepared_manifest": str(prepared_manifest_path),
        "table": str(table_path),
        "tile_width": args.tile_width,
        "tile_height": args.tile_height,
        "cell_width": cell_width,
        "cell_height": cell_height,
        "glyph_offset_x": args.glyph_offset_x,
        "glyph_offset_y": args.glyph_offset_y,
        "columns": columns,
        "rows": rows,
        "tile_count": tile_count,
        "hangul_count": HANGUL_COUNT,
        "unused_tiles": tile_count - HANGUL_COUNT,
        "entries": report_entries,
    }
    if args.report:
        Path(args.report).write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")

    print(f"atlas          : {atlas_path}")
    print(f"grid           : {columns} x {rows}")
    print(f"cell           : {cell_width} x {cell_height}")
    print(f"glyph          : {args.tile_width} x {args.tile_height} @ +{args.glyph_offset_x},+{args.glyph_offset_y}")
    print(f"tile_count     : {tile_count}")
    print(f"hangul_count   : {HANGUL_COUNT}")
    print(f"unused_tiles   : {tile_count - HANGUL_COUNT}")
    print(f"prepared_dir   : {output_dir}")
    print(f"prepared_count : {len(report_entries)}")
    print(f"prepared_table : {table_path}")
    if args.report:
        print(f"report         : {args.report}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
