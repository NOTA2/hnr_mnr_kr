# Agent Handoff

이 파일은 호환용 handoff 문서다.

새 세션은 먼저 [session_start.md](/Users/user/test/docs/session_start.md) 와 [active_task.md](/Users/user/test/docs/active_task.md) 만 읽는다.

## 현재 초점

- 데이터 구조 조사
- 다음 작업: `0x184A0C` effect/overlay row 의 `word0` / `word3` 의미를 `0x047A88` 내부에서 좁히기

## 최근 검증

- `0x184A0C..0x184AD3` 은 `10 * 0x14` effect/overlay parameter table 후보로 굳어졌다.
- `0x06CFB8` 은 `0x03002FFC == 0x10` 일 때 `0x03005FF8` 를 row index 로 사용한다.
- `0x03005FF8` 은 독립 effect state 가 아니라 world-map 선택/hover location index byte 로 보는 해석이 강하다.
- 확인된 direct writer 는 `0x06A52E` 하나이며, hit-test loop index `0..9` 를 저장한다.
- `0x06CEC0` 은 selected index 를 current-location byte `0x03006020` 으로 복사한다.
- `find-u32-refs` CLI 가 추가되어 특정 `u32` literal hit 와 Thumb literal load 후보를 자동 추적할 수 있다.

## 바로 열 문서

- 기본: [active_task.md](/Users/user/test/docs/active_task.md)
- effect index 흐름: [effect_overlay_index_flow.md](/Users/user/test/analysis/effect_overlay_index_flow.md)
- location/world-map bundle 요약: [location_bundle_family.md](/Users/user/test/analysis/location_bundle_family.md)

## 열지 말 것

- 시작 시 전체 [experiment_log.md](/Users/user/test/analysis/experiment_log.md) 를 읽지 않는다.
- 시작 시 대형 JSON을 읽지 않는다.
- [current_constraints.md](/Users/user/test/analysis/current_constraints.md) 는 금지 가정 충돌을 확인할 때만 연다.

## 실수 방지

- `0x06B8B0` 시작부 `strb #0` 은 `0x03005FF8` 초기화가 아니라 `0x03005FE8` write 다.
- `0x06A5B2` 의 `strb #2` 는 `0x03006018 = 2` state write 다.
- direct ref 수가 적은 table 을 dead table 로 단정하지 않는다. static constant cluster 경유 소비 가능성이 있다.
