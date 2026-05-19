# Entry8 Repoint Expansion Strategy

## Current Findings

- Current confirmed variable offsets: `60`
- Structural unprotected variable candidates: `2488`
- Early bucket candidates: `1763`
- Late bucket candidates: `725`
- Current build boundary-crossing applied in-place: `21`
- Current build segment-repointed records: `3942`
- VM gap parse coverage: `0.846`
- English comparison relocatable operand roles: `0`

## Candidate Risk Buckets

- `hard_ref_risky`: `16` segments
- `u16_review_needed`: `58` segments
- `candidate`: `1` segments

## Interpretation

- Entry8 text records are inline counted records: `01 FF` + character count + payload. The vanilla engine appears to consume the payload at the current script stream position.
- Therefore, repointing only the payload bytes is not naturally supported unless we also patch the Entry8 interpreter or discover an existing opcode that loads text from an external pointer.
- The safer expansion unit is a segment/script block: rebuild a segment with longer inline records, append it elsewhere, then update the Entry8 segment directory.
- The current `confirmed_repoint=60` is a conservative tail-safe set, not a hard ceiling. The existing analyses already identify `2488` unprotected variable candidates, but many segments require operand/control-flow validation before enabling all at once.
- Halfwidth spaces are currently blocked mainly by our normalization policy for Entry8 fixed-width records. Repointable records can likely use halfwidth spaces safely if we split normalization policy by length policy instead of by source group only.

## Recommended Path

1. Keep fixed/in-place Entry8 records on conservative fullwidth normalization until renderer behavior is proven per context.
2. For confirmed/structurally safe variable records, switch normalization to allow halfwidth spaces and narrow punctuation. This can reduce byte pressure and improve spacing.
3. Expand repoint coverage by segment batches, not one giant all-record switch. Start from `safe_tail_baseline`, then add candidate segment `0x148`, then low-risk `u16_review_needed` segments with no hard u32 refs, then broader early/late buckets.
4. For each batch, build one test ROM path only (`hnr_localization_review_entry8_test.gba`) and compare apply reports plus targeted gameplay checkpoints.
5. Investigate whether an existing opcode can display external text pointers. If not found, per-text pointer repoint would require code patching the Entry8 interpreter, which is a bigger engine hack than segment repoint.
