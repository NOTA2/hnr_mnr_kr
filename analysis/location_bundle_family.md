# Location Bundle Family

근거 산출물:

- [location_bundle_tables.json](/Users/user/test/analysis/location_bundle_tables.json)
- [location_record_table.md](/Users/user/test/analysis/location_record_table.md)
- [location_record_table.json](/Users/user/test/analysis/location_record_table.json)
- [effect_overlay_index_flow.md](/Users/user/test/analysis/effect_overlay_index_flow.md)

## 핵심 결론

- `0x184220` 이후 tail 은 단순 문자열 꼬리가 아니라, **location / world-map bundle** 로 보는 편이 맞다.
- 현재 확인된 하위 구조는 아래와 같다.
  1. `0x184220..0x184244`: `10-entry` order/permutation table
  2. `0x184248..0x1843FF`: `10 * 0x2C` location record table
  3. `0x184420..0x1844AF`: `18 * (u32, u32)` hotspot/location pair table
  4. `0x1844B0..0x1847F7`: route path byte region
  5. `0x184820..0x184887`: `13 * (x, y)` node position pair table 후보
  6. `0x184888..0x1848AF`: `10-entry` route script block pointer table
  7. `0x1849A0..0x1849D3`: `13-entry` Thumb handler pointer table
  8. `0x1849D4..0x184A0B`: `7 * (u32, u32)` special location/event pair table

## Location Record 와 Node 좌표

- location record 의 `field1/field2` 는 `0x184820` 좌표쌍 테이블 앞 `10`개와 거의 일치한다.
- 일치 패턴:
  - `8 / 10` 은 완전 일치
  - `ヴィヴァス`: `(-8, 0)` delta
  - `リオール`: `(-12, -8)` delta

현재 가장 안전한 해석:

- `field1/field2` 는 location icon / hotspot 의 화면 기준 좌상단 좌표다.
- 근거: `0x06A418` hit-test 루틴은 `field1`, `field2` 를 기준으로, `0x1840F8` companion descriptor 의 `(dim_a, dim_b) * 8` 범위를 비교해 사각형 클릭 판정을 만든다.
- `0x184820` table 은 같은 위치군에 대한 cursor/icon/node anchor 좌표 후보다.
- 즉 `field1/field2` 와 `node_position_pairs` 는 완전히 같은 역할이 아니라, **아이콘 직사각형 원점** 과 **경로/커서 anchor** 의 관계로 보는 편이 더 자연스럽다.

## Location Record Draw Field

- `0x069E9C` 루틴은 활성 location row 를 순회하며, 각 row 의 `field0`, `field1`, `field2`, `field4`, `field3` 를 helper `0x63000` 에 넘긴다.
- `0x06D4A8` 계열도 현재 선택된 row 의 같은 필드 조합을 helper `0x63424` 로 넘긴다.

현재 가장 안전한 해석:

- `field0`: location icon draw helper 가 받는 **asset / icon family ID** 후보
  - 값 범위가 `99`, `100`, `101` 로 좁고, 같은 helper 의 다른 caller 는 `0x66`, `0x67`, `0x69`, `0x6A` 같은 고정 asset ID 를 넘긴다.
- `field3`: location icon 의 **draw subtype / mode / palette 계열 파라미터** 후보
  - 값은 현재 `3`, `4`, `5` 세 종류만 확인되었다.
- `field4`: location icon 의 **graphic variant / tile-base 계열 파라미터** 후보
  - 값이 `0x80`, `0x84`, `0x88`, `0x8C`, `0x100`, `0x104`, `0x108` 식으로 정렬되어 있어, 연속된 graphic block / tile variant 축으로 읽는 해석이 가장 자연스럽다.
- 즉 `field0/field3/field4` 는 좌표나 활성 플래그보다 **표시 파라미터** 쪽에 가깝다.
- caller/handler 배선까지 보면 더 구체적으로 정리할 수 있다.
  - `0x069E9C` / `0x06D4A8` caller 는 `field4` 를 `r3` 로, `field3` 를 stack arg 로 `0x63000` / `0x63424` 에 넘긴다.
  - helper 내부에서 `r3` (`field4`) 는 sprite attr2 low 10-bit 쪽에 더해진다. 즉 현재는 **tile index / graphic variant offset** 해석이 가장 강하다.
  - stack arg (`field3`) 는 sprite attr2 high byte 상위 nibble 쪽에 더해진다. 즉 현재는 **palette bank / draw subtype** 해석이 가장 강하다.
  - `0x63000` / `0x63424` 는 추상 로직 helper 보다, 거의 같은 구조를 가진 **sprite/OAM build helper pair** 로 보는 편이 더 정확하다.

