# Cleanup Safety Gate

Date: 2026-06-02 KST

This checklist must run before any deletion, untracking batch, or large structure
change.

## Required Reading

Before touching files, read the current navigation and cleanup docs:

- `README.md`
- `docs/session_start.md`
- `docs/active_task.md`
- `docs/reference_map.md`
- `docs/cleanup/README.md`
- `docs/cleanup/current_state.md`
- `docs/cleanup/execution_plan.md`
- `docs/structure/README.md`
- `docs/structure/migration_map.md`

For a target subtree, also read every tracked `*.md` file inside that subtree
before changing it.

## Required Checks

Run these checks before changing tracked files:

```bash
git status --short --branch
git diff --name-status <baseline>..HEAD
git ls-files '<target>'
rg -n '<target-path-or-folder-name>' README.md docs confirmed_data scripts tools gba_kor_tool analysis
```

For deletion or untracking batches:

```bash
git diff --name-status <baseline>..HEAD | awk '$1=="D" {print $2}'
git diff --name-only --diff-filter=D <baseline>..HEAD
```

If a file is only being untracked with `git rm --cached`, verify that it still
exists locally:

```bash
python3 - <<'PY'
from pathlib import Path
import subprocess
paths = subprocess.check_output(
    ["git", "diff", "--name-only", "--diff-filter=D", "<baseline>..HEAD"],
    text=True,
).splitlines()
missing = [p for p in paths if not Path(p).exists()]
print("git_deleted_count", len(paths))
print("missing_on_disk_count", len(missing))
PY
```

For ROM/savestate safety:

```bash
git diff --name-status <baseline>..HEAD | rg '\.(gba|sav|sgm|state|srm|ips|ups|bps)$|^(D|A|M)\s+(local_roms|patched_roms)/'
```

Expected result for normal cleanup: no ROM, savestate, or patch files.

## Required Decision Rules

- Do not use broad `git clean -fdX`.
- Do not use broad `rm -rf` on project data folders.
- Do not delete or untrack active build inputs just because active GUI JSON does
  not reference them.
- Treat `confirmed_data/image_inventory/` as high risk until image-side QA ends.
- Treat `analysis/generated_workbenches/current_review/prepared.tbl` as active
  while scripts still reference it.
- Commit and push before and after risky cleanup batches.
- If a deletion batch is not clearly reversible, stop and ask first.

## Current Baseline Note

The cleanup baseline before this work was commit `4256e71`. The current pushed
cleanup checkpoint after image inventory risk documentation is `2372d10`.

As of the safety check after `2372d10`:

- Working tree: clean.
- Git-tracked deletions since `4256e71`: `3,847`.
- Deleted-from-Git paths: only generated PGM files under:
  - `analysis/generated_workbenches/inline_event_text_test/`
  - `analysis/generated_workbenches/current_review_entry8_retranslated/`
  - `analysis/generated_workbenches/current_review_entry8_two_only/`
- Missing local files among those untracked PGM paths: `0`.
- Direct Markdown references to those untracked PGM paths: `0`.
- ROM/savestate/patch files changed since baseline: `0`.
- Local `.DS_Store`: `0`.
- Local `__pycache__/`: `0`.
