# Hangul Core UI Priority Plan

core UI 한글 glyph 제작은 현재 두 단계로 나눈다.

## 세트

- `priority24`
  - 파일: [hangul_core_ui_priority24_manifest.json](/Users/user/test/analysis/hangul_core_ui_priority24_manifest.json)
  - workbench: [hangul_core_ui_priority24_workbench](/Users/user/test/analysis/hangul_core_ui_priority24_workbench)
  - 목적: 아주 작은 첫 아트 패스
  - 한계: 현재 완성 문장 커버 `0`

- `priority48`
  - 파일: [hangul_core_ui_priority48_manifest.json](/Users/user/test/analysis/hangul_core_ui_priority48_manifest.json)
  - workbench: [hangul_core_ui_priority48_workbench](/Users/user/test/analysis/hangul_core_ui_priority48_workbench)
  - 목적: 첫 실제 문자열 테스트 가능 배치
  - 현재 완성 문장 커버 `5`

- `full80`
  - 파일: [hangul_core_ui_seed_manifest.json](/Users/user/test/analysis/hangul_core_ui_seed_manifest.json)
  - workbench: [hangul_core_ui_workbench](/Users/user/test/analysis/hangul_core_ui_workbench)
  - 목적: 현재 core UI 번역 초안 전체 대응
  - 현재 완성 문장 커버 `19`

## 현재 커버 요약

근거 파일: [hangul_core_ui_priority_coverage.json](/Users/user/test/analysis/hangul_core_ui_priority_coverage.json)

- `priority24`: `0`
- `priority48`: `5`
- `full80`: `19`

`priority48` 에서 바로 테스트 가능한 대표 문자열:

- `통신 중...`
- `저장 중이다…`
- `리오르`
- `이스트 시티`
- `레돈도`

## 권장 순서

1. `priority48` workbench glyph 를 먼저 다듬는다.
2. 그 세트로 첫 품질 있는 in-game 문자열 테스트를 한다.
3. 이후 `full80` 으로 확장한다.
