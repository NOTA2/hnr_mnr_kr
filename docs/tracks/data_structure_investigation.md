# Data Structure Investigation

이 트랙 문서는 데이터 구조 조사의 **현재 지도**만 담는다.

시작 시 기본으로 읽지 않는다. 구체 작업은 [active_task.md](/Users/user/test/docs/active_task.md) 를 따른다.

## 상태

- 상태: `IN PROGRESS`
- 현재 초점: `0x184A0C` effect/overlay row 의 `word4` side-path exact 의미와 `word1 low nibble` 오해 정리

## 텍스트 구조

- 일부 문자열은 `cp932 + 00 terminator` 평문이다.
- 일부 메뉴/진행 메시지는 명령 스트림 내부 `cp932` 문자열이며 `0x10` 구분자를 쓴다.
- `0x3D2036`, `0x3D2D60`, `0x3D327E` 계열은 단순 절대 포인터 뱅크가 아니라 인덱스/레코드/상대 오프셋 기반 mixed resource 가능성이 높다.

## Registry / Resource 구조

- `0x17C1C0` 은 예외적인 `length-pointer` 테이블이다.
- `0x076530` 은 상위 registry hub 이며, `0x000290` / `0x0002CC` / `0x000304` helper family 가 일부 registry 를 고른다.
- `0x17785C` 는 `0x03BC` / `0x0414` 전용 accessor 를 가지며, 일부 호출부는 DMA3 그래픽 복사다.
- `Registry B (0x17C384)` 는 `0x183D50` 미러와 `0x068DF8` helper 경로로 소비된다.
- `0x068DF8` 는 엔트리 선두 `ZP` 를 검사해 decode 또는 raw fallback 으로 분기한다.

## Location / World-Map 구조

- `0x184248..0x1843FF`: `10 * 0x2C` location record table
- `0x18425C`: 첫 location record 의 name field
- `0x184420..0x1844AF`: hotspot/cell id -> location index lookup
- `0x1844B0..0x1847F7`: route path byte sequence region
- `0x184820`: `13 * (x, y)` node/cursor anchor 후보
- `0x184888`: `10-entry` route block table, 각 block 은 `10-slot` matrix
- `0x1849A0`: `13-entry` Thumb handler pointer table 후보
- `0x1849D4`: `(location_index, special event/script/message id)` table
- `0x184A0C..0x184AD3`: `10 * 0x14` effect/overlay parameter table

## 현재 가장 중요한 해석

