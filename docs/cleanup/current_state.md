# Current Cleanup State

Date: 2026-06-02 KST

## Repo Snapshot

- Workspace: `/Users/user/test`
- Branch: `codex/bootstrap-toolkit`
- Git status at start of cleanup pass: clean
- Latest commit at start: `4256e71` (`이미지 워크벤치 추출 및 적용 안정화`)
- Tracked files: `31,006`
- Ignored-but-present files: `3,714`

## Tracked File Distribution

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
- `analysis/generated_workbenches/inline_event_text_test`: `1,781` tracked files
- `analysis/generated_workbenches/current_review_entry8_retranslated`: `1,441` tracked files

## External Path References

Text search found `545` hits for absolute or temporary paths such as:

- `/Users/user/test`
- `/private/tmp`
- `/Users/user/Downloads`
- temporary screenshot folders

Many are documentation links or provenance fields in JSON manifests. Before final
release, active scripts and manifests should use repo-relative paths where possible.
Historical docs can keep absolute paths only when clearly marked as historical notes.

