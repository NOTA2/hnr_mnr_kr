#!/usr/bin/env python3

from __future__ import annotations

import json
from pathlib import Path

from build_tile_contact_sheets import ROOT, read_pgm, write_png_gray


WORKSPACES = ROOT / "confirmed_data" / "image_inventory" / "workspaces"
WORKBENCH = ROOT / "confirmed_data" / "localization_workbench"
IMAGE_REPLACEMENTS_PATH = WORKBENCH / "image_replacements.json"
DATASET_PATH = WORKBENCH / "workbench_dataset.json"


def read_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, payload) -> None:
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def pgm_to_png(pgm_path: Path, png_path: Path) -> None:
    width, height, pixels = read_pgm(pgm_path)
    write_png_gray(png_path, width, height, pixels)


def build_gallery_for_report(report_path: Path) -> tuple[str, list[dict]]:
    report = read_json(report_path)
    workspace = report_path.parent.parent
    png_dir = workspace / "png_exports"
    png_dir.mkdir(parents=True, exist_ok=True)
    gallery: list[dict] = []
    for index, candidate in enumerate(report.get("candidates", []), start=1):
        pgm_path = ROOT / candidate["preview_path"]
        png_path = png_dir / f"{index:03d}_off_{int(candidate['offset']):08X}.png"
        pgm_to_png(pgm_path, png_path)
        gallery.append(
            {
                "index": index,
                "offset": candidate.get("offset"),
                "rom_address": candidate.get("rom_address"),
                "compressed_size": candidate.get("compressed_size"),
                "decompressed_size": candidate.get("decompressed_size"),
                "tile_count": candidate.get("tile_count"),
                "png_path": str(png_path.relative_to(ROOT)),
                "raw_path": candidate.get("raw_path"),
            }
        )
    gallery_path = workspace / "notes" / "candidate_gallery.json"
    write_json(gallery_path, gallery)
    return str(report.get("review_unit")), gallery


def main() -> int:
    galleries: dict[str, list[dict]] = {}
    converted = 0
    for report_path in sorted(WORKSPACES.glob("*/notes/*candidate_report.json")):
        unit, gallery = build_gallery_for_report(report_path)
        galleries[unit] = gallery
        converted += len(gallery)

    image_items = read_json(IMAGE_REPLACEMENTS_PATH)
    linked = 0
    for item in image_items:
        unit = item.get("group_id")
        gallery = galleries.get(unit)
        if not gallery:
            continue
        item["candidate_gallery"] = gallery
        linked += 1
    write_json(IMAGE_REPLACEMENTS_PATH, image_items)

    dataset = read_json(DATASET_PATH)
    image_map = {item["item_id"]: item for item in image_items}
    for item in dataset.get("items", []):
        if item.get("category_id") != "image_review_units":
            continue
        sidecar = image_map.get(item["item_id"])
        if sidecar and "candidate_gallery" in sidecar:
            item["candidate_gallery"] = sidecar["candidate_gallery"]
    write_json(DATASET_PATH, dataset)

    print(f"converted candidate PNGs: {converted}")
    print(f"linked GUI image items: {linked}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
