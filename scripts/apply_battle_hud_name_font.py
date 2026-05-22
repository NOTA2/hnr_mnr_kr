#!/usr/bin/env python3
"""Apply Korean battle HUD names without touching the shared text font.

The first implementation tried to place Hangul into the English HUD LZ77 block
at 0x00534874. That block is shared by field/dialogue/menu UI, so overwriting
its slots corrupts unrelated screens. This safe pass uses only the battle-name
raw mini-font resource at 0x00186C34 and rewrites resource 0x0933 name strings
to point at those mini-font slots.
"""

from __future__ import annotations

import argparse
import json
import shutil
import struct
import sys
from datetime import datetime
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
VENDOR = ROOT / ".vendor"
if VENDOR.exists() and str(VENDOR) not in sys.path:
    sys.path.insert(0, str(VENDOR))

try:
    from PIL import Image, ImageDraw, ImageFont
except Exception as exc:  # pragma: no cover
    raise SystemExit(f"error: Pillow is required: {exc}")


DEFAULT_TARGET = ROOT / "patched_roms" / "current_review" / "hnr_localization_review.gba"
DEFAULT_ATLAS = ROOT / "third_party" / "font_atlases" / "finalists" / "Galmuri7_9x9_no_shadow.png"
NAME_TABLE_JSON = ROOT / "confirmed_data" / "font_assets" / "battle_hud_name_table.json"
REPORT_PATH = ROOT / "confirmed_data" / "font_assets" / "battle_hud_name_font_apply_report.json"
MAPPING_PATH = ROOT / "confirmed_data" / "font_assets" / "battle_hud_name_hangul_tile_map.json"
PREVIEW_PATH = ROOT / "confirmed_data" / "font_assets" / "battle_hud_name_hangul_slots_preview.png"

RESOURCE_TABLE = 0x0017785C
RESOURCE_INDEX = 0x0933
RECORD_SIZE = 0x1A
BATTLE_FONT_TABLE_ENTRY = 0x0017789C
BATTLE_FONT_OFFSET = 0x00186C34
BATTLE_FONT_SIZE = 0x0F00
BATTLE_FONT_TILE_COUNT = BATTLE_FONT_SIZE // 32
HANGUL_BASE = 0xAC00
HANGUL_END = 0xD7A3

