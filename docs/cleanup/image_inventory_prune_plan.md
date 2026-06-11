# Image Inventory Prune Plan

Date: 2026-06-12 KST

This plan uses `confirmed_data/image_inventory/image_source_manifest.json` to
separate active GUI image paths from large image-side evidence folders.

No files are removed by this document.

## Current Baseline

- `confirmed_data/image_inventory/`: about `239M`
- tracked files under image inventory: `15,781+`
- item-level GUI image manifest records: `2,406`
- item-level missing paths: `0`
- GUI workflow integrity audit: passing

## Protected Active Path Families

These are directly referenced by current GUI image replacement state as source,
preview, or replacement paths.

| Family | Manifest records | Decision |
| --- | ---: | --- |
| `edit_packs/page_turn_power_animation` | 1,928 | Keep. Active page-turn RLE tile source family. |
| `edit_packs/common_hud_tiles_00534874` | 256 | Keep. Active shared HUD tile source family. |
| `edit_packs/alchemy_tiles_003A206C` | 192 | Keep. Active alchemy/card UI tile family and direct patch asset location. |
| `edit_packs/registry_b_zp01_resources` | 13 | Keep. Active Registry B image resource family. |
| `edit_packs/battle_command_buttons` | 5 | Keep. Active battle command button source family. |
| `runtime_tile_matches/*` | 8 | Keep. Runtime-derived source previews used by active GUI items. |
| `runtime_rle_screen_order/*` | 3 | Keep. Runtime screen-order evidence used by active GUI items. |
| `runtime_rle_patch_previews/single_rle_layouts` | 1 | Keep. Runtime patch preview used by active GUI item. |
| `localization_workbench/uploaded_image_replacements` | 203 replacements | Keep. Current replacement assets. |

## Keep With Caution

These are not all direct source families in the item-level manifest, but they
are still referenced by scripts, target lists, reports, or retrospective notes.

| Family | Why not prune yet |
| --- | --- |
| `edit_packs/title_screen` | `build_localization_workbench_dataset.py` still documents title-screen edit-pack paths; target lists also reference title screen edit paths. |
| `edit_packs/field_menu_labels` | Historical/source edit-pack for field labels; active GUI now points at runtime match previews, but the source pack explains lineage. |
| `edit_packs/card_book_right_tabs` | Referenced by current review extraction docs and target lists. |
| `edit_packs/card_list_labels` | Referenced in image restore/apply reports and card UI audit evidence. |
| `edit_packs/card_list_power_labels` | Manifest-rich candidate family; needs lesson summary before pruning. |
| `edit_packs/card_page_count` | Active direct patch manifest feeds `alchemy_tiles_003A206C` direct patch entry. |
| `edit_packs/party_menu_names_trace` | Runtime/OAM reconstruction evidence for party menu naming; useful retrospective material. |
| `edit_packs/party_menu_ss4_ss5` | User-supplied savestate UI evidence; needs summary before pruning. |
| `edit_packs/user_supplied_ss4_ss5_only*` | User-supplied capture crops; preserve until their role is summarized. |
| `workspaces/` | Largest folder, but holds review-unit evidence and contact sheets. Needs summary first. |
| `global_tile_extraction/` | Broad extraction output; scripts and reports still use it as discovery context. |
| `rle_tile_extraction/` | Broad RLE extraction output; image scripts still use default reports under this tree. |

## Later Prune Candidates

These are plausible candidates only after the keep-with-caution gates are met.

- Generated contact sheets whose source manifest and regeneration command are
  known.
- Preview scale variants when the 1x source, tile map, and replacement path are
  preserved.
- Superseded user-supplied crop folders after a compact lesson and active target
  decision are written.
- Broad extraction outputs after scripts stop using their default reports.

## Required Gates Before Any Image Deletion

1. Run `python3 scripts/build_image_source_manifest.py`.
2. Confirm `missing paths: 0`.
3. Run `python3 scripts/audit_gui_workflow_integrity.py`.
4. Read any tracked `README.md` or `*.md` inside the target subtree.
5. Search references to the exact subtree from `README.md`, `docs/`,
   `scripts/`, `confirmed_data/`, `tools/`, and `gba_kor_tool/`.
6. Write or update a retrospective note if the subtree explains a failed image
   approach.
7. Delete or untrack only one small family per commit.

## Next Practical Step

The non-deleting `workspaces/` summary now lives in
`image_workspaces_summary.md`. The next practical step is to decide whether the
lowest-priority review unit can be summarized further and pruned one unit at a
time.
