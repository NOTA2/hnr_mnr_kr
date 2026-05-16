#!/usr/bin/env python3

from __future__ import annotations

import argparse
import json
import math
import re
import sys
from dataclasses import dataclass
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
VENDOR_DIR = REPO_ROOT / ".vendor"
if VENDOR_DIR.exists():
    sys.path.insert(0, str(VENDOR_DIR))

try:
    from PIL import Image
except Exception as exc:  # pragma: no cover - runtime dependency guard
    raise SystemExit(
        "error: Pillow 가 필요합니다. `python3 -m pip install --target .vendor pillow` 로 설치하세요.\n"
        f"detail: {exc}"
    )


@dataclass
class BmChar:
    char_id: int
    page: int
    x: int
    y: int
    width: int
    height: int
    xoffset: int
    yoffset: int
    xadvance: int


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="BMFont .fnt + atlas PNG 에서 12x12 PGM glyph seed workbench 를 생성합니다."
    )
    parser.add_argument("--fnt-path", required=True)
    parser.add_argument("--manifest", required=True)
    parser.add_argument("--output-dir", required=True)
    parser.add_argument("--canvas-width", type=int, default=12)
    parser.add_argument("--canvas-height", type=int, default=12)
    parser.add_argument("--x-offset", type=int, default=0)
    parser.add_argument("--y-offset", type=int, default=0)
    parser.add_argument(
        "--placement-mode",
        choices=("center", "metrics"),
        default="center",
        help="glyph 를 캔버스에 배치하는 방식. 기본값: center",
    )
    parser.add_argument(
        "--quantization-mode",
        choices=("native3", "binary2", "grayscale"),
        default="binary2",
    )
    parser.add_argument("--binary-threshold", type=int, default=128)
    parser.add_argument("--binary-cutoff-ratio", type=float)
    parser.add_argument("--report")
    return parser.parse_args()


def sanitize_stem(value: str) -> str:
    stem = re.sub(r"[^0-9A-Za-z_.-]+", "_", value).strip("_")
    return stem or "glyph"


def write_pgm(path: Path, pixels: bytes, width: int, height: int) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    header = f"P5\n{width} {height}\n255\n".encode("ascii")
    path.write_bytes(header + pixels)


def quantize_to_native_fnt_levels(pixels: bytes) -> bytes:
    out = bytearray(len(pixels))
    for index, value in enumerate(pixels):
        level = round(value * 2 / 255)
        out[index] = level * 17
    return bytes(out)


def quantize_to_binary_fnt_levels(pixels: bytes, *, threshold: int) -> bytes:
    out = bytearray(len(pixels))
    normalized_threshold = max(0, min(255, threshold))
    for index, value in enumerate(pixels):
        out[index] = 34 if value >= normalized_threshold else 0
    return bytes(out)


def resolve_binary_threshold(pixels: bytes, *, threshold: int, cutoff_ratio: float | None) -> int:
    if cutoff_ratio is None:
        return max(0, min(255, threshold))
    if cutoff_ratio < 0 or cutoff_ratio > 1:
        raise ValueError("binary_cutoff_ratio must be within 0..1")
    nonzero_values = [value for value in pixels if value]
    if not nonzero_values:
        return max(0, min(255, threshold))
    max_nonzero = max(nonzero_values)
    return max(1, min(255, math.ceil(max_nonzero * cutoff_ratio)))


def parse_key_values(line: str) -> dict[str, str]:
    result: dict[str, str] = {}
    for key, raw_value in re.findall(r'(\w+)=(".*?"|\S+)', line):
        value = raw_value[1:-1] if raw_value.startswith('"') and raw_value.endswith('"') else raw_value
        result[key] = value
    return result


def parse_bmfont(path: Path) -> tuple[dict[int, Path], dict[int, BmChar]]:
    pages: dict[int, Path] = {}
    chars: dict[int, BmChar] = {}
    for line in path.read_text(encoding="utf-8").splitlines():
        if line.startswith("page "):
            values = parse_key_values(line)
            pages[int(values["id"])] = path.parent / values["file"]
        elif line.startswith("char "):
            values = parse_key_values(line)
            char_id = int(values["id"])
            chars[char_id] = BmChar(
                char_id=char_id,
                page=int(values["page"]),
                x=int(values["x"]),
                y=int(values["y"]),
                width=int(values["width"]),
                height=int(values["height"]),
                xoffset=int(values["xoffset"]),
                yoffset=int(values["yoffset"]),
                xadvance=int(values["xadvance"]),
            )
    return pages, chars


def crop_nonzero(glyph: Image.Image) -> Image.Image:
    bbox = glyph.getbbox()
    return glyph.crop(bbox) if bbox else glyph


