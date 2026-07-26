# Failure Modes And Prevention Playbook

Date: 2026-06-12 KST

This document turns the project retrospective into reusable operating rules for
future GBA localization work. It summarizes recurring failure modes, their
symptoms, the safer check, and the starter-kit rule to extract later.

Raw Codex logs are not copied into the repo. This playbook is based on project
docs, cleanup audits, build scripts, and summarized evidence.

## 1. Runtime Evidence Mistaken For Editable Source

Symptom:

- A screenshot, savestate dump, or runtime tile capture looks like the thing to
  edit, but replacing it does not affect the ROM or only works in a preview.

Cause:

- Runtime captures show what the game assembled on screen. They are evidence for
  locating assets, not automatically ROM-backed edit sources.

Prevention:

- Mark runtime-derived folders as `reference-only` until a ROM-backed resource,
  tilemap, palette, and insertion path are identified.
- Build edit packs from ROM-backed LZ/RLE/raw resources, not from screenshots
  alone.

Starter-kit rule:

- Every image target needs `evidence_path`, `rom_resource_path`, `tilemap_path`,
  `palette_source`, and `apply_script` fields. If any is unknown, the target is
  not yet an editable source.

## 2. Raw Tile Order Mistaken For Screen Order

Symptom:

- Extracted graphics are scrambled or replacements appear in the wrong visual
  order even when the tile pixels are correct.

Cause:

- GBA graphics are often assembled through tilemaps/screenblocks. Raw tile order
  is storage order, not necessarily visual order.

Prevention:

- Treat tile data, tilemap, palette, scroll/fine offset, and screenblock context
  as one unit.
- Prefer screen-order workspaces for user-facing edits, while preserving the map
  back to ROM tile indices.

Starter-kit rule:

- Image extraction should create both a raw-resource manifest and a screen-order
  edit manifest. The latter must point back to the former.

## 3. Generated Bulk Mistaken For Source Of Truth

Symptom:

- Thousands of generated PGM/JSON/report files accumulate, and cleanup becomes
  scary because it is unclear which ones are active.

Cause:

- Generated workbenches were kept as if every output were evidence. The true
  source of truth was the active input JSON, generator script, manifest, and a
  compact audit summary.

Prevention:

- Keep active manifest-referenced outputs only when the build directly needs
  them.
- Delete or untrack historical generated output only after preserving the lesson
  and regeneration command.

Starter-kit rule:

- Generated folders need an ownership marker: `active`, `historical-summary-kept`,
  or `scratch-delete-ok`. Cleanup must compare actual files against the active
  manifest before deleting.

## 4. Machine Paths Becoming Hidden Dependencies

Symptom:

- Reports or docs contain `/Users/...` or `/private/tmp/...`, and later sessions
  cannot tell whether those paths are required.

Cause:

- Absolute paths are useful provenance during experiments but unsafe as active
  workflow inputs.

Prevention:

- Active scripts and manifests should write repo-relative paths whenever the file
  is inside the repo.
- Historical docs may keep absolute paths only as provenance.

Starter-kit rule:

- Add a portability audit that separates `active dependency`, `historical
  provenance`, and `external user input`.

## 5. GUI State Lagging Disk State

Symptom:

- A translation or metadata fix is present on disk, but the GUI still shows old
  data or rebuilds from stale state.

Cause:

- The GUI server can keep dataset state in memory. Regenerating JSON does not
  guarantee the running process reloaded it.

Prevention:

- Restart or reload the GUI after dataset schema/source changes.
- Record whether a change is disk-only, GUI-visible, or ROM-applied.

Starter-kit rule:

- GUI tools need an explicit dataset version/reload indicator and a rebuild
  sequence check.

## 6. Source Families Overgeneralized

Symptom:

- A rule that is correct for one text family breaks another: spacing, line
  breaks, byte limits, or punctuation policies become inconsistent.

Cause:

- `Entry8`, `Registry D`, UI/item text, battle/ability/material descriptions,
  credits, and inline event text use different runtime profiles.

Prevention:

- Do not apply global limits such as "one line N chars" without source-family
  evidence.
- Store layout/insertion capability per source family, not just per workset.

Starter-kit rule:

- Maintain a `text_category_capability_matrix` from the beginning, with fields
  for terminator, counted header, repoint support, runtime line profile, and
  punctuation/width policy.

## 7. Header Or Structural Metadata Lost During Apply

Symptom:

- Text appears corrupted, boundaries move, or command streams break even though
  the visible translation itself looks short enough.

Cause:

- Command-stream records such as `01 FF <char_count>` require metadata to travel
  with the translation. Payload-only replacement drops structural meaning.

Prevention:

- Preserve `header_offset`, `prefix`, `char_count`, terminator policy, and raw
  span metadata through extraction, GUI, worksets, and build scripts.
- Run normalization regression audits after policy changes.

Starter-kit rule:

- Translation records must have a schema that distinguishes plain terminated
  text, fixed slots, counted command-stream records, and packed script entries.