## Route Pair Table

- base: `0x184420`
- 개수: `18`
- 각 entry 는 현재 `(hotspot_id, location_index)` 로 읽는 해석이 가장 강하다.
- 근거:
  - `0x06A1F8` 부근 루틴이 `0x184420` 을 직접 읽는다.
  - helper `0x561D4` 반환값과 entry 첫 필드를 `18`건 순회 비교한다.
  - 일치하면 entry 둘째 필드를 global current-location byte (`0x03006020`) 로 기록한다.

location 별 hotspot 분포:

- `0`: `14, 18, 24, 30, 34`
- `6`: `38, 41, 46, 47`
- `9`: `62, 64`
- 나머지 다수 location 은 `1`개 hotspot ID 만 가진다.

현재 가장 안전한 해석:

- 이 table 은 route graph edge 정보가 아니라, **맵 hit-test / hotspot ID -> location index 변환표** 다.
- 즉 `0x184888` path matrix 와 성격이 다르며, 두 table 을 같은 종류의 pair/edge 구조로 보면 안 된다.

## Route Script Block Table

- base: `0x184888`
- 개수: `10`
- 각 엔트리는 `0x1844E4`, `0x184538`, `0x184594`, `0x1845E8`, `0x184640`, `0x184690`, `0x1846E8`, `0x184740`, `0x1847A0`, `0x1847F8` 같은 pointer sub-table 을 가리킨다.
- 각 sub-table 은 다시 `10-slot` pointer matrix 로 읽힌다.
- slot pointer 가 `null` 이면 route/command 가 비어 있고, non-null 이면 `0x1844B0..0x1847F7` bytecode 영역을 가리킨다.
- 모든 block 은 자기 자신의 slot 하나만 `null` 이다.
  - `block 0 -> slot 0 null`
  - `block 1 -> slot 1 null`
  - ...
  - `block 9 -> slot 9 null`

route sequence 공통 패턴:

- 길이: 대체로 `4 ~ 8` bytes
- 마지막 바이트는 `FF`
- `FF` 를 제외한 값은 현재 `0..12` 만 나온다.
- 예시:
  - `00 0A 01 FF`
  - `02 0B 01 0A 00 FF`
  - `07 06 0C 0B 01 FF`
  - `09 08 07 06 0C 0B 01 FF`

현재 가장 안전한 해석:

- 이 구조는 **per-location route path matrix** 후보다.
- `10`개 location block 이 있고, 각 block 은 다른 `9`개 목적지까지의 경로를 한 줄씩 저장한다.
- sequence 안의 값은 현재 `13`개 node 집합을 가리키는 것으로 보는 해석이 가장 자연스럽다.
  - `0..9`: location node
  - `0x0A..0x0C`: 중간 connector / transit node 후보
- 즉 이 영역은 "opcode script" 라기보다 **node list + terminator** 형식의 경로 데이터일 가능성이 높다.

## Node Position Pair Table

- base: `0x184820`
- 개수: `13`
- 값 예시:
  - `(0, 69)`
  - `(94, 47)`
  - `(163, 31)`
  - `(192, 81)`
  - `(126, 210)`

현재 해석:

- location/world-map 상의 node/icon/cursor position 후보
- route sequence 가 `0..12` 값만 사용한다는 점도, 이 table 이 실제 `13-node` 공간을 설명한다는 해석과 잘 맞는다.

## Label Position Pair 후보

- base: `0x184950`
- 개수: `10`
- 값 예시:
  - `(10, 50)`
  - `(116, 46)`
  - `(156, 14)`
  - `(186, 56)`

현재 해석:

- location name label 또는 UI text 배치용 좌표 후보

## Handler Pointer Table

