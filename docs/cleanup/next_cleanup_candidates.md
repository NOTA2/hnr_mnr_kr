# Next Cleanup Candidates

Date: 2026-06-12 KST

This document prevents the remaining cleanup from becoming ad hoc. It ranks the
next areas by safety, value, and dependency risk.

## Current Progress Baseline

- Overall request: about `45%`
- Project cleanup / structure: about `65%`
- Retrospective: about `30%`
- Starter-kit extraction: about `20%`

These percentages are intentionally conservative. The repo is much cleaner, but
large active-data areas still need QA-aware handling.

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

Why this is next:

- Project structure is still flat and hard to scan.
- Moving scripts during active QA can break GUI subprocess calls and documented
  commands, so the safe first move is classification.

Exit gate:

- Active GUI/server script calls are traced.
- Old top-level script paths can be kept as wrappers if grouping begins later.

## Candidate 3: Confirmed Image Inventory Reduction

Classification: `KEEP WITH CAUTION`

Action:

- Build a minimal final image-source manifest from active GUI state and image
  apply reports.
- Summarize the lessons from `workspaces` before any untracking or deletion.
- Promote any non-regenerable source assets before pruning generated previews.

Why this is high value:

- `confirmed_data/image_inventory` is the largest tracked cleanup target at
  about `239M` and `15,781` tracked files.

Why this is not immediately safe:

- `rle_tile_extraction` and `global_tile_extraction` are still script defaults.
- `workspaces` holds review evidence that may matter for remaining image QA and
  retrospective extraction.

Exit gate:

- The minimal manifest proves which image assets are final source inputs,
  generated previews, runtime evidence, and historical/debug artifacts.

## Candidate 4: Remaining Ignored Local Paths

Classification: `KEEP LOCAL / DO NOT TRACK`

Action:

- Keep the current 11 ignored path families unless QA closes or the user asks for
  a local machine cleanup.

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

Do Candidate 2 next: classify active scripts more sharply without moving them.
That improves structure while keeping the active gameplay QA path stable.
