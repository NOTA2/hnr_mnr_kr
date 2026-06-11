# Text Scripts

Future home for extraction, translation workset, Entry8, Registry D, and text
application helpers.

Current implementations still live in `scripts/` top level. Move them here only
after compatibility wrappers are in place.

## Current Top-Level Scripts

Translation source/workset operations:

- `scripts/build_entry8_cluster_worksets.py`
- `scripts/build_entry8_dialogue_run_worksets.py`
- `scripts/build_entry8_full_retranslation_batches.py`
- `scripts/build_entry8_retranslation_review_payload.py`
- `scripts/build_registry_d_dialogue_workset.py`
- `scripts/expand_translation_worksets_full.py`
- `scripts/import_translation_agent_results.py`
- `scripts/sync_workbench_to_sources.py`
- `scripts/fix_gameplay_terms_korean.py`

Dialogue/layout metadata:

- `scripts/build_text_box_family_manifest.py`
- `scripts/build_text_layout_assignment_index.py`
- `scripts/build_text_taxonomy_manifest.py`
- `scripts/build_runtime_candidate_groups.py`
- `scripts/build_runtime_dialogue_family_report.py`
- `scripts/build_runtime_dialogue_subprofiles.py`
- `scripts/build_runtime_family_focus_report.py`
- `scripts/build_runtime_pageflow_focus.py`
- `scripts/build_runtime_resolution_gates.py`
- `scripts/build_dialogue_speaker_probe.py`
- `scripts/build_dialogue_state_cluster_summary.py`
- `scripts/build_dialogue_state_index.py`
- `scripts/build_dialogue_state_runs.py`

One-off text analysis candidates:

- `scripts/analyze_entry8_english_operand_relocation.py`
- `scripts/analyze_entry8_opening_pagination.py`
- `scripts/analyze_entry8_repoint_candidates.py`
- `scripts/analyze_entry8_vm_structure.py`
- `scripts/build_entry8_kss_spacing_candidates.py`
- `scripts/build_entry8_missing_context_units.py`
- `scripts/build_entry8_no_space_slack_candidates.py`
- `scripts/build_entry8_segment_capability_map.py`
- `scripts/build_entry8_structural_repoint_sets.py`
- `scripts/apply_entry8_retranslation_pass.py`
- `scripts/apply_entry8_suspect_retranslation_v2.py`
- `scripts/registry_b_zp.py`

## Move Holds

- `run_localization_workbench.py` calls `sync_workbench_to_sources.py` and
  `import_translation_agent_results.py` by top-level path.
- Entry8 and Registry D scripts encode hard-won source-family knowledge. Do not
  archive them until their lessons are reflected in retrospective docs and the
  starter-kit rules.

## Future Migration Shape

Split active workset/import/sync tools from one-off analysis after QA closes.
Archived text experiments should keep a short README explaining the failure mode
or decision they supported.
