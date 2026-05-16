#!/usr/bin/env python3

from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
VENDOR_DIR = REPO_ROOT / ".vendor"
if VENDOR_DIR.exists():
    sys.path.insert(0, str(VENDOR_DIR))

from PIL import Image, ImageDraw

ACTIVE_WORKBENCH = REPO_ROOT / "analysis" / "startup_intro_active_workbench"
ACTIVE_REPORT = REPO_ROOT / "analysis" / "startup_intro_active_workbench_report.json"
ACTIVE_ROM = REPO_ROOT / "patched_roms" / "startup_intro_active" / "hnr_startup_intro_test.gba"
OUTPUT_DIR = REPO_ROOT / "patched_roms" / "font_compare"
SUMMARY_PATH = REPO_ROOT / "analysis" / "startup_intro_font_compare_summary.json"
SHEET_PATH = REPO_ROOT / "analysis" / "startup_intro_font_compare_sheet.png"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="startup intro 폰트 후보 비교 ROM/시트를 생성합니다.")
    parser.add_argument(
        "--config",
        default=str(REPO_ROOT / "analysis" / "startup_font_compare_candidates.json"),
        help="candidate JSON path",
    )
    return parser.parse_args()


def run(cmd: list[str]) -> None:
    subprocess.run(cmd, check=True, cwd=REPO_ROOT)


def slugify(value: str) -> str:
    return "".join(ch.lower() if ch.isalnum() else "_" for ch in value).strip("_")


def build_candidate(entry: dict[str, object]) -> tuple[str, Path]:
    label = str(entry["label"])
    font_name = str(entry.get("font_name", label))
    cutoff_percent = str(entry.get("cutoff_percent", 20))
    cmd = [sys.executable, "scripts/build_startup_intro_variant.py", font_name, cutoff_percent]
    if entry.get("font_path"):
        cmd += ["--font-path", str(entry["font_path"])]
    if entry.get("bmfont_fnt"):
        cmd += ["--bmfont-fnt", str(entry["bmfont_fnt"])]
    if entry.get("font_size") is not None:
        cmd += ["--font-size", str(entry["font_size"])]
    if entry.get("x_offset") is not None:
        cmd += ["--x-offset", str(entry["x_offset"])]
    if entry.get("y_offset") is not None:
        cmd += ["--y-offset", str(entry["y_offset"])]
    if entry.get("placement_mode"):
        cmd += ["--placement-mode", str(entry["placement_mode"])]
    run(cmd)

    slug = slugify(label)
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    rom_path = OUTPUT_DIR / f"hnr_startup_intro_{slug}.gba"
    report_path = OUTPUT_DIR / f"{slug}_workbench_report.json"
    shutil.copy2(ACTIVE_ROM, rom_path)
    shutil.copy2(ACTIVE_REPORT, report_path)
    return label, report_path


def read_pixels_from_pgm(path: Path) -> bytes:
    return path.read_bytes().split(b"255\n", 1)[1]


def build_summary(report_paths: list[tuple[str, Path]]) -> dict[str, list[dict[str, object]]]:
    summary: dict[str, list[dict[str, object]]] = {}
    for label, report_path in report_paths:
        report = json.loads(report_path.read_text(encoding="utf-8"))
        rows = []
        for entry in report["entries"]:
            pixels = read_pixels_from_pgm(Path(entry["pgm"]))
            rows.append(
                {
                    "char": entry["char"],
                    "nonzero_pixels": sum(1 for value in pixels if value),
                }
            )
        summary[label] = rows
    SUMMARY_PATH.write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")
    return summary


def build_sheet(report_paths: list[tuple[str, Path]]) -> None:
    manifests = []
    for label, report_path in report_paths:
        report = json.loads(report_path.read_text(encoding="utf-8"))
        manifests.append((label, report["entries"]))

    chars = [entry["char"] for entry in manifests[0][1]]
    cell = 48
    label_w = 160
    header_h = 28
    image = Image.new("RGB", (label_w + len(chars) * cell, header_h + len(manifests) * cell), "white")
    draw = ImageDraw.Draw(image)
    for index, char in enumerate(chars):
        draw.text((label_w + index * cell + 16, 8), char, fill="black")

    for row, (label, entries) in enumerate(manifests):
        y0 = header_h + row * cell
        draw.text((8, y0 + 14), label, fill="black")
        for col, entry in enumerate(entries):
            pixels = read_pixels_from_pgm(Path(entry["pgm"]))
            mapped = bytes(255 if value else 0 for value in pixels)
            glyph = Image.frombytes("L", (12, 12), mapped).resize((36, 36), Image.Resampling.NEAREST)
            image.paste(glyph.convert("RGB"), (label_w + col * cell + 6, y0 + 6))
    image.save(SHEET_PATH)


def main() -> int:
    args = parse_args()
    config_path = Path(args.config)
    if not config_path.is_absolute():
        config_path = (REPO_ROOT / config_path).resolve()
    payload = json.loads(config_path.read_text(encoding="utf-8"))
    if not isinstance(payload, list):
        raise SystemExit("config must be a JSON array")
    if not payload:
        raise SystemExit("config is empty")

    report_paths = [build_candidate(entry) for entry in payload]
    build_summary(report_paths)
    build_sheet(report_paths)
    build_candidate(payload[0])
    print(f"compare sheet : {SHEET_PATH}")
    print(f"compare summary: {SUMMARY_PATH}")
    print(f"compare rom dir: {OUTPUT_DIR}")
    print(f"active restore: {payload[0]['label']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
