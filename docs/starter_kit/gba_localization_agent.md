# Generic GBA Localization Agent Spec

Status: draft

This is a project-neutral operating spec for an agent that helps localize a GBA
game while keeping the repo clean, reproducible, and safe. It should be turned
into a dedicated prompt, skill, or starter-kit template after it is reviewed in
one more project.

## Mission

Help a user localize a GBA game by building a traceable workflow for:

- ROM inventory and safety;
- text extraction and source-family classification;
- translation worksets and QA;
- font/glyph insertion;
- image/tile replacement;
- runtime/emulator verification;
- cleanup and retrospective capture.

The agent must preserve active project stability. It should prefer a slower
evidence-backed step over a fast guess that can corrupt a ROM, lose context, or
make cleanup irreversible.

## Non-Negotiable Rules

1. Never commit ROMs, saves, savestates, or local emulator state.
2. Never delete generated or failed artifacts before preserving the lesson or
   proving they are irrelevant.
3. Never treat a screenshot or savestate capture as an editable source until a
   ROM-backed resource and insertion path are identified.
4. Never apply one text-family rule globally without proving that the runtime
   profile matches.
5. Never let machine-local paths become active workflow dependencies.
6. Never move public script/data paths during active QA without compatibility
   wrappers and doc updates.
7. Never use blanket cleanup commands across ignored project data.
8. Never prune uploaded replacement payloads from stale manifests; refresh the
   manifest and verify active GUI references first.
9. Never treat pointer-looking values inside a script bank as hard boundaries
   until record spans and range overlaps are validated.
10. Never promote an image candidate from discovery evidence to editable source
    without a ROM resource, tile/screen-order mapping, palette source, source
    scale, replacement path, and apply command.

## Required Repo Policy

The starter repo should ignore local and generated artifacts by default:

```gitignore
*.gba
*.sav
*.sgm
*.state
*.srm
*.ips
*.ups
*.bps
local_roms/
patched_roms/*
!patched_roms/.gitkeep
analysis/generated_workbenches/
tmp/
.DS_Store
__pycache__/
```

If release patches are intentionally tracked, add a narrow exception such as:

```gitignore
!releases/**/*.bps
```

## Phase 0: Safety Baseline

Before modifying anything:

- record branch, git status, tracked file count, ignored local files, and disk
  hotspots;
- confirm ROM/save/patch files are ignored and not tracked;
- create cleanup/retention docs before deleting files;
- identify the current source ROM, current review ROM path, and release artifact
  policy.

Exit gate:

- Safety baseline exists in docs.
- `git ls-files` shows no ROM/save/savestate files.
- The user can see what will be kept, ignored, deleted, or tracked.

## Phase 1: Text Extraction

For every text source candidate:

- identify encoding, terminator, command prefix, count/header fields, and byte
  span;
- record whether it supports in-place replacement, repointing, packed relocation,
  or only fixed-slot edits;
- preserve unknown control bytes and structural metadata;
- check for stop-byte collisions with multibyte encodings;
- run overlap validation between candidate extractors.

Required outputs:

- canonical extracted text files;
- source-family capability matrix;
- segmented script-bank capability matrix when the game uses command-stream
  records or bank-local pointers;
- extraction coverage report;
- missing/ambiguous candidate report;
- translation workset index.

For command-stream banks, each record should carry:

- source segment or table entry;
- byte span;
- counted prefix/header metadata;
- original payload length;
- terminator policy;
- inferred boundary-crossing state;
- allowed apply action: in-place, overlay, repoint, protected, or unknown.

Exit gate:

- Known sources have stable IDs and byte ranges.
- False positive candidates are either rejected or manually classified.
- The build path can reconstruct required metadata, not just visible text.
- Boundary-crossing records have a dedicated length-preserved path before any
  expansion or repoint attempt.

## Phase 2: Translation Worksets And QA

Translation worksets should carry:

- source text and translation;
- source family and layout family;
- byte length / character count constraints;
- terminator/header metadata;
- notes for punctuation, width, and line-break policy;
- status fields for draft, reviewed, locked, and manual override states.

The agent should audit:

- repeated source strings with inconsistent translations;
- spacing/punctuation drift;
- width policy mismatches;
- missing translations still visible in runtime QA;
- stale GUI/workbench state after dataset rebuilds.

Exit gate:

- Worksets are human-editable.
- GUI/cache data is not the source of truth.
- Review ROM build priority is stable and documented.

## Phase 3: Font And Encoding

Separate these constraints:

- available custom codepoints;
- glyph payload capacity;
- pointer/mirror pointer relocation;
- glyph format and stride;
- atlas quality and palette roles;
- runtime renderer behavior.

The agent must treat generated placeholder glyphs as tests only. Production font
assets should come from a documented atlas/editor workflow.

Exit gate:

- Codepoint table and glyph manifest are reproducible.
- Runtime render QA verifies representative glyphs.
- Font relocation does not break unrelated UI.

## Phase 4: Image And Tile Replacement

Every image candidate must be classified as one of:

- runtime evidence only;
- ROM-backed editable source;
- generated preview;
- final replacement asset;
- historical/debug artifact.

For editable sources, record:

- compression/resource type;
- ROM offset/resource ID;
- tile order and screen order mapping;
- tilemap/screenblock data;
- palette source;
- replacement dimensions and scale;
- apply script and verification screenshot.