def render_glyph(
    *,
    entry: BmChar,
    atlas_pages: dict[int, Image.Image],
    width: int,
    height: int,
    x_offset: int,
    y_offset: int,
    placement_mode: str,
) -> bytes:
    atlas = atlas_pages[entry.page]
    glyph = atlas.crop((entry.x, entry.y, entry.x + entry.width, entry.y + entry.height)).convert("L")
    glyph = crop_nonzero(glyph)

    canvas = Image.new("L", (width, height), 0)
    if placement_mode == "metrics":
        paste_x = ((width - entry.xadvance) // 2) + entry.xoffset + x_offset
        paste_y = entry.yoffset + y_offset
    else:
        paste_x = (width - glyph.width) // 2 + x_offset
        paste_y = (height - glyph.height) // 2 + y_offset
    canvas.paste(glyph, (paste_x, paste_y))
    return canvas.tobytes()


def main() -> int:
    args = parse_args()
    manifest_path = Path(args.manifest)
    output_dir = Path(args.output_dir)
    fnt_path = Path(args.fnt_path)

    if not fnt_path.exists():
        raise SystemExit(f"error: bmfont file not found: {fnt_path}")

    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    if not isinstance(manifest, list):
        raise SystemExit("error: manifest 는 JSON 배열이어야 합니다.")

    page_paths, chars = parse_bmfont(fnt_path)
    atlas_pages = {page_id: Image.open(page_path) for page_id, page_path in page_paths.items()}
    output_dir.mkdir(parents=True, exist_ok=True)

    prepared_manifest: list[dict[str, object]] = []
    report_entries: list[dict[str, object]] = []
    table_lines: list[str] = []

    for index, item in enumerate(manifest):
        code = str(item["code"])
        char = str(item["char"])
        stem_source = str(item.get("name") or item.get("label") or f"glyph_{code}")
        stem = sanitize_stem(stem_source)
        pgm_path = output_dir / f"{stem}.pgm"
        char_id = ord(char)
        if char_id not in chars:
            raise SystemExit(f"error: glyph not found in bmfont: {char} U+{char_id:04X}")

        pixels = render_glyph(
            entry=chars[char_id],
            atlas_pages=atlas_pages,
            width=args.canvas_width,
            height=args.canvas_height,
            x_offset=args.x_offset,
            y_offset=args.y_offset,
            placement_mode=args.placement_mode,
        )
        effective_binary_threshold = None
        if args.quantization_mode == "native3":
            pixels = quantize_to_native_fnt_levels(pixels)
        elif args.quantization_mode == "binary2":
            effective_binary_threshold = resolve_binary_threshold(
                pixels,
                threshold=args.binary_threshold,
                cutoff_ratio=args.binary_cutoff_ratio,
            )
            pixels = quantize_to_binary_fnt_levels(pixels, threshold=effective_binary_threshold)
        nonzero = sum(1 for value in pixels if value)
        write_pgm(pgm_path, pixels, args.canvas_width, args.canvas_height)

        prepared_manifest.append({"code": code, "char": char, "pgm": str(pgm_path)})
        table_lines.append(f"{code.replace('0x', '').upper()}={char}")
        report_entries.append(
            {
                "index": index,
                "code": code,
                "char": char,
                "pgm": str(pgm_path),
                "nonzero_pixels": nonzero,
                "bmfont_char_id": char_id,
                "effective_binary_threshold": effective_binary_threshold,
            }
        )

    prepared_manifest_path = output_dir / "prepared_manifest.json"
    table_path = output_dir / "prepared.tbl"
    prepared_manifest_path.write_text(
        json.dumps(prepared_manifest, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    table_path.write_text("\n".join(table_lines) + "\n", encoding="utf-8")

    result = {
        "fnt_path": str(fnt_path),
        "manifest": str(manifest_path),
        "output_dir": str(output_dir),
        "prepared_manifest": str(prepared_manifest_path),
        "table": str(table_path),
        "canvas_width": args.canvas_width,
        "canvas_height": args.canvas_height,
        "x_offset": args.x_offset,
        "y_offset": args.y_offset,
        "placement_mode": args.placement_mode,
        "quantization_mode": args.quantization_mode,
        "binary_threshold": args.binary_threshold,
        "binary_cutoff_ratio": args.binary_cutoff_ratio,
        "count": len(report_entries),
        "entries": report_entries,
    }
    if args.report:
        Path(args.report).write_text(
            json.dumps(result, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )

    print(f"bmfont          : {fnt_path}")
    print(f"prepared_dir    : {output_dir}")
    print(f"prepared_count  : {len(report_entries)}")
    print(f"prepared_manifest: {prepared_manifest_path}")
    print(f"table           : {table_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
