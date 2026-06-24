# Local Runtime Artifacts Matrix

Date: YYYY-MM-DD

This file documents local ROM, save, savestate, emulator, and review artifacts.
It should not list copyrighted ROM contents in Git, but it should explain which
local ignored files are still needed for QA.

## Policy

- ROMs, saves, savestates, and emulator cache are ignored.
- Release patches may be tracked only under the approved release path.
- Local paths are operator-specific and must not become build dependencies.

## Matrix

| Artifact | Local path | Role | Tracked? | Keep reason | Removal gate |
| --- | --- | --- | --- | --- | --- |
| Source ROM | `local_roms/source.gba` | Clean patch input | No | Required to build/rebuild locally. | Never commit; user-controlled local file. |
| Review ROM | `patched_roms/review/review.gba` | QA output | No | Active gameplay testing. | QA closes or replaced by newer review ROM. |
| QA save | `patched_roms/review/review.sav` | Runtime reproduction | No | Reproduces reported scenes. | Bugs verified or save superseded. |

## Audit Commands

```bash
git ls-files '*.gba' '*.sav' '*.ss' '*.sgm' '*.srm' '*.state' '*.bps' ':!:releases/**/*.bps'
git status --short --ignored
```
