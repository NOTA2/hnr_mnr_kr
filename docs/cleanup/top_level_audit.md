# Top-Level Cleanup Audit

Date: 2026-06-12 KST

This audit covers small top-level items that make the repo look noisier than the
current localization workflow requires.

## Decisions

| Path | Decision | Reason |
| --- | --- | --- |
| `package.json` | `DELETE` | Legacy Node dependency file. No active script or documented command uses it. |
| `package-lock.json` | `DELETE` | Lockfile for the same unused Node dependency set. |
| `generated-images/` | `KEEP WITH CAUTION` | Contains one tracked PNG still referenced by image edit-pack manifests. |
| `startup_profiles/` | `DELETE LOCAL EMPTY DIR` | Empty untracked directory; no git-tracked files or references. |
| `generated-images/apply-ready/` | `DELETE LOCAL EMPTY DIR` | Empty untracked directory under a kept top-level folder. |

## Package File Trace

`package.json` only declared:

- `@vitalets/google-translate-api`
- `p-limit`

Reference search found no active project script importing those packages.
Remaining references are the package files themselves, historical experiment
notes, and cleanup classification docs.

The tracked package files were introduced in commit `b6c377b`
(`Entry8 번역 워크벤치와 분석 결과 통합`). They are not part of the current
Python-based build, GUI, image replacement, runtime QA, or release workflow.

## generated-images Hold

Do not delete `generated-images/` yet. The tracked file
`generated-images/debug_tiles_003A206C/compose_jangjjae_galmuri9_with_tile013_040_clean_1x.png`
is referenced by:

- `confirmed_data/image_inventory/edit_packs/card_page_count/manifest.json`
- `confirmed_data/image_inventory/edit_packs/alchemy_tiles_003A206C/manifest.json`

Future cleanup option:

- Move the referenced PNG into a clearer `confirmed_data/image_inventory/...`
  source or replacement folder.
- Update both manifests in the same commit.
- Verify the new path exists and no stale `generated-images` references remain.

## Local Empty Dirs

Empty untracked directories can be removed locally when found:

- `startup_profiles/`
- `generated-images/apply-ready/`, if still empty

These removals do not affect Git history.
