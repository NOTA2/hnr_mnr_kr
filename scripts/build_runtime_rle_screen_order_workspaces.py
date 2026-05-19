#!/usr/bin/env python3
"""Build tilemap-aware, screen-order edit workspaces for runtime-matched RLE blocks.

Raw RLE sheets are often unreadable because the game places the tiles through
BG screenblocks. This script scans the runtime match reports, reassembles each
matched RLE block in the on-screen order, and writes a manifest that the
localization workbench can expose as editable image items.
"""

from __future__ import annotations

import argparse
import json
import struct
from pathlib import Path

from build_runtime_rle_patch_previews import (
    ROOT,
    build_match_only_view,
    bounds,
    crop_rgb,
    draw_border_rgb,
    find_rle_block,
    frame_prefix,
    read_bg_control,
    rle_tile_index,
    runtime_matches,
    scale_rgb,
)
from render_runtime_tilemaps import (
    SCREEN_H,
    SCREEN_W,
    crop_viewport,
    read_palette,
    render_bg_map,
    write_png_rgb,
)


IMAGE_INVENTORY = ROOT / "confirmed_data" / "image_inventory"
MATCH_ROOT = IMAGE_INVENTORY / "runtime_tile_matches"
CAPTURE_ROOT = IMAGE_INVENTORY / "runtime_user_captures"
TIMELINE_CAPTURE_ROOT = IMAGE_INVENTORY / "pymgba_runtime_timeline"
RLE_REPORT = IMAGE_INVENTORY / "rle_tile_extraction" / "notes" / "rle_tile_extraction_report.json"
OUT_ROOT = IMAGE_INVENTORY / "runtime_rle_screen_order"


KNOWN_LABELS = {
    0x003A206C: "전투 메뉴 워드마크 ALCHEMY/SKILL/ITEM/CARD/NETWORK",
    0x00186AE8: "전투 HUD 소형 숫자/상태 표시",
    0x003ABB9C: "OK? 예/아니요 팝업",
    0x003AF23C: "연성/사용/버리기/돌아가기 팝업",
    0x005323AC: "필드/카드 라벨 錬成",
    0x0053257C: "필드/카드 라벨 アセやし",
    0x007E0000: "타이틀 로고/저작권",
    0x007E9158: "타이틀 PUSH START",
    0x007E9404: "타이틀 처음부터",
    0x007E95E0: "타이틀 이어하기",
    0x007E97A4: "타이틀 통신",
}

HIGH_VALUE_OFFSETS = {
    0x003A206C,
    0x003ABB9C,
    0x003AF23C,
    0x007E0000,
    0x007E9158,
    0x007E9404,
    0x007E95E0,
    0x007E97A4,
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out-dir", type=Path, default=OUT_ROOT)
    parser.add_argument("--min-tiles", type=int, default=4)
    parser.add_argument("--max-per-scene", type=int, default=24)
    parser.add_argument("--padding-tiles", type=int, default=1)
    return parser.parse_args()


def read_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, payload) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def probe_dir_for_scene(scene: str) -> Path | None:
    direct = CAPTURE_ROOT / scene
    if direct.exists():
        return direct
    if scene.startswith("timeline") and TIMELINE_CAPTURE_ROOT.exists():
        return TIMELINE_CAPTURE_ROOT
    return None


def active_bg_indexes(ioreg: bytes) -> list[int]:
    dispcnt = struct.unpack_from("<H", ioreg, 0)[0]
    mode = dispcnt & 0x7
    bgs: list[int] = []
    for bg in range(4):
        if not (dispcnt & (1 << (8 + bg))):
            continue
        if mode > 1 and bg < 2:
            continue
        bgs.append(bg)
    return bgs


def unique_rle_matches(match_report: list[dict], max_per_scene: int) -> list[dict]:
    best_by_offset: dict[int, dict] = {}
    for runtime in match_report:
        for match in runtime.get("matches", []):
            if match.get("source") != "rle":
                continue
            offset = int(match["offset"])
            current = best_by_offset.get(offset)
            if current is None or float(match.get("score", 0)) > float(current.get("score", 0)):
                best_by_offset[offset] = {**match, "frame": runtime.get("frame", "")}
    ranked = sorted(
        best_by_offset.values(),
        key=lambda item: (
            int(item["offset"]) in HIGH_VALUE_OFFSETS,
            float(item.get("candidate_coverage", 0)),
            float(item.get("score", 0)),
            int(item.get("shared_tiles", 0)),
        ),
        reverse=True,
    )
    return ranked[:max_per_scene]


