# Image Text Inventory

- status: `in_progress`
- last_updated: `2026-05-18`

## Confirmed Non-Image Text Contexts

- `startup_intro_card`: Handled as fixed-slot text records in startup_intro_texts.json, not baked image text.
- `dialogue_box_payloads`: Entry8 and Registry D dialogue strings are extracted as script records; portraits are separate image assets.
- `world_map_location_labels`: Location names are extracted in location_texts.json and rendered by the world-map text path.
- `save_menu_prompts`: Save/menu prompts are extracted as 01 FF command-stream records, not image-baked labels.
- `credits_strings`: Credits are extracted as padded plain text records, not confirmed image text.

## Review Units

- `title_logo_wordmark` (`pending_review`, `order=1`)
  Main title/logo style text is not mapped by current canonical extracted text sources.
  Treat as a concrete review unit rather than a generic bucket.
- `title_screen_static_menu_wordmarks` (`pending_review`, `order=2`)
  Static title-screen menu labels and mode wordmarks may be image-backed.
  No canonical extracted source currently covers title-screen wordmark art.
- `event_or_cutscene_text_cards` (`pending_review`, `order=3`)
  Story/event presentation cards or overlays are a higher-value image-text candidate than generic event illustrations.
  Keep separate from dialogue payloads, which are already confirmed non-image text.
- `dialogue_window_frame_art` (`review_started`, `order=4`)
  Dialogue text itself is extracted text, but the window frame art is a distinct visual asset family.
  This unit matters for localization QA even if it contains no baked text.
- `portrait_headshot_assets` (`review_started`, `order=5`)
  Portraits are confirmed image assets.
  Speaker text itself is not baked into portraits, but portrait coverage matters for dialogue QA and future image tasks.
- `ui_panel_label_art` (`pending_review`, `order=6`)
  Panels, tabs, or framed UI labels that may contain baked text should be reviewed as a distinct unit.
  Keep separate from plain extracted save/menu/system strings.
- `ui_icon_badge_wordmarks` (`pending_review`, `order=7`)
  Icon/badge-sized wordmarks should be reviewed separately from larger UI panels.
  Useful to keep isolated because replacement strategy is likely different from panel art.
- `battle_result_or_reward_banners` (`pending_review`, `order=8`)
  Result/reward banners are plausible baked-text candidates in battle or post-battle presentation.
  Separate from dialogue and term-description sources, which are already extracted text.

## Operational Reading

- Image text inventory is now started as a separate audit track.
- Several important text contexts are already confirmed to be non-image text and should not block translation.
- The remaining work is asset-side review of concrete review_units rather than reopening canonical text extraction.