- base: `0x1849A0`
- 개수: `13`
- 값은 모두 odd ROM address 이며 Thumb 함수 포인터 형태다.
- 예시:
  - `0x0806A09D`
  - `0x0806A3E5`
  - `0x0806D601`

현재 해석:

- per-node callback/handler table 후보
- route sequence 와 node position table 이 모두 `13`개 축을 공유하므로, 현재는 `node 13개 <-> handler 13개` 정렬 가능성을 우선 둔다.
- 다만 direct ref 는 현재 `0x069E94`, `0x08BFC8` 두 군데뿐이라, `0x1849D4` 나 `0x184248` 처럼 여러 code literal 에서 반복 소비되는 강한 테이블과는 성격이 다를 수 있다.
- 즉 handler table 은 독립 상수라기보다, **상위 static bundle 의 일부 슬롯**으로 간접 소비될 가능성을 열어 두는 편이 안전하다.

## Special Pair Table

- base: `0x1849D4`
- 개수: `7`
- 값 예시:
  - `(1, 0x3E1)`
  - `(3, 0x3E8)`
  - `(7, 0x3E7)`
  - `(9, 0x3EB)`

현재 해석:

- 각 entry 는 `(location_index, special event/script/message id)` 로 읽는 해석이 가장 강하다.
- 근거:
  - `0x06D5A8` 루틴은 `7`개 엔트리를 순회하며, **둘째 필드** (`0x3E1..0x3EF`) 를 helper `0x47EB0` 에 넘긴 뒤, 반환값을 **첫 필드** location index 로 색인되는 배열 슬롯에 저장한다.
- `0x06D430` 루틴은 별도의 `0..6` selector 로 같은 table 을 인덱싱하고, **첫 필드** 를 location slot 번호처럼 사용해 플래그를 세운다.
- 따라서 현재는 `special_pair_table` 을 "특수 이동/이벤트 가능한 location 목록 + 그에 대응하는 event/script/message ID" 로 보는 편이 가장 자연스럽다.

## Static Constant Cluster

- `0x08BFC8..0x08C2B8` 구간에는 location/world-map bundle 관련 static constant 가 조밀하게 반복 배치되어 있다.
- 이 구간에서 반복 확인된 target:
  - `0x184248` location record table
  - `0x18425C` first name field
  - `0x184420` hotspot/location lookup
  - `0x184820` node position pair table
  - `0x1848B0` numeric blob
  - `0x1849A0` handler pointer table
  - `0x1849D4` special pair table
  - `0x1840F8` / `0x1841E8` companion descriptor pair
  - `0x184A0C` effect/overlay parameter table
- 이 static constant 들 옆에는 `0x03002Fxx`, `0x03005Fxx`, `0x030060xx`, `0x030009xx` runtime global 이 반복해서 붙는다.
- 현재 가장 안전한 해석:
  - 코드가 모든 location bundle 하위 table 을 독립 literal 로만 들고 다니는 것이 아니라,
  - **정적 constant cluster + runtime global 조합** 을 통해 higher-level UI/state bundle 처럼 소비하는 경로도 함께 가진다.
- 특히 `0x1849A0` 은 direct ref 가 `2`건뿐이지만, `0x184248`, `0x1849D4`, `0x184820`, `0x1840F8`, `0x1841E8` 는 code literal 과 이 static cluster 양쪽에서 반복 확인된다.
- 또한 `0x184A0C` 는 `0x06D070`, `0x08C1FC` direct ref 가 있어, location bundle tail 끝을 무조건 `0x184A0B` 에서 끊는 해석은 피하는 편이 안전하다.

## Effect / Overlay Parameter Table

- base: `0x184A0C`
- 범위: `0x184A0C..0x184AD3`
- 개수: `10`
- row 크기: `0x14`
- row 구조 후보: `5 * u32`
- 바로 뒤 `0x184AD4` 부터는 `0x087E0000`, `0x00002B18` 처럼 pointer/length 성격의 다른 데이터가 시작되므로, 현재는 `0x184A0C` table 을 `10 * 0x14` 로 끊는 편이 가장 자연스럽다.

값 예시:

