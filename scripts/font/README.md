# Font Scripts

Future home for font atlas, glyph workbench, charset, startup intro, and HUD font
helpers.

Current implementations still live in `scripts/` top level. Move them here only
after compatibility wrappers are in place.

## Current Top-Level Scripts

Atlas and glyph workbench:

- `scripts/build_font_charset_report.py`
- `scripts/build_workbench_from_active_atlas.py`
- `scripts/import_hangul_syllable_atlas.py`
- `scripts/rebuild_active_workbenches_from_atlas.sh`
- `scripts/render_galmuri7_hud_text_preview.py`

Startup / intro test ROMs:

- `scripts/build_finalist_startup_tests.py`
- `scripts/build_startup_intro_from_atlas.sh`
- `scripts/build_startup_intro_test.sh`
- `scripts/build_core_ui_test_roms.sh`
- `scripts/build_intro_full_test.sh`
- `scripts/build_intro_full_compact_test.sh`
- `scripts/build_translated_rom_with_active_atlas.sh`

HUD font helpers that still matter:

- `scripts/extract_battle_hud_name_table.py`
- `scripts/apply_english_battle_hud_font.py`
- `scripts/apply_common_hud_korean_slot_patch.py`
- `scripts/apply_battle_hud_name_font.py`

Archived font trials:

- `scripts/archive/font_trials/2026-05-17_pre_finalist_bitmap/`

## Move Holds

- `build_localization_review_rom.py` calls the HUD font apply scripts by
  top-level path.
- `run_localization_workbench.py` calls `extract_battle_hud_name_table.py` by
  top-level path.
- `docs/active_task.md` documents startup/font build commands by top-level path.

## Future Migration Shape

Keep top-level wrappers for atlas build commands and HUD post-patch helpers.
Archive only failed font trials whose lessons are already summarized in
retrospective docs.
