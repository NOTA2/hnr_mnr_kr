# Current Constraints

이 문서는 **지금 시점에 꼭 기억해야 하는 사실, 금지 가정, 미해결점**만 짧게 모은 작업용 요약이다.

전체 이력은 [experiment_log.md](/Users/user/test/analysis/experiment_log.md) 에 남긴다.

## 지금 확실한 사실

1. 일부 문자열은 `cp932 + 00` 평문이다.
2. 일부 메뉴/진행 메시지는 명령 스트림 내부 `cp932` 문자열이며 `0x10` 구분자를 쓴다.
3. `0x18425C` 지역명 뱅크는 절대 포인터가 확인됐다.
4. `0x3D2036` 전투 뱅크와 `0x3D327E` 능력 뱅크는 일반 절대 포인터가 바로 안 잡힌다.
5. `0x17C1C0` 테이블은 `length-pointer` 이고, 엔트리들이 서로 겹친다.
6. `0x076530` 부근에는 여러 상위 레지스트리 경계를 가리키는 포인터 허브가 있다.
7. `0x17C2F4`, `0x17C384`, `0x17C71C`, `0x17C7E4` 이후 상위 레지스트리들은 `pointer-length` 쪽이 맞다.
8. `0x17785C` 레지스트리에는 실제 Thumb accessor `0x03BC`, `0x0414` 가 있다.
9. `0x17CE0` 는 `base + 2 * (x + y * 32)` 목적지 주소를 계산한다.
10. `0x17EB4` / `0x017ED8` / `0x017EEC` 는 `0x17785C` 포인터/길이 엔트리를 DMA3 로 halfword 복사한다.
11. `0x03E8` helper 는 literal base `0x17C7E4` 를 사용하고, 현재 BL 호출자 `3`개 (`0x0106E6`, `0x010798`, `0x010892`) 가 확인되었다.
12. `0x007760` 단독 accessor 경로는 고정 index `0x093D` (`0x3D2A40`, 길이 `0x0320`) binary table 을 읽는다.
13. `0x007824` 단독 accessor 경로는 고정 index `0x093E` (`0x3D2D60`, 길이 `0x06C0`) 를 읽으며, 앞쪽 `7-byte` 레코드와 뒤쪽 `cp932` 문자열 영역을 함께 쓴다.
14. `0x007578` 단독 accessor 경로는 고정 index `0x094B` (`0x3DDB30`, 길이 `0x02C3`) binary table 을 읽으며 직접 평문 텍스트 경로는 아니다.
15. `0x0002C0` 의 `0x076530` 포인터는 `0x000290` helper 의 literal 이며, 이 helper 는 허브 첫 4엔트리 (`0x17785C`, `0x17C2F4`, `0x17C384`, `0x17C71C`) 중 하나를 선택해 반환한다.
16. `0x0002CC` / `0x000304` 는 `0x000290` 위에 쌓인 generic accessor 로, 선택된 registry 엔트리의 `pointer` / `length` 필드를 읽는다.
17. `0x17C7E4` 는 허브 안에 있으나 generic `0x000290` family 가 선택하는 첫 4엔트리에는 포함되지 않고, 별도 direct helper 계열로 관리되는 것으로 보인다.
18. direct `0x0002CC` 호출 `20`개 중 현재 고정 selector 로 확인된 값은 `1` 과 `3` 뿐이다.
19. `selector=1` direct 호출 `8`개는 모두 `entry_index=0` 으로 `Registry A (0x17C2F4)` 첫 엔트리를 읽는다.
20. `selector=3` direct 호출 `11`개는 `entry_index 0/2/3/5` 를 읽으며, `0x06F4xx` / `0x0704xx` / `0x0709xx` 군집으로 몰려 있다.
21. `0x000304` 의 유일한 BL 호출자는 `0x000392` 이며, 이는 `0x00033C` wrapper 내부 길이 조회다.
22. `0x00033C` 호출자 `6`개는 현재 모두 `selector=3` 을 넘긴다.
23. `selector=0` direct generic caller 부재는 `0x17785C` 전용 helper (`0x03BC`, `0x0414`) 가 이미 널리 쓰인다는 점으로 설명 가능하다.
24. `Registry B (0x17C384)` 의 `115`개 엔트리는 `0x183D50` 에 완전히 같은 `pointer-length` 미러 테이블로 한 번 더 저장되어 있다.
25. `0x183D50` 미러 테이블은 direct 포인터 참조 `22`개가 확인되며, 이는 `0x17C384` 의 허브 참조 `1`건보다 훨씬 강한 live access 근거다.
26. 공용 helper `0x068DF8` 는 `0x183D50 + index * 8` 엔트리를 읽고, 선두 2바이트가 `ZP` 인지 검사해 decode 또는 raw fallback 으로 분기한다.
27. `0x068DF8` BL 호출자는 현재 `38`개다.
28. `0x183D50` 미러 엔트리 중 `50 / 115`개가 `ZP00` 또는 `ZP01` 로 시작한다.
29. 따라서 `Registry B` 는 concrete access route 가 비어 있는 축이 아니라, **미러 테이블 + ZP-aware helper** 경로로 접근되는 mixed compressed/raw asset bank 로 보는 편이 맞다.
30. `0x068DF8` caller 들은 전부 같은 성격이 아니며, 고정 index 호출과 descriptor/global 기반 동적 index 호출이 섞여 있다.
31. `0x1840F8..0x1841E7` 구간은 `15 * 16-byte` companion descriptor 배열로 읽히며, 각 row 는 `destination_vram + registry_b_index + dim_a + dim_b` 패턴을 가진다.
32. `0x1841E8..0x18421F` 구간은 `7 * 8-byte` companion descriptor 배열로 읽히며, 각 row 는 `registry_b_index + destination_palette_ram` 패턴을 가진다.
33. `0x184220` 이후에는 다른 metadata 와 문자열이 섞이기 시작하므로, `0x1840E8..` 전체를 한 가지 uniform struct 로 다시 다루면 안 된다.
34. `0x184220..0x184244` 구간에는 `3, 4, 0, 2, 7, 9, 5, 1, 6, 8` 값의 `10-entry` permutation/order table 이 있다.
35. `0x184248..0x1843FF` 구간은 `10 * 0x2C` fixed-size location record table 이며, 각 row 는 `5 * u32 metadata + 0x18-byte name field` 구조로 읽힌다.
36. 기존 `0x18425C` 지역명 문자열은 독립 뱅크라기보다 첫 location record 의 name field (`record + 0x14`) 다.
37. `0x184248` record base direct ref 는 `12`개, `0x18425C` 첫 name field direct ref 는 `4`개가 확인되므로, 실제 소비 단위는 문자열보다 record table 쪽일 가능성이 높다.
38. `0x184420..0x1844AF` 구간의 `18 * (u32, u32)` table 은 현재 `(hotspot_id, location_index)` 변환표로 보는 해석이 가장 강하다.
39. `0x1844B0..0x1847F7` 구간은 `FF` 종료 경로 시퀀스가 밀집한 route region 으로 보는 편이 더 자연스럽다.
40. `0x184888` 에는 `10-entry` route script block pointer table 이 있고, 각 block 은 다시 `10-slot` pointer matrix 로 읽힌다.
41. 이 matrix 의 non-null slot 은 `0x1844B0..0x1847F7` 시퀀스를 가리키며, 각 block 에서 자기 자신의 slot 하나만 `null` 이다.
42. route 시퀀스는 `FF` 를 제외하면 현재 `0..12` 값만 사용한다.
43. 따라서 `0x184888` 구조는 opcode script 보다 `10개 location 간 이동 경로를 13개 node 위에서 나열한 path matrix` 로 보는 해석이 더 강하다.
44. `0..9` 는 location node, `0x0A..0x0C` 는 connector / transit node 후보로 두는 해석이 가장 자연스럽다.
45. `0x184820` node position pair table 후보는 `13 * (x, y)` 구조이며, location record `field1/field2` 와 `8 / 10` 완전 일치, 나머지 `2 / 10` 은 작은 delta 만 가진다.
46. 코드 기준으로 `field1/field2` 는 location icon / hotspot 사각형의 좌상단 좌표로 보는 편이 더 정확하다. `0x06A418` hit-test 루틴이 descriptor `(dim_a, dim_b) * 8` 과 함께 이 두 필드를 직접 비교한다.
47. `field0`, `field3`, `field4` 는 좌표보다 draw helper 파라미터 쪽에 가깝다. `0x069E9C` / `0x06D4A8` 계열이 이 필드들을 helper `0x63000` / `0x63424` 로 직접 넘긴다.
48. 현재 가장 안전한 해석은 `field0 = asset/icon family ID 후보`, `field3 = draw subtype/mode 후보`, `field4 = graphic/tile-base variant 후보` 다.
49. `0x184950` 에는 `10 * (x, y)` label position pair 후보가 있다.
50. `0x1849A0` 에는 `13-entry` Thumb handler pointer table 이 있고, 현재는 위 `13-node` 축과 맞물릴 가능성을 우선 둔다.
51. `0x1849D4` table 은 현재 `(location_index, special event/script/message id)` 로 보는 해석이 가장 강하다.
52. `0x06D5A8` 루틴은 `0x1849D4` 의 둘째 필드 (`0x3E1..0x3EF`) 를 helper `0x47EB0` 에 넘겨 런타임 값을 얻고, 그 결과를 첫 필드 location index 로 색인되는 배열 슬롯에 저장한다.
53. `0x06A838` helper 는 `0x030009A0 + location_index * 4` 플래그를 읽어 location 활성 여부를 판정한다. 따라서 활성/비활성은 `field3` 가 아니라 별도 플래그 배열이 맡는다.

