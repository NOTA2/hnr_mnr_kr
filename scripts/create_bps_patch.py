#!/usr/bin/env python3
"""Create and verify simple BPS patches.

This writer intentionally emits only SourceRead and TargetRead actions. The
resulting patch is easy to audit and is compatible with standard BPS patchers.
"""

from __future__ import annotations

import argparse
import binascii
import hashlib
import struct
from pathlib import Path


MODE_SOURCE_READ = 0
MODE_TARGET_READ = 1
MODE_SOURCE_COPY = 2
MODE_TARGET_COPY = 3


def crc32(data: bytes | bytearray) -> int:
    return binascii.crc32(data) & 0xFFFFFFFF


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def encode_number(value: int) -> bytes:
    if value < 0:
        raise ValueError("BPS numbers must be non-negative")

    out = bytearray()
    while True:
        byte = value & 0x7F
        value >>= 7
        if value == 0:
            out.append(byte | 0x80)
            return bytes(out)
        out.append(byte)
        value -= 1


def decode_number(data: bytes | bytearray, offset: int) -> tuple[int, int]:
    value = 0
    shift = 1

    while True:
        if offset >= len(data):
            raise ValueError("Unexpected end of BPS data while reading number")
        byte = data[offset]
        offset += 1
        value += (byte & 0x7F) * shift
        if byte & 0x80:
            return value, offset
        shift <<= 7
        value += shift


def add_action(out: bytearray, mode: int, length: int) -> None:
    if length <= 0:
        return
    out.extend(encode_number(((length - 1) << 2) | mode))


def same_offset_match_length(source: bytes, target: bytes, offset: int) -> int:
    limit = min(len(source), len(target))
    pos = offset
    while pos < limit and source[pos] == target[pos]:
        pos += 1
    return pos - offset


def create_patch(source: bytes, target: bytes, metadata: bytes = b"") -> bytes:
    out = bytearray(b"BPS1")
    out.extend(encode_number(len(source)))
    out.extend(encode_number(len(target)))
    out.extend(encode_number(len(metadata)))
    out.extend(metadata)

    pos = 0
    min_source_read = 4

    while pos < len(target):
        match_len = same_offset_match_length(source, target, pos)
        if match_len >= min_source_read:
            add_action(out, MODE_SOURCE_READ, match_len)
            pos += match_len
            continue

        start = pos
        while pos < len(target):
            match_len = same_offset_match_length(source, target, pos)
            if match_len >= min_source_read:
                break
            pos += max(1, match_len)

        add_action(out, MODE_TARGET_READ, pos - start)
        out.extend(target[start:pos])

    out.extend(struct.pack("<I", crc32(source)))
    out.extend(struct.pack("<I", crc32(target)))
    out.extend(struct.pack("<I", crc32(out)))
    return bytes(out)


def signed_offset_delta(value: int) -> int:
    sign = -1 if value & 1 else 1
    return sign * (value >> 1)


def apply_patch(source: bytes, patch: bytes, verify: bool = True) -> bytes:
    if len(patch) < 16 or patch[:4] != b"BPS1":
        raise ValueError("Not a BPS1 patch")

    stored_source_crc = struct.unpack("<I", patch[-12:-8])[0]
    stored_target_crc = struct.unpack("<I", patch[-8:-4])[0]
    stored_patch_crc = struct.unpack("<I", patch[-4:])[0]

    if verify and crc32(patch[:-4]) != stored_patch_crc:
        raise ValueError("Patch CRC32 mismatch")
    if verify and crc32(source) != stored_source_crc:
        raise ValueError("Source CRC32 mismatch")

    end = len(patch) - 12
    offset = 4
    source_size, offset = decode_number(patch, offset)
    target_size, offset = decode_number(patch, offset)
    metadata_size, offset = decode_number(patch, offset)
    offset += metadata_size

    if len(source) != source_size:
        raise ValueError(f"Source size mismatch: expected {source_size}, got {len(source)}")
    if offset > end:
        raise ValueError("Invalid BPS metadata length")

    target = bytearray()
    source_relative_offset = 0
    target_relative_offset = 0

    while len(target) < target_size:
        action, offset = decode_number(patch, offset)
        mode = action & 3
        length = (action >> 2) + 1

        if mode == MODE_SOURCE_READ:
            source_offset = len(target)
            target.extend(source[source_offset : source_offset + length])
        elif mode == MODE_TARGET_READ:
            target.extend(patch[offset : offset + length])
            offset += length
        elif mode == MODE_SOURCE_COPY:
            encoded, offset = decode_number(patch, offset)
            source_relative_offset += signed_offset_delta(encoded)
            for _ in range(length):
                target.append(source[source_relative_offset])
                source_relative_offset += 1
        elif mode == MODE_TARGET_COPY:
            encoded, offset = decode_number(patch, offset)
            target_relative_offset += signed_offset_delta(encoded)
            for _ in range(length):
                target.append(target[target_relative_offset])
                target_relative_offset += 1
        else:
            raise AssertionError("unreachable BPS mode")

    if offset != end:
        raise ValueError(f"Unused BPS action data: {end - offset} bytes")

    result = bytes(target)
    if verify and crc32(result) != stored_target_crc:
        raise ValueError("Target CRC32 mismatch")
    return result


def build_metadata(source_path: Path, target_path: Path, source: bytes, target: bytes) -> bytes:
    lines = [
        "Hagane no Renkinjutsushi - Meisou no Rondo Korean patch",
        "Release: hnr_mnr_ko_v0.1.0",
        f"Source file: {source_path.name}",
        f"Source SHA256: {sha256(source)}",
        f"Target file: {target_path.name}",
        f"Target SHA256: {sha256(target)}",
    ]
    return ("\n".join(lines) + "\n").encode("utf-8")


def command_create(args: argparse.Namespace) -> None:
    source_path = Path(args.source)
    target_path = Path(args.target)
    output_path = Path(args.output)

    source = source_path.read_bytes()
    target = target_path.read_bytes()
    metadata = build_metadata(source_path, target_path, source, target)
    patch = create_patch(source, target, metadata)

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_bytes(patch)

    verified = apply_patch(source, patch)
    if verified != target:
        raise RuntimeError("Internal verification failed: applied patch differs from target")

    print(f"Wrote: {output_path}")
    print(f"Patch bytes: {len(patch)}")
    print(f"Source SHA256: {sha256(source)}")
    print(f"Target SHA256: {sha256(target)}")
    print(f"Patch SHA256: {sha256(patch)}")


def command_verify(args: argparse.Namespace) -> None:
    source = Path(args.source).read_bytes()
    target = Path(args.target).read_bytes()
    patch = Path(args.patch).read_bytes()

    verified = apply_patch(source, patch)
    if verified != target:
        raise RuntimeError("Verification failed: applied patch differs from target")

    print("BPS verification passed")
    print(f"Target SHA256: {sha256(verified)}")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest="command", required=True)

    create = subparsers.add_parser("create", help="create a BPS patch")
    create.add_argument("source", help="clean source ROM")
    create.add_argument("target", help="patched target ROM")
    create.add_argument("output", help="output .bps path")
    create.set_defaults(func=command_create)

    verify = subparsers.add_parser("verify", help="verify a BPS patch")
    verify.add_argument("source", help="clean source ROM")
    verify.add_argument("target", help="expected patched target ROM")
    verify.add_argument("patch", help="input .bps path")
    verify.set_defaults(func=command_verify)

    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
