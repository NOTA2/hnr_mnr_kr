---
name: gba-localization-font
description: Design and verify GBA Korean font and encoding support by separating codepoint space, glyph payload capacity, tile format, pointer relocation, renderer addressing, atlas quality, width behavior, and runtime slot safety. Use when inserting Hangul glyphs, choosing an encoding, relocating font data, fixing missing or combined glyphs, auditing mini-fonts, or validating production font assets.
---

# GBA Font Pipeline

Prove the renderer path as well as the bitmap data. A correct static atlas can
still fail at runtime.

## Prepare

1. Require `rom_analysis` to be ready and load the current text-family manifest.
2. Read `.gba-localization/manifests/font.json`.
3. Read [font-gates.md](references/font-gates.md).
4. Inventory every renderer/font family separately: dialogue, UI, HUD,
   variable-width, mini-font, and image-backed labels may not share rules.
5. Acquire the `font` lifecycle claim before changing maps or font assets.

## Establish Capacity

1. Audit available codepoints independently from available glyph storage.
2. Identify glyph dimensions, bit depth, stride, tile order, palette roles, and
   table indexing.
3. Find all base pointers, mirror pointers, size constants, and bounds checks
   before relocation.
4. Determine whether the renderer addresses one-byte slots, multibyte codes,
   composed marks, or remapped indices.
5. Build a runtime slot-safety probe for small fonts. Do not assume every
   physical tile is an independent character; some slots may combine with the
   preceding glyph.

## Choose The Encoding And Glyph Set

1. Derive required glyphs from canonical translations plus dynamic runtime
   inputs and fallback policy.
2. Decide whether to store a full Hangul set, a project subset, or a composed
   scheme based on proven code space, storage, and renderer behavior.
3. Keep codepoint mapping deterministic and versioned.
4. Preserve original digits, Latin text, and symbols when reuse is safe.
5. Define missing-glyph behavior; never let an unmapped character silently emit
   a structurally meaningful byte.

## Produce Assets

1. Use placeholder glyphs only for addressing tests.
2. Build production glyphs from a documented, licensed atlas or editor flow.
3. Record source font, license, rasterization size, thresholding, baseline, and
   conversion command.
4. Keep source atlas, generated binary, mapping manifest, and previews in
   distinct roles.
5. When automatic rasterization needs repeated visual correction, provide a
   local bitmap editor with draw/erase, undo/redo, glyph navigation, baseline
   or crop controls, and deterministic import/export. Save user corrections as
   canonical overlays instead of asking for repeated one-off code changes.

## Verify

Test representative Hangul syllables, punctuation, spacing, numbers, line
breaks, width extremes, page transitions, and each renderer family in runtime.
Include one easy-to-reach early-game screen for quick iteration. Check unrelated
UI and original glyphs after relocation.

## Exit Gate

Mark `font` as `ready` only when code space, storage, relocation, atlas, and
runtime renderer gates all pass for the release scope. A static preview or one
successful dialogue line is not sufficient evidence. Release the lifecycle
claim after checkpointing the phase.
