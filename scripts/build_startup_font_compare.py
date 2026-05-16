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

OUTPUT_ROOT = REPO_ROOT / "patched_roms" / "font_compare"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="startup intro 폰트 후보 비교 ROM/시트를 생성합니다.")
    parser.add_argument("cutoff_percent", type=float, help="모든 후보에 공통 적용할 하위 컷 퍼센트")
    parser.add_argument(
        "--config",
        default=str(REPO_ROOT / "analysis" / "startup_font_compare_candidates.json"),
        help="candidate JSON path",
    )
    parser.add_argument(
        "--output-folder",
        help="결과 폴더명 override. 기본값은 p{percent}",
    )
    return parser.parse_args()


def run(cmd: list[str]) -> None:
    subprocess.run(cmd, check=True, cwd=REPO_ROOT)


def slugify(value: str) -> str:
    return "".join(ch.lower() if ch.isalnum() else "_" for ch in value).strip("_")


def sanitize_report(temp_report: Path, output_report: Path) -> None:
    payload = json.loads(temp_report.read_text(encoding="utf-8"))
    for entry in payload.get("entries", []):
        if "pgm" in entry:
            entry["pgm_basename"] = Path(entry["pgm"]).name
            del entry["pgm"]
    output_report.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")


def build_candidate(entry: dict[str, object], cutoff_percent: float, output_dir: Path) -> tuple[str, Path, Path, Path]:
    label = str(entry["label"])
    font_name = str(entry.get("font_name", label))
    slug = slugify(label)
    temp_name = f"font_compare_tmp_{output_dir.name}_{slug}"
    temp_report = REPO_ROOT / "analysis" / f"startup_intro_{temp_name}_workbench_report.json"
    temp_workbench = REPO_ROOT / "analysis" / f"startup_intro_{temp_name}_workbench"
    temp_output = REPO_ROOT / "patched_roms" / temp_name

    cmd = [
        sys.executable,
        "scripts/build_startup_intro_variant.py",
        font_name,
        str(cutoff_percent),
        "--output-name",
        temp_name,
    ]
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

    output_dir.mkdir(parents=True, exist_ok=True)
    rom_path = output_dir / f"hnr_startup_intro_{slug}.gba"
    report_path = output_dir / f"{slug}_workbench_report.json"
    shutil.copy2(temp_output / "hnr_startup_intro_test.gba", rom_path)
    sanitize_report(temp_report, report_path)

    return label, temp_report, temp_workbench, temp_output


def read_pixels_from_pgm(path: Path) -> bytes:
    return path.read_bytes().split(b"255\n", 1)[1]


def build_summary(report_paths: list[tuple[str, Path]], summary_path: Path) -> dict[str, list[dict[str, object]]]:
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
    summary_path.write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")
    return summary


def build_sheet(report_paths: list[tuple[str, Path]], sheet_path: Path) -> None:
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
    image.save(sheet_path)


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

    cutoff_label = str(int(args.cutoff_percent)) if args.cutoff_percent.is_integer() else str(args.cutoff_percent).replace(".", "_")
    folder_name = args.output_folder or f"p{cutoff_label}"
    output_dir = OUTPUT_ROOT / folder_name
    if output_dir.exists():
        shutil.rmtree(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    builds = [build_candidate(entry, args.cutoff_percent, output_dir) for entry in payload]
    report_paths = [(label, report_path) for label, report_path, _, _ in builds]
    summary_path = output_dir / "startup_intro_font_compare_summary.json"
    sheet_path = output_dir / "startup_intro_font_compare_sheet.png"
    build_summary(report_paths, summary_path)
    build_sheet(report_paths, sheet_path)
    for _, temp_report, temp_workbench, temp_output in builds:
        if temp_workbench.exists():
            shutil.rmtree(temp_workbench)
        if temp_report.exists():
            temp_report.unlink()
        if temp_output.exists():
            shutil.rmtree(temp_output)
    print(f"compare sheet : {sheet_path}")
    print(f"compare summary: {summary_path}")
    print(f"compare rom dir: {output_dir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
