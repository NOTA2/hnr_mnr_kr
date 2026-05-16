#!/usr/bin/env python3

from __future__ import annotations

import argparse
import shutil
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
ROM_PATH = REPO_ROOT / "Hagane no Renkinjutsushi - Meisou no Rondo (Japan).gba"
TEXTS_PATH = REPO_ROOT / "analysis" / "startup_intro_texts.json"
SEED_MANIFEST = REPO_ROOT / "analysis" / "startup_intro_seed_manifest.json"
PATCHED_ROOT = REPO_ROOT / "patched_roms"
ANALYSIS_ROOT = REPO_ROOT / "analysis"

FONT_PRESETS = {
    "d2coding": {
        "kind": "ttf",
        "font_path": Path("/Users/user/Library/Fonts/D2Coding-Ver1.3.2-20180524.ttf"),
        "font_size": 11,
        "x_offset": 0,
        "y_offset": 0,
    },
    "galmuri11": {
        "kind": "ttf",
        "font_path": REPO_ROOT / "node_modules" / "galmuri" / "dist" / "Galmuri11.ttf",
        "font_size": 10,
        "x_offset": 0,
        "y_offset": 0,
    },
    "nanumsquarer": {
        "kind": "ttf",
        "font_path": Path("/Users/user/Library/Fonts/NanumSquareR.ttf"),
        "font_size": 11,
        "x_offset": 0,
        "y_offset": 0,
    },
    "sourcehansanskr": {
        "kind": "bmfont",
        "fnt_path": REPO_ROOT / "third_party" / "gba_free_fonts" / "SourceHanSansKR" / "source_han_sans_kr.fnt",
        "placement_mode": "center",
        "x_offset": 0,
        "y_offset": 0,
    },
    "sourcehanmonokr": {
        "kind": "bmfont",
        "fnt_path": REPO_ROOT / "third_party" / "gba_free_fonts" / "SourceHanMonoKR" / "source_han_mono_kr.fnt",
        "placement_mode": "center",
        "x_offset": 0,
        "y_offset": 0,
    },
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="startup intro 한글 glyph seed와 테스트 ROM을 폰트명 + 하위 퍼센트 컷으로 생성합니다."
    )
    parser.add_argument("font_name", help="예: D2Coding, Galmuri11, NanumSquareR")
    parser.add_argument("cutoff_percent", type=float, help="예: 20 -> 하위 20%% 컷")
    parser.add_argument("--font-path", help="preset 대신 직접 폰트 파일 경로 사용")
    parser.add_argument("--bmfont-fnt", help="preset 대신 직접 BMFont .fnt 경로 사용")
    parser.add_argument("--font-size", type=int, help="폰트 크기 override")
    parser.add_argument("--x-offset", type=int, help="x offset override")
    parser.add_argument("--y-offset", type=int, help="y offset override")
    parser.add_argument("--placement-mode", choices=("center", "metrics"), help="BMFont glyph 배치 방식 override")
    parser.add_argument("--output-name", help="기본 active 경로 대신 쓸 이름")
    parser.add_argument("--keep-workbench", action="store_true", help="기존 같은 이름 workbench를 덮어쓰지 않고 유지")
    return parser.parse_args()


def run(cmd: list[str]) -> None:
    print("$", " ".join(cmd))
    subprocess.run(cmd, check=True, cwd=REPO_ROOT)


def slugify(value: str) -> str:
    return "".join(ch.lower() if ch.isalnum() else "_" for ch in value).strip("_")


