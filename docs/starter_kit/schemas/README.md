# Starter Kit Schemas

These lightweight JSON schemas define the minimum metadata a future GBA
localization project should carry from the beginning.

They are intentionally generic. They do not encode this project's specific text
banks, ROM offsets, or asset paths.

- `project_config.schema.json`: top-level repo policy and command locations.
- `text_source_family.schema.json`: extraction/apply/layout capability for one
  text family.
- `image_target.schema.json`: source/evidence/replacement metadata for one
  image target.

Use these as starting contracts. A real project may split them into stricter
schemas once its ROM format is understood.
