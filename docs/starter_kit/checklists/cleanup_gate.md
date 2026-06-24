# Cleanup Gate

Use this checklist before deleting, untracking, moving, or archiving project
files.

## Classify First

Every cleanup candidate must be classified as one of:

- `KEEP`: active source, build input, GUI state, release artifact, or required
  documentation.
- `KEEP WITH CAUTION`: active-looking, large, mixed-role, or referenced by
  scripts/docs but not fully understood.
- `RETROSPECTIVE KEEP`: useful because it explains a failure mode or project
  decision.
- `UNTRACK`: generated or local artifact that should remain on disk but not in
  Git.
- `DELETE`: reproducible, obsolete, unreferenced, and already summarized if it
  contains a lesson.
- `UNKNOWN`: not safe to touch.

## Required Reads

- Read nearby `README.md` and `*.md` files in the candidate subtree.
- Read the project retention policy and current cleanup plan.
- Read the relevant retrospective note if the candidate is a failed experiment
  or generated analysis output.

## Reference Search

Search exact paths and path stems from:

- active scripts;
- active GUI/workbench JSON;
- project docs;
- source package code;
- release scripts;
- manifest files.

## Validation Commands

Run the project-specific integrity audits before and after a cleanup batch.
Typical gates:

```bash
python3 scripts/audit_gui_workflow_integrity.py
python3 scripts/build_image_source_manifest.py
git ls-files '*.gba' '*.sav' '*.ss' '*.bps' ':!:releases/**/*.bps'
```

## Batch Rules

- Do not mix unrelated cleanup families in one commit.
- Do not use blanket deletion across ignored project data.
- Preserve the lesson before deleting confusing failed artifacts.
- Use wrappers before moving public script paths.
- Prune one image workspace or generated family per commit.
- Commit and push checkpoints for risky cleanup.
