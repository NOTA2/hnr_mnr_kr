# Image Text Inventory

- status: `started`
- last_updated: `2026-05-17`

## Confirmed Non-Image Text Contexts

- `startup_intro_card`: Handled as fixed-slot text records in startup_intro_texts.json, not baked image text.
- `dialogue_box_payloads`: Entry8 and Registry D dialogue strings are extracted as script records; portraits are separate image assets.
- `world_map_location_labels`: Location names are extracted in location_texts.json and rendered by the world-map text path.
- `save_menu_prompts`: Save/menu prompts are extracted as 01 FF command-stream records, not image-baked labels.
- `credits_strings`: Credits are extracted as padded plain text records, not confirmed image text.

## Review Buckets

- `title_logo_and_static_title_graphics` (`pending_review`)
  Potential baked-text candidate bucket.
  No canonical extracted source currently maps this bucket.
- `event_illustration_overlays_or_cutscene_cards` (`pending_review`)
  Potential baked-text candidate bucket for story/event presentation assets.
  Not yet inventoried structurally.
- `ui_icons_badges_or_panels_with_embedded_labels` (`pending_review`)
  Potential baked-text candidate bucket for non-dialogue UI art.
  Needs later asset review.
- `portrait_assets` (`review_started`)
  Portraits are confirmed image assets.
  Current evidence suggests speaker text itself is not baked into portraits, but portrait/image inventory still matters for localization QA.

## Operational Reading

- Image text inventory is now started as a separate audit track.
- Several important text contexts are already confirmed to be non-image text and should not block translation.
- The remaining work is asset-side review of review_buckets rather than reopening canonical text extraction.
