# Image Workspace Prune Readiness

Date: 2026-06-12 KST

This document ranks the remaining
`confirmed_data/image_inventory/workspaces/` review units after the first
per-unit prune. It exists to prevent image cleanup from becoming ad hoc while
gameplay QA is still active.

## Baseline

- `workspaces/`: about `82M`
- Active GUI image source manifest records: `2,406`
- Active GUI image source manifest missing paths: `0`
- `07_ui_icon_badge_wordmarks` is already pruned to summary-only.
- None of the remaining workspace folders are direct item-level GUI source
  families, but several are still high-value review evidence.

## Readiness Table

| Workspace | Size | Files | Priority | Localization needed | State | Decision |
| --- | ---: | ---: | --- | --- | --- | --- |
| `01_title_logo_wordmark` | `15M` | 218 | high | yes | active scaffold | Keep. Do not prune during QA. |
| `02_title_screen_static_menu_wordmarks` | `11M` | 364 | high | yes | active scaffold | Keep. Do not prune during QA. |
| `03_event_or_cutscene_text_cards` | `18M` | 372 | high | no/pending | active scaffold | Hold. Summarize before any later prune. |
| `04_dialogue_window_frame_art` | `11M` | 364 | medium | no/pending | review started | Hold. UI frame evidence may matter for QA. |
| `05_portrait_headshot_assets` | `11M` | 364 | medium | no | review started | Hold. Portrait evidence is useful context even if not text-bearing. |
| `06_ui_panel_label_art` | `5.7M` | 364 | medium | no/pending | active scaffold | Hold. UI panel labels can still become text-bearing cases. |
| `07_ui_icon_badge_wordmarks` | `4.0K` | 1 | low | no | pruned summary | Done. Summary-only. |
| `08_battle_result_or_reward_banners` | `11M` | 364 | medium | no/pending | active scaffold | Hold. Battle/result text may appear late in QA. |

## Current Decision

No additional workspace subtree should be pruned immediately.

The next prune candidate must first satisfy all of these:

1. A compact per-unit `README.md` preserves candidate count, representative
   offsets, role, and regeneration commands.
2. `rg` finds no active GUI/build/apply references to files that will be
   removed.
3. `python3 scripts/build_image_source_manifest.py` reports `missing paths: 0`.
4. `python3 scripts/audit_gui_workflow_integrity.py` passes.
5. The unit is not a high-priority runtime-visible title/menu case.

## Practical Next Step

Keep the remaining seven units as `KEEP WITH CAUTION` while gameplay QA is
ongoing. If more space reduction is needed later, start with a documentation-only
summary for `06_ui_panel_label_art` or `05_portrait_headshot_assets`, then
re-run the safety gates before deleting generated artifacts.
