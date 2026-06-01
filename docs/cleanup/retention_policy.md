# Cleanup Retention Policy

Date: 2026-06-02 KST

The final repo should contain only two kinds of material:

1. files needed to keep the current Korean localization project buildable,
   reviewable, and safe to continue;
2. files needed to explain the project retrospectively and extract a reusable
   GBA localization starter kit.

Everything else is a cleanup candidate, but no candidate is removed until it
passes the safety gate.

## Keep

Keep these in the repo:

- active source-of-truth text, worksets, metadata, font assets, and layout
  manifests;
- active build, apply, audit, GUI, image, runtime, and font scripts;
- active GUI state and data files, especially
  `confirmed_data/localization_workbench/workbench_dataset.json` and
  `confirmed_data/localization_workbench/image_replacements.json`;
- active uploaded image replacement payloads referenced by GUI state;
- current review inputs that scripts still reference, such as
  `analysis/generated_workbenches/current_review/prepared.tbl`;
- small navigation and status docs that let a new session continue the project
  without opening huge JSON files.

## Keep With Caution

Keep these until their active role is proven closed:

- `confirmed_data/image_inventory/`, while image-side QA is still active;
- broad RLE/global extraction reports used as script defaults;
- current runtime evidence used to diagnose remaining QA issues;
- current workbench outputs used by active font or text build scripts.

These can be reduced later, but only after their current role is replaced by a
smaller manifest, summary, or active source file.

## Retrospective Keep

Keep only compact evidence that teaches a reusable lesson:

- summary Markdown explaining a recurring mistake or important decision;
- small structured reports that preserve a traceable conclusion;
- one or two representative examples when a failure mode would be hard to
  understand from text alone.

Do not keep raw Codex session logs in the repo. Use local logs only as read-only
evidence while writing summaries.

## Untrack Candidate

Untrack, rather than delete, when a file is useful on this machine but should not
bloat the shared repo:

- generated glyph PGM/PNG workbench outputs that can be rebuilt;
- local review exports or debug captures that are already summarized;
- intermediate analysis products under ignored folders.

After untracking, verify that the file still exists locally when local
availability matters.

## Delete Candidate

Delete from the repo only when all are true:

- the file is generated, duplicated, obsolete, or superseded;
- no active script, GUI JSON, manifest, Markdown doc, or build command references
  it;
- the retrospective lesson has already been summarized;
- the source-of-truth input or regeneration command is known, or the artifact has
  no remaining diagnostic value;
- the batch is small enough to review clearly in `git diff --name-status`.

## Never Remove Automatically

Do not remove these without an explicit separate decision:

- ROMs, saves, savestates, and patch files;
- active review ROM output paths used by the user for QA;
- active workbench JSON files;
- active uploaded image replacement payloads;
- source scripts used by documented commands;
- files referenced by active docs, manifests, or GUI state;
- broad folders whose only evidence is "not referenced by the GUI".

## Required Checks Per Candidate

Before untracking or deleting a candidate subtree:

1. Read the candidate subtree's tracked `*.md` files.
2. Search references from `README.md`, `docs/`, `confirmed_data/`, `scripts/`,
   `tools/`, `gba_kor_tool/`, and `analysis/`.
3. Check active GUI JSON references when the target is image or workbench data.
4. Check active script defaults and documented commands.
5. Decide `KEEP`, `KEEP WITH CAUTION`, `RETROSPECTIVE KEEP`, `UNTRACK`, or
   `DELETE`.
6. Record the decision in a cleanup audit document.
7. Make a small commit and push after the batch.

If any check is ambiguous, keep the file and document the ambiguity.
