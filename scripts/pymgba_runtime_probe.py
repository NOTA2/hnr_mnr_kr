#!/usr/bin/env python3
"""Run the current GBA ROM through pymgba and dump visual runtime state.

This is intentionally small and local: it uses the mGBA Python bindings built
under third_party/mgba-python-build-x86 plus pymgba-mcp's emulator wrapper.
"""

from __future__ import annotations

import argparse
import contextlib
import ctypes
import json
import os
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
STABLE_ROM = ROOT / "patched_roms/current_review/hnr_localization_review_no_entry8_stable.gba"
DEFAULT_ROM = STABLE_ROM if STABLE_ROM.exists() else ROOT / "patched_roms/current_review/hnr_localization_review.gba"
DEFAULT_OUT = ROOT / "confirmed_data/image_inventory/pymgba_runtime_probe"
PYMGBA_SRC = ROOT / "third_party/pymgba-mcp/src"
MGBA_PY_BUILD = ROOT / "third_party/mgba-python-build-x86/python/lib.macosx-14.0-x86_64-cpython-312"


def add_runtime_paths() -> None:
    for path in (PYMGBA_SRC, MGBA_PY_BUILD):
        if not path.exists():
            raise SystemExit(f"missing runtime path: {path}")
        sys.path.insert(0, str(path))


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--rom", type=Path, default=DEFAULT_ROM, help="GBA ROM to load")
    parser.add_argument("--out-dir", type=Path, default=DEFAULT_OUT, help="dump output directory")
    parser.add_argument("--frames", type=int, default=180, help="frames to run before dumping")
    parser.add_argument("--state-file", type=Path, help="mGBA savestate file (.ss0-.ss9) to load before dumping")
    parser.add_argument(
        "--press",
        action="append",
        default=[],
        metavar="BUTTON:FRAMES",
        help="button press before the final frame run, e.g. start:20 or a:8",
    )
    parser.add_argument("--show-mgba-log", action="store_true", help="show verbose mGBA stderr logging")
    return parser.parse_args()


@contextlib.contextmanager
def maybe_silence_mgba_log(enabled: bool):
    if not enabled:
        yield
        return

    saved_stdout = os.dup(1)
    saved_stderr = os.dup(2)
    try:
        with open(os.devnull, "wb") as devnull:
            os.dup2(devnull.fileno(), 1)
            os.dup2(devnull.fileno(), 2)
            yield
    finally:
        ctypes.CDLL(None).fflush(None)
        os.dup2(saved_stdout, 1)
        os.dup2(saved_stderr, 2)
        os.close(saved_stdout)
        os.close(saved_stderr)


def run() -> None:
    args = parse_args()
    add_runtime_paths()

    from pymgba_mcp.emulator import Emulator
    from mgba._pylib import ffi, lib

    rom = args.rom.resolve()
    out_dir = args.out_dir.resolve()
    out_dir.mkdir(parents=True, exist_ok=True)

    output_png = None
    with maybe_silence_mgba_log(not args.show_mgba_log):
        emu = Emulator()
        try:
            info = emu.load_rom(str(rom))
            if args.state_file:
                state_path = args.state_file.resolve()
                vf = lib.VFileOpen(str(state_path).encode(), os.O_RDONLY)
                if vf == ffi.NULL:
                    raise SystemExit(f"failed to open savestate: {state_path}")
                if not lib.mCoreLoadStateNamed(emu._core, vf, 1 | 8):
                    raise SystemExit(f"failed to load savestate: {state_path}")
            for spec in args.press:
                button, _, frame_text = spec.partition(":")
                emu.press_button(button, int(frame_text or "1"))
            frame_count = emu.run_frames(args.frames)

            prefix = f"frame_{frame_count:06d}"
            output_png = out_dir / f"{prefix}.png"
            output_png.write_bytes(emu.take_screenshot())
            (out_dir / f"{prefix}_vram_06000000.bin").write_bytes(bytes(emu.read_memory(0x06000000, 0x18000)))
            (out_dir / f"{prefix}_palette_05000000.bin").write_bytes(bytes(emu.read_memory(0x05000000, 0x400)))
            (out_dir / f"{prefix}_ioreg_04000000.bin").write_bytes(bytes(emu.read_memory(0x04000000, 0x60)))
            (out_dir / f"{prefix}_oam_07000000.json").write_text(
                json.dumps(emu.dump_oam(), ensure_ascii=False, indent=2),
                encoding="utf-8",
            )
            (out_dir / f"{prefix}_info.json").write_text(
                json.dumps({"rom": str(rom), "frame_count": frame_count, "game": info}, ensure_ascii=False, indent=2),
                encoding="utf-8",
            )
        finally:
            emu.close()
    print(f"wrote runtime probe: {output_png}")


if __name__ == "__main__":
    run()
