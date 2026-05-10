# Core UI Test ROM Matrix

2026-05-10 기준 core UI 한글 표시 테스트 ROM 요약.

## Priority48

- font ROM: `/private/tmp/hnr_font_core_ui_priority48_font.gba`
- coverable translations: [core_ui_priority48_coverable_translations.json](/Users/user/test/analysis/core_ui_priority48_coverable_translations.json)
- table: [prepared.tbl](/Users/user/test/analysis/hangul_core_ui_priority48_workbench/prepared.tbl)

### 기본 번역

- output ROM: `/private/tmp/hnr_core_ui_priority48_text_test.gba`
- report: [core_ui_priority48_apply_report.json](/Users/user/test/analysis/core_ui_priority48_apply_report.json)
- 결과: `4 in_place`, `1 skipped_no_pointer`

### compact 번역

- output ROM: `/private/tmp/hnr_core_ui_priority48_compact_text_test.gba`
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

- font ROM: `/private/tmp/hnr_font_core_ui_full80_font.gba`
- coverable translations: [core_ui_full80_coverable_translations.json](/Users/user/test/analysis/core_ui_full80_coverable_translations.json)
- table: [prepared.tbl](/Users/user/test/analysis/hangul_core_ui_workbench/prepared.tbl)

### 기본 번역

- output ROM: `/private/tmp/hnr_core_ui_full80_text_test.gba`
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

- output ROM: `/private/tmp/hnr_core_ui_full80_compact_text_test.gba`
- translations: [core_ui_full80_compact_test_translations.json](/Users/user/test/analysis/core_ui_full80_compact_test_translations.json)
- report: [core_ui_full80_compact_apply_report.json](/Users/user/test/analysis/core_ui_full80_compact_apply_report.json)
- 결과: `19 in_place`

compact 대체 예:

- `지금까지의 여정을 저장할까?` -> `여정을 저장할까?`
- `저장 중이다…` -> `저장 중...`
- `이대로 여행을 계속할까?` -> `여행을 계속할까?`
- `크루스 유적` -> `크루스유적`

## 현재 추천

첫 실제 시각 QA는 `priority48 compact` 또는 `full80 compact` ROM 기준으로 진행하는 편이 가장 안전하다.
