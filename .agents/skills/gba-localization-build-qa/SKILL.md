---
name: gba-localization-build-qa
description: Build reproducible GBA localization review ROMs and run evidence-backed gameplay QA across text families, fonts, images, structural edge cases, saves, transitions, and GUI-to-ROM synchronization. Use when applying translations, rebuilding review ROMs, diagnosing reverted or missing changes, testing gameplay progression, recording bugs, or validating a release candidate before patch packaging.
---

# GBA Build And QA

Build from a verified clean source through one canonical sequential pipeline.
Never patch the source ROM in place.

## Prepare

1. Require `font` and `translate` to be ready. Allow `images` to remain
   `in_progress` for text-only review builds, but record omitted targets.
2. Verify source ROM SHA-256 and a clean or understood Git status.
3. Read canonical commands from `.gba-localization/project.json`.
4. Read [build-qa-contract.md](references/build-qa-contract.md).
5. Acquire the `build_qa` lifecycle claim before generating shared outputs.

## Build Sequentially

Use one top-level command that:

1. validates manifests and canonical translation ownership;
2. regenerates derived datasets;
3. prepares font and encoding assets;
4. applies text by explicit field priority and family capability;
5. applies image targets in deterministic parent-resource order;
6. audits skipped, protected, overflowed, and unknown records;
7. writes a new review ROM and build manifest;
8. restores or discards partial output on failure.

Do not run dataset regeneration and ROM apply concurrently. A race can reapply
stale values after a correct edit.

## Build Manifest

Record source ROM hash, Git revision, canonical data fingerprints, tool
versions, commands, apply counts by family, skipped reasons, output ROM hash,
and build ID. Keep local ROM paths repo-relative.

## Gameplay QA

Test:

- smoke boot and save/load;
- representative screens for every text and renderer family;
- shortest, longest, multiline, and boundary-crossing records;
- line wraps, page turns, punctuation, dynamic tokens, and player input;
- menus, battle HUD, world map, images, palettes, animation, and shared assets;
- progression transitions after repointing or relocation;
- reported missing or awkward translations at exact build IDs.

When the user reports a problem, create a reproducible QA case before changing
data. Record location, steps, expected/actual result, screenshot or save path,
build ID, suspected phase, and resolution status.

## Diagnose Stale Results

Distinguish:

- canonical data changed;
- generated dataset changed;
- running GUI reloaded;
- review ROM rebuilt;
- emulator opened the intended build.

Do not assume the visible ROM corresponds to the latest file merely because its
path is familiar.

## Exit Gate

Mark `build_qa` as `ready` when a clean canonical build reproduces the reviewed
ROM, required QA cases pass, remaining issues are classified, and progression
has no known localization-induced blocker. Mark it `complete` only for a
specific release candidate. Release the lifecycle claim after checkpointing the
phase.
