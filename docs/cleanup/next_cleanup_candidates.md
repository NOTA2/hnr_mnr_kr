# Next Cleanup Candidates

Date: 2026-06-12 KST

This document prevents the remaining cleanup from becoming ad hoc. It ranks the
next areas by safety, value, and dependency risk.

## Current Progress Baseline

- Overall request: about `55%`
- Project cleanup / structure: about `80%`
- Retrospective: about `38%`
- Starter-kit extraction: about `23%`

These percentages are intentionally conservative. The repo is much cleaner and
the structure/retrospective safety rails are stronger, but large active-data
areas still need QA-aware handling.

## Candidate 1: Documentation Index Polish

Classification: `KEEP / STRUCTURE`

Action:

- Keep improving navigation docs so future sessions can start from compact
  indexes instead of opening large JSON files or guessing from folder names.

Why this is safe:

- It changes only Markdown.
- It reduces future deletion risk by making active sources easier to find.

Exit gate:

- `docs/reference_map.md`, `docs/cleanup/README.md`, and
  `docs/structure/README.md` point to the current cleanup, retrospective, and
  starter-kit docs.

## Candidate 2: Script Grouping Without Moving Scripts

Classification: `KEEP WITH CAUTION / STRUCTURE`

Action:

- Expand `scripts/README.md` as the transition index.
- Identify scripts that are active entry points, active helpers, one-off
  historical analysis, or archive candidates.
- Do not move active scripts yet.

Current artifact:

- `docs/structure/script_transition_audit.md`
- `docs/structure/script_move_readiness.md`
- `scripts/{build,audit,text,image,font,runtime,workbench,layout,archive}/README.md`
- `docs/structure/data_role_inventory.md`
- `docs/cleanup/analysis_retention_matrix.md`

Why this is next:

- Project structure is still flat and hard to scan.
- Moving scripts during active QA can break GUI subprocess calls and documented
  commands, so the safe first move is classification.

Exit gate:

- Active GUI/server script calls are traced.
- Old top-level script paths can be kept as wrappers if grouping begins later.
- Each future script group has active/move-hold notes before any actual move.

## Candidate 3: Confirmed Image Inventory Reduction

Classification: `KEEP WITH CAUTION`

Action:

- Build a minimal final image-source manifest from active GUI state and image
  apply reports.
- Summarize the lessons from `workspaces` before any untracking or deletion.
- Promote any non-regenerable source assets before pruning generated previews.

Why this is high value:

- `confirmed_data/image_inventory` is the largest tracked cleanup target at
  about `237M` and `15,420` tracked files after the first workspace prune.
- `docs/structure/data_role_inventory.md` now separates this area from canonical
  text/font/layout data so image cleanup can be scoped independently.
- `confirmed_data/image_inventory/image_source_manifest.md` records the current
  GUI image replacement baseline and path existence checks.
- `confirmed_data/image_inventory/image_source_manifest.json` records all
  `2,406` GUI image items with source/replacement roles and missing-path checks.
- `docs/cleanup/image_inventory_prune_plan.md` records protected path families
  and deletion gates.
- `docs/cleanup/image_workspace_prune_readiness.md` records why the remaining
  workspace units are on hold after the first safe prune.

Why this is not immediately safe:

- `rle_tile_extraction` and `global_tile_extraction` are still script defaults.
- Remaining `workspaces` units hold review evidence that may matter for image QA
  and retrospective extraction. `07_ui_icon_badge_wordmarks` is already reduced
  to a summary README and should be used as the model for future per-unit
  pruning.
- No further workspace subtree should be pruned during active QA without a
  per-unit summary and a fresh GUI workflow audit.

Exit gate:

- The minimal manifest proves which image assets are final source inputs,
  generated previews, runtime evidence, and historical/debug artifacts.
- `python3 scripts/audit_gui_workflow_integrity.py` passes after any image
  manifest or path move.
- `python3 scripts/build_image_source_manifest.py` reports `missing paths: 0`.

## Candidate 4: Remaining Ignored Local Paths

Classification: `KEEP LOCAL / DO NOT TRACK`

Action:

- Keep the current 11 ignored path families unless QA closes or the user asks for
  a local machine cleanup.
- Use `local_runtime_artifacts_matrix.md` for the current ROM/save/savestate and
  current-review report decisions.

Why this is safe:

- They are ignored and documented.
- ROMs, saves, emulator tooling, and QA outputs should not enter Git.

Exit gate:

- QA no longer needs the review ROM/save set, or a replacement artifact policy
  is written.

## Candidate 5: Retrospective Consolidation

Classification: `RETROSPECTIVE KEEP`

Action:

- Merge the evidence digest and failure-mode playbook into reusable rules for
  the starter-kit agent.
- Preserve only compact examples; do not import raw session logs.
- Use `analysis_retention_matrix.md` before deleting any analysis evidence.

Why this matters:

- Some confusing failed outputs are useful only if their lesson is captured
  before cleanup.

Exit gate:

- Each major cleanup family has either a keep reason, a compact lesson, or a
  safe removal decision.

## Current Do-Not-Delete List

Do not remove or untrack these without a separate audit update:

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

## Next Recommended Step

Candidate 2 is now in progress: active scripts have been classified without
moving active GUI/build paths. The first wrapper pilot is complete for the
read-only GUI workflow audit. The next safe structure step is either another
read-only audit wrapper after checking report outputs, or continued image-source
manifest work if gameplay QA needs image cleanup first. README-only placeholders
now exist for layout/dialogue reports and archive candidates, but no scripts
should move there until outputs and retrospective value are classified. Do not
move GUI, ROM build, image apply, patch creation, font, or runtime scripts next.
For analysis cleanup, summarize the largest structure reports before deleting
raw JSON evidence.
For ignored local cleanup, no more ROM/save/savestate cleanup is recommended
during active QA; only exact-reference-checked leftovers should be removed.
