# Workbench Scripts

Future home for local GUI servers, import/sync helpers, and browser-facing
workflow glue.

Current implementations still live in `scripts/` top level. Move them here only
after compatibility wrappers are in place.

## Current Top-Level Scripts

GUI entry points:

- `scripts/run_localization_workbench.py`
- `scripts/run_glyph_editor.py`

Workbench glue:

- `scripts/rebuild_localization_workbench_all_in_one.py`
- `scripts/build_localization_workbench_dataset.py`
- `scripts/sync_workbench_to_sources.py`
- `scripts/import_translation_agent_results.py`

Cross-group scripts called by the GUI:

- `scripts/extract_battle_hud_name_table.py`
- `scripts/apply_image_replacements.py`
- `scripts/build_localization_review_rom.py`

## Move Holds

- The workbench server is the main operator surface. Do not move its entry point
  until active docs and any local launch habits are updated.
- GUI subprocess calls should be converted to wrapper-aware helpers before
  target scripts are relocated.

## Future Migration Shape

This group should eventually contain the GUI server, import/sync orchestration,
and browser-facing glue. Domain-heavy implementations can live in their own
groups only after the workbench calls wrappers or module entry points.
