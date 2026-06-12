# Entry8 VM Lessons

Date: 2026-06-12 KST

This note condenses the largest Entry8 structure reports into reusable rules.
It does not replace the raw analysis yet, but it gives future cleanup a compact
lesson to preserve before any large JSON pruning.

## Evidence Files

- `analysis/entry8_vm_structure.md`
- `analysis/entry8_vm_structure.json`
- `analysis/entry8_segment_capability_map.md`
- `analysis/entry8_segment_capability_map.json`
- `analysis/entry8_boundary_crossing_structure_analysis.md`
- `analysis/entry8_boundary_crossing_structure_analysis.json`

## Facts Worth Preserving

- Entry8 starts at `0x6B594C` and spans `0xBD8FC` bytes.
- The analysis found `77` segments.
- Opcode format inference found `58 / 217` stable opcode formats.
- Gap parse coverage was about `0.846`, good enough for guidance but not enough
  to treat every gap as a safe boundary.
- The segment capability map classified:
  - `18` active repoint segments;
  - `2` active repoint plus overlay segments;
  - `53` structural candidates;
  - `2` protected segments;
  - `2` unknown or unused segments.
- The final apply mix was not one global strategy:
  - `3,913` records used segment repointing;
  - `6,189` records stayed length-preserved in-place;
  - `21` boundary-crossing records required a special length-preserved path.

## Main Mistake

The dangerous assumption was that every pointer-looking value inside the Entry8
table range could be used as a hard segment boundary. Some values pointed into
counted text payloads, so a naive "next pointer is the end" heuristic split
valid records and made safe text look structurally impossible.

## Corrected Rule

Entry8 text must be treated as command-stream data with per-record metadata, not
as plain strings. A safe record carries:

- source segment;
- byte span;
- counted prefix and char count;
- terminator policy;
- original payload length;
- whether it crosses an inferred segment boundary;
- allowed apply action: in-place, overlay, repoint, protected, or unknown.

## Boundary-Crossing Lesson

The project found `21` boundary-crossing counted records. The safe fix was not
to expand them blindly. If the Korean payload fit the original payload length,
the builder patched the original Entry8 bytes and the patched source blob used
for relocation, then extended relocated segment copy through the text tail when
needed.

Starter-kit rule:

- Boundary-crossing does not automatically mean "unsafe" or "needs repoint".
- First check whether the translated payload can remain length-preserved.
- If a segment is repointed, copy enough tail bytes to include the full original
  record span.

## Capability Matrix Lesson

The useful abstraction was the segment capability map. Each segment needs a
clear class before translation apply:

- `active_repoint`: already proven safe for segment repointing;
- `active_repoint_overlay`: needs both repoint and fixed overlay behavior;
- `candidate_structural`: has evidence but is not yet a safe expansion target;
- `protected`: should not expand by default;
- `unknown_or_unused`: requires fresh proof before use.

Starter-kit rule:

- Build this matrix before mass translation, not after something breaks.
- Do not let one successful segment repoint become a global Entry8 policy.

## Cleanup Decision

Keep the compact Markdown summaries and this retrospective note. Keep the raw
JSON reports until the generic starter-kit schema includes:

- command-stream record fields;
- range-overlap validation;
- segment capability classes;
- boundary-crossing handling;
- apply-action audit output.

After those rules are represented in the starter kit, the raw JSON reports can
be reconsidered as archive or local-only evidence.
