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
