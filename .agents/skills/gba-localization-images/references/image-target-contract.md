# Image Target Contract

## Artifact Roles

- `runtime_evidence`: screenshot, savestate, or runtime capture used to locate or
  verify a resource.
- `discovery_workspace`: broad extraction, contact sheet, or analysis dump.
- `editable_source`: ROM-backed 1x source with a reversible mapping.
- `generated_preview`: scaled or annotated view that can be regenerated.
- `uploaded_payload`: user or browser upload still referenced by tooling.
- `final_replacement`: reviewed source asset consumed by the build.
- `historical_debug`: representative evidence retained for a lesson.

## Target Record

Record:

```json
{
  "target_id": "main-menu-label",
  "artifact_role": "editable_source",
  "display_context": "main menu",
  "evidence_paths": ["localization/evidence/main-menu.png"],
  "rom_resource_offset_or_id": "0x00123456",
  "compression": "gba-lz77",
  "tile_format": "4bpp-8x8",
  "tile_order": "storage order description",
  "screen_order_mapping": "localization/assets/main-menu/tile-map.json",
  "tilemap_or_screenblock_path": "localization/assets/main-menu/tilemap.bin",
  "palette_source": "localization/assets/main-menu/palette.bin",
  "source_1x_path": "localization/assets/main-menu/source.png",
  "preview_paths": ["localization/generated/main-menu-8x.png"],
  "replacement_path": "localization/assets/main-menu/ko.png",
  "replacement_scale": "1x",
  "allowed_edit_rect": {"x": 0, "y": 0, "width": 64, "height": 16},
  "manual_adjustment": {
    "x_offset": 0,
    "y_offset": 0,
    "tile_start": 0,
    "tile_order": []
  },
  "shared_parent_target_ids": [],
  "apply_command": "python3 scripts/apply_main_menu.py",
  "verification_command": "python3 scripts/verify_main_menu.py",
  "runtime_evidence_path": "localization/evidence/main-menu-ko.png"
}
```

## Promotion Gate

Do not promote discovery evidence to an editable source until these fields are
known:

- ROM resource offset or ID;
- compression and tile format;
- tile/screen-order mapping;
- palette source;
- 1x source path;
- replacement path;
- apply command.

## Pixel And Tile Validation

Require:

- exact output dimensions;
- zero changed pixels outside the allowed rectangle or mask;
- palette indices constrained by the target policy;
- visible 8x8 grid and tile indices in editable previews;
- saved numeric alignment and tile-order configuration;
- regression checks for every target sharing the parent resource or palette.

## Cleanup Gate

Before deleting image-side files:

1. Refresh the active target and upload manifests.
2. Require zero missing paths.
3. Read subtree documentation.
4. Search exact references in scripts, manifests, GUI data, and docs.
5. Preserve the failure lesson and regeneration command.
6. Remove one resource family per recoverable Git checkpoint.
