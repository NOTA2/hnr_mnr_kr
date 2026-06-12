# Archive Candidate Scripts

Future home for one-off historical analysis scripts after their lessons are
captured in retrospective docs.

Do not move scripts here just because they look old. Exact filename references,
generated outputs, and retrospective value must be checked first.

## Current Top-Level Candidates

Entry8 analysis and repointing experiments:

- `scripts/analyze_entry8_english_operand_relocation.py`
- `scripts/analyze_entry8_opening_pagination.py`
- `scripts/analyze_entry8_repoint_candidates.py`
- `scripts/analyze_entry8_vm_structure.py`
- `scripts/build_entry8_kss_spacing_candidates.py`
- `scripts/build_entry8_missing_context_units.py`
- `scripts/build_entry8_no_space_slack_candidates.py`
- `scripts/build_entry8_segment_capability_map.py`
- `scripts/build_entry8_structural_repoint_sets.py`
- `scripts/apply_entry8_retranslation_pass.py`
- `scripts/apply_entry8_suspect_retranslation_v2.py`

Image candidate expansion:

- `scripts/build_expanded_nearby_image_candidates.py`

Registry experiments:

- `scripts/registry_b_zp.py`

## Archive Gate

Before moving or deleting any candidate:

1. Search docs and scripts for the exact filename.
2. Identify generated outputs that depend on it.
3. Preserve the lesson in `docs/retrospective/` if it explains a repeated
   mistake or useful dead end.
4. Keep the top-level path as a wrapper if any active command or doc still uses
   it.
