# GBA Korean Localization Workspace

This repository contains the late-stage Korean localization workspace for a GBA
game, plus the tools and documentation produced during the project.

The active priority is stable QA and careful cleanup. Do not treat this repo as a
fresh generic CLI sample: it now contains project data, active review workflows,
retrospective notes, and starter-kit extraction material.

## Start Here

- Session start: [docs/session_start.md](docs/session_start.md)
- Current task card: [docs/active_task.md](docs/active_task.md)
- Reference map: [docs/reference_map.md](docs/reference_map.md)
- Cleanup plan: [docs/cleanup/execution_plan.md](docs/cleanup/execution_plan.md)
- Current structure: [docs/structure/current_layout.md](docs/structure/current_layout.md)
- Data roles: [docs/structure/data_role_inventory.md](docs/structure/data_role_inventory.md)
- Script transition audit: [docs/structure/script_transition_audit.md](docs/structure/script_transition_audit.md)

For cleanup work, read [docs/cleanup/README.md](docs/cleanup/README.md) before
deleting, moving, or untracking anything.

## Current Safety Rules

- Do not commit ROMs, saves, savestates, or local emulator state.
- Do not move public `scripts/<name>.py` paths during active QA without wrappers.
- Do not prune `confirmed_data/image_inventory/` until the image source manifest
  is expanded and active references are verified.
- Do not copy raw Codex session logs into the repo. Summarize lessons in
  `docs/retrospective/` instead.
- Cleanup happens in small, pushed checkpoints.

## Main Areas

- `gba_kor_tool/`: Python CLI helpers for ROM inspection, text extraction,
  pointer search, table handling, tile/font operations, and translation apply.
- `scripts/`: active project workflow scripts. Group folders exist as transition
  indexes, but current entry points remain at top level for compatibility.
- `tools/`: local browser-based workbench HTML files.
- `confirmed_data/`: active project data, including extracted texts, worksets,
  font assets, layout metadata, workbench state, and image inventory.
- `analysis/`: selected reverse-engineering evidence and generated workbench
  outputs. Many files are historical or retrospective material.
- `docs/`: handoff, cleanup, structure, retrospective, translation, and starter
  kit documents.
- `releases/`: tracked patch/release bundles. Release patches are intentionally
  allowed here.
- `local_roms/` and `patched_roms/`: local-only ignored ROM inputs/outputs.

## Active Local Files

The source ROM and review ROM are local files and should remain ignored by Git.

Common local paths:

- source ROM at repo root;
- current review ROM under `patched_roms/current_review/`;
- active save files next to the ROM or review ROM.

`.gitignore` is configured so ROM/save/savestate files stay out of the repo.

## Useful Commands

Run the local workbench:

```bash
python3 scripts/run_localization_workbench.py
```

Rebuild the workbench dataset:

```bash
python3 scripts/build_localization_workbench_dataset.py
```

Build the current review ROM:

```bash
python3 scripts/build_localization_review_rom.py
```

Quick CLI help:

```bash
python3 -m gba_kor_tool --help
```

## Retrospective And Starter Kit

The retrospective and starter-kit materials are intentionally draft-stage while
gameplay QA is still active.

- Evidence digest: [docs/retrospective/evidence_digest.md](docs/retrospective/evidence_digest.md)
- Failure modes: [docs/retrospective/failure_modes.md](docs/retrospective/failure_modes.md)
- Starter-kit agent draft: [docs/starter_kit/gba_localization_agent.md](docs/starter_kit/gba_localization_agent.md)

The goal is to turn this project into reusable GBA localization guidance after
project-specific cleanup and the user's own retrospective notes are merged.
