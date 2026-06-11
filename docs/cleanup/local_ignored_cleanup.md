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

## Rule

Clean ignored files by targeted path, never with a blanket repo-wide clean.
