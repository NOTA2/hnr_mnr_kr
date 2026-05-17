# Runtime Dialogue Family Report

- last_updated: `2026-05-17`

## entry8_singleline_counted_dialogue_profile

- source_group: `registry_a_entry8_prefixed_texts`
- record family: `entry8_prefixed_01ff_script_line`
- runtime candidate: `shared_text_object_r3_20`
- record_count: `9823`
- max_chars: `19`
- p95_chars: `14`
- newline_record_count: `0`
- max_explicit_newlines: `0`
- max_rendered_lines_if_newline_split: `1`

- Payloads are overwhelmingly short counted lines and currently contain no explicit newline bytes in extracted text.
- The dominant remaining uncertainty is not record boundary, but how these short lines chain into visible dialogue boxes/pages at runtime.
- Until runtime page-flow is visually locked, translations should assume concise single-line records that may be sequenced externally by script controls.

## registry_d_multiline_fc_dialogue_profile

- source_group: `registry_d_fc_script_texts`
- record family: `registry_d_fc_stop_script_line`
- runtime candidate: `shared_text_object_r3_20`
- record_count: `244`
- max_chars: `90`
- p95_chars: `38`
- newline_record_count: `166`
- max_explicit_newlines: `6`
- max_rendered_lines_if_newline_split: `7`

- Many payloads already contain explicit newlines, so part of the visible box/page flow is embedded directly in the extracted text rather than only in adjacent controls.
- The source still shares the same r3=20 candidate renderer family, but its runtime behavior is materially different from entry8 because multiline payloads are common.
- Until runtime page-turn behavior is visually locked, translators should preserve existing newlines and avoid inventing extra ones.

## Operational Reading

- High-priority dialogue runtime work is no longer a single unresolved blob.
- It is narrowed to two profiles on the shared r3=20 candidate family: single-line counted script lines (entry8) and multiline FC-delimited dialogue payloads (Registry D).
- This reduces the remaining runtime blocker to visual/page confirmation rather than record-boundary discovery.
