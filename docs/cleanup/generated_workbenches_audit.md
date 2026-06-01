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