- `0x03005FF8` 은 effect 전용 state 가 아니라 world-map 선택/hover location index byte 로 보는 해석이 강하다.
- `0x06A52E` 가 `0x03005FF8` 의 확인된 direct writer 이며, hit-test loop index `0..9` 를 저장한다.
- `0x06CEC0` 은 selected index 를 current-location byte `0x03006020` 으로 복사한다.
- `0x06CFB8` 은 selected index 로 `0x184A0C + index * 0x14` row 를 읽고 `0x047A88` 에 전달한다.
- `0x184A0C` row `word0` 은 `0x184420` hotspot/location lookup 의 hotspot id 와 row별로 정확히 맞으므로, location 대표 hotspot/cell id 로 보는 해석이 강하다.
- `word1` / `word2` 는 `0x047A88` 안에서 각각 한 번만 읽히고, sign-extended 16-bit pair 로 `0x0587BC` 에 함께 전달된다.
- `0x0587BC` 는 두 축에 scalar transform helper `0x075560` 을 적용한 뒤, active object/entry 의 `+0x08` / `+0x0C` 에 결과를 저장한다.
- `0x075560` 은 signed int 를 IEEE-754 single float bit pattern 으로 포장하는 helper 로 보인다.
- 따라서 `word1` / `word2` 는 현재 **직접적인 signed integer 좌표쌍** 으로 보는 해석이 가장 강하다.
- `0x03CA68` dispatch table 분석은 helper-family 차원에서는 유효하지만, `0x047A88` effect row 경로의 실제 `0x02B96C` call site 는 두 번째 인자 `r1 = 0` 으로 고정된다.
- 따라서 이전의 "`word1 low nibble` 이 effect row 경로에서 dispatch 를 고른다"는 해석은 현재 철회하는 편이 안전하다.
- `word4` 는 `0x047A88` 안에서 한 번만 읽히며, `0` 여부에 따라 tracked slot 두 개를 제외한 slot `8..23` clearing side-path 를 켠다.
- `0x03001450 + 0x33C/+0x33E` 는 이 side-path 안에서 `+8` 보정 후 실제 slot `8..23` 과 직접 비교되므로, 적어도 **raw tracked slot id 2개** 로 보는 해석이 강하다.
- `0x044320(slot, flag)` 는 `+0x0574 + (slot + 8) * 0x34` record 플래그를 clear/set 하고, `0x0443B4(slot)` 는 같은 플래그를 검사하는 helper 로 보는 해석이 강하다.
- `0x03D6F0` 는 `+0x33E` 와 `+0x33C` 를 함께 읽어 tracked slot 상태를 맞추는 보조 루틴처럼 보인다.
- 이 루틴의 첫 비교는 `cmp` 가 아니라 `cmn` 이므로, 실제 특수값은 `+0x33E == -1` sentinel 로 읽는 편이 자연스럽다.
- 따라서 `+0x33E` 는 optional second tracked slot field 후보로 더 좁혀졌다.
- `0x0443F8` 는 `0x0300503C` iterator 로 slot `0..15` 후보를 훑는 allocator 로 보인다.
- 이 allocator 는 tracked slot `0x33C/+0x33E` 와 충돌하는 후보를 제외하고, `0x03005240` per-slot state table 과 slot record / 위치 조건을 검사한 뒤 결과를 `0x03005284` 에 `slot id` 또는 `-1` sentinel 로 남긴다.
- 현재 확인된 `0x0443F8` direct caller 는 `0x059034` 하나이며, caller 는 반환 slot id 를 `slot + 0x5A` runtime id 로 변환해 후속 object 구축에 쓴다.
- `0x045B98` / `0x047A28` 등은 `0x03005284` 를 consumer 로 읽는다.
- `0x044B7C` 는 시작부터 `0x33E` 를 읽어 `0x714` table 기반 후속 object 흐름으로 들어가므로, `+0x33E` 는 optional second tracked slot consumer 경로도 가진다.
- 따라서 `word4` 는 현재 **overlay slot maintenance mode flag** 로 보는 해석이 가장 강하다.
- `word3` 은 `0x02B96C` 에 세 번째 인자로 전달되고 `& 7` 로 제한된 뒤, `0x0383F8 -> 0x1824F0` 8-entry accessor table 로 이어진다.
- 이 accessor 들은 공통 descriptor 의 halfword field `+0x04` 부터 `+0x12` 까지 low 10-bit 값을 읽으므로, `word3` 은 사실상 **descriptor field selector** 로 보는 해석이 가장 강하다.
- 현재 effect/overlay row 에서는 `word3 = 0` 이 기본이고, row `2` 만 `word3 = 6` 을 사용한다.

## 다음 질문

1. `0x184A0C` row 의 `word4` side-path 가 보존/삭제하는 slot 군의 역할과 `+0x33C/+0x33E` tracked field writer / promotion path
2. `0x03CA68` helper-family 분석을 effect row 경로와 분리해서 어떻게 기록할지 정리
3. `0x1849A0` handler table 의 static cluster slot 소비 경로
4. `field3` exact palette/subtype 의미
5. `0x093D` / `0x093E` / `0x094B` 고정 리소스 관계

## 자세한 근거

- 전체 참고 맵: [reference_map.md](/Users/user/test/docs/reference_map.md)
- location/world-map bundle: [location_bundle_family.md](/Users/user/test/analysis/location_bundle_family.md)
- effect index 흐름: [effect_overlay_index_flow.md](/Users/user/test/analysis/effect_overlay_index_flow.md)
- registry 구조: [resource_registry_map.md](/Users/user/test/analysis/resource_registry_map.md)
- 실험 로그: [experiment_log.md](/Users/user/test/analysis/experiment_log.md)
