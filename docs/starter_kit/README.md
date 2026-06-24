# GBA Localization Starter Kit

This folder contains project-neutral material to extract from this localization
project into a reusable GBA localization agent or skill.

It must not contain:

- ROM files or patches;
- project-specific extracted text;
- raw chat/session logs;
- machine-specific paths;
- assumptions that only fit one game.

## Start Here

- `gba_localization_agent.md`: reusable agent operating spec.
- `prompts/agent_seed_prompt.md`: copyable seed prompt for a new project.
- `workflows/bootstrap_sequence.md`: first-days workflow for another GBA
  localization repo.
- `checklists/session_start.md`: repeatable safety checks for every agent
  session.
- `checklists/cleanup_gate.md`: cleanup safety gate before deletion or moves.

The agent spec is derived from `docs/retrospective/failure_modes.md`, but it is
written so it can be copied to a new GBA localization repo without this
project's data.

## Folder Structure

```text
docs/starter_kit/
  README.md
  gba_localization_agent.md
  prompts/
    agent_seed_prompt.md
  workflows/
    bootstrap_sequence.md
    cleanup_sequence.md
  checklists/
    session_start.md
    cleanup_gate.md
    release_gate.md
  schemas/
    project_config.schema.json
    text_source_family.schema.json
    image_target.schema.json
  templates/
    project_config.example.json
    gitignore.gba-localization.example
    local_runtime_artifacts_matrix.template.md
    generated_workbench_retention.template.md
```

The extraction map in `docs/structure/starter_kit_extraction_map.md` explains
which current project documents feed each reusable output.

Recent lessons already folded into the spec:

- command-stream script banks need record-span and boundary validation;
- uploaded replacement payloads need a current active-reference manifest before
  pruning;
- local ROM/save/savestate artifacts need an explicit keep matrix;
- public script paths should move by compatibility wrapper, not broad rename.
- image/tile work needs explicit artifact roles, palette provenance, 1x source
  separation from scaled previews, and per-workspace prune gates.
