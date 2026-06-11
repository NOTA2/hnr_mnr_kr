# Image Scripts

Future home for image extraction, edit-pack generation, runtime visual evidence,
and image replacement helpers.

Current implementations still live in `scripts/` top level. Move them here only
after compatibility wrappers are in place.

## Current Top-Level Scripts

Active apply path:

- `scripts/apply_image_replacements.py`

Inventory and extraction:

- `scripts/build_image_source_manifest.py`
- `scripts/build_image_extraction_pipeline.py`
- `scripts/build_image_text_inventory.py`
- `scripts/build_graphics_extraction_progress.py`
- `scripts/build_actual_localization_tilemap_targets.py`
- `scripts/extract_global_image_tiles.py`
- `scripts/extract_image_review_candidates.py`
- `scripts/extract_rle_image_tiles.py`
- `scripts/extract_english_expanded_lz77_graphics.py`
- `scripts/extract_runtime_tilemap_localization_targets.py`

Edit-pack builders:

- `scripts/build_battle_command_button_edit_pack.py`
- `scripts/build_card_book_right_tabs_edit_pack.py`
- `scripts/build_card_list_labels_edit_pack.py`
- `scripts/build_card_list_power_labels_edit_pack.py`
- `scripts/build_card_page_count_edit_pack.py`
- `scripts/build_field_menu_label_edit_pack.py`
- `scripts/build_title_screen_edit_pack.py`

Review and matching helpers:

- `scripts/build_image_candidate_gallery.py`
- `scripts/build_rle_contact_sheets.py`
- `scripts/build_tile_contact_sheets.py`
- `scripts/build_rle_layout_variant_sheets.py`
- `scripts/build_readable_rle_layouts.py`
- `scripts/build_runtime_rle_patch_previews.py`
- `scripts/build_runtime_rle_screen_order_workspaces.py`
- `scripts/build_runtime_tile_sheets.py`
- `scripts/compare_english_patch_lz77_graphics.py`
- `scripts/compare_english_patch_rle_graphics.py`
- `scripts/match_runtime_tiles_to_rom_blocks.py`
- `scripts/link_image_review_previews.py`
- `scripts/register_runtime_visual_case.py`
- `scripts/build_expanded_nearby_image_candidates.py`

## Move Holds

- `run_localization_workbench.py` calls `apply_image_replacements.py` by
  top-level path.
- `confirmed_data/image_inventory/` is still high risk. Do not archive image
  scripts until the minimal final image-source manifest exists.
- Runtime captures and contact sheets are evidence, not necessarily edit
  sources. Preserve that distinction when regrouping.

## Future Migration Shape

Separate final image apply tools from extraction/contact-sheet/debug helpers.
Only archive generated-review helpers after `docs/cleanup/image_inventory_audit.md`
has a matching keep/delete decision for their outputs.
