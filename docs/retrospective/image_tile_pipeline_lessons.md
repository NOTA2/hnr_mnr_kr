# Image And Tile Pipeline Lessons

Date: 2026-06-24 KST

This document preserves the reusable lessons from the image/tile side of the
project before any further image inventory cleanup. It is intentionally compact:
the repo should not keep every generated preview forever, but it must not delete
the only evidence that explains why an image approach failed.

No image files are removed by this document.

## Evidence Read Before Writing

- `docs/cleanup/image_inventory_audit.md`
- `docs/cleanup/image_inventory_prune_plan.md`
- `docs/cleanup/image_workspace_prune_readiness.md`
- `docs/cleanup/image_workspaces_summary.md`
- `docs/cleanup/uploaded_replacements_audit.md`
- `confirmed_data/image_inventory/workspaces/07_ui_icon_badge_wordmarks/README.md`
- `docs/retrospective/evidence_digest.md`
- `docs/retrospective/failure_modes.md`

## Core Lesson

Image localization on GBA needs three separate ideas to stay separate:

1. discovery evidence;
2. ROM-backed editable sources;
3. final replacement assets.

The project became risky whenever a file moved between those roles without an
explicit manifest update. A screenshot, contact sheet, broad extraction output,
or uploaded browser payload may be useful, but it is not automatically a source
of truth for ROM rebuilding.

## Artifact Roles

| Artifact family | Role | Cleanup decision |
| --- | --- | --- |
| `runtime_tile_matches/` and `runtime_rle_screen_order/` | Runtime/screen-order evidence used to locate or verify assets. | Keep while referenced by GUI items; do not treat as editable ROM source unless the backing resource is identified. |
| `global_tile_extraction/` and `rle_tile_extraction/` | Broad discovery output and script-default report inputs. | Keep with caution until scripts stop using their reports or the required reports are promoted. |
| `workspaces/` | Review-unit discovery evidence, mostly generated dumps/previews/contact sheets. | Summarize per unit before pruning; prune one unit per commit only after safety gates pass. |
| `edit_packs/` | Durable editable source packs and direct patch asset families. | Protect by default; each pack needs palette, tile-order, source, and apply-path notes. |
| `uploaded_image_replacements/` | Current GUI replacement payloads, including user/browser uploads. | Track active references; do not prune from stale manifests or shell-only path checks. |
| `image_source_manifest.json` | Active GUI item-level source/replacement/reference baseline. | Regenerate before image cleanup and require `missing paths: 0`. |

## Repeated Failure Patterns

### Static Discovery Looked Like An Editable Source

Contact sheets and review workspaces were good for finding possible text-bearing
graphics, but they did not prove how the game assembled those graphics at
runtime. The `07_ui_icon_badge_wordmarks` prune preserved this lesson: the
interesting `0x00534874` candidate turned out to belong to the shared battle HUD
small-font/tile family, and the protected active work lives under
`edit_packs/common_hud_tiles_00534874`.

Future rule:

- A candidate is not editable until it has a ROM resource, tile/screen order
  mapping, palette source, replacement dimensions, and apply script.

### Preview Scale And Source Scale Became Ambiguous

The workflow mixed 1x editable sources with scaled PNG previews. That was useful
for visual review but dangerous when uploads/downloads later had to become build
inputs.

Future rule:

- The editable source and replacement should be 1x unless the target explicitly
  requires another scale. Scaled files are preview artifacts and should be
  regenerable.

### Palette Context Was Part Of The Asset

4bpp tile graphics are indexed through palette context. A replacement can have
the correct shape but still look wrong if it was quantized against the wrong
palette or sibling UI component.

Future rule:

- Every image edit pack must record palette provenance and a quantization check.
  Sibling UI pieces should share a deliberate palette policy.

### Whole-Block Editing Was Too Heavy For Small Labels

Some UI text lived inside large compressed tile blocks. Replacing the entire
block made the edit slow and increased the chance of unnecessary repointing.

Future rule:

- Prefer focused crop edit packs for small labels, with a reversible map back to
  the parent compressed resource.

### Uploaded Payloads Were Small But Operationally Critical

`uploaded_image_replacements/` looked like browser cache, but active GUI JSON
referenced many payloads directly. A stale manifest and macOS Unicode filename
normalization made shell-only checks misleading.

Future rule:

- Refresh the upload manifest with the same path semantics used by the runtime.
  Require active GUI references to have zero missing paths before pruning any
  uploaded payload.

## Minimal Image Target Schema

A future starter kit should create an image target record with these fields
before any replacement is considered final:

- `target_id`
- `display_context`
- `artifact_role`
- `evidence_paths`
- `rom_resource_offset_or_id`
- `compression`
- `tile_order`
- `screen_order_mapping`
- `tilemap_or_screenblock_path`
- `palette_source`
- `source_1x_path`
- `preview_paths`
- `replacement_path`
- `replacement_scale`
- `apply_script`
- `verification_command`
- `runtime_screenshot_or_save`
- `cleanup_classification`

If any of `rom_resource_offset_or_id`, `palette_source`, `source_1x_path`, or
`apply_script` is unknown, the target is still discovery evidence rather than a
final editable source.

## Image Cleanup Gate

Before deleting or untracking image-side generated files:

1. Regenerate `confirmed_data/image_inventory/image_source_manifest.json`.
2. Confirm `missing paths: 0`.
3. Run `python3 scripts/audit_gui_workflow_integrity.py`.
4. Read `README.md` and `*.md` files inside the target subtree.
5. Search exact references from `docs/`, `scripts/`, `confirmed_data/`,
   `tools/`, and `gba_kor_tool/`.
6. Write a compact lesson if the subtree explains a failed or corrected image
   approach.
7. Prune one family or review unit per commit.

## Starter-Kit Extraction

The generic GBA localization agent should ship with:

- an image artifact role taxonomy;
- an image target manifest schema;
- an uploaded replacement manifest gate;
- a workspace prune checklist;
- a palette provenance requirement;
- a 1x-source vs preview-scale rule;
- a crop edit-pack workflow for small labels.

These rules are now project-neutral enough to reuse. They should be converted
into a starter-kit template after the active localization project finishes and
the user adds their own final retrospective notes.
