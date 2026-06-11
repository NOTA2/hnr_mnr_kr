# Top-Level Cleanup Audit

Date: 2026-06-12 KST

This audit covers small top-level items that make the repo look noisier than the
current localization workflow requires.

## Decisions

| Path | Decision | Reason |
| --- | --- | --- |
| `package.json` | `DELETE` | Legacy Node dependency file. No active script or documented command uses it. |
| `package-lock.json` | `DELETE` | Lockfile for the same unused Node dependency set. |
| `generated-images/` | `MOVED / DELETE EMPTY DIRS` | The only tracked PNG was moved into the relevant image edit pack. |
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

## generated-images Cleanup

The former tracked file
`generated-images/debug_tiles_003A206C/compose_jangjjae_galmuri9_with_tile013_040_clean_1x.png`
was moved to:

- `confirmed_data/image_inventory/edit_packs/alchemy_tiles_003A206C/direct_patch_replacements/compose_jangjjae_galmuri9_with_tile013_040_clean_1x.png`

The two referencing manifests were updated:

- `confirmed_data/image_inventory/edit_packs/card_page_count/manifest.json`
- `confirmed_data/image_inventory/edit_packs/alchemy_tiles_003A206C/manifest.json`

After this move, `generated-images/` has no tracked files and can stay absent.

## Local Empty Dirs

Empty untracked directories can be removed locally when found:

- `startup_profiles/`
- `generated-images/apply-ready/`, if still empty

These removals do not affect Git history.
