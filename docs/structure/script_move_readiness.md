# Script Move Readiness

Date: 2026-06-12 KST

This document ranks future script grouping work without moving any script in this
checkpoint. It exists to keep late-stage QA stable while still making the
project structure easier to improve later.

## Current Rule

- Treat top-level `scripts/<name>.py` and `scripts/<name>.sh` paths as the
  public command surface.
- Do not move active GUI, build, patch, font, image, or runtime scripts until a
  top-level compatibility wrapper exists.
- A grouped implementation can be introduced only when the old command path
  still works.
- After any wrapper or call-site change, run the GUI workflow audit before
  pruning or moving more files.

## Hard Hold Entry Points

These files must stay callable at their current paths during active QA:

- `scripts/run_localization_workbench.py`
- `scripts/build_localization_review_rom.py`
- `scripts/build_localization_workbench_dataset.py`
- `scripts/rebuild_localization_workbench_all_in_one.py`
- `scripts/sync_workbench_to_sources.py`
- `scripts/import_translation_agent_results.py`
- `scripts/apply_image_replacements.py`
- `scripts/create_bps_patch.py`
- `scripts/run_glyph_editor.py`
- `scripts/build_translated_rom_with_active_atlas.sh`

## Group Readiness Table

| Future group | Readiness | Why | Before any move |
| --- | --- | --- | --- |
| `scripts/audit/` | `PILOT CANDIDATE` | Mostly read-only checks. It is the safest group for the first wrapper experiment. | Keep `scripts/audit_gui_workflow_integrity.py` as a top-level wrapper. Compile changed scripts and run the audit from the old path. |
| `scripts/build/` | `BLOCKED` | GUI and operator flows call review ROM, workbench dataset, all-in-one rebuild, and BPS patch scripts by top-level path. | Add wrappers for build entry points, update docs only after old paths pass, and run GUI audit plus a review ROM build when the QA window allows. |
| `scripts/workbench/` | `BLOCKED` | The local GUI is the active operator surface and launches helper scripts through top-level paths. | Add a shared subprocess path helper or wrappers, then verify GUI actions for text sync, image apply, ROM build, and patch creation. |
| `scripts/font/` | `BLOCKED` | Review ROM builds call atlas, startup, battle HUD, and name-table font patch scripts directly. | Preserve shell script entry points, add wrappers for HUD/font helpers, and test startup/font checks before changing documented commands. |
| `scripts/image/` | `HOLD` | Image replacement is active, and broad image inventory data is still being reduced with manifest gates. | Finish manifest-backed image cleanup gates, keep `apply_image_replacements.py` stable, and run both image manifest and GUI audits after any path change. |
| `scripts/text/` | `HOLD` | Workbench sync/import scripts are active, and Entry8/Registry D one-off lessons still feed retrospective docs. | Separate active sync/import commands from one-off historical scripts, then create wrappers before moving implementations. |
| `scripts/runtime/` | `HOLD` | Emulator, savestate, and runtime visual capture tooling may still be needed while gameplay QA is open. | Document local runtime setup such as `MGBA_BIN`, keep local paths ignored, and move only after runtime QA closes or wrappers exist. |
| `scripts/archive/` | `PENDING` | Historical one-offs may still explain repeated failure modes. | Summarize the lesson in `docs/retrospective/` before archiving or deleting. |

## First Safe Pilot

The first future implementation move should be an audit script, not a GUI or ROM
builder script. A safe pilot shape is:

```text
scripts/audit_gui_workflow_integrity.py          # stable wrapper
scripts/audit/audit_gui_workflow_integrity.py    # grouped implementation
```

Do not start with `run_localization_workbench.py`,
`build_localization_review_rom.py`, `apply_image_replacements.py`, or
`create_bps_patch.py`. Those are directly tied to the user's late-stage QA flow.

## Required Checks After Any Future Wrapper Or Move

- `python3 scripts/audit_gui_workflow_integrity.py`
- `python3 scripts/build_image_source_manifest.py`, if image paths or image
  inventory files changed
- `python3 -m py_compile <changed scripts>`
- A review ROM build when build, font, image apply, or patch creation paths are
  touched and the QA window allows it
- `git diff --name-status` review before staging

## Current Checkpoint

No script files were moved in this checkpoint. The project now has enough
classification to continue cleanup without guessing which commands are safe to
touch.
