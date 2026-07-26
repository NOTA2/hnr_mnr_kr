# Lifecycle Phase Contracts

## Contents

1. Shared status model
2. Bootstrap
3. ROM analysis
4. Text
5. Font
6. Images
7. Translation
8. Build and QA
9. Release

## Shared Status Model

- `not_started`: no reliable phase work exists.
- `in_progress`: evidence is being produced or revised.
- `blocked`: a concrete missing fact, capability, input, or decision prevents
  meaningful progress.
- `ready`: the phase can support downstream work, while iterative QA may still
  return findings.
- `complete`: the release scope has passed its final phase gate.

Every `ready` or `complete` phase needs at least one existing repo-relative
evidence path. Store uncertainties and unsupported areas explicitly.

Acquire the phase claim before mutating canonical state. A claim expires, but an
expired claim is still a signal to inspect Git status and output hashes before
continuing.

The lifecycle tool also enforces these machine-readable minimums:

| Phase | Automated minimum |
| --- | --- |
| `bootstrap` | Source ROM exists, SHA-256 matches, path is ignored, and no runtime file is tracked. |
| `rom_analysis` | Artifact inventory is non-empty and every item has an ID, role, and confidence. |
| `text` | At least one family defines ID, record type, encoding, and apply capabilities. |
| `font` | Code space, storage, renderer, atlas, and passing runtime tests are recorded. |
| `images` | Inventory is complete; final replacements carry rebuild fields. |
| `translate` | Canonical source and release-ready workset summaries exist. |
| `build_qa` | Build ID exists and every QA case passed or was explicitly waived. |
| `release` | Patch metadata is complete and round-trip verification passed. |

These checks are minimums, not proof that the phase is semantically correct.
The phase skill's exit gate still applies.

## Bootstrap

Required evidence:

- source ROM identity and SHA-256 without tracking the ROM;
- ROM/save/savestate ignore policy;
- repository-relative artifact paths;
- local runtime artifact inventory;
- current Git baseline and release patch policy.

Exit gate: no forbidden runtime artifact is tracked, the source ROM path is
ignored, and another session can identify the canonical inputs.

## ROM Analysis

Required evidence:

- ROM header and size facts;
- resource and pointer hypotheses labeled by confidence;
- experiment log with command, input hash, output, and conclusion;
- artifact inventory separating confirmed sources from discovery evidence.

Exit gate: the next domain probes have bounded targets and no guessed pointer or
compression rule has been promoted to a global invariant.

## Text

Required evidence:

- source-family manifest;
- canonical extracted records with stable IDs and byte spans;
- terminator/header/control-byte policy per family;
- overlap and coverage audits;
- apply capability per family or segment;
- workset generation command.

Exit gate: extraction is reproducible, structural metadata survives the
round-trip, and unsupported apply paths are protected.

## Font

Required evidence:

- codepoint map and encoding policy;
- glyph storage capacity and relocation facts;
- mirror-pointer or table updates where relevant;
- production atlas provenance and license;
- representative runtime renderer tests.

Exit gate: static previews and runtime addressing both pass, and unrelated UI
fonts remain intact.

## Images

Required evidence:

- image target manifest and artifact roles;
- ROM resource, compression, tile order, screen-order map, and palette source;
- 1x editable source and reversible apply path;
- runtime verification for final replacements;
- current upload/reference manifest when a GUI accepts files.

Exit gate: every final replacement is rebuildable from tracked source assets, or
the inventory explicitly records that no image localization is in scope.

## Translation

Required evidence:

- canonical worksets linked to text-family records;
- terminology and style policy;
- source-of-truth and field priority;
- draft/review/lock states;
- consistency, width, punctuation, and untranslated-text audits.

Exit gate: reviewed content can be regenerated without treating GUI state as the
canonical source.

## Build And QA

Required evidence:

- one canonical sequential review-build command;
- build manifest with source and output hashes;
- apply report by source family and image target;
- smoke, representative, edge-case, and regression QA cases;
- reproducible bug records with build ID and runtime location.

Exit gate: a clean build reproduces the reviewed ROM and required gameplay paths
pass without unclassified corruption.

## Release

Required evidence:

- patch path and format;
- expected source and output hashes;
- successful patch round-trip;
- QA scope, known issues, asset licenses, and patch instructions;
- cleanup retention decisions and retrospective updates.

Exit gate: the release contains no ROM, is reproducible from the documented
source revision, and can be handed to a new user without local machine context.
