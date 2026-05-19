# Runtime Family Focus Report

- structural extraction status: `closed_for_known_sources`

## High priority

- `registry_d_fc_script_texts` -> `registry_d_fc_stop_script_line` (risk=medium, candidate=shared_text_object_r3_20)
- `registry_a_entry8_prefixed_texts` -> `entry8_prefixed_01ff_script_line` (risk=high, candidate=shared_text_object_r3_20)

## Medium priority

- `system_messages` -> `system_messages_plain_newline_00` (risk=medium)
- `save_menu_texts` -> `save_menu_prefixed_01ff` (risk=medium)
- `battle_texts` -> `term_description_plain_00_optional_0b` (risk=low)
- `ability_texts` -> `term_description_plain_00_optional_0b` (risk=low)
- `material_texts` -> `term_description_plain_00_optional_0b` (risk=low)

## Low priority

- `ui_skill_texts` -> `ui_or_item_plain_00_record` (risk=low)
- `item_texts` -> `ui_or_item_plain_00_record` (risk=low)
- `registry_a_entry12_texts` -> `ui_or_item_plain_00_record` (risk=low)
- `credits_texts` -> `credits_padded_plain_00_record` (risk=low)

## Reading

- High priority items are runtime QA focus areas, not automatically byte-slot blockers.
- `registry_d_fc_script_texts` supports packed relocation, so translate naturally and validate line width/page-flow visually.
- `registry_a_entry8_prefixed_texts` is still a counted script family without equivalent packed relocation, so keep it concise.
- Medium/low groups are structurally extracted and can already be translated with source-family-specific constraints.
- `system_messages` / `save_menu` are operationally bounded: residual uncertainty remains, but they are no longer treated as major runtime blockers.
- This report is meant to keep runtime-family work focused instead of treating all unresolved families as equally risky.
