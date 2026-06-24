# Bootstrap Sequence

Use this order when starting another GBA localization project.

## 1. Create Safety Rails

- Add `.gitignore` rules for ROMs, saves, savestates, local emulator state,
  generated workbenches, temporary reports, and patch outputs.
- Add narrow release exceptions only if patch files are intentionally tracked.
- Create `docs/cleanup/safety_gate.md` and `docs/cleanup/retention_policy.md`
  before cleanup starts.

## 2. Establish Artifact Roles

- Create a project config file.
- Create a text source-family matrix.
- Create an image target manifest.
- Create a local runtime artifact matrix.
- Separate canonical data, worksets, GUI state, generated reports, and runtime
  evidence from the beginning.

## 3. Extract Conservatively

- Preserve byte spans, headers, terminators, pointers, and command-stream
  metadata with every text record.
- Reject overlapping candidate text ranges unless manually classified.
- Treat screenshots and savestate captures as evidence until a ROM-backed
  resource and apply path are known.

## 4. Build Workflows Before Bulk Work

- Provide one canonical review ROM build command.
- Provide one GUI/workbench integrity audit.
- Provide one image manifest validation command.
- Provide one patch creation command.
- Keep public command paths stable, or add wrappers before moving scripts.

## 5. Capture Lessons Continuously

- Record recurring failure modes in `docs/retrospective/failure_modes.md`.
- Summarize failed generated artifacts before deleting them.
- Keep raw chat/session logs outside the repo.
