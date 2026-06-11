# Data Role Inventory

Date: 2026-06-12 KST

This inventory classifies `confirmed_data/` before any further cleanup or
structure move. It does not move or delete files.

## Safety Boundary

- Treat `confirmed_data/` as active until a narrower source-of-truth is proven.
- Do not remove a large subtree only because the GUI does not directly load it.
- Keep runtime evidence separate from editable ROM-backed sources.
- Keep historical failed translation passes until their lessons are captured in
  retrospective docs.

## Role Classes

- `SOURCE OF TRUTH`: canonical input for extraction, translation, font, layout,
  or rebuild.
- `ACTIVE STATE`: GUI/workbench state that current tooling reads or updates.
- `DERIVED INDEX`: generated from source-of-truth files, but still useful for
  navigation, QA, or rebuild safety.
- `RUNTIME EVIDENCE`: screenshots, savestate-derived data, tilemaps, or debug
  captures. Useful for diagnosis, not automatically editable source.
- `RETROSPECTIVE HOLD`: failed or superseded experiment output kept until the
  lesson is summarized.
- `KEEP LOCAL`: ignored local support data, not shared repo source.

## Top-Level confirmed_data Map

| Path | Role | Current decision |
| --- | --- | --- |
| `confirmed_data/extracted_texts/` | `SOURCE OF TRUTH` | Keep. Canonical extracted text inputs. |
| `confirmed_data/translation_worksets/` | `SOURCE OF TRUTH` | Keep. Human-editable prioritized worksets. |
| `confirmed_data/font_assets/` | `SOURCE OF TRUTH` | Keep. Active font profile and small tracked font evidence. |
| `confirmed_data/text_layout/` | `SOURCE OF TRUTH` / `DERIVED INDEX` | Keep. Layout family constraints and assignment index. |
| `confirmed_data/dialogue_metadata/` | `DERIVED INDEX` | Keep. Dialogue state-token sidecars used for QA tone/flow consistency. |
| `confirmed_data/translation_workspace/` | `SOURCE OF TRUTH` / `DERIVED INDEX` / `RETROSPECTIVE HOLD` | Keep with caution. Contains canonical master files and old Entry8 pass evidence. |
| `confirmed_data/localization_workbench/` | `ACTIVE STATE` | Keep. GUI dataset, progress, imports, and image replacement state. |
| `confirmed_data/image_inventory/` | `RUNTIME EVIDENCE` / `SOURCE CANDIDATE` / `DERIVED INDEX` | Keep with caution. Largest active cleanup target, but not safe to prune yet. |
| `confirmed_data/runtime_debug/` | `KEEP LOCAL` / `RUNTIME EVIDENCE` | Keep ignored locally until runtime QA closes. |

## Size And Count Snapshot

- `confirmed_data/image_inventory/`: about `239M`, `15,781` tracked files.
- `confirmed_data/translation_workspace/`: about `91M`, `322` tracked files.
- `confirmed_data/localization_workbench/`: about `40M`, `421` tracked files.
- `confirmed_data/dialogue_metadata/`: about `8.6M`, `8` tracked files.
- `confirmed_data/extracted_texts/`: about `7.2M`, `17` tracked files.
- `confirmed_data/font_assets/`: about `560K`, `49` tracked files.
- `confirmed_data/translation_worksets/`: about `584K`, `10` tracked files.
- `confirmed_data/text_layout/`: about `176K`, `15` tracked files.
- `confirmed_data/runtime_debug/`: about `1.6M`, ignored and not tracked.

## Cleanup Notes By Area

### extracted_texts

Keep as canonical extracted source data. Discovery scans and false-positive
candidate data should stay outside this folder or be summarized elsewhere.

### translation_worksets

Keep as human-facing worksets. These are safer than editing GUI cache data
directly because they are small and reviewable.

### translation_workspace

Keep with caution. It mixes:

- canonical master/index files;
- extraction/audit reports;
- Entry8 cluster/run work products;
- older retranslation passes that may be retrospective evidence.

Future cleanup should split active canonical files from old pass evidence only
after the Entry8 lessons are folded into `docs/retrospective/`.

### localization_workbench

Keep as active GUI state. The `uploaded_image_replacements/` files are tracked
because the image replacement workflow may need them for rebuild/apply.

Generated import reports and temporary chunks can be reviewed later, but not
while the GUI state is the active operator surface.

### image_inventory

Keep with caution. It contains review units, edit packs, broad extraction
outputs, runtime captures, tilemap evidence, and source candidates.

Do not prune until:

1. a minimal final image-source manifest exists;
2. source assets are distinguished from previews and runtime evidence;
3. scripts that use broad extraction reports have either new inputs or wrappers;
4. review-unit lessons are summarized.

### runtime_debug

Keep ignored locally. It is current runtime evidence, not shared source data.

## Next Safe Data Step

Use `confirmed_data/image_inventory/image_source_manifest.json` to drive the next
image cleanup pass. It classifies each active image-side item by source role,
replacement role, path family, and keep reason before any large prune.
