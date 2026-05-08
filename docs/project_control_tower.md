# Project Control Tower

이 문서는 장기 대시보드다.

새 세션의 시작점은 [session_start.md](/Users/user/test/docs/session_start.md) 이고, 실제 다음 작업은 [active_task.md](/Users/user/test/docs/active_task.md) 를 따른다.

## 단계

- 데이터 구조 조사: `IN PROGRESS`
- 텍스트 추출: `IN PROGRESS`
- 텍스트 재삽입: `BOOTSTRAPPED`
- 폰트/문자 매핑: `NOT STARTED`
- 이미지 리소스: `NOT STARTED`
- GUI/작업 워크플로우: `DEFERRED`

## 현재 우선순위

1. `0x184A0C` effect/overlay row 의 `word3` object/subresource variant 의미 확인
2. `0x1849A0` handler table static cluster slot 소비 경로 찾기
3. `field3` exact palette/subtype 의미 추가 분리
4. `0x093D` / `0x093E` / `0x094B` 고정 리소스 관계 확인

## 최근 핵심 진전

- `0x184A0C..0x184AD3` 을 `10 * 0x14` effect/overlay parameter table 후보로 분리했다.
- `0x03005FF8` 은 world-map 선택/hover location index byte 로 보는 해석이 강해졌다.
- 확인된 direct writer 는 `0x06A52E` 이며, hit-test loop index `0..9` 를 저장한다.
- `0x06CEC0` 은 selected index 를 current-location byte `0x03006020` 으로 복사한다.
- `0x184A0C` row `word0` 은 `0x184420` hotspot/location lookup 과 row별로 정확히 맞아 location 대표 hotspot/cell id 로 좁혀졌다.
- `word3` 은 `0x02B96C` 내부에서 `& 7` 로 제한되어 `0x0383F8` 로 넘어가는 3-bit object/subresource variant 후보가 됐다.
- `find-u32-refs` CLI 로 `u32` literal hit 와 Thumb literal load 후보를 추적할 수 있게 했다.

## 안정화된 큰 구조

- `0x17C1C0`: 예외적인 `length-pointer` 리소스 디스크립터
- `0x076530`: 상위 registry hub
- `0x17785C`: `0x03BC` / `0x0414` 전용 accessor 축
- `0x183D50`: Registry B 미러, `0x068DF8` ZP-aware helper 경로
- `0x184248..`: location/world-map bundle
- `0x3Dxxxx`: 텍스트와 binary record 가 섞인 mixed resource 구간

## 운영 정책

- 시작 시 이 문서를 읽지 않는다.
- 단계나 우선순위가 바뀐 경우에만 갱신한다.
- 매 실행마다 갱신해야 하는 문서는 [active_task.md](/Users/user/test/docs/active_task.md) 이다.
