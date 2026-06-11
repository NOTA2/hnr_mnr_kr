# 07 UI Icon Badge Wordmarks

Date pruned: 2026-06-12 KST

This workspace was reduced to a summary during the project cleanup pass.

## Decision

- State: `pruned_summary`
- Original candidate count: `120`
- Original tracked files: `364`
- Original size: about `3.6M`
- Removed artifact types:
  - `120` raw LZ77 dumps under `dumps/`
  - `120` PGM tile previews under `exports/`
  - `120` PNG previews under `png_exports/`
  - `1` generated contact sheet under `contact_sheets/`
  - `3` generated note/report files under `notes/`

The removed files were review-unit discovery artifacts. They were not active
GUI image source files, active replacement files, ROM build inputs, or patch
generation inputs at the time of pruning.

## Preserved Reading

`ui_icon_badge_wordmarks` was a low-priority review unit for small icon, badge,
or mini-label graphics. The useful lesson from this workspace is that static
candidate sheets can surface broad LZ77 blocks, but they are not enough to
promote an asset into the localization GUI. Runtime tilemap/screen-order
evidence is needed before an extracted block becomes an editable source.

The representative `0x00534874` candidate was classified as a shared battle HUD
small font/glyph sheet, not as a text-bearing image label. Current active work
for that block lives in:

- `confirmed_data/image_inventory/edit_packs/common_hud_tiles_00534874`

That active edit pack remains protected and is still referenced by the GUI image
workflow.

## Candidate Summary

- Tile-count distribution:
  - `128`: `26`
  - `160`: `5`
  - `192`: `15`
  - `224`: `1`
  - `256`: `73`
- Decompressed-size distribution:
  - `4096`: `26`
  - `5120`: `5`
  - `6144`: `15`
  - `7168`: `1`
  - `8192`: `73`
- Compressed-size range: `807` to `4425`
- Compressed-size median: about `2035`

Top compressed candidates before pruning:

| Index | Offset | Compressed size | Tiles |
| ---: | --- | ---: | ---: |
| `075` | `0x00476C7C` | `4425` | `192` |
| `074` | `0x0046DBAC` | `3965` | `224` |
| `001` | `0x00477DCC` | `3428` | `256` |
| `076` | `0x00478B34` | `3400` | `192` |
| `077` | `0x0042E42C` | `3392` | `192` |
| `002` | `0x004888F8` | `3170` | `256` |
| `003` | `0x00457FE4` | `3050` | `256` |
| `078` | `0x0047A1F4` | `3035` | `192` |
| `004` | `0x00534874` | `3031` | `256` |
| `079` | `0x00481664` | `2894` | `192` |

## Regeneration

The workspace can be regenerated from the repo scripts if this low-priority
review unit needs to be reopened:

```bash
python3 scripts/extract_image_review_candidates.py ui_icon_badge_wordmarks --limit 120
python3 scripts/build_tile_contact_sheets.py
```

After regeneration, run the safety checks before promoting any file back into
the active workflow:

```bash
python3 scripts/build_image_source_manifest.py
python3 scripts/audit_gui_workflow_integrity.py
```
