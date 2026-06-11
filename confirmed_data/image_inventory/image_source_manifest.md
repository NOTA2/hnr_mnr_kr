# Image Source Manifest

Status: draft

Date: 2026-06-12 KST

This manifest is a cleanup safety layer for image-side assets. It summarizes the
active GUI image replacement state before any large `confirmed_data/image_inventory`
cleanup. It is not yet a full item-by-item machine-readable manifest.

## Source Inputs

- `confirmed_data/localization_workbench/image_replacements.json`
- `confirmed_data/localization_workbench/workbench_dataset.json`
- `confirmed_data/image_inventory/image_text_inventory.json`
- `confirmed_data/image_inventory/image_extraction_pipeline.json`

## Current GUI Image Replacement Summary

- Total image replacement items: `2,406`
- `candidate_found`: `2,195`
- `edited`: `211`
- Items with non-empty `replacement_path`: `211`
- Items marked `replacement_target == true`: `2,401`
- Missing non-empty replacement files: `0`
- Missing `source_download_path` files: `0`
- Missing `source_preview_path` files: `0`

## Category Summary

| Category | Count | Edited | Candidate found | Replacement target | Has replacement |
| --- | ---: | ---: | ---: | ---: | ---: |
| `alchemy_tiles` | 192 | 8 | 184 | 192 | 8 |
| `common_hud_tiles` | 256 | 83 | 173 | 255 | 83 |
| `image_group_battle_command_buttons` | 5 | 5 | 0 | 5 | 5 |
| `image_group_battle_popups_panels` | 2 | 2 | 0 | 2 | 2 |
| `image_group_field_menu_labels` | 4 | 4 | 0 | 4 | 4 |
| `image_group_title_screen` | 6 | 4 | 2 | 4 | 4 |
| `page_turn_rle_05_tiles` | 128 | 34 | 94 | 128 | 34 |
| `page_turn_rle_06_tiles` | 300 | 10 | 290 | 300 | 10 |
| `page_turn_rle_07_tiles` | 300 | 10 | 290 | 300 | 10 |
| `page_turn_rle_08_tiles` | 300 | 10 | 290 | 300 | 10 |
| `page_turn_rle_09_tiles` | 300 | 10 | 290 | 300 | 10 |
| `page_turn_rle_10_tiles` | 300 | 10 | 290 | 300 | 10 |
| `page_turn_rle_11_tiles` | 300 | 10 | 290 | 300 | 10 |
| `registry_b_zp01_resources` | 13 | 11 | 2 | 11 | 11 |

## Active Path Families

Non-empty replacement files currently live under:

- `confirmed_data/localization_workbench/uploaded_image_replacements`: `203`
- `confirmed_data/image_inventory/edit_packs`: `8`

Source download paths currently live under:

- `confirmed_data/image_inventory/edit_packs/page_turn_power_animation`: `1,928`
- `confirmed_data/image_inventory/edit_packs/common_hud_tiles_00534874`: `256`
- `confirmed_data/image_inventory/edit_packs/alchemy_tiles_003A206C`: `192`
- `confirmed_data/image_inventory/edit_packs/registry_b_zp01_resources`: `13`
- `confirmed_data/image_inventory/edit_packs/battle_command_buttons`: `5`
- `confirmed_data/image_inventory/runtime_tile_matches/timeline_with_rle`: `4`
- `confirmed_data/image_inventory/runtime_tile_matches/curated_neighborhoods`: `2`
- `confirmed_data/image_inventory/runtime_tile_matches/no_entry8_ss2`: `1`
- `confirmed_data/image_inventory/runtime_tile_matches/no_entry8_ss1`: `1`
- `confirmed_data/image_inventory/runtime_rle_screen_order/timeline_with_rle`: `1`
- `confirmed_data/image_inventory/runtime_rle_screen_order/no_entry8_latest_ss1`: `1`
- `confirmed_data/image_inventory/runtime_rle_screen_order/current_review_ss2`: `1`
- `confirmed_data/image_inventory/runtime_rle_patch_previews/single_rle_layouts`: `1`

## Review Units

| Review unit | Status | Localize? | Priority | Workspace |
| --- | --- | --- | --- | --- |
| `title_logo_wordmark` | `runtime_case_registered` | yes | high | `workspaces/01_title_logo_wordmark` |
| `title_screen_static_menu_wordmarks` | `runtime_case_registered` | yes | high | `workspaces/02_title_screen_static_menu_wordmarks` |
| `event_or_cutscene_text_cards` | `pending_review` | no | high | `workspaces/03_event_or_cutscene_text_cards` |
| `dialogue_window_frame_art` | `review_started` | no | medium | `workspaces/04_dialogue_window_frame_art` |
| `portrait_headshot_assets` | `review_started` | no | medium | `workspaces/05_portrait_headshot_assets` |
| `ui_panel_label_art` | `pending_review` | no | medium | `workspaces/06_ui_panel_label_art` |
| `ui_icon_badge_wordmarks` | `pending_review` | no | low | `workspaces/07_ui_icon_badge_wordmarks` |
| `battle_result_or_reward_banners` | `pending_review` | no | medium | `workspaces/08_battle_result_or_reward_banners` |

## Role Rules

- `replacement_path` with `progress_status == edited`: final or current
  replacement asset. Keep until the image apply path is replaced and verified.
- `source_download_path`: current editable or reference source shown to the user.
  Keep until every active item has a smaller source manifest and missing-file
  check passes.
- `source_preview_path`: generated display/reference preview. It may be
  reducible later, but only after the source path and replacement path are
  preserved.
- `runtime_*` paths: runtime evidence or screen-order reconstruction. These are
  not automatically editable source, but they can be the only trace explaining
  how a source was identified.
- broad extraction folders such as `rle_tile_extraction` and
  `global_tile_extraction`: do not prune until scripts that use them as defaults
  have narrower inputs.

## Cleanup Gate

Before deleting or untracking any image-side subtree:

1. Generate an item-level manifest from `image_replacements.json`.
2. Verify all non-empty `replacement_path`, `source_download_path`, and
   `source_preview_path` files exist.
3. Preserve replacement assets under `uploaded_image_replacements/` or a
   deliberate final-source location.
4. Separate runtime evidence from ROM-backed editable sources.
5. Summarize any review-unit lesson before removing workspace evidence.

## Next Step

Turn this draft into a small machine-readable manifest that records item ID,
category, status, replacement path, source path, source role, and keep reason.
