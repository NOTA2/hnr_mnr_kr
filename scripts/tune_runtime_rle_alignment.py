#!/usr/bin/env python3
"""Retune a runtime RLE screen-order workspace by pixel shift numbers.

Use this when a screen-order extraction is basically correct, but the rebuilt
tiles are a few pixels off from the runtime context because of scroll residue or
another alignment quirk. The script rewrites the workspace previews and stores
the chosen shift in tile_map.json, so later ROM insertion uses the same numbers.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT / "scripts") not in sys.path:
    sys.path.insert(0, str(ROOT / "scripts"))

from build_runtime_rle_patch_previews import read_bg_control, rle_tile_index, runtime_matches
from build_runtime_rle_screen_order_workspaces import crop_and_write, probe_dir_for_scene
from render_runtime_tilemaps import read_palette


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("tile_map", type=Path, help="Path to a runtime_rle_screen_order tile_map.json")
    parser.add_argument("--shift-x", type=int, default=None, help="Absolute pixel shift for rebuilt tiles. Positive moves right.")
    parser.add_argument("--shift-y", type=int, default=None, help="Absolute pixel shift for rebuilt tiles. Positive moves down.")
    parser.add_argument("--add-shift-x", type=int, default=0, help="Add this many pixels to the current x shift.")
    parser.add_argument("--add-shift-y", type=int, default=0, help="Add this many pixels to the current y shift.")
    parser.add_argument("--padding-tiles", type=int, default=None, help="Crop padding in 8x8 tiles. Defaults to the current map padding.")
    parser.add_argument("--min-tiles", type=int, default=1)
    return parser.parse_args()


def read_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def workspace_path(path: Path) -> Path:
    resolved = (ROOT / path).resolve() if not path.is_absolute() else path.resolve()
    if not resolved.is_file() or ROOT not in resolved.parents:
        raise FileNotFoundError(f"tile map is not inside the workspace: {path}")
    return resolved


def infer_padding(tile_map: dict) -> int:
    matches = tile_map.get("matches", [])
    crop = tile_map.get("crop_screen_tiles", {})
    if not matches or not crop:
        return 1
    min_x = min(int(item["screen_tile_x"]) for item in matches)
    min_y = min(int(item["screen_tile_y"]) for item in matches)
    max_x = max(int(item["screen_tile_x"]) for item in matches)
    max_y = max(int(item["screen_tile_y"]) for item in matches)
    pads = [
        min_x - int(crop.get("min_x", min_x)),
        min_y - int(crop.get("min_y", min_y)),
        int(crop.get("max_x", max_x)) - max_x,
        int(crop.get("max_y", max_y)) - max_y,
    ]
    return max(0, max(pads))


def frame_paths(probe_dir: Path, frame: str) -> tuple[Path, Path, Path]:
    vram_path = probe_dir / f"{frame}_vram_06000000.bin"
    ioreg_path = probe_dir / f"{frame}_ioreg_04000000.bin"
    palette_path = probe_dir / f"{frame}_palette_05000000.bin"
    missing = [path for path in (vram_path, ioreg_path, palette_path) if not path.exists()]
    if missing:
        raise FileNotFoundError("missing runtime dump files: " + ", ".join(str(path) for path in missing))
    return vram_path, ioreg_path, palette_path


def main() -> int:
    args = parse_args()
    tile_map_path = workspace_path(args.tile_map)
    tile_map = read_json(tile_map_path)
    scene = str(tile_map["scene"])
    frame = str(tile_map["frame"])
    bg = int(tile_map["bg"])
    rle_offset = int(tile_map["rle_offset"])

    probe_dir = probe_dir_for_scene(scene)
    if probe_dir is None:
        raise FileNotFoundError(f"runtime probe directory not found for scene: {scene}")
    vram_path, ioreg_path, palette_path = frame_paths(probe_dir, frame)
    vram = vram_path.read_bytes()
    ioreg = ioreg_path.read_bytes()
    palette = read_palette(palette_path.read_bytes())
    control = read_bg_control(ioreg, bg)

    current = tile_map.get("alignment_adjustment_pixels") or {}
    current_x = int(current.get("x", 0))
    current_y = int(current.get("y", 0))
    shift_x = args.shift_x if args.shift_x is not None else current_x + args.add_shift_x
    shift_y = args.shift_y if args.shift_y is not None else current_y + args.add_shift_y
    control["alignment_adjustment_pixels"] = {"x": int(shift_x), "y": int(shift_y)}

    rle_raw_path = (ROOT / tile_map["rle_raw_path"]).resolve()
    if not rle_raw_path.exists():
        raise FileNotFoundError(f"RLE raw payload not found: {rle_raw_path}")
    rle_raw = rle_raw_path.read_bytes()
    matches = runtime_matches(vram, control, rle_tile_index(rle_raw))
    if len(matches) < args.min_tiles:
        raise ValueError(f"only {len(matches)} matched tiles after retune")

    padding_tiles = args.padding_tiles if args.padding_tiles is not None else infer_padding(tile_map)
    item = crop_and_write(
        out_dir=tile_map_path.parent,
        scene=scene,
        frame=frame,
        bg=bg,
        rle_offset=rle_offset,
        rle_raw_path=tile_map["rle_raw_path"],
        vram=vram,
        palette=palette,
        control=control,
        matches=matches,
        padding_tiles=padding_tiles,
        palette_path=palette_path,
        source_match=tile_map.get("source_match", {}),
    )
    summary = {
        "tile_map": str(tile_map_path.relative_to(ROOT)),
        "shift": {"x": int(shift_x), "y": int(shift_y)},
        "padding_tiles": padding_tiles,
        "matched_tile_count": len(matches),
        "context_preview_path": item["context_preview_path"],
        "editable_preview_path": item["editable_preview_path"],
    }
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
