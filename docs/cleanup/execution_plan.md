# Cleanup Execution Plan

Date: 2026-06-02 KST

Updated checkpoint: 2026-06-12 KST

The project is still active, so cleanup must be reversible, evidence-driven, and
split into small commits. The current pass is documentation and dependency
tracing only.

## 2026-06-12 Progress Estimate

This estimate covers the user's full request: project cleanup/structure,
retrospective synthesis, and a reusable GBA localization starter-kit agent.

- Overall request: about `45%`
- Project cleanup / structure track: about `65%`
- Retrospective track: about `30%`
- Starter-kit agent track: about `20%`

Why the overall percentage is lower than the cleanup percentage:

- The safest cleanup batches are mostly done.
- The repo is much cleaner than before, but image-inventory pruning and script
  migration are intentionally deferred while QA is active.
- Retrospective synthesis now includes an evidence digest and a failure-mode
  playbook, but it still needs final consolidation after QA closes.
- The starter-kit has an initial project-neutral agent spec, but not yet a full
  template/skill package.

Current order of operations:

1. Keep active QA stable and do not move public script/data paths yet.
2. Finish cleanup documentation and only do small, evidence-backed cleanup
   batches.
3. Expand retrospective notes into reusable failure-mode and decision-pattern
   docs.
4. Extract those patterns into a project-neutral GBA localization starter-kit
   agent.

## Phase 0: Safety Baseline

Status: complete for current cleanup pass

- Record current branch, git status, file counts, ignored local files, and size
  hotspots.
- Do not delete or move tracked files.
- Do not rewrite active scripts before dependency tracing.
- Keep Codex session logs outside the repo; use them only as read-only
  retrospective evidence.
- Before any deletion, untracking batch, or large structure change, run
  `safety_gate.md`.
- Classify every candidate with `retention_policy.md` before changing it.

Completed:

- Safety and retention docs are in place.
- `.gba`, `.sav`, savestate, and patch tracking checks are part of every cleanup
  batch.
- Cleanup is being saved through small commits and pushed checkpoints.

## Phase 1: Active Dependency Map

Status: mostly complete for the areas touched so far

- Trace active GUI data:
  - `confirmed_data/localization_workbench/workbench_dataset.json`
  - `confirmed_data/localization_workbench/image_replacements.json`
- Trace active build/apply scripts under `scripts/`.
- Trace edit-pack manifests referenced by active GUI data.
- Separate final source assets from previews, contact sheets, runtime captures,
  and generated debug reports.

Exit condition:

- Every deletion candidate has a reason and an active-reference check result.

Current note:

- Generated workbench, local ROM, ignored cache/tooling, release bundle, and
  small active referenced assets have explicit keep/delete/track decisions.
- `confirmed_data/image_inventory/` remains high risk and is not pruned yet.

## Phase 2: No-Delete Portability Fixes

Status: partially complete

These are low-risk because they should only remove machine-specific assumptions.

- Replace active `/Users/user/test/...` script paths with repo-root-derived paths.
- Add small font fallback behavior where debug labels currently use fixed macOS
  system fonts.
- Convert generated active docs from absolute repo links to repo-relative links
  when the target file layout is stable.
- Keep active uploaded image replacements visible to Git instead of silently
  ignoring them.

Completed so far:

- Active `scripts/` no longer contain `/Users/user/test` references outside
  archived scripts.
- Translation workspace README generation now uses repo-relative links.
- `uploaded_image_replacements/` is no longer ignored.

Exit condition:

- Current build/workbench scripts still run, but no active workflow depends on a
  specific user home path.

Current note:

- Active generated workbench reports were normalized to repo-relative paths.
- Broader historical docs still contain absolute paths when they serve as
  provenance. That is acceptable until final documentation polish.

## Phase 3: Structure Migration Without Breakage

Status: started, intentionally conservative

