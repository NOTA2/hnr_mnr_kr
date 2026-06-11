# Generated Workbenches Audit

Date: 2026-06-02 KST

This audit covers `analysis/generated_workbenches/`.

## Current Shape

- Tracked files under `analysis/generated_workbenches/`: `13,625`
- Approximate disk size: `66M`
- Most tracked files are generated glyph PGM files.

Tracked file distribution by folder:

- `current_review`: `9,529`
- `inline_event_text_test`: `1,781`
- `current_review_entry8_retranslated`: `1,441`
- `current_review_entry8_two_only`: `640`
- `core_ui_active`: `85`
- `intro_full_active`: `78`
- `intro_full_compact_active`: `70`
- root README: `1`

## Active References

Do not remove `analysis/generated_workbenches/current_review` as a whole:

- `scripts/build_entry8_no_space_slack_candidates.py`
- `scripts/build_entry8_kss_spacing_candidates.py`
- `scripts/audit_translation_expansion_opportunities.py`
- `scripts/analyze_entry8_repoint_candidates.py`

These scripts refer to `analysis/generated_workbenches/current_review/prepared.tbl`.

Also keep small active workbenches until the font workflow is fully rechecked:

- `core_ui_active`
- `intro_full_active`
- `intro_full_compact_active`

## Batch 1 Plan

Status: executed.

Untracked generated PGM glyph files from historical/test workbenches only. Kept
local files on disk, and keep their non-PGM reports/manifests tracked.

Planned untrack-only targets:

- `analysis/generated_workbenches/inline_event_text_test/*.pgm`: `1,776`
- `analysis/generated_workbenches/current_review_entry8_retranslated/*.pgm`: `1,436`
- `analysis/generated_workbenches/current_review_entry8_two_only/*.pgm`: `635`

Total planned untracked generated PGM files: `3,847`

This was an index cleanup, not a local deletion. Because `analysis/` is ignored,
the files remain available on this machine but stop bloating the tracked repo.

Verification:

- Staged removed-from-index files: `3,847`
- Tracked files under `analysis/generated_workbenches/` after untracking: `9,778`
- Sample local PGM file still exists after untracking: yes

## Batch 2 Plan

Status: executed.

Untrack the remaining tracked metadata files from the same historical/test
workbenches:

- `analysis/generated_workbenches/inline_event_text_test/`
- `analysis/generated_workbenches/current_review_entry8_retranslated/`
- `analysis/generated_workbenches/current_review_entry8_two_only/`

Target files:

- `import_report.json`
- `prepared.tbl`
- `prepared_manifest.json`
- `seed_manifest.json`
- `workbench_report.json`

Total target files: `15`
Total target bytes: `2,058,647`

Safety checks before selection:

- Target subtree Markdown read: only `analysis/generated_workbenches/README.md`.
- Active GUI JSON references: `0`.
- Direct references outside cleanup docs: none to these workbench directories.
- Script references: no active script reads these three directories.
- Retrospective summary: preserved in `docs/retrospective/evidence_digest.md`.

Decision: `UNTRACK`, not local delete.

Reason:

- These files are generated workbench outputs, not source-of-truth inputs.
- The important lesson is the workflow shape and source/provenance issue, not the
  full generated tables.
- Local files should remain for now because at least one historical input path
  was under `/private/tmp`, so exact regeneration is not guaranteed without more
  archaeology.

Verification:

- Staged removed-from-index files in batch 2: `15`
- Local files still present after `git rm --cached`: `15 / 15`
- Tracked files under `analysis/generated_workbenches/` after batch 2: `9,763`
- Tracked files left in the three historical/test workbench folders: `0`
- ROM/savestate/patch files changed in this batch: `0`

## Batch 3 Plan

Status: executed on 2026-06-11 KST.

Deleted the ignored, local-only ability text layout audit output folder:

- `analysis/generated_workbenches/ability_texts_layout_audit/`

Deleted files:

- `ability_texts_layout_candidates.md`
- `ability_texts_layout_candidates.json`

Preserved evidence in this document:

- The audit checked `413` `ability_texts` rows.
- `198` rows had an inline `0x0B` source separator.
- High/medium/low layout candidates: `0`.
- All rows were `ok`.

Regeneration command:

```sh
python3 scripts/audit_ability_text_layout_candidates.py
```

Decision: `DELETE LOCAL OUTPUT`.

Reason:

- The folder was ignored by `.gitignore` through `analysis/`.
- The folder had no git-tracked files.
- The only active reference is the generating script's default output path.
- The useful retrospective result is the zero-candidate summary, not the
  generated JSON/Markdown files themselves.

Verification:

- Directory exists after deletion: no
- Git-tracked deleted files after deletion: `0`
- Tracked files under `analysis/generated_workbenches/` after deletion: `9,763`
- ROM/savestate/patch files changed in this batch: `0`

## Batch 4 Plan

Status: executed on 2026-06-11 KST.

Cleaned stale glyph PGM accumulation from the active
`analysis/generated_workbenches/current_review/` workbench.

Pre-cleanup shape:

- Actual PGM files in `current_review`: `15,430`
- PGM files referenced by the current `prepared_manifest.json`: `1,000`
- Referenced PGM files missing locally: `0`
- Unreferenced actual PGM files: `14,430`
- Tracked PGM files before staging: `9,517`
- Tracked referenced PGM files before staging: `72`
- Tracked unreferenced PGM files before staging: `9,445`
- Untracked but referenced PGM files before staging: `928`

Executed cleanup:

- Rebuilt the `current_review` workbench from
  `patched_roms/current_review/current_review_translations.json`.
- Pruned only generated `hangul_*.pgm` and `punct_*.pgm` files that were not
  referenced by the newly written `prepared_manifest.json`.
- Kept all `1,000` manifest-referenced PGM files.
- Force-added the `928` referenced PGM files that were present locally but
  ignored by the broad `analysis/` ignore rule.
- Removed the `9,445` tracked stale PGM files that the current manifest no
  longer references.

Script hardening added:

- `scripts/build_workbench_from_active_atlas.py` now prunes unreferenced
  generated PGM files after successful manifest generation.
- `scripts/build_workbench_from_active_atlas.py` and
  `scripts/import_hangul_syllable_atlas.py` now write repo-relative report and
  manifest paths for files inside this repository.

Post-cleanup shape:

- Actual PGM files in `current_review`: `1,000`
- PGM files referenced by `prepared_manifest.json`: `1,000`
- Referenced PGM files missing locally: `0`
- Unreferenced actual PGM files: `0`
- `current_review` disk size: about `4.7M`
- `analysis/generated_workbenches` disk size: about `23M`
- `analysis` disk size: about `44M`

Decision: `DELETE STALE LOCAL/TRACKED OUTPUT; KEEP ACTIVE REFERENCED OUTPUT`.

Reason:

- The deleted PGM files were generated workbench outputs.
- They were not referenced by the current active manifest.
- The current active manifest remains self-contained in the repo by tracking all
  `1,000` referenced PGM files.
- The rebuild command is known and was run successfully.

Verification:

- Absolute `/Users/user/test` and `/private/tmp` paths in the current review
  workbench JSON/TBL reports after regeneration: `0`
- ROM/savestate/patch files changed in this batch: `0`
