# Layout And Dialogue Runtime Scripts

Future home for text-box layout, dialogue metadata, runtime dialogue family, and
page-flow analysis scripts.

Current implementations still live in `scripts/` top level. Move them here only
after compatibility wrappers are in place and the generated report paths are
documented.

## Current Top-Level Scripts

Layout and taxonomy:

- `scripts/build_text_box_family_manifest.py`
- `scripts/build_text_layout_assignment_index.py`
- `scripts/build_text_taxonomy_manifest.py`

Dialogue runtime reports:

- `scripts/build_runtime_candidate_groups.py`
- `scripts/build_runtime_dialogue_family_report.py`
- `scripts/build_runtime_dialogue_subprofiles.py`
- `scripts/build_runtime_family_focus_report.py`
- `scripts/build_runtime_pageflow_focus.py`
- `scripts/build_runtime_resolution_gates.py`

Dialogue speaker and state metadata:

- `scripts/build_dialogue_speaker_probe.py`
- `scripts/build_dialogue_state_cluster_summary.py`
- `scripts/build_dialogue_state_index.py`
- `scripts/build_dialogue_state_runs.py`

## Move Holds

- These scripts write or explain metadata under `confirmed_data/text_layout/`
  and `confirmed_data/dialogue_metadata/`.
- Some outputs are used as QA context rather than direct rebuild inputs.
- Do not archive a generator until its output is classified as active,
  reproducible, or retrospective-only.

## Future Migration Shape

Keep top-level wrappers first, then move one report family at a time. After each
move, regenerate or inspect the associated report and update docs that reference
the old path.
