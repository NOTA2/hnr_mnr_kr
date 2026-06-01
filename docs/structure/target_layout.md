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
│   ├── start.md
│   ├── workflow_text.md
│   ├── workflow_font.md
│   ├── workflow_image.md
│   ├── qa_checklist.md
│   └── failure_modes.md
├── src/
│   └── gba_kor_tool/
├── scripts/
│   ├── audit/
│   ├── build/
│   ├── image/
│   ├── text/
│   └── runtime/
├── templates/
│   ├── translation_workset.schema.json
│   ├── image_edit_pack.schema.json
│   └── project_config.example.json
└── .gitignore
```

The starter kit should contain no ROM, no project-specific extracted text, no
local Codex logs, and no `/Users/user/test` paths.

