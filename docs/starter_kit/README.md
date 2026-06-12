# GBA Localization Starter Kit

This folder contains project-neutral material to extract from this localization
project into a reusable GBA localization agent or skill.

It must not contain:

- ROM files or patches;
- project-specific extracted text;
- raw chat/session logs;
- machine-specific paths;
- assumptions that only fit one game.

Start with:

- `gba_localization_agent.md`: reusable agent operating spec.

The agent spec is derived from `docs/retrospective/failure_modes.md`, but it is
written so it can be copied to a new GBA localization repo without this
project's data.

Recent lessons already folded into the spec:

- command-stream script banks need record-span and boundary validation;
- uploaded replacement payloads need a current active-reference manifest before
  pruning;
- local ROM/save/savestate artifacts need an explicit keep matrix;
- public script paths should move by compatibility wrapper, not broad rename.
