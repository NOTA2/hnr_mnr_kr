#!/usr/bin/env python3

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_PROFILE = REPO_ROOT / "confirmed_data" / "font_assets" / "active_hangul_font_profile.json"
HANGUL_START = 0xAC00
HANGUL_END = 0xD7A3
SAFE_TRAIL_BYTES = set(range(0x40, 0x7F)) | set(range(0x80, 0xFC))
NARROW_PUNCTUATION_GLYPHS = [
    {"code": "0x0021", "source_code": "0x8149", "label": "ascii_exclamation"},
    {"code": "0x0022", "bitmap": "double_quote", "label": "ascii_double_quote"},
    {"code": "0x0027", "bitmap": "apostrophe", "label": "ascii_apostrophe"},
    {"code": "0x002C", "source_code": "0x8141", "label": "ascii_comma"},
    {"code": "0x002D", "source_code": "0x817C", "label": "ascii_hyphen"},
    {"code": "0x002F", "source_code": "0x815E", "label": "ascii_slash"},
    {"code": "0x003F", "source_code": "0x8148", "label": "ascii_question"},
]
PUNCTUATION_BITMAP_POINTS = {
    "apostrophe": [(6, 1), (6, 2), (5, 3)],
    "double_quote": [(4, 1), (4, 2), (7, 1), (7, 2)],
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="번역 JSON 에서 한글 subset 을 추출하고 active atlas 로 workbench 를 생성합니다."
    )
    parser.add_argument("output_dir", help="output workbench directory")
    parser.add_argument("inputs", nargs="+", help="translation json files")
    parser.add_argument("--field", default="translation", help="text field to scan")
    parser.add_argument("--start-code", default="0xE940", help="first custom code")
    parser.add_argument("--limit", type=int, help="optional glyph count limit")
    parser.add_argument("--profile", default=str(DEFAULT_PROFILE), help="active font profile json")
    parser.add_argument("--report", help="output report json path")
    return parser.parse_args()


def load_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def iter_strings(value):
    if isinstance(value, str):
        yield value
    elif isinstance(value, list):
        for item in value:
            yield from iter_strings(item)
    elif isinstance(value, dict):
        for item in value.values():
            yield from iter_strings(item)


def extract_hangul_chars(inputs: list[Path], field: str, limit: int | None) -> tuple[list[str], list[dict]]:
    seen: set[str] = set()
    chars: list[str] = []
    sources: list[dict] = []

    for path in inputs:
        payload = load_json(path)
        if not isinstance(payload, list):
            raise SystemExit(f"error: expected JSON array in {path}")
        for record_index, record in enumerate(payload):
            if not isinstance(record, dict):
                continue
            if field not in record:
                continue
            for text in iter_strings(record.get(field)):
                for char in text:
                    codepoint = ord(char)
                    if HANGUL_START <= codepoint <= HANGUL_END and char not in seen:
                        seen.add(char)
                        chars.append(char)
                        sources.append(
                            {
                                "char": char,
                                "source_file": str(path),
                                "record_index": record_index,
                            }
                        )
                        if limit is not None and len(chars) >= limit:
                            return chars, sources
    return chars, sources


def is_safe_custom_code(code: int) -> bool:
    lead = code >> 8
    trail = code & 0xFF
    return 0xE0 <= lead <= 0xEF and trail in SAFE_TRAIL_BYTES


def iter_safe_custom_codes(start_code: int):
    code = start_code
    while code <= 0xEFFF:
        if is_safe_custom_code(code):
            yield code
        code += 1


def write_seed_manifest(chars: list[str], output_path: Path, start_code: int) -> list[dict]:
    manifest = []
    safe_codes = iter_safe_custom_codes(start_code)
    for char in chars:
        try:
            code = next(safe_codes)
        except StopIteration as exc:
            raise SystemExit("error: not enough safe custom Shift-JIS codes for Hangul subset") from exc
        manifest.append(
            {
                "code": f"0x{code:04X}",
                "char": char,
                "name": f"hangul_{code:04X}_{ord(char):04X}",
            }
        )
    output_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")
    return manifest


def write_pgm(path: Path, pixels: bytes, width: int = 12, height: int = 12) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(f"P5\n{width} {height}\n255\n".encode("ascii") + pixels)


