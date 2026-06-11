# Current Layout

Date: 2026-06-02 KST

Updated checkpoint: 2026-06-11 KST

## Top Level

- `gba_kor_tool/`
  - Python CLI package.
  - ROM inspection, text extraction, pointer search, table handling, tile/font
    operations, and translation application live here.
- `scripts/`
  - Project workflow scripts.
  - Current executable paths still live mostly in the top-level `scripts/`
    namespace because docs, GUI subprocess calls, and operator habit all refer
    to `scripts/<name>.py` / `scripts/<name>.sh`.
  - Placeholder group directories now exist for the future migration:
    `build/`, `audit/`, `text/`, `image/`, `font/`, `runtime/`, and
    `workbench/`. See `scripts/README.md`.
- `tools/`
  - Browser-based local workbench HTML files.
- `confirmed_data/`
  - Intended source-of-truth project data.
  - Contains extracted text, translation worksets, font assets, image inventory,
    text layout metadata, dialogue metadata, and workbench cache/state.
- `analysis/`
  - Exploration, generated workbenches, reverse-engineering evidence, and old
    experiment reports.
  - Already ignored by `.gitignore`, but selected active/referenced outputs are
    tracked deliberately.
  - After the 2026-06-11 cleanup pass this is about `27M`; the generated
    workbench area is about `6.4M`.
  - `analysis/generated_workbenches/current_review/` now contains only the
    `1,000` PGM files referenced by its current manifest, plus active reports.
  - Historical/test generated workbench folders were deleted locally after their
    summary was preserved in `docs/retrospective/evidence_digest.md`.
- `docs/`
  - Active handoff docs, workflow docs, translation team docs, cleanup docs,
    retrospective docs, and now structure docs.
- `third_party/`
  - Font atlases, free font assets, and local third-party runtime experiments.
- `releases/`
  - Versioned patch/release bundles. `*.bps` is ignored globally except under
    `releases/**/*.bps`.
- `patched_roms/`, `local_roms/`
  - Local-only ignored ROM outputs/inputs.

## Main Friction Points

- `scripts/` is too flat.
  - Script names are descriptive, but workflow ownership is hard to scan.
  - Do not move scripts during active QA; wrappers and doc updates should come
    first.
- `analysis/` is both historical evidence and generated bulk.
  - This makes cleanup risky because some files explain hard-won lessons.
  - The biggest generated workbench bulk has now been reduced, but broad
    reverse-engineering evidence still needs cautious review.
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
- `analysis/generated_workbenches/current_review/`
- `analysis/generated_workbenches/hud_galmuri7_8x8/`
- `analysis/generated_workbenches/translation_consistency/` while text QA is
  active
- `scripts/`
- `tools/`
- `gba_kor_tool/`
- `releases/hnr_mnr_ko_v0.1.0/`
- `patched_roms/current_review/hnr_localization_review.gba`
- root source ROM path, local-only and ignored
