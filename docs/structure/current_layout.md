# Current Layout

Date: 2026-06-02 KST

## Top Level

- `gba_kor_tool/`
  - Python CLI package.
  - ROM inspection, text extraction, pointer search, table handling, tile/font
    operations, and translation application live here.
- `scripts/`
  - Project workflow scripts.
  - This currently mixes build, audit, extraction, image, font, runtime, GUI,
    and one-off analysis scripts in one flat directory.
- `tools/`
  - Browser-based local workbench HTML files.
- `confirmed_data/`
  - Intended source-of-truth project data.
  - Contains extracted text, translation worksets, font assets, image inventory,
    text layout metadata, dialogue metadata, and workbench cache/state.
- `analysis/`
  - Exploration, generated workbenches, reverse-engineering evidence, and old
    experiment reports.
  - Already ignored by `.gitignore`, but many files are still tracked.
- `docs/`
  - Active handoff docs, workflow docs, translation team docs, cleanup docs,
    retrospective docs, and now structure docs.
- `third_party/`
  - Font atlases, free font assets, and local third-party runtime experiments.
- `patched_roms/`, `local_roms/`
  - Local-only ignored ROM outputs/inputs.
- `generated-images/`
  - Local generated image scratch area.

## Main Friction Points

- `scripts/` is too flat.
  - Script names are descriptive, but workflow ownership is hard to scan.
- `analysis/` is both historical evidence and generated bulk.
  - This makes cleanup risky because some files explain hard-won lessons.
- `confirmed_data/image_inventory/` contains active edit packs, runtime evidence,
  previews, contact sheets, and broad extraction outputs together.
- Active docs contain many absolute `/Users/user/test/...` links.
- Active GUI JSON references ignored uploaded image replacements.
- Root `README.md` still reads like an early generic CLI toolkit intro, not the
  current late-stage localization project map.

## Current Safe Boundary

Until the migration map is executed, these paths are treated as stable public
interfaces:

- `confirmed_data/`
- `analysis/`
- `scripts/`
- `tools/`
- `gba_kor_tool/`
- `patched_roms/current_review/hnr_localization_review.gba`
- root source ROM path, local-only and ignored

