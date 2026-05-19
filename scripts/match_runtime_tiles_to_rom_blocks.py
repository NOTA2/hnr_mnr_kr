#!/usr/bin/env python3
"""Match runtime VRAM tiles against extracted ROM LZ77 graphics blocks."""

from __future__ import annotations

import argparse
import binascii
import collections
import json
import math
import struct
import zlib
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_PROBE_DIR = ROOT / "confirmed_data/image_inventory/pymgba_runtime_timeline"
DEFAULT_REPORT = ROOT / "confirmed_data/image_inventory/global_tile_extraction/notes/global_tile_extraction_report.json"
DEFAULT_RLE_REPORT = ROOT / "confirmed_data/image_inventory/rle_tile_extraction/notes/rle_tile_extraction_report.json"
DEFAULT_OUT_DIR = ROOT / "confirmed_data/image_inventory/runtime_tile_matches"
TILE_SIZE = 32
CHARBLOCK_SIZE = 0x4000


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--probe-dir", type=Path, default=DEFAULT_PROBE_DIR)
    parser.add_argument("--global-report", type=Path, default=DEFAULT_REPORT)
    parser.add_argument("--rle-report", type=Path, default=DEFAULT_RLE_REPORT)
    parser.add_argument("--out-dir", type=Path, default=DEFAULT_OUT_DIR)
    parser.add_argument("--top", type=int, default=12)
    parser.add_argument("--min-shared-tiles", type=int, default=8)
    parser.add_argument("--gallery-limit", type=int, default=60)
    return parser.parse_args()


def tile_hash(tile: bytes) -> int:
    return binascii.crc32(tile) & 0xFFFFFFFF


def is_blank_tile(tile: bytes) -> bool:
    return not tile or all(byte == tile[0] for byte in tile)


def tile_hashes(data: bytes) -> list[int | None]:
    usable = len(data) - (len(data) % TILE_SIZE)
    hashes: list[int | None] = []
    for offset in range(0, usable, TILE_SIZE):
        tile = data[offset : offset + TILE_SIZE]
        hashes.append(None if is_blank_tile(tile) else tile_hash(tile))
    return hashes


def nonblank_counter(hashes: list[int | None]) -> collections.Counter[int]:
    return collections.Counter(value for value in hashes if value is not None)


def shared_count(left: collections.Counter[int], right: collections.Counter[int]) -> int:
    return sum(min(count, right.get(key, 0)) for key, count in left.items())


def longest_common_run(left: list[int | None], right: list[int | None], *, max_positions_per_hash: int = 128) -> int:
    positions: dict[int, list[int]] = collections.defaultdict(list)
    for index, value in enumerate(right):
        if value is not None and len(positions[value]) < max_positions_per_hash:
            positions[value].append(index)

    best = 0
    active: dict[int, int] = {}
    for left_index, value in enumerate(left):
        next_active: dict[int, int] = {}
        if value is not None:
            for right_index in positions.get(value, []):
                run = active.get(right_index - 1, 0) + 1
                if run > next_active.get(right_index, 0):
                    next_active[right_index] = run
                    best = max(best, run)
        active = next_active
    return best


def build_candidate(item: dict, *, source: str) -> dict | None:
    raw_path = ROOT / item["raw_path"]
    if not raw_path.exists():
        return None
    data = raw_path.read_bytes()
    hashes = tile_hashes(data)
    counter = nonblank_counter(hashes)
    if not counter:
        return None
    offset = int(item["offset"])
    return {
        "source": source,
        "index": item["index"],
        "offset": offset,
        "rom_address": int(item.get("rom_address", 0x08000000 + offset)),
        "decompressed_size": int(item.get("decompressed_size", item.get("raw_size", len(data)))),
        "compressed_size": int(item.get("compressed_size", 0)),
        "tile_count": len(hashes),
        "nonblank_tile_count": sum(counter.values()),
        "raw_path": item["raw_path"],
        "preview_path": item["preview_path"],
        "_hashes": hashes,
        "_counter": counter,
    }


def load_candidates(report_path: Path) -> list[dict]:
    report = json.loads(report_path.read_text(encoding="utf-8"))
    candidates = []
    for source in ("lz77", "raw"):
        for item in report.get(source, []):
            candidate = build_candidate(item, source=source)
            if candidate:
                candidates.append(candidate)
    return candidates


def load_rle_candidates(report_path: Path) -> list[dict]:
    if not report_path.exists():
        return []
    report = json.loads(report_path.read_text(encoding="utf-8"))
    candidates = []
    for item in report.get("blocks", []):
        candidate = build_candidate(item, source="rle")
        if candidate:
            candidates.append(candidate)
    return candidates


