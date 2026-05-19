#!/usr/bin/env python3
"""Summarize graphics extraction progress for the localization workbench."""

from __future__ import annotations

import json
from collections import Counter
from datetime import datetime
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
IMAGE_ROOT = ROOT / "confirmed_data" / "image_inventory"
WORKBENCH_ROOT = ROOT / "confirmed_data" / "localization_workbench"
OUT_JSON = IMAGE_ROOT / "graphics_extraction_progress.json"
OUT_MD = IMAGE_ROOT / "graphics_extraction_progress.md"


def load_json(path: Path, default):
    if not path.exists():
        return default
    return json.loads(path.read_text(encoding="utf-8"))


def count_pngs(path: Path) -> int:
    if not path.exists():
        return 0
    return sum(1 for _ in path.rglob("*.png"))


def unique_offsets_from_runtime_matches() -> dict[str, set[int]]:
    offsets: dict[str, set[int]] = {"lz77": set(), "rle": set(), "raw": set()}
    match_root = IMAGE_ROOT / "runtime_tile_matches"
    for path in match_root.glob("*/runtime_tile_matches.json"):
        payload = load_json(path, [])
        for frame in payload:
            for match in frame.get("matches", []):
                source = str(match.get("source", ""))
                if source in offsets and "offset" in match:
                    offsets[source].add(int(match["offset"]))
    return offsets


