# Font Asset Workflow

이 문서는 **현재 확정된 한글 폰트 제작 방식**만 짧게 정리한다.

## 현재 기준

- active 한글 glyph source 는 [maruminyahangul_12x12.png](/Users/user/test/third_party/font_atlases/maruminyahangul_12x12.png) 하나다.
- 기준 설정은 [active_hangul_font_profile.json](/Users/user/test/confirmed_data/font_assets/active_hangul_font_profile.json) 에 있다.
- 예전 벡터 폰트 seed 비교 결과는 [analysis/archive/font_trials/2026-05-17_pre_bitmap_lock](/Users/user/test/analysis/archive/font_trials/2026-05-17_pre_bitmap_lock) 아래로 내렸다.

## 원칙

1. 전체 `11172`자를 ROM 에 한 번에 넣지 않는다.
2. 실제 번역 JSON 에서 쓰인 한글만 subset 으로 추출한다.
3. 그 subset 을 active atlas 에서 잘라 `PGM 12x12` workbench 로 만든다.
4. 사람이 glyph editor 로 손본 뒤 ROM 에 append 한다.

## 기본 경로

### startup intro active workbench 재생성

```bash
zsh scripts/rebuild_active_workbenches_from_atlas.sh
```

이 명령은 아래 active 경로를 새 atlas 기준으로 다시 만든다.

- [startup_intro_active_workbench](/Users/user/test/analysis/startup_intro_active_workbench)
- [hangul_core_ui_priority48_workbench](/Users/user/test/analysis/hangul_core_ui_priority48_workbench)
- [hangul_core_ui_workbench](/Users/user/test/analysis/hangul_core_ui_workbench)

### 임의의 번역 JSON 에서 workbench 생성

```bash
python3 scripts/build_workbench_from_active_atlas.py \
  analysis/generated_workbenches/core_ui_active \
  confirmed_data/translation_worksets/translation_workset_core_ui.json
```

생성물:

- `seed_manifest.json`
- `prepared_manifest.json`
- `prepared.tbl`
- `workbench_report.json`

### 번역 JSON 을 active atlas 로 바로 ROM 에 적용

```bash
zsh scripts/build_translated_rom_with_active_atlas.sh \
  "Hagane no Renkinjutsushi - Meisou no Rondo (Japan).gba" \
  confirmed_data/translation_worksets/translation_workset_core_ui.json \
  patched_roms/core_ui_active \
  core_ui_active
```

결과:

- [core_ui_active_translated.gba](/Users/user/test/patched_roms/core_ui_active/core_ui_active_translated.gba)
- glyph audit / font append / apply report 일체

## 편집

glyph 수동 수정은 그대로 glyph editor 를 쓴다.

```bash
python3 scripts/run_glyph_editor.py \
  --manifest analysis/startup_intro_active_workbench/prepared_manifest.json
```

기본 active manifest 는 atlas 기반 startup intro workbench 다.

## 문자 집합 관리

- 지금 atlas 는 `12x12`, `64`열, row-major `U+AC00..U+D7A3` 순서다.
- 따라서 giant 문자 목록을 별도 텍스트 파일로 계속 들고 가기보다,
  [maruminyahangul_12x12.metadata.json](/Users/user/test/third_party/font_atlases/maruminyahangul_12x12.metadata.json)
  과 [active_hangul_font_profile.json](/Users/user/test/confirmed_data/font_assets/active_hangul_font_profile.json)
  두 파일로 규칙을 관리한다.
- 나중에 다른 atlas 가 비표준 순서라면 그때만 별도 explicit mapping table 이 필요하다.
