#!/usr/bin/env python3
"""Patch Korean status-name glyphs into confirmed name-only HUD slots.

The 0x00534874 block also contains shared small UI glyphs, so only the
confirmed name ranges are safe to modify:

- 0xAA-0xBE: Ed / Al / Mustang / Hawkeye
- 0xCA-0xDD: Armstrong / Martins / Cony

Do not touch 0xA0-0xA9; those slots are shared elsewhere.
"""

from __future__ import annotations

import argparse
import json
import shutil
import sys
from datetime import datetime
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
VENDOR = ROOT / ".vendor"
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
if VENDOR.exists() and str(VENDOR) not in sys.path:
    sys.path.insert(0, str(VENDOR))

try:
    from PIL import Image, ImageDraw, ImageFont
except Exception as exc:  # pragma: no cover
    raise SystemExit(f"error: Pillow is required: {exc}")

from gba_kor_tool.cli import decompress_lz77
from scripts.apply_image_replacements import compress_lz77


DEFAULT_TARGET = ROOT / "patched_roms" / "current_review" / "hnr_localization_review.gba"
DEFAULT_ATLAS = ROOT / "third_party" / "font_atlases" / "finalists" / "Galmuri7_9x9.png"
OFFSET = 0x00534874
EXPECTED_DECOMPRESSED_SIZE = 0x2000
HANGUL_BASE = 0xAC00
OUT_DIR = ROOT / "confirmed_data" / "font_assets"
REPORT_PATH = OUT_DIR / "common_hud_korean_slot_patch_report.json"
PREVIEW_PATH = OUT_DIR / "common_hud_korean_slot_patch_preview.png"


BACKGROUND_NIBBLE = 0x0D
SHADOW_NIBBLE = 0x01
INK_NIBBLE = 0x0F

ALLOWED_SLOT_RANGES = [(0xAA, 0xBE), (0xCA, 0xDD)]

NAME_SLOT_GROUPS = [
    {"slot": 0xAA, "slot_count": 5, "source": "Ed", "text": "에드"},
    {"slot": 0xAF, "slot_count": 6, "source": "Al", "text": "알"},
    {"slot": 0xB5, "slot_count": 5, "source": "Mustang", "text": "머스탱"},
    {"slot": 0xBA, "slot_count": 5, "source": "Hawkeye", "text": "호크아이"},
    {"slot": 0xCA, "slot_count": 8, "source": "ARMSTRONG", "text": "암스트롱"},
    {"slot": 0xD2, "slot_count": 6, "source": "Martins", "text": "마틴스"},
    {"slot": 0xD8, "slot_count": 6, "source": "Cony", "text": "코니"},
]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--target", type=Path, default=DEFAULT_TARGET)
    parser.add_argument("--atlas", type=Path, default=DEFAULT_ATLAS)
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--no-backup", action="store_true")
    return parser.parse_args()


def rel(path: Path | None) -> str | None:
    if path is None:
        return None
    try:
        return str(path.relative_to(ROOT))
    except ValueError:
        return str(path)


def blank_status_tile() -> bytes:
    return bytes([BACKGROUND_NIBBLE | (BACKGROUND_NIBBLE << 4)] * 32)


def slot_is_allowed(slot: int) -> bool:
    return any(start <= slot <= end for start, end in ALLOWED_SLOT_RANGES)


