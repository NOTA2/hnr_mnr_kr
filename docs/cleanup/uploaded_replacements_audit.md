# Uploaded Replacements Audit

Date: 2026-06-02 KST

This audit covers
`confirmed_data/localization_workbench/uploaded_image_replacements/`.

## Summary

- Payload files on disk, excluding generated manifest: `365`
- Files on disk including README and manifest: `366`
- Size on disk: about `2.9M`
- Unique active GUI references from `workbench_dataset.json` and
  `image_replacements.json`: `340`
- Missing active references by Python `Path.exists()`: `0`
- Already tracked payload files in this folder before the upload audit: `255`
- Newly visible untracked files after manifest generation: `111`
- Active referenced payload files on disk: `328`
- Payload files not directly referenced by active GUI JSON: `37`

## Interpretation

This folder is small and active enough that ignoring it is risky. It is not just
throwaway browser upload cache: active replacement state references many of these
files directly.

Part of this folder was already tracked despite the folder-level ignore. The
cleanup pass changed `.gitignore` so the remaining files can also be tracked.
This does not stage files by itself, but it makes the active replacement payloads
visible to Git and prevents future cleanup from silently omitting them.

A generated manifest now records active-reference status:

- `confirmed_data/localization_workbench/uploaded_image_replacements/manifest.json`

## Unicode Filename Note

A byte-level shell comparison showed `12` apparent missing paths, but Python
`Path.exists()` reported `0` missing active references. The mismatch comes from
Korean filenames that differ by Unicode normalization form on macOS, for example
composed vs decomposed Hangul.

Future stable replacement assets should prefer ASCII filenames or generated IDs.
Korean display labels should live in JSON metadata, not in the only filename that
active build logic depends on.

## Next Action

Before deletion:

1. Review the generated manifest.
2. Decide whether to keep all files or prune unreferenced payloads in a later
   cleanup batch.
3. For any final user-supplied payload, consider promoting it into the matching
   `confirmed_data/image_inventory/edit_packs/...` folder.
4. After promotion/pruning, rerun active reference tracing and require zero
   missing paths.
