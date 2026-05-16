# Core UI Test ROM Matrix

2026-05-16 기준 core UI 한글 표시 테스트 ROM 요약.

중요:

- 스크린샷에서 보였던 이상한 `가` 는 **legacy placeholder test** (`hangul_test_ga.pgm`) 계열이다.
- 현재 `priority48/full80` production workbench 는 그 자산을 재사용하지 않는다.
- 최신 테스트 ROM 은 아래 matrix 또는 `scripts/build_core_ui_test_roms.sh` 로 다시 생성한 결과만 기준으로 본다.

## Startup Intro

- font ROM: `/Users/user/test/patched_roms/rebuild_check/hnr_font_startup_nanumsquare_font.gba`
- translations: [startup_intro_texts.json](/Users/user/test/analysis/startup_intro_texts.json)
- glyph table: [prepared.tbl](/Users/user/test/analysis/startup_intro_nanumsquare_workbench/prepared.tbl)
- glyph workbench: [startup_intro_nanumsquare_workbench](/Users/user/test/analysis/startup_intro_nanumsquare_workbench)
- source font: `NanumSquareR.ttf`

### 기본 번역

- output ROM: `/Users/user/test/patched_roms/rebuild_check/hnr_startup_intro_test.gba`
- report: [startup_intro_apply_report.json](/Users/user/test/analysis/startup_intro_apply_report.json)
- 결과: `4 in_place`

적용 문자열:

- `대륙력`
- `1910년 2월`
- `리젠불 마을`
- `형 11세    동생 10세`

이 화면은 게임 시작 직후 바로 보여서, 현재 **가장 빠른 첫 시각 QA 지점** 으로 추천한다.

고정 확인 오프셋:

- `0x703D70` -> `대륙력`
- `0x703D7E` -> `1910년 2월`
- `0x703D94` -> `리젠불 마을`
- `0x703DAC` -> `형 11세    동생 10세`

## Priority48

- font ROM: `/Users/user/test/patched_roms/rebuild_check/hnr_font_core_ui_priority48_font.gba`
- coverable translations: [core_ui_priority48_coverable_translations.json](/Users/user/test/analysis/core_ui_priority48_coverable_translations.json)
- table: [prepared.tbl](/Users/user/test/analysis/hangul_core_ui_priority48_workbench/prepared.tbl)

### 기본 번역

- output ROM: `/Users/user/test/patched_roms/rebuild_check/hnr_core_ui_priority48_text_test.gba`
- report: [core_ui_priority48_apply_report.json](/Users/user/test/analysis/core_ui_priority48_apply_report.json)
- 결과: `4 in_place`, `1 skipped_no_pointer`

### compact 번역

- output ROM: `/Users/user/test/patched_roms/rebuild_check/hnr_core_ui_priority48_compact_text_test.gba`
- translations: [core_ui_priority48_compact_test_translations.json](/Users/user/test/analysis/core_ui_priority48_compact_test_translations.json)
- report: [core_ui_priority48_compact_apply_report.json](/Users/user/test/analysis/core_ui_priority48_compact_apply_report.json)
- 결과: `5 in_place`

대표 확인 문자열:

- `통신 중...`
- `저장 중...`
- `리오르`
- `이스트 시티`
- `레돈도`

## Full80

- font ROM: `/Users/user/test/patched_roms/rebuild_check/hnr_font_core_ui_full80_font.gba`
- coverable translations: [core_ui_full80_coverable_translations.json](/Users/user/test/analysis/core_ui_full80_coverable_translations.json)
- table: [prepared.tbl](/Users/user/test/analysis/hangul_core_ui_workbench/prepared.tbl)

### 기본 번역

- output ROM: `/Users/user/test/patched_roms/rebuild_check/hnr_core_ui_full80_text_test.gba`
- report: [core_ui_full80_apply_report.json](/Users/user/test/analysis/core_ui_full80_apply_report.json)
- 결과: `15 in_place`, `4 skipped_no_pointer`

skip 원인:

- 번역문이 원문보다 약간 길어져 pointer repoint 가 필요했지만 direct pointer 검색이 실패한 케이스
- 대상:
  - `지금까지의 여정을 저장할까?`
  - `저장 중이다…`
  - `이대로 여행을 계속할까?`
  - `크루스 유적`

### compact 번역

- output ROM: `/Users/user/test/patched_roms/rebuild_check/hnr_core_ui_full80_compact_text_test.gba`
- translations: [core_ui_full80_compact_test_translations.json](/Users/user/test/analysis/core_ui_full80_compact_test_translations.json)
- report: [core_ui_full80_compact_apply_report.json](/Users/user/test/analysis/core_ui_full80_compact_apply_report.json)
- 결과: `19 in_place`

compact 대체 예:

- `지금까지의 여정을 저장할까?` -> `여정을 저장할까?`
- `저장 중이다…` -> `저장 중...`
- `이대로 여행을 계속할까?` -> `여행을 계속할까?`
- `크루스 유적` -> `크루스유적`

## 현재 추천

첫 실제 시각 QA는 `startup intro` 또는 `priority48 compact` ROM 기준으로 진행하는 편이 가장 안전하다.

가장 빠른 확인은 `startup intro` 다. 별도 메뉴 진입 없이 게임 시작 직후 바로 본다.

## 재생성

시작 화면만 빠르게 다시 만들 때:

```bash
zsh scripts/build_startup_intro_test.sh \
  "Hagane no Renkinjutsushi - Meisou no Rondo (Japan).gba" \
  patched_roms/rebuild_check
```

전체 matrix 를 한 번에 다시 만들 때:

```bash
zsh scripts/build_core_ui_test_roms.sh \
  "Hagane no Renkinjutsushi - Meisou no Rondo (Japan).gba" \
  patched_roms/rebuild_check
```

위 스크립트는 아래 산출물을 한 번에 다시 만든다.

- `font_expand_base.gba`
- `hnr_font_core_ui_priority48_font.gba`
- `hnr_font_core_ui_full80_font.gba`
- `hnr_font_startup_nanumsquare_font.gba`
- `hnr_core_ui_priority48_text_test.gba`
- `hnr_core_ui_priority48_compact_text_test.gba`
- `hnr_core_ui_full80_text_test.gba`
- `hnr_core_ui_full80_compact_text_test.gba`
- `hnr_startup_intro_test.gba`
