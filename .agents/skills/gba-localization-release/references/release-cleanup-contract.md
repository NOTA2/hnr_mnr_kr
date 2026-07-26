# Release And Cleanup Contract

## Release Manifest Entry

Record:

```json
{
  "version": "1.0.0",
  "git_revision": "...",
  "patch_path": "releases/1.0.0/game-ko.bps",
  "patch_sha256": "...",
  "source_rom_sha256": "...",
  "output_rom_sha256": "...",
  "roundtrip_verified": true,
  "qa_build_id": "release-1.0.0",
  "known_issues_path": "releases/1.0.0/KNOWN_ISSUES.md"
}
```

## Cleanup Decision

For each batch, record:

- exact target paths;
- producer and consumers;
- active references;
- canonical or generated role;
- regeneration command;
- keep/delete/untrack decision;
- retrospective lesson path;
- recovery commit.

Unknown means stop. Do not interpret it as permission to delete.

## Retrospective Entry

Capture:

1. symptom;
2. incorrect assumption;
3. evidence that corrected it;
4. final technical rule;
5. automated or procedural guard;
6. phase and trigger;
7. representative evidence retained;
8. project-specific details removed before reuse.

## Skill Promotion Test

Promote a lesson into the generic suite only when:

- it can recur in another GBA title;
- it is phrased without current-game offsets or names;
- it does not require files outside the target repository;
- it changes a decision, required field, check, or gate;
- it is not already covered by an existing rule.
