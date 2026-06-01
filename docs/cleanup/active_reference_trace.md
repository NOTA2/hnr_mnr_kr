# Active Reference Trace

Date: 2026-06-02 KST

This is a conservative trace from the two most important active GUI data files:

- `confirmed_data/localization_workbench/workbench_dataset.json`
- `confirmed_data/localization_workbench/image_replacements.json`

The trace extracts path-like strings and normalizes `/Users/user/test/...` to
repo-relative paths. It is not a complete dependency graph, but it is a useful
guardrail before cleanup.

## Summary

- Unique path-like references in active GUI data: `5,252`
- Missing referenced paths on disk: `0`
- Tracked `confirmed_data/image_inventory` files directly referenced: `4,882`
- Tracked `confirmed_data/image_inventory` files not directly referenced: `10,899`

## Referenced Path Families

- `confirmed_data/image_inventory/edit_packs`: `4,867`
- `confirmed_data/localization_workbench/uploaded_image_replacements`: `340`
- `confirmed_data/image_inventory/runtime_rle_screen_order`: `15`
- `confirmed_data/image_inventory/runtime_tile_matches`: `11`
- `confirmed_data/image_inventory/english_patch_diff`: `3`
- `third_party/font_atlases/finalists`: `2`
- `patched_roms/current_review/hnr_localization_review.gba`: `1`
- `local_roms/english_patched/Fullmetal Alchemist Stray Rondo (English Patched v0.02).gba`: `1`
- selected translation worksets and reports: several single-file references

## Unreferenced Tracked Image Inventory Families

Unreferenced here means "not directly referenced by the active GUI JSON files".
It does not mean safe to delete.

- `confirmed_data/image_inventory/workspaces`: `2,776`
- `confirmed_data/image_inventory/rle_tile_extraction`: `2,235`
- `confirmed_data/image_inventory/global_tile_extraction`: `1,924`
- `confirmed_data/image_inventory/edit_packs`: `932`
- `confirmed_data/image_inventory/runtime_rle_screen_order`: `827`
- `confirmed_data/image_inventory/runtime_tile_sheets`: `614`
- `confirmed_data/image_inventory/runtime_tile_matches`: `545`
- `confirmed_data/image_inventory/runtime_tilemaps`: `317`
- `confirmed_data/image_inventory/runtime_user_captures`: `175`
- `confirmed_data/image_inventory/english_patch_diff`: `164`
- `confirmed_data/image_inventory/runtime_rle_patch_previews`: `72`
- `confirmed_data/image_inventory/savestate_compare_labels`: `72`
- `confirmed_data/image_inventory/localization_targets`: `60`
- `confirmed_data/image_inventory/runtime_tilemap_targets`: `50`

## Immediate Interpretation

- The active GUI data is internally consistent enough for cleanup planning:
  all referenced paths exist.
- Most active references point into `edit_packs`, so that folder is not a blanket
  deletion target.
- `workspaces`, broad extraction folders, runtime captures, tilemaps, and contact
  sheets are the largest cleanup candidates, but they need retrospective/evidence
  review first.
- `uploaded_image_replacements` is ignored by `.gitignore`, but active JSON points
  at local files there. For final release, replacements should either be promoted
  into a tracked, repo-local asset folder or the build should document that local
  uploads are required.

## Next Trace Pass

1. Trace script imports and hard-coded paths from `scripts/`.
2. Trace manifest references inside active `edit_packs`.
3. Identify preview-only scaled assets that can be regenerated.
4. Separate "final editable source" from "debug/contact-sheet/reference" images.

