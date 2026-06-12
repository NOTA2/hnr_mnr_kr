# Local Runtime Artifacts Matrix

Date: 2026-06-12 KST

This matrix records the ignored local ROM/save/savestate/report files that still
exist after the local ROM cleanup batches. These files are not tracked by Git.

## Current Local GBA Set

Local `.gba` files now present: `5`

| Path | Decision | Why |
| --- | --- | --- |
| `Hagane no Renkinjutsushi - Meisou no Rondo (Japan).gba` | `KEEP LOCAL` | Clean source ROM. Required for patch verification and rebuilds. |
| `patched_roms/current_review/hnr_localization_review.gba` | `KEEP LOCAL` | Current QA/release review ROM. |
| `patched_roms/current_review/current_review_font_ready.gba` | `KEEP WITH ACTIVE TOOL REFS` | Used by `apply_image_replacements.py`, `audit_translation_expansion_opportunities.py`, and GUI workflow audit. |
| `patched_roms/current_review/current_review_text_fast_translated.gba` | `KEEP WITH ACTIVE TOOL REFS` | Latest fast text-output ROM and referenced by review ROM build/audit flow. |
| `local_roms/english_patched/Fullmetal Alchemist Stray Rondo (English Patched v0.02).gba` | `KEEP WITH ACTIVE TOOL REFS` | English HUD/image comparison source for image/font scripts and workbench evidence. |

## Save And Savestate Set

Keep for now:

- `Hagane no Renkinjutsushi - Meisou no Rondo (Japan).sav`
- `hnr_localization_review.sav`
- `patched_roms/current_review/hnr_localization_review.sav`
- `patched_roms/current_review/hnr_localization_review.ss1`
- `patched_roms/current_review/hnr_localization_review.ss2`
- `patched_roms/current_review/hnr_localization_review.ss3`
- `patched_roms/current_review/hnr_localization_review.ss4`
- `patched_roms/current_review/hnr_localization_review.ss5`
- `patched_roms/current_review/hnr_localization_review.ss8`
- English reference save/savestates under `local_roms/english_patched/`

Reason:

- These files are small.
- Several image inventory manifests and runtime captures reference `ss1` through
  `ss5` and `ss8` as provenance.
- Save files can still help reproduce late-stage QA reports.

## Current Review Reports

Keep locally while the review ROM can still be rebuilt or compared:

- `current_review_apply_report.json`
- `current_review_text_fast_apply_report.json`
- `current_review_translations.json`
- font/glyph/layout report JSON files under `patched_roms/current_review/`

These reports are ignored local build outputs. They should not be committed, but
they are useful while active QA continues.

## 2026-06-12 Local Cleanup

Removed local ignored files after exact-reference checks found no hits:

- `patched_roms/current_review/hnr_localization_review.sa2` (`0` bytes)
- `patched_roms/current_review/hnr_localization_review-0.png` (`28,622` bytes)

Safety checks:

- Both files were ignored by `.gitignore`.
- Neither file was tracked by Git.
- Direct reference search across docs, scripts, confirmed data, tools, package
  code, and analysis files found no hits.

## Next Rule

Do not delete the remaining `.gba`, `.sav`, `.ss*`, current-review report, or
English reference files during active QA. Revisit this matrix only after:

1. gameplay QA is closed or a new patch baseline is created;
2. active scripts no longer reference `current_review_font_ready.gba`,
   `current_review_text_fast_translated.gba`, or the English patched ROM;
3. image inventory runtime/savestate provenance is either summarized or no
   longer needed.