def crop_and_write(
    *,
    out_dir: Path,
    scene: str,
    frame: str,
    bg: int,
    rle_offset: int,
    rle_raw_path: str,
    vram: bytes,
    palette: list[tuple[int, int, int]],
    control: dict,
    matches: list[dict],
    padding_tiles: int,
    palette_path: Path,
    source_match: dict,
) -> dict:
    crop_box = bounds(matches, padding_tiles)
    min_x, min_y, max_x, max_y = crop_box
    crop_px = (min_x * 8, min_y * 8, (max_x - min_x + 1) * 8, (max_y - min_y + 1) * 8)

    map_w, map_h, bg_pixels = render_bg_map(vram, palette, control["bgcnt"])
    viewport = crop_viewport(bg_pixels, map_w, map_h, control["scroll_x"], control["scroll_y"])
    context_plain = crop_rgb(viewport, SCREEN_W, *crop_px)
    context_grid = bytearray(context_plain)
    for item in matches:
        draw_border_rgb(
            context_grid,
            crop_px[2],
            crop_px[3],
            (item["screen_tile_x"] - min_x) * 8,
            (item["screen_tile_y"] - min_y) * 8,
            8,
            8,
            (255, 64, 64),
        )

    matched_plain = build_match_only_view(vram, palette, control, matches, crop_box)
    matched_grid = build_match_only_view(vram, palette, control, matches, crop_box, draw_grid=True)

    out_dir.mkdir(parents=True, exist_ok=True)
    write_png_rgb(out_dir / "context_crop.png", crop_px[2], crop_px[3], context_plain)
    write_png_rgb(out_dir / "context_crop_grid.png", crop_px[2], crop_px[3], bytes(context_grid))
    write_png_rgb(out_dir / "context_crop_4x.png", *scale_rgb(context_plain, crop_px[2], crop_px[3], 4))
    write_png_rgb(out_dir / "matched_tiles_screen_order.png", crop_px[2], crop_px[3], matched_plain)
    write_png_rgb(out_dir / "matched_tiles_screen_order_grid.png", crop_px[2], crop_px[3], matched_grid)
    write_png_rgb(out_dir / "matched_tiles_screen_order_4x.png", *scale_rgb(matched_plain, crop_px[2], crop_px[3], 4))

    payload = {
        "scene": scene,
        "frame": frame,
        "bg": bg,
        "rle_offset": rle_offset,
        "rle_offset_hex": f"0x{rle_offset:08X}",
        "rle_raw_path": rle_raw_path,
        "runtime_palette_path": str(palette_path.relative_to(ROOT)),
        "crop_screen_tiles": {"min_x": min_x, "min_y": min_y, "max_x": max_x, "max_y": max_y},
        "crop_pixels": {"x": crop_px[0], "y": crop_px[1], "width": crop_px[2], "height": crop_px[3]},
        "matched_tile_count": len(matches),
        "source_match": {
            "score": source_match.get("score"),
            "shared_tiles": source_match.get("shared_tiles"),
            "runtime_coverage": source_match.get("runtime_coverage"),
            "candidate_coverage": source_match.get("candidate_coverage"),
            "candidate_index": source_match.get("candidate_index"),
            "decompressed_size": source_match.get("decompressed_size"),
            "compressed_size": source_match.get("compressed_size"),
        },
        "matches": matches,
    }
    write_json(out_dir / "tile_map.json", payload)

    return {
        "scene": scene,
        "frame": frame,
        "bg": bg,
        "offset": rle_offset,
        "offset_hex": f"0x{rle_offset:08X}",
        "label": KNOWN_LABELS.get(rle_offset, f"RLE 0x{rle_offset:08X} 화면순 재조립"),
        "workspace": str(out_dir.relative_to(ROOT)),
        "context_preview_path": str((out_dir / "context_crop_4x.png").relative_to(ROOT)),
        "editable_preview_path": str((out_dir / "matched_tiles_screen_order_4x.png").relative_to(ROOT)),
        "source_download_path": str((out_dir / "matched_tiles_screen_order_4x.png").relative_to(ROOT)),
        "tile_map_path": str((out_dir / "tile_map.json").relative_to(ROOT)),
        "matched_tile_count": len(matches),
        "score": source_match.get("score"),
        "shared_tiles": source_match.get("shared_tiles"),
        "candidate_coverage": source_match.get("candidate_coverage"),
        "runtime_coverage": source_match.get("runtime_coverage"),
        "replacement_target": True,
    }