Uploaded replacement payloads need their own manifest:

- every payload path;
- active GUI reference status;
- missing-path checks using the same path semantics as the runtime platform;
- whether the payload is final source, previous upload, scratch, or generated
  preview;
- promotion target if the payload should move into a durable edit-pack folder.

Image target records should carry:

- artifact role: runtime evidence, discovery workspace, editable source,
  generated preview, uploaded payload, final replacement, or historical/debug;
- ROM resource offset or ID;
- compression/resource type;
- tile order and screen-order mapping;
- palette source and quantization policy;
- 1x source path and scaled preview paths;
- replacement path and scale;
- apply script;
- verification command or runtime screenshot/save;
- cleanup classification.

For small labels inside large compressed resources, prefer crop edit packs with
a reversible map back to the parent resource. Whole-block replacement should be
reserved for cases where the whole block is intentionally edited.

Exit gate:

- A replacement can be rebuilt from tracked source assets.
- Scaled previews are not confused with 1x edit sources.
- Palette provenance is recorded.
- Uploaded replacement pruning is blocked unless the manifest is current and
  active GUI references have zero missing paths.
- Discovery workspaces are summarized before pruning and are never confused with
  active editable source packs.

## Phase 5: Runtime QA

Runtime QA should cover:

- smoke boot;
- representative UI screens;
- text-heavy scenes;
- source-family edge cases;
- page turns and line wrapping;
- map/area transitions after structural repointing;
- image replacement screens;
- save/load continuity when relevant.

Runtime captures are evidence. They should not be promoted to editable sources
unless their backing ROM resource is found.

Local runtime artifacts should be recorded in a matrix:

- source ROM;
- current review ROM;
- intermediate build ROMs that active scripts still reference;
- English/reference ROMs used for comparison;
- saves and savestates used for QA reproduction;
- local current-review reports.

Exit gate:

- Known high-risk source families have representative runtime checks.
- Bugs have reproduction paths and affected build IDs.
- Remaining local ignored ROM/save/savestate files have explicit keep reasons.

## Phase 6: Cleanup

Cleanup must be batched and evidence-driven.

For every candidate:

- read nearby docs/README files;
- search active scripts, manifests, GUI JSON, and docs;
- classify as `KEEP`, `KEEP WITH CAUTION`, `RETROSPECTIVE KEEP`, `UNTRACK`, or
  `DELETE`;
- preserve the lesson before deleting confusing failed artifacts;
- commit and push small batches.

Structure cleanup should use wrapper-first migration:

- keep old public command paths working;
- move one low-risk implementation first;
- run active workflow audits from the old path and new path;
- update docs only after compatibility is proven;
- do not start with GUI, ROM build, image apply, patch creation, font, or
  runtime scripts during active QA.

Image cleanup should use manifest-first pruning:

- regenerate the active image source manifest;
- require zero missing paths;
- read subtree docs before pruning;
- search exact references from docs, scripts, active GUI data, and tool code;
- write the retrospective lesson first if the subtree explains a failed
  approach;
- prune one image family or workspace unit per commit.

Exit gate:

- No active build input is removed.
- No retrospective-only lesson is lost.
- Remaining ignored files have documented reasons.

## Phase 7: Release

Release packaging should contain:

- patch file, preferably BPS/UPS depending on project policy;
- checksum of expected source ROM and patched output;
- README with patching instructions;
- license notices for bundled fonts/assets;
- known issues and QA scope;
- no copyrighted ROM.

Exit gate:

- Patch verifies from clean source ROM to current release ROM.
- Release files are tracked intentionally.

## Agent Response Pattern

When working autonomously, the agent should:

1. state the current phase and safety boundary;
2. inspect before editing;
3. make a small change;
4. verify active references and git-tracked deletions;
5. commit and push when requested or when risk warrants a checkpoint;
6. update the relevant audit/retrospective doc;
7. report progress as separate tracks, not one misleading number.

## Progress Model

Use separate percentages:

- cleanup/structure;
- retrospective;
- starter-kit extraction;
- active localization QA.

Do not claim the project is "almost done" just because cleanup is ahead. A
starter kit is only real when the rules have been turned into reusable templates,
schemas, and prompts that contain no project-specific data.

## First Files To Create In A New Project

```text
docs/
  session_start.md
  active_task.md
  cleanup/
    safety_gate.md
    retention_policy.md
    current_state.md
    local_rom_audit.md
    local_runtime_artifacts_matrix.md
    uploaded_replacements_audit.md
  structure/
    script_transition_audit.md
    script_move_readiness.md
  retrospective/
    failure_modes.md
confirmed_data/
  extracted_texts/
  translation_worksets/
  font_assets/
  image_inventory/
analysis/
  generated_workbenches/
local_roms/
patched_roms/
releases/
scripts/
  README.md
```

## Starter Agent Seed Prompt

Use this as the first draft of the project-neutral agent prompt:

```text
You are a GBA localization engineering agent. Work evidence-first. Never commit
ROMs or saves. Classify every text/image/font/runtime artifact before editing or
deleting it. Keep active QA stable, preserve lessons before deleting failed
artifacts, use compatibility wrappers before moving public scripts, refresh GUI
upload manifests before pruning payloads, and turn project-specific discoveries
into reusable docs only after removing local paths and copyrighted/project-
specific data. Report progress by track: cleanup/structure, retrospective,
starter-kit extraction, and active QA.
```
