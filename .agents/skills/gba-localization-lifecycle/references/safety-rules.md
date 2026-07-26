# Cross-Phase Safety Rules

These rules were extracted from repeated failures in a completed GBA
localization workflow.

1. Treat runtime captures as evidence until a ROM-backed source and apply path
   are proven.
2. Treat raw tile order and screen order as different data.
3. Keep canonical inputs separate from generated workbenches and previews.
4. Keep machine paths out of active scripts and manifests.
5. Restart or explicitly reload GUI tools after dataset structure changes.
6. Define text constraints per source family; do not apply one global rule.
7. Preserve counted headers, terminators, control bytes, and byte spans through
   extraction, editing, and apply.
8. Search nearby printable islands when runtime text is missing.
9. Reject candidate text by range overlap, not only duplicate start offsets.
10. Audit codepoint availability and glyph payload capacity separately.
11. Prove mini-font slots in runtime; physical tiles may be combining marks.
12. Record palette context for every indexed-color replacement.
13. Prefer reversible crop edit packs for small labels in large resources.
14. Regenerate datasets before builds and use one explicit apply priority.
15. Preserve the failure lesson before deleting confusing artifacts.
16. Validate pointer-looking boundaries against full record spans.
17. Give every image artifact an explicit role before promotion or cleanup.
18. Refresh active GUI upload references before pruning uploaded payloads.

When a new failure repeats across two sessions or affects more than one source
family, add a project-specific entry to
`.gba-localization/retrospective/failure_modes.md`. Promote it into this suite only
after removing game-specific offsets, copyrighted content, and machine paths.
