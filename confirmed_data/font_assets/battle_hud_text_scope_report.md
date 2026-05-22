# Battle HUD Text Scope Report

## Current Capacity Finding

- Raw HUD mini-font block: `0x00186C34`
- Resource table entry: `0x0017789C`
- Current block length: `0x0F00`
- Tile size: `8x8`, 4bpp, `32` bytes per tile
- Tile count: `120`
- Empty tiles found: `34`

This means the initially confirmed HUD-only Hangul glyphs can fit. The full
battle name table has now been found, so final capacity should be judged
against that list rather than the single ss2 sample.

## Confirmed Runtime/Text Targets So Far

| area | source | suggested Korean | handling |
| --- | --- | --- | --- |
| Battle HUD actor | `エド` | `에드` | mini-font/text renderer candidate |
| Battle HUD actor | `アル` | `알` | mini-font/text renderer candidate |
| Battle HUD enemy seen in ss2 | `メインビースト` | `메인비스트` | mini-font/text renderer, source table found |
| Battle command | `こうげき` | `공격` | raw 4bpp command image block |
| Battle command | `れんせい` | `연성` | raw 4bpp command image block |
| Battle command | `てちょう` | `수첩` | raw 4bpp command image block |
| Battle command | `アイテム` | `아이템` | raw 4bpp command image block |
| Battle card panel | `2枚` | `2장` | RLE image block |
| Alchemy popup | `錬成` | `연성` | RLE image block |
| Alchemy popup | `もどる` | `돌아가기` | RLE image block |
| Alchemy popup | `つかう` | `사용` | RLE image block |
| Alchemy popup | `すてる` | `버리기` | RLE image block |
| Card list | `いいえ` | `아니요` | RLE image block |
| Notebook label | `錬成手帳` | `연성수첩` | runtime text/tilemap candidate |

The suggested Korean text above contains `28` unique Hangul syllables:

`가 격 공 기 니 돌 드 리 메 버 비 사 성 수 스 아 알 에 연 요 용 이 인 장 첩 템 트`

## Battle HUD Name Table

- Source resource table: `0x0017785C`
- Name/battle record resource index: `0x0933`
- Resource offset: `0x003D0E80`
- Record size: `0x1A`
- Record count: `94`
- Unique decoded names: `64`
- Full extraction report: `confirmed_data/font_assets/battle_hud_name_table.md`

The current ss2 enemy name is not `メイビースト`; it is `メインビースト`.
The ROM source bytes are `d2 b2 dd cb de b0 bd c4`, decoded by the HUD
renderer as `ﾒｲﾝﾋﾞｰｽﾄ`.

## Repoint Assessment

Repointing the HUD mini-font block looks plausible because the source is
referenced by a pointer-length table. The name string storage also sits inside
resource `0x0933`, which is itself pointer-length addressed, so expanding or
moving the name table is feasible if translations exceed the current string
area. The separate caution is that the HUD renderer currently addresses a
120-slot 8x8 glyph space through one-byte codes and dakuten modifiers, so using
more than those slots would require a renderer patch, not only a data repoint.

1. Append a larger HUD mini-font block to expanded ROM space.
2. Update the pointer-length table entry at `0x0017789C`.
3. Repoint/expand resource `0x0933` if the translated name strings need more
byte space.
4. Verify whether the 120 renderer-addressable glyph slots are enough for the
chosen Korean name translations.

## Korean HUD Name Patch Status

The first attempted pass that wrote Hangul into `0x00534874` was rolled back.
That block is shared by field/dialogue/menu UI, so replacing many slots there
corrupts unrelated screens. The safe patch now avoids that block entirely.

- Apply script: `scripts/apply_battle_hud_name_font.py`
- Target ROM: `patched_roms/current_review/hnr_localization_review.gba`
- Rollback for the bad shared-font pass: `patched_roms/current_review/hnr_localization_review.before_battle_hud_name_font.gba`
- Backup before the current safe pass: `patched_roms/current_review/hnr_localization_review.before_safe_battle_hud_name_font.gba`
- Font atlas: `third_party/font_atlases/finalists/Galmuri7_9x9_no_shadow.png`
- Backup before the no-shadow font repaint: `patched_roms/current_review/hnr_localization_review.before_no_shadow_battle_hud_name_font.gba`
- Backup before the black/white inversion fix: `patched_roms/current_review/hnr_localization_review.before_bw_invert_battle_hud_name_font.gba`
- Current atlas conversion: bright white pixels are glyph ink; black atlas pixels are transparent background.
- Patched battle-name raw font block: `0x00186C34`
- Unchanged shared UI/font block: `0x00534874`
- Patched name resource: `0x0933` at `0x003D0E80`
- Hangul glyphs used: `99`
- Addressable battle mini-font slots used: `99`
- HUD-only compact labels used to fit the slot budget:
  - `ゴウトウ`: `도적`
  - `サンゾク`: `도적`
  - `シシオウ`: `사왕`
  - `ゴーゴンリップ`: `고르곤`
- Name strings used `307` bytes inside resource `0x0933`, leaving `327` bytes free
- Reports:
  - `confirmed_data/font_assets/battle_hud_name_font_apply_report.json`
  - `confirmed_data/font_assets/battle_hud_name_hangul_tile_map.json`
  - `confirmed_data/font_assets/battle_hud_name_hangul_slots_preview.png`
  - `confirmed_data/font_assets/battle_hud_name_no_shadow_sample_preview_8x.png`
  - `confirmed_data/font_assets/battle_hud_name_bw_inverted_sample_preview_8x.png`

This safe pass is applied to the current review ROM, but it is not yet wired
into `scripts/build_localization_review_rom.py`. Keep it manual until the
runtime screen check confirms the mini-font byte range behaves as expected.

## Next Extraction Need

The enemy/actor name list is now proven from ROM data. The next practical step
is to decide Korean names, count unique Hangul syllables, and then build the
HUD mini-font mapping/repoint plan from that final list.
