# Generated Workbench Retention

Date: YYYY-MM-DD

Use this before deleting or untracking generated extraction/workbench output.

## Candidate

- Path:
- Generator command:
- Active input manifest:
- Active output manifest:
- Current role: `active`, `historical-summary-kept`, `scratch-delete-ok`, or
  `unknown`.

## Keep Evidence

Record the smallest useful facts before deletion:

- item count:
- representative IDs or offsets:
- source input path:
- reason the output was useful:
- reason the output is no longer active:
- regeneration command:

## Decision

| Decision | Meaning |
| --- | --- |
| `KEEP` | Active build/GUI/QA dependency. |
| `KEEP WITH CAUTION` | Not proven safe to remove. |
| `RETROSPECTIVE KEEP` | Keep compact summary or representative sample. |
| `UNTRACK` | Keep locally but remove from Git. |
| `DELETE` | Remove after lesson and regeneration path are recorded. |

## Validation

Run the active project integrity checks before and after the cleanup batch.
