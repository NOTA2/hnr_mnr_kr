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

1. `0x184A0C` effect/overlay row 의 `word4` tracked slot side-path 와 `+0x33C/+0x33E` writer / promotion path 추가 분리
2. `0x1849A0` handler table static cluster slot 소비 경로 찾기
3. `field3` exact palette/subtype 의미 추가 분리
4. `0x093D` / `0x093E` / `0x094B` 고정 리소스 관계 확인

## 최근 핵심 진전

- `0x184A0C..0x184AD3` 을 `10 * 0x14` effect/overlay parameter table 후보로 분리했다.
- `0x03005FF8` 은 world-map 선택/hover location index byte 로 보는 해석이 강해졌다.
- 확인된 direct writer 는 `0x06A52E` 이며, hit-test loop index `0..9` 를 저장한다.
- `0x06CEC0` 은 selected index 를 current-location byte `0x03006020` 으로 복사한다.
- `0x184A0C` row `word0` 은 `0x184420` hotspot/location lookup 과 row별로 정확히 맞아 location 대표 hotspot/cell id 로 좁혀졌다.
- `word1` / `word2` 는 sign-extended integer 좌표쌍이며, runtime object 에는 float 형태로 저장된다는 해석이 가장 강하다.
- `word3` 은 `0x02B96C` 내부에서 `& 7` 로 제한된 뒤 `0x0383F8 -> 0x1824F0` 8-entry accessor table 로 이어진다.
- 이 accessor 들은 공통 descriptor 의 halfword field `+0x04 .. +0x12` 에서 low 10-bit 값을 읽으므로, `word3` 은 descriptor field selector 로 보는 해석이 가장 강하다.
- 현재 effect/overlay row 에서 실제 사용된 `word3` 값은 `0` 과 `6` 뿐이다.
- `word4 != 0` side-path 는 `0x03001450 + 0x33C/+0x33E` 의 raw tracked slot id 두 개를 읽어, 나머지 slot `8..23` 의 병렬 block 을 지우는 maintenance 경로로 좁혀졌다.
- `0x044320` / `0x0443B4` / `0x03D6F0` 는 같은 tracked slot record 플래그를 set/check/sync 하는 helper 군으로 보는 해석이 강하다.
- `0x03D6F0` 첫 비교는 `cmp` 가 아니라 `cmn` 이므로, `+0x33E` 는 `-1` sentinel 을 갖는 optional second tracked slot field 후보로 좁혀졌다.
- `0x0443F8` 는 tracked slot `0x33C/+0x33E` 를 피해서 slot `0..15` 후보를 훑는 allocator 로 보이며, 선택 결과를 `0x03005284` 에 남긴다.
- `0x03005240` 은 이 allocator 가 갱신하는 `16 * 4-byte` per-slot state table 후보로 좁혀졌다.
- `0x0443F8` direct caller 는 현재 `0x059034` 하나이며, caller 는 반환 slot id 를 `slot + 0x5A` runtime id 로 변환해 후속 object 구축에 사용한다.
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
