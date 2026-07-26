---
name: gba-localization-bootstrap
description: Establish the safe, reproducible baseline for a GBA localization repository, including ROM identity, Git ignore policy, artifact roles, repo-relative paths, local runtime inventory, canonical commands, and checkpoint rules. Use at the start of a new project, when adopting an existing localization repo, or when lifecycle checks report bootstrap and portability problems.
---

# GBA Localization Bootstrap

Create a baseline that makes later experimentation recoverable and portable.
Do not begin ROM mutation in this phase.

## Read State

1. Run the lifecycle `check` and `status` commands.
2. Read `.gba-localization/project.json` and the current Git status.
3. Read repository-level `README.md`, `AGENTS.md`, and nearby safety docs if
   present. Do not load every historical analysis file.
4. Read [baseline-contract.md](references/baseline-contract.md).
5. Acquire the `bootstrap` lifecycle claim before editing repository policy.

## Establish The Baseline

1. Confirm the intended repository root. Reject active inputs that resolve
   outside it.
2. Identify the source ROM by repo-relative local path, byte size, and SHA-256.
   Never commit or print ROM content.
3. Merge the relevant rules from `.gba-localization/gitignore.fragment` into
   `.gitignore` without removing existing rules.
4. Verify tracked files contain no ROM, save, savestate, or emulator state.
5. Classify directories and files by role:
   - canonical input;
   - generated output;
   - GUI/cache state;
   - runtime evidence;
   - local ignored artifact;
   - release artifact;
   - retrospective evidence.
6. Record every local ROM, review ROM, save, savestate, and comparison build in
   a repo-tracked manifest that stores paths and roles, never file contents.
7. Fill repository-relative path and command placeholders in
   `.gba-localization/project.json`.
8. Record the release patch tracking policy. Keep patch files ignored unless a
   narrow release exception is intentional.

## Verify

Run:

```bash
git status --short
git ls-files
python3 <lifecycle-skill-dir>/scripts/lifecycle.py check --root <repo-root>
```

Also verify the source ROM with `git check-ignore --no-index` and confirm its
computed hash matches `project.json`.

## Exit Gate

Mark `bootstrap` as `ready` only when:

- source ROM identity is stable;
- forbidden runtime files are untracked and ignored;
- all active project paths are repo-relative;
- artifact roles and local runtime inputs are documented;
- canonical command slots exist, even if later phases have not implemented them.

Use `.gba-localization/project.json`, the runtime artifact manifest, and the ignore
policy as evidence. Commit this baseline before risky analysis begins.
Release the lifecycle claim after the checkpoint.
