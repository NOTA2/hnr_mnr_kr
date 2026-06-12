# Structure Migration Map

Date: 2026-06-02 KST

This map turns the current repo into the target layout without breaking the
active late-stage QA workflow.

## Phase A: Navigation Layer

Status: completed

- Add structure docs.
- Add script index.
- Update reference map and README so new sessions know where cleanup and
  restructuring live.
- No file moves.

Exit condition:

- A new session can understand the current/target layout without opening large
  JSON or generated folders.

## Phase B: Path Portability

Status: started

- Remove `/Users/user/test` from active scripts.
- Keep script command names stable while internals become repo-root based.
- Decide how to handle ignored uploaded image replacements.
- Add helper constants/config only when it reduces repeated hard-coded paths.

Completed so far:

- `scripts/build_startup_intro_from_atlas.sh` now derives `ROOT` instead of
  embedding `/Users/user/test`.
- `scripts/build_translation_workspace.py` now generates repo-relative README
  links.
- `confirmed_data/localization_workbench/uploaded_image_replacements/` is no
  longer ignored because active replacement state references files there.

Exit condition:

- Active commands still run from repo root, and no active command requires a
  specific home directory.

## Phase C: Script Grouping Without Breaking Calls

Status: started

Use compatibility wrappers before moving real implementations.

Example:

```text
scripts/build_localization_review_rom.py
scripts/build/build_localization_review_rom.py
```

The old top-level path can remain as a tiny wrapper until docs, GUI calls, and
muscle memory move to the grouped path.

Proposed groups:

- `scripts/build/`: ROM/workbench generation.
- `scripts/audit/`: coverage, safety, consistency, readiness checks.
- `scripts/text/`: extraction, workset, Entry8/Registry D text operations.
- `scripts/image/`: image extraction, edit-pack generation, image replacement.
- `scripts/font/`: font atlas, glyph, charset, HUD font operations.
- `scripts/runtime/`: emulator/savestate/tilemap runtime capture tooling.
- `scripts/workbench/`: local GUI server and sync/import helpers.
- `scripts/layout/`: text-box layout, dialogue metadata, and runtime dialogue
  family reports.
- `scripts/archive/`: one-off historical scripts.

Completed so far:

- Added group placeholder directories with README files.
- Kept all current top-level script entry points in place.
- Added `script_move_readiness.md` so future script moves start with a
  wrapper-first readiness decision instead of a broad rename.
- Completed the first wrapper pilot by moving the
  `audit_gui_workflow_integrity.py` implementation into `scripts/audit/` while
  keeping the old top-level command path as a compatibility wrapper.
- Added README-only `scripts/layout/` and `scripts/archive/` placeholders so
  layout/dialogue report scripts and one-off historical scripts have explicit
  future homes before any moves.
- Kept GUI, build, font, image, text, and runtime groups blocked or on hold
  during active QA.

Exit condition:

- Existing commands still work.
- New grouped commands are documented.
- GUI server subprocess calls are updated only after wrappers exist.

## Phase D: Data Layout Split

Status: pending

Do not rename `confirmed_data/` directly during active QA. Instead split roles
inside it first:

- source-of-truth text and worksets
- active image edit sources
- active workbench cache/state
- generated reports
- runtime evidence
- historical broad extraction output

Only after this split is stable should a later branch consider a `data/` rename.

Exit condition:

- Active build/apply flow can say exactly which data folders are required.
- Generated or historical folders have clear archive/delete decisions.

## Phase E: Analysis Cleanup

Status: pending

- Keep summary Markdown and small structured reports that explain decisions.
- Move or remove reproducible generated workbenches.
- Keep representative failed cases only when they teach a recurring failure mode.
- Untrack generated bulk only after `docs/retrospective/evidence_digest.md` is
  expanded enough to preserve the lesson.

Exit condition:

- `analysis/` no longer dominates the tracked repo.
- The project still has enough evidence to explain major decisions.

## Phase F: Starter Kit Extraction

Status: pending

- Extract workflows, schemas, templates, and agent rules.
- Remove this game's data, ROM names, path assumptions, and session-log details.
- Keep the lessons as general failure-mode checklists.

Exit condition:

- A new GBA project can start from the kit without inheriting this repo's clutter.
