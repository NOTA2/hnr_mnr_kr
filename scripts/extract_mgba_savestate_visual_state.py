#!/usr/bin/env python3
"""Extract visual runtime state directly from mGBA PNG savestates.

mGBA save states are PNG files with a zlib-compressed `gbAs` chunk containing
the serialized GBA state. This script extracts the visual memory regions into
the same files produced by `pymgba_runtime_probe.py`, so the existing tilemap
and ROM-block matching pipeline can work without running the emulator.
"""

from __future__ import annotations

import argparse
import binascii
import json
import re
import struct
import zlib
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUT_ROOT = ROOT / "confirmed_data" / "image_inventory" / "runtime_user_captures"

PNG_SIGNATURE = b"\x89PNG\r\n\x1a\n"
STATE_CHUNK = b"gbAs"
EXTRA_CHUNK = b"gbAx"
GBA_STATE_SIZE = 0x61000

IO_OFFSET = 0x00400
IO_DUMP_SIZE = 0x60
PALETTE_OFFSET = 0x00800
PALETTE_SIZE = 0x400
OAM_OFFSET = 0x00C00
OAM_SIZE = 0x400
VRAM_OFFSET = 0x01000
VRAM_SIZE = 0x18000


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("savestates", nargs="+", type=Path)
    parser.add_argument("--out-root", type=Path, default=DEFAULT_OUT_ROOT)
    parser.add_argument(
        "--case-prefix",
        default="current_review_ss",
        help="Output directory prefix. Slot number is appended, e.g. current_review_ss1.",
    )
    return parser.parse_args()


def png_chunk(kind: bytes, payload: bytes) -> bytes:
    return (
        struct.pack(">I", len(payload))
        + kind
        + payload
        + struct.pack(">I", binascii.crc32(kind + payload) & 0xFFFFFFFF)
    )


def iter_png_chunks(data: bytes):
    if not data.startswith(PNG_SIGNATURE):
        raise ValueError("savestate is not a PNG-backed mGBA state")
    pos = len(PNG_SIGNATURE)
    while pos + 8 <= len(data):
        length = struct.unpack(">I", data[pos : pos + 4])[0]
        kind = data[pos + 4 : pos + 8]
        payload_start = pos + 8
        payload_end = payload_start + length
        crc_end = payload_end + 4
        if crc_end > len(data):
            raise ValueError(f"truncated PNG chunk {kind!r}")
        yield kind, data[payload_start:payload_end]
        pos = crc_end
        if kind == b"IEND":
            break


def clean_screenshot_png(chunks: list[tuple[bytes, bytes]]) -> bytes:
    keep = []
    for kind, payload in chunks:
        if kind in (STATE_CHUNK, EXTRA_CHUNK):
            continue
        keep.append(png_chunk(kind, payload))
        if kind == b"IEND":
            break
    return PNG_SIGNATURE + b"".join(keep)


def state_slot(path: Path) -> int:
    match = re.search(r"\.ss(\d+)$", path.name)
    if match:
        return int(match.group(1))
    digits = re.findall(r"(\d+)", path.stem)
    return int(digits[-1]) if digits else 0


def decode_oam(oam: bytes) -> list[dict]:
    entries = []
    for index in range(128):
        base = index * 8
        attr0, attr1, attr2 = struct.unpack_from("<HHH", oam, base)
        x = attr1 & 0x1FF
        y = attr0 & 0xFF
        if x >= 256:
            x -= 512
        if y >= 160:
            y -= 256
        entries.append(
            {
                "index": index,
                "x": x,
                "y": y,
                "tile": attr2 & 0x3FF,
                "palette": (attr2 >> 12) & 0xF,
                "attr0": attr0,
                "attr1": attr1,
                "attr2": attr2,
            }
        )
    return entries


def extract_one(savestate: Path, out_root: Path, case_prefix: str) -> dict:
    data = savestate.read_bytes()
    chunks = list(iter_png_chunks(data))
    state_payload = next((payload for kind, payload in chunks if kind == STATE_CHUNK), None)
    if state_payload is None:
        raise ValueError(f"missing {STATE_CHUNK.decode()} chunk: {savestate}")
    state = zlib.decompress(state_payload)
    if len(state) != GBA_STATE_SIZE:
        raise ValueError(f"unexpected GBA state size {len(state):#x}: {savestate}")

    slot = state_slot(savestate)
    case_id = f"{case_prefix}{slot}"
    frame = f"frame_{slot:06d}"
    out_dir = out_root / case_id
    out_dir.mkdir(parents=True, exist_ok=True)

    (out_dir / f"{frame}.png").write_bytes(clean_screenshot_png(chunks))
    (out_dir / f"{frame}_vram_06000000.bin").write_bytes(state[VRAM_OFFSET : VRAM_OFFSET + VRAM_SIZE])
    (out_dir / f"{frame}_palette_05000000.bin").write_bytes(state[PALETTE_OFFSET : PALETTE_OFFSET + PALETTE_SIZE])
    (out_dir / f"{frame}_ioreg_04000000.bin").write_bytes(state[IO_OFFSET : IO_OFFSET + IO_DUMP_SIZE])
    (out_dir / f"{frame}_oam_07000000.json").write_text(
        json.dumps(decode_oam(state[OAM_OFFSET : OAM_OFFSET + OAM_SIZE]), ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    info = {
        "source_savestate": str(savestate.resolve()),
        "case_id": case_id,
        "frame": frame,
        "state_size": len(state),
        "extraction": "direct_mgba_png_gbAs",
    }
    (out_dir / f"{frame}_info.json").write_text(
        json.dumps(info, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    return {
        "case_id": case_id,
        "frame": frame,
        "out_dir": str(out_dir.relative_to(ROOT)),
        "screenshot": str((out_dir / f"{frame}.png").relative_to(ROOT)),
    }


def main() -> int:
    args = parse_args()
    out_root = args.out_root.resolve()
    results = []
    for savestate in args.savestates:
        results.append(extract_one(savestate.resolve(), out_root, args.case_prefix))
    for result in results:
        print(f"{result['case_id']}: {result['screenshot']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
