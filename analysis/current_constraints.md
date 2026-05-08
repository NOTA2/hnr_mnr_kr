# Current Constraints

이 문서는 **금지 가정과 현재 좁혀진 질문**만 담는다.

시작 시 기본으로 읽지 않는다. 판단이 충돌하거나 반복 실수 위험이 있을 때만 연다.

## 확실한 기준점

- 일부 텍스트는 `cp932 + 00` 평문이다.
- 일부 메뉴/진행 메시지는 명령 스트림 내부 `cp932` 문자열이며 `0x10` 구분자를 쓴다.
- `0x17C1C0` 은 예외적인 `length-pointer` 테이블이다.
- `0x076530` 은 상위 registry pointer hub 이고, `0x000290` / `0x0002CC` / `0x000304` family 가 일부 registry 를 고른다.
- `0x17785C` 는 전용 helper `0x03BC` / `0x0414` 를 가지며, 일부 경로는 DMA3 그래픽 복사다.
- `Registry B (0x17C384)` 는 `0x183D50` 미러와 `0x068DF8` ZP-aware helper 경로로 실제 소비된다.
- `0x184248..0x1843FF` 은 `10 * 0x2C` location record table 이고, `0x18425C` 는 첫 record 의 name field 다.
- `0x184888` 은 `10 * 10` route/path matrix 로 보는 해석이 강하다.
- `0x1849D4` 는 `(location_index, special event/script/message id)` 매핑으로 보는 해석이 강하다.
- `0x184A0C..0x184AD3` 은 `10 * 0x14` effect/overlay parameter table 후보다.
- `0x03005FF8` 은 world-map 선택/hover location index byte 로 보는 해석이 강하다.
- `0x184A0C` row `word0` 은 location 대표 hotspot/cell id 로 보는 해석이 강하다.

## 반복 금지

- 모든 텍스트 뱅크가 같은 구조라고 가정하지 않는다.
- `0x17Cxxx` 주변 디스크립터가 모두 같은 레이아웃이라고 가정하지 않는다.
- `0x03BC` 단독 호출부가 곧바로 순수 문자열 포인터를 반환한다고 가정하지 않는다.
- `0x1840E8..` 전체를 한 종류의 descriptor 배열로 보지 않는다.
- `0x18425C` 를 standalone string bank 로 보지 않는다.
- `0x184420` 을 route edge table 로 보지 않는다. 현재는 hotspot/cell id -> location index lookup 이다.
- `0x1844B0..0x1847F7` 을 opcode script 로 단정하지 않는다. 현재는 node path list 해석이 강하다.
- `field3` 를 location 활성 플래그로 보지 않는다. 활성 여부는 `0x030009A0` runtime array 쪽이다.
- `0x184A0C` 를 텍스트 후보나 포인터 배열로 보지 않는다.
- `0x06B8B0` 시작부 `strb #0` 을 `0x03005FF8` 초기화로 보지 않는다.
- `0x06A5B2` 의 `strb #2` 를 `0x03005FF8` write 로 보지 않는다.

## 현재 질문

1. `0x184A0C` row 의 `word3` 이 `0x02B96C` / `0x0383F8` 경로에서 어떤 subresource variant 를 고르는가
2. `0x1849A0` handler table 의 static cluster 슬롯을 실제로 소비하는 코드는 어디인가
3. `field3` 가 palette bank 인지, palette + subtype 복합 값인지 더 좁힐 수 있는가
4. `0x47EB0` 가 `0x3E1..0x3EF` 를 어떤 런타임 객체로 바꾸는가
5. `0x093D` / `0x093E` / `0x094B` 고정 리소스 관계는 무엇인가

## 전체 근거

- 위치/월드맵 구조: [location_bundle_family.md](/Users/user/test/analysis/location_bundle_family.md)
- effect index 흐름: [effect_overlay_index_flow.md](/Users/user/test/analysis/effect_overlay_index_flow.md)
- registry 구조: [resource_registry_map.md](/Users/user/test/analysis/resource_registry_map.md)
- 상세 실험 기록: [experiment_log.md](/Users/user/test/analysis/experiment_log.md)
