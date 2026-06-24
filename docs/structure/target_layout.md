# Target Layout

This is the desired long-term shape. It is not the current layout yet.

## Project-Specific Repo Shape

```text
.
├── README.md
├── docs/
│   ├── start.md
│   ├── qa/
│   ├── structure/
│   ├── retrospective/
│   └── workflows/
├── src/
│   └── gba_kor_tool/
├── scripts/
│   ├── build/
│   ├── audit/
│   ├── text/
│   ├── image/
│   ├── font/
│   ├── runtime/
│   ├── workbench/
│   └── archive/
├── tools/
│   ├── localization_workbench/
│   └── glyph_editor/
├── data/
│   ├── canonical/
│   ├── worksets/
│   ├── fonts/
│   ├── images/
│   ├── layout/
│   └── workbench/
├── artifacts/
│   ├── analysis/
│   ├── generated_workbenches/
│   ├── reports/
│   └── screenshots/
├── roms/
│   ├── source/
│   └── patched/
└── third_party/
```

## Meaning

- `src/`: reusable code.
- `scripts/`: command entry points, grouped by workflow.
- `tools/`: local UI tools, with assets and server code nearby.
- `data/canonical/`: stable source-of-truth extracted data.
- `data/worksets/`: human translation/editing units.
- `data/images/`: final image edit sources and manifests.
- `artifacts/`: regenerable or historical outputs, mostly ignored.
- `roms/`: local-only ROM input/output area, ignored by default.
- `docs/workflows/`: current operating manuals.
- `docs/retrospective/`: lessons learned and project history.

## Starter-Kit Shape

The future generic GBA localization starter kit should not copy this repo's
project data. It should copy the workflow skeleton:

```text
gba-localization-starter/
├── README.md
├── docs/
│   ├── checklists/
│   │   ├── session_start.md
│   │   ├── cleanup_gate.md
│   │   └── release_gate.md
│   ├── workflows/
│   │   ├── bootstrap_sequence.md
│   │   └── cleanup_sequence.md
│   ├── retrospective/
│   │   └── failure_modes.md
│   └── start.md
├── src/
│   └── gba_kor_tool/
├── scripts/
│   ├── audit/
│   ├── build/
│   ├── image/
│   ├── text/
│   └── runtime/
├── schemas/
│   ├── project_config.schema.json
│   ├── text_source_family.schema.json
│   └── image_target.schema.json
├── templates/
│   ├── project_config.example.json
│   ├── gitignore.gba-localization.example
│   ├── local_runtime_artifacts_matrix.template.md
│   └── generated_workbench_retention.template.md
├── prompts/
│   └── agent_seed_prompt.md
└── .gitignore
```

The starter kit should contain no ROM, no project-specific extracted text, no
local Codex logs, and no `/Users/user/test` paths.

Starter-kit extraction should use `docs/retrospective/failure_modes.md` as the
main source for reusable agent guardrails.

## Current Starter-Kit Extraction Layer

The active repo now keeps the reusable extraction layer under
`docs/starter_kit/`:

- `checklists/`: session, cleanup, and release gates.
- `schemas/`: neutral metadata contracts for project config, text families, and
  image targets.
- `templates/`: copyable starter files.
- `prompts/`: reusable agent seed prompt.
- `workflows/`: bootstrap and late-stage cleanup operating order.

This layer is allowed to become more organized before the active project data
does. It must stay free of ROMs, extracted project text, local paths, and raw
session logs.
