# 2026-06-16 Cleanup / Retrospective / Starter-Kit Handoff

Date: 2026-06-16 KST
Branch: `codex/bootstrap-toolkit`
Base commit before this handoff: `e13f4e4` (`스타터킷 안전장치 규칙 보강`)

This document is for continuing the project from another computer or another
Codex session. It summarizes the user's priorities, the current safety boundary,
what has already been cleaned, and the next safe plan.

## User Priorities

The user is in late-stage gameplay QA. They are actively playing the localized
ROM and checking:

- awkward Korean translations;
- places where gameplay progression breaks;
- image/text/font issues visible in-game;
- whether the project can be finalized cleanly.

The user repeatedly emphasized:

- Project cleanup must not break the active localization workflow.
- Cleanup is not just deletion. The repo should become structured and easier to
  continue.
- Before deleting or moving anything, read relevant docs/README/Markdown files
  and verify references two or three times.
- Keep only files that are required for the current project or useful for
  retrospective/starter-kit lessons.
- Remove unnecessary analysis/generated/local leftovers only after the lesson or
  keep/delete reason is documented.
- Do not make the repo depend on files outside this repo.
- Do not refer to another repo or external local path as an active dependency.
- Commit, and usually push, small checkpoints because cleanup is risky.
- Preserve GUI workflows:
  - Korean localization item visibility;
  - text apply/sync;
  - image replacement apply;
  - review ROM build;
  - BPS patch creation.
- The retrospective matters because the next goal is a generic GBA localization
  starter-kit agent with rules, safety checks, and eventually skill material.

## Current Progress Estimate

Use separate tracks, not one misleading number:

- Overall request: about `57%`
- Project cleanup / structure: about `80%`
- Retrospective: about `40%`
- Starter-kit extraction: about `28%`

These are intentionally conservative. The repo is much cleaner, but active image
inventory, QA state, and starter-kit extraction are not finished.

## Current Safety Boundary

Do not remove, move, or untrack these without a fresh audit:

- `confirmed_data/localization_workbench/`
- `confirmed_data/translation_workspace/`
- `confirmed_data/extracted_texts/`
- `confirmed_data/font_assets/`
- `confirmed_data/image_inventory/`
- `analysis/generated_workbenches/current_review/`
- `analysis/generated_workbenches/translation_consistency/`
- `confirmed_data/runtime_debug/`
- `local_roms/`
- `patched_roms/current_review/`
- root source ROM/SAV
- `third_party/mgba-python-build-x86/`
- `third_party/pymgba-mcp/`

Important active paths:

- GUI server: `scripts/run_localization_workbench.py`
- review ROM build: `scripts/build_localization_review_rom.py`
- dataset build: `scripts/build_localization_workbench_dataset.py`
- all-in-one rebuild: `scripts/rebuild_localization_workbench_all_in_one.py`
- source sync/import:
  - `scripts/sync_workbench_to_sources.py`
  - `scripts/import_translation_agent_results.py`
- image apply: `scripts/apply_image_replacements.py`
- patch creation: `scripts/create_bps_patch.py`
- glyph editor: `scripts/run_glyph_editor.py`
- translated ROM shell path:
  `scripts/build_translated_rom_with_active_atlas.sh`

Do not move GUI, ROM build, image apply, patch creation, font, text sync/import,
or runtime scripts as the next structure step.

## Required Start Checks

Run these at the start of the next machine/session:

```bash
git status --short --branch
git log -8 --oneline
python3 scripts/audit_gui_workflow_integrity.py
python3 scripts/build_image_source_manifest.py
git ls-files '*.gba' '*.sav' '*.ss' '*.bps' ':!:releases/**/*.bps'
find . -path './.git' -prune -o -type d -name '__pycache__' -print
```

Expected as of this handoff:

- working tree should be clean;
- GUI workflow audit should print `gui workflow integrity: ok`;
- image source manifest should report `items: 2406` and `missing paths: 0`;
- tracked ROM/save/savestate/patch query should print nothing, except release
  BPS files are intentionally allowed by the exclusion;
