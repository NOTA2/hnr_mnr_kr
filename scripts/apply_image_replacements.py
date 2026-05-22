#!/usr/bin/env python3
"""Apply uploaded image replacements to a review ROM.

The GUI only records which edited PNG the user uploaded. This script owns the
ROM-facing conversion: edited review PNG -> 4bpp tile payload -> ROM image block.
Most exposed UI fragments are compressed GBA RLE/LZ77 blocks, but some battle
command wordmarks are raw 4bpp tile blocks copied directly into VRAM.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
if str(ROOT / "scripts") not in sys.path:
    sys.path.insert(0, str(ROOT / "scripts"))
if str(ROOT / ".vendor") not in sys.path:
    sys.path.append(str(ROOT / ".vendor"))

from PIL import Image

from gba_kor_tool.cli import decompress_lz77
from extract_rle_image_tiles import decompress_gba_rle
from registry_b_zp import (
    ZPCodecError,
    compress_zp_resource,
    decompress_zp_resource,
    gba_pointer_to_file_offset,
)
from render_runtime_tilemaps import read_palette


DEFAULT_ROM = ROOT / "patched_roms/current_review/hnr_localization_review.gba"
FALLBACK_ROM = ROOT / "patched_roms/current_review/hnr_localization_review_no_entry8_stable.gba"
DEFAULT_IMAGE_REPLACEMENTS = ROOT / "confirmed_data/localization_workbench/image_replacements.json"
DEFAULT_REPORT = ROOT / "confirmed_data/localization_workbench/image_apply_report.json"
DEFAULT_RLE_REPORT = ROOT / "confirmed_data/image_inventory/rle_tile_extraction/notes/rle_tile_extraction_report.json"
TILE_BYTES = 32
GBA_ROM_BASE = 0x08000000
GBA_MAX_ROM_SIZE = 0x02000000
REPOINT_ALIGNMENT = 4
REFERENCE_CAPACITY_ROMS = [
    ROOT / "patched_roms/current_review/current_review_font_ready.gba",
    ROOT / "Hagane no Renkinjutsushi - Meisou no Rondo (Japan).gba",
]
LZ77_STABILITY_REFERENCE_ROMS = [
    ("jp", ROOT / "Hagane no Renkinjutsushi - Meisou no Rondo (Japan).gba"),
    (
        "en",
        ROOT
        / "local_roms"
        / "english_patched"
        / "Fullmetal Alchemist Stray Rondo (English Patched v0.02).gba",
    ),
]
FIELD_LABEL_ARCHIVE_DATA_BASE = 0x00427688
FIELD_LABEL_LZ77_TABLE_REPOINTS = {
    0x005323AC: {"name": "field_alchemy_label", "table_offset": 0x00420168},
    0x0053257C: {"name": "field_item_label", "table_offset": 0x0042016C},
    0x00532764: {"name": "field_status_label", "table_offset": 0x00420170},
    0x0053293C: {"name": "field_save_label", "table_offset": 0x00420174},
}
COMMON_HUD_TILE_LZ77_OFFSET = 0x00534874
COMMON_HUD_RESERVED_TILE_INDEXES = {0x000}
COMMON_HUD_ZERO_TO_SHADOW_TILE_RANGES = ((0x0AA, 0x0BD), (0x0CA, 0x0D9))


OFFSET_RE = re.compile(r"(?:^|[:_])(?P<offset>[0-9A-Fa-f]{8})(?:$|[_:])")
COLS_RE = re.compile(r"_(?P<cols>\d+)cols(?:_|\\.)")
TILE_INDEX_RE = re.compile(r"(?:tile|slot|idx)[_:]?(?P<tile>[0-9A-Fa-f]{2,3})", re.IGNORECASE)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--rom", type=Path, default=DEFAULT_ROM)
    parser.add_argument("--image-replacements", type=Path, default=DEFAULT_IMAGE_REPLACEMENTS)
    parser.add_argument("--item-id", action="append", default=[], help="Optional image item id filter. May be repeated.")
    parser.add_argument("--report", type=Path, default=DEFAULT_REPORT)
    return parser.parse_args()


def compress_gba_rle(payload: bytes) -> bytes:
    if not (0 < len(payload) <= 0xFFFFFF):
        raise ValueError(f"invalid RLE payload size: {len(payload)}")
    # Dynamic programming avoids near-miss failures where a greedy encoder is a
    # few bytes larger than the game's original RLE block.
    n = len(payload)
    run_lengths = [1] * n
    for i in range(n - 2, -1, -1):
        if payload[i] == payload[i + 1]:
            run_lengths[i] = min(130, run_lengths[i + 1] + 1)

    inf = 1 << 60
    dp = [inf] * (n + 1)
    choices: list[tuple[str, int] | None] = [None] * n
    dp[n] = 0
    for i in range(n - 1, -1, -1):
        max_literal = min(128, n - i)
        for length in range(1, max_literal + 1):
            cost = 1 + length + dp[i + length]
            if cost < dp[i]:
                dp[i] = cost
                choices[i] = ("literal", length)
        max_run = min(130, run_lengths[i])
        for length in range(3, max_run + 1):
            cost = 2 + dp[i + length]
            if cost < dp[i]:
                dp[i] = cost
                choices[i] = ("run", length)

    out = bytearray([0x30, n & 0xFF, (n >> 8) & 0xFF, (n >> 16) & 0xFF])
    cursor = 0
    while cursor < n:
        choice = choices[cursor]
        if choice is None:
            raise ValueError("RLE compression failed to choose a packet")
        kind, length = choice
        if kind == "run":
            out.append(0x80 | (length - 3))
            out.append(payload[cursor])
        else:
            out.append(length - 1)
            out.extend(payload[cursor : cursor + length])
        cursor += length
    return bytes(out)


def lz77_match_index(payload: bytes) -> list[list[tuple[int, int]]]:
    positions_by_key: dict[bytes, list[int]] = {}
    matches: list[list[tuple[int, int]]] = [[] for _ in payload]
    n = len(payload)
    for index in range(n):
        if index + 3 <= n:
            key = payload[index : index + 3]
            candidates = positions_by_key.get(key, [])
            best_by_length: dict[int, int] = {}
            for previous in reversed(candidates[-128:]):
                distance = index - previous
                if not 1 <= distance <= 0x1000:
                    continue
                length = 3
                max_length = min(18, n - index)
                while length < max_length and payload[previous + length] == payload[index + length]:
                    length += 1
                for current_length in range(3, length + 1):
                    best_by_length.setdefault(current_length, distance)
                if length == max_length:
                    break
            matches[index] = sorted(
                ((length, distance) for length, distance in best_by_length.items()),
                reverse=True,
            )
            candidates.append(index)
            if len(candidates) > 512:
                del candidates[: len(candidates) - 512]
            positions_by_key[key] = candidates
    return matches


def compress_lz77(payload: bytes) -> bytes:
    if not (0 < len(payload) <= 0xFFFFFF):
        raise ValueError(f"invalid LZ77 payload size: {len(payload)}")

    n = len(payload)
    matches = lz77_match_index(payload)
    inf = 1 << 60
    dp = [[inf] * 8 for _ in range(n + 1)]
    choices: list[list[tuple[str, int, int] | None]] = [[None] * 8 for _ in range(n)]
    for phase in range(8):
        dp[n][phase] = 0

    for index in range(n - 1, -1, -1):
        for phase in range(8):
            group_cost = 1 if phase == 0 else 0
            next_phase = (phase + 1) % 8
            best_cost = group_cost + 1 + dp[index + 1][next_phase]
            best_choice: tuple[str, int, int] = ("literal", 1, 0)
            for length, distance in matches[index]:
                cost = group_cost + 2 + dp[index + length][next_phase]
                if cost < best_cost:
                    best_cost = cost
                    best_choice = ("match", length, distance)
            dp[index][phase] = best_cost
            choices[index][phase] = best_choice

    tokens: list[tuple[str, bytes]] = []
    index = 0
    phase = 0
    while index < n:
        choice = choices[index][phase]
        if choice is None:
            raise ValueError("LZ77 compression failed to choose a packet")
        kind, length, distance = choice
        if kind == "match":
            disp = distance - 1
            b1 = ((length - 3) << 4) | ((disp >> 8) & 0x0F)
            b2 = disp & 0xFF
            tokens.append((kind, bytes([b1, b2])))
            index += length
        else:
            tokens.append((kind, bytes([payload[index]])))
            index += 1
        phase = (phase + 1) % 8

    out = bytearray([0x10, n & 0xFF, (n >> 8) & 0xFF, (n >> 16) & 0xFF])
    for start in range(0, len(tokens), 8):
        group = tokens[start : start + 8]
        flag = 0
        body = bytearray()
        for bit, (kind, data) in enumerate(group):
            if kind == "match":
                flag |= 0x80 >> bit
            body.extend(data)
        out.append(flag)
        out.extend(body)
    return bytes(out)


def lz77_match_index_preserve_distances(payload: bytes) -> list[list[tuple[int, int]]]:
    """Build matches without discarding alternate distances for the same length."""
    positions_by_key: dict[bytes, list[int]] = {}
    matches: list[list[tuple[int, int]]] = [[] for _ in payload]
    n = len(payload)
    for index in range(n):
        if index + 3 <= n:
            key = payload[index : index + 3]
            candidates = positions_by_key.get(key, [])
            seen: set[tuple[int, int]] = set()
            current_matches: list[tuple[int, int]] = []
            for previous in reversed(candidates[-512:]):
                distance = index - previous
                if not 1 <= distance <= 0x1000:
                    continue
                length = 3
                max_length = min(18, n - index)
                while length < max_length and payload[previous + length] == payload[index + length]:
                    length += 1
                for current_length in range(3, length + 1):
                    candidate = (current_length, distance)
                    if candidate in seen:
                        continue
                    seen.add(candidate)
                    current_matches.append(candidate)
            matches[index] = sorted(current_matches, reverse=True)
            candidates.append(index)
            if len(candidates) > 1024:
                del candidates[: len(candidates) - 1024]
            positions_by_key[key] = candidates
    return matches


def compress_lz77_avoid_distance_one(payload: bytes) -> bytes:
    """Encode LZ77 without encoded displacement zero.

    The 0x00534874 shared HUD block is accepted by the English patch and the
    original game stream, but those streams never use distance=1 references.
    Our optimal encoder emits many of them, which appears to upset this block's
    runtime path even though a normal verifier can decode the stream.
    """
    if not (0 < len(payload) <= 0xFFFFFF):
        raise ValueError(f"invalid LZ77 payload size: {len(payload)}")

    n = len(payload)
    matches = lz77_match_index_preserve_distances(payload)
    inf = 1 << 60
    dp = [[inf] * 8 for _ in range(n + 1)]
    choices: list[list[tuple[str, int, int] | None]] = [[None] * 8 for _ in range(n)]
    for phase in range(8):
        dp[n][phase] = 0

    for index in range(n - 1, -1, -1):
        for phase in range(8):
            group_cost = 1 if phase == 0 else 0
            next_phase = (phase + 1) % 8
            best_cost = group_cost + 1 + dp[index + 1][next_phase]
            best_choice: tuple[str, int, int] = ("literal", 1, 0)
            for length, distance in matches[index]:
                if distance == 1:
                    continue
                cost = group_cost + 2 + dp[index + length][next_phase]
                if cost < best_cost:
                    best_cost = cost
                    best_choice = ("match", length, distance)
            dp[index][phase] = best_cost
            choices[index][phase] = best_choice

    tokens: list[tuple[str, bytes]] = []
    index = 0
    phase = 0
    while index < n:
        choice = choices[index][phase]
        if choice is None:
            raise ValueError("LZ77 compression failed to choose a packet")
        kind, length, distance = choice
        if kind == "match":
            disp = distance - 1
            b1 = ((length - 3) << 4) | ((disp >> 8) & 0x0F)
            b2 = disp & 0xFF
            tokens.append((kind, bytes([b1, b2])))
            index += length
        else:
            tokens.append((kind, bytes([payload[index]])))
            index += 1
        phase = (phase + 1) % 8

    out = bytearray([0x10, n & 0xFF, (n >> 8) & 0xFF, (n >> 16) & 0xFF])
    for start in range(0, len(tokens), 8):
        group = tokens[start : start + 8]
        flag = 0
        body = bytearray()
        for bit, (kind, data) in enumerate(group):
            if kind == "match":
                flag |= 0x80 >> bit
            body.extend(data)
        out.append(flag)
        out.extend(body)
    return bytes(out)


def compress_lz77_literal(payload: bytes) -> bytes:
    """Encode LZ77 using literal packets only.

    The field/menu OBJ labels are decompressed and rearranged by game code that
    is sensitive to some back-reference streams even when our verifier can
    decode them. Literal LZ77 is larger, but repointing makes it reliable.
    """
    if not (0 < len(payload) <= 0xFFFFFF):
        raise ValueError(f"invalid LZ77 payload size: {len(payload)}")
    out = bytearray([0x10, len(payload) & 0xFF, (len(payload) >> 8) & 0xFF, (len(payload) >> 16) & 0xFF])
    for start in range(0, len(payload), 8):
        out.append(0x00)
        out.extend(payload[start : start + 8])
    return bytes(out)


def lz77_distance_stats_from_stream(stream: bytes) -> dict:
    if len(stream) < 4 or stream[0] != 0x10:
        return {"valid": False, "reason": "not a GBA LZ77 stream"}
    output_size = stream[1] | (stream[2] << 8) | (stream[3] << 16)
    if output_size <= 0:
        return {"valid": False, "reason": "invalid output size", "decompressed_size": output_size}

    src = 4
    out = 0
    matches = 0
    literals = 0
    distance_one = 0
    max_distance = 0
    try:
        while out < output_size:
            flags = stream[src]
            src += 1
            for bit in range(8):
                if out >= output_size:
                    break
                if flags & (0x80 >> bit):
                    b1 = stream[src]
                    b2 = stream[src + 1]
                    src += 2
                    length = (b1 >> 4) + 3
                    distance = (((b1 & 0x0F) << 8) | b2) + 1
                    matches += 1
                    if distance == 1:
                        distance_one += 1
                    max_distance = max(max_distance, distance)
                    out += min(length, output_size - out)
                else:
                    src += 1
                    literals += 1
                    out += 1
    except IndexError:
        return {
            "valid": False,
            "reason": "truncated LZ77 stream",
            "decompressed_size": output_size,
            "consumed_size": len(stream),
        }

    return {
        "valid": True,
        "decompressed_size": output_size,
        "consumed_size": src,
        "distance_one_references": distance_one,
        "match_count": matches,
        "literal_count": literals,
        "max_distance": max_distance,
    }


def lz77_distance_stats_from_rom(rom: bytes, offset: int) -> dict | None:
    if offset < 0 or offset >= len(rom) or rom[offset] != 0x10:
        return None
    stats = lz77_distance_stats_from_stream(rom[offset:])
    if not stats.get("valid"):
        return stats
    return stats


def build_lz77_distance_one_check(
    *,
    item_id: str,
    original_offset: int,
    compressed: bytes,
    encoder: str,
) -> dict:
    patched_stats = lz77_distance_stats_from_stream(compressed)
    references: dict[str, dict] = {}
    reference_dist1_values: list[int] = []
    for label, rom_path in LZ77_STABILITY_REFERENCE_ROMS:
        if not rom_path.is_file():
            references[label] = {"available": False, "path": str(rom_path.relative_to(ROOT))}
            continue
        stats = lz77_distance_stats_from_rom(rom_path.read_bytes(), original_offset)
        if stats is None:
            references[label] = {"available": False, "path": str(rom_path.relative_to(ROOT))}
            continue
        public_stats = dict(stats)
        public_stats["available"] = bool(stats.get("valid"))
        references[label] = public_stats
        if stats.get("valid"):
            reference_dist1_values.append(int(stats.get("distance_one_references", 0)))

    patched_dist1 = int(patched_stats.get("distance_one_references", 0)) if patched_stats.get("valid") else None
    reference_has_dist1 = any(value > 0 for value in reference_dist1_values)
    reference_all_zero = bool(reference_dist1_values) and not reference_has_dist1
    warning = patched_dist1 is not None and patched_dist1 > 0 and reference_all_zero
    return {
        "kind": "lz77_distance_one",
        "item_id": item_id,
        "offset_hex": f"0x{original_offset:08X}",
        "encoder": encoder,
        "status": "warning" if warning else "ok",
        "warning": (
            "patched stream introduced distance=1 references while available JP/EN reference streams have none"
            if warning
            else ""
        ),
        "patched": patched_stats,
        "references": references,
    }


def summarize_lz77_stability_checks(results: list[dict]) -> dict:
    checks = [result["lz77_stability"] for result in results if result.get("lz77_stability")]
    warnings = [
        {
            "item_id": check.get("item_id"),
            "offset_hex": check.get("offset_hex"),
            "encoder": check.get("encoder"),
            "warning": check.get("warning"),
            "patched_distance_one_references": (check.get("patched") or {}).get("distance_one_references"),
        }
        for check in checks
        if check.get("status") == "warning"
    ]
    return {
        "lz77_distance_one": {
            "checked_count": len(checks),
            "warning_count": len(warnings),
            "status": "warning" if warnings else "ok",
            "warnings": warnings,
        }
    }


def attach_lz77_distance_one_check(
    result: dict,
    *,
    item_id: str,
    original_offset: int,
    compressed: bytes,
    encoder: str,
) -> dict:
    if result.get("status") == "applied":
        result["lz77_stability"] = build_lz77_distance_one_check(
            item_id=item_id,
            original_offset=original_offset,
            compressed=compressed,
            encoder=encoder,
        )
    return result


def gba_pointer_for_offset(offset: int) -> bytes:
    return (GBA_ROM_BASE + offset).to_bytes(4, "little")


def rom_offset_from_pointer_value(value: int) -> int | None:
    offset = value - GBA_ROM_BASE
    if 0 <= offset < GBA_MAX_ROM_SIZE:
        return offset
    return None


def pointer_value_at(rom: bytes | bytearray, pointer_offset: int) -> int | None:
    if not (0 <= pointer_offset <= len(rom) - 4):
        return None
    return int.from_bytes(rom[pointer_offset : pointer_offset + 4], "little")


def aligned_resource_size(size: int) -> int:
    return size + ((REPOINT_ALIGNMENT - (size % REPOINT_ALIGNMENT)) % REPOINT_ALIGNMENT)


def repoint_size_word_patches(
    rom: bytes | bytearray,
    pointer_offsets: list[int],
    *,
    original_consumed: int,
    current_consumed: int | None,
    new_consumed: int,
) -> list[dict]:
    expected_old_values = {aligned_resource_size(original_consumed)}
    if current_consumed is not None:
        expected_old_values.add(aligned_resource_size(current_consumed))
    new_value = aligned_resource_size(new_consumed)
    patches: list[dict] = []
    for pointer_offset in pointer_offsets:
        size_offset = pointer_offset + 4
        if not (0 <= size_offset <= len(rom) - 4):
            continue
        old_value = int.from_bytes(rom[size_offset : size_offset + 4], "little")
        if old_value == new_value:
            continue
        if old_value not in expected_old_values:
            continue
        patches.append(
            {
                "offset": size_offset,
                "old_value": old_value,
                "new_value": new_value,
            }
        )
    return patches


def apply_repoint_size_word_patches(rom: bytearray, patches: list[dict]) -> dict[int, bytes]:
    old_bytes: dict[int, bytes] = {}
    for patch in patches:
        offset = int(patch["offset"])
        old_bytes[offset] = bytes(rom[offset : offset + 4])
        rom[offset : offset + 4] = int(patch["new_value"]).to_bytes(4, "little")
    return old_bytes


def public_size_word_patches(patches: list[dict]) -> list[dict]:
    return [
        {
            "offset": f"0x{int(patch['offset']):08X}",
            "old_value": f"0x{int(patch['old_value']):08X}",
            "new_value": f"0x{int(patch['new_value']):08X}",
        }
        for patch in patches
    ]


def find_word_aligned_pointer_offsets(rom: bytes | bytearray, target_offset: int) -> list[int]:
    needle = gba_pointer_for_offset(target_offset)
    haystack = bytes(rom)
    hits: list[int] = []
    start = 0
    while True:
        index = haystack.find(needle, start)
        if index < 0:
            break
        if index % 4 == 0:
            hits.append(index)
        start = index + 1
    return hits


def previous_repoint_pointer_offsets(item: dict) -> list[int]:
    offsets: list[int] = []
    summary = item.get("last_apply_summary") or {}
    for result in summary.get("results", []):
        if result.get("item_id") != item.get("item_id"):
            continue
        for value in result.get("pointer_offsets", []):
            try:
                offsets.append(int(str(value), 16) if isinstance(value, str) else int(value))
            except (TypeError, ValueError):
                continue
    return sorted(set(offsets))


def pointer_offsets_for_repoint(
    rom: bytes | bytearray,
    item: dict,
    original_offset: int,
    *,
    compression_tag: int,
    decompressed_size: int,
) -> list[int]:
    direct_hits = find_word_aligned_pointer_offsets(rom, original_offset)
    if direct_hits:
        return direct_hits

    reusable_hits: list[int] = []
    for pointer_offset in previous_repoint_pointer_offsets(item):
        value = pointer_value_at(rom, pointer_offset)
        if value is None:
            continue
        pointed_offset = rom_offset_from_pointer_value(value)
        if pointed_offset is None or pointed_offset >= len(rom):
            continue
        if rom[pointed_offset] != compression_tag:
            continue
        if pointed_offset + 4 > len(rom):
            continue
        pointed_size = rom[pointed_offset + 1] | (rom[pointed_offset + 2] << 8) | (rom[pointed_offset + 3] << 16)
        # A previously repointed item may grow again when screen-order alias
        # splitting appends extra tiles. The stored block size can therefore be
        # the older replacement size, not the size we are about to write.
        reusable_hits.append(pointer_offset)
    return sorted(set(reusable_hits))


def reference_consumed_size(
    *,
    offset: int,
    current_payload_size: int,
    current_consumed: int,
    decompressor,
) -> int:
    """Return the original block capacity when the current ROM was already patched.

    LZ/RLE streams report only the bytes needed by the currently stored stream.
    If a previous replacement was smaller than the game's original block, using
    that current length as capacity makes later, still-safe replacements fail.
    """
    best = current_consumed
    for rom_path in REFERENCE_CAPACITY_ROMS:
        if not rom_path.is_file():
            continue
        try:
            payload, consumed = decompressor(rom_path.read_bytes(), offset, max_output_size=0x400000)
        except Exception:
            continue
        if len(payload) == current_payload_size and consumed > best:
            best = consumed
    return best


def append_repoint_blob(
    rom: bytearray,
    item: dict,
    *,
    original_offset: int,
    original_consumed: int,
    compressed: bytes,
    payload: bytes,
    compression: str,
    compression_tag: int,
    decompressor,
) -> dict:
    pointer_offsets = pointer_offsets_for_repoint(
        rom,
        item,
        original_offset,
        compression_tag=compression_tag,
        decompressed_size=len(payload),
    )
    if not pointer_offsets:
        overage = len(compressed) - original_consumed
        prefix = (
            f"compressed replacement too large: {len(compressed)} > {original_consumed}; "
            if overage > 0
            else ""
        )
        return {
            "item_id": item["item_id"],
            "status": "error",
            "reason": f"{prefix}repoint failed: no pointer to original image block found",
            "offset_hex": f"0x{original_offset:08X}",
            "compression": compression,
            "compressed_size": len(compressed),
            "available_size": original_consumed,
            "repoint_attempted": True,
        }

    current_pointer_values = [
        pointer_value_at(rom, pointer_offset)
        for pointer_offset in pointer_offsets
    ]
    pointed_offsets = {
        rom_offset_from_pointer_value(value)
        for value in current_pointer_values
        if value is not None
    }
    pointed_offsets.discard(None)
    if len(pointed_offsets) == 1:
        existing_offset = next(iter(pointed_offsets))
        if existing_offset != original_offset and existing_offset is not None and existing_offset < len(rom):
            try:
                existing = decompressor(bytes(rom), existing_offset, max_output_size=0x400000)
            except Exception:
                existing = None
            if existing and existing[0] == payload:
                size_word_patches = repoint_size_word_patches(
                    rom,
                    pointer_offsets,
                    original_consumed=original_consumed,
                    current_consumed=existing[1],
                    new_consumed=len(compressed),
                )
                apply_repoint_size_word_patches(rom, size_word_patches)
                return {
                    "item_id": item["item_id"],
                    "status": "applied",
                    "compression": compression,
                    "storage": "repoint",
                    "already_repointed": True,
                    "offset": original_offset,
                    "offset_hex": f"0x{original_offset:08X}",
                    "new_offset": existing_offset,
                    "new_offset_hex": f"0x{existing_offset:08X}",
                    "pointer_offsets": [f"0x{value:08X}" for value in pointer_offsets],
                    "old_pointer_values": [f"0x{value:08X}" for value in current_pointer_values if value is not None],
                    "new_pointer_value": f"0x{GBA_ROM_BASE + existing_offset:08X}",
                    "size_word_patches": public_size_word_patches(size_word_patches),
                    "decompressed_size": len(payload),
                    "compressed_size": existing[1],
                    "available_size": original_consumed,
                    "original_consumed_size": original_consumed,
                    "size_overage": len(compressed) - original_consumed,
                    "rom_size_after": len(rom),
                    "repoint_attempted": True,
                }

    original_rom_len = len(rom)
    if len(rom) % REPOINT_ALIGNMENT:
        rom.extend(b"\xFF" * (REPOINT_ALIGNMENT - (len(rom) % REPOINT_ALIGNMENT)))
    new_offset = len(rom)
    if new_offset + len(compressed) > GBA_MAX_ROM_SIZE:
        del rom[original_rom_len:]
        overage = len(compressed) - original_consumed
        prefix = (
            f"compressed replacement too large: {len(compressed)} > {original_consumed}; "
            if overage > 0
            else ""
        )
        return {
            "item_id": item["item_id"],
            "status": "error",
            "reason": (
                f"{prefix}repoint failed: ROM would exceed {GBA_MAX_ROM_SIZE} bytes"
            ),
            "offset_hex": f"0x{original_offset:08X}",
            "compression": compression,
            "compressed_size": len(compressed),
            "available_size": original_consumed,
            "repoint_attempted": True,
        }

    rom.extend(compressed)
    new_pointer = gba_pointer_for_offset(new_offset)
    old_pointer_values = []
    old_pointer_bytes = {}
    for pointer_offset in pointer_offsets:
        old_pointer_values.append(pointer_value_at(rom, pointer_offset))
        old_pointer_bytes[pointer_offset] = bytes(rom[pointer_offset : pointer_offset + 4])
        rom[pointer_offset : pointer_offset + 4] = new_pointer
    size_word_patches = repoint_size_word_patches(
        rom,
        pointer_offsets,
        original_consumed=original_consumed,
        current_consumed=None,
        new_consumed=len(compressed),
    )
    old_size_word_bytes = apply_repoint_size_word_patches(rom, size_word_patches)

    try:
        verify = decompressor(bytes(rom), new_offset, max_output_size=0x400000)
    except Exception:
        verify = None
    if not verify or verify[0] != payload:
        for pointer_offset, old_bytes in old_pointer_bytes.items():
            rom[pointer_offset : pointer_offset + 4] = old_bytes
        for size_offset, old_bytes in old_size_word_bytes.items():
            rom[size_offset : size_offset + 4] = old_bytes
        del rom[original_rom_len:]
        return {
            "item_id": item["item_id"],
            "status": "error",
            "reason": "repoint verification failed",
            "offset_hex": f"0x{original_offset:08X}",
            "new_offset_hex": f"0x{new_offset:08X}",
            "compression": compression,
            "compressed_size": len(compressed),
            "available_size": original_consumed,
            "repoint_attempted": True,
        }

    return {
        "item_id": item["item_id"],
        "status": "applied",
        "compression": compression,
        "storage": "repoint",
        "offset": original_offset,
        "offset_hex": f"0x{original_offset:08X}",
        "new_offset": new_offset,
        "new_offset_hex": f"0x{new_offset:08X}",
        "pointer_offsets": [f"0x{value:08X}" for value in pointer_offsets],
        "old_pointer_values": [f"0x{value:08X}" for value in old_pointer_values if value is not None],
        "new_pointer_value": f"0x{GBA_ROM_BASE + new_offset:08X}",
        "size_word_patches": public_size_word_patches(size_word_patches),
        "decompressed_size": len(payload),
        "compressed_size": len(compressed),
        "available_size": original_consumed,
        "original_consumed_size": original_consumed,
        "size_overage": len(compressed) - original_consumed,
        "rom_size_after": len(rom),
        "repoint_attempted": True,
    }


def restore_same_offset_pointer_patches(
    rom: bytearray,
    item: dict,
    *,
    original_offset: int,
    original_consumed: int,
    compression_tag: int,
    decompressor,
) -> list[dict]:
    patches: list[dict] = []
    target_pointer = int.from_bytes(gba_pointer_for_offset(original_offset), "little")
    target_size = aligned_resource_size(original_consumed)
    for pointer_offset in previous_repoint_pointer_offsets(item):
        value = pointer_value_at(rom, pointer_offset)
        if value is None or value == target_pointer:
            continue
        pointed_offset = rom_offset_from_pointer_value(value)
        if pointed_offset is None or pointed_offset >= len(rom):
            continue
        if rom[pointed_offset] != compression_tag:
            continue
        try:
            _, pointed_consumed = decompressor(bytes(rom), pointed_offset, max_output_size=0x400000)
        except Exception:
            continue
        size_offset = pointer_offset + 4
        old_size = None
        if 0 <= size_offset <= len(rom) - 4:
            old_size = int.from_bytes(rom[size_offset : size_offset + 4], "little")
        rom[pointer_offset : pointer_offset + 4] = gba_pointer_for_offset(original_offset)
        if old_size is not None and old_size in {
            aligned_resource_size(pointed_consumed),
            target_size,
        }:
            rom[size_offset : size_offset + 4] = target_size.to_bytes(4, "little")
        patches.append(
            {
                "pointer_offset": f"0x{pointer_offset:08X}",
                "old_pointer_value": f"0x{value:08X}",
                "new_pointer_value": f"0x{target_pointer:08X}",
                "size_offset": f"0x{size_offset:08X}" if old_size is not None else "",
                "old_size_value": f"0x{old_size:08X}" if old_size is not None else "",
                "new_size_value": f"0x{target_size:08X}" if old_size is not None else "",
            }
        )
    return patches


def append_field_label_lz77_repoint_blob(
    rom: bytearray,
    item: dict,
    *,
    original_offset: int,
    original_consumed: int,
    compressed: bytes,
    payload: bytes,
) -> dict | None:
    repoint = FIELD_LABEL_LZ77_TABLE_REPOINTS.get(original_offset)
    if repoint is None:
        return None

    table_offset = int(repoint["table_offset"])
    header_offset = original_offset - 4
    if header_offset < 0 or header_offset + 4 > len(rom):
        return {
            "item_id": item["item_id"],
            "status": "error",
            "reason": "field label repoint failed: original entry header is outside ROM",
            "offset_hex": f"0x{original_offset:08X}",
            "compression": "lz77",
            "compressed_size": len(compressed),
            "available_size": original_consumed,
            "repoint_attempted": True,
        }
    if table_offset < 0 or table_offset + 4 > len(rom):
        return {
            "item_id": item["item_id"],
            "status": "error",
            "reason": "field label repoint failed: archive table offset is outside ROM",
            "offset_hex": f"0x{original_offset:08X}",
            "compression": "lz77",
            "compressed_size": len(compressed),
            "available_size": original_consumed,
            "repoint_attempted": True,
        }

    entry_header = bytes(rom[header_offset:header_offset + 4])
    if not entry_header or entry_header[-1] & 0x80 == 0:
        return {
            "item_id": item["item_id"],
            "status": "error",
            "reason": "field label repoint failed: original entry header is not compressed",
            "offset_hex": f"0x{original_offset:08X}",
            "compression": "lz77",
            "compressed_size": len(compressed),
            "available_size": original_consumed,
            "repoint_attempted": True,
        }

    old_table_value = int.from_bytes(rom[table_offset:table_offset + 4], "little")
    pointed_entry_offset = FIELD_LABEL_ARCHIVE_DATA_BASE + old_table_value
    if 0 <= pointed_entry_offset + 4 <= len(rom):
        try:
            existing_payload, existing_consumed = decompress_lz77(
                bytes(rom),
                pointed_entry_offset + 4,
                max_output_size=0x400000,
            )
        except Exception:
            existing_payload = None
            existing_consumed = 0
        if (
            pointed_entry_offset != header_offset
            and existing_payload == payload
            and existing_consumed == len(compressed)
        ):
            return {
                "item_id": item["item_id"],
                "status": "applied",
                "compression": "lz77",
                "storage": "field_label_archive_repoint",
                "already_repointed": True,
                "offset": original_offset,
                "offset_hex": f"0x{original_offset:08X}",
                "new_offset": pointed_entry_offset + 4,
                "new_offset_hex": f"0x{pointed_entry_offset + 4:08X}",
                "entry_header_offset": f"0x{pointed_entry_offset:08X}",
                "table_offsets": [f"0x{table_offset:08X}"],
                "old_table_values": [f"0x{old_table_value:08X}"],
                "archive_data_base": f"0x{FIELD_LABEL_ARCHIVE_DATA_BASE:08X}",
                "decompressed_size": len(payload),
                "compressed_size": existing_consumed,
                "available_size": original_consumed,
                "original_consumed_size": original_consumed,
                "size_overage": len(compressed) - original_consumed,
                "rom_size_after": len(rom),
                "repoint_attempted": True,
            }

    original_rom_len = len(rom)
    if len(rom) % REPOINT_ALIGNMENT:
        rom.extend(b"\xFF" * (REPOINT_ALIGNMENT - (len(rom) % REPOINT_ALIGNMENT)))
    new_entry_offset = len(rom)
    new_lz77_offset = new_entry_offset + 4
    blob = entry_header + compressed
    if new_entry_offset + len(blob) > GBA_MAX_ROM_SIZE:
        del rom[original_rom_len:]
        return {
            "item_id": item["item_id"],
            "status": "error",
            "reason": f"compressed replacement too large: {len(compressed)} > {original_consumed}; field label repoint failed: ROM would exceed {GBA_MAX_ROM_SIZE} bytes",
            "offset_hex": f"0x{original_offset:08X}",
            "compression": "lz77",
            "compressed_size": len(compressed),
            "available_size": original_consumed,
            "repoint_attempted": True,
        }

    new_table_value = new_entry_offset - FIELD_LABEL_ARCHIVE_DATA_BASE
    if not (0 <= new_table_value <= 0xFFFFFFFF):
        del rom[original_rom_len:]
        return {
            "item_id": item["item_id"],
            "status": "error",
            "reason": "field label repoint failed: new archive-relative offset is out of range",
            "offset_hex": f"0x{original_offset:08X}",
            "compression": "lz77",
            "compressed_size": len(compressed),
            "available_size": original_consumed,
            "repoint_attempted": True,
        }

    old_table_bytes = bytes(rom[table_offset:table_offset + 4])
    rom.extend(blob)
    rom[table_offset:table_offset + 4] = new_table_value.to_bytes(4, "little")

    try:
        verify = decompress_lz77(bytes(rom), new_lz77_offset, max_output_size=0x400000)
    except Exception:
        verify = None
    table_verify = FIELD_LABEL_ARCHIVE_DATA_BASE + int.from_bytes(rom[table_offset:table_offset + 4], "little")
    if not verify or verify[0] != payload or table_verify != new_entry_offset:
        rom[table_offset:table_offset + 4] = old_table_bytes
        del rom[original_rom_len:]
        return {
            "item_id": item["item_id"],
            "status": "error",
            "reason": "field label archive repoint verification failed",
            "offset_hex": f"0x{original_offset:08X}",
            "new_offset_hex": f"0x{new_lz77_offset:08X}",
            "compression": "lz77",
            "compressed_size": len(compressed),
            "available_size": original_consumed,
            "repoint_attempted": True,
        }

    return {
        "item_id": item["item_id"],
        "status": "applied",
        "compression": "lz77",
        "storage": "field_label_archive_repoint",
        "offset": original_offset,
        "offset_hex": f"0x{original_offset:08X}",
        "new_offset": new_lz77_offset,
        "new_offset_hex": f"0x{new_lz77_offset:08X}",
        "entry_header_offset": f"0x{new_entry_offset:08X}",
        "table_offsets": [f"0x{table_offset:08X}"],
        "old_table_values": [f"0x{old_table_value:08X}"],
        "new_table_value": f"0x{new_table_value:08X}",
        "archive_data_base": f"0x{FIELD_LABEL_ARCHIVE_DATA_BASE:08X}",
        "decompressed_size": len(payload),
        "compressed_size": len(compressed),
        "available_size": original_consumed,
        "original_consumed_size": original_consumed,
        "size_overage": len(compressed) - original_consumed,
        "rom_size_after": len(rom),
        "repoint_attempted": True,
    }


def field_label_pointed_entry_offset(rom: bytes | bytearray, original_offset: int) -> int | None:
    repoint = FIELD_LABEL_LZ77_TABLE_REPOINTS.get(original_offset)
    if repoint is None:
        return None
    table_offset = int(repoint["table_offset"])
    if table_offset < 0 or table_offset + 4 > len(rom):
        return None
    return FIELD_LABEL_ARCHIVE_DATA_BASE + int.from_bytes(rom[table_offset:table_offset + 4], "little")


def rle_offset_from_item(item: dict) -> int | None:
    for value in (item.get("item_id", ""), item.get("group_id", "")):
        match = OFFSET_RE.search(str(value))
        if match:
            return int(match.group("offset"), 16)
    for subunit in item.get("subunits", []):
        for value in (subunit.get("id", ""), subunit.get("label", "")):
            match = OFFSET_RE.search(str(value))
            if match:
                return int(match.group("offset"), 16)
    return None


def columns_from_item(item: dict, tile_count: int) -> int:
    for field in ("tile_columns", "layout_columns"):
        value = item.get(field)
        if value not in ("", None):
            columns = int(value)
            if columns > 0:
                return min(columns, tile_count)
    paths = [
        item.get("source_preview_path", ""),
        item.get("source_download_path", ""),
        item.get("replacement_path", ""),
    ]
    for candidate in item.get("candidate_gallery", []):
        paths.extend([candidate.get("preview_path", ""), candidate.get("png_path", "")])
    for path in paths:
        match = COLS_RE.search(str(path))
        if match:
            return int(match.group("cols"))
    return min(32, max(1, tile_count))


def image_to_indices(path: Path, expected_w: int, expected_h: int) -> bytes:
    image = Image.open(path).convert("RGBA")
    if image.size != (expected_w, expected_h):
        if image.size[0] % expected_w or image.size[1] % expected_h:
            raise ValueError(
                f"{path} size {image.size} is not compatible with expected {expected_w}x{expected_h}"
            )
        image = image.resize((expected_w, expected_h), Image.Resampling.NEAREST)

    out = bytearray(expected_w * expected_h)
    pixels = image.load()
    for y in range(expected_h):
        for x in range(expected_w):
            r, g, b, a = pixels[x, y]
            if a == 0:
                value = 0
            else:
                value = round(((r + g + b) / 3) / 17)
            out[y * expected_w + x] = max(0, min(15, value))
    return bytes(out)


def common_hud_tile_uses_zero_to_shadow_remap(tile_index: int) -> bool:
    return any(start <= tile_index <= end for start, end in COMMON_HUD_ZERO_TO_SHADOW_TILE_RANGES)


def remap_zero_indices(indices: bytes, replacement: int = 1) -> bytes:
    replacement &= 0x0F
    return bytes(replacement if value == 0 else value for value in indices)


def remap_common_hud_zero_to_shadow_ranges(payload: bytes | bytearray) -> tuple[bytearray, int]:
    out = bytearray(payload)
    changed = 0
    for start_tile, end_tile in COMMON_HUD_ZERO_TO_SHADOW_TILE_RANGES:
        for tile_index in range(start_tile, end_tile + 1):
            base = tile_index * TILE_BYTES
            if base + TILE_BYTES > len(out):
                continue
            for index in range(base, base + TILE_BYTES):
                byte = out[index]
                lo = byte & 0x0F
                hi = (byte >> 4) & 0x0F
                if lo == 0:
                    lo = 1
                    changed += 1
                if hi == 0:
                    hi = 1
                    changed += 1
                out[index] = lo | (hi << 4)
    return out, changed


def indices_to_4bpp_tiles(indices: bytes, width: int, height: int, columns: int, tile_count: int) -> bytes:
    rows = height // 8
    payload = bytearray(tile_count * TILE_BYTES)
    for tile_index in range(tile_count):
        tile_x = (tile_index % columns) * 8
        tile_y = (tile_index // columns) * 8
        if tile_y + 8 > height:
            break
        base = tile_index * TILE_BYTES
        for y in range(8):
            for pair in range(4):
                x0 = tile_x + pair * 2
                lo = indices[(tile_y + y) * width + x0] & 0x0F
                hi = indices[(tile_y + y) * width + x0 + 1] & 0x0F
                payload[base + y * 4 + pair] = lo | (hi << 4)
    return bytes(payload)


def tile_indices_from_item(item: dict, resource_tile_count: int) -> list[int]:
    values = item.get("tile_indices") or item.get("edit_tile_indices") or []
    if not values:
        return []
    tile_indices: list[int] = []
    for value in values:
        index = parse_int_value(value)
        if index is None:
            continue
        if 0 <= index < resource_tile_count:
            tile_indices.append(index)
    return tile_indices


def changed_tile_indexes(left: bytes, right: bytes) -> list[int]:
    tile_count = min(len(left), len(right)) // TILE_BYTES
    changed = [
        index
        for index in range(tile_count)
        if left[index * TILE_BYTES : index * TILE_BYTES + TILE_BYTES]
        != right[index * TILE_BYTES : index * TILE_BYTES + TILE_BYTES]
    ]
    if len(left) != len(right):
        changed.extend(range(tile_count, max(len(left), len(right)) // TILE_BYTES))
    return changed


def resize_replacement(path: Path, expected_w: int, expected_h: int) -> Image.Image:
    image = Image.open(path).convert("RGBA")
    if image.size != (expected_w, expected_h):
        if image.size[0] % expected_w or image.size[1] % expected_h:
            raise ValueError(
                f"{path} size {image.size} is not compatible with expected {expected_w}x{expected_h}"
            )
        image = image.resize((expected_w, expected_h), Image.Resampling.NEAREST)
    return image


def nearest_palette_nibble(rgb: tuple[int, int, int], palette: list[tuple[int, int, int]], palette_bank: int) -> int:
    start = palette_bank * 16
    choices = palette[start : start + 16]
    if not choices:
        return round(sum(rgb) / 3 / 17)
    best_index = 0
    best_score = 1 << 62
    for index, color in enumerate(choices):
        score = sum((rgb[channel] - color[channel]) ** 2 for channel in range(3))
        if score < best_score:
            best_score = score
            best_index = index
    return best_index & 0x0F


def rgba_to_nibble(
    rgba: tuple[int, int, int, int],
    *,
    palette: list[tuple[int, int, int]] | None = None,
    palette_bank: int = 0,
) -> int:
    r, g, b, a = rgba
    if a == 0:
        return 0
    if palette is None:
        return max(0, min(15, round(((r + g + b) / 3) / 17)))
    return nearest_palette_nibble((r, g, b), palette, palette_bank)


def nibble_from_tile(tile: bytes, x: int, y: int) -> int:
    if not (0 <= x < 8 and 0 <= y < 8) or len(tile) < TILE_BYTES:
        return 0
    byte = tile[y * 4 + (x // 2)]
    return (byte >> 4) & 0x0F if x % 2 else byte & 0x0F


def tile_from_image(
    image: Image.Image,
    x0: int,
    y0: int,
    *,
    palette: list[tuple[int, int, int]] | None = None,
    palette_bank: int = 0,
    hflip: bool = False,
    vflip: bool = False,
    fallback_tile: bytes | None = None,
    source_color_map: dict[tuple[int, tuple[int, int, int]], int] | None = None,
    source_image: Image.Image | None = None,
) -> bytes:
    pixels = image.load()
    source_pixels = source_image.load() if source_image is not None else None
    tile = bytearray(TILE_BYTES)
    for y in range(8):
        for pair in range(4):
            raw_x0 = pair * 2
            raw_x1 = raw_x0 + 1
            screen_x0 = 7 - raw_x0 if hflip else raw_x0
            screen_x1 = 7 - raw_x1 if hflip else raw_x1
            screen_y = 7 - y if vflip else y
            pixel_x0 = x0 + screen_x0
            pixel_x1 = x0 + screen_x1
            pixel_y = y0 + screen_y
            if 0 <= pixel_x0 < image.width and 0 <= pixel_y < image.height:
                rgba = pixels[pixel_x0, pixel_y]
                if source_pixels is not None and source_pixels[pixel_x0, pixel_y] == rgba:
                    lo = nibble_from_tile(fallback_tile or b"", raw_x0, y)
                else:
                    mapped = None
                    if source_color_map and rgba[3] != 0:
                        mapped = source_color_map.get((palette_bank, (rgba[0], rgba[1], rgba[2])))
                    lo = mapped if mapped is not None else rgba_to_nibble(rgba, palette=palette, palette_bank=palette_bank)
            else:
                lo = nibble_from_tile(fallback_tile or b"", raw_x0, y)
            if 0 <= pixel_x1 < image.width and 0 <= pixel_y < image.height:
                rgba = pixels[pixel_x1, pixel_y]
                if source_pixels is not None and source_pixels[pixel_x1, pixel_y] == rgba:
                    hi = nibble_from_tile(fallback_tile or b"", raw_x1, y)
                else:
                    mapped = None
                    if source_color_map and rgba[3] != 0:
                        mapped = source_color_map.get((palette_bank, (rgba[0], rgba[1], rgba[2])))
                    hi = mapped if mapped is not None else rgba_to_nibble(rgba, palette=palette, palette_bank=palette_bank)
            else:
                hi = nibble_from_tile(fallback_tile or b"", raw_x1, y)
            tile[y * 4 + pair] = lo | (hi << 4)
    return bytes(tile)


def load_tile_map(item: dict) -> dict | None:
    tile_map_path = item.get("tile_map_path", "")
    if not tile_map_path:
        return None
    path = (ROOT / tile_map_path).resolve()
    if not path.is_file() or ROOT not in path.parents:
        raise FileNotFoundError(f"tile_map_path not found: {tile_map_path}")
    return json.loads(path.read_text(encoding="utf-8"))


def palette_for_tile_map(tile_map: dict) -> list[tuple[int, int, int]] | None:
    palette_path = tile_map.get("runtime_palette_path", "")
    if not palette_path:
        return None
    path = (ROOT / palette_path).resolve()
    if not path.is_file() or ROOT not in path.parents:
        return None
    return read_palette(path.read_bytes())


def is_screen_order_rle_item(item: dict, tile_map: dict | None = None) -> bool:
    if tile_map is None:
        return False
    item_id = str(item.get("item_id", ""))
    return item_id.startswith("image:rle_screen_order:") or item_id.startswith(
        "image:rle_screen_order_focus:"
    )


def option_bool(item: dict, key: str, default: bool = False) -> bool:
    value = item.get(key, None)
    if value in ("", None):
        return default
    return bool(value)


def runtime_capture_base_for_tile_map(tile_map: dict) -> Path:
    scene = str(tile_map.get("scene", ""))
    frame = str(tile_map.get("frame", ""))
    return ROOT / "confirmed_data" / "image_inventory" / "runtime_user_captures" / scene / frame


def runtime_vram_payload_from_tile_map(tile_map: dict, fallback_payload: bytes) -> bytes | None:
    base = runtime_capture_base_for_tile_map(tile_map)
    vram_path = base.with_name(base.name + "_vram_06000000.bin")
    ioreg_path = base.with_name(base.name + "_ioreg_04000000.bin")
    if not vram_path.is_file() or not ioreg_path.is_file():
        return None
    vram = vram_path.read_bytes()
    ioreg = ioreg_path.read_bytes()
    bg = int(tile_map.get("bg", 0))
    if 8 + bg * 2 + 2 > len(ioreg):
        return None
    bgcnt = int.from_bytes(ioreg[8 + bg * 2 : 8 + bg * 2 + 2], "little")
    char_base = ((bgcnt >> 2) & 0x3) * 0x4000
    payload = bytearray(fallback_payload)
    for match in tile_map.get("matches", []):
        runtime_tile_index = int(match["runtime_tile_index"])
        start = char_base + runtime_tile_index * TILE_BYTES
        tile = vram[start : start + TILE_BYTES]
        if len(tile) != TILE_BYTES:
            continue
        for tile_index in match.get("rle_tile_indexes", []):
            dst = int(tile_index) * TILE_BYTES
            if dst + TILE_BYTES <= len(payload):
                payload[dst : dst + TILE_BYTES] = tile
    return bytes(payload)


def screen_order_payload_base(item: dict, tile_map: dict | None, original_payload: bytes) -> bytes:
    if not tile_map:
        return original_payload
    mode = item.get("replacement_payload_base")
    if mode in ("", None) and is_screen_order_rle_item(item, tile_map):
        mode = "source_raw"
    if mode == "runtime_vram":
        payload = runtime_vram_payload_from_tile_map(tile_map, original_payload)
        if payload is not None and len(payload) == len(original_payload):
            return payload
    if mode == "source_raw":
        raw_path = tile_map.get("rle_raw_path", "")
        if raw_path:
            payload_path = (ROOT / raw_path).resolve()
            if payload_path.is_file():
                payload = payload_path.read_bytes()
                if len(payload) == len(original_payload):
                    return payload
    return original_payload


def screen_order_source_image_path(item: dict, tile_map: dict) -> Path | None:
    for key in ("source_download_path", "source_preview_path"):
        value = item.get(key, "")
        if value:
            path = (ROOT / value).resolve()
            if path.is_file() and ROOT in path.parents:
                return path
    tile_map_path = item.get("tile_map_path", "")
    if tile_map_path:
        path = (ROOT / tile_map_path).resolve().parent / "matched_tiles_screen_order_4x.png"
        if path.is_file() and ROOT in path.parents:
            return path
    return None


def source_color_nibble_map_from_image(
    source_path: Path,
    tile_map: dict,
    base_payload: bytes,
) -> dict[tuple[int, tuple[int, int, int]], int]:
    crop = tile_map["crop_pixels"]
    source = resize_replacement(source_path, int(crop["width"]), int(crop["height"]))
    pixels = source.load()
    crop_x = int(crop.get("x", int(tile_map["crop_screen_tiles"]["min_x"]) * 8))
    crop_y = int(crop.get("y", int(tile_map["crop_screen_tiles"]["min_y"]) * 8))
    fine = tile_map.get("fine_scroll_pixels") or {}
    adjustment = tile_map.get("alignment_adjustment_pixels") or {}
    fine_x = int(fine.get("x", 0))
    fine_y = int(fine.get("y", 0))
    shift_x = int(adjustment.get("x", 0))
    shift_y = int(adjustment.get("y", 0))
    counts: dict[tuple[int, tuple[int, int, int]], dict[int, int]] = {}
    layout = infer_rle_runtime_tile_layout(tile_map)
    for match in tile_map.get("matches", []):
        rel_x = int(match["screen_tile_x"]) * 8 - fine_x + shift_x - crop_x
        rel_y = int(match["screen_tile_y"]) * 8 - fine_y + shift_y - crop_y
        palette_bank = int(match.get("palette_bank", 0))
        for tile_index in rle_tile_indexes_for_match(match, layout):
            start = tile_index * TILE_BYTES
            if start + TILE_BYTES > len(base_payload):
                continue
            tile = base_payload[start : start + TILE_BYTES]
            for y in range(8):
                for x in range(8):
                    source_x = 7 - x if match.get("hflip") else x
                    source_y = 7 - y if match.get("vflip") else y
                    px = rel_x + x
                    py = rel_y + y
                    if not (0 <= px < source.width and 0 <= py < source.height):
                        continue
                    r, g, b, a = pixels[px, py]
                    if a == 0:
                        continue
                    nibble = nibble_from_tile(tile, source_x, source_y)
                    key = (palette_bank, (r, g, b))
                    counts.setdefault(key, {})
                    counts[key][nibble] = counts[key].get(nibble, 0) + 1
    return {
        key: max(nibble_counts.items(), key=lambda item: (item[1], -item[0]))[0]
        for key, nibble_counts in counts.items()
    }


def screen_entry_with_tile_index(screen_entry: int, tile_index: int) -> int:
    if not 0 <= tile_index <= 0x3FF:
        raise ValueError(f"screen tile index is outside GBA BG range: 0x{tile_index:X}")
    return (int(screen_entry) & ~0x03FF) | (tile_index & 0x03FF)


def infer_rle_runtime_tile_layout(tile_map: dict) -> dict | None:
    by_rle_index: dict[int, int] = {}
    strict_conflict = False
    for match in tile_map.get("matches", []):
        runtime_tile_index = int(match["runtime_tile_index"])
        for value in match.get("rle_tile_indexes", []):
            rle_tile_index = int(value)
            previous = by_rle_index.get(rle_tile_index)
            if previous is not None and previous != runtime_tile_index:
                strict_conflict = True
                continue
            by_rle_index[rle_tile_index] = runtime_tile_index
    if not by_rle_index:
        return None

    screen_xs = [int(match["screen_tile_x"]) for match in tile_map.get("matches", [])]
    preferred_columns = max(screen_xs) - min(screen_xs) + 1 if screen_xs else 0
    candidate_columns = [preferred_columns] if preferred_columns > 0 else []
    candidate_columns.extend(value for value in range(1, 33) if value != preferred_columns)
    pairs = sorted(by_rle_index.items())
    if not strict_conflict:
        for columns in candidate_columns:
            for stride in range(columns, 0x81):
                bases = {
                    runtime_index - (rle_index // columns) * stride - (rle_index % columns)
                    for rle_index, runtime_index in pairs
                }
                if len(bases) == 1:
                    base = bases.pop()
                    return {
                        "base": base,
                        "columns": columns,
                        "stride": stride,
                        "known_pairs": len(pairs),
                    }

    matches = [match for match in tile_map.get("matches", []) if match.get("rle_tile_indexes")]
    if not matches:
        return None

    # Some screen-order maps list every matching source RLE tile as a candidate.
    # For those, infer the linear runtime layout by finding a base/stride that
    # lets each screen tile choose one candidate matching its runtime tile index.
    for columns in candidate_columns:
        for stride in range(columns, 0x81):
            base_votes: dict[int, int] = {}
            for match in matches:
                runtime_tile_index = int(match["runtime_tile_index"])
                for value in match.get("rle_tile_indexes", []):
                    rle_tile_index = int(value)
                    base = runtime_tile_index - (rle_tile_index // columns) * stride - (rle_tile_index % columns)
                    base_votes[base] = base_votes.get(base, 0) + 1

            for base, votes in sorted(base_votes.items(), key=lambda item: item[1], reverse=True):
                covered = 0
                for match in matches:
                    runtime_tile_index = int(match["runtime_tile_index"])
                    if any(
                        base + (int(value) // columns) * stride + (int(value) % columns) == runtime_tile_index
                        for value in match.get("rle_tile_indexes", [])
                    ):
                        covered += 1
                if covered == len(matches):
                    return {
                        "base": base,
                        "columns": columns,
                        "stride": stride,
                        "known_pairs": votes,
                        "resolved_candidate_matches": covered,
                    }
    return None


def runtime_tile_index_for_rle_index(layout: dict, rle_tile_index: int) -> int:
    columns = int(layout["columns"])
    return int(layout["base"]) + (rle_tile_index // columns) * int(layout["stride"]) + (rle_tile_index % columns)


def rle_tile_indexes_for_match(match: dict, layout: dict | None) -> list[int]:
    indexes = [int(value) for value in match.get("rle_tile_indexes", [])]
    if not layout:
        return indexes
    runtime_tile_index = int(match["runtime_tile_index"])
    resolved = [
        tile_index
        for tile_index in indexes
        if runtime_tile_index_for_rle_index(layout, tile_index) == runtime_tile_index
    ]
    if resolved:
        return [resolved[0]]
    return indexes


def rle_tile_reference_counts(tile_map: dict) -> dict[int, int]:
    counts: dict[int, int] = {}
    for match in tile_map.get("matches", []):
        for value in match.get("rle_tile_indexes", []):
            tile_index = int(value)
            counts[tile_index] = counts.get(tile_index, 0) + 1
    return counts


def rle_tile_screen_entries(tile_map: dict, rle_tile_index: int) -> list[int]:
    entries: list[int] = []
    for match in tile_map.get("matches", []):
        if rle_tile_index in {int(value) for value in match.get("rle_tile_indexes", [])}:
            entry = int(match["screen_entry"])
            if entry not in entries:
                entries.append(entry)
    return entries


def allocate_recycled_rle_tile_slot(
    payload: bytes | bytearray,
    tile_map: dict,
    *,
    reserved_tile_indexes: set[int],
) -> tuple[int, int] | None:
    reference_counts = rle_tile_reference_counts(tile_map)
    groups: dict[bytes, list[int]] = {}
    tile_count = len(payload) // TILE_BYTES
    for tile_index in range(tile_count):
        tile = bytes(payload[tile_index * TILE_BYTES : tile_index * TILE_BYTES + TILE_BYTES])
        groups.setdefault(tile, []).append(tile_index)

    candidates: list[tuple[int, int, int]] = []
    for indexes in groups.values():
        if len(indexes) < 2:
            continue
        for freed_index in indexes:
            if freed_index in reserved_tile_indexes:
                continue
            if not rle_tile_screen_entries(tile_map, freed_index):
                continue
            keepers = [index for index in indexes if index != freed_index]
            if not keepers:
                continue
            keeper_index = max(
                keepers,
                key=lambda index: (reference_counts.get(index, 0), -index),
            )
            candidates.append((reference_counts.get(freed_index, 0), freed_index, keeper_index))
    if not candidates:
        return None
    _, freed_index, keeper_index = min(candidates)
    return freed_index, keeper_index


def rle_report_blocks() -> list[dict]:
    if not DEFAULT_RLE_REPORT.is_file():
        return []
    try:
        report = json.loads(DEFAULT_RLE_REPORT.read_text(encoding="utf-8"))
    except Exception:
        return []
    return list(report.get("blocks", []))


def screen_entry_sparse_grid(tile_map: dict) -> dict[tuple[int, int], int]:
    sparse: dict[tuple[int, int], int] = {}
    for match in tile_map.get("matches", []):
        key = (int(match["screen_tile_x"]), int(match["screen_tile_y"]))
        sparse[key] = int(match["screen_entry"])
    return sparse


def best_screen_entry_alignment(
    entries: list[int],
    sparse: dict[tuple[int, int], int],
    updates: list[dict],
) -> tuple[int, int, int, list[tuple[int, int]], list[int]] | None:
    by_value: dict[int, list[tuple[int, int]]] = {}
    for position, value in sparse.items():
        by_value.setdefault(value, []).append(position)

    entry_count = len(entries)
    best: tuple[int, int, int, int, int, list[tuple[int, int]], list[int]] | None = None
    for width in range(1, 33):
        if entry_count % width:
            continue
        height = entry_count // width
        scores: dict[tuple[int, int], int] = {}
        for local_index, value in enumerate(entries):
            local_x = local_index % width
            local_y = local_index // width
            for screen_x, screen_y in by_value.get(value, []):
                origin = (screen_x - local_x, screen_y - local_y)
                scores[origin] = scores.get(origin, 0) + 1
        for (origin_x, origin_y), score in scores.items():
            patches: list[tuple[int, int]] = []
            handled: list[int] = []
            for update_index, update in enumerate(updates):
                local_x = int(update["screen_tile_x"]) - origin_x
                local_y = int(update["screen_tile_y"]) - origin_y
                if not (0 <= local_x < width and 0 <= local_y < height):
                    continue
                entry_index = local_y * width + local_x
                if entries[entry_index] == int(update["old_entry"]):
                    patches.append((update_index, entry_index))
                    handled.append(update_index)
                elif entries[entry_index] == int(update["new_entry"]):
                    handled.append(update_index)
            if not handled:
                continue
            minimum_score = max(4, len(handled) * 2)
            if score < minimum_score:
                continue
            candidate = (len(handled), score, -len(patches), width, origin_x, origin_y, patches, handled)
            if best is None or candidate > best:
                best = candidate
    if best is None:
        return None
    _, _, _, width, origin_x, origin_y, patches, handled = best
    return width, origin_x, origin_y, patches, handled


def plan_screen_entry_alias_split_patches(
    rom: bytes | bytearray,
    tile_map: dict,
    updates: list[dict],
    *,
    graphics_rle_offset: int,
    entry_rewrites: list[dict] | None = None,
) -> list[dict]:
    entry_rewrites = entry_rewrites or []
    if not updates:
        return []
    sparse = screen_entry_sparse_grid(tile_map)
    plans: list[dict] = []
    patched_update_indexes: set[int] = set()
    for block in rle_report_blocks():
        try:
            offset = int(block["offset"])
        except (KeyError, TypeError, ValueError):
            continue
        if offset == graphics_rle_offset or offset < 0 or offset >= len(rom):
            continue
        current = decompress_gba_rle(bytes(rom), offset, max_output_size=0x400000)
        if not current:
            continue
        payload, consumed = current
        if len(payload) % 2:
            continue
        entries = [int.from_bytes(payload[pos : pos + 2], "little") for pos in range(0, len(payload), 2)]
        alignment = best_screen_entry_alignment(entries, sparse, updates)
        if alignment is None:
            continue
        width, origin_x, origin_y, patches, handled = alignment
        if not patches:
            patched_update_indexes.update(handled)
            continue
        patched_entries = list(entries)
        rewrite_count = 0
        for entry_index, value in enumerate(patched_entries):
            for rewrite in entry_rewrites:
                if value == int(rewrite["old_entry"]):
                    patched_entries[entry_index] = int(rewrite["new_entry"])
                    rewrite_count += 1
                    break
        for update_index, entry_index in patches:
            patched_entries[entry_index] = int(updates[update_index]["new_entry"])
        if patched_entries == entries:
            patched_update_indexes.update(handled)
            continue
        new_payload = bytearray()
        for value in patched_entries:
            new_payload.extend(int(value).to_bytes(2, "little"))
        compressed = compress_gba_rle(bytes(new_payload))
        if len(compressed) > consumed:
            raise ValueError(
                "screen-entry alias split map patch is larger than its original RLE block: "
                f"0x{offset:08X} {len(compressed)} > {consumed}"
            )
        plans.append(
            {
                "offset": offset,
                "offset_hex": f"0x{offset:08X}",
                "consumed_size": consumed,
                "compressed_size": len(compressed),
                "payload_size": len(new_payload),
                "width": width,
                "origin_x": origin_x,
                "origin_y": origin_y,
                "patch_count": len(patches),
                "rewrite_count": rewrite_count,
                "update_indexes": handled,
                "compressed": compressed,
            }
        )
        patched_update_indexes.update(handled)

    missing = sorted(set(range(len(updates))) - patched_update_indexes)
    if missing:
        sparse = screen_entry_sparse_grid(tile_map)
        direct_plans: list[dict] = []
        handled_direct: set[int] = set()
        by_row: dict[int, list[int]] = {}
        for update_index in missing:
            row = int(updates[update_index]["screen_tile_y"])
            by_row.setdefault(row, []).append(update_index)
        for row, update_indexes in sorted(by_row.items()):
            row_entries = sorted(
                ((x, entry) for (x, y), entry in sparse.items() if y == row),
                key=lambda item: item[0],
            )
            if not row_entries:
                continue
            min_x = row_entries[0][0]
            pattern = b"".join(int(entry).to_bytes(2, "little") for _, entry in row_entries)
            hits: list[int] = []
            search_from = 0
            while True:
                hit = bytes(rom).find(pattern, search_from)
                if hit < 0:
                    break
                hits.append(hit)
                search_from = hit + 1
            if not hits:
                continue

            raw_patches: list[dict] = []
            row_handled: set[int] = set()
            for hit in hits:
                for update_index in update_indexes:
                    update = updates[update_index]
                    column = int(update["screen_tile_x"]) - min_x
                    patch_offset = hit + column * 2
                    old_entry = int(update["old_entry"])
                    new_entry = int(update["new_entry"])
                    if not 0 <= patch_offset <= len(rom) - 2:
                        continue
                    current_entry = int.from_bytes(rom[patch_offset : patch_offset + 2], "little")
                    if current_entry not in {old_entry, new_entry}:
                        continue
                    raw_patches.append(
                        {
                            "offset": patch_offset,
                            "offset_hex": f"0x{patch_offset:08X}",
                            "old_entry": old_entry,
                            "new_entry": new_entry,
                            "screen_tile_x": int(update["screen_tile_x"]),
                            "screen_tile_y": int(update["screen_tile_y"]),
                            "row_pattern_offset": hit,
                            "row_pattern_offset_hex": f"0x{hit:08X}",
                        }
                    )
                    row_handled.add(update_index)
            if raw_patches:
                direct_plans.append(
                    {
                        "offset": hits[0],
                        "offset_hex": f"0x{hits[0]:08X}",
                        "storage": "raw_direct_screen_entries",
                        "row": row,
                        "row_min_x": min_x,
                        "row_entry_count": len(row_entries),
                        "row_pattern_hits": [f"0x{hit:08X}" for hit in hits],
                        "patch_count": len(raw_patches),
                        "update_indexes": sorted(row_handled),
                        "raw_patches": raw_patches,
                    }
                )
                handled_direct.update(row_handled)
        if direct_plans:
            plans.extend(direct_plans)
            patched_update_indexes.update(handled_direct)

    missing = sorted(set(range(len(updates))) - patched_update_indexes)
    if missing:
        details = [
            f"({updates[index]['screen_tile_x']},{updates[index]['screen_tile_y']}) "
            f"0x{updates[index]['old_entry']:04X}->0x{updates[index]['new_entry']:04X}"
            for index in missing
        ]
        raise ValueError(
            "screen-entry alias split could not find patchable RLE tilemap blocks for: "
            + ", ".join(details)
        )
    return plans


def apply_screen_entry_patch_plans(rom: bytearray, plans: list[dict]) -> list[dict]:
    applied: list[dict] = []
    for plan in plans:
        if "raw_patches" in plan:
            for patch in plan["raw_patches"]:
                offset = int(patch["offset"])
                old_entry = int(patch["old_entry"])
                new_entry = int(patch["new_entry"])
                current_entry = int.from_bytes(rom[offset : offset + 2], "little")
                if current_entry in {old_entry, new_entry}:
                    rom[offset : offset + 2] = new_entry.to_bytes(2, "little")
                else:
                    raise ValueError(
                        "raw screen-entry patch target changed unexpectedly: "
                        f"0x{offset:08X} has 0x{current_entry:04X}, expected 0x{old_entry:04X}"
                    )
            public = {key: value for key, value in plan.items() if key != "raw_patches"}
            public["raw_patch_offsets"] = [patch["offset_hex"] for patch in plan["raw_patches"]]
            applied.append(public)
            continue
        offset = int(plan["offset"])
        compressed = bytes(plan["compressed"])
        consumed = int(plan["consumed_size"])
        rom[offset : offset + len(compressed)] = compressed
        if len(compressed) < consumed:
            rom[offset + len(compressed) : offset + consumed] = b"\x00" * (consumed - len(compressed))
        public = {key: value for key, value in plan.items() if key != "compressed"}
        applied.append(public)
    return applied


def parse_int_value(value) -> int | None:
    try:
        if isinstance(value, str):
            return int(value, 0)
        return int(value)
    except (TypeError, ValueError):
        return None


def protected_screen_entry_patch_blocks(current_item: dict, protected_items: list[dict] | None) -> dict[int, list[dict]]:
    protected: dict[int, list[dict]] = {}
    if not protected_items:
        return protected
    current_item_id = current_item.get("item_id")
    for item in protected_items:
        item_id = item.get("item_id")
        if item_id == current_item_id:
            continue
        if not item.get("replacement_path"):
            continue
        summary = item.get("last_apply_summary") or {}
        if not isinstance(summary, dict):
            continue
        for result in summary.get("results", []):
            if result.get("item_id") != item_id or result.get("status") != "applied":
                continue
            for block in result.get("screen_entry_patch_blocks") or []:
                offset = parse_int_value(block.get("offset_hex") or block.get("offset"))
                if offset is None:
                    continue
                protected.setdefault(offset, []).append(
                    {
                        "item_id": item_id,
                        "label": item.get("label", ""),
                        "replacement_path": item.get("replacement_path", ""),
                    }
                )
    return protected


def validate_screen_entry_patch_safety(
    item: dict,
    plans: list[dict],
    protected_items: list[dict] | None,
) -> None:
    if not plans:
        return
    protected = protected_screen_entry_patch_blocks(item, protected_items)
    if not protected:
        return
    conflicts: list[str] = []
    for plan in plans:
        offset = int(plan["offset"])
        for owner in protected.get(offset, []):
            conflicts.append(
                f"0x{offset:08X} is protected by {owner['item_id']} ({owner['label']})"
            )
    if conflicts:
        raise ValueError(
            "screen-entry patch safety guard blocked a shared tilemap edit: "
            + "; ".join(conflicts)
            + ". Adjust the replacement PNG so it does not require alias-split screen-entry patches, "
            "or intentionally rebuild the affected shared tilemap entries together."
        )


def screen_order_image_to_rle_payload(
    path: Path,
    tile_map: dict,
    original_payload: bytes,
    *,
    payload_base: bytes | None = None,
    source_color_map: dict[tuple[int, tuple[int, int, int]], int] | None = None,
    source_image: Image.Image | None = None,
) -> tuple[bytes, dict]:
    crop = tile_map["crop_pixels"]
    expected_w = int(crop["width"])
    expected_h = int(crop["height"])
    image = resize_replacement(path, expected_w, expected_h)
    palette = palette_for_tile_map(tile_map)
    base_payload = payload_base if payload_base is not None else original_payload
    if len(base_payload) != len(original_payload):
        raise ValueError(
            "screen-order payload base size does not match current RLE payload: "
            f"{len(base_payload)} != {len(original_payload)}"
        )
    payload = bytearray(base_payload)
    min_x = int(tile_map["crop_screen_tiles"]["min_x"])
    min_y = int(tile_map["crop_screen_tiles"]["min_y"])
    crop_x = int(crop.get("x", min_x * 8))
    crop_y = int(crop.get("y", min_y * 8))
    fine = tile_map.get("fine_scroll_pixels") or {}
    adjustment = tile_map.get("alignment_adjustment_pixels") or {}
    fine_x = int(fine.get("x", 0))
    fine_y = int(fine.get("y", 0))
    shift_x = int(adjustment.get("x", 0))
    shift_y = int(adjustment.get("y", 0))
    layout = infer_rle_runtime_tile_layout(tile_map)
    requests_by_tile_index: dict[int, list[dict]] = {}
    for match in tile_map.get("matches", []):
        rel_x = int(match["screen_tile_x"]) * 8 - fine_x + shift_x - crop_x
        rel_y = int(match["screen_tile_y"]) * 8 - fine_y + shift_y - crop_y
        palette_bank = int(match.get("palette_bank", 0))
        for tile_index in rle_tile_indexes_for_match(match, layout):
            start = tile_index * TILE_BYTES
            if start + TILE_BYTES <= len(payload):
                tile = tile_from_image(
                    image,
                    rel_x,
                    rel_y,
                    palette=palette,
                    palette_bank=palette_bank,
                    hflip=bool(match.get("hflip")),
                    vflip=bool(match.get("vflip")),
                    fallback_tile=bytes(base_payload[start : start + TILE_BYTES]),
                    source_color_map=source_color_map,
                    source_image=source_image,
                )
                requests_by_tile_index.setdefault(tile_index, []).append(
                    {
                        "tile": tile,
                        "screen_tile_x": int(match["screen_tile_x"]),
                        "screen_tile_y": int(match["screen_tile_y"]),
                        "screen_entry": int(match["screen_entry"]),
                        "runtime_tile_index": int(match["runtime_tile_index"]),
                    }
                )
    if not requests_by_tile_index:
        raise ValueError("tile_map did not map any replacement tiles")

    next_tile_index = len(payload) // TILE_BYTES
    written: set[int] = set()
    conflicts: list[dict] = []
    splits: list[dict] = []
    screen_entry_updates: list[dict] = []
    entry_rewrites: list[dict] = []
    reserved_tile_indexes: set[int] = set()
    for tile_index, requests in sorted(requests_by_tile_index.items()):
        unique_tiles: dict[bytes, list[dict]] = {}
        for request in requests:
            unique_tiles.setdefault(bytes(request["tile"]), []).append(request)
        if len(unique_tiles) == 1:
            tile = next(iter(unique_tiles))
            payload[tile_index * TILE_BYTES : tile_index * TILE_BYTES + TILE_BYTES] = tile
            if tile != base_payload[tile_index * TILE_BYTES : tile_index * TILE_BYTES + TILE_BYTES]:
                written.add(tile_index)
            continue

        if layout is None:
            positions = [(request["screen_tile_x"], request["screen_tile_y"]) for request in requests]
            raise ValueError(
                f"tile alias conflict at RLE tile {tile_index}; cannot infer runtime tile layout for {positions}"
            )

        conflicts.append(
            {
                "rle_tile_index": tile_index,
                "variant_count": len(unique_tiles),
                "screen_positions": [
                    [request["screen_tile_x"], request["screen_tile_y"]]
                    for request in requests
                ],
            }
        )
        for variant_index, (tile, variant_requests) in enumerate(unique_tiles.items()):
            if variant_index == 0:
                payload[tile_index * TILE_BYTES : tile_index * TILE_BYTES + TILE_BYTES] = tile
                if tile != base_payload[tile_index * TILE_BYTES : tile_index * TILE_BYTES + TILE_BYTES]:
                    written.add(tile_index)
                reserved_tile_indexes.add(tile_index)
                continue

            recycled = allocate_recycled_rle_tile_slot(
                payload,
                tile_map,
                reserved_tile_indexes=reserved_tile_indexes | {tile_index},
            )
            recycled_from_duplicate = recycled is not None
            if recycled_from_duplicate:
                new_tile_index, keeper_tile_index = recycled
                reserved_tile_indexes.add(keeper_tile_index)
                keeper_runtime_tile_index = runtime_tile_index_for_rle_index(layout, keeper_tile_index)
                for old_entry in rle_tile_screen_entries(tile_map, new_tile_index):
                    entry_rewrites.append(
                        {
                            "old_entry": old_entry,
                            "new_entry": screen_entry_with_tile_index(old_entry, keeper_runtime_tile_index),
                            "freed_rle_tile_index": new_tile_index,
                            "keeper_rle_tile_index": keeper_tile_index,
                        }
                    )
                payload[new_tile_index * TILE_BYTES : new_tile_index * TILE_BYTES + TILE_BYTES] = tile
            else:
                new_tile_index = next_tile_index
                next_tile_index += 1
                payload.extend(tile)
            new_runtime_tile_index = runtime_tile_index_for_rle_index(layout, new_tile_index)
            if not 0 <= new_runtime_tile_index <= 0x3FF:
                raise ValueError(
                    "tile alias split would exceed the GBA BG tile index range: "
                    f"RLE tile {new_tile_index} -> runtime tile 0x{new_runtime_tile_index:X}"
                )
            reserved_tile_indexes.add(new_tile_index)
            written.add(new_tile_index)
            split = {
                "source_rle_tile_index": tile_index,
                "new_rle_tile_index": new_tile_index,
                "new_runtime_tile_index": new_runtime_tile_index,
                "recycled_from_duplicate": recycled_from_duplicate,
                "screen_positions": [
                    [request["screen_tile_x"], request["screen_tile_y"]]
                    for request in variant_requests
                ],
            }
            splits.append(split)
            for request in variant_requests:
                new_entry = screen_entry_with_tile_index(request["screen_entry"], new_runtime_tile_index)
                screen_entry_updates.append(
                    {
                        "screen_tile_x": request["screen_tile_x"],
                        "screen_tile_y": request["screen_tile_y"],
                        "old_entry": request["screen_entry"],
                        "new_entry": new_entry,
                        "source_rle_tile_index": tile_index,
                        "new_rle_tile_index": new_tile_index,
                        "new_runtime_tile_index": new_runtime_tile_index,
                    }
                )

    return bytes(payload), {
        "written_tile_count": len(written),
        "written_tile_indexes": sorted(written),
        "tile_count_after_alias_split": len(payload) // TILE_BYTES,
        "alias_conflicts": conflicts,
        "alias_splits": splits,
        "screen_entry_updates": screen_entry_updates,
        "entry_rewrites": entry_rewrites,
        "rle_runtime_tile_layout": layout,
    }


def screen_order_image_to_masked_rle_payload(
    path: Path,
    tile_map: dict,
    original_payload: bytes,
    native_bbox: dict,
    native_clear_bbox: dict | None = None,
    payload_base: bytes | None = None,
    tile_splits: list[dict] | None = None,
) -> tuple[bytes, dict]:
    crop = tile_map["crop_pixels"]
    expected_w = int(crop["width"])
    expected_h = int(crop["height"])
    image = resize_replacement(path, expected_w, expected_h)
    palette = palette_for_tile_map(tile_map)
    base_payload = payload_base if payload_base is not None else original_payload
    if len(base_payload) != len(original_payload):
        raise ValueError(
            "replacement_payload_base size does not match current RLE payload: "
            f"{len(base_payload)} != {len(original_payload)}"
        )
    payload = bytearray(base_payload)
    min_x = int(tile_map["crop_screen_tiles"]["min_x"])
    min_y = int(tile_map["crop_screen_tiles"]["min_y"])
    layout = infer_rle_runtime_tile_layout(tile_map)
    matches: dict[tuple[int, int], list[dict]] = {}
    for match in tile_map.get("matches", []):
        key = (int(match["screen_tile_x"]), int(match["screen_tile_y"]))
        matches.setdefault(key, []).append(match)

    x0 = int(native_bbox["x"])
    y0 = int(native_bbox["y"])
    width = int(native_bbox["width"])
    height = int(native_bbox["height"])
    if width <= 0 or height <= 0:
        raise ValueError(f"invalid replacement_native_patch_bbox: {native_bbox}")

    def write_nibble(tile_index: int, raw_x: int, raw_y: int, nibble: int) -> bool:
        byte_index = tile_index * TILE_BYTES + raw_y * 4 + raw_x // 2
        if not 0 <= byte_index < len(payload):
            return False
        old_byte = payload[byte_index]
        if raw_x % 2:
            old_nibble = (old_byte >> 4) & 0x0F
            payload[byte_index] = (old_byte & 0x0F) | (nibble << 4)
        else:
            old_nibble = old_byte & 0x0F
            payload[byte_index] = (old_byte & 0xF0) | nibble
        return old_nibble != nibble

    def native_matches(x: int, y: int) -> list[tuple[dict, int, int]]:
        screen_tile_x = min_x + x // 8
        screen_tile_y = min_y + y // 8
        out: list[tuple[dict, int, int]] = []
        for match in matches.get((screen_tile_x, screen_tile_y), []):
            local_x = x % 8
            local_y = y % 8
            raw_x = 7 - local_x if bool(match.get("hflip")) else local_x
            raw_y = 7 - local_y if bool(match.get("vflip")) else local_y
            out.append((match, raw_x, raw_y))
        return out

    clear_pixel_changes = 0
    clear_bbox_out: dict | None = None
    if native_clear_bbox:
        clear_x = int(native_clear_bbox["x"])
        clear_y = int(native_clear_bbox["y"])
        clear_w = int(native_clear_bbox["width"])
        clear_h = int(native_clear_bbox["height"])
        if clear_w <= 0 or clear_h <= 0:
            raise ValueError(f"invalid replacement_native_clear_bbox: {native_clear_bbox}")
        clear_bbox_out = {"x": clear_x, "y": clear_y, "width": clear_w, "height": clear_h}
        clear_source = original_payload
        raw_path = tile_map.get("rle_raw_path", "")
        if raw_path:
            candidate = (ROOT / raw_path).resolve()
            if candidate.is_file():
                clear_source = candidate.read_bytes()
        for y in range(clear_y, clear_y + clear_h):
            for x in range(clear_x, clear_x + clear_w):
                if not (0 <= x < expected_w and 0 <= y < expected_h):
                    continue
                for match, raw_x, raw_y in native_matches(x, y):
                    for tile_index in rle_tile_indexes_for_match(match, layout):
                        start = tile_index * TILE_BYTES
                        if start + TILE_BYTES > len(clear_source):
                            continue
                        source_nibble = nibble_from_tile(clear_source[start : start + TILE_BYTES], raw_x, raw_y)
                        if write_nibble(tile_index, raw_x, raw_y, source_nibble):
                            clear_pixel_changes += 1

    written_pixels = 0
    written_tile_indexes: set[int] = set()
    pixels = image.load()
    for y in range(y0, y0 + height):
        for x in range(x0, x0 + width):
            if not (0 <= x < expected_w and 0 <= y < expected_h):
                continue
            for match, raw_x, raw_y in native_matches(x, y):
                palette_bank = int(match.get("palette_bank", 0))
                nibble = rgba_to_nibble(pixels[x, y], palette=palette, palette_bank=palette_bank)
                for tile_index in rle_tile_indexes_for_match(match, layout):
                    if write_nibble(tile_index, raw_x, raw_y, nibble):
                        written_pixels += 1
                    written_tile_indexes.add(tile_index)

    alias_splits: list[dict] = []
    screen_entry_updates: list[dict] = []
    for split in tile_splits or []:
        source_tile_index = int(split["source_rle_tile_index"])
        new_tile_index = int(split["new_rle_tile_index"])
        if source_tile_index == new_tile_index:
            raise ValueError(f"replacement_tile_splits cannot split tile {source_tile_index} into itself")
        source_start = source_tile_index * TILE_BYTES
        new_start = new_tile_index * TILE_BYTES
        if source_start + TILE_BYTES > len(payload):
            raise ValueError(f"replacement_tile_splits source tile is outside payload: {source_tile_index}")
        if new_start + TILE_BYTES > len(payload):
            raise ValueError(f"replacement_tile_splits new tile is outside payload: {new_tile_index}")

        screen_tile_x = int(split["screen_tile_x"])
        screen_tile_y = int(split["screen_tile_y"])
        candidates = []
        for match in matches.get((screen_tile_x, screen_tile_y), []):
            resolved = rle_tile_indexes_for_match(match, layout)
            if source_tile_index in resolved or source_tile_index in {int(value) for value in match.get("rle_tile_indexes", [])}:
                candidates.append(match)
        if len(candidates) != 1:
            raise ValueError(
                "replacement_tile_splits could not resolve one screen entry for "
                f"tile {source_tile_index} at ({screen_tile_x},{screen_tile_y}); found {len(candidates)}"
            )
        match = candidates[0]
        if layout is None:
            new_runtime_tile_index = int(split.get("new_runtime_tile_index", new_tile_index))
        else:
            new_runtime_tile_index = runtime_tile_index_for_rle_index(layout, new_tile_index)
        if not 0 <= new_runtime_tile_index <= 0x3FF:
            raise ValueError(
                "replacement_tile_splits would exceed the GBA BG tile index range: "
                f"RLE tile {new_tile_index} -> runtime tile 0x{new_runtime_tile_index:X}"
            )

        modified_source_tile = bytes(payload[source_start : source_start + TILE_BYTES])
        payload[new_start : new_start + TILE_BYTES] = modified_source_tile
        payload[source_start : source_start + TILE_BYTES] = base_payload[source_start : source_start + TILE_BYTES]
        if payload[source_start : source_start + TILE_BYTES] == base_payload[source_start : source_start + TILE_BYTES]:
            written_tile_indexes.discard(source_tile_index)
        if payload[new_start : new_start + TILE_BYTES] != base_payload[new_start : new_start + TILE_BYTES]:
            written_tile_indexes.add(new_tile_index)
        new_entry = screen_entry_with_tile_index(int(match["screen_entry"]), new_runtime_tile_index)
        alias_splits.append(
            {
                "source_rle_tile_index": source_tile_index,
                "new_rle_tile_index": new_tile_index,
                "new_runtime_tile_index": new_runtime_tile_index,
                "manual_tile_split": True,
                "screen_positions": [[screen_tile_x, screen_tile_y]],
            }
        )
        screen_entry_updates.append(
            {
                "screen_tile_x": screen_tile_x,
                "screen_tile_y": screen_tile_y,
                "old_entry": int(match["screen_entry"]),
                "new_entry": new_entry,
                "source_rle_tile_index": source_tile_index,
                "new_rle_tile_index": new_tile_index,
                "new_runtime_tile_index": new_runtime_tile_index,
            }
        )

    if not written_tile_indexes:
        raise ValueError("masked screen-order patch did not map any replacement pixels")

    return bytes(payload), {
        "written_tile_count": len(written_tile_indexes),
        "tile_count_after_alias_split": len(payload) // TILE_BYTES,
        "alias_conflicts": [],
        "alias_splits": alias_splits,
        "screen_entry_updates": screen_entry_updates,
        "entry_rewrites": [],
        "rle_runtime_tile_layout": layout,
        "masked_native_bbox": {
            "x": x0,
            "y": y0,
            "width": width,
            "height": height,
        },
        "masked_native_pixel_changes": written_pixels,
        "masked_native_clear_bbox": clear_bbox_out,
        "masked_native_clear_pixel_changes": clear_pixel_changes,
    }


def direct_rle_tiles_from_image(
    path: Path,
    tile_map: dict | None,
    original_payload: bytes,
    tile_specs: list[dict],
    payload_base: bytes | None = None,
) -> tuple[bytes, dict]:
    image = Image.open(path).convert("RGBA")
    palette = palette_for_tile_map(tile_map) if tile_map else None
    base_payload = payload_base if payload_base is not None else original_payload
    if len(base_payload) != len(original_payload):
        raise ValueError(
            "replacement_payload_base size does not match current RLE payload: "
            f"{len(base_payload)} != {len(original_payload)}"
        )
    payload = bytearray(base_payload)
    written: list[int] = []
    for spec in tile_specs:
        tile_index = int(spec["tile_index"])
        source_x = int(spec["source_x"])
        source_y = int(spec["source_y"])
        palette_bank = int(spec.get("palette_bank", 0))
        start = tile_index * TILE_BYTES
        if start + TILE_BYTES > len(payload):
            raise ValueError(f"replacement_direct_rle_tiles tile is outside payload: {tile_index}")
        tile = tile_from_image(
            image,
            source_x,
            source_y,
            palette=palette,
            palette_bank=palette_bank,
            fallback_tile=bytes(base_payload[start : start + TILE_BYTES]),
        )
        payload[start : start + TILE_BYTES] = tile
        if tile != base_payload[start : start + TILE_BYTES]:
            written.append(tile_index)
    if not written:
        raise ValueError("replacement_direct_rle_tiles did not change any RLE tiles")
    return bytes(payload), {
        "written_tile_count": len(set(written)),
        "written_tile_indexes": sorted(set(written)),
        "tile_count_after_alias_split": len(payload) // TILE_BYTES,
        "alias_conflicts": [],
        "alias_splits": [],
        "screen_entry_updates": [],
        "entry_rewrites": [],
        "direct_rle_tile_patch": True,
    }


def apply_rle_item(rom: bytearray, item: dict, protected_items: list[dict] | None = None) -> dict:
    replacement = item.get("replacement_path", "")
    if not replacement:
        return {"item_id": item["item_id"], "status": "skipped", "reason": "no replacement_path"}
    replacement_path = (ROOT / replacement).resolve()
    if not replacement_path.is_file() or ROOT not in replacement_path.parents:
        return {"item_id": item["item_id"], "status": "error", "reason": "replacement file not found"}

    offset = rle_offset_from_item(item)
    if offset is None:
        return {"item_id": item["item_id"], "status": "skipped", "reason": "no RLE offset"}
    current = decompress_gba_rle(bytes(rom), offset, max_output_size=0x400000)
    if not current:
        return {"item_id": item["item_id"], "status": "error", "reason": "target is not a GBA RLE block"}
    original_payload, current_consumed = current
    original_consumed = reference_consumed_size(
        offset=offset,
        current_payload_size=len(original_payload),
        current_consumed=current_consumed,
        decompressor=decompress_gba_rle,
    )
    if len(original_payload) % TILE_BYTES:
        return {"item_id": item["item_id"], "status": "error", "reason": "RLE payload is not 4bpp tile aligned"}

    tile_count = len(original_payload) // TILE_BYTES
    tile_map = load_tile_map(item)
    columns = None
    screen_order_meta: dict = {}
    screen_entry_patch_plans: list[dict] = []
    direct_tile_specs = item.get("replacement_direct_rle_tiles") or []
    if direct_tile_specs:
        payload_base = None
        if item.get("replacement_payload_base") == "source_raw":
            if not tile_map:
                raise ValueError("replacement_payload_base=source_raw requires tile_map.rle_raw_path")
            raw_path = tile_map.get("rle_raw_path", "")
            if not raw_path:
                raise ValueError("replacement_payload_base=source_raw requires tile_map.rle_raw_path")
            payload_base_path = (ROOT / raw_path).resolve()
            if not payload_base_path.is_file():
                raise FileNotFoundError(f"source raw payload not found: {raw_path}")
            payload_base = payload_base_path.read_bytes()
        payload, screen_order_meta = direct_rle_tiles_from_image(
            replacement_path,
            tile_map,
            original_payload,
            direct_tile_specs,
            payload_base,
        )
    elif tile_map:
        native_patch_bbox = item.get("replacement_native_patch_bbox")
        if native_patch_bbox:
            payload_base = None
            if item.get("replacement_payload_base") == "source_raw":
                raw_path = tile_map.get("rle_raw_path", "")
                if not raw_path:
                    raise ValueError("replacement_payload_base=source_raw requires tile_map.rle_raw_path")
                payload_base_path = (ROOT / raw_path).resolve()
                if not payload_base_path.is_file():
                    raise FileNotFoundError(f"source raw payload not found: {raw_path}")
                payload_base = payload_base_path.read_bytes()
            payload, screen_order_meta = screen_order_image_to_masked_rle_payload(
                replacement_path,
                tile_map,
                original_payload,
                native_patch_bbox,
                item.get("replacement_native_clear_bbox"),
                payload_base,
                item.get("replacement_tile_splits") or [],
            )
        else:
            payload_base = screen_order_payload_base(item, tile_map, original_payload)
            source_color_map = None
            source_path = None
            source_image = None
            default_source_safety = is_screen_order_rle_item(item, tile_map)
            use_source_color_map = option_bool(
                item,
                "replacement_source_color_map",
                default=default_source_safety,
            )
            verify_source_noop = option_bool(
                item,
                "replacement_verify_source_noop",
                default=default_source_safety,
            )
            if use_source_color_map:
                source_path = screen_order_source_image_path(item, tile_map)
                if source_path:
                    source_color_map = source_color_nibble_map_from_image(source_path, tile_map, payload_base)
                    crop = tile_map["crop_pixels"]
                    source_image = resize_replacement(source_path, int(crop["width"]), int(crop["height"]))
            if verify_source_noop:
                if not source_path or not source_color_map or source_image is None:
                    raise ValueError("replacement_verify_source_noop requires source image color map")
                source_payload, _ = screen_order_image_to_rle_payload(
                    source_path,
                    tile_map,
                    original_payload,
                    payload_base=payload_base,
                    source_color_map=source_color_map,
                    source_image=source_image,
                )
                source_changed = changed_tile_indexes(payload_base, source_payload)
                if source_changed:
                    raise ValueError(
                        "screen-order source no-op verification failed; applying this item would recolor unchanged tiles: "
                        + ", ".join(f"0x{index:03X}" for index in source_changed[:24])
                        + (" ..." if len(source_changed) > 24 else "")
                    )
            payload, screen_order_meta = screen_order_image_to_rle_payload(
                replacement_path,
                tile_map,
                original_payload,
                payload_base=payload_base,
                source_color_map=source_color_map,
                source_image=source_image,
            )
        if screen_order_meta.get("screen_entry_updates"):
            manual_raw_offsets = item.get("screen_entry_manual_raw_patch_offsets") or []
            if manual_raw_offsets:
                if len(screen_order_meta["screen_entry_updates"]) != 1:
                    raise ValueError(
                        "screen_entry_manual_raw_patch_offsets requires exactly one screen_entry_update"
                    )
                update = screen_order_meta["screen_entry_updates"][0]
                raw_patches = []
                for raw_offset_value in manual_raw_offsets:
                    raw_offset = parse_int_value(raw_offset_value)
                    if raw_offset is None:
                        raise ValueError(f"invalid manual raw screen-entry patch offset: {raw_offset_value}")
                    raw_patches.append(
                        {
                            "offset": raw_offset,
                            "offset_hex": f"0x{raw_offset:08X}",
                            "old_entry": int(update["old_entry"]),
                            "new_entry": int(update["new_entry"]),
                            "screen_tile_x": int(update["screen_tile_x"]),
                            "screen_tile_y": int(update["screen_tile_y"]),
                            "manual_raw_patch": True,
                        }
                    )
                screen_entry_patch_plans = [
                    {
                        "offset": raw_patches[0]["offset"],
                        "offset_hex": raw_patches[0]["offset_hex"],
                        "storage": "manual_raw_screen_entries",
                        "patch_count": len(raw_patches),
                        "raw_patches": raw_patches,
                    }
                ]
            else:
                screen_entry_patch_tile_map = tile_map
                screen_entry_patch_tile_map_path = item.get("screen_entry_patch_tile_map_path", "")
                if screen_entry_patch_tile_map_path:
                    patch_tile_map_path = (ROOT / screen_entry_patch_tile_map_path).resolve()
                    if not patch_tile_map_path.is_file() or ROOT not in patch_tile_map_path.parents:
                        raise FileNotFoundError(
                            f"screen_entry_patch_tile_map_path not found: {screen_entry_patch_tile_map_path}"
                        )
                    screen_entry_patch_tile_map = json.loads(patch_tile_map_path.read_text(encoding="utf-8"))
                screen_entry_patch_plans = plan_screen_entry_alias_split_patches(
                    rom,
                    screen_entry_patch_tile_map,
                    screen_order_meta["screen_entry_updates"],
                    graphics_rle_offset=offset,
                    entry_rewrites=screen_order_meta.get("entry_rewrites", []),
                )
            validate_screen_entry_patch_safety(item, screen_entry_patch_plans, protected_items)
    else:
        columns = columns_from_item(item, tile_count)
        rows = (tile_count + columns - 1) // columns
        width = columns * 8
        height = rows * 8
        indices = image_to_indices(replacement_path, width, height)
        payload = indices_to_4bpp_tiles(indices, width, height, columns, tile_count)
    compressed = compress_gba_rle(payload)
    if len(compressed) > original_consumed:
        result = append_repoint_blob(
            rom,
            item,
            original_offset=offset,
            original_consumed=original_consumed,
            compressed=compressed,
            payload=payload,
            compression="rle",
            compression_tag=0x30,
            decompressor=decompress_gba_rle,
        )
        if result.get("status") == "applied":
            result["columns"] = columns
            result["tile_map_path"] = item.get("tile_map_path", "")
            if screen_order_meta:
                result["screen_order_meta"] = {
                    key: value
                    for key, value in screen_order_meta.items()
                    if key != "screen_entry_updates"
                }
            if screen_entry_patch_plans:
                result["screen_entry_patch_blocks"] = apply_screen_entry_patch_plans(rom, screen_entry_patch_plans)
        return result

    rom[offset : offset + len(compressed)] = compressed
    if len(compressed) < original_consumed:
        rom[offset + len(compressed) : offset + original_consumed] = b"\x00" * (original_consumed - len(compressed))
    verify = decompress_gba_rle(bytes(rom), offset, max_output_size=0x400000)
    if not verify or verify[0] != payload:
        return {"item_id": item["item_id"], "status": "error", "reason": "verification failed"}
    restored_pointer_patches = restore_same_offset_pointer_patches(
        rom,
        item,
        original_offset=offset,
        original_consumed=original_consumed,
        compression_tag=0x30,
        decompressor=decompress_gba_rle,
    )
    result = {
        "item_id": item["item_id"],
        "status": "applied",
        "compression": "rle",
        "storage": "same_offset",
        "offset": offset,
        "offset_hex": f"0x{offset:08X}",
        "columns": columns,
        "tile_map_path": item.get("tile_map_path", ""),
        "decompressed_size": len(payload),
        "compressed_size": len(compressed),
        "available_size": original_consumed,
        "current_consumed_size": current_consumed,
    }
    if restored_pointer_patches:
        result["restored_same_offset_pointers"] = restored_pointer_patches
    if screen_order_meta:
        result["screen_order_meta"] = {
            key: value
            for key, value in screen_order_meta.items()
            if key != "screen_entry_updates"
        }
    if screen_entry_patch_plans:
        result["screen_entry_patch_blocks"] = apply_screen_entry_patch_plans(rom, screen_entry_patch_plans)
    return result


def apply_lz77_item(rom: bytearray, item: dict) -> dict:
    replacement = item.get("replacement_path", "")
    if not replacement:
        return {"item_id": item["item_id"], "status": "skipped", "reason": "no replacement_path"}
    replacement_path = (ROOT / replacement).resolve()
    if not replacement_path.is_file() or ROOT not in replacement_path.parents:
        return {"item_id": item["item_id"], "status": "error", "reason": "replacement file not found"}

    offset = rle_offset_from_item(item)
    if offset is None:
        return {"item_id": item["item_id"], "status": "skipped", "reason": "no image offset"}
    try:
        original_payload, current_consumed = decompress_lz77(bytes(rom), offset, max_output_size=0x400000)
    except Exception:
        return {"item_id": item["item_id"], "status": "skipped", "reason": "target is not a GBA LZ77 block"}
    if len(original_payload) % TILE_BYTES:
        return {"item_id": item["item_id"], "status": "error", "reason": "LZ77 payload is not 4bpp tile aligned"}
    original_consumed = reference_consumed_size(
        offset=offset,
        current_payload_size=len(original_payload),
        current_consumed=current_consumed,
        decompressor=decompress_lz77,
    )

    tile_count = len(original_payload) // TILE_BYTES
    columns = columns_from_item(item, tile_count)
    rows = (tile_count + columns - 1) // columns
    width = columns * 8
    height = rows * 8
    indices = image_to_indices(replacement_path, width, height)
    payload = indices_to_4bpp_tiles(indices, width, height, columns, tile_count)
    field_label_target = offset in FIELD_LABEL_LZ77_TABLE_REPOINTS
    compressed = compress_lz77_literal(payload) if field_label_target else compress_lz77(payload)
    pointed_entry_offset = field_label_pointed_entry_offset(rom, offset)
    field_label_is_repointed = pointed_entry_offset is not None and pointed_entry_offset != offset - 4
    if len(compressed) > original_consumed or field_label_is_repointed:
        field_label_result = append_field_label_lz77_repoint_blob(
            rom,
            item,
            original_offset=offset,
            original_consumed=original_consumed,
            compressed=compressed,
            payload=payload,
        )
        if field_label_result is not None:
            if field_label_result.get("status") == "applied":
                field_label_result["columns"] = columns
                field_label_result["lz77_encoder"] = "literal"
            return attach_lz77_distance_one_check(
                field_label_result,
                item_id=item["item_id"],
                original_offset=offset,
                compressed=compressed,
                encoder="literal",
            )
    if len(compressed) > original_consumed:
        result = append_repoint_blob(
            rom,
            item,
            original_offset=offset,
            original_consumed=original_consumed,
            compressed=compressed,
            payload=payload,
            compression="lz77",
            compression_tag=0x10,
            decompressor=decompress_lz77,
        )
        if result.get("status") == "applied":
            result["columns"] = columns
        return attach_lz77_distance_one_check(
            result,
            item_id=item["item_id"],
            original_offset=offset,
            compressed=compressed,
            encoder="optimal",
        )

    rom[offset : offset + len(compressed)] = compressed
    if len(compressed) < original_consumed:
        rom[offset + len(compressed) : offset + original_consumed] = b"\x00" * (original_consumed - len(compressed))
    verify = decompress_lz77(bytes(rom), offset, max_output_size=0x400000)
    if verify[0] != payload:
        return {"item_id": item["item_id"], "status": "error", "reason": "verification failed"}
    result = {
        "item_id": item["item_id"],
        "status": "applied",
        "compression": "lz77",
        "lz77_encoder": "optimal",
        "offset": offset,
        "offset_hex": f"0x{offset:08X}",
        "columns": columns,
        "decompressed_size": len(payload),
        "compressed_size": len(compressed),
        "available_size": original_consumed,
        "current_consumed_size": current_consumed,
    }
    return attach_lz77_distance_one_check(
        result,
        item_id=item["item_id"],
        original_offset=offset,
        compressed=compressed,
        encoder="optimal",
    )


def lz77_tile_index_from_item(item: dict) -> int | None:
    for field in ("tile_index", "tile_slot", "tile"):
        value = parse_int_value(item.get(field))
        if value is not None:
            return value
    for field in ("tile_index_hex", "tile_slot_hex"):
        raw = item.get(field)
        if raw not in ("", None):
            try:
                return int(str(raw), 0)
            except ValueError:
                return None
    for value in (item.get("item_id", ""), item.get("group_id", ""), item.get("label", "")):
        match = TILE_INDEX_RE.search(str(value))
        if match:
            return int(match.group("tile"), 16)
    return None


def lz77_tile_replacement_from_item(
    item: dict,
    *,
    offset: int,
    original_payload: bytes,
    tile_count: int,
) -> dict:
    replacement = item.get("replacement_path", "")
    if not replacement:
        return {"item_id": item["item_id"], "status": "skipped", "reason": "no replacement_path"}
    replacement_path = (ROOT / replacement).resolve()
    if not replacement_path.is_file() or ROOT not in replacement_path.parents:
        return {"item_id": item["item_id"], "status": "error", "reason": "replacement file not found"}

    tile_index = lz77_tile_index_from_item(item)
    if tile_index is None:
        return {"item_id": item["item_id"], "status": "error", "reason": "missing tile_index"}
    if not (0 <= tile_index < tile_count):
        return {
            "item_id": item["item_id"],
            "status": "error",
            "reason": f"tile_index 0x{tile_index:03X} outside block tile count {tile_count}",
        }

    reserved_common_hud_tile = (
        offset == COMMON_HUD_TILE_LZ77_OFFSET and tile_index in COMMON_HUD_RESERVED_TILE_INDEXES
    )
    zero_to_shadow_remap = False
    if reserved_common_hud_tile:
        replacement_tile = None
        for rom_path in REFERENCE_CAPACITY_ROMS:
            if not rom_path.is_file():
                continue
            try:
                reference_payload, _ = decompress_lz77(
                    rom_path.read_bytes(),
                    offset,
                    max_output_size=0x400000,
                )
            except Exception:
                continue
            if len(reference_payload) != len(original_payload):
                continue
            start = tile_index * TILE_BYTES
            replacement_tile = reference_payload[start : start + TILE_BYTES]
            break
        if replacement_tile is None:
            return {
                "item_id": item["item_id"],
                "status": "error",
                "reason": f"reserved common HUD tile 0x{tile_index:03X} could not be restored from reference ROMs",
            }
    else:
        indices = image_to_indices(replacement_path, 8, 8)
        zero_to_shadow_remap = (
            offset == COMMON_HUD_TILE_LZ77_OFFSET
            and common_hud_tile_uses_zero_to_shadow_remap(tile_index)
        )
        if zero_to_shadow_remap:
            indices = remap_zero_indices(indices, 1)
        replacement_tile = indices_to_4bpp_tiles(indices, 8, 8, 1, 1)

    return {
        "item_id": item["item_id"],
        "status": "ready",
        "tile_index": tile_index,
        "replacement_tile": replacement_tile,
        "reserved_tile_restored": reserved_common_hud_tile,
        "replacement_ignored": reserved_common_hud_tile,
        "zero_to_shadow_remap": zero_to_shadow_remap,
    }


def write_lz77_tile_payload(
    rom: bytearray,
    *,
    offset: int,
    payload: bytes,
    original_payload: bytes,
    current_consumed: int,
    item_ids: list[str],
) -> dict:
    original_consumed = reference_consumed_size(
        offset=offset,
        current_payload_size=len(original_payload),
        current_consumed=current_consumed,
        decompressor=decompress_lz77,
    )
    use_common_hud_encoder = offset == COMMON_HUD_TILE_LZ77_OFFSET
    compressed = (
        compress_lz77_avoid_distance_one(payload)
        if use_common_hud_encoder
        else compress_lz77(payload)
    )
    encoder_name = "no_dist1" if use_common_hud_encoder else "optimal"
    if len(compressed) > original_consumed:
        return {
            "status": "error",
            "reason": f"LZ77 tile patch compressed stream too large: {len(compressed)} > {original_consumed}",
            "compression": "lz77_tile",
            "lz77_encoder": encoder_name,
            "storage": "same_offset",
            "offset": offset,
            "offset_hex": f"0x{offset:08X}",
            "compressed_size": len(compressed),
            "available_size": original_consumed,
            "size_overage": len(compressed) - original_consumed,
        }

    rom[offset : offset + len(compressed)] = compressed
    tail_fill = "none"
    if len(compressed) < original_consumed:
        reference_tail = None
        if use_common_hud_encoder:
            for rom_path in REFERENCE_CAPACITY_ROMS:
                if not rom_path.is_file():
                    continue
                reference_bytes = rom_path.read_bytes()
                try:
                    reference_payload, reference_consumed = decompress_lz77(
                        reference_bytes,
                        offset,
                        max_output_size=0x400000,
                    )
                except Exception:
                    continue
                if len(reference_payload) == len(payload) and reference_consumed >= original_consumed:
                    reference_tail = reference_bytes[offset + len(compressed) : offset + original_consumed]
                    break
        if reference_tail is not None:
            rom[offset + len(compressed) : offset + original_consumed] = reference_tail
            tail_fill = "reference"
        else:
            rom[offset + len(compressed) : offset + original_consumed] = b"\x00" * (
                original_consumed - len(compressed)
            )
            tail_fill = "zero"

    verify = decompress_lz77(bytes(rom), offset, max_output_size=0x400000)
    if verify[0] != payload:
        return {"status": "error", "reason": "verification failed"}

    stability = build_lz77_distance_one_check(
        item_id=item_ids[0] if item_ids else "",
        original_offset=offset,
        compressed=compressed,
        encoder=encoder_name,
    )
    return {
        "status": "applied",
        "compression": "lz77_tile",
        "lz77_encoder": encoder_name,
        "storage": "same_offset",
        "offset": offset,
        "offset_hex": f"0x{offset:08X}",
        "decompressed_size": len(payload),
        "compressed_size": len(compressed),
        "available_size": original_consumed,
        "current_consumed_size": current_consumed,
        "tail_fill": tail_fill,
        "lz77_stability": stability,
    }


def apply_lz77_tile_items(rom: bytearray, items: list[dict]) -> list[dict]:
    if not items:
        return []
    offsets = {rle_offset_from_item(item) for item in items}
    offsets.discard(None)
    if len(offsets) != 1:
        return [
            {
                "item_id": item["item_id"],
                "status": "error",
                "reason": "LZ77 tile batch must share one block offset",
            }
            for item in items
        ]
    offset = next(iter(offsets))
    try:
        original_payload, current_consumed = decompress_lz77(bytes(rom), offset, max_output_size=0x400000)
    except Exception:
        return [
            {
                "item_id": item["item_id"],
                "status": "skipped",
                "reason": "target is not a GBA LZ77 block",
            }
            for item in items
        ]
    if len(original_payload) % TILE_BYTES:
        return [
            {
                "item_id": item["item_id"],
                "status": "error",
                "reason": "LZ77 payload is not 4bpp tile aligned",
            }
            for item in items
        ]
    tile_count = len(original_payload) // TILE_BYTES
    prepared = [
        lz77_tile_replacement_from_item(
            item,
            offset=offset,
            original_payload=original_payload,
            tile_count=tile_count,
        )
        for item in items
    ]
    blocking = [result for result in prepared if result.get("status") != "ready"]
    if blocking:
        return blocking

    payload = bytearray(original_payload)
    per_item: list[dict] = []
    for item, replacement in zip(items, prepared):
        tile_index = int(replacement["tile_index"])
        start = tile_index * TILE_BYTES
        before_tile = bytes(payload[start : start + TILE_BYTES])
        replacement_tile = bytes(replacement["replacement_tile"])
        payload[start : start + TILE_BYTES] = replacement_tile
        per_item.append(
            {
                "item_id": item["item_id"],
                "tile_index": tile_index,
                "tile_index_hex": f"0x{tile_index:03X}",
                "tile_changed": before_tile != replacement_tile,
                "reserved_tile_restored": bool(replacement.get("reserved_tile_restored")),
                "replacement_ignored": bool(replacement.get("replacement_ignored")),
                "zero_to_shadow_remap": bool(replacement.get("zero_to_shadow_remap")),
            }
        )

    range_zero_to_shadow_pixels = 0
    if offset == COMMON_HUD_TILE_LZ77_OFFSET:
        payload, range_zero_to_shadow_pixels = remap_common_hud_zero_to_shadow_ranges(payload)

    write_result = write_lz77_tile_payload(
        rom,
        offset=offset,
        payload=bytes(payload),
        original_payload=original_payload,
        current_consumed=current_consumed,
        item_ids=[item["item_id"] for item in items],
    )
    if write_result.get("status") != "applied":
        return [
            {
                "item_id": item["item_id"],
                **write_result,
            }
            for item in items
        ]

    shared_stability = write_result.get("lz77_stability")
    results: list[dict] = []
    for item_result in per_item:
        stability = dict(shared_stability) if isinstance(shared_stability, dict) else None
        if stability is not None:
            stability["item_id"] = item_result["item_id"]
        result = {
            **write_result,
            **item_result,
            "batch_applied_count": len(per_item),
            "batch_tile_indices": [entry["tile_index_hex"] for entry in per_item],
            "range_zero_to_shadow_pixels": range_zero_to_shadow_pixels,
        }
        if stability is not None:
            result["lz77_stability"] = stability
        results.append(result)
    return results


def apply_lz77_tile_item(rom: bytearray, item: dict) -> dict:
    replacement = item.get("replacement_path", "")
    if not replacement:
        return {"item_id": item["item_id"], "status": "skipped", "reason": "no replacement_path"}
    replacement_path = (ROOT / replacement).resolve()
    if not replacement_path.is_file() or ROOT not in replacement_path.parents:
        return {"item_id": item["item_id"], "status": "error", "reason": "replacement file not found"}

    offset = rle_offset_from_item(item)
    if offset is None:
        return {"item_id": item["item_id"], "status": "skipped", "reason": "no LZ77 block offset"}
    tile_index = lz77_tile_index_from_item(item)
    if tile_index is None:
        return {"item_id": item["item_id"], "status": "error", "reason": "missing tile_index"}

    try:
        original_payload, current_consumed = decompress_lz77(bytes(rom), offset, max_output_size=0x400000)
    except Exception:
        return {"item_id": item["item_id"], "status": "skipped", "reason": "target is not a GBA LZ77 block"}
    if len(original_payload) % TILE_BYTES:
        return {"item_id": item["item_id"], "status": "error", "reason": "LZ77 payload is not 4bpp tile aligned"}
    tile_count = len(original_payload) // TILE_BYTES
    if not (0 <= tile_index < tile_count):
        return {
            "item_id": item["item_id"],
            "status": "error",
            "reason": f"tile_index 0x{tile_index:03X} outside block tile count {tile_count}",
        }

    reserved_common_hud_tile = (
        offset == COMMON_HUD_TILE_LZ77_OFFSET and tile_index in COMMON_HUD_RESERVED_TILE_INDEXES
    )
    zero_to_shadow_remap = False
    if reserved_common_hud_tile:
        replacement_tile = None
        for rom_path in REFERENCE_CAPACITY_ROMS:
            if not rom_path.is_file():
                continue
            try:
                reference_payload, _ = decompress_lz77(
                    rom_path.read_bytes(),
                    offset,
                    max_output_size=0x400000,
                )
            except Exception:
                continue
            if len(reference_payload) != len(original_payload):
                continue
            start = tile_index * TILE_BYTES
            replacement_tile = reference_payload[start : start + TILE_BYTES]
            break
        if replacement_tile is None:
            return {
                "item_id": item["item_id"],
                "status": "error",
                "reason": f"reserved common HUD tile 0x{tile_index:03X} could not be restored from reference ROMs",
            }
    else:
        indices = image_to_indices(replacement_path, 8, 8)
        zero_to_shadow_remap = (
            offset == COMMON_HUD_TILE_LZ77_OFFSET
            and common_hud_tile_uses_zero_to_shadow_remap(tile_index)
        )
        if zero_to_shadow_remap:
            indices = remap_zero_indices(indices, 1)
        replacement_tile = indices_to_4bpp_tiles(indices, 8, 8, 1, 1)
    payload = bytearray(original_payload)
    start = tile_index * TILE_BYTES
    before_tile = bytes(payload[start : start + TILE_BYTES])
    payload[start : start + TILE_BYTES] = replacement_tile
    range_zero_to_shadow_pixels = 0
    if offset == COMMON_HUD_TILE_LZ77_OFFSET:
        payload, range_zero_to_shadow_pixels = remap_common_hud_zero_to_shadow_ranges(payload)

    original_consumed = reference_consumed_size(
        offset=offset,
        current_payload_size=len(original_payload),
        current_consumed=current_consumed,
        decompressor=decompress_lz77,
    )
    use_common_hud_encoder = offset == COMMON_HUD_TILE_LZ77_OFFSET
    compressed = (
        compress_lz77_avoid_distance_one(bytes(payload))
        if use_common_hud_encoder
        else compress_lz77(bytes(payload))
    )
    encoder_name = "no_dist1" if use_common_hud_encoder else "optimal"
    if len(compressed) > original_consumed:
        return {
            "item_id": item["item_id"],
            "status": "error",
            "reason": f"LZ77 tile patch compressed stream too large: {len(compressed)} > {original_consumed}",
            "compression": "lz77_tile",
            "lz77_encoder": encoder_name,
            "storage": "same_offset",
            "offset": offset,
            "offset_hex": f"0x{offset:08X}",
            "tile_index": tile_index,
            "tile_index_hex": f"0x{tile_index:03X}",
            "compressed_size": len(compressed),
            "available_size": original_consumed,
            "size_overage": len(compressed) - original_consumed,
        }

    rom[offset : offset + len(compressed)] = compressed
    tail_fill = "none"
    if len(compressed) < original_consumed:
        reference_tail = None
        if use_common_hud_encoder:
            for rom_path in REFERENCE_CAPACITY_ROMS:
                if not rom_path.is_file():
                    continue
                reference_bytes = rom_path.read_bytes()
                try:
                    reference_payload, reference_consumed = decompress_lz77(
                        reference_bytes,
                        offset,
                        max_output_size=0x400000,
                    )
                except Exception:
                    continue
                if len(reference_payload) == len(payload) and reference_consumed >= original_consumed:
                    reference_tail = reference_bytes[offset + len(compressed) : offset + original_consumed]
                    break
        if reference_tail is not None:
            rom[offset + len(compressed) : offset + original_consumed] = reference_tail
            tail_fill = "reference"
        else:
            rom[offset + len(compressed) : offset + original_consumed] = b"\x00" * (
                original_consumed - len(compressed)
            )
            tail_fill = "zero"
    verify = decompress_lz77(bytes(rom), offset, max_output_size=0x400000)
    if verify[0] != bytes(payload):
        return {"item_id": item["item_id"], "status": "error", "reason": "verification failed"}
    result = {
        "item_id": item["item_id"],
        "status": "applied",
        "compression": "lz77_tile",
        "lz77_encoder": encoder_name,
        "storage": "same_offset",
        "offset": offset,
        "offset_hex": f"0x{offset:08X}",
        "tile_index": tile_index,
        "tile_index_hex": f"0x{tile_index:03X}",
        "tile_changed": before_tile != replacement_tile,
        "decompressed_size": len(payload),
        "compressed_size": len(compressed),
        "available_size": original_consumed,
        "current_consumed_size": current_consumed,
        "tail_fill": tail_fill,
        "reserved_tile_restored": reserved_common_hud_tile,
        "replacement_ignored": reserved_common_hud_tile,
        "zero_to_shadow_remap": zero_to_shadow_remap,
        "range_zero_to_shadow_pixels": range_zero_to_shadow_pixels,
    }
    return attach_lz77_distance_one_check(
        result,
        item_id=item["item_id"],
        original_offset=offset,
        compressed=compressed,
        encoder=encoder_name,
    )


def apply_raw4bpp_item(rom: bytearray, item: dict) -> dict:
    replacement = item.get("replacement_path", "")
    if not replacement:
        return {"item_id": item["item_id"], "status": "skipped", "reason": "no replacement_path"}
    replacement_path = (ROOT / replacement).resolve()
    if not replacement_path.is_file() or ROOT not in replacement_path.parents:
        return {"item_id": item["item_id"], "status": "error", "reason": "replacement file not found"}

    offset = rle_offset_from_item(item)
    if offset is None:
        return {"item_id": item["item_id"], "status": "skipped", "reason": "no raw image offset"}
    raw_byte_length = int(item.get("raw_byte_length") or item.get("decompressed_size") or 0)
    if raw_byte_length <= 0:
        return {"item_id": item["item_id"], "status": "error", "reason": "missing raw_byte_length"}
    if raw_byte_length % TILE_BYTES:
        return {"item_id": item["item_id"], "status": "error", "reason": "raw payload is not 4bpp tile aligned"}
    if offset < 0 or offset + raw_byte_length > len(rom):
        return {"item_id": item["item_id"], "status": "error", "reason": "raw image range is outside ROM"}

    tile_count = raw_byte_length // TILE_BYTES
    columns = columns_from_item(item, tile_count)
    rows = (tile_count + columns - 1) // columns
    width = columns * 8
    height = rows * 8
    indices = image_to_indices(replacement_path, width, height)
    payload = indices_to_4bpp_tiles(indices, width, height, columns, tile_count)
    if len(payload) != raw_byte_length:
        return {"item_id": item["item_id"], "status": "error", "reason": "converted raw payload size mismatch"}

    rom[offset : offset + raw_byte_length] = payload
    if bytes(rom[offset : offset + raw_byte_length]) != payload:
        return {"item_id": item["item_id"], "status": "error", "reason": "raw verification failed"}
    return {
        "item_id": item["item_id"],
        "status": "applied",
        "compression": "raw4bpp",
        "storage": "same_offset",
        "offset": offset,
        "offset_hex": f"0x{offset:08X}",
        "columns": columns,
        "raw_byte_length": raw_byte_length,
        "decompressed_size": len(payload),
        "available_size": raw_byte_length,
    }


def apply_rle_tile_item(rom: bytearray, item: dict) -> dict:
    replacement = item.get("replacement_path", "")
    if not replacement:
        return {"item_id": item["item_id"], "status": "skipped", "reason": "no replacement_path"}
    replacement_path = (ROOT / replacement).resolve()
    if not replacement_path.is_file() or ROOT not in replacement_path.parents:
        return {"item_id": item["item_id"], "status": "error", "reason": "replacement file not found"}

    offset = rle_offset_from_item(item)
    if offset is None:
        return {"item_id": item["item_id"], "status": "skipped", "reason": "no RLE block offset"}
    tile_index = lz77_tile_index_from_item(item)
    if tile_index is None:
        return {"item_id": item["item_id"], "status": "error", "reason": "missing tile_index"}

    current = decompress_gba_rle(bytes(rom), offset, max_output_size=0x400000)
    if not current:
        return {"item_id": item["item_id"], "status": "error", "reason": "target is not a GBA RLE block"}
    original_payload, current_consumed = current
    if len(original_payload) % TILE_BYTES:
        return {"item_id": item["item_id"], "status": "error", "reason": "RLE payload is not 4bpp tile aligned"}
    tile_count = len(original_payload) // TILE_BYTES
    if not (0 <= tile_index < tile_count):
        return {
            "item_id": item["item_id"],
            "status": "error",
            "reason": f"tile_index 0x{tile_index:03X} outside block tile count {tile_count}",
        }

    indices = image_to_indices(replacement_path, 8, 8)
    replacement_tile = indices_to_4bpp_tiles(indices, 8, 8, 1, 1)
    payload = bytearray(original_payload)
    start = tile_index * TILE_BYTES
    before_tile = bytes(payload[start : start + TILE_BYTES])
    payload[start : start + TILE_BYTES] = replacement_tile

    original_consumed = reference_consumed_size(
        offset=offset,
        current_payload_size=len(original_payload),
        current_consumed=current_consumed,
        decompressor=decompress_gba_rle,
    )
    compressed = compress_gba_rle(bytes(payload))
    if len(compressed) > original_consumed:
        result = append_repoint_blob(
            rom,
            item,
            original_offset=offset,
            original_consumed=original_consumed,
            compressed=compressed,
            payload=bytes(payload),
            compression="rle",
            compression_tag=0x30,
            decompressor=decompress_gba_rle,
        )
        result["tile_index"] = tile_index
        result["tile_index_hex"] = f"0x{tile_index:03X}"
        result["tile_changed"] = before_tile != replacement_tile
        return result

    rom[offset : offset + len(compressed)] = compressed
    if len(compressed) < original_consumed:
        rom[offset + len(compressed) : offset + original_consumed] = b"\x00" * (original_consumed - len(compressed))
    verify = decompress_gba_rle(bytes(rom), offset, max_output_size=0x400000)
    if not verify or verify[0] != bytes(payload):
        return {"item_id": item["item_id"], "status": "error", "reason": "verification failed"}
    restored_pointer_patches = restore_same_offset_pointer_patches(
        rom,
        item,
        original_offset=offset,
        original_consumed=original_consumed,
        compression_tag=0x30,
        decompressor=decompress_gba_rle,
    )
    return {
        "item_id": item["item_id"],
        "status": "applied",
        "compression": "rle_tile",
        "storage": "same_offset",
        "offset": offset,
        "offset_hex": f"0x{offset:08X}",
        "tile_index": tile_index,
        "tile_index_hex": f"0x{tile_index:03X}",
        "tile_changed": before_tile != replacement_tile,
        "decompressed_size": len(payload),
        "compressed_size": len(compressed),
        "available_size": original_consumed,
        "current_consumed_size": current_consumed,
        **({"restored_same_offset_pointers": restored_pointer_patches} if restored_pointer_patches else {}),
    }


def registry_b_table_offset_from_item(item: dict) -> int | None:
    for field in ("registry_b_table_offset", "registry_b_table_offset_hex"):
        value = parse_int_value(item.get(field))
        if value is not None:
            return value
    entry = parse_int_value(item.get("registry_b_entry"))
    if entry is None:
        raw = str(item.get("registry_b_entry_hex") or "")
        if raw:
            entry = parse_int_value(raw)
    if entry is None:
        return None
    return 0x00183D50 + entry * 8


def current_registry_b_resource_offset(rom: bytes | bytearray, table_offset: int, fallback_offset: int) -> tuple[int, int | None, int | None]:
    if not (0 <= table_offset <= len(rom) - 8):
        return fallback_offset, None, None
    pointer = int.from_bytes(rom[table_offset : table_offset + 4], "little")
    length = int.from_bytes(rom[table_offset + 4 : table_offset + 8], "little")
    offset = gba_pointer_to_file_offset(pointer, len(rom))
    if offset is None:
        return fallback_offset, pointer, length
    return offset, pointer, length


def read_registry_b_resource_payload(
    rom: bytes | bytearray,
    offset: int,
    table_length: int | None,
) -> dict:
    if not (0 <= offset < len(rom)):
        raise ValueError("Registry B resource offset is outside ROM")
    magic = bytes(rom[offset : offset + 4])
    if magic in {b"ZP00", b"ZP01"}:
        decoded = decompress_zp_resource(bytes(rom), offset, max_output_size=0x400000)
        return {
            "variant": decoded.variant,
            "payload": decoded.payload,
            "consumed_size": decoded.consumed,
            "available_size": table_length or decoded.consumed,
            "compression": f"registry_b_{decoded.variant.lower()}",
        }
    if table_length is None or table_length <= 0:
        raise ValueError("raw Registry B resource has no table length")
    if offset + table_length > len(rom):
        raise ValueError("raw Registry B resource exceeds ROM size")
    return {
        "variant": "raw",
        "payload": bytes(rom[offset : offset + table_length]),
        "consumed_size": table_length,
        "available_size": table_length,
        "compression": "registry_b_raw4bpp",
    }


def apply_registry_b_zp_item(rom: bytearray, item: dict) -> dict:
    replacement = item.get("replacement_path", "")
    if not replacement:
        return {"item_id": item["item_id"], "status": "skipped", "reason": "no replacement_path"}
    replacement_path = (ROOT / replacement).resolve()
    if not replacement_path.is_file() or ROOT not in replacement_path.parents:
        return {"item_id": item["item_id"], "status": "error", "reason": "replacement file not found"}

    original_offset = rle_offset_from_item(item)
    if original_offset is None:
        return {"item_id": item["item_id"], "status": "skipped", "reason": "no Registry B ZP offset"}
    table_offset = registry_b_table_offset_from_item(item)
    if table_offset is None:
        return {"item_id": item["item_id"], "status": "error", "reason": "missing registry_b_table_offset"}

    current_offset, old_pointer, table_length = current_registry_b_resource_offset(rom, table_offset, original_offset)
    try:
        current = read_registry_b_resource_payload(rom, current_offset, table_length)
    except (ZPCodecError, ValueError) as exc:
        return {
            "item_id": item["item_id"],
            "status": "error",
            "reason": f"target is not a supported Registry B tile resource: {exc}",
            "offset_hex": f"0x{current_offset:08X}",
        }
    if current["variant"] not in {"ZP00", "ZP01", "raw"}:
        return {"item_id": item["item_id"], "status": "error", "reason": f"unsupported Registry B variant: {current['variant']}"}
    if len(current["payload"]) % TILE_BYTES:
        return {"item_id": item["item_id"], "status": "error", "reason": "Registry B payload is not 4bpp tile aligned"}

    resource_tile_count = len(current["payload"]) // TILE_BYTES
    selected_tile_indices = tile_indices_from_item(item, resource_tile_count)
    edit_tile_count = len(selected_tile_indices) if selected_tile_indices else resource_tile_count
    columns = columns_from_item(item, edit_tile_count)
    rows = (edit_tile_count + columns - 1) // columns
    width = columns * 8
    height = rows * 8
    indices = image_to_indices(replacement_path, width, height)
    replacement_tiles = indices_to_4bpp_tiles(indices, width, height, columns, edit_tile_count)
    if selected_tile_indices:
        payload_bytes = bytearray(current["payload"])
        for edit_index, target_index in enumerate(selected_tile_indices):
            src = edit_index * TILE_BYTES
            dst = target_index * TILE_BYTES
            payload_bytes[dst : dst + TILE_BYTES] = replacement_tiles[src : src + TILE_BYTES]
        payload = bytes(payload_bytes)
    else:
        payload = replacement_tiles
    if len(payload) != len(current["payload"]):
        return {"item_id": item["item_id"], "status": "error", "reason": "converted Registry B payload size mismatch"}

    if current["variant"] == "raw":
        compressed = payload
    else:
        compressed = compress_zp_resource(payload, current["variant"])
    available_size = int(current["available_size"] or current["consumed_size"])
    if available_size <= 0:
        available_size = int(current["consumed_size"])

    storage = "same_offset"
    new_offset = current_offset
    old_table_pointer_bytes = bytes(rom[table_offset : table_offset + 4])
    old_table_length_bytes = bytes(rom[table_offset + 4 : table_offset + 8])
    original_rom_len = len(rom)

    if len(compressed) <= available_size:
        rom[current_offset : current_offset + len(compressed)] = compressed
        if len(compressed) < available_size:
            rom[current_offset + len(compressed) : current_offset + available_size] = b"\x00" * (
                available_size - len(compressed)
            )
        rom[table_offset + 4 : table_offset + 8] = len(compressed).to_bytes(4, "little")
    else:
        storage = "repoint"
        if len(rom) % REPOINT_ALIGNMENT:
            rom.extend(b"\xFF" * (REPOINT_ALIGNMENT - (len(rom) % REPOINT_ALIGNMENT)))
        new_offset = len(rom)
        if new_offset + len(compressed) > GBA_MAX_ROM_SIZE:
            del rom[original_rom_len:]
            return {
                "item_id": item["item_id"],
                "status": "error",
                "reason": f"Registry B replacement too large for ROM max size: {len(compressed)} bytes",
                "compression": current["compression"],
                "offset_hex": f"0x{current_offset:08X}",
                "compressed_size": len(compressed),
                "available_size": available_size,
                "repoint_attempted": True,
            }
        rom.extend(compressed)
        rom[table_offset : table_offset + 4] = gba_pointer_for_offset(new_offset)
        rom[table_offset + 4 : table_offset + 8] = len(compressed).to_bytes(4, "little")

    try:
        verify = read_registry_b_resource_payload(rom, new_offset, len(compressed))
        verified = verify["payload"] == payload and verify["variant"] == current["variant"]
    except Exception:
        verify = None
        verified = False
    if not verified:
        rom[table_offset : table_offset + 4] = old_table_pointer_bytes
        rom[table_offset + 4 : table_offset + 8] = old_table_length_bytes
        if storage == "repoint":
            del rom[original_rom_len:]
        return {
            "item_id": item["item_id"],
            "status": "error",
            "reason": "Registry B verification failed",
            "compression": current["compression"],
            "offset_hex": f"0x{current_offset:08X}",
            "new_offset_hex": f"0x{new_offset:08X}",
            "compressed_size": len(compressed),
            "available_size": available_size,
        }

    return {
        "item_id": item["item_id"],
        "status": "applied",
        "compression": current["compression"],
        "storage": storage,
        "variant": current["variant"],
        "offset": current_offset,
        "offset_hex": f"0x{current_offset:08X}",
        "original_offset": original_offset,
        "original_offset_hex": f"0x{original_offset:08X}",
        "new_offset": new_offset,
        "new_offset_hex": f"0x{new_offset:08X}",
        "registry_b_table_offset": table_offset,
        "registry_b_table_offset_hex": f"0x{table_offset:08X}",
        "old_pointer_value": f"0x{old_pointer:08X}" if old_pointer is not None else "",
        "new_pointer_value": f"0x{GBA_ROM_BASE + new_offset:08X}",
        "columns": columns,
        "tile_count": resource_tile_count,
        "edit_tile_count": edit_tile_count,
        "edited_tile_indices": selected_tile_indices,
        "decompressed_size": len(payload),
        "compressed_size": len(compressed),
        "available_size": available_size,
        "current_consumed_size": current["consumed_size"],
        "rom_size_after": len(rom),
        "repoint_attempted": storage == "repoint",
    }


def is_rle_tile_item(item: dict) -> bool:
    return item.get("compression") == "rle_tile" or item.get("source") in {
        "rle_tile",
        "rle_tile_4bpp",
    }


def is_raw4bpp_item(item: dict) -> bool:
    source = str(item.get("source", ""))
    expected = str(item.get("expected_text_kind", ""))
    return (
        source in {"raw4bpp", "raw_4bpp", "raw_tile_4bpp"}
        or expected == "battle_command_raw4bpp_wordmark"
        or item.get("compression") == "raw4bpp"
    )


def is_lz77_tile_item(item: dict) -> bool:
    return item.get("compression") == "lz77_tile" or item.get("source") in {
        "lz77_tile",
        "lz77_tile_4bpp",
    }


def is_registry_b_zp_item(item: dict) -> bool:
    return item.get("compression") in {"registry_b_zp00", "registry_b_zp01", "registry_b_raw4bpp"} or item.get("source") in {
        "registry_b_raw4bpp",
        "registry_b_zp01",
        "registry_b_zp01_4bpp",
    }


def apply_image_item(rom: bytearray, item: dict, protected_items: list[dict] | None = None) -> dict:
    offset = rle_offset_from_item(item)
    if offset is None:
        return {"item_id": item["item_id"], "status": "skipped", "reason": "no image offset"}
    if is_lz77_tile_item(item):
        return apply_lz77_tile_item(rom, item)
    if is_rle_tile_item(item):
        return apply_rle_tile_item(rom, item)
    if is_raw4bpp_item(item):
        return apply_raw4bpp_item(rom, item)
    if is_registry_b_zp_item(item):
        return apply_registry_b_zp_item(rom, item)
    if offset < len(rom) and rom[offset] == 0x10:
        return apply_lz77_item(rom, item)
    if offset < len(rom) and rom[offset] == 0x30:
        return apply_rle_item(rom, item, protected_items=protected_items)
    rle_result = apply_rle_item(rom, item, protected_items=protected_items)
    if rle_result.get("status") == "applied":
        return rle_result
    lz77_result = apply_lz77_item(rom, item)
    if lz77_result.get("status") == "applied":
        return lz77_result
    return {
        "item_id": item["item_id"],
        "status": "error",
        "reason": f"target is neither supported RLE nor LZ77 ({rle_result.get('reason')}; {lz77_result.get('reason')})",
    }


def main() -> int:
    args = parse_args()
    rom_path = args.rom.resolve()
    if not rom_path.exists() and args.rom == DEFAULT_ROM and FALLBACK_ROM.exists():
        rom_path = FALLBACK_ROM.resolve()
    items = json.loads(args.image_replacements.resolve().read_text(encoding="utf-8"))
    filters = set(args.item_id)
    rom = bytearray(rom_path.read_bytes())
    candidates = []
    for item in items:
        if filters and item["item_id"] not in filters:
            continue
        if item.get("replacement_target") is False:
            continue
        offset = rle_offset_from_item(item)
        if offset is None or not item.get("replacement_path"):
            continue
        candidates.append(item)

    lz77_tile_groups: dict[int, list[dict]] = {}
    for item in candidates:
        if not is_lz77_tile_item(item):
            continue
        offset = rle_offset_from_item(item)
        if offset is None:
            continue
        lz77_tile_groups.setdefault(offset, []).append(item)

    results = []
    handled_item_ids: set[str] = set()
    for item in candidates:
        if item["item_id"] in handled_item_ids:
            continue
        try:
            offset = rle_offset_from_item(item)
            lz77_tile_group = lz77_tile_groups.get(offset or -1, [])
            if is_lz77_tile_item(item) and len(lz77_tile_group) > 1:
                results.extend(apply_lz77_tile_items(rom, lz77_tile_group))
                handled_item_ids.update(group_item["item_id"] for group_item in lz77_tile_group)
            else:
                results.append(apply_image_item(rom, item, protected_items=items))
                handled_item_ids.add(item["item_id"])
        except Exception as exc:
            results.append(
                {
                    "item_id": item["item_id"],
                    "status": "error",
                    "reason": str(exc),
                }
            )

    applied = [item for item in results if item["status"] == "applied"]
    if applied:
        rom_path.write_bytes(rom)

    report = {
        "rom": str(rom_path.relative_to(ROOT) if rom_path.is_relative_to(ROOT) else rom_path),
        "applied_count": len(applied),
        "stability_checks": summarize_lz77_stability_checks(results),
        "results": results,
    }
    args.report.resolve().parent.mkdir(parents=True, exist_ok=True)
    args.report.resolve().write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    if applied and rom_path == DEFAULT_ROM.resolve() and args.image_replacements.resolve() == DEFAULT_IMAGE_REPLACEMENTS.resolve():
        applied_by_id = {result["item_id"]: result for result in applied}
        for item in items:
            item_id = item.get("item_id")
            if item_id in applied_by_id:
                item["progress_status"] = "edited"
                item["last_apply_summary"] = {
                    "rom": report["rom"],
                    "applied_count": 1,
                    "results": [applied_by_id[item_id]],
                }
        args.image_replacements.resolve().write_text(
            json.dumps(items, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )
    print(json.dumps(report, ensure_ascii=False, indent=2))
    if any(item["status"] == "error" for item in results):
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
