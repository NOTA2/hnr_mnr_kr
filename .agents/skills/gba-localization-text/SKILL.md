---
name: gba-localization-text
description: Build a safe GBA text pipeline that discovers, extracts, classifies, audits, and prepares text for reinsertion while preserving byte spans, encodings, terminators, control bytes, counted headers, pointers, segment capabilities, and source-family layout rules. Use for text extraction, missing Japanese text, source-family design, command-stream scripts, overlap bugs, workset generation, or text apply capability work.
---

# GBA Text Pipeline

Treat text as structured binary records, not strings found by a decoder.

## Prepare

1. Require `rom_analysis` to be ready and verify the source ROM hash.
2. Read `.gba-localization/manifests/text_sources.json`.
3. Read [text-family-contract.md](references/text-family-contract.md) before
   adding or changing a family.
4. Inspect existing extractors and canonical data before writing a broad scan.
5. Acquire the `text` lifecycle claim before changing canonical records.

## Discover And Classify

1. Use broad decoding scans only to find candidates.
2. Define a source family for each distinct record structure and runtime layout:
   terminated text, fixed slot, counted command stream, packed script, pointer
   table, or unknown.
3. Determine encoding, stop-byte behavior, terminator, header/count unit,
   control bytes, pointer provenance, byte span, and layout profile per family.
4. Make scanners multibyte-aware. A stop byte may be the trailing byte of a
   valid encoded character.
5. Reject candidate ranges that overlap canonical records unless manual
   classification proves a separate fixed slot.
6. When gameplay shows untranslated text near a known record, inspect nearby
   printable islands before assuming the extractor already covers the screen.

## Build Canonical Extraction

1. Give every record a stable ID and exact start/end offsets.
2. Preserve raw structural metadata needed to reconstruct the record.
3. Separate canonical extraction from generated reports and GUI datasets.
4. For segmented command streams, create a capability matrix:
   `repoint`, `repoint_overlay`, `length_preserved`, `protected`, or `unknown`.
5. Validate pointer-looking boundaries against complete record spans.
6. Give boundary-crossing records a length-preserved path before attempting
   expansion.
7. Generate human-editable worksets from canonical records; never reverse the
   ownership direction.

## Validate

Run deterministic checks for:

- decode/encode round-trip of unchanged records;
- extraction reproducibility;
- duplicate stable IDs;
- byte-range overlap;
- header/count consistency;
- terminator and control-byte preservation;
- source-family coverage and explicit unknowns;
- apply dry run with unchanged content.

Do not claim full coverage from a scan count alone. Runtime QA remains an
independent source of missing-text findings.

## Exit Gate

Mark `text` as `ready` when known source families are reproducible, structural
metadata survives a no-op round-trip, overlaps are classified, unsupported
families are protected, and worksets can be regenerated. Keep final runtime
coverage as an explicit QA item rather than silently declaring extraction
complete. Release the lifecycle claim after checkpointing the phase.