- no `__pycache__` directories should be present.

## What Was Completed Recently

### Structure And Script Cleanup

- Added script grouping docs and placeholder directories:
  - `scripts/build/`
  - `scripts/audit/`
  - `scripts/text/`
  - `scripts/image/`
  - `scripts/font/`
  - `scripts/runtime/`
  - `scripts/workbench/`
  - `scripts/layout/`
  - `scripts/archive/`
- Added `docs/structure/script_move_readiness.md`.
- Completed one safe wrapper pilot:
  - stable command: `scripts/audit_gui_workflow_integrity.py`
  - grouped implementation: `scripts/audit/audit_gui_workflow_integrity.py`
- Other active scripts are still top-level and should remain there for now.

### Image Inventory Cleanup

- Built and validated `confirmed_data/image_inventory/image_source_manifest.json`.
- Pruned only one image workspace:
  `confirmed_data/image_inventory/workspaces/07_ui_icon_badge_wordmarks`
  now keeps only a summary README.
- The active edit pack
  `confirmed_data/image_inventory/edit_packs/common_hud_tiles_00534874`
  was protected and must stay protected.
- Added image workspace prune readiness docs. Remaining workspaces are on hold
  during active QA unless each has a per-unit summary, reference search, and GUI
  audit.

### Uploaded Replacement State

- `uploaded_image_replacements/` is tracked because active GUI JSON references
  payload files there.
- Rechecked post-QA title uploads:
  - `title_240x160_transparent.png` is no longer present on disk;
  - remaining post-QA title/workspace payloads are active JSON references.
- Existing upload manifest is stale by two active payloads:
  - `title_960x640_transparent (1).png`
  - `workspace-file (2) (1).png`
- Do not prune uploaded replacement payloads until the manifest is refreshed and
  Unicode-normalized path checks agree with active GUI state.

### Local Runtime / ROM Cleanup

- `.gba`, saves, savestates, and patches remain ignored.
- No ROM/save/savestate is tracked.
- Local ignored cleanup removed only exact-reference-checked leftovers:
  - empty `analysis/tmp_lz77_tile_test/`;
  - `patched_roms/current_review/hnr_localization_review.sa2`;
  - `patched_roms/current_review/hnr_localization_review-0.png`.
- Current local `.gba` set is documented in
  `docs/cleanup/local_runtime_artifacts_matrix.md`.
- Do not delete more local ROM/save/savestate files during active QA.

### Analysis And Retrospective

- Added `docs/cleanup/analysis_retention_matrix.md`.
- Summarized Entry8 VM structure lessons in
  `docs/retrospective/entry8_vm_lessons.md`.
- Added failure mode for pointer-looking values mistaken as segment boundaries.
- Raw large Entry8 JSON reports are still kept for now.
- Cleanup rule: summarize the lesson before deleting analysis evidence.

### Starter Kit

- Updated `docs/starter_kit/gba_localization_agent.md` with:
  - command-stream record metadata;
  - segment capability matrix;
  - uploaded replacement manifest gates;
  - local runtime artifact matrix;
  - wrapper-first script migration rules.
- This is still a document draft, not a packaged Codex skill yet.

## Most Important Docs To Read

Start here:

- `docs/reference_map.md`
- `docs/session_start.md`
- `docs/active_task.md`
- `docs/cleanup/next_cleanup_candidates.md`
- `docs/cleanup/current_state.md`
- `docs/cleanup/safety_gate.md`
- `docs/structure/script_transition_audit.md`
- `docs/structure/script_move_readiness.md`
- `docs/cleanup/image_workspace_prune_readiness.md`
- `docs/cleanup/uploaded_replacements_audit.md`
- `docs/cleanup/local_runtime_artifacts_matrix.md`
- `docs/cleanup/analysis_retention_matrix.md`
- `docs/retrospective/failure_modes.md`
- `docs/retrospective/entry8_vm_lessons.md`
- `docs/starter_kit/gba_localization_agent.md`

