#!/usr/bin/env python3
"""Search ROM for runtime BG screenblock/tilemap fragments.

Tilemap-rendered previews are only diagnostic. To make them actionable, we need
to connect visible runtime layers back to ROM data. This script extracts BG
screenblocks from pymgba VRAM dumps and searches for exact raw tilemap spans in
the ROM. Exact hits are likely direct tilemap source data or decompressed map
payloads copied verbatim from ROM.
"""

from __future__ import annotations

import argparse
import json
import struct
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_ROM = ROOT / "patched_roms/current_review/hnr_localization_review_no_entry8_stable.gba"
DEFAULT_CAPTURE_ROOT = ROOT / "confirmed_data/image_inventory/runtime_user_captures"
DEFAULT_OUT = ROOT / "confirmed_data/image_inventory/runtime_tilemaps/tilemap_source_audit.json"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--rom", type=Path, default=DEFAULT_ROM)
    parser.add_argument("--capture-root", type=Path, default=DEFAULT_CAPTURE_ROOT)
    parser.add_argument("--out", type=Path, default=DEFAULT_OUT)
    parser.add_argument("--min-run", type=int, default=8, help="minimum non-zero tilemap entries to search")
    return parser.parse_args()


def read_bg_controls(ioreg: bytes) -> list[dict]:
    controls = []
    dispcnt = struct.unpack_from("<H", ioreg, 0)[0]
    for bg in range(4):
        bgcnt = struct.unpack_from("<H", ioreg, 0x8 + bg * 2)[0]
        controls.append(
            {
                "bg": bg,
                "enabled": bool(dispcnt & (1 << (8 + bg))),
                "bgcnt": bgcnt,
                "char_base": (bgcnt >> 2) & 0x3,
                "screen_base": (bgcnt >> 8) & 0x1F,
                "is_8bpp": bool(bgcnt & 0x80),
                "size": (bgcnt >> 14) & 0x3,
                "scroll_x": struct.unpack_from("<H", ioreg, 0x10 + bg * 4)[0] & 0x1FF,
                "scroll_y": struct.unpack_from("<H", ioreg, 0x12 + bg * 4)[0] & 0x1FF,
            }
        )
    return controls


def nonzero_spans(screenblock: bytes, min_run: int) -> list[dict]:
    entries = [struct.unpack_from("<H", screenblock, index * 2)[0] for index in range(len(screenblock) // 2)]
    spans = []
    start = None
    for index, entry in enumerate(entries + [0]):
        if entry != 0 and start is None:
            start = index
        elif entry == 0 and start is not None:
            if index - start >= min_run:
                spans.append(
                    {
                        "entry_start": start,
                        "entry_end": index,
                        "byte_start": start * 2,
                        "byte_end": index * 2,
                        "payload": screenblock[start * 2 : index * 2],
                    }
                )
            start = None
    return spans


def first_rom_hit(rom: bytes, payload: bytes) -> int | None:
    offset = rom.find(payload)
    return None if offset < 0 else offset


def audit_probe_dir(rom: bytes, probe_dir: Path, min_run: int) -> list[dict]:
    results = []
    for vram_path in sorted(probe_dir.glob("frame_*_vram_06000000.bin")):
        frame = vram_path.name.removesuffix("_vram_06000000.bin")
        ioreg_path = vram_path.with_name(f"{frame}_ioreg_04000000.bin")
        if not ioreg_path.exists():
            continue
        vram = vram_path.read_bytes()
        ioreg = ioreg_path.read_bytes()
        for bg in read_bg_controls(ioreg):
            screen_offset = bg["screen_base"] * 0x800
            screenblock = vram[screen_offset : screen_offset + 0x800]
            whole_hit = first_rom_hit(rom, screenblock)
            spans = []
            for span in nonzero_spans(screenblock, min_run):
                hit = first_rom_hit(rom, span["payload"])
                if hit is None:
                    continue
                spans.append(
                    {
                        "entry_start": span["entry_start"],
                        "entry_end": span["entry_end"],
                        "byte_length": len(span["payload"]),
                        "rom_offset": hit,
                        "rom_offset_hex": f"0x{hit:08X}",
                    }
                )
            results.append(
                {
                    "scene": probe_dir.name,
                    "frame": frame,
                    **bg,
                    "screenblock_vram_offset": screen_offset,
                    "screenblock_vram_offset_hex": f"0x{screen_offset:05X}",
                    "nonzero_entries": sum(
                        1
                        for index in range(len(screenblock) // 2)
                        if struct.unpack_from("<H", screenblock, index * 2)[0]
                    ),
                    "whole_block_rom_offset": whole_hit,
                    "whole_block_rom_offset_hex": f"0x{whole_hit:08X}" if whole_hit is not None else "",
                    "raw_span_hits": spans,
                }
            )
    return results


def main() -> int:
    args = parse_args()
    rom = args.rom.resolve().read_bytes()
    capture_root = args.capture_root.resolve()
    all_results = []
    for probe_dir in sorted(path for path in capture_root.iterdir() if path.is_dir()):
        if list(probe_dir.glob("frame_*_vram_06000000.bin")):
            all_results.extend(audit_probe_dir(rom, probe_dir, args.min_run))

    payload = {
        "rom": str(args.rom),
        "min_run": args.min_run,
        "results": all_results,
    }
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    hit_count = sum(1 for item in all_results if item["whole_block_rom_offset"] is not None or item["raw_span_hits"])
    print(f"layers audited: {len(all_results)}")
    print(f"layers with raw ROM hits: {hit_count}")
    print(f"out: {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
