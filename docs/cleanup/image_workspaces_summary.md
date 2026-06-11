# Image Workspaces Summary

Date: 2026-06-12 KST

This summary preserves the cleanup/review lesson from
`confirmed_data/image_inventory/workspaces/` before any future archive or prune
decision.

No files are removed by this document.

## Shape

- Total size: about `86M`
- Purpose: review-unit candidate workspaces for image/text-in-graphics audit.
- Main file types:
  - `918` `.pgm`
  - `918` `.bin`
  - `914` `.png`
  - `17` `.json`
  - `9` `.md`

The folder is mostly generated candidate dumps, exports, PNG previews, and
contact sheets.

## Review Units

| Workspace | Size | Candidate count | Cleanup reading |
| --- | ---: | ---: | --- |
| `01_title_logo_wordmark` | `15M` | 66 | High-value evidence for title logo/wordmark search. |
| `02_title_screen_static_menu_wordmarks` | `11M` | 120 | Title menu candidate evidence; overlaps later title-screen edit-pack work. |
| `03_event_or_cutscene_text_cards` | `18M` | 120 | Largest review unit; likely broad generated candidates, summarize before pruning. |
| `04_dialogue_window_frame_art` | `11M` | 120 | Frame/label art evidence; not automatically editable source. |
| `05_portrait_headshot_assets` | `11M` | 120 | Portrait evidence; mostly diagnostic unless text-bearing assets are found. |
| `06_ui_panel_label_art` | `5.7M` | 120 | UI panel candidate evidence. |
| `07_ui_icon_badge_wordmarks` | `3.6M` | 120 | Small badge/icon candidate evidence. |
| `08_battle_result_or_reward_banners` | `11M` | 120 | Battle result/reward banner candidate evidence. |

## Lesson To Preserve

The workspaces show why image-side localization cannot be driven by static
candidate sheets alone:

- A visible runtime text asset may not be the same as a raw extracted tile sheet.
- Runtime screen-order/tilemap evidence is often needed before an editable source
  can be promoted to the GUI.
- Candidate contact sheets are useful for discovery, but final apply paths should
  be based on item-level source/replacement manifests.

## Current Decision

`workspaces/` remains `RETROSPECTIVE HOLD / KEEP WITH CAUTION`.

It is not directly referenced by the item-level GUI image source manifest, but it
still explains the review-unit approach and may contain useful evidence for
remaining image QA.

## Future Prune Gate

Before pruning this folder:

1. Keep `workspace_contact_sheets.md` and `workspace_contact_sheets.json`, or a
   compact replacement summary.
2. Preserve at least the review-unit lesson above in retrospective docs.
3. Confirm no remaining image QA question needs the raw `dumps/`, `exports/`, or
   `png_exports/` files.
4. Run:

```bash
python3 scripts/build_image_source_manifest.py
python3 scripts/audit_gui_workflow_integrity.py
```

5. Prune one review unit at a time, starting from the lowest priority unit, not
   the whole `workspaces/` folder.
