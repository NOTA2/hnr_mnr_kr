# Image Inventory Audit

Date: 2026-06-02 KST

This audit covers `confirmed_data/image_inventory/`.

## Size / Tracked Shape

Largest tracked families:

- `edit_packs`: `5,789` tracked files, about `28M`
- `workspaces`: `2,776` tracked files, about `86M`
- `rle_tile_extraction`: `2,235` tracked files, about `33M`
- `global_tile_extraction`: `1,924` tracked files, about `52M`
- `runtime_rle_screen_order`: `839` tracked files, about `17M`
- `runtime_tile_matches`: `554` tracked files, about `6.2M`

## Active GUI Trace

Direct active GUI references from `workbench_dataset.json` and
`image_replacements.json`:

- `workspaces`: `0`
- `global_tile_extraction`: `0`
- `rle_tile_extraction`: `0`

This does not make them safe to delete. It only means the current workbench GUI
does not directly load them as active replacement assets.

## Script / Workflow References

Do not remove `rle_tile_extraction` or `global_tile_extraction` as a batch yet.
Several scripts use their reports as default inputs:

- `scripts/apply_image_replacements.py`
- `scripts/compare_english_patch_rle_graphics.py`
- `scripts/build_runtime_rle_patch_previews.py`
- `scripts/match_runtime_tiles_to_rom_blocks.py`
- `scripts/build_readable_rle_layouts.py`
- `scripts/build_rle_contact_sheets.py`
- `scripts/build_rle_layout_variant_sheets.py`

`workspaces` is not directly used by active GUI JSON, but it is referenced by
`image_text_inventory.md` as the review-unit evidence area for image-side audit.

## Current Decision

No image inventory files were removed or untracked in this pass.

Reason:

- image-side QA is still active;
- RLE/global extraction reports are script defaults;
- `workspaces` holds review evidence and candidate reports that may still matter
  for the retrospective and remaining image pass.

## 2026-06-12 Manifest Baseline

`confirmed_data/image_inventory/image_source_manifest.md` now captures the first
cleanup manifest baseline:

- image replacement items: `2,406`
- edited items with replacement files: `211`
- missing non-empty replacement files: `0`
- missing source download files: `0`
- missing source preview files: `0`

`confirmed_data/image_inventory/image_source_manifest.json` now expands this
into an item-level machine-readable manifest:

- item-level records: `2,406`
- missing path count: `0`
- active source role records from `edit_packs`: `2,394`
- active runtime evidence source records: `12`

This does not make image inventory safe to prune yet. It defines the baseline
for separating active source/replacement/runtime evidence from generated previews
and broader historical extraction outputs.

## Next Safe Image Cleanup Order

1. Keep `edit_packs` and active uploaded replacements.
2. Keep `image_source_manifest.json` current with active GUI state.
3. Summarize review-unit lessons from `workspaces`.
4. Only then untrack or archive `workspaces` generated exports/dumps.
5. Treat `rle_tile_extraction` and `global_tile_extraction` as regenerable only
   after their report inputs are either promoted or documented.
