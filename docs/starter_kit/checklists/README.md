# Starter Kit Checklists

These checklists are project-neutral gates extracted from the current GBA
localization project. They are meant to be copied into a new project before any
ROM, text, font, image, or cleanup work starts.

Use them as operating gates, not as historical notes:

- `session_start.md`: first checks at the start of every agent session.
- `cleanup_gate.md`: required checks before deleting, untracking, or moving
  project files.
- `release_gate.md`: release packaging checks that prevent ROM leakage and
  broken patch artifacts.

The current project-specific evidence behind these rules lives in
`docs/retrospective/` and `docs/cleanup/`.
