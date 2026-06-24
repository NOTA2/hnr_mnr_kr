# Session Start Checklist

Run this at the start of every GBA localization agent session.

## Repo State

- Confirm the current branch and whether it tracks a remote branch.
- Check `git status --short --branch`.
- Confirm there are no unexpected staged files.
- If the tree is dirty, identify whether changes are user work, generated
  outputs, or previous agent work before editing.

## Artifact Safety

- Confirm ROMs, saves, savestates, screenshots, and local emulator state are
  ignored unless explicitly tracked as release-safe artifacts.
- Run a tracked-artifact audit such as:

```bash
git ls-files '*.gba' '*.sav' '*.ss' '*.sgm' '*.srm' '*.state' '*.bps' ':!:releases/**/*.bps'
```

- If release patches are tracked, confirm they live only under the release
  policy path.

## Active Workflow Health

- Run the project's GUI/workbench integrity audit if one exists.
- Regenerate or validate active image/text manifests when the task touches those
  areas.
- Confirm missing-path counts are zero before moving or pruning assets.

## Session Scope

- Identify whether the task is active localization QA, cleanup, retrospective,
  starter-kit extraction, or release packaging.
- State the safety boundary before editing.
- Prefer one small checkpoint commit over a large mixed cleanup.

## Stop Conditions

Stop and ask the user before proceeding if:

- the source ROM or current review ROM cannot be identified;
- active GUI/build checks fail;
- a planned deletion touches a file with unknown active references;
- local files outside the repo appear to be required.
