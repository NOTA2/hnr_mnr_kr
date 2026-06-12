# Analysis Retention Matrix

Date: 2026-06-12 KST

This matrix classifies `analysis/` before any more pruning. The goal is to keep
retrospective value without letting generated evidence dominate the repo.

## Current Snapshot

- `analysis/`: about `27M`
- top-level analysis files: `243` files
- `analysis/generated_workbenches/`: about `6.4M`, `1,259` tracked files
- `analysis/archive/`: about `2.3M`, `468` tracked files
- `analysis/tmp_lz77_tile_test/`: local empty directory, `0` tracked files

## Retention Classes

| Area | Current role | Decision | Why |
| --- | --- | --- | --- |
| `analysis/*.md` summaries | `RETROSPECTIVE KEEP` | Keep | These are compact explanations for resource registry, font, text extraction, Entry8, and location-map decisions. |
| large `analysis/*.json` structure reports | `RETROSPECTIVE HOLD` | Keep for now | Some are oversized, but they are still the detailed evidence behind structural conclusions and failure-mode lessons. Summarize before pruning. |
| `analysis/generated_workbenches/current_review/` | `KEEP WITH CAUTION` | Keep | Current review workbench evidence remains useful for late QA and font/text rebuild diagnosis. |
| `analysis/generated_workbenches/translation_consistency/` | `RETROSPECTIVE HOLD` / `QA HOLD` | Keep | It supports translation consistency review and should not be removed while wording QA is still open. |
| `analysis/generated_workbenches/core_ui_active/` | `KEEP WITH CAUTION` | Keep | Active subset workbench for core UI font coverage. Revisit only after font workflow closes. |
| `analysis/generated_workbenches/intro_full_active/` and `intro_full_compact_active/` | `KEEP WITH CAUTION` | Keep | Startup intro font/layout evidence. Can later be reduced to reports if startup QA is closed. |
| `analysis/generated_workbenches/hud_galmuri7_8x8/` | `KEEP WITH CAUTION` | Keep | HUD mini-font subset evidence. Do not remove while HUD rendering remains a possible QA topic. |
| `analysis/archive/font_trials/` | `RETROSPECTIVE HOLD` | Keep compactly | Old font trials explain why the project moved away from earlier candidates and into bitmap-locked sources. |
| `analysis/archive/data_structure_raw/` | `RETROSPECTIVE HOLD` | Keep | Small raw evidence for resource and helper analysis. Useful when a summary needs byte-level re-checking. |
| `analysis/tmp_lz77_tile_test/` | `DELETE LOCAL OK` | Local cleanup only | Currently empty and untracked. Older local ROM audit notes mention a prior ignored GBA there, but the current directory does not affect Git cleanup. |

## Deletion Gate

Before removing any `analysis/` file or subtree:

1. Search exact filenames in `docs/`, `scripts/`, and active manifests.
2. Check whether the file explains a failure mode in
   `docs/retrospective/failure_modes.md`.
3. Preserve a compact summary in `docs/retrospective/` or a cleanup audit if the
   evidence is useful only historically.
4. Prefer pruning generated bulk by manifest comparison, not by folder name.
5. Run `python3 scripts/audit_gui_workflow_integrity.py` if any active
   workbench, font, image, or patch-related path is touched.

## Next Analysis Cleanup Candidate

The first summary extraction target is complete in
`docs/retrospective/entry8_vm_lessons.md`. The raw Entry8 JSON reports should
still stay for now, but future cleanup can use that note as the preserved lesson
before deciding whether the raw reports belong in archive, local-only storage,
or the tracked repo.
