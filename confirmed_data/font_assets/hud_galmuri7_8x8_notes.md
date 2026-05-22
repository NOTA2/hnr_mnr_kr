# Galmuri7 8x8 HUD Font Candidate

- Source atlas: `third_party/font_atlases/finalists/Galmuri7_9x9.png`
- Source size: `576x1575`
- Grid: `64x175`
- Cell size: `9x9`
- Cropped glyph size: `8x8`
- Character order: Unicode Hangul syllables, `U+AC00` to `U+D7A3`
- Prepared workbench: `analysis/generated_workbenches/hud_galmuri7_8x8`
- Preview: `confirmed_data/font_assets/hud_galmuri7_8x8_preview.png`

## Battle HUD Notes

- The visible enemy name `メイビースト` in `current_review_ss2` is a BG1 mini-font render, not a normal dialogue string and not a single baked image.
- Its on-screen crop is `56x8` pixels.
- The runtime uses 7 tiles for the 6 visible kana because `ビ` is split into a base glyph plus dakuten-like tile.
- The corresponding source glyph tiles are in the raw HUD font block around `0x00186C34`, not in the global 12x12 dialogue font.
- The raw HUD font resource appears to be referenced by a pointer-length table around `0x0017785C`; the candidate block is `0x00186C34` length `0x0F00` (`120` 8x8 tiles).
- That block has unused zero tiles, so adding HUD-only Hangul glyphs may be possible once the enemy-name/custom-code source data is identified.

## Current Limitation

The enemy name source data/encoding has not been identified yet. Direct CP932 searches for `メイビースト`, decomposed `メイヒ゛ースト`, and source tile-index sequences did not produce a full match in ROM or the ss2 savestate.
