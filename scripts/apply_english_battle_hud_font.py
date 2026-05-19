#!/usr/bin/env python3

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
    sys.path.insert(0, str(ROOT / "scripts"))

from build_tile_contact_sheets import read_pgm, write_png_gray
from extract_global_image_tiles import render_4bpp_pgm
from gba_kor_tool.cli import decompress_lz77


OFFSET = 0x00534874
EXPECTED_DECOMPRESSED_SIZE = 0x2000
DEFAULT_SOURCE = (
    ROOT
    / "local_roms"
    / "english_patched"
    / "Fullmetal Alchemist Stray Rondo (English Patched v0.02).gba"
)
DEFAULT_TARGET = ROOT / "patched_roms" / "current_review" / "hnr_localization_review.gba"
OUT_DIR = ROOT / "local_roms" / "extracted" / "english_battle_hud_small_font"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="영문판 전투 HUD 소형 폰트 LZ77 블록만 추출해 현재 리뷰 ROM에 적용합니다."
    )
    parser.add_argument("--source", type=Path, default=DEFAULT_SOURCE)
    parser.add_argument("--target", type=Path, default=DEFAULT_TARGET)
    parser.add_argument("--extract-only", action="store_true")
    return parser.parse_args()


def read_lz77_block(rom_path: Path) -> tuple[bytes, bytes, int]:
    data = rom_path.read_bytes()
    payload, consumed = decompress_lz77(
        data,
        OFFSET,
        max_output_size=max(4 * 1024 * 1024, EXPECTED_DECOMPRESSED_SIZE + 0x1000),
    )
    if len(payload) != EXPECTED_DECOMPRESSED_SIZE:
        raise SystemExit(
            f"{rom_path}의 0x{OFFSET:08X} 복원 크기가 예상과 다릅니다: "
            f"{len(payload)} != {EXPECTED_DECOMPRESSED_SIZE}"
        )
    return data[OFFSET : OFFSET + consumed], payload, consumed


def write_reference_outputs(compressed: bytes, payload: bytes) -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    compressed_path = OUT_DIR / f"english_0x{OFFSET:08X}_compressed_lz77.bin"
    payload_path = OUT_DIR / f"english_0x{OFFSET:08X}_decompressed_4bpp.bin"
    pgm_path = OUT_DIR / f"english_0x{OFFSET:08X}_preview.pgm"
    png_path = OUT_DIR / f"english_0x{OFFSET:08X}_preview.png"
    compressed_path.write_bytes(compressed)
    payload_path.write_bytes(payload)
    render_4bpp_pgm(payload, pgm_path, columns=32)
    width, height, pixels = read_pgm(pgm_path)
    write_png_gray(png_path, width, height, pixels)


def patch_target(target_path: Path, compressed: bytes, target_consumed: int) -> None:
    if len(compressed) > target_consumed:
        raise SystemExit(
            f"영문판 압축 스트림이 대상 블록보다 큽니다: {len(compressed)} > {target_consumed}"
        )
    data = bytearray(target_path.read_bytes())
    data[OFFSET : OFFSET + len(compressed)] = compressed
    target_path.write_bytes(data)


def main() -> int:
    args = parse_args()
    source_compressed, source_payload, source_consumed = read_lz77_block(args.source)
    _, target_payload_before, target_consumed = read_lz77_block(args.target)
    write_reference_outputs(source_compressed, source_payload)

    applied = False
    if not args.extract_only:
        patch_target(args.target, source_compressed, target_consumed)
        _, target_payload_after, _ = read_lz77_block(args.target)
        if target_payload_after != source_payload:
            raise SystemExit("패치 후 대상 ROM의 LZ77 복원 결과가 영문판과 일치하지 않습니다.")
        applied = True

    report = {
        "source": str(args.source.relative_to(ROOT) if args.source.is_relative_to(ROOT) else args.source),
        "target": str(args.target.relative_to(ROOT) if args.target.is_relative_to(ROOT) else args.target),
        "offset": OFFSET,
        "offset_hex": f"0x{OFFSET:08X}",
        "decompressed_size": EXPECTED_DECOMPRESSED_SIZE,
        "source_consumed": source_consumed,
        "target_consumed_before": target_consumed,
        "same_as_target_before": source_payload == target_payload_before,
        "applied": applied,
        "outputs": {
            "compressed": str((OUT_DIR / f"english_0x{OFFSET:08X}_compressed_lz77.bin").relative_to(ROOT)),
            "decompressed": str((OUT_DIR / f"english_0x{OFFSET:08X}_decompressed_4bpp.bin").relative_to(ROOT)),
            "preview_png": str((OUT_DIR / f"english_0x{OFFSET:08X}_preview.png").relative_to(ROOT)),
        },
    }
    report_path = OUT_DIR / "apply_report.json"
    report_path.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