def write_punctuation_bitmap(output_dir: Path, name: str) -> Path:
    pixels = bytearray(12 * 12)
    for x, y in PUNCTUATION_BITMAP_POINTS[name]:
        pixels[y * 12 + x] = 17
    pgm_path = output_dir / f"punct_{name}.pgm"
    write_pgm(pgm_path, bytes(pixels))
    return pgm_path


def append_narrow_punctuation_entries(output_dir: Path) -> list[dict]:
    """Copy visible fullwidth/Japanese punctuation glyphs onto ASCII codes.

    The renderer gives single-byte ASCII punctuation a narrower advance, but the
    original fnt lookup maps several ASCII punctuation codes to blank glyph 0.
    These copy entries make punctuation visible without forcing fullwidth codes.
    """
    manifest_path = output_dir / "prepared_manifest.json"
    manifest = load_json(manifest_path)
    if not isinstance(manifest, list):
        raise SystemExit(f"error: expected prepared manifest array in {manifest_path}")

    existing_codes = {
        str(item.get("code", "")).lower()
        for item in manifest
        if isinstance(item, dict)
    }
    appended: list[dict] = []
    for item in NARROW_PUNCTUATION_GLYPHS:
        code = item["code"].lower()
        if code in existing_codes:
            continue
        bitmap = item.get("bitmap")
        entry = {
            "code": item["code"],
            "overwrite_code": True,
            "label": item["label"],
        }
        if bitmap:
            entry["pgm"] = str(write_punctuation_bitmap(output_dir, str(bitmap)))
        else:
            entry["source_code"] = item["source_code"]
        manifest.append(entry)
        appended.append(entry)
        existing_codes.add(code)

    if appended:
        manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")
    return appended


def main() -> int:
    args = parse_args()
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    input_paths = [Path(item) for item in args.inputs]
    profile_path = Path(args.profile)
    profile = load_json(profile_path)

    start_code = int(str(args.start_code), 0)
    chars, sources = extract_hangul_chars(input_paths, args.field, args.limit)
    if not chars:
        raise SystemExit("error: no Hangul syllables found in the selected translation field")

    seed_manifest_path = output_dir / "seed_manifest.json"
    seed_manifest = write_seed_manifest(chars, seed_manifest_path, start_code)
    atlas_path = REPO_ROOT / str(profile["source_png"])
    import_report_path = output_dir / "import_report.json"

    command = [
        sys.executable,
        "scripts/import_hangul_syllable_atlas.py",
        "--atlas",
        str(atlas_path),
        "--manifest",
        str(seed_manifest_path),
        "--output-dir",
        str(output_dir),
        "--tile-width",
        str(profile["tile_width"]),
        "--tile-height",
        str(profile["tile_height"]),
        "--expected-columns",
        str(profile["columns"]),
        "--expected-rows",
        str(profile["rows"]),
        "--report",
        str(import_report_path),
    ]
    subprocess.run(command, cwd=REPO_ROOT, check=True)
    punctuation_entries = append_narrow_punctuation_entries(output_dir)

    report = {
        "profile": str(profile_path),
        "atlas": str(atlas_path),
        "output_dir": str(output_dir),
        "field": args.field,
        "start_code": f"0x{start_code:04X}",
        "input_files": [str(path) for path in input_paths],
        "hangul_count": len(chars),
        "narrow_punctuation_count": len(punctuation_entries),
        "seed_manifest": str(seed_manifest_path),
        "prepared_manifest": str(output_dir / "prepared_manifest.json"),
        "prepared_table": str(output_dir / "prepared.tbl"),
        "sources": sources,
        "entries": seed_manifest,
        "narrow_punctuation_entries": punctuation_entries,
    }
    report_path = Path(args.report) if args.report else output_dir / "workbench_report.json"
    report_path.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")

    print(f"output_dir      : {output_dir}")
    print(f"hangul_count    : {len(chars)}")
    print(f"narrow_punct    : {len(punctuation_entries)}")
    print(f"seed_manifest   : {seed_manifest_path}")
    print(f"prepared_tbl    : {output_dir / 'prepared.tbl'}")
    print(f"prepared_manifest: {output_dir / 'prepared_manifest.json'}")
    print(f"report          : {report_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
