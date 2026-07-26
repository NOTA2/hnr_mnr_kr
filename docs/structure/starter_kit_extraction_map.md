# Starter Kit Extraction Map

Date: 2026-06-24 KST

This map explains how the current project's cleanup and retrospective documents
flow into the reusable starter kit. It is a structure document, not a migration
command: no active project files should be moved because of this map alone.

## Current Project Sources

| Current source | Reusable output |
| --- | --- |
| `docs/retrospective/failure_modes.md` | Agent guardrails and prevention checklist. |
| `docs/retrospective/entry8_vm_lessons.md` | Text source-family and command-stream schema rules. |
| `docs/retrospective/image_tile_pipeline_lessons.md` | Image target schema, image cleanup gate, palette/source-scale rules. |
| `docs/cleanup/retention_policy.md` | Cleanup classification terms. |
| `docs/cleanup/safety_gate.md` | Cleanup gate checklist. |
| `docs/cleanup/local_runtime_artifacts_matrix.md` | Runtime artifact matrix pattern. |
| `docs/structure/script_transition_audit.md` | Wrapper-first script migration rule. |
| `docs/structure/data_role_inventory.md` | Artifact role inventory pattern. |

## Starter Kit Outputs Now Present

| Output | Purpose |
| --- | --- |
| `docs/starter_kit/gba_localization_agent.md` | Main project-neutral agent spec. |
| `docs/starter_kit/prompts/agent_seed_prompt.md` | Copyable seed prompt. |
| `docs/starter_kit/checklists/session_start.md` | First checks for every session. |
| `docs/starter_kit/checklists/cleanup_gate.md` | Gate before deletion, untracking, or moves. |
| `docs/starter_kit/checklists/release_gate.md` | Gate before publishing a patch release. |
| `docs/starter_kit/schemas/project_config.schema.json` | Minimal project policy contract. |
| `docs/starter_kit/schemas/text_source_family.schema.json` | Text extraction/apply capability contract. |
| `docs/starter_kit/schemas/image_target.schema.json` | Image evidence/source/replacement contract. |
| `docs/starter_kit/templates/project_config.example.json` | Copyable starting config. |
| `docs/starter_kit/templates/gitignore.gba-localization.example` | Starter ignore policy for ROMs, saves, patches, and generated bulk. |
| `docs/starter_kit/templates/local_runtime_artifacts_matrix.template.md` | Local runtime keep/removal matrix pattern. |
| `docs/starter_kit/templates/generated_workbench_retention.template.md` | Generated-output retention decision pattern. |
| `docs/starter_kit/workflows/bootstrap_sequence.md` | New-project operating order. |
| `docs/starter_kit/workflows/cleanup_sequence.md` | Late-stage cleanup operating order. |

## Runnable Skill Suite

The reusable rules are now implemented as repository-scoped Codex skills under
`.agents/skills/`.

| Skill | Lifecycle responsibility |
| --- | --- |
| `gba-localization-lifecycle` | Initialize, resume, validate, route, and checkpoint the whole lifecycle. |
| `gba-localization-bootstrap` | Establish ROM, Git, path, artifact, and command safety. |
| `gba-localization-rom-analysis` | Turn ROM hypotheses into bounded evidence. |
| `gba-localization-text` | Discover, extract, classify, and round-trip text families. |
| `gba-localization-font` | Prove encoding, capacity, relocation, atlas, and runtime rendering. |
| `gba-localization-images` | Map, edit, apply, and verify ROM-backed graphics. |
| `gba-localization-translate` | Generate, translate, review, merge, and synchronize worksets. |
| `gba-localization-build-qa` | Build deterministic review ROMs and run gameplay QA. |
| `gba-localization-release` | Verify patches, package releases, clean safely, and capture lessons. |

The suite keeps active control state in the target repository under
`.gba-localization/`.
It does not read current-project scripts, data, ROM offsets, or paths as runtime
dependencies.

## Still Project-Specific

These remain useful evidence, but should not be copied directly into a generic
starter kit:

- extracted text and translation worksets;
- actual ROM offsets and game-specific tables;
- active GUI JSON;
- image edit packs and uploaded payloads;
- local ROM/save/savestate paths;
- raw Codex logs;
- screenshots or runtime captures from this project.

## Next Iteration Steps

1. Forward-test lifecycle initialization and checkpoint behavior in a temporary
   Git repository.
2. Use the suite in another GBA localization project.
3. Promote only newly proven, project-neutral failure-prevention rules.
4. Consider plugin packaging after the standalone skills stabilize.

## Safety Boundary

Do not move active scripts, GUI data, image inventory, translation worksets, or
analysis evidence just because a matching starter-kit path exists. The starter
kit is a reusable extraction layer; the active project keeps its stable paths
until the late-stage QA pipeline no longer depends on them.
