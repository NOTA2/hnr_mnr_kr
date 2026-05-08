# Location Bundle Family

근거 산출물:

- [location_bundle_tables.json](/Users/user/test/analysis/location_bundle_tables.json)
- [location_record_table.md](/Users/user/test/analysis/location_record_table.md)
- [location_record_table.json](/Users/user/test/analysis/location_record_table.json)

## 핵심 결론

- `0x184220` 이후 tail 은 단순 문자열 꼬리가 아니라, **location / world-map bundle** 로 보는 편이 맞다.
- 현재 확인된 하위 구조는 아래와 같다.
  1. `0x184220..0x184244`: `10-entry` order/permutation table
  2. `0x184248..0x1843FF`: `10 * 0x2C` location record table
  3. `0x184420..0x1844AF`: `18 * (u32, u32)` pair table
  4. `0x1844B0..0x1847F7`: route/command bytecode region
  5. `0x184820..0x184887`: `13 * (x, y)` node position pair table 후보
  6. `0x184888..0x1848AF`: `10-entry` route script block pointer table
  7. `0x1849A0..0x1849D3`: `13-entry` Thumb handler pointer table
  8. `0x1849D4..0x184A0B`: `7 * (u32, u32)` special pair table 후보

## Location Record 와 Node 좌표

- location record 의 `field1/field2` 는 `0x184820` 좌표쌍 테이블 앞 `10`개와 거의 일치한다.
- 일치 패턴:
  - `8 / 10` 은 완전 일치
  - `ヴィヴァス`: `(-8, 0)` delta
  - `リオール`: `(-12, -8)` delta

현재 가장 안전한 해석:

- `field1/field2` 는 location/node 좌표 계열 값이다.
- `0x184820` table 은 같은 위치군에 대한 cursor/icon/node 좌표 후보다.

## Route Script Block Table

- base: `0x184888`
- 개수: `10`
- 각 엔트리는 `0x1844E4`, `0x184538`, `0x184594`, `0x1845E8`, `0x184640`, `0x184690`, `0x1846E8`, `0x184740`, `0x1847A0`, `0x1847F8` 같은 pointer sub-table 을 가리킨다.
- 각 sub-table 은 다시 `10-slot` pointer matrix 로 읽힌다.
- slot pointer 가 `null` 이면 route/command 가 비어 있고, non-null 이면 `0x1844B0..0x1847F7` bytecode 영역을 가리킨다.

bytecode 공통 패턴:

- 길이: 대체로 `4 ~ 8` bytes
- 마지막 바이트는 `FF`
- 예시:
  - `00 0A 01 FF`
  - `02 0B 01 0A 00 FF`
  - `07 06 0C 0B 01 FF`

현재 가장 안전한 해석:

- 이 구조는 **per-location route/transition command matrix** 후보다.
- 즉 `10`개 location 사이의 이동/연결/표시 규칙을 bytecode 로 저장하는 테이블일 가능성이 높다.

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

- per-node 또는 per-state callback/handler table 후보

## Special Pair Table

- base: `0x1849D4`
- 개수: `7`
- 값 예시:
  - `(1, 0x3E1)`
  - `(3, 0x3E8)`
  - `(7, 0x3E7)`
  - `(9, 0x3EB)`

현재 해석:

- location/node index 와 event/script/message ID 계열을 묶는 special mapping 후보

## Direct Ref 강도

- `0x184248` location record base: direct ref `12`
- `0x184820` node position pair base: direct ref `12`
- `0x184888` route script block base: direct ref `8`
- `0x1848B0` numeric blob base: direct ref `8`
- `0x1849A0` handler pointer base: direct ref `2`
- `0x1849D4` special pair base: direct ref `7`

이 패턴은 이 영역 전체가 우연한 데이터 모음이 아니라, 코드와 descriptor bundle 에서 반복 소비되는 **한 묶음의 UI/맵 데이터 세트** 라는 해석과 잘 맞는다.

## 다음 질문

1. `field0`, `field3`, `field4` 는 각각 어떤 게임 의미를 가지는가
2. `0x184420` pair table 은 route bytecode region 과 어떤 인덱스 규칙으로 연결되는가
3. `0x1849A0` handler pointer `13`개는 `0x184820` node `13`개와 1:1 대응하는가
4. `0x1849D4` special pair 값 `0x3E1..0x3EF` 는 script/event/message 중 무엇인가
