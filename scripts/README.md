# Scripts

This directory currently keeps workflow scripts in one flat namespace. Do not
move scripts yet: the GUI server, documentation, and operator muscle memory still
refer to many `scripts/<name>.py` paths directly.

For the cleanup/restructure effort, treat this file as the transition index.

Current transition audit:

- [script_transition_audit.md](/Users/user/test/docs/structure/script_transition_audit.md)

## Group Directories

The future group directories now exist as placeholders:

- `scripts/build/`
- `scripts/audit/`
- `scripts/text/`
- `scripts/image/`
- `scripts/font/`
- `scripts/runtime/`
- `scripts/workbench/`

They intentionally contain only README files for now. Current command paths stay
at `scripts/<name>.py` and `scripts/<name>.sh`.

Each group README now records the scripts assigned to that future group, the
paths that are still active public entry points, and the holds that must be
cleared before any file move.

## Proposed Groups

### Build / Rebuild

- `build_localization_review_rom.py`
- `build_localization_workbench_dataset.py`
- `rebuild_localization_workbench_all_in_one.py`
- `build_translation_workspace.py`
- `build_master_text_workspace.py`
- `build_extraction_audit_status.py`
- `build_translation_readiness_report.py`
- `build_workset_coverage_audit.py`
- `build_workset_metadata_index.py`
- `build_translation_normalization_profile.py`
- `create_bps_patch.py`

### Text / Translation

- `build_entry8_cluster_worksets.py`
- `build_entry8_dialogue_run_worksets.py`
- `build_entry8_full_retranslation_batches.py`
- `build_entry8_retranslation_review_payload.py`
- `build_registry_d_dialogue_workset.py`
- `expand_translation_worksets_full.py`
- `import_translation_agent_results.py`
- `sync_workbench_to_sources.py`
- `fix_gameplay_terms_korean.py`

### Audit

- `audit_gui_workflow_integrity.py`
- `audit_current_review_text_coverage.py`
- `audit_ability_text_layout_candidates.py`
- `audit_entry8_missing_prefixed_records.py`
- `audit_entry8_repoint_safety.py`
- `audit_entry8_retranslation_batches.py`
- `audit_gameplay_term_particle_style.py`
- `audit_rom_text_extraction_gaps.py`
- `audit_text_layout_metadata_candidates.py`
- `audit_translation_consistency_variants.py`
- `audit_translation_expansion_opportunities.py`
- `audit_translation_normalization_regressions.py`
- `audit_workbench_source_consistency.py`

### Font / Glyph

- `build_font_charset_report.py`
- `build_workbench_from_active_atlas.py`
- `build_finalist_startup_tests.py`
- `build_startup_intro_from_atlas.sh`
- `build_startup_intro_test.sh`
- `build_core_ui_test_roms.sh`
- `build_intro_full_test.sh`
- `build_intro_full_compact_test.sh`
- `build_translated_rom_with_active_atlas.sh`
- `rebuild_active_workbenches_from_atlas.sh`
- `import_hangul_syllable_atlas.py`
- `render_galmuri7_hud_text_preview.py`
- `extract_battle_hud_name_table.py`
- `apply_english_battle_hud_font.py`
- `apply_common_hud_korean_slot_patch.py`
- `apply_battle_hud_name_font.py`

### Image / Tile

- `build_image_extraction_pipeline.py`
- `build_image_text_inventory.py`
- `build_battle_command_button_edit_pack.py`
- `build_card_book_right_tabs_edit_pack.py`
- `build_card_list_labels_edit_pack.py`
- `build_card_list_power_labels_edit_pack.py`
- `build_card_page_count_edit_pack.py`
- `build_field_menu_label_edit_pack.py`
- `build_title_screen_edit_pack.py`
- `build_graphics_extraction_progress.py`
- `build_actual_localization_tilemap_targets.py`
- `build_image_candidate_gallery.py`
- `build_rle_contact_sheets.py`
- `build_tile_contact_sheets.py`
- `build_rle_layout_variant_sheets.py`
- `build_readable_rle_layouts.py`
- `build_runtime_rle_patch_previews.py`
- `build_runtime_rle_screen_order_workspaces.py`
- `build_runtime_tile_sheets.py`
- `extract_global_image_tiles.py`
- `extract_image_review_candidates.py`
- `extract_rle_image_tiles.py`
- `extract_english_expanded_lz77_graphics.py`
- `extract_runtime_tilemap_localization_targets.py`
- `compare_english_patch_lz77_graphics.py`
- `compare_english_patch_rle_graphics.py`
- `match_runtime_tiles_to_rom_blocks.py`
- `link_image_review_previews.py`
- `register_runtime_visual_case.py`
- `apply_image_replacements.py`

### Runtime / Emulator

- `pymgba_runtime_probe.py`
- `run_mgba_runtime_probe.sh`
- `extract_mgba_savestate_visual_state.py`
- `render_runtime_tilemaps.py`
- `render_all_runtime_tilemaps.py`
- `analyze_runtime_tilemap_sources.py`
- `tune_runtime_rle_alignment.py`

### Layout / Dialogue Runtime

- `build_text_box_family_manifest.py`
- `build_text_layout_assignment_index.py`
- `build_text_taxonomy_manifest.py`
- `build_runtime_candidate_groups.py`
- `build_runtime_dialogue_family_report.py`
- `build_runtime_dialogue_subprofiles.py`
- `build_runtime_family_focus_report.py`
- `build_runtime_pageflow_focus.py`
- `build_runtime_resolution_gates.py`
- `build_dialogue_speaker_probe.py`
- `build_dialogue_state_cluster_summary.py`
- `build_dialogue_state_index.py`
- `build_dialogue_state_runs.py`

### Workbench UI

- `run_localization_workbench.py`
- `run_glyph_editor.py`

### One-Off Analysis / Archive Candidates

- `analyze_entry8_english_operand_relocation.py`
- `analyze_entry8_opening_pagination.py`
- `analyze_entry8_repoint_candidates.py`
- `analyze_entry8_vm_structure.py`
- `build_entry8_kss_spacing_candidates.py`
- `build_entry8_missing_context_units.py`
- `build_entry8_no_space_slack_candidates.py`
- `build_entry8_segment_capability_map.py`
- `build_entry8_structural_repoint_sets.py`
- `build_expanded_nearby_image_candidates.py`
- `apply_entry8_retranslation_pass.py`
- `apply_entry8_suspect_retranslation_v2.py`
- `registry_b_zp.py`

## Migration Rule

When scripts are eventually grouped, keep old top-level entry points as wrappers
until all docs, GUI subprocess calls, and regular commands have moved to the new
paths.

Do not move or archive scripts until the hard active entry points and subprocess
dependencies listed in `docs/structure/script_transition_audit.md` have wrappers
or updated call sites.