def glyph_tile(atlas: Image.Image, char: str) -> bytes:
    index = ord(char) - HANGUL_BASE
    if index < 0:
        raise ValueError(f"not Hangul: {char}")
    x = (index % 64) * 9
    y = (index // 64) * 9
    tile = atlas.crop((x, y, x + 8, y + 8)).convert("RGBA")
    pixels = tile.load()
    out = bytearray()
    for py in range(8):
        for px in range(0, 8, 2):
            packed = 0
            for dx in (0, 1):
                r, g, b, a = pixels[px + dx, py]
                luminance = (r * 299 + g * 587 + b * 114) // 1000
                if a < 32 or luminance < 16:
                    value = BACKGROUND_NIBBLE
                elif luminance >= 240:
                    value = INK_NIBBLE
                else:
                    value = SHADOW_NIBBLE
                packed |= value << (dx * 4)
            out.append(packed)
    return bytes(out)


def render_preview(payload: bytes) -> None:
    slots: list[tuple[int, str]] = []
    for group in NAME_SLOT_GROUPS:
        start = int(group["slot"])
        text = str(group["text"])
        for index in range(int(group["slot_count"])):
            label = text[index] if index < len(text) else ""
            slots.append((start + index, label))

    cols = 16
    cell = 48
    rows = (len(slots) + cols - 1) // cols
    out = Image.new("RGB", (cols * cell, max(1, rows) * cell), (20, 20, 20))
    preview_palette = {
        0x0: (0, 0, 0),
        SHADOW_NIBBLE: (32, 32, 32),
        BACKGROUND_NIBBLE: (200, 0, 0),
        INK_NIBBLE: (248, 248, 248),
    }
    draw = ImageDraw.Draw(out)
    try:
        label_font = ImageFont.truetype("/System/Library/Fonts/Monaco.ttf", 8)
    except Exception:
        label_font = None
    for index, (slot, label) in enumerate(slots):
        raw = payload[slot * 32 : slot * 32 + 32]
        tile = Image.new("L", (8, 8), 0)
        pix = tile.load()
        for y in range(8):
            for pair, byte in enumerate(raw[y * 4 : y * 4 + 4]):
                pix[pair * 2, y] = (byte & 0x0F) * 17
                pix[pair * 2 + 1, y] = ((byte >> 4) & 0x0F) * 17
        x = (index % cols) * cell
        y = (index // cols) * cell
        big = tile.resize((32, 32), Image.Resampling.NEAREST).convert("RGB")
        big_pixels = big.load()
        for py in range(big.height):
            for px in range(big.width):
                gray = big_pixels[px, py][0]
                nibble = gray // 17
                big_pixels[px, py] = preview_palette.get(nibble, (gray, gray, gray))
        out.paste(big, (x + 8, y + 12))
        draw.text((x + 2, y + 2), f"{slot:02X} {label}", fill=(245, 225, 90), font=label_font)
    PREVIEW_PATH.parent.mkdir(parents=True, exist_ok=True)
    out.save(PREVIEW_PATH)


def main() -> int:
    args = parse_args()
    target = args.target if args.target.is_absolute() else ROOT / args.target
    atlas_path = args.atlas if args.atlas.is_absolute() else ROOT / args.atlas
    if not target.exists():
        raise SystemExit(f"error: target ROM not found: {target}")
    if not atlas_path.exists():
        raise SystemExit(f"error: atlas not found: {atlas_path}")

    rom = bytearray(target.read_bytes())
    original_payload, consumed = decompress_lz77(
        bytes(rom),
        OFFSET,
        max_output_size=EXPECTED_DECOMPRESSED_SIZE + 0x1000,
    )
    if len(original_payload) != EXPECTED_DECOMPRESSED_SIZE:
        raise SystemExit(f"error: unexpected decompressed size: {len(original_payload)}")
    atlas = Image.open(atlas_path).convert("RGBA")
    patched_payload = bytearray(original_payload)
    patched_groups = []
    for group in NAME_SLOT_GROUPS:
        start = int(group["slot"])
        slot_count = int(group["slot_count"])
        text = str(group["text"])
        touched_slots = range(start, start + slot_count)
        outside = [slot for slot in touched_slots if not slot_is_allowed(slot)]
        if outside:
            raise SystemExit(
                "error: refused to patch outside confirmed name slots: "
                + ", ".join(f"0x{slot:02X}" for slot in outside)
            )
        if len(text) > slot_count:
            raise SystemExit(f"error: {text!r} does not fit in {slot_count} slots at 0x{start:02X}")
        for index in range(slot_count):
            slot = start + index
            tile = glyph_tile(atlas, text[index]) if index < len(text) else blank_status_tile()
            patched_payload[slot * 32 : slot * 32 + 32] = tile
        patched_groups.append(
            {
                "source": group["source"],
                "text": text,
                "start_slot": f"0x{start:02X}",
                "slot_count": slot_count,
                "used_slots": [f"0x{start + index:02X}" for index in range(len(text))],
                "cleared_slots": [f"0x{start + index:02X}" for index in range(len(text), slot_count)],
            }
        )

    compressed = compress_lz77(bytes(patched_payload))
    if len(compressed) > consumed:
        raise SystemExit(f"error: compressed patch does not fit: {len(compressed)} > {consumed}")
    render_preview(bytes(patched_payload))

    backup_path = None
    if not args.dry_run:
        if not args.no_backup:
            backup_path = target.with_name(f"{target.stem}.before_common_hud_korean_slots{target.suffix}")
            if not backup_path.exists():
                shutil.copy2(target, backup_path)
        rom[OFFSET : OFFSET + len(compressed)] = compressed
        # Keep stale tail bytes harmless by leaving the old tail in place; GBA
        # LZ77 decode stops after the new stream's declared output length.
        verify, _ = decompress_lz77(bytes(rom), OFFSET, max_output_size=EXPECTED_DECOMPRESSED_SIZE + 0x1000)
        if verify != bytes(patched_payload):
            raise SystemExit("error: verification failed after patch")
        target.write_bytes(rom)

    report = {
        "target": rel(target),
        "atlas": rel(atlas_path),
        "offset": OFFSET,
        "offset_hex": f"0x{OFFSET:08X}",
        "dry_run": args.dry_run,
        "timestamp": datetime.now().isoformat(timespec="seconds"),
        "status_name_slot_groups": patched_groups,
        "allowed_slot_ranges": [f"0x{start:02X}-0x{end:02X}" for start, end in ALLOWED_SLOT_RANGES],
        "palette_nibbles": {
            "background": f"0x{BACKGROUND_NIBBLE:X}",
            "shadow": f"0x{SHADOW_NIBBLE:X}",
            "ink": f"0x{INK_NIBBLE:X}",
        },
        "existing_compressed_size": consumed,
        "new_compressed_size": len(compressed),
        "fits_in_place": len(compressed) <= consumed,
        "backup": rel(backup_path),
        "preview_path": rel(PREVIEW_PATH),
    }
    REPORT_PATH.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
