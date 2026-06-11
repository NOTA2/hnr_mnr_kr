# Text Layout Metadata Candidate Audit

- generated_at: `2026-06-04T00:36:04`
- source_rom: `Hagane no Renkinjutsushi - Meisou no Rondo (Japan).gba`

This audit searches extracted text records for nearby signed 32-bit fields
that match `field_value = display_units(original_text) * 6 + constant`.
Strict candidates still need runtime confirmation before applying patches.

## Strict Candidates

| source_group | field_delta | formula | record_count | stride | evidence |
|---|---:|---|---:|---:|---|
| location_texts | `0x14` | `value = display_units(text) * 6 + -104` | 10 | 44 | small=1.0, constant=1.0 |

## Suspicious Fields

- None

## Source Group Summary

| source_group | records | common_stride | candidates |
|---|---:|---:|---:|
| ability_texts | 413 | 17 | 0 |
| battle_texts | 104 | 3 | 0 |
| credits_texts | 28 | 88 | 0 |
| duplicate_text_slots | 28 | 80 | 0 |
| item_texts | 49 | 12 | 0 |
| location_texts | 10 | 44 | 1 |
| material_texts | 44 | 32 | 0 |
| registry_a_entry12_texts | 22 | 80 | 0 |
| registry_a_entry8_prefixed_texts | 10417 | 30 | 0 |
| registry_a_map_labels | 70 | 4676 | 0 |
| registry_d_fc_script_texts | 245 | 58 | 0 |
| save_menu_prefixed_texts | 12 | 26 | 0 |
| startup_intro_texts | 4 | 14 | 0 |
| system_messages | 10 | 44 | 0 |
| ui_skill_texts | 25 | 32 | 0 |
| ui_status_texts | 2 | 92404 | 0 |
