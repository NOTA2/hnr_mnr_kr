---
name: gba-localization-images
description: Discover, classify, edit, reinsert, and verify GBA text-bearing graphics with explicit ROM resources, compression, tile and screen order, tilemaps, palette provenance, source scale, reversible crop maps, GUI upload references, and cleanup roles. Use for title screens, menus, HUD labels, icons, RLE or LZ graphics, palette problems, scrambled tiles, image workbenches, or replacement payload cleanup.
---

# GBA Image Pipeline

Keep discovery evidence, editable ROM sources, and final replacements separate.
An image that resembles the target is not necessarily the data the ROM uses.

## Prepare

1. Require `rom_analysis` to be ready and verify the source ROM hash.
2. Read `.gba-localization/manifests/image_targets.json`.
3. Read [image-target-contract.md](references/image-target-contract.md).
4. Inventory text-bearing visual screens before editing individual files.
5. Acquire the `images` lifecycle claim before changing shared image assets.

## Discover

1. Use screenshots, savestates, VRAM captures, contact sheets, and broad tile
   dumps as runtime or discovery evidence only.
2. Locate the backing ROM resource and determine compression, dimensions, bit
   depth, tile order, tilemap or screenblock, palette bank, and assembly context.
3. Distinguish raw storage order from screen order. Preserve a reversible map
   between the two.
4. Reject a candidate as an editable source until its ROM resource and apply
   path are known.
5. Verify the original label and gameplay meaning before translating an image;
   do not trust a guessed reading or a visually similar menu item.
6. When alignment remains uncertain, provide a local adjustment tool with an
   8x8 grid, tile indices, numeric x/y offset, tile start/order, palette
   selection, live preview, and a saved repo-relative configuration.

## Create An Edit Pack

1. Store a 1x editable source image. Mark scaled images as generated previews.
2. Record palette provenance and quantization policy for indexed-color assets.
3. For a small label inside a large compressed block, create a focused crop
   with a reversible parent-resource map.
4. When multiple edits share a compressed parent, apply them to one current
   parent payload in a deterministic order. Do not rebuild each edit from a
   stale original block.
5. Keep source, replacement, generated binary, previews, and runtime evidence in
   distinct paths and manifest roles.
6. Record an allowed edit rectangle or pixel mask. Fail validation if any pixel
   outside it changes, if dimensions change, or if new palette colors appear
   without an explicit policy.

## Integrate GUI Uploads

If a GUI accepts replacement files:

1. Treat uploads as operational assets until they are promoted or dereferenced.
2. Regenerate the active-reference manifest from current GUI state.
3. Use the same Unicode normalization and path semantics as the runtime
   platform.
4. Require zero missing active references before pruning upload storage.
5. Reload the GUI after dataset or schema changes.

## Apply And Verify

1. Apply to a copy of the verified source or canonical current build.
2. Validate compressed sizes, pointers, checksums, tile counts, and palette
   indices.
3. Re-extract the patched resource and compare it with the intended replacement.
4. Verify the actual screen in runtime, including sibling colors, animation
   frames, shared tiles, and later screens that reuse the resource.
5. Re-run every sibling target that shares the compressed parent, tile bank, or
   palette. A successful target does not excuse corruption in another screen.

## Exit Gate

Mark `images` as `ready` when each final target has a rebuildable ROM-backed
source, reversible apply path, palette and mapping provenance, and runtime
evidence. If no graphics require localization, set `inventory_complete` and
record that scoped conclusion as evidence. Release the lifecycle claim after
checkpointing the phase.
