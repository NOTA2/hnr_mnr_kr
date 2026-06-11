# Build Scripts

Future home for ROM, workbench, workspace, and report build entry points.

Current implementations still live in `scripts/` top level. Move them here only
after compatibility wrappers are in place.

## Current Top-Level Scripts

Hard active entry points:

- `scripts/build_localization_review_rom.py`
- `scripts/build_localization_workbench_dataset.py`
- `scripts/rebuild_localization_workbench_all_in_one.py`
- `scripts/create_bps_patch.py`

Workspace and report builders:

- `scripts/build_translation_workspace.py`
- `scripts/build_master_text_workspace.py`
- `scripts/build_extraction_audit_status.py`
- `scripts/build_translation_readiness_report.py`
- `scripts/build_workset_coverage_audit.py`
- `scripts/build_workset_metadata_index.py`
- `scripts/build_translation_normalization_profile.py`

## Move Holds

- `run_localization_workbench.py` calls `build_localization_review_rom.py` by
  top-level path.
- `rebuild_localization_workbench_all_in_one.py` calls
  `sync_workbench_to_sources.py` and `build_localization_workbench_dataset.py`
  by top-level path.
- Release patch creation is exposed through the GUI and should remain stable
  until release docs and GUI calls are updated.

## Future Migration Shape

When this group is migrated, keep wrappers at the old top-level paths first.
Verify both the full review ROM build and fast text rebuild paths before
removing any compatibility wrapper.
