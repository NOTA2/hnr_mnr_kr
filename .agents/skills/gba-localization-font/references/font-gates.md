# Font And Encoding Gates

## Gate 1: Code Space

Record valid source codes, reserved control values, multibyte collisions,
fallback codes, and the number of assignable entries.

## Gate 2: Glyph Storage

Record original location, byte capacity, glyph stride, alignment, compression,
new location if relocated, and maximum safe glyph count.

Code space and storage capacity are separate numbers. Pass both.

## Gate 3: References And Bounds

Find and test:

- primary and mirror pointers;
- lookup tables;
- glyph count or bounds constants;
- cache or decompression destinations;
- alternate renderer families.

## Gate 4: Atlas Quality

Record:

- font name and license;
- source size and rasterization settings;
- baseline and width policy;
- 1bpp/2bpp/4bpp conversion;
- deterministic generation command;
- representative visual review.

Generated placeholders do not pass this gate.

If manual correction is required, keep the generated seed and user-authored
overlay separate. Regenerating the seed must not erase the overlay.

## Gate 5: Runtime Addressing

Test direct glyph slots in actual gameplay. Include suspected combining-mark or
special-control slots. A tile that looks independent in a preview may be
interpreted as a mark attached to the previous character.

## Gate 6: Layout

Test narrow and wide syllables, punctuation, spaces, repeated glyphs, line
wrapping, page turns, menu alignment, and clipping. Keep layout profiles linked
to text source families rather than one global character limit.