def frame_prefix_from_vram(path: Path) -> str:
    return path.name.removesuffix("_vram_06000000.bin")


def iter_runtime_charblocks(probe_dir: Path) -> list[dict]:
    charblocks: list[dict] = []
    for vram_path in sorted(probe_dir.glob("frame_*_vram_06000000.bin")):
        frame = frame_prefix_from_vram(vram_path)
        data = vram_path.read_bytes()
        for charblock in range(len(data) // CHARBLOCK_SIZE):
            start = charblock * CHARBLOCK_SIZE
            payload = data[start : start + CHARBLOCK_SIZE]
            hashes = tile_hashes(payload)
            counter = nonblank_counter(hashes)
            if not counter:
                continue
            charblocks.append(
                {
                    "frame": frame,
                    "charblock": charblock,
                    "vram_offset": start,
                    "tile_count": len(hashes),
                    "nonblank_tile_count": sum(counter.values()),
                    "_hashes": hashes,
                    "_counter": counter,
                }
            )
    return charblocks


def score_candidate(runtime: dict, candidate: dict) -> dict | None:
    shared = shared_count(runtime["_counter"], candidate["_counter"])
    if shared <= 0:
        return None
    runtime_nonblank = runtime["nonblank_tile_count"]
    candidate_nonblank = candidate["nonblank_tile_count"]
    runtime_coverage = shared / runtime_nonblank if runtime_nonblank else 0.0
    candidate_coverage = shared / candidate_nonblank if candidate_nonblank else 0.0
    run = longest_common_run(runtime["_hashes"], candidate["_hashes"])
    score = shared * 2.0 + run * 6.0 + runtime_coverage * 40.0 + candidate_coverage * 25.0
    return {
        "score": round(score, 4),
        "shared_tiles": shared,
        "longest_contiguous_tile_run": run,
        "runtime_coverage": round(runtime_coverage, 4),
        "candidate_coverage": round(candidate_coverage, 4),
        "source": candidate["source"],
        "candidate_index": candidate["index"],
        "offset": candidate["offset"],
        "rom_address": candidate["rom_address"],
        "decompressed_size": candidate["decompressed_size"],
        "compressed_size": candidate["compressed_size"],
        "candidate_tile_count": candidate["tile_count"],
        "candidate_nonblank_tile_count": candidate["nonblank_tile_count"],
        "raw_path": candidate["raw_path"],
        "preview_path": candidate["preview_path"],
    }


def strip_private_fields(item: dict) -> dict:
    return {key: value for key, value in item.items() if not key.startswith("_")}


def read_pgm(path: Path) -> tuple[int, int, bytes]:
    data = path.read_bytes()
    if not data.startswith(b"P5\n"):
        raise ValueError(f"not a raw PGM: {path}")
    cursor = 3
    while data[cursor : cursor + 1] == b"#":
        cursor = data.index(b"\n", cursor) + 1
    next_newline = data.index(b"\n", cursor)
    width, height = map(int, data[cursor:next_newline].split())
    cursor = next_newline + 1
    next_newline = data.index(b"\n", cursor)
    max_value = int(data[cursor:next_newline])
    if max_value != 255:
        raise ValueError(f"unsupported PGM max value {max_value}: {path}")
    return width, height, data[next_newline + 1 :]


def scale_gray(src: bytes, width: int, height: int, out_w: int, out_h: int) -> bytes:
    out = bytearray(out_w * out_h)
    for y in range(out_h):
        sy = min(height - 1, int(y * height / out_h))
        for x in range(out_w):
            sx = min(width - 1, int(x * width / out_w))
            out[y * out_w + x] = src[sy * width + sx]
    return bytes(out)


def png_chunk(kind: bytes, payload: bytes) -> bytes:
    return (
        struct.pack(">I", len(payload))
        + kind
        + payload
        + struct.pack(">I", binascii.crc32(kind + payload) & 0xFFFFFFFF)
    )


def write_png_gray(path: Path, width: int, height: int, pixels: bytes) -> None:
    rows = bytearray()
    for y in range(height):
        rows.append(0)
        rows.extend(pixels[y * width : (y + 1) * width])
    path.write_bytes(
        b"".join(
            [
                b"\x89PNG\r\n\x1a\n",
                png_chunk(b"IHDR", struct.pack(">IIBBBBB", width, height, 8, 0, 0, 0, 0)),
                png_chunk(b"IDAT", zlib.compress(bytes(rows), level=6)),
                png_chunk(b"IEND", b""),
            ]
        )
    )


def write_gallery(out_dir: Path, matches: list[dict], limit: int) -> str | None:
    out_dir.mkdir(parents=True, exist_ok=True)
    seen: set[tuple[str, int]] = set()
    chosen: list[dict] = []
    for runtime in matches:
        for candidate in runtime["matches"]:
            key = (candidate["source"], candidate["candidate_index"])
            if key in seen:
                continue
            seen.add(key)
            chosen.append(candidate)
            if len(chosen) >= limit:
                break
        if len(chosen) >= limit:
            break
    if not chosen:
        return None

    thumb_w = 160
    thumb_h = 96
    columns = 5
    gap = 4
    rows = math.ceil(len(chosen) / columns)
    width = columns * thumb_w + (columns - 1) * gap
    height = rows * thumb_h + (rows - 1) * gap
    sheet = bytearray([24] * width * height)

    for index, candidate in enumerate(chosen):
        pgm_path = ROOT / candidate["preview_path"]
        src_w, src_h, pixels = read_pgm(pgm_path)
        thumb = scale_gray(pixels, src_w, src_h, thumb_w, thumb_h)
        x0 = (index % columns) * (thumb_w + gap)
        y0 = (index // columns) * (thumb_h + gap)
        for y in range(thumb_h):
            dst = (y0 + y) * width + x0
            sheet[dst : dst + thumb_w] = thumb[y * thumb_w : (y + 1) * thumb_w]

    output = out_dir / "top_matched_rom_blocks_gallery.png"
    write_png_gray(output, width, height, bytes(sheet))
    return str(output.relative_to(ROOT))


def write_matched_preview_pngs(out_dir: Path, matches: list[dict]) -> None:
    preview_dir = out_dir / "matched_previews"
    preview_dir.mkdir(parents=True, exist_ok=True)
    seen: set[tuple[str, int]] = set()
    for runtime in matches:
        for candidate in runtime["matches"]:
            key = (candidate["source"], candidate["candidate_index"])
            output = preview_dir / (
                f"{candidate['source']}_{candidate['candidate_index']:04d}"
                f"_off_{candidate['offset']:08X}.png"
            )
            candidate["preview_png_path"] = str(output.relative_to(ROOT))
            if key in seen:
                continue
            seen.add(key)
            pgm_path = ROOT / candidate["preview_path"]
            width, height, pixels = read_pgm(pgm_path)
            write_png_gray(output, width, height, pixels)


def write_reports(out_dir: Path, matches: list[dict], gallery_path: str | None) -> None:
    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / "runtime_tile_matches.json").write_text(
        json.dumps(matches, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    lines = ["# Runtime Tile Matches", ""]
    if gallery_path:
        lines.append(f"- top gallery: `{gallery_path}`")
        lines.append("")
    for runtime in matches:
        lines.append(f"## `{runtime['frame']}` charblock `{runtime['charblock']}`")
        lines.append("")
        lines.append(
            f"- runtime nonblank tiles: `{runtime['nonblank_tile_count']}` / `{runtime['tile_count']}`"
        )
        for candidate in runtime["matches"]:
            lines.append(
                "- "
                f"score=`{candidate['score']}` shared=`{candidate['shared_tiles']}` "
                f"run=`{candidate['longest_contiguous_tile_run']}` "
                f"runtime_cov=`{candidate['runtime_coverage']}` cand_cov=`{candidate['candidate_coverage']}` "
                f"rom=`0x{candidate['offset']:08X}` preview=`{candidate.get('preview_png_path', candidate['preview_path'])}`"
            )
        lines.append("")
    (out_dir / "runtime_tile_matches.md").write_text("\n".join(lines), encoding="utf-8")


def main() -> int:
    args = parse_args()
    out_dir = args.out_dir.resolve()
    candidates = load_candidates(args.global_report.resolve())
    candidates.extend(load_rle_candidates(args.rle_report.resolve()))
    runtimes = iter_runtime_charblocks(args.probe_dir.resolve())
    matches: list[dict] = []

    for runtime in runtimes:
        scored = []
        for candidate in candidates:
            result = score_candidate(runtime, candidate)
            if not result:
                continue
            if result["shared_tiles"] < args.min_shared_tiles:
                continue
            scored.append(result)
        scored.sort(
            key=lambda item: (
                item["score"],
                item["longest_contiguous_tile_run"],
                item["shared_tiles"],
                item["candidate_coverage"],
            ),
            reverse=True,
        )
        matches.append({**strip_private_fields(runtime), "matches": scored[: args.top]})

    write_matched_preview_pngs(out_dir, matches)
    gallery_path = write_gallery(out_dir, matches, args.gallery_limit)
    write_reports(out_dir, matches, gallery_path)
    print(f"runtime charblocks: {len(runtimes)}")
    print(f"rom candidates   : {len(candidates)}")
    print(f"report           : {out_dir / 'runtime_tile_matches.md'}")
    if gallery_path:
        print(f"gallery          : {ROOT / gallery_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