# Keep the main translation table intact, but use a few shorter HUD-only labels
# so the full name set fits in the battle mini-font's addressable slots.
HUD_TEXT_OVERRIDES = {
    "ゴウトウ": "도적",
    "サンゾク": "도적",
    "シシオウ": "사왕",
    "ゴーゴンリップ": "고르곤",
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--target", type=Path, default=DEFAULT_TARGET)
    parser.add_argument("--atlas", type=Path, default=DEFAULT_ATLAS)
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--no-backup", action="store_true")
    parser.add_argument("--cell-size", type=int, default=9)
    parser.add_argument("--glyph-size", type=int, default=8)
    parser.add_argument("--columns", type=int, default=64)
    return parser.parse_args()


def rel(path: Path | None) -> str | None:
    if path is None:
        return None
    try:
        return str(path.relative_to(ROOT))
    except ValueError:
        return str(path)


def is_hangul_syllable(char: str) -> bool:
    return len(char) == 1 and HANGUL_BASE <= ord(char) <= HANGUL_END


def normalize_hud_name(text: str) -> str:
    return "".join(char for char in text.strip() if char != " ")


def load_name_table() -> dict[str, Any]:
    if not NAME_TABLE_JSON.exists():
        raise SystemExit(f"error: missing name table report: {NAME_TABLE_JSON}")
    return json.loads(NAME_TABLE_JSON.read_text(encoding="utf-8"))


def read_resource_entry(rom: bytes, index: int) -> tuple[int, int]:
    table_offset = RESOURCE_TABLE + index * 8
    rom_address, length = struct.unpack_from("<II", rom, table_offset)
    return rom_address - 0x08000000, length


def battle_font_entry_matches(rom: bytes) -> bool:
    rom_address, length = struct.unpack_from("<II", rom, BATTLE_FONT_TABLE_ENTRY)
    return rom_address == 0x08000000 + BATTLE_FONT_OFFSET and length == BATTLE_FONT_SIZE


def direct_slot_codes() -> list[tuple[int, bytes, str]]:
    # The mini-font renderer maps normal bytes as tile = byte - 0xA2. Bytes
    # 0xDE/0xDF are reserved dakuten markers, so 0xA2-0xDD and 0xE0-0xFF are
    # direct-addressable. The 0xE0-0xFF range is how the English patch encodes
    # extra HUD-name letters.
    return [
        *[(byte - 0xA2, bytes([byte]), f"direct 0x{byte:02X}") for byte in range(0xA2, 0xDE)],
        *[(byte - 0xA2, bytes([byte]), f"direct 0x{byte:02X}") for byte in range(0xE0, 0x100)],
    ]


def combo_slot_codes() -> list[tuple[int, bytes, str]]:
    # Confirmed Japanese voiced/semi-voiced composition slots. These add seven
    # extra slots that are not reachable through a direct byte.
    return [
        (61, bytes([0xB3, 0xDE]), "ウ+dakuten"),
        (94, bytes([0xCE, 0xDF]), "ホ+handakuten"),
        (100, bytes([0xCA, 0xDE]), "ハ+dakuten"),
        (101, bytes([0xCB, 0xDE]), "ヒ+dakuten"),
        (102, bytes([0xCC, 0xDE]), "フ+dakuten"),
        (103, bytes([0xCD, 0xDE]), "ヘ+dakuten"),
        (104, bytes([0xCE, 0xDE]), "ホ+dakuten"),
    ]


def available_slot_codes() -> list[tuple[int, bytes, str]]:
    entries = direct_slot_codes() + combo_slot_codes()
    seen_slots: set[int] = set()
    unique = []
    for slot, code, note in entries:
        if not (0 <= slot < BATTLE_FONT_TILE_COUNT):
            continue
        if slot in seen_slots:
            continue
        seen_slots.add(slot)
        unique.append((slot, code, note))
    return unique


def hud_text_for_record(record: dict[str, Any]) -> str:
    source = str(record.get("decoded_name") or "")
    if source == "ヌル":
        # Keep the null/placeholder entry untouched. It is not meant to be a
        # visible battle label and otherwise costs a scarce Hangul slot.
        return ""
    return normalize_hud_name(HUD_TEXT_OVERRIDES.get(source, str(record.get("korean_translation") or source)))


def build_hangul_mapping(records: list[dict[str, Any]]) -> tuple[dict[str, dict[str, Any]], list[dict[str, Any]]]:
    chars = sorted({char for record in records for char in hud_text_for_record(record) if is_hangul_syllable(char)})
    slots = available_slot_codes()
    if len(chars) > len(slots):
        raise SystemExit(f"error: not enough battle mini-font slots: {len(chars)} > {len(slots)}")
    mapping: dict[str, dict[str, Any]] = {}
    entries = []
    for char, (slot, code, note) in zip(chars, slots):
        item = {
            "char": char,
            "slot": slot,
            "slot_hex": f"0x{slot:02X}",
            "encoded_hex": code.hex(),
            "encoding_note": note,
        }
        mapping[char] = item
        entries.append(item)
    return mapping, entries


def glyph_tile_from_atlas(
    atlas: Image.Image,
    char: str,
    *,
    cell_size: int,
    glyph_size: int,
    columns: int,
) -> bytes:
    index = ord(char) - HANGUL_BASE
    if index < 0 or ord(char) > HANGUL_END:
        raise ValueError(f"not a Hangul syllable: {char}")
    x = (index % columns) * cell_size
    y = (index // columns) * cell_size
    tile = atlas.crop((x, y, x + glyph_size, y + glyph_size)).convert("RGBA")
    pixels = tile.load()
    out = bytearray()
    for py in range(glyph_size):
        for px in range(0, glyph_size, 2):
            packed = 0
            for dx in (0, 1):
                r, g, b, a = pixels[px + dx, py]
                luminance = (r * 299 + g * 587 + b * 114) // 1000
                # The Galmuri atlas used here is black-background, white-ink.
                # Use only the bright pixels as glyph ink; the black cell
                # background must stay transparent in the GBA tile.
                value = 0x01 if a >= 32 and luminance >= 240 else 0x00
                packed |= value << (dx * 4)
            out.append(packed)
    return bytes(out)


def patch_battle_font(
    rom: bytearray,
    mapping: dict[str, dict[str, Any]],
    atlas_path: Path,
    *,
    cell_size: int,
    glyph_size: int,
    columns: int,
) -> bytes:
    if not battle_font_entry_matches(bytes(rom)):
        raise SystemExit("error: battle mini-font resource entry no longer matches the expected raw block")
    font = bytearray(rom[BATTLE_FONT_OFFSET : BATTLE_FONT_OFFSET + BATTLE_FONT_SIZE])
    atlas = Image.open(atlas_path).convert("RGBA")
    for char, entry in mapping.items():
        slot = int(entry["slot"])
        font[slot * 32 : slot * 32 + 32] = glyph_tile_from_atlas(
            atlas,
            char,
            cell_size=cell_size,
            glyph_size=glyph_size,
            columns=columns,
        )
    rom[BATTLE_FONT_OFFSET : BATTLE_FONT_OFFSET + BATTLE_FONT_SIZE] = font
    return bytes(font)


def encode_hud_text(text: str, mapping: dict[str, dict[str, Any]]) -> bytes:
    out = bytearray()
    for char in text:
        if is_hangul_syllable(char):
            out.extend(bytes.fromhex(str(mapping[char]["encoded_hex"])))
        elif char.isascii() and char.isdigit():
            out.append(ord(char))
        else:
            raise SystemExit(f"error: unsupported HUD-name character: {char!r} in {text!r}")
    if not out or 0 in out:
        raise SystemExit(f"error: invalid encoded HUD text: {text!r}")
    return bytes(out)


def read_c_string(data: bytes, offset: int) -> bytes:
    end = offset
    while end < len(data) and data[end] != 0:
        end += 1
    return data[offset:end]


def patch_name_resource(
    rom: bytearray,
    records: list[dict[str, Any]],
    mapping: dict[str, dict[str, Any]],
) -> dict[str, Any]:
    resource_offset, resource_length = read_resource_entry(bytes(rom), RESOURCE_INDEX)
    resource = bytearray(rom[resource_offset : resource_offset + resource_length])
    record_count = len(records)
    string_cursor = record_count * RECORD_SIZE
    encoded_offsets: dict[bytes, int] = {}
    applied_records = []

    for record in records:
        record_index = int(record["record_index"])
        source = str(record.get("decoded_name") or "")
        hud_text = hud_text_for_record(record)
        if not hud_text:
            # Keep the null placeholder non-visible without spending a Hangul
            # slot. Allocate a fresh empty C string so later rewritten strings
            # cannot accidentally change what this pointer sees.
            empty = b""
            if empty not in encoded_offsets:
                if string_cursor + 1 > resource_length:
                    raise SystemExit("error: no room for empty HUD placeholder")
                encoded_offsets[empty] = string_cursor
                resource[string_cursor] = 0
                string_cursor += 1
            name_rel = encoded_offsets[empty]
            struct.pack_into("<H", resource, record_index * RECORD_SIZE + 1, name_rel)
            applied_records.append(
                {
                    "record_index": record_index,
                    "source": source,
                    "hud_text": "",
                    "empty_placeholder": True,
                    "encoded_hex": "",
                    "name_rel": name_rel,
                    "name_rel_hex": f"0x{name_rel:04X}",
                }
            )
            continue

        encoded = encode_hud_text(hud_text, mapping)
        if encoded not in encoded_offsets:
            required = len(encoded) + 1
            if string_cursor + required > resource_length:
                raise SystemExit(
                    f"error: encoded HUD names exceed resource 0x{RESOURCE_INDEX:04X}: "
                    f"need 0x{string_cursor + required:04X}, have 0x{resource_length:04X}"
                )
            encoded_offsets[encoded] = string_cursor
            resource[string_cursor : string_cursor + len(encoded)] = encoded
            resource[string_cursor + len(encoded)] = 0
            string_cursor += required
        name_rel = encoded_offsets[encoded]
        struct.pack_into("<H", resource, record_index * RECORD_SIZE + 1, name_rel)
        applied_records.append(
            {
                "record_index": record_index,
                "source": source,
                "korean_translation": record.get("korean_translation"),
                "hud_text": hud_text,
                "used_hud_override": source in HUD_TEXT_OVERRIDES,
                "encoded_hex": encoded.hex(),
                "name_rel": name_rel,
                "name_rel_hex": f"0x{name_rel:04X}",
            }
        )

    if string_cursor < resource_length:
        resource[string_cursor:] = bytes(resource_length - string_cursor)
    rom[resource_offset : resource_offset + resource_length] = resource
    return {
        "resource_index": f"0x{RESOURCE_INDEX:04X}",
        "resource_offset": resource_offset,
        "resource_offset_hex": f"0x{resource_offset:08X}",
        "resource_length": resource_length,
        "resource_length_hex": f"0x{resource_length:04X}",
        "record_count": record_count,
        "deduped_korean_string_count": len(encoded_offsets),
        "used_string_bytes": string_cursor - record_count * RECORD_SIZE,
        "free_resource_bytes": resource_length - string_cursor,
        "records": applied_records,
    }


def render_mapping_preview(mapping_entries: list[dict[str, Any]], font: bytes) -> None:
    cols = 16
    cell = 46
    rows = max(1, (len(mapping_entries) + cols - 1) // cols)
    out = Image.new("RGB", (cols * cell, rows * cell), (20, 20, 20))
    draw = ImageDraw.Draw(out)
    try:
        font_label = ImageFont.truetype("/System/Library/Fonts/Monaco.ttf", 8)
    except Exception:
        font_label = None
    for index, entry in enumerate(mapping_entries):
        slot = int(entry["slot"])
        raw = font[slot * 32 : slot * 32 + 32]
        tile = Image.new("L", (8, 8), 0)
        pixels = tile.load()
        for y in range(8):
            for pair, byte in enumerate(raw[y * 4 : y * 4 + 4]):
                pixels[pair * 2, y] = (byte & 0x0F) * 255
                pixels[pair * 2 + 1, y] = ((byte >> 4) & 0x0F) * 255
        big = tile.resize((24, 24), Image.Resampling.NEAREST).convert("RGB")
        x = (index % cols) * cell
        y = (index // cols) * cell
        draw.text((x + 2, y + 2), f"{slot:02X} {entry['char']}", fill=(245, 225, 90), font=font_label)
        out.paste(big, (x + 10, y + 17))
    PREVIEW_PATH.parent.mkdir(parents=True, exist_ok=True)
    out.save(PREVIEW_PATH)


def main() -> int:
    args = parse_args()
    target = args.target if args.target.is_absolute() else ROOT / args.target
    atlas = args.atlas if args.atlas.is_absolute() else ROOT / args.atlas
    if not target.exists():
        raise SystemExit(f"error: target ROM not found: {target}")
    if not atlas.exists():
        raise SystemExit(f"error: atlas not found: {atlas}")

    table = json.loads(NAME_TABLE_JSON.read_text(encoding="utf-8"))
    records = table.get("records")
    if not isinstance(records, list) or not records:
        raise SystemExit("error: battle HUD name table report has no records")

    mapping, mapping_entries = build_hangul_mapping(records)
    rom = bytearray(target.read_bytes())
    font = patch_battle_font(
        rom,
        mapping,
        atlas,
        cell_size=args.cell_size,
        glyph_size=args.glyph_size,
        columns=args.columns,
    )
    name_report = patch_name_resource(rom, records, mapping)
    render_mapping_preview(mapping_entries, font)

    report = {
        "target": rel(target),
        "atlas": rel(atlas),
        "dry_run": args.dry_run,
        "timestamp": datetime.now().isoformat(timespec="seconds"),
        "cause_of_previous_bad_patch": (
            "0x00534874 is shared by field/dialogue/menu UI; this pass leaves that block untouched."
        ),
        "battle_font_offset": BATTLE_FONT_OFFSET,
        "battle_font_offset_hex": f"0x{BATTLE_FONT_OFFSET:08X}",
        "battle_font_size": BATTLE_FONT_SIZE,
        "battle_font_tile_count": BATTLE_FONT_TILE_COUNT,
        "hangul_glyph_count": len(mapping_entries),
        "available_slot_count": len(available_slot_codes()),
        "hud_text_overrides": HUD_TEXT_OVERRIDES,
        "name_resource": name_report,
        "mapping_path": rel(MAPPING_PATH),
        "preview_path": rel(PREVIEW_PATH),
    }

    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    MAPPING_PATH.write_text(json.dumps(mapping_entries, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    REPORT_PATH.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    backup_path = None
    if not args.dry_run:
        if not args.no_backup:
            backup_path = target.with_name(f"{target.stem}.before_safe_battle_hud_name_font{target.suffix}")
            if not backup_path.exists():
                shutil.copy2(target, backup_path)
        target.write_bytes(rom)

    print(json.dumps({**report, "backup": rel(backup_path)}, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
