# Current Cleanup State

Date: 2026-06-02 KST

## 2026-06-11 Post-Release Cleanup Checkpoint

- Branch: `codex/bootstrap-toolkit`
- Latest cleanup checkpoint before this note: `f57a251`
  (`로컬 ROM 정리 batch 3 기록`)
- Tracked files: `27,299`
- Ignored-but-present status lines: `5,930`
- Local `.DS_Store` files after the latest ignored cleanup: `0`
- Local `__pycache__` directories after the latest ignored cleanup: `0`
- Git-tracked deleted files after local ROM and ignored cleanup batches: `0`

Current disk hotspots:

- `.git`: about `874M` (do not touch during project cleanup)
- `confirmed_data`: about `389M`
- `analysis`: about `44M` after current review stale PGM pruning
- `analysis/generated_workbenches`: about `23M`
- `analysis/generated_workbenches/current_review`: about `4.7M`
- `patched_roms`: about `54M`, ignored except `.gitkeep`
- `local_roms`: about `16M`, ignored
- `.vendor`: about `13M`, ignored local tooling/runtime cache
- `releases`: about `860K`

The current local ROM set is intentionally reduced but not minimal. The source
ROM, current review ROM, English patched reference ROM, two rebuild helper ROMs,
and active save files are retained until QA and rebuild flows no longer need
them. See `local_rom_audit.md`.

## Repo Snapshot

- Workspace: `/Users/user/test`
- Branch: `codex/bootstrap-toolkit`
- Git status at start of cleanup pass: clean
- Latest commit at start: `4256e71` (`이미지 워크벤치 추출 및 적용 안정화`)
- Tracked files: `31,006`
- Ignored-but-present files: `3,714`

## Current After Cleanup Checkpoints

- Cleanup checkpoint before generated workbench batch 2: `ae4c4b6`
  (`정리 보존 기준 추가`)
- Tracked files after current generated workbench batch 2: `27,280`
- Tracked `analysis/generated_workbenches` files after batch 2: `9,763`
- Local `.DS_Store` files: `0`
- Local `__pycache__` directories: `0`

Current tracked top-level distribution:

- `confirmed_data`: `16,619`
- `analysis`: `10,472`
- `scripts`: `120`
- `docs`: `39`
- `third_party`: `18`
- `gba_kor_tool`: `4`
- `tools`: `2`
- other tracked top-level entries: `6`

Current top tracked extensions:

- `pgm`: `13,183`
- `png`: `9,624`
- `bin`: `3,142`
- `json`: `929`
- `md`: `223`
- `py`: `107`
- `txt`: `32`
- `tbl`: `24`

## Initial Tracked File Distribution

- `confirmed_data`: `16,508` tracked files
- `analysis`: `14,334` tracked files
- `scripts`: `112` tracked files
- `docs`: `22` tracked files
- `third_party`: `18` tracked files
- `gba_kor_tool`: `4` tracked files
- `tools`: `2` tracked files

Top tracked extensions:

- `pgm`: `17,030`
- `png`: `9,515`
- `bin`: `3,142`
- `json`: `940`
- `md`: `197`
- `py`: `107`
- `txt`: `32`
- `tbl`: `27`

## Disk Hotspots

- `confirmed_data`: about `392M`
- `patched_roms`: about `128M`, ignored except `.gitkeep`
- `analysis`: about `95M`
- `third_party`: about `59M`
- `local_roms`: about `16M`, ignored
- `.vendor`: about `14M`, ignored
- Root original ROM/SAV: present locally and ignored by `.gitignore`

## Important Safety Notes

- `*.gba`, `*.sav`, and savestate-style files are ignored and not tracked.
- `local_roms/` and `patched_roms/*` are ignored, with only `patched_roms/.gitkeep`
  tracked.
- `.vendor/`, `.idea/`, `__pycache__/`, `.DS_Store`, runtime debug folders,
  uploaded image replacements, and import inbox/report folders are ignored.
- `analysis/` is now ignored, but many historical `analysis` files are already
  tracked. These need deliberate untracking/deletion decisions, not blanket cleanup.

## Active-Looking Large Files

Do not touch these until the workbench and build flow are traced:

- `confirmed_data/localization_workbench/workbench_dataset.json` (`~26.9M`)
- `confirmed_data/localization_workbench/image_replacements.json` (`~8.4M`)
- `confirmed_data/translation_workspace/all_extracted_texts_master.json` (`~9.0M`)
- `confirmed_data/extracted_texts/registry_a_entry8_prefixed_texts.json` (`~7.2M`)
- `third_party/gba_free_fonts/*/*.fnt` and source atlas PNGs

## High-Volume Areas

- `confirmed_data/image_inventory/edit_packs`: `5,789` tracked files
- `confirmed_data/image_inventory/edit_packs/page_turn_power_animation`: `4,510` tracked files
- `confirmed_data/image_inventory/workspaces`: `2,776` tracked files
- `confirmed_data/image_inventory/rle_tile_extraction`: `2,235` tracked files
- `confirmed_data/image_inventory/global_tile_extraction`: `1,924` tracked files
- `confirmed_data/image_inventory/runtime_*`: `2,668` tracked files
- `analysis/generated_workbenches/current_review`: `9,529` tracked files
- `analysis/generated_workbenches/inline_event_text_test`: `0` tracked files
- `analysis/generated_workbenches/current_review_entry8_retranslated`: `0` tracked files
- `analysis/generated_workbenches/current_review_entry8_two_only`: `0` tracked files

## External Path References

Text search found `545` hits for absolute or temporary paths such as:

- `/Users/user/test`
- `/private/tmp`
- `/Users/user/Downloads`
- temporary screenshot folders

Many are documentation links or provenance fields in JSON manifests. Before final
release, active scripts and manifests should use repo-relative paths where possible.
Historical docs can keep absolute paths only when clearly marked as historical notes.
