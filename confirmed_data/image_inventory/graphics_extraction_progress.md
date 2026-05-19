# Graphics Extraction Progress

Generated: `2026-05-19T07:15:26`

## Static ROM Extraction

- LZ77 blocks extracted: `442`
- RLE blocks extracted: `1084`
- Raw scan windows rendered: `512`

## English Patch Diff

- LZ77 compared/changed: `439` / `2`
- RLE compared/changed: `1084` / `20`

## Runtime Matching

- Runtime match sets: `10`
- Unique matched LZ77/RLE/raw offsets: `28` / `50` / `1`
- Total unique runtime-matched offsets: `79`

## Workbench

- GUI image items: `14`
- Directly editable items: `14`
- Uploaded replacements: `2`
- Items with apply errors: `0`
- Progress states: `{'candidate_found': 12, 'edited': 2}`
- Actual localization targets curated: `11`
- Focused runtime tilemap targets: `4`

## Preview Assets

- Runtime match PNGs: `149`
- Runtime tilemap PNGs: `56`
- Runtime RLE screen-order workspaces: `30`
- Runtime RLE screen-order PNGs: `181`
- Edit-pack PNGs: `5`

## Open Risks

- Static extraction counts are discovery totals, not localization-needed totals.
- Raw RLE tile sheets can be misleading when the game reorders tiles through runtime tilemaps.
- Runtime coverage depends on collected savestates/screens; newly reached screens can reveal more image assets.
- Title-screen menu graphics need tilemap-aware replacement testing, not blind raw tile replacement.
