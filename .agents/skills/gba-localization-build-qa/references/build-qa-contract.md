# Build And QA Contract

## Canonical Build Properties

The top-level build must be:

- sequential;
- deterministic for identical inputs;
- non-mutating to the source ROM;
- explicit about translation field priority;
- fail-fast on structural corruption;
- able to report partial skips without hiding them;
- recoverable after failure.

## Apply Report

Report counts by source family and action:

- in-place;
- overlay;
- repointed;
- length-preserved boundary crossing;
- image replacement;
- protected;
- overflow;
- unknown;
- skipped with reason.

Compare counts with the previous known-good build and require an explanation for
unexpected drops or increases.

## QA Case Shape

```json
{
  "case_id": "intro-first-dialogue",
  "build_id": "review-2026-01-01-001",
  "scope": ["dialogue-counted", "main-font"],
  "setup": "New game from clean save",
  "steps": ["Start game", "Advance to first dialogue"],
  "expected": "Korean line renders and advances",
  "actual": "",
  "status": "pending",
  "evidence_paths": [],
  "suspected_phase": ""
}
```

## Runtime Coverage

Keep a matrix by source family, renderer, image target, and progression region.
One successful opening screen cannot validate relocated data used hours later.

## Regression Response

If QA invalidates an earlier assumption:

1. keep the failing build and reproduction metadata locally;
2. move the responsible phase back to `in_progress`;
3. add the failed assumption to retrospective evidence;
4. fix canonical logic or data;
5. rebuild from the clean source;
6. rerun the focused case and one neighboring regression case.