## 8. Inline Fixed Text Missed Near Extracted Records

Symptom:

- A screen still shows Japanese even though the nearby Entry8 record is already
  extracted and translated.

Cause:

- Some choices, short exclamations, or event lines are printable fixed slots
  between control bytes, not counted Entry8 records.

Prevention:

- When a user reports remaining Japanese near an Entry8 line, inspect bytes
  before and after the nearby record, not only the extracted record itself.
- Search for fullwidth-space choice runs and control-separated printable spans.

Starter-kit rule:

- Add a "nearby printable island" audit around every high-priority script bank,
  with overlap checks against canonical records.

## 9. False Positive Inline Text Applied Over Canonical Records

Symptom:

- An inline candidate looks valid but actually overlaps an existing term or
  Entry8 record, causing duplicate or partial replacement.

Cause:

- Dedupe by exact offset is not enough. A false positive can start inside another
  record's byte span.

Prevention:

- Reject inline candidates whose byte range overlaps a canonical text record
  unless manually classified as a separate fixed slot.

Starter-kit rule:

- All candidate extraction passes need range-overlap validation, not only offset
  equality checks.

## 10. Font Code Space Confused With Font Storage Capacity

Symptom:

- There seem to be many safe custom codes, but adding glyphs still fails or
  corrupts text rendering.

Cause:

- Available codepoints and available glyph payload capacity are different
  constraints.

Prevention:

- Audit codepoint availability, glyph payload capacity, mirror pointer tables,
  glyph stride, and relocation side effects separately.
- Treat placeholder glyphs as renderer tests, not production font assets.

Starter-kit rule:

- Font workflow must have separate gates for code space, glyph storage,
  relocation/mirror pointers, visual atlas quality, and runtime render QA.

## 11. HUD Mini-Font Physical Tiles Mistaken For Safe Slots

Symptom:

- Static preview shows a glyph in a tile, but runtime output combines or shifts
  characters incorrectly.

Cause:

- Some physical tiles are treated by the renderer as dakuten/handakuten-like
  marks rather than independent characters.

Prevention:

- Validate direct-addressable slots in runtime, not only in static previews.
- Do not use composite mark slots as independent Hangul syllables without an ASM
  renderer patch.

Starter-kit rule:

- Mini-font workflows need a runtime slot-safety audit before assigning custom
  glyphs.

## 12. Palette Context Ignored In Image Edits

Symptom:

- A replacement image has the correct shape but wrong colors compared with
  sibling UI elements.

Cause:

- In 4bpp assets, RGB colors map through a specific palette bank/context. The
  same visible color can quantize differently under another palette.

Prevention:

- Record palette source and sibling palette policy in every edit pack.
- Reuse palette context for related UI components.

Starter-kit rule:

- Image edit packs must include a palette provenance field and a quantization
  validation step.

## 13. Whole-Block Replacement Used For Small Label Edits

Symptom:

- Editing a small UI label becomes slow, risky, or forces unnecessary repointing.

Cause:

- The workflow edits a whole RLE/LZ block when the actual target is a small crop
  inside that block.

Prevention:

- Create focused crop edit packs for small labels.
- Preserve current ROM payload as the base when multiple edits share one block.

Starter-kit rule:

- Image workflow should support focused crop replacement with a reversible map to
  the parent resource.

## 14. Build Order Races Reintroduce Old Data

Symptom:

- A translation appears fixed, then a rebuild brings back an older draft or
  stale value.

Cause:

- Dataset regeneration and review ROM build can race, or build priority can use
  `agent_draft` before final `translation`.

Prevention:

- Run dataset regeneration before review ROM build, sequentially.
- Apply priority must be `manual_locked translation -> translation ->
  agent_draft -> original`.

Starter-kit rule:

- Provide one canonical "rebuild all" command with validation and restore-on-
  failure behavior.

## 15. Cleanup Done Before Preserving The Lesson

Symptom:

- A confusing failed artifact is deleted, and later the same mistake repeats
  because the artifact was the only memory of why it failed.

Cause:

- Cleanup optimized disk/repo size before extracting the retrospective lesson.

Prevention:

- Before deleting a confusing artifact, preserve the mistake, decision, and
  replacement rule in a compact retrospective document.
- Do not keep every failed artifact just because it was painful; keep the lesson
  and representative evidence.

Starter-kit rule:

- Cleanup agents must require a retention decision and a retrospective note for
  every deletion batch.

## 16. Pointer-Looking Values Treated As Segment Boundaries

Symptom:

- A counted Entry8 record appears to cross a segment boundary, and the apply
  path either corrupts nearby bytes or incorrectly marks the record impossible.

Cause:

- The segment-end heuristic treats every pointer-looking value in the Entry8
  table range as a hard boundary, even when the value points into a counted text
  payload.

Prevention:

- Carry byte span, counted prefix, original payload length, inferred segment,
  and boundary-crossing state through extraction and apply.
