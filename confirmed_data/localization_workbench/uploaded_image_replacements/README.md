# Uploaded Image Replacements

This folder stores image replacement payloads uploaded through the localization
workbench.

## Role

- Active GUI/build state may reference files here through
  `confirmed_data/localization_workbench/image_replacements.json`.
- These files are not temporary browser cache when they are referenced by active
  JSON. They are part of the current localization state.
- Keep this folder repo-local. Do not depend on `/Users/user/Downloads`, temp
  folders, or Codex session logs for replacement payloads.

## Cleanup Rule

- Do not delete a file from this folder unless active reference tracing confirms
  that no current GUI/build JSON points to it.
- Prefer ASCII filenames for new stable assets. Some existing Korean filenames
  differ only by Unicode normalization form on macOS, which can make byte-level
  path comparisons look missing even when `Path.exists()` succeeds.
- If an uploaded file becomes the final source of truth for an edit pack, consider
  promoting or copying it into the relevant `confirmed_data/image_inventory`
  edit-pack folder during a later cleanup batch.

