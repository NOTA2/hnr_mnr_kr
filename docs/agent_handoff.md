# Agent Handoff

이 파일은 **호환용 legacy handoff** 문서다.

새 세션의 실제 시작점은 [session_start.md](/Users/user/test/docs/session_start.md) 와 [active_task.md](/Users/user/test/docs/active_task.md) 이다.

## 현재 초점

- 메인: 공통 폰트 확장/재배치 경로 위에서 첫 한글 문자열 테스트 확장
- 병행: Registry A entry `8` cluster 라벨링 유지
- 보류: 새 text source 징후가 없으면 텍스트 추출 구조 분석 deep dive 는 잠시 내림

## 최근 핵심 판단

- 텍스트 추출 coverage 관점에서:
  - Registry A tail (`9..17`) 분류는 실질적으로 닫힘
  - Registry D entry `70` 판정도 실질적으로 닫힘
  - 아직 남은 핵심은 Registry A entry `8` cluster 장면/용도 라벨링과 실제 플레이 검증
- 폰트 관점에서:
  - 공통 `fnt` payload 는 mapped code `1698`, 현재 사용 `1411`, 미사용 `287`
  - glyph gap `0`, payload tail free `0`
  - 즉 code space 는 남지만 glyph space 가 먼저 막힌 상태
  - `relocate-chunk` 로 공통 font entry `0` 을 더 큰 위치로 옮기는 테스트는 성공
  - 단, `0x17C2F4` entry `0` 뿐 아니라 mirror table `0x1823A0` entry `0` 도 함께 갱신해야 함
  - `append-fnt-glyph-set` 과 [hangul_test.tbl](/Users/user/test/analysis/hangul_test.tbl) 로 `가/나/다` glyph 및 문자열 테스트 ROM 1건까지 확보함

## 바로 열 문서

- 기본: [active_task.md](/Users/user/test/docs/active_task.md)
- 텍스트 coverage: [text_extraction_coverage.md](/Users/user/test/analysis/text_extraction_coverage.md)
- 폰트 전략: [common_fnt_hangul_strategy.md](/Users/user/test/analysis/common_fnt_hangul_strategy.md)
- 폰트 트랙: [font_and_encoding_progress.md](/Users/user/test/docs/tracks/font_and_encoding_progress.md)

## 열지 말 것

- 시작 시 전체 [experiment_log.md](/Users/user/test/analysis/experiment_log.md) 를 읽지 않는다.
- 시작 시 대형 JSON을 직접 열지 않는다.
- world-map 구조 문서는 지금 작업이 막힐 때만 다시 연다.
