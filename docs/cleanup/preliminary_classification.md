# Preliminary File Classification

This is a first-pass classification only. It is intentionally conservative because
the project is still active.

## KEEP

- `gba_kor_tool/`
- `scripts/*.py` and `scripts/*.sh` that build, apply, audit, or run the current
  localization workflow
- `tools/localization_workbench.html`
- `tools/glyph_editor.html`
- `confirmed_data/localization_workbench/workbench_dataset.json`
- `confirmed_data/localization_workbench/image_replacements.json`
- `confirmed_data/localization_workbench/progress_state.json`
- `confirmed_data/localization_workbench/speaker_*.json`
- `confirmed_data/extracted_texts/`
- `confirmed_data/translation_workspace/` current manifests, audits, and active
  translation batches
- `confirmed_data/translation_worksets/`
- `confirmed_data/font_assets/active_hangul_font_profile.json`
- `confirmed_data/font_assets/translation_normalization_profile.json`
- `third_party/font_atlases/`
- `third_party/gba_free_fonts/`
- `README.md`, `.gitignore`, `package.json`, `package-lock.json`

## KEEP WITH CAUTION

- `confirmed_data/image_inventory/edit_packs/`
  - Contains active image edit packs, including title, field labels, card UI,
    battle command buttons, and page-turn power animation work.
  - Needs dependency tracing from `workbench_dataset.json` and
    `image_replacements.json` before pruning.
- `confirmed_data/image_inventory/localization_targets/`
  - Likely useful as the curated target list.
- `confirmed_data/image_inventory/gui_display_previews/`
  - May be GUI-facing; trace before removing.
- `analysis/entry8_*.json` and `analysis/entry8_*.md`
  - Large but useful for explaining Entry8 structure, capacity, and repointing.
- `analysis/experiment_log.md`
  - Strong retrospective value.

## ARCHIVE CANDIDATE

- `analysis/generated_workbenches/`
  - Many generated PGM workbench files. Likely reproducible from scripts and
    manifests, but useful for understanding font and encoding attempts.
- `analysis/archive/font_trials/`
  - Historical by name. Good retrospective material, not likely needed for final
    runtime.
- `confirmed_data/image_inventory/global_tile_extraction/`
  - Broad extraction results. Useful as historical discovery output.
- `confirmed_data/image_inventory/rle_tile_extraction/`
  - Broad extraction results. Useful as historical discovery output.
- `confirmed_data/image_inventory/workspaces/`
  - Early category workspaces. Need to check whether final GUI still references them.
- `confirmed_data/image_inventory/runtime_tilemaps*/`
  - Runtime-derived evidence. Useful for debugging, risky as active edit source.
- `confirmed_data/image_inventory/runtime_tile_matches*/`
  - Runtime matching evidence. Useful for retrospective and targeted debugging.
- `confirmed_data/image_inventory/runtime_user_captures*/`
  - Savestate-derived runtime evidence. Should not be treated as direct edit source.
- `confirmed_data/image_inventory/savestate_compare_labels/`
  - QA/comparison material rather than final patch input.

## DELETE CANDIDATE AFTER EVIDENCE DIGEST

These should not be removed until the lesson they represent is written down:

- Duplicate preview scale files such as `_4x`, `_6x`, `_8x` when a 1x source and
  manifest can regenerate them.
- Large contact sheets if they are not referenced by active GUI data.
- Failed no-op/repoint test reports that duplicate a final successful report.
- Obsolete runtime probes under `pymgba_runtime_probe_*` if not referenced.
- Intermediate generated workbench glyph images that can be regenerated.

## DO NOT TRACK / LOCAL ONLY

These are already ignored or should remain local-only:

- Original ROMs and patched ROMs
- Save files and savestates
- `.vendor/`
- `.idea/`
- `__pycache__/`
- `.DS_Store`
- uploaded image replacement inbox files
- temporary import reports and agent inbox files

## Next Checks Before Any Deletion

Completed:

- Built a first-pass path reference list from `workbench_dataset.json`.
- Built a first-pass path reference list from `image_replacements.json`.
- Compared direct active GUI references against tracked
  `confirmed_data/image_inventory` files.

Remaining:

1. Trace active script imports and command-line defaults.
2. Trace manifest references inside active `edit_packs`.
3. Mark unreferenced generated previews as candidates, not deletions.
4. Summarize lessons from candidates before removing them.
