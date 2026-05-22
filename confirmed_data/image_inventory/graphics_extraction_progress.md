# Graphics Extraction Progress

Generated: `2026-05-22T00:24:49`

## Static ROM Extraction

- LZ77 blocks extracted: `442`
- RLE blocks extracted: `1084`
- Raw scan windows rendered: `512`

## English Patch Diff

- LZ77 compared/changed: `439` / `2`
- RLE compared/changed: `1084` / `20`

## Runtime Matching

- Runtime match sets: `19`
- Unique matched LZ77/RLE/raw offsets: `28` / `95` / `6`
- Total unique runtime-matched offsets: `129`

## Workbench

- GUI image items: `30`
- Directly editable items: `24`
- Uploaded replacements: `9`
- Items with apply errors: `0`
- Progress states: `{'candidate_found': 21, 'edited': 9}`
- Actual localization targets curated: `24`
- Focused runtime tilemap targets: `12`

## Preview Assets

- Runtime match PNGs: `463`
- Runtime tilemap PNGs: `166`
- Runtime RLE screen-order workspaces: `117`
- Runtime RLE screen-order PNGs: `710`
- Edit-pack PNGs: `23`

## Open Risks

- Static extraction counts are discovery totals, not localization-needed totals.
- Raw RLE tile sheets can be misleading when the game reorders tiles through runtime tilemaps.
- Runtime coverage depends on collected savestates/screens; newly reached screens can reveal more image assets.
- Title-screen menu graphics need tilemap-aware replacement testing, not blind raw tile replacement.