Avoid opening huge JSON directly unless needed. Prefer targeted queries.

## Next Safe Plan

### 1. First, Reconfirm Baseline

- Run the required start checks above.
- Confirm the branch is `codex/bootstrap-toolkit`.
- Confirm the working tree is clean before changing anything.

### 2. Keep Active QA Stable

- Do not move active GUI/build/image/font/runtime scripts.
- Do not prune uploaded replacements yet.
- Do not prune remaining image workspaces without per-unit summary and audit.
- Do not delete remaining local ROM/save/savestate files while gameplay QA is
  active.

### 3. Continue Image Inventory Reduction Carefully

Best next high-value area, but high risk:

- refresh or regenerate uploaded replacement manifest first;
- keep Unicode normalization in mind on macOS;
- use `scripts/build_image_source_manifest.py`;
- only prune generated previews or workspace evidence after:
  - README summary exists;
  - exact reference search passes;
  - `python3 scripts/audit_gui_workflow_integrity.py` passes;
  - `python3 scripts/build_image_source_manifest.py` reports missing paths `0`.

Do not touch:

- active edit packs;
- `confirmed_data/localization_workbench/`;
- current review ROM/report/savestate local files;
- `common_hud_tiles_00534874` active source.

### 4. Continue Retrospective Consolidation

Good next low-risk work:

- summarize another large analysis family before considering raw JSON pruning;
- fold the lesson into `docs/retrospective/failure_modes.md`;
- update `docs/starter_kit/gba_localization_agent.md` only with project-neutral
  rules.

Good candidates:

- Registry/resource directory lessons;
- image palette/tilemap/source-vs-preview lessons;
- GUI stale-state/rebuild-order lessons.

### 5. Starter-Kit Extraction

Do not jump straight to a packaged skill yet. First create reusable templates:

- `.gitignore` policy template;
- cleanup safety gate template;
- source-family capability matrix template;
- image target manifest schema;
- uploaded replacement manifest schema;
- local runtime artifact matrix template;
- agent prompt and checklist.

Only after those are stable should the starter-kit become an actual Codex skill
or plugin.

### 6. Script Structure

The only completed move is the audit wrapper pilot. If doing more script
structure work:

- choose another read-only audit script only;
- preserve the old top-level path as a wrapper;
- run audits from old and new paths;
- do not start with GUI/build/image/font/runtime scripts.

## Deletion Rules

Before deleting anything:

1. Read nearby README/docs.
2. Search exact filename/path in:
   - `docs/`
   - `scripts/`
   - `confirmed_data/`
   - `tools/`
   - `gba_kor_tool/`
   - `analysis/`
3. Decide whether the file is:
   - active source;
   - generated but needed;
   - retrospective evidence;
   - local-only ignored artifact;
   - safe delete candidate.
4. Preserve the lesson if it explains a repeated mistake.
5. Run the relevant safety checks.
6. Commit a small batch.

Never use broad cleanup commands such as `git clean -fdX`.

## Commit / Push Expectations

The user asked to commit and push periodically because cleanup is risky.

Preferred pattern:

```bash
git status --short --branch
git diff --check
python3 scripts/audit_gui_workflow_integrity.py
git add <specific files>
git diff --cached --check
git commit -m "<small focused Korean message>"
git push
```

If a destructive local cleanup is needed, use only exact named paths and record
the deletion in cleanup docs.

## Current Good State Summary

As of this handoff:

- active GUI audit passes;
- image source manifest has `2406` items and `0` missing paths;
- no tracked ROM/save/savestate/patch files outside intentional release BPS;
- no `__pycache__`;
- working tree was clean before this handoff document was created;
- latest pushed work before this handoff was `e13f4e4`.

The next machine should pull `codex/bootstrap-toolkit`, read this file, run the
start checks, then continue from the "Next Safe Plan" section.
