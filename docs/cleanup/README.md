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

This is an inventory-only pass. No tracked project files have been removed.

## Inventory Documents

- `current_state.md`: repo size, tracked-file distribution, ignored local files,
  and high-volume areas.
- `execution_plan.md`: staged cleanup, retrospective, and starter-kit plan.
- `active_reference_trace.md`: references extracted from active GUI JSON files.
- `external_path_audit.md`: active vs historical absolute-path findings.
- `uploaded_replacements_audit.md`: active uploaded image replacement tracking.
- `local_ignored_cleanup.md`: non-destructive ignored-file cleanup preview.
- `preliminary_classification.md`: conservative first-pass file categories.
