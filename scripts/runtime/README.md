# Runtime Scripts

Future home for emulator, savestate, tilemap, and runtime capture tooling.

Current implementations still live in `scripts/` top level. Move them here only
after compatibility wrappers are in place.

## Current Top-Level Scripts

Emulator and savestate probing:

- `scripts/pymgba_runtime_probe.py`
- `scripts/run_mgba_runtime_probe.sh`
- `scripts/extract_mgba_savestate_visual_state.py`

Tilemap/runtime rendering:

- `scripts/render_runtime_tilemaps.py`
- `scripts/render_all_runtime_tilemaps.py`
- `scripts/analyze_runtime_tilemap_sources.py`
- `scripts/tune_runtime_rle_alignment.py`

Runtime visual case registration:

- `scripts/register_runtime_visual_case.py`

## Move Holds

- Runtime tooling is closely tied to active gameplay QA and user-supplied
  savestates. Do not move it until the user-facing QA loop is stable.
- `run_mgba_runtime_probe.sh` still has a local convenience search for
  `$HOME/Downloads`; keep explicit `MGBA_BIN` support if this is refactored.

## Future Migration Shape

Keep emulator setup local and ignored. Tracked runtime scripts should document
what evidence they produce and whether that evidence is editable source,
diagnostic capture, or retrospective-only proof.
