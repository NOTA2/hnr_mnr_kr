# Cleanup Execution Plan

Date: 2026-06-02 KST

The project is still active, so cleanup must be reversible, evidence-driven, and
split into small commits. The current pass is documentation and dependency
tracing only.

## Phase 0: Safety Baseline

Status: started

- Record current branch, git status, file counts, ignored local files, and size
  hotspots.
- Do not delete or move tracked files.
- Do not rewrite active scripts before dependency tracing.
- Keep Codex session logs outside the repo; use them only as read-only
  retrospective evidence.

## Phase 1: Active Dependency Map

Status: started

- Trace active GUI data:
  - `confirmed_data/localization_workbench/workbench_dataset.json`
  - `confirmed_data/localization_workbench/image_replacements.json`
- Trace active build/apply scripts under `scripts/`.
- Trace edit-pack manifests referenced by active GUI data.
- Separate final source assets from previews, contact sheets, runtime captures,
  and generated debug reports.

Exit condition:

- Every deletion candidate has a reason and an active-reference check result.

## Phase 2: No-Delete Portability Fixes

Status: started

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

## Phase 3: Structure Migration Without Breakage

Status: started

- Maintain `docs/structure/` as the migration control point.
- Keep old public paths working while introducing grouped structure.
- Start with navigation and compatibility wrappers before moving active scripts.
- Split data roles before renaming any major data directory.

Exit condition:

- A new session can identify active source-of-truth data, generated artifacts,
  local-only files, and archive candidates without opening large JSON files.

## Phase 4: Evidence Digest Before Deletion

Status: pending

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

## Phase 5: Conservative Cleanup Batches

Status: pending

Batch order should be smallest-risk first.

1. Remove duplicate scaled previews that are regenerable from 1x sources.
2. Remove obsolete contact sheets and debug-only reports not referenced by active
   GUI data.
3. Untrack or remove generated `analysis/` workbenches that are reproducible and
   already summarized.
4. Prune unreferenced broad extraction outputs under `confirmed_data/image_inventory/`.
5. Review oversized active JSON files for generated fields that can be rebuilt.

Exit condition:

- After each batch, active reference tracing has zero missing paths.
- Current build or review ROM generation still works.

## Phase 6: GBA Localization Starter Kit

Status: pending

The starter kit should be created only after the project-specific cleanup reveals
which rules are genuinely reusable.

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
