---
name: gba-localization-lifecycle
description: Orchestrate a complete, resumable GBA game localization lifecycle across repository bootstrap, ROM analysis, text extraction, Korean font and encoding work, image localization, translation, ROM building, gameplay QA, patch release, cleanup, and retrospective capture. Use when starting a new GBA localization project, resuming one after a break, deciding the next phase, checking cross-phase readiness, or coordinating the other gba-localization-* skills.
---

# GBA Localization Lifecycle

Use this skill as the control plane for the suite. Keep project state in the
target repository so another Codex session can resume without relying on chat
history or machine-local paths.

## Start Or Resume

1. Locate the repository root and inspect Git status before changing files.
2. Look for `.gba-localization/project.json` and
   `.gba-localization/lifecycle.json`.
3. If they are absent, read [phase-contracts.md](references/phase-contracts.md)
   and [safety-rules.md](references/safety-rules.md), then initialize:

   ```bash
   python3 <this-skill-dir>/scripts/lifecycle.py init \
     --root <repo-root> \
     --name <project-name> \
     --source-rom local_roms/source.gba
   ```

4. Review `.gba-localization/gitignore.fragment`; merge its rules into the
   repository `.gitignore` deliberately. Do not overwrite existing rules.
5. If state exists, run:

   ```bash
   python3 <this-skill-dir>/scripts/lifecycle.py check --root <repo-root>
   python3 <this-skill-dir>/scripts/lifecycle.py status --root <repo-root>
   ```

6. Read only the current phase evidence and blockers. Load older analysis or
   chat-derived retrospectives only when the current problem overlaps a known
   failure.

## Claim Mutating Work

Before editing canonical data, GUI state, shared image parents, or ROM build
outputs, acquire one phase claim:

```bash
python3 <this-skill-dir>/scripts/lifecycle.py claim \
  --root <repo-root> \
  --phase images \
  --owner <task-or-session-id>
```

If another unexpired owner holds the claim, stop mutating and coordinate or use
an isolated worktree whose local build outputs cannot collide. Release the claim
after the phase checkpoint:

```bash
python3 <this-skill-dir>/scripts/lifecycle.py release-claim \
  --root <repo-root> \
  --owner <task-or-session-id>
```

## Route Work

Use the phase skill named by `status`:

| Phase | Skill |
| --- | --- |
| `bootstrap` | `$gba-localization-bootstrap` |
| `rom_analysis` | `$gba-localization-rom-analysis` |
| `text` | `$gba-localization-text` |
| `font` | `$gba-localization-font` |
| `images` | `$gba-localization-images` |
| `translate` | `$gba-localization-translate` |
| `build_qa` | `$gba-localization-build-qa` |
| `release` | `$gba-localization-release` |

`text`, `font`, and `images` may progress in parallel after ROM analysis.
Translation and build QA form an iterative loop. A gameplay finding may move an
earlier phase back to `in_progress`; record the regression instead of hiding it.

## Checkpoint A Phase

Update the repository artifacts first. Then record status with existing,
repo-relative evidence paths:

```bash
python3 <this-skill-dir>/scripts/lifecycle.py checkpoint \
  --root <repo-root> \
  --phase text \
  --status ready \
  --evidence .gba-localization/manifests/text_sources.json \
  --note "Known text families extracted; runtime coverage remains in QA"
```

Use `blocked` only with a concrete blocker:

```bash
python3 <this-skill-dir>/scripts/lifecycle.py checkpoint \
  --root <repo-root> \
  --phase font \
  --status blocked \
  --blocker "Renderer slot addressing is not yet proven in runtime"
```

Never mark `ready` or `complete` from confidence alone. The lifecycle tool
requires dependencies, evidence paths, and phase-specific manifest minimums,
but the phase skill remains responsible for deeper semantic validation.

## Operating Rules

- Keep ROMs, saves, savestates, emulator state, and local review builds ignored.
- Keep active inputs and commands inside the repository. Treat external paths
  as user-provided inputs or historical provenance, never hidden dependencies.
- Preserve control bytes, offsets, counts, pointers, palette provenance, and
  regeneration commands alongside human-facing assets.
- Separate canonical data, generated views, GUI/cache state, runtime evidence,
  uploaded payloads, and final release artifacts.
- Run mutating build steps sequentially when output order affects correctness.
- Allow only one writer for canonical data and shared build outputs.
- Make a Git checkpoint before risky relocation, bulk apply, cleanup, or release
  work. Keep each checkpoint narrow and verified.
- Do not delete evidence until its lesson and replacement rule are captured.

## Report Progress

Report each phase independently with its status, evidence, and blocker count.
Do not compress the whole project into one percentage that hides unfinished
font, image, runtime, or release work.
