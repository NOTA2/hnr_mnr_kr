# Cleanup Sequence

Use this order when a GBA localization project reaches late-stage QA.

## 1. Freeze The Safety Boundary

- Identify active source ROM, current review ROM, release patch policy, GUI
  state, and build commands.
- Confirm ROMs/saves/savestates are not tracked.
- Run active GUI/build/image manifest audits.

## 2. Classify Before Moving

- Build a top-level role inventory.
- Mark active source, active state, derived indexes, runtime evidence,
  retrospective hold areas, local-only paths, and deletion candidates.
- Do not rename canonical data folders during active QA.

## 3. Reduce Generated Bulk Carefully

- Preserve compact summaries for failed or confusing artifacts.
- Keep generator scripts and active input manifests.
- Delete or untrack only reproducible generated output whose lesson has already
  been captured.

## 4. Structure Scripts With Wrappers

- Create future group directories first.
- Move one low-risk implementation as a pilot.
- Keep old public paths as wrappers.
- Verify old and new commands.
- Avoid starting with GUI, ROM build, image apply, patch generation, font, or
  runtime scripts during active QA.

## 5. Prune Image Data Last

- Regenerate active image source manifests.
- Require zero missing paths.
- Summarize each review workspace before pruning.
- Promote final uploaded payloads into durable edit packs before deleting upload
  cache-like folders.

## 6. Commit In Checkpoints

- Commit each cleanup family separately.
- Push risky checkpoints.
- Keep final reports short enough for a later agent to resume without rereading
  large generated data.