- row `0`: `(0x1E, 0x190, 0x1AB, 0, 1)`
- row `2`: `(0x01, 0x1E0, 0x1C2, 6, 1)`
- row `9`: `(0x3E, 0x050, 0x1EA, 0, 0)`

소비 경로:

- `0x06D070` 은 코드 시작점이 아니라, `0x06CFB8` 계열 함수의 literal pool 안에 있는 `0x08184A0C` 값이다.
- 해당 함수는 `0x03002FFC` halfword 가 `0x10` 일 때, `0x03005FF8` byte 를 index 로 사용해 `0x184A0C + index * 0x14` row 를 읽는다.
- row 의 `5`개 word 는 helper `0x047A88` 로 그대로 전달된다.
  - `r0 = word0`
  - `r1 = word1`
  - `r2 = word2`
  - `r3 = word3`
  - `[sp] = word4`
  - `[sp+4] = 0`

현재 가장 안전한 해석:

- 이 table 은 텍스트나 포인터 테이블이 아니라, **world-map effect / overlay spawn parameter table** 후보다.
- `0x03005FF8` 은 direct code slice 기준으로 독립 effect state 가 아니라 **선택/hover 된 location index byte** 로 보는 해석이 강하다.
- 확인된 writer 는 `0x06A52E` 이며, hit-test loop index `0..9` 를 `0x03005FF8` 에 byte 로 저장한다.
- `0x06CEC0` 은 이 selected index 를 current-location byte `0x03006020` 로 복사하므로, 이 값은 "선택 후보 -> 현재 위치 확정" 흐름의 중간 상태로도 쓰인다.
- `0x047A88` 의 다른 caller (`0x051E96`, `0x051FFE`) 도 구조체 필드들을 같은 helper 로 넘기므로, `0x184A0C` row 는 그 구조체 일부를 정적 table 로 빼 둔 형태에 가깝다.
- `word1/word2` 는 signed coordinate-like 값으로 바로 사용되고, `word4` 는 helper 내부 optional branch 를 켜는 flag 처럼 쓰인다.
- `word0` 은 `0x047A88 -> 0x0561F8` 경로에서 `*(0x03005014) + 0x90` byte 로 저장되며, `0x0561D4` getter 가 같은 값을 읽는다.
- `word0` 값 `10`개는 `0x184420` hotspot/location lookup 의 hotspot id 와 정확히 `1:1` 매칭되고, 매칭된 location index 도 row index 와 같다. 따라서 현재는 **location 대표 hotspot/cell id** 로 보는 해석이 가장 강하다.
- `word3` 은 `0x047A88 -> 0x02B96C` 경로에서 세 번째 인자로 전달되고, `0x02B96C` 내부에서 `& 7` 로 제한된 뒤 `0x0383F8` 에 전달된다. 현재는 **3-bit object/subresource variant index** 후보로 둔다.

## Direct Ref 강도

- `0x184248` location record base: direct ref `12`
- `0x184820` node position pair base: direct ref `12`
- `0x184888` route script block base: direct ref `8`
- `0x1848B0` numeric blob base: direct ref `8`
- `0x1849A0` handler pointer base: direct ref `2`
- `0x1849D4` special pair base: direct ref `7`

이 패턴은 이 영역 전체가 우연한 데이터 모음이 아니라, 코드와 descriptor bundle 에서 반복 소비되는 **한 묶음의 UI/맵 데이터 세트** 라는 해석과 잘 맞는다.

## 다음 질문

1. `field3` 가 정확히 palette bank 인지, 또는 palette + subtype 복합 값인지 더 좁힐 수 있는가
2. `0x1849A0` handler table 의 **단일 static cluster 슬롯** 을 실제로 소비하는 코드가 어디인가
3. `0x03005FF8` effect/overlay table index 를 어떤 코드가 최종 선택하는가
4. `0x184A0C` row 의 `word3` 이 `0x02B96C` / `0x0383F8` 경로에서 정확히 어떤 subresource variant 를 고르는가
5. `0x47EB0` 가 `0x3E1..0x3EF` 를 어떤 종류의 런타임 객체로 바꾸는가
6. `0x561D4` 로 읽히는 대표 hotspot/cell id 가 실제 맵 좌표계에서 어떤 단위를 의미하는가
