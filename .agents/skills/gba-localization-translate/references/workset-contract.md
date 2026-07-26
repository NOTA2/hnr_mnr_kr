# Translation Workset Contract

## Record Shape

Use a structure equivalent to:

```json
{
  "record_id": "dialogue:00123456",
  "source_family": "dialogue-counted",
  "source_fingerprint": "sha256-of-structural-source",
  "source_text": "...",
  "context": {
    "scene": "intro",
    "speaker_evidence": "unknown",
    "neighbors": ["dialogue:00123420", "dialogue:00123490"]
  },
  "constraints": {
    "layout_profile": "single_line_dialogue",
    "max_encoded_bytes": 24,
    "preserve_tokens": ["{PLAYER}"]
  },
  "agent_draft": "",
  "translation": "",
  "review_state": "untranslated",
  "manual_locked": false,
  "notes": []
}
```

Keep bulky structural bytes in canonical extraction records and link them by
stable ID. Do not duplicate enough metadata to create conflicting authorities.

## Import Rules

Before importing:

- match the exact record ID;
- compare source fingerprint;
- reject duplicate results;
- preserve manual locks;
- report unknown and missing IDs;
- write an import summary before replacing canonical files;
- make the update atomic or restore the previous file on failure.

## Parallel Work Rules

Partition by stable IDs, not line numbers in a mutable JSON file. Workers must
not edit shared terminology or schemas independently. Merge terminology changes
first, regenerate worksets if constraints changed, then import translations.

## Content QA

Automated checks may flag but should not blindly rewrite:

- source-language characters;
- inconsistent translations for repeated source;
- punctuation and whitespace drift;
- width or encoded-byte overflow;
- missing required tokens;
- forbidden control bytes;
- draft text selected ahead of reviewed text.

Human runtime review decides awkwardness, context, timing, and tone.
