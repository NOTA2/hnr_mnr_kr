# ROM Analysis Evidence

## Experiment Record

Record each meaningful probe with this shape:

```json
{
  "experiment_id": "text-pointer-table-001",
  "input_rom_sha256": "...",
  "question": "Does this table point to terminated CP932 records?",
  "command": "python3 scripts/probe_text_table.py ...",
  "outputs": ["analysis/text-pointer-table-001.json"],
  "observation": "18 of 20 aligned values resolve to valid records",
  "conclusion": "strong_hypothesis",
  "unknowns": ["consumer function not yet confirmed"],
  "next_test": "trace two table consumers"
}
```

## Confidence Rules

- `confirmed`: two independent checks or one direct runtime/build proof.
- `strong_hypothesis`: multiple structural checks agree, but no direct consumer
  or runtime proof exists.
- `weak_hypothesis`: plausible pattern with unresolved alternatives.
- `rejected`: a specific observation disproved the hypothesis.

Never convert a confidence label by editing prose alone; add the evidence that
changed it.

## Address Safety

Record both file offset and runtime address when relevant. State the conversion
rule. Preserve original base addresses in disassembly and hexdump annotations.

For every inferred record, keep:

- start and end offsets;
- pointer/table provenance;
- raw structural prefix and suffix;
- decoder and terminator policy;
- overlap result;
- consumer or runtime evidence.

## Discovery Versus Canonical Data

Discovery scans may contain false positives, overlapping fragments, duplicate
views, and broad generated output. Canonical data must have stable IDs,
provenance, bounded byte ranges, and a known regeneration command.