def main() -> int:
    args = parse_args()
    preset_key = args.font_name.lower()
    preset = FONT_PRESETS.get(preset_key)
    if preset is None and not args.font_path and not args.bmfont_fnt:
        available = ", ".join(sorted(FONT_PRESETS))
        raise SystemExit(f"unknown font preset: {args.font_name}\navailable: {available}")

    preset_kind = str(preset["kind"]) if preset is not None else ("bmfont" if args.bmfont_fnt else "ttf")
    x_offset = args.x_offset if args.x_offset is not None else int((preset or {}).get("x_offset", 0))
    y_offset = args.y_offset if args.y_offset is not None else int((preset or {}).get("y_offset", 0))
    placement_mode = args.placement_mode if args.placement_mode is not None else str((preset or {}).get("placement_mode", "center"))

    font_path = None
    bmfont_fnt = None
    font_size = None
    if preset_kind == "ttf":
        font_path = Path(args.font_path).expanduser() if args.font_path else Path(preset["font_path"])
        font_size = args.font_size if args.font_size is not None else int(preset["font_size"])
        if not font_path.exists():
            raise SystemExit(f"font file not found: {font_path}")
    else:
        bmfont_fnt = Path(args.bmfont_fnt).expanduser() if args.bmfont_fnt else Path(preset["fnt_path"])
        if not bmfont_fnt.exists():
            raise SystemExit(f"bmfont file not found: {bmfont_fnt}")

    cutoff_ratio = args.cutoff_percent / 100.0
    if cutoff_ratio < 0 or cutoff_ratio > 1:
        raise SystemExit("cutoff_percent must be between 0 and 100")

    if args.output_name:
        font_slug = slugify(args.output_name)
        workbench_dir = ANALYSIS_ROOT / f"startup_intro_{font_slug}_workbench"
        report_path = ANALYSIS_ROOT / f"startup_intro_{font_slug}_workbench_report.json"
        output_dir = PATCHED_ROOT / font_slug
        font_rom_name = f"hnr_font_startup_{font_slug}.gba"
    else:
        font_slug = "active"
        workbench_dir = ANALYSIS_ROOT / "startup_intro_active_workbench"
        report_path = ANALYSIS_ROOT / "startup_intro_active_workbench_report.json"
        output_dir = PATCHED_ROOT / "startup_intro_active"
        font_rom_name = "hnr_font_startup_active.gba"
    base_rom = output_dir / "font_expand_base.gba"
    font_rom = output_dir / font_rom_name
    intro_rom = output_dir / "hnr_startup_intro_test.gba"

    if workbench_dir.exists() and not args.keep_workbench:
        shutil.rmtree(workbench_dir)
    if output_dir.exists():
        shutil.rmtree(output_dir)
    workbench_dir.mkdir(parents=True, exist_ok=True)
    output_dir.mkdir(parents=True, exist_ok=True)

    if preset_kind == "ttf":
        run(
            [
                sys.executable,
                "scripts/render_reference_font_workbench.py",
                "--font-path",
                str(font_path),
                "--manifest",
                str(SEED_MANIFEST),
                "--output-dir",
                str(workbench_dir),
                "--font-size",
                str(font_size),
                "--x-offset",
                str(x_offset),
                "--y-offset",
                str(y_offset),
                "--quantization-mode",
                "binary2",
                "--binary-cutoff-ratio",
                str(cutoff_ratio),
                "--report",
                str(report_path),
            ]
        )
    else:
        run(
            [
                sys.executable,
                "scripts/import_bmfont_workbench.py",
                "--fnt-path",
                str(bmfont_fnt),
                "--manifest",
                str(SEED_MANIFEST),
                "--output-dir",
                str(workbench_dir),
                "--x-offset",
                str(x_offset),
                "--y-offset",
                str(y_offset),
                "--placement-mode",
                placement_mode,
                "--quantization-mode",
                "binary2",
                "--binary-cutoff-ratio",
                str(cutoff_ratio),
                "--report",
                str(report_path),
            ]
        )

    run(
        [
            sys.executable,
            "-m",
            "gba_kor_tool",
            "audit-pgm-glyph-set",
            str(workbench_dir / "prepared_manifest.json"),
            "--allowed-values",
            "0,34",
            "--fail-on-disallowed",
            "--fail-on-blank",
            "--output",
            str(output_dir / "glyph_audit.json"),
        ]
    )

    run(
        [
            sys.executable,
            "-m",
            "gba_kor_tool",
            "relocate-chunk",
            str(ROM_PATH),
            str(base_rom),
            "--table",
            "0x17C2F4",
            "--index",
            "0",
            "--layout",
            "pointer-length",
            "--new-length",
            "0x42000",
            "--destination-offset",
            "0x800000",
            "--mirror-table",
            "0x1823A0",
            "--report",
            str(output_dir / "font_expand_base_report.json"),
        ]
    )

    run(
        [
            sys.executable,
            "-m",
            "gba_kor_tool",
            "append-fnt-glyph-set",
            str(base_rom),
            str(font_rom),
            "0x800000",
            "--payload-length",
            "0x42000",
            "--manifest",
            str(workbench_dir / "prepared_manifest.json"),
            "--report",
            str(output_dir / "font_append_report.json"),
        ]
    )

    run(
        [
            sys.executable,
            "-m",
            "gba_kor_tool",
            "apply-translations",
            str(font_rom),
            str(TEXTS_PATH),
            str(intro_rom),
            "--table",
            str(workbench_dir / "prepared.tbl"),
            "--encoding",
            "cp932",
            "--report",
            str(output_dir / "startup_intro_apply_report.json"),
        ]
    )

    print()
    print("done")
    print(f"font preset : {args.font_name}")
    if font_path is not None:
        print(f"font path   : {font_path}")
    if bmfont_fnt is not None:
        print(f"bmfont fnt  : {bmfont_fnt}")
    print(f"cutoff      : {args.cutoff_percent}%")
    print(f"workbench   : {workbench_dir}")
    print(f"font rom    : {font_rom}")
    print(f"intro rom   : {intro_rom}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