## 지금 반복하면 안 되는 가정

1. 모든 텍스트 뱅크가 같은 구조라고 가정하지 않는다.
2. `0x17Cxxx` 주변 디스크립터가 모두 같은 레이아웃이라고 가정하지 않는다.
3. `text_hits > 0` 만으로 새 텍스트 뱅크라고 확정하지 않는다.
4. `0x17C1C0` 을 공통 상위 레지스트리의 메인 경로라고 단정하지 않는다.
5. `0x17C7E4` 도 `0x17785C` 와 같은 accessor 패턴일 거라고 가정하지 않는다.
6. `0x03BC` 단독 호출부가 곧바로 순수 문자열 포인터를 반환한다고 가정하지 않는다.
7. `0x076530` 허브의 모든 포인터가 같은 helper family 에서 직접 사용된다고 가정하지 않는다.
8. `0x0002CC` generic accessor 가 모든 registry selector 를 비슷한 빈도로 쓸 거라고 가정하지 않는다.
9. `0x1840E8..` 전체를 한 종류의 descriptor 배열이라고 가정하지 않는다.
10. `0x18425C` 지역명 구간을 순수 standalone string bank 라고 가정하지 않는다.
11. `field1/field2` 를 단순 ID 라고 가정하지 않는다. 현재는 좌표 계열 값일 가능성이 더 높다.
12. `0x1844B0..0x1847F7` 시퀀스를 곧바로 opcode script 라고 가정하지 않는다. 현재는 node path 목록 해석이 더 강하다.
13. `0x184420` table 을 route graph edge table 이라고 가정하지 않는다. 현재는 hotspot/cell id -> location index lookup 해석이 더 강하다.
14. `0x1849D4` 를 단순 숫자 쌍이라고 가정하지 않는다. 현재는 location index -> special event/script/message id 매핑 해석이 더 강하다.
15. `field3` 를 location 활성 플래그라고 가정하지 않는다. 활성 여부는 `0x030009A0` runtime array 가 따로 관리한다.

## 지금 가장 유력한 다음 질문

1. `field3` 의 정확한 subtype 의미와 `0x63000` / `0x63424` helper signature 를 더 분리할 수 있는가
2. `0x1849A0` handler `13`개는 `0x06A864` / `0x06D600` special overlay 흐름에서 어떤 역할을 가지는가
3. `0x47EB0` 가 `0x3E1..0x3EF` 를 어떤 종류의 런타임 객체로 바꾸는가
4. `0x561D4` hotspot helper 반환값이 실제 맵 좌표계에서 어떤 단위를 의미하는가
5. `0x093D` binary table 은 `0x093E` 재료 문자열 뱅크와 어떤 관계인가
6. `0x094B` / `0x12DF8(0x63)` 경로는 어떤 게임 데이터 분류를 읽는가

## 문서 사용 규칙

- 작업 시작 전에는 이 문서만 읽고, 필요한 경우에만 전체 실험 로그를 연다.
- 새 사실이 안정적으로 검증되면 이 문서를 먼저 갱신하고, 그 다음 전체 실험 로그를 갱신한다.
