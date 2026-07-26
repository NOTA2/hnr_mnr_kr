# Bootstrap Baseline Contract

## Project Configuration

Keep these facts in `.gba-localization/project.json`:

- schema version and project name;
- target language;
- source ROM repo-relative path and SHA-256;
- canonical data, workset, asset, evidence, and release directories;
- one canonical command per pipeline action.

Do not store emulator application paths, user home paths, temporary directory
paths, or copied ROM data in the tracked configuration.

## Local Runtime Inventory

Create a manifest entry for each local runtime artifact:

```json
{
  "id": "source-rom",
  "path": "local_roms/source.gba",
  "role": "source_rom",
  "tracked": false,
  "required_by": ["build_review_rom"],
  "keep_reason": "Canonical clean input"
}
```

Use roles such as `source_rom`, `review_rom`, `comparison_rom`, `save`,
`savestate`, `emulator_state`, and `temporary_build`.

## Artifact Ownership

Every large or ambiguous directory should answer:

- What creates it?
- What consumes it?
- Is it canonical, generated, evidence, or cache?
- Can it be regenerated?
- What must be preserved before cleanup?

Do not call an artifact disposable merely because Git ignores it.

## Git Checkpoint Policy

Create a checkpoint after:

- baseline and ignore policy;
- first confirmed extractor;
- first font relocation;
- first image apply path;
- first canonical review ROM;
- each risky cleanup batch;
- each release candidate.

Keep failed experiments out of production commits unless their compact evidence
is intentionally preserved.