- Maintain `docs/structure/` as the migration control point.
- Keep old public paths working while introducing grouped structure.
- Start with navigation and compatibility wrappers before moving active scripts.
- Split data roles before renaming any major data directory.

Exit condition:

- A new session can identify active source-of-truth data, generated artifacts,
  local-only files, and archive candidates without opening large JSON files.

Current note:

- `scripts/` group folders exist as placeholders, but active scripts remain at
  their original paths to avoid breaking documented commands and GUI subprocess
  calls.
- Current/target layout docs and group README files explain this transitional
  state, including active entry points and move holds.

## Phase 4: Evidence Digest Before Deletion

Status: started

- Expand `docs/retrospective/evidence_digest.md` from local session logs and
  project evidence.
- For each large cleanup family, write the lesson before removing bulk files.
- Keep representative samples only when they explain a recurring failure mode.

Families to digest:

- `analysis/generated_workbenches/`
- `analysis/archive/font_trials/`
- broad image extraction folders
- runtime captures and savestate comparison folders
- failed image replacement reports and no-op tests

Exit condition:

- Each deletion batch has a matching retrospective note.

Current note:

- `docs/retrospective/evidence_digest.md` preserves key generated-workbench and
  cleanup lessons.
- This still needs to be expanded into a direct "failure modes / prevention
  playbook" before starter-kit extraction.

## Phase 5: Conservative Cleanup Batches

Status: in progress

Batch order should be smallest-risk first.

1. Remove duplicate scaled previews that are regenerable from 1x sources.
2. Remove obsolete contact sheets and debug-only reports not referenced by active
   GUI data.
3. Untrack or remove generated `analysis/` workbenches that are reproducible and
   already summarized.
4. Prune unreferenced broad extraction outputs under `confirmed_data/image_inventory/`.
5. Review oversized active JSON files for generated fields that can be rebuilt.

Current image-inventory note:

- Do not prune `confirmed_data/image_inventory/` yet. See
  `image_inventory_audit.md`; active GUI references are not the only dependency
  because image scripts still use broad extraction reports.
- Remaining cleanup candidates and their exit gates are ranked in
  `next_cleanup_candidates.md`.

Completed so far:

- Untracked `3,847` generated PGM files from historical/test workbenches under
  `analysis/generated_workbenches/`, with all local files verified present after
  the index cleanup.
- No files under `confirmed_data/image_inventory/` were removed or untracked.
- Pruned stale `current_review` generated-workbench PGM accumulation down to the
  `1,000` files referenced by the active manifest.
- Deleted local-only historical/test generated workbench folders after their
  retrospective summary was preserved.
- Pruned local ROM backup/intermediate files while preserving source/current
  review/English reference ROMs and active saves.
- Promoted small active referenced assets hidden by broad ignore rules.
- Recorded explicit keep decisions for remaining ignored QA/tooling paths.
- Removed legacy top-level Node package files after verifying no active script or
  documented command uses them.

Exit condition:

- After each batch, active reference tracing has zero missing paths.
- Current build or review ROM generation still works.

## Phase 6: GBA Localization Starter Kit

Status: started, with project-neutral draft defined

The starter kit should be expanded only after the project-specific cleanup
reveals which rules are genuinely reusable.

Current artifact:

- `docs/starter_kit/gba_localization_agent.md`

Reusable agent capabilities:

- Repo bootstrap and `.gitignore` policy for ROMs, saves, temporary outputs, and
  generated workbenches.
- Text extraction audit loop with coverage gates.
- Font/glyph workflow with palette, codepoint table, capacity, and layout checks.
- Image replacement workflow that distinguishes runtime evidence from ROM-backed
  edit sources.
- QA loop for emulator screenshots, user savestates, and regression checks.
- Retrospective memory that records repeated failure modes without importing
  raw chat logs into the repo.

Exit condition:

- A project-neutral starter-kit prompt/skill exists and contains no dependency on
  this repo, local ROM paths, or Codex session logs.
