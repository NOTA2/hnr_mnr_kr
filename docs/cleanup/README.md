# Cleanup Workspace

This folder tracks the end-of-project cleanup without changing the active
localization pipeline by accident.

## Ground Rules

- Do not delete, move, or rewrite active project files during inventory.
- Treat Codex session logs outside this repo as read-only retrospective evidence.
- Do not copy raw session logs into the repo.
- Do not make the repo depend on paths outside this repo, such as `~/.codex`,
  `/private/tmp`, `/Users/user/Downloads`, or temporary screenshot folders.
- Before deleting a file that may explain a mistake, preserve the lesson in a
  retrospective document.
- Prefer staged cleanup commits over one large deletion commit.

## Classification

- `KEEP`: Required for the current build, GUI, translation, or image replacement flow.
- `KEEP WITH CAUTION`: Active or likely active, but oversized or messy enough to audit.
- `ARCHIVE CANDIDATE`: Not needed for final execution, but useful for history or diagnosis.
- `DELETE CANDIDATE`: Likely generated, duplicate, or obsolete after evidence is summarized.
- `UNKNOWN`: Needs dependency tracing before any action.

## Current Status

The inventory pass is complete and cleanup is now in targeted batches.

No active ROM, savestate, patch, source script, or image replacement payload has
been removed. Current cleanup checkpoints include:

- local ROM backup/intermediate pruning, with source/current review/English
  reference ROMs and active saves retained;
- release packaging for `releases/hnr_mnr_ko_v0.1.0/`;
- current review generated-workbench pruning from stale accumulated PGM files to
  the `1,000` manifest-referenced PGM files;
- local deletion of historical/test generated workbench folders after compact
  retrospective summaries were preserved;
- tracking of small active referenced assets that had been hidden by broad ignore
  rules, such as the HUD 8x8 PGM set and battle HUD preview PNG;
- explicit keep decisions for remaining ignored local QA/tooling paths.

See `generated_workbenches_audit.md`, `local_rom_audit.md`,
`local_ignored_cleanup.md`, and `safety_gate.md` before making or reviewing any
further cleanup batch.

## Inventory Documents

- `current_state.md`: repo size, tracked-file distribution, ignored local files,
  and high-volume areas.
- `safety_gate.md`: mandatory checks before deletion or large structure changes.
- `gui_workflow_safety.md`: read-only GUI/text/image/ROM build/release safety
  audit and latest known-good result.
- `retention_policy.md`: criteria for keep, retrospective keep, untrack, and
  delete decisions.
- `post_qa_release_snapshot.md`: file-state snapshot after first-pass QA and
  v0.1.0 patch creation.
- `top_level_audit.md`: small top-level cleanup decisions such as legacy
  package files and scratch folders.
- `execution_plan.md`: staged cleanup, retrospective, and starter-kit plan.
- `active_reference_trace.md`: references extracted from active GUI JSON files.
- `external_path_audit.md`: active vs historical absolute-path findings.
- `uploaded_replacements_audit.md`: active uploaded image replacement tracking.
- `local_ignored_cleanup.md`: non-destructive ignored-file cleanup preview.
- `local_rom_audit.md`: ignored local `.gba` inventory and cleanup candidates.
- `generated_workbenches_audit.md`: generated workbench bulk cleanup plan.
- `image_inventory_audit.md`: image inventory cleanup risk classification.
- `image_inventory_prune_plan.md`: item-level manifest-based image pruning plan.
- `next_cleanup_candidates.md`: ranked list of remaining cleanup/structure
  candidates and their exit gates.
- `preliminary_classification.md`: conservative first-pass file categories.
