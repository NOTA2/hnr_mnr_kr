#!/usr/bin/env python3
"""Registry B ZP00/ZP01 resource codec helpers.

The game loads these resources through the helper at 0x068DF8.  ZP payloads are
not BIOS LZ77/RLE; they are sparse delta streams.  ZP01 is a two-level form:
first it reconstructs the per-8-byte bitmask, then it reconstructs the final
payload bytes selected by that bitmask, and both layers use prefix sums.
"""

from __future__ import annotations

from dataclasses import dataclass


GBA_ROM_BASE = 0x08000000


class ZPCodecError(ValueError):
    pass


@dataclass(frozen=True)
class ZPDecoded:
    payload: bytes
    consumed: int
    variant: str
    output_size: int


def ceil_div(value: int, divisor: int) -> int:
    return (value + divisor - 1) // divisor


def gba_pointer_to_file_offset(pointer: int, rom_size: int | None = None) -> int | None:
    offset = pointer - GBA_ROM_BASE
    if offset < 0:
        return None
    if rom_size is not None and offset >= rom_size:
        return None
    return offset


def iter_bits_msb_first(mask: bytes, bit_count: int):
    for index in range(bit_count):
        yield (mask[index // 8] >> (7 - (index & 7))) & 1


def sparse_expand(mask: bytes, values: bytes, output_size: int) -> tuple[bytes, int]:
    out = bytearray(output_size)
    cursor = 0
    for index, bit in enumerate(iter_bits_msb_first(mask, ceil_div(output_size, 8) * 8)):
        if index >= output_size:
            break
        if bit:
            if cursor >= len(values):
                raise ZPCodecError("ZP sparse stream ended early")
            out[index] = values[cursor]
            cursor += 1
    return bytes(out), cursor


def prefix_sum(delta: bytes) -> bytes:
    out = bytearray(len(delta))
    previous = 0
    for index, value in enumerate(delta):
        previous = (previous + value) & 0xFF
        out[index] = previous
    return bytes(out)


def prefix_delta(payload: bytes) -> bytes:
    out = bytearray(len(payload))
    previous = 0
    for index, value in enumerate(payload):
        out[index] = (value - previous) & 0xFF
        previous = value
    return bytes(out)


def sparse_pack(delta: bytes) -> tuple[bytes, bytes]:
    mask = bytearray(ceil_div(len(delta), 8))
    values = bytearray()
    for index, value in enumerate(delta):
        if value:
            mask[index // 8] |= 0x80 >> (index & 7)
            values.append(value)
    return bytes(mask), bytes(values)


def decompress_zp00_payload(payload: bytes, output_size: int) -> tuple[bytes, int]:
    mask_size = ceil_div(output_size, 8)
    if len(payload) < mask_size:
        raise ZPCodecError("ZP00 payload is shorter than its bitmask")
    mask = payload[:mask_size]
    delta_values = payload[mask_size:]
    sparse_delta, used = sparse_expand(mask, delta_values, output_size)
    return prefix_sum(sparse_delta), mask_size + used


def decompress_zp01_payload(payload: bytes, output_size: int) -> tuple[bytes, int]:
    mask1_size = ceil_div(output_size, 8)
    mask2_size = ceil_div(mask1_size, 8)
    if len(payload) < 4 + mask2_size:
        raise ZPCodecError("ZP01 payload is shorter than its header/bitmask")

    level1_value_count = int.from_bytes(payload[:4], "little")
    mask2_start = 4
    mask2_end = mask2_start + mask2_size
    level1_start = mask2_end
    level1_end = level1_start + level1_value_count
    if level1_end > len(payload):
        raise ZPCodecError("ZP01 level-1 values exceed payload length")

    level1_delta, used_level1 = sparse_expand(
        payload[mask2_start:mask2_end],
        payload[level1_start:level1_end],
        mask1_size,
    )
    if used_level1 != level1_value_count:
        raise ZPCodecError("ZP01 level-1 value count does not match bitmask")
    mask1 = prefix_sum(level1_delta)

    level2_start = level1_end
    final_delta, used_level2 = sparse_expand(mask1, payload[level2_start:], output_size)
    return prefix_sum(final_delta), level2_start + used_level2


def decompress_zp_resource(data: bytes, offset: int, *, max_output_size: int = 0x400000) -> ZPDecoded:
    if offset < 0 or offset + 8 > len(data):
        raise ZPCodecError("ZP resource offset is outside data")
    magic = data[offset : offset + 4]
    if magic not in {b"ZP00", b"ZP01"}:
        raise ZPCodecError("not a ZP00/ZP01 resource")
    output_size = int.from_bytes(data[offset + 4 : offset + 8], "little")
    if output_size <= 0 or output_size > max_output_size:
        raise ZPCodecError(f"invalid ZP output size: {output_size}")
    payload = data[offset + 8 :]
    if magic == b"ZP00":
        decoded, used = decompress_zp00_payload(payload, output_size)
    else:
        decoded, used = decompress_zp01_payload(payload, output_size)
    return ZPDecoded(
        payload=decoded,
        consumed=8 + used,
        variant=magic.decode("ascii"),
        output_size=output_size,
    )


def compress_zp00_resource(payload: bytes) -> bytes:
    delta = prefix_delta(payload)
    mask, values = sparse_pack(delta)
    return b"ZP00" + len(payload).to_bytes(4, "little") + mask + values


def compress_zp01_resource(payload: bytes) -> bytes:
    final_delta = prefix_delta(payload)
    mask1, level2_values = sparse_pack(final_delta)
    level1_delta = prefix_delta(mask1)
    mask2, level1_values = sparse_pack(level1_delta)
    return (
        b"ZP01"
        + len(payload).to_bytes(4, "little")
        + len(level1_values).to_bytes(4, "little")
        + mask2
        + level1_values
        + level2_values
    )


def compress_zp_resource(payload: bytes, variant: str = "ZP01") -> bytes:
    if variant == "ZP00":
        return compress_zp00_resource(payload)
    if variant == "ZP01":
        return compress_zp01_resource(payload)
    raise ZPCodecError(f"unsupported ZP variant: {variant}")

