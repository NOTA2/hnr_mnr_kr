#!/usr/bin/env python3

from __future__ import annotations

import argparse
import math
import json
import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
VENDOR_DIR = REPO_ROOT / ".vendor"
if VENDOR_DIR.exists():
    sys.path.insert(0, str(VENDOR_DIR))

try:
    from PIL import Image, ImageDraw, ImageFont
except Exception as exc:  # pragma: no cover - runtime dependency guard
    raise SystemExit(
        "error: Pillow 가 필요합니다. `python3 -m pip install --target .vendor pillow` 로 설치하세요.\n"
        f"detail: {exc}"
    )


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="참조 폰트에서 12x12 PGM glyph seed workbench 를 생성합니다."
    )
    parser.add_argument("--font-path", required=True)
    parser.add_argument("--manifest", required=True)
    parser.add_argument("--output-dir", required=True)
    parser.add_argument("--font-size", type=int, default=11)
    parser.add_argument("--canvas-width", type=int, default=12)
    parser.add_argument("--canvas-height", type=int, default=12)
    parser.add_argument("--x-offset", type=int, default=0)
    parser.add_argument("--y-offset", type=int, default=0)
    parser.add_argument(
        "--quantization-mode",
        choices=("native3", "binary2", "grayscale"),
        default="binary2",
        help="seed glyph 픽셀 양자화 방식. 기본값: binary2",
    )
    parser.add_argument(
        "--binary-threshold",
        type=int,
        default=128,
        help="binary2 모드에서 획으로 남길 최소 grayscale 값. 기본값: 128",
    )
    parser.add_argument(
        "--binary-cutoff-ratio",
        type=float,
        help="binary2 모드에서 glyph별 최대 밝기 대비 하위 비율만 잘라냅니다. 예: 0.1, 0.2",
    )
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


def render_glyph(
    *,
    char: str,
    font: ImageFont.FreeTypeFont,
    width: int,
    height: int,
    x_offset: int,
    y_offset: int,
) -> bytes:
    image = Image.new("L", (width, height), 0)
    draw = ImageDraw.Draw(image)
    bbox = draw.textbbox((0, 0), char, font=font)
    glyph_w = bbox[2] - bbox[0]
    glyph_h = bbox[3] - bbox[1]
    x = (width - glyph_w) // 2 - bbox[0] + x_offset
    y = (height - glyph_h) // 2 - bbox[1] + y_offset
    draw.text((x, y), char, fill=255, font=font)
    return image.tobytes()


def main() -> int:
    args = parse_args()
    manifest_path = Path(args.manifest)
    output_dir = Path(args.output_dir)
    font_path = Path(args.font_path).expanduser()

    if not font_path.exists():
        raise SystemExit(f"error: font file not found: {font_path}")

    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    if not isinstance(manifest, list):
        raise SystemExit("error: manifest 는 JSON 배열이어야 합니다.")

    output_dir.mkdir(parents=True, exist_ok=True)
    font = ImageFont.truetype(str(font_path), args.font_size)

    prepared_manifest: list[dict[str, object]] = []
    report_entries: list[dict[str, object]] = []
    table_lines: list[str] = []

    for index, item in enumerate(manifest):
        code = str(item["code"])
        char = str(item["char"])
        stem_source = str(item.get("name") or item.get("label") or f"glyph_{code}")
        stem = sanitize_stem(stem_source)
        pgm_path = output_dir / f"{stem}.pgm"

        pixels = render_glyph(
            char=char,
            font=font,
            width=args.canvas_width,
            height=args.canvas_height,
            x_offset=args.x_offset,
            y_offset=args.y_offset,
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
                "pgm": str(pgm_path),
                "nonzero_pixels": nonzero,
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
        "font_path": str(font_path),
        "manifest": str(manifest_path),
        "output_dir": str(output_dir),
        "prepared_manifest": str(prepared_manifest_path),
        "table": str(table_path),
        "font_size": args.font_size,
        "canvas_width": args.canvas_width,
        "canvas_height": args.canvas_height,
        "x_offset": args.x_offset,
        "y_offset": args.y_offset,
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

    print(f"font            : {font_path}")
    print(f"prepared_dir    : {output_dir}")
    print(f"prepared_count  : {len(report_entries)}")
    print(f"prepared_manifest: {prepared_manifest_path}")
    print(f"table           : {table_path}")
    if args.report:
        print(f"report          : {args.report}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
