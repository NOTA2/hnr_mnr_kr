# GUI Workflow Safety

Date: 2026-06-12 KST

This document protects the GUI-facing workflow during cleanup.

The user-facing features that must stay intact are:

- GUI item/category display;
- text apply / review ROM rebuild;
- fast text apply using the prepared font cache;
- image replacement apply;
- current review ROM path tracking;
- release patch generation.

## Safety Command

Run this before any cleanup batch that touches `scripts/`, `tools/`,
`confirmed_data/localization_workbench/`, `confirmed_data/image_inventory/`,
`analysis/generated_workbenches/current_review/`, `patched_roms/current_review/`,
or `releases/`:

```bash
python3 scripts/audit_gui_workflow_integrity.py
```

This audit is read-only. It checks:

- required GUI JSON files parse;
- workbench image replacement items still match dataset items;
- image source/preview/replacement paths exist;
- current review ROM and source ROM paths exist locally;
- fast text apply prerequisites exist;
- critical GUI/build/apply/patch scripts have valid Python syntax;
- BPS patch generation passes an in-memory roundtrip;
- `.gitignore` still blocks ROM/save/patch files outside release exceptions.

## Latest Result

Latest local run:

```text
gui workflow integrity: ok
- workbench_items: 14017
- workbench_categories: 21
- workbench_image_items: 2406
- image_replacement_items: 2406
- edited_image_replacements: 211
- bps_roundtrip_bytes: 33
```

## Cleanup Rule

If this audit fails after a cleanup step, stop and fix the broken path or restore
the moved/deleted file before continuing.