def render_scene(scene: str, match_json: Path, out_root: Path, *, min_tiles: int, max_per_scene: int, padding_tiles: int) -> list[dict]:
    probe_dir = probe_dir_for_scene(scene)
    if probe_dir is None:
        return []
    match_report = read_json(match_json)
    source_matches = unique_rle_matches(match_report, max_per_scene)
    if not source_matches:
        return []

    produced: list[dict] = []
    rle_cache: dict[int, tuple[dict, dict[bytes, list[int]]]] = {}
    for source_match in source_matches:
        frame = str(source_match.get("frame") or frame_prefix(probe_dir, ""))
        vram_path = probe_dir / f"{frame}_vram_06000000.bin"
        ioreg_path = probe_dir / f"{frame}_ioreg_04000000.bin"
        palette_path = probe_dir / f"{frame}_palette_05000000.bin"
        if not vram_path.exists() or not ioreg_path.exists() or not palette_path.exists():
            continue
        vram = vram_path.read_bytes()
        ioreg = ioreg_path.read_bytes()
        palette = read_palette(palette_path.read_bytes())
        offset = int(source_match["offset"])
        if offset not in rle_cache:
            rle_block = find_rle_block(RLE_REPORT, offset)
            rle_raw = (ROOT / rle_block["raw_path"]).read_bytes()
            rle_cache[offset] = (rle_block, rle_tile_index(rle_raw))
        rle_block, index = rle_cache[offset]

        for bg in active_bg_indexes(ioreg):
            control = read_bg_control(ioreg, bg)
            if control["is_8bpp"]:
                continue
            matches = runtime_matches(vram, control, index)
            if len(matches) < min_tiles:
                continue
            out_dir = out_root / scene / f"{frame}_bg{bg}_rle_{offset:08X}"
            produced.append(
                crop_and_write(
                    out_dir=out_dir,
                    scene=scene,
                    frame=frame,
                    bg=bg,
                    rle_offset=offset,
                    rle_raw_path=rle_block["raw_path"],
                    vram=vram,
                    palette=palette,
                    control=control,
                    matches=matches,
                    padding_tiles=padding_tiles,
                    palette_path=palette_path,
                    source_match=source_match,
                )
            )
    return produced


def write_index(out_root: Path, manifest: list[dict]) -> None:
    lines = [
        "# Runtime RLE Screen-Order Workspaces",
        "",
        "런타임 BG tilemap을 적용해 RLE 타일을 실제 화면 배치에 가깝게 재조립한 편집 후보입니다.",
        "",
        "| label | scene | bg | offset | tiles | preview |",
        "| --- | --- | ---: | --- | ---: | --- |",
    ]
    for item in manifest:
        lines.append(
            "| {label} | `{scene}` | `{bg}` | `{offset}` | `{tiles}` | `{preview}` |".format(
                label=item["label"],
                scene=item["scene"],
                bg=item["bg"],
                offset=item["offset_hex"],
                tiles=item["matched_tile_count"],
                preview=item["context_preview_path"],
            )
        )
    (out_root / "README.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    args = parse_args()
    out_root = args.out_dir.resolve()
    manifest: list[dict] = []
    for match_json in sorted(MATCH_ROOT.glob("*/runtime_tile_matches.json")):
        scene = match_json.parent.name
        manifest.extend(
            render_scene(
                scene,
                match_json,
                out_root,
                min_tiles=args.min_tiles,
                max_per_scene=args.max_per_scene,
                padding_tiles=args.padding_tiles,
            )
        )
    manifest.sort(key=lambda item: (item["scene"], item["frame"], item["bg"], item["offset"]))
    write_json(out_root / "screen_order_manifest.json", manifest)
    write_index(out_root, manifest)
    print(f"screen-order workspaces: {len(manifest)}")
    print(f"manifest: {out_root / 'screen_order_manifest.json'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
