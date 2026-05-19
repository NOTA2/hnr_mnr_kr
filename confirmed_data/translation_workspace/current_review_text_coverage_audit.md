# Current Review Text Coverage Audit

- Last updated: `2026-05-19T09:13:34.567758+00:00`
- Extracted records: `11440`
- Workbench text records: `11497`
- Current review translations: `11418`
- Apply actions: `{'entry8_segment0_in_place_length_preserved': 241, 'entry8_boundary_crossing_in_place_length_preserved': 21, 'entry8_in_place_length_preserved': 6190, 'entry8_segment_repointed': 3913, 'packed_repointed': 244, 'in_place': 771, 'repointed': 22}`
- Untranslated Japanese candidates, excluding locked ??????: `0`

## Reading

- ??????/????? 형태의 잠금 또는 미확인 표시는 원본 상태로 간주해 미번역 후보에서 제외한다.
- `・`, `・・・`, `ー` 같은 보존 대상 일본식 기호는 일본어 잔존으로 보지 않는다. 실제 가나/한자만 후보로 잡는다.
- skipped_no_pointer 는 추출은 되었지만 원래 슬롯을 초과했고, 이 레코드에 대한 직접 포인터를 찾지 못해 ROM 확장 repoint 가 불가능했던 항목이다.

## Source Summary

| Source | Extracted | Workbench | Review translations | Apply actions |
|---|---:|---:|---:|---|
| ability_texts | 413 | 413 | 413 | `{'in_place': 413}` |
| battle_texts | 104 | 104 | 77 | `{'in_place': 77}` |
| choice_yes_no_texts | 0 | 16 | 16 | `{'in_place': 16}` |
| credits_texts | 10 | 10 | 10 | `{'in_place': 10}` |
| duplicate_text_slots | 28 | 28 | 28 | `{'in_place': 28}` |
| inline_event_texts | 0 | 41 | 41 | `{'in_place': 41}` |
| item_texts | 49 | 49 | 49 | `{'in_place': 35, 'repointed': 14}` |
| location_texts | 10 | 10 | 10 | `{'in_place': 10}` |
| material_texts | 44 | 44 | 44 | `{'in_place': 44}` |
| registry_a_entry12_texts | 22 | 22 | 22 | `{'in_place': 22}` |
| registry_a_entry8_prefixed_texts | 10417 | 10417 | 10365 | `{'entry8_segment0_in_place_length_preserved': 241, 'entry8_boundary_crossing_in_place_length_preserved': 21, 'entry8_in_place_length_preserved': 6190, 'entry8_segment_repointed': 3913}` |
| registry_a_map_labels | 48 | 48 | 48 | `{'in_place': 48}` |
| registry_d_fc_script_texts | 244 | 244 | 244 | `{'packed_repointed': 244}` |
| save_menu_texts | 12 | 12 | 12 | `{}` |
| startup_intro_texts | 4 | 4 | 4 | `{}` |
| system_messages | 10 | 10 | 10 | `{'in_place': 8, 'repointed': 2}` |
| ui_skill_texts | 25 | 25 | 25 | `{'in_place': 19, 'repointed': 6}` |

## Skipped Examples

## Untranslated Japanese Candidates
