# Local ROM Audit

Date: 2026-06-02 KST

This audit covers local `.gba` files. These files are ignored by Git and are not
tracked in the repo.

## Git Ignore Status

`.gba` files are already ignored:

- `.gitignore:1`: `*.gba`
- `.gitignore:9`: `local_roms/`
- `.gitignore:10`: `patched_roms/*`
- `.gitignore:11`: `!patched_roms/.gitkeep`
- `.gitignore:28`: `analysis/`

Tracked `.gba` files: `0`

Tracked `patched_roms/` entries: only `patched_roms/.gitkeep`

## Current Local Inventory

Local `.gba` files found: `16`

Keep locally:

- `Hagane no Renkinjutsushi - Meisou no Rondo (Japan).gba`
- `patched_roms/current_review/hnr_localization_review.gba`

Keep with caution:

- `local_roms/english_patched/Fullmetal Alchemist Stray Rondo (English Patched v0.02).gba`
- `patched_roms/current_review/current_review_font_ready.gba`

Reason: these are not the user's current play/QA ROMs, but active scripts or
reports still reference them as English-patch comparison/source inputs or pointer
scan/base ROMs. Delete only after those script defaults are changed or the
English/comparison tasks are closed.

Local delete candidates after one more confirmation:

- `analysis/tmp_lz77_tile_test/hnr_lz77_tile_test_changed.gba`
- `patched_roms/current_review/backups/hnr_localization_review_before_field_label_archive_repoint.gba`
- `patched_roms/current_review/backups/hnr_localization_review_before_image_capacity_fix.gba`
- `patched_roms/current_review/current_review_font_expand_base.gba`
- `patched_roms/current_review/current_review_translated.gba`
- `patched_roms/current_review/hnr_localization_review.before_card_page_source_fix.gba`
- `patched_roms/current_review/hnr_localization_review.before_common_hud_korean_slots.gba`

Retrospective delete candidates:

- `patched_roms/current_review/hnr_localization_review.before_battle_hud_name_font.gba`
- `patched_roms/current_review/hnr_localization_review.before_bw_invert_battle_hud_name_font.gba`
- `patched_roms/current_review/hnr_localization_review.before_no_shadow_battle_hud_name_font.gba`
- `patched_roms/current_review/hnr_localization_review.before_safe_battle_hud_name_font.gba`
- `patched_roms/current_review/hnr_localization_review_no_entry8_segment_repoint.gba`

Reason: these are referenced by reports or runtime debug JSON, so the lesson or
diagnostic value should be summarized before deletion. They are still local-only
and ignored by Git.

## Direct Reference Check

Reference check searched file names in:

- `README.md`
- `docs/`
- `confirmed_data/`
- `scripts/`
- `tools/`
- `gba_kor_tool/`
- `analysis/`

Results:

- root original ROM: `76` direct name hits.
- current review ROM: `510` direct name hits.
- English patched ROM: `25` direct name hits.
- `current_review_font_ready.gba`: `4` direct name hits.
- four battle HUD rollback/backup ROMs: `1` direct name hit each.
- `hnr_localization_review_no_entry8_segment_repoint.gba`: `4` direct name hits
  in runtime debug JSON.
- all other listed delete candidates: `0` direct name hits.

## Deletion Rule

Do not delete local ROMs through broad cleanup commands.

If local ROM cleanup is executed, delete only a named batch after:

1. re-running the direct reference check;
2. confirming the root original and `hnr_localization_review.gba` remain;
3. preserving any retrospective lesson in Markdown;
4. checking `git status --short --branch` before and after.

## Post-QA Update: 2026-06-11

After first-pass QA and release packaging, local `.gba` inventory changed.

Important findings:

- `patched_roms/current_review/hnr_localization_review.gba` is the verified
  v0.1.0 release target.
- Root `hnr_localization_review.gba` exists locally but matches the clean source
  ROM SHA256. It is not the release target.
- `patched_roms/current_review/current_review_text_fast_translated.gba` is a new
  local candidate that needs direct reference checks before deletion.

Do not run a ROM deletion batch until the release baseline is committed.

## Local Delete Batch 1: Executed

Date: 2026-06-11 KST

The v0.1.0 release baseline has been committed and pushed. Batch 1 should remove
only local ignored `.gba` files that are not active review targets and are not
used by active script defaults.

Keep:

- `Hagane no Renkinjutsushi - Meisou no Rondo (Japan).gba`
- `patched_roms/current_review/hnr_localization_review.gba`
- `local_roms/english_patched/Fullmetal Alchemist Stray Rondo (English Patched v0.02).gba`
- `patched_roms/current_review/current_review_font_ready.gba`
- `patched_roms/current_review/current_review_text_fast_translated.gba`

Keep all `.sav` files in this batch. Save files are small and may still help QA
reproduction.

Delete candidates for batch 1:

- `hnr_localization_review.gba`
- `analysis/tmp_lz77_tile_test/hnr_lz77_tile_test_changed.gba`
- `patched_roms/current_review/backups/hnr_localization_review_before_field_label_archive_repoint.gba`
- `patched_roms/current_review/backups/hnr_localization_review_before_image_capacity_fix.gba`
- `patched_roms/current_review/current_review_font_expand_base.gba`
- `patched_roms/current_review/current_review_translated.gba`
- `patched_roms/current_review/hnr_localization_review.before_card_page_source_fix.gba`
- `patched_roms/current_review/hnr_localization_review.before_common_hud_korean_slots.gba`

Reasons:

- root `hnr_localization_review.gba` has the same SHA256 as the clean source ROM
  and is therefore a misleading duplicate, not the release target.
- `analysis/tmp_lz77_tile_test/hnr_lz77_tile_test_changed.gba` is an ignored
  temporary LZ77 tile test output.
- the remaining files are older local review backups or intermediate translated
  ROMs with no active script-default role.

Pre-delete checks:

- Git-tracked `.gba` / `.sav` files: `0`
- working tree before doc update: clean
- active release target SHA256 preserved in
  `post_qa_release_snapshot.md`

Post-delete verification:

- Keep files missing after delete: `0`
- Deleted target files still present: `0`
- Git-tracked deleted files: `0`
- Approximate local bytes removed: `69,667,668`
- `.sav` files removed: `0`

Remaining local `.gba` files after batch 1:

- `Hagane no Renkinjutsushi - Meisou no Rondo (Japan).gba`
- `local_roms/english_patched/Fullmetal Alchemist Stray Rondo (English Patched v0.02).gba`
- `patched_roms/current_review/current_review_font_ready.gba`
- `patched_roms/current_review/current_review_text_fast_translated.gba`
- `patched_roms/current_review/hnr_localization_review.before_battle_hud_name_font.gba`
- `patched_roms/current_review/hnr_localization_review.before_bw_invert_battle_hud_name_font.gba`
- `patched_roms/current_review/hnr_localization_review.before_no_shadow_battle_hud_name_font.gba`
- `patched_roms/current_review/hnr_localization_review.before_safe_battle_hud_name_font.gba`
- `patched_roms/current_review/hnr_localization_review.gba`
- `patched_roms/current_review/hnr_localization_review_no_entry8_segment_repoint.gba`

Next ROM cleanup pass:

- Keep the source ROM and current review ROM.
- Keep English patched ROM and `current_review_font_ready.gba` while active
  scripts reference them.
- Review battle-HUD rollback ROMs and `no_entry8_segment_repoint` only after
  their retrospective/debug references are summarized or retired.
- Review `.sav` files separately; they are small and may be useful for QA
  reproduction.
