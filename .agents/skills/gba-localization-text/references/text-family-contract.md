# Text Family Contract

## Family Record

Each source family should define:

```json
{
  "family_id": "dialogue-counted",
  "record_type": "counted_command_stream",
  "encoding": "cp932",
  "terminator": null,
  "header": {
    "prefix": ["01", "FF"],
    "count_field": "u16le",
    "count_unit": "characters"
  },
  "control_byte_policy": "preserve",
  "apply_capabilities": ["length_preserved", "repoint"],
  "layout_profile": "single_line_dialogue",
  "overlap_validation": true,
  "extract_command": "python3 scripts/extract_dialogue.py",
  "apply_command": "python3 scripts/apply_dialogue.py"
}
```

Use explicit `null` or `unknown`; do not omit a field because it is
inconvenient.

## Canonical Text Record

Carry at least:

- stable record ID and family ID;
- source offset and exclusive end offset;
- source bytes hash or encoded payload length;
- decoded source text;
- raw prefix/header and suffix/terminator metadata;
- pointer or segment provenance;
- layout profile;
- allowed apply action;
- boundary-crossing and overlap states;
- translation state and notes.

## Range Validation

Sort candidate intervals by start offset and compare full half-open ranges
`[start, end)`. Exact-offset deduplication is insufficient because a false
positive may begin inside a canonical record.

## Command-Stream Safety

Do not treat every pointer-looking value as a segment end. Validate:

- whether it lands inside a record payload;
- whether the full record crosses the inferred boundary;
- whether relocation copies the complete tail;
- whether a length-preserved patch can update both original and relocated data;
- whether downstream commands refer to absolute or bank-local addresses.

## Workset Ownership

Canonical extracted records own structural metadata. Worksets own translation
and review fields. GUI datasets are replaceable views. Define the merge priority
and reject a rebuild that would overwrite newer canonical translation data.
