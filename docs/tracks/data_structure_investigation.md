# Data Structure Investigation

이 트랙 문서는 데이터 구조 조사의 **현재 지도**만 담는다.

시작 시 기본으로 읽지 않는다. 구체 작업은 [active_task.md](/Users/user/test/docs/active_task.md) 를 따른다.

## 상태

- 상태: `IN PROGRESS`
- 현재 초점: `0x184A0C` effect/overlay row 세부 의미

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
- `word3` 은 `0x02B96C` 에 세 번째 인자로 전달되고 `& 7` 로 제한되므로, 3-bit object/subresource variant index 후보로 둔다.

## 다음 질문

1. `0x184A0C` row 의 `word3` object/subresource variant 의미
2. `0x1849A0` handler table 의 static cluster slot 소비 경로
3. `field3` exact palette/subtype 의미
4. `0x47EB0` / `0x561D4` helper 의미
5. `0x093D` / `0x093E` / `0x094B` 고정 리소스 관계

## 자세한 근거

- 전체 참고 맵: [reference_map.md](/Users/user/test/docs/reference_map.md)
- location/world-map bundle: [location_bundle_family.md](/Users/user/test/analysis/location_bundle_family.md)
- effect index 흐름: [effect_overlay_index_flow.md](/Users/user/test/analysis/effect_overlay_index_flow.md)
- registry 구조: [resource_registry_map.md](/Users/user/test/analysis/resource_registry_map.md)
- 실험 로그: [experiment_log.md](/Users/user/test/analysis/experiment_log.md)