- Classify segments with a capability matrix before choosing in-place, overlay,
  repoint, protected, or unknown apply behavior.

Starter-kit rule:

- Script-bank tooling must validate candidate boundaries against record spans
  and range overlaps. Boundary-crossing records need a dedicated
  length-preserved path before any expansion or repoint attempt.

## 17. Image Discovery Output Promoted Without A Source Role

Symptom:

- A contact sheet, runtime capture, or broad tile extraction looks like the
  image to localize, but the replacement path later cannot be rebuilt or does
  not affect the target screen.

Cause:

- Discovery evidence, ROM-backed editable sources, previews, and final
  replacements were not separated with an explicit image target manifest.

Prevention:

- Assign every image artifact a role before editing or cleanup.
- Promote a candidate only after identifying the ROM resource, tile/screen-order
  mapping, palette source, 1x source image, replacement path, and apply script.
- Keep scaled previews regenerable and separate from editable sources.

Starter-kit rule:

- Image workflows need an artifact role taxonomy and a required image target
  schema before any candidate becomes a final replacement.

## 18. Uploaded Replacement Payloads Treated As Disposable Cache

Symptom:

- A small upload folder appears safe to prune, but active GUI JSON still points
  at files inside it.

Cause:

- Browser/user uploads became operational replacement assets before being
  promoted into durable edit packs. A stale manifest or byte-level filename
  comparison can miss active references, especially with macOS Unicode
  normalization.

Prevention:

- Regenerate the upload manifest from current GUI state before cleanup.
- Use the same path existence semantics as the runtime platform.
- Promote final assets into durable edit packs when appropriate, then update GUI
  references and verify zero missing paths.

Starter-kit rule:

- Uploaded replacement pruning is blocked unless the active-reference manifest
  is current, Unicode/path checks agree, and GUI integrity passes.

## 19. Manual Correction Trapped In An Agent Round Trip

Symptom:

- The user repeatedly asks for one-pixel shifts, crop changes, tile-order fixes,
  font baseline adjustments, or palette selection because the tool cannot save
  those parameters.

Cause:

- Discovery output was produced, but uncertain visual parameters remained
  hard-coded in scripts or depended on a fresh agent edit.

Prevention:

- Provide a local adjustment surface with an 8x8 grid, tile indices, numeric
  x/y offsets, tile start/order, palette selection, undo/redo, and saved
  repo-relative configuration.
- Preserve generated seeds separately from user-authored correction overlays.

Starter-kit rule:

- Repeated visual correction must graduate into deterministic user controls
  instead of consuming another agent round trip.

## 20. Shared Resources Or Concurrent Writers Reintroduced Damage

Symptom:

- Fixing one image breaks an earlier image, or two sessions modify the same
  canonical file/build output and the later result silently loses work.

Cause:

- Multiple targets shared one compressed parent, tile bank, palette, or output
  ROM, while apply steps rebuilt from stale inputs or more than one writer
  mutated shared state.

Prevention:

- Aggregate all edits for a shared parent into one deterministic apply order.
- Re-run every sibling target after the parent changes.
- Use a repository-local phase claim and one-writer policy for canonical data,
  GUI state, and shared build outputs.

Starter-kit rule:

- A successful target is insufficient when its parent is shared; parent-level
  regression and single-writer gates are required.

## 21. Pixel Edit Escaped Its Allowed Region

Symptom:

- A localized image looks plausible at first, but nearby borders, gradients,
  shadows, transparent pixels, or unrelated UI become contaminated.

Cause:

- The workflow relied on visual inspection without a machine-checkable edit
  rectangle or pixel mask.

Prevention:

- Require exact output dimensions.
- Compare source and replacement pixels and fail if any pixel outside the
  allowed rectangle or mask changes.
- Reject unapproved palette colors, resampling, and antialiasing.

Starter-kit rule:

- Image targets need pixel invariants in addition to ROM mapping and runtime QA.

## Starter-Kit Extraction Checklist

Before creating the generic GBA localization agent, convert the above failure
modes into:

- a bootstrap `.gitignore` policy for ROMs, saves, patches, generated workbenches,
  local tooling, and previews;
- a text extraction schema that distinguishes terminators, counted headers,
  fixed slots, packed scripts, and source-family layout rules;
- a script-bank capability matrix for segmented command-stream data such as
  Entry8;
- a font workflow with code-space, glyph-storage, relocation, atlas, and runtime
  render gates;
- an image workflow that separates runtime evidence, discovery workspaces,
  editable ROM-backed sources, scaled previews, and final replacements;
- saved manual tile/alignment controls and exact pixel-diff gates;
- parent-resource sibling regression and repository-local writer claims;
- an uploaded replacement manifest gate with Unicode/path checks;
- a GUI/workbench rebuild sequence with stale-state detection;
- a cleanup workflow that records keep/delete/untrack/track decisions before
  modifying files;
- a retrospective memory workflow that summarizes lessons without importing raw
  chat logs or machine-specific paths.
