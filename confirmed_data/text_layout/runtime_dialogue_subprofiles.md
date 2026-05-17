# Runtime Dialogue Subprofiles

- last_updated: `2026-05-18`

## Entry8

- `chain_heavy_singleline`: `42` clusters
- `chain_moderate_singleline`: `26` clusters
- `mostly_standalone_singleline`: `4` clusters

### Entry8 Focus Clusters

- cluster `38` `central`: `records=786`, `runs=589`, `multi_runs=131`, `max_run=11`
- cluster `18` `east_city`: `records=523`, `runs=314`, `multi_runs=91`, `max_run=12`
- cluster `61` `military`: `records=483`, `runs=274`, `multi_runs=83`, `max_run=15`
- cluster `55` `east_city`: `records=438`, `runs=342`, `multi_runs=80`, `max_run=5`
- cluster `70` `military`: `records=257`, `runs=113`, `multi_runs=46`, `max_run=12`
- cluster `26` `central`: `records=274`, `runs=167`, `multi_runs=45`, `max_run=37`
- cluster `20` `central`: `records=325`, `runs=138`, `multi_runs=44`, `max_run=24`
- cluster `62` `central`: `records=291`, `runs=191`, `multi_runs=42`, `max_run=26`

### Entry8 Reading

- Entry8 records are still single-line counted payloads, but runtime flow is not purely one-record-per-box.
- Many clusters contain multi-record contiguous state runs, so the remaining runtime question is chaining/page-flow across short records rather than multiline decoding.
- Translation should treat chain-heavy clusters as likely externally sequenced dialogue stretches and keep per-record lines concise.

## Registry D

- `single_line_short`: `runs=62`, `record_coverage=80`
- `short_or_one_break`: `runs=87`, `record_coverage=94`
- `mid_multiline`: `runs=50`, `record_coverage=52`
- `long_multiline`: `runs=8`, `record_coverage=18`

### Registry D Reading

- Registry D is not one monolithic multiline family; it splits into short single-line battle/tutorial barks, one-break explanatory lines, mid multiline explanations, and a small long-multiline manual/tutorial tier.
- This narrows the remaining runtime risk from generic 'page-flow unknown' to a much smaller question: how the longest multiline tier turns pages inside the shared r3=20 candidate family.
- Translation should preserve existing newlines and avoid adding extra breaks until runtime page-turn QA is locked.

## Operational Reading

- Entry8 remaining uncertainty is now concentrated in chain-heavy single-line clusters rather than the entire source.
- Registry D remaining uncertainty is now concentrated in a very small long-multiline tier plus page-turn behavior, not the whole source.
