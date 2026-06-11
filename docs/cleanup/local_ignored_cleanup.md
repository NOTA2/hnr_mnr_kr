# Local Ignored Cleanup

Date: 2026-06-02 KST

This started as a non-destructive preview of ignored local files. The first
low-risk cleanup batch has now been executed.

## Executed Batch 1

Deleted local cache files only:

- `.DS_Store`: `32 -> 0`
- `__pycache__/`: `6 -> 0`

Git-tracked deleted files after the cleanup: `0`

## Executed Batch 2

Date: 2026-06-11 KST

Deleted regenerated macOS folder metadata only:

- `.DS_Store`
- `releases/.DS_Store`
- `patched_roms/current_review/.DS_Store`
- `local_roms/english_patched/.DS_Store`

Safety checks:

- All four paths were ignored by `.gitignore`.
- None of the four paths were tracked by git.
- Local `.DS_Store` files after the cleanup: `0`
- Local `__pycache__` directories after the cleanup: `0`
- Git-tracked deleted files after the cleanup: `0`

## Executed Batch 3

Date: 2026-06-12 KST

Deleted empty local-only directories:

- `startup_profiles/`
- `generated-images/apply-ready/`

Safety checks:

- Neither directory had git-tracked files.
- `generated-images/` itself remains because one tracked PNG under
  `generated-images/debug_tiles_003A206C/` is still referenced by image edit-pack
  manifests.
- No ROM, save, patch, source script, source asset, or active manifest was
  removed by this local-only batch.

## Ignored File Count

Ignored-but-present paths before batch 1: `3,605`

Top-level distribution:

- `analysis`: `2,629`
- `third_party`: `542`
- `.vendor`: `180`
- `scripts`: `110`
- `confirmed_data`: `84`
- `patched_roms`: `29`
- `local_roms`: `10`
- `gba_kor_tool`: `8`
- `.idea`: `7`
- `generated-images`: `2`
- root original ROM/SAV: `2`
- `.DS_Store`: `1`

Also present:

- `.DS_Store` files: `32`
- `__pycache__` directories: `6`

## Do Not Blanket-Clean

Do not run `git clean -fdX` across the repo. It would try to remove local-only
but important files such as:

- source ROM and save files
- `local_roms/`
- `patched_roms/`
- `.vendor/`
- third-party runtime/build folders
- generated workbenches that may still be useful during active QA

## Low-Risk Cleanup Candidates

These are good first deletion candidates, but still require an explicit deletion
batch:

- `.DS_Store`
- `__pycache__/`
- old `confirmed_data/runtime_debug/` contents if not part of current QA
- stale `generated-images/` scratch outputs

## Higher-Risk Cleanup Candidates

These need evidence review before deletion:

- ignored `analysis/generated_workbenches/.../hangul_*.pgm`
- local patched ROMs and savestates; see `local_rom_audit.md`
- local original/English ROM copies
- third-party emulator/runtime build folders

## 2026-06-11 Keep Decisions

After the post-release cleanup batches, these ignored local paths remain by
design:

- `analysis/generated_workbenches/translation_consistency/`: keep during active
  text QA. It is a generated report from
  `scripts/audit_translation_consistency_variants.py`, but the detailed variant
  list is directly useful while checking awkward or inconsistent translations.
- `confirmed_data/runtime_debug/`: keep until runtime/Entry8 QA is closed. It is
  small and contains current/Japanese/no-segment comparison captures that explain
  past runtime failures.
- `.vendor/`, `third_party/mgba-python-build-x86/`, and `third_party/pymgba-mcp/`:
  keep as local tooling/runtime support. Do not track or delete during active QA.
- `.idea/`: keep ignored as local IDE state.
- root source ROM/SAV, `local_roms/`, and `patched_roms/current_review/`: keep
  ignored for current gameplay QA and rebuild flow; see `local_rom_audit.md`.

## Rule

Clean ignored files by targeted path, never with a blanket repo-wide clean.
