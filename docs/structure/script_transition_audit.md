# Script Transition Audit

Date: 2026-06-12 KST

This audit classifies `scripts/` before any real restructure. It exists so
script grouping can happen later without breaking active QA or the GUI.

## Safety Boundary

- Do not move, rename, or delete active top-level scripts yet.
- Treat `scripts/<name>.py` and `scripts/<name>.sh` as public paths while QA is
  active.
- If scripts are grouped later, keep top-level wrappers until docs, GUI
  subprocess calls, and operator commands all point to the new locations.

## Current Shape

- Tracked files under `scripts/`: `131` after the first wrapper pilot and
  layout/archive placeholder READMEs.
- Top-level scripts are still the active command surface.
- `scripts/audit/` now contains the first grouped implementation:
  `audit_gui_workflow_integrity.py`.
- Other group directories remain README placeholders:
  `build`, `text`, `image`, `font`, `runtime`, `workbench`, `layout`, and
  `archive`.

## Hard Active Entry Points

These are user-facing or GUI-facing and must keep their current paths for now.

- `scripts/run_localization_workbench.py`
- `scripts/build_localization_review_rom.py`
- `scripts/build_localization_workbench_dataset.py`
- `scripts/rebuild_localization_workbench_all_in_one.py`
- `scripts/sync_workbench_to_sources.py`
- `scripts/import_translation_agent_results.py`
- `scripts/apply_image_replacements.py`
- `scripts/create_bps_patch.py`
- `scripts/run_glyph_editor.py`

Why:

- `docs/active_task.md` still documents top-level commands.
- `run_localization_workbench.py` invokes several scripts by top-level path.
- Release packaging is exposed through the GUI and release artifacts.

## GUI Subprocess Dependencies

`scripts/run_localization_workbench.py` directly invokes:

- `scripts/extract_battle_hud_name_table.py`
- `scripts/apply_image_replacements.py`
- `scripts/sync_workbench_to_sources.py`
- `scripts/build_localization_review_rom.py`
- `scripts/import_translation_agent_results.py`

Migration rule:

- Do not move these until the GUI call sites are changed or top-level wrappers
  are added.
- After any wrapper or path change, run
  `python3 scripts/audit_gui_workflow_integrity.py`.

## Review ROM Build Dependencies

`scripts/build_localization_review_rom.py` directly invokes:

- `scripts/build_translated_rom_with_active_atlas.sh`
- `scripts/apply_english_battle_hud_font.py`
- `scripts/apply_common_hud_korean_slot_patch.py`
- `scripts/apply_battle_hud_name_font.py`
- `python -m gba_kor_tool apply-translations`

Migration rule:

- Keep these paths stable until the full review ROM build and fast text rebuild
  paths are verified after any wrapper change.
- Use `scripts/audit_gui_workflow_integrity.py` as the first read-only gate
  before running heavier rebuild checks.

## Active Manual Commands

`docs/active_task.md` currently documents these commands:

- `zsh scripts/rebuild_active_workbenches_from_atlas.sh`
- `zsh scripts/build_startup_intro_test.sh`
- `python3 scripts/build_finalist_startup_tests.py`
- `zsh scripts/build_intro_full_test.sh`
- `python3 scripts/build_workbench_from_active_atlas.py`
- `zsh scripts/build_translated_rom_with_active_atlas.sh`
- `python3 scripts/build_localization_workbench_dataset.py`
- `python3 scripts/run_localization_workbench.py`

Migration rule:

- These are public operator commands until `active_task.md` and related docs are
  updated.

## Active QA / Runtime Tooling

Keep these available while live QA is active:

- `scripts/run_mgba_runtime_probe.sh`
- `scripts/pymgba_runtime_probe.py`
- `scripts/extract_mgba_savestate_visual_state.py`
- `scripts/render_runtime_tilemaps.py`
- `scripts/render_all_runtime_tilemaps.py`
- `scripts/analyze_runtime_tilemap_sources.py`
- `scripts/tune_runtime_rle_alignment.py`
- `scripts/register_runtime_visual_case.py`

Migration rule:

- Runtime scripts can move only after savestate/emulator workflows are either
  closed or wrapped.

## Image Inventory Script Holds

Do not move or archive these until `confirmed_data/image_inventory` is reduced:

- `scripts/apply_image_replacements.py`
- `scripts/compare_english_patch_rle_graphics.py`
- `scripts/build_runtime_rle_patch_previews.py`
- `scripts/match_runtime_tiles_to_rom_blocks.py`
- `scripts/build_readable_rle_layouts.py`
- `scripts/build_rle_contact_sheets.py`
- `scripts/build_rle_layout_variant_sheets.py`

Why:

- `docs/cleanup/image_inventory_audit.md` identifies these as relying on broad
  image extraction reports or related image-side evidence.

## Portability Follow-Ups

These are not blockers for the current cleanup checkpoint, but should be fixed
before turning the repo layout into a reusable template:

- `scripts/run_mgba_runtime_probe.sh` searches `$HOME/Downloads` for mGBA.
- `scripts/build_localization_review_rom.py` and
  `scripts/build_localization_workbench_dataset.py` include a
  `Path.home()/.cache/codex-runtimes/...` Pillow fallback.

Migration rule:

- Keep explicit environment-variable or argument overrides.
- Prefer documented local setup paths over hidden machine-specific defaults.

## Archive Candidate Handling

The existing `scripts/README.md` lists one-off analysis and archive candidates.
Do not delete them yet.

Before archiving or removing any script:

1. Search docs and active scripts for the exact filename.
2. Check whether it explains a retrospective failure mode.
3. If useful only historically, summarize the lesson first.
4. Commit a small batch with `git diff --name-status` review.

## Next Safe Move

The group README files now have active vs hold notes, and
`script_move_readiness.md` ranks future wrapper work. The first read-only audit
wrapper pilot is complete for `audit_gui_workflow_integrity.py`. Actual GUI,
review ROM, image apply, patch creation, font, or runtime script moves should
wait until wrappers are introduced and the relevant paths are re-tested.
