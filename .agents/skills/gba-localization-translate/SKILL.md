---
name: gba-localization-translate
description: Run a traceable GBA translation workflow from canonical text records through terminology, context preparation, drafting, human review, locking, consistency audits, layout checks, GUI synchronization, and merge-safe worksets. Use when preparing translation batches, coordinating agents or reviewers, fixing awkward Korean, resolving inconsistent terms, preventing stale workbench data, or deciding which translation field the ROM build should apply.
---

# GBA Translation Workflow

Keep translation ownership explicit. Canonical worksets own reviewed text; GUI
datasets and agent outputs are replaceable views or imports.

## Prepare

1. Require `text` to be ready. Read the text-family manifest and workset
   generation command.
2. Read `.gba-localization/manifests/translation.json`.
3. Read [workset-contract.md](references/workset-contract.md).
4. Define terminology, names, register, punctuation, spacing, control tokens,
   and family-specific layout policies before bulk translation.
5. Acquire the `translate` lifecycle claim before changing canonical worksets.

## Build Worksets

1. Generate worksets from canonical text records using stable IDs.
2. Carry source family, layout profile, byte constraints, structural metadata
   references, context, and review state.
3. Split large worksets into non-overlapping stable ranges or IDs. Record the
   exact source revision used by each worker.
4. Never infer a speaker as fact from weak dialogue state. Preserve uncertain
   speaker or portrait state as context evidence, not a required translation
   authority.

## Translate And Review

Use states such as:

- `untranslated`;
- `agent_draft`;
- `translated`;
- `reviewed`;
- `manual_locked`;
- `blocked_context`;
- `excluded`.

Keep draft, translation, review notes, and lock state in separate fields.
Preserve tokens and control markers exactly.

Review for:

- meaning and tone in local context;
- terminology and name consistency;
- repeated source strings with intentionally contextual exceptions;
- Korean spacing and punctuation;
- line breaks, page flow, width, and byte constraints per source family;
- untranslated source-language text;
- accidental edits to locked records.

## Merge And Synchronize

1. Import by stable ID and verify the source fingerprint before overwriting.
2. Reject unknown IDs, duplicate IDs, stale source text, and overlapping worker
   batches.
3. Use this apply priority unless the project documents another explicit one:
   `manual_locked_translation`, `translation`, `agent_draft`, `original`.
4. Regenerate GUI datasets from canonical worksets.
5. Restart or explicitly reload the GUI after schema or dataset changes.
6. Verify disk state, GUI-visible state, and ROM-applied state independently.

## Exit Gate

Mark `translate` as `ready` when release-scope worksets are reviewed or
explicitly excluded, locks and field priority are enforced, consistency and
layout audits pass, and the canonical data can regenerate the workbench without
losing newer translations. Release the lifecycle claim after checkpointing the
phase.
