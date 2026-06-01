# Retrospective Evidence Digest

This document records lessons from local project files and local Codex session
metadata. Raw session logs are not copied into the repo.

## Evidence Sources

Relevant local Codex sessions found in `/Users/user/.codex/session_index.jsonl`
include:

- `GBA 한글화 도구 만들기`
- `코어 UI 번역 초안 작성`
- `게임 용어 번역`
- `Entry8 번역 JSON 작성`
- `Entry8 재번역`
- `검토 Entry8 띄어쓰기·부호`
- `Review Entry8 translations`
- `Adjust Korean spacing`
- `Fix Korean spacing`
- `Retranslate Entry8 records`
- `GBA 이미지 추출 개선`
- `이어하기로 교체`
- `불필요한 항목 제거`
- `한글화 이미지 생성`
- `문자 판독하기`

## Early Lessons

### Runtime Captures Are Evidence, Not Edit Sources

Runtime/savestate-derived captures helped identify what the game displayed, but
they were repeatedly easy to confuse with direct ROM-editable assets. The safer
rule is:

- use runtime captures to locate and verify;
- use ROM-backed tile/RLE/LZ77 edit packs as the source of replacement truth;
- label runtime-derived folders as reference-only unless proven otherwise.

### Screen-Order Tilemaps Matter

GBA tile graphics are not always stored in visual reading order. Several image
extraction failures came from treating raw tile order as screen order. The stable
workflow needs tile data, tilemap/screenblock, palette, and scroll/fine-offset
context.

### 1x Source, Scaled Preview

The project mixed 1x editable source images with 4x/8x previews. That made GUI
download/upload behavior ambiguous. The lasting rule:

- source and replacement images should be 1x unless the target explicitly says
  otherwise;
- scaled files are preview-only and should be regenerable.

### Palette Bank Is Part of the Asset

The `돌` vs `금속` color mismatch was not a font problem. It came from different
palette mapping context. For 4bpp assets, the same RGB source color can map to a
different nibble if the palette bank/context differs.

Required future rule:

- every image edit pack must record the palette source used for quantization;
- sibling UI assets should share a stable palette source when they are visually
part of the same component.

### Crop the Target, Not the Whole RLE Block

Large RLE blocks made drag-and-drop replacement too slow and sometimes forced
unnecessary repointing. Focused edit packs for small UI regions, such as
`POWER/파워`, were safer and faster.

Required future rule:

- when only a label changes, create a focused crop edit pack;
- preserve current ROM payload as the base when multiple edits share a block;
- avoid whole-block replacement unless the whole block is actually being edited.

### Running GUI State Can Lag Disk Data

Several moments looked like data was missing even though JSON files had been
updated. The likely cause was an already-running GUI server keeping old data in
memory.

Required future rule:

- after dataset structure changes, restart the GUI server or expose an explicit
  reload path;
- record whether a change is disk-only or live-server-visible.

### External Paths Are Provenance, Not Dependencies

Many manifests and docs contain absolute paths from the working machine. They can
be useful for history, but final scripts and reusable starter-kit logic must use
repo-relative paths or explicit user-provided inputs.

## Cleanup-Relevant Lessons

- Do not delete a confusing failed artifact until the mistake it represents is
  summarized.
- Do not keep every failed artifact just because it was painful to make.
- Keep minimal representative evidence, then remove reproducible generated bulk.
- The final repo should explain what is active, what is archived, and what is
  deliberately ignored.