def main() -> int:
    lz77_report = load_json(IMAGE_ROOT / "global_tile_extraction" / "notes" / "global_tile_extraction_report.json", {})
    rle_report = load_json(IMAGE_ROOT / "rle_tile_extraction" / "notes" / "rle_tile_extraction_report.json", {})
    en_lz77_diff = load_json(IMAGE_ROOT / "english_patch_diff" / "notes" / "english_patch_lz77_diff_report.json", {})
    en_rle_diff = load_json(
        IMAGE_ROOT / "english_patch_diff" / "rle_same_offset" / "notes" / "english_patch_rle_same_offset_diff.json",
        {},
    )
    image_items = load_json(WORKBENCH_ROOT / "image_replacements.json", [])
    screen_order_manifest = load_json(IMAGE_ROOT / "runtime_rle_screen_order" / "screen_order_manifest.json", [])
    actual_targets = load_json(IMAGE_ROOT / "localization_targets" / "actual_localization_targets.json", [])
    runtime_tilemap_targets = load_json(IMAGE_ROOT / "runtime_tilemap_targets" / "runtime_tilemap_targets.json", [])
    runtime_offsets = unique_offsets_from_runtime_matches()

    progress_counter = Counter(item.get("progress_status", "unknown") for item in image_items)
    editable_items = [item for item in image_items if item.get("replacement_target") is not False]
    uploaded_items = [item for item in image_items if item.get("replacement_path")]
    error_items = [
        item
        for item in image_items
        for result in (item.get("last_apply_summary", {}) or {}).get("results", [])
        if result.get("status") == "error"
    ]

    summary = {
        "generated_at": datetime.now().isoformat(timespec="seconds"),
        "rom_static_extraction": {
            "lz77_blocks": int(lz77_report.get("lz77_count", len(lz77_report.get("lz77", [])))),
            "raw_windows": int(lz77_report.get("raw_count", len(lz77_report.get("raw", [])))),
            "rle_blocks": int(rle_report.get("count", len(rle_report.get("blocks", [])))),
        },
        "english_patch_diff": {
            "lz77_compared": int(en_lz77_diff.get("compared", 0)),
            "lz77_changed": int(en_lz77_diff.get("changed_count", 0)),
            "rle_compared": int(en_rle_diff.get("compared", 0)),
            "rle_changed": int(en_rle_diff.get("changed_count", 0)),
        },
        "runtime_matching": {
            "captures_with_match_json": len(list((IMAGE_ROOT / "runtime_tile_matches").glob("*/runtime_tile_matches.json"))),
            "matched_lz77_offsets": len(runtime_offsets["lz77"]),
            "matched_rle_offsets": len(runtime_offsets["rle"]),
            "matched_raw_offsets": len(runtime_offsets["raw"]),
            "matched_total_unique_offsets": sum(len(values) for values in runtime_offsets.values()),
        },
        "workbench": {
            "image_items": len(image_items),
            "directly_editable_items": len(editable_items),
            "uploaded_replacements": len(uploaded_items),
            "items_with_apply_errors": len(error_items),
            "progress_status_counts": dict(sorted(progress_counter.items())),
            "actual_localization_targets": len(actual_targets),
            "focused_runtime_tilemap_targets": len(runtime_tilemap_targets),
        },
        "preview_assets": {
            "global_lz77_pngs": count_pngs(IMAGE_ROOT / "global_tile_extraction" / "lz77_png"),
            "global_lz77_pgms": len(list((IMAGE_ROOT / "global_tile_extraction" / "lz77_pgm").glob("*.pgm"))),
            "rle_pgms": len(list((IMAGE_ROOT / "rle_tile_extraction" / "rle_pgm").glob("*.pgm"))),
            "runtime_match_pngs": count_pngs(IMAGE_ROOT / "runtime_tile_matches"),
            "runtime_tilemap_pngs": count_pngs(IMAGE_ROOT / "runtime_tilemaps"),
            "runtime_rle_screen_order_workspaces": len(screen_order_manifest),
            "runtime_rle_screen_order_pngs": count_pngs(IMAGE_ROOT / "runtime_rle_screen_order"),
            "edit_pack_pngs": count_pngs(IMAGE_ROOT / "edit_packs"),
        },
        "open_risks": [
            "Static extraction counts are discovery totals, not localization-needed totals.",
            "Raw RLE tile sheets can be misleading when the game reorders tiles through runtime tilemaps.",
            "Runtime coverage depends on collected savestates/screens; newly reached screens can reveal more image assets.",
            "Title-screen menu graphics need tilemap-aware replacement testing, not blind raw tile replacement.",
        ],
    }

    OUT_JSON.write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    lines = [
        "# Graphics Extraction Progress",
        "",
        f"Generated: `{summary['generated_at']}`",
        "",
        "## Static ROM Extraction",
        "",
        f"- LZ77 blocks extracted: `{summary['rom_static_extraction']['lz77_blocks']}`",
        f"- RLE blocks extracted: `{summary['rom_static_extraction']['rle_blocks']}`",
        f"- Raw scan windows rendered: `{summary['rom_static_extraction']['raw_windows']}`",
        "",
        "## English Patch Diff",
        "",
        f"- LZ77 compared/changed: `{summary['english_patch_diff']['lz77_compared']}` / `{summary['english_patch_diff']['lz77_changed']}`",
        f"- RLE compared/changed: `{summary['english_patch_diff']['rle_compared']}` / `{summary['english_patch_diff']['rle_changed']}`",
        "",
        "## Runtime Matching",
        "",
        f"- Runtime match sets: `{summary['runtime_matching']['captures_with_match_json']}`",
        f"- Unique matched LZ77/RLE/raw offsets: `{summary['runtime_matching']['matched_lz77_offsets']}` / `{summary['runtime_matching']['matched_rle_offsets']}` / `{summary['runtime_matching']['matched_raw_offsets']}`",
        f"- Total unique runtime-matched offsets: `{summary['runtime_matching']['matched_total_unique_offsets']}`",
        "",
        "## Workbench",
        "",
        f"- GUI image items: `{summary['workbench']['image_items']}`",
        f"- Directly editable items: `{summary['workbench']['directly_editable_items']}`",
        f"- Uploaded replacements: `{summary['workbench']['uploaded_replacements']}`",
        f"- Items with apply errors: `{summary['workbench']['items_with_apply_errors']}`",
        f"- Progress states: `{summary['workbench']['progress_status_counts']}`",
        f"- Actual localization targets curated: `{summary['workbench']['actual_localization_targets']}`",
        f"- Focused runtime tilemap targets: `{summary['workbench']['focused_runtime_tilemap_targets']}`",
        "",
        "## Preview Assets",
        "",
        f"- Runtime match PNGs: `{summary['preview_assets']['runtime_match_pngs']}`",
        f"- Runtime tilemap PNGs: `{summary['preview_assets']['runtime_tilemap_pngs']}`",
        f"- Runtime RLE screen-order workspaces: `{summary['preview_assets']['runtime_rle_screen_order_workspaces']}`",
        f"- Runtime RLE screen-order PNGs: `{summary['preview_assets']['runtime_rle_screen_order_pngs']}`",
        f"- Edit-pack PNGs: `{summary['preview_assets']['edit_pack_pngs']}`",
        "",
        "## Open Risks",
        "",
    ]
    lines.extend(f"- {risk}" for risk in summary["open_risks"])
    lines.append("")
    OUT_MD.write_text("\n".join(lines), encoding="utf-8")
    print(f"wrote {OUT_JSON.relative_to(ROOT)}")
    print(f"wrote {OUT_MD.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
