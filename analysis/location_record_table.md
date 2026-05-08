# Location Record Table

근거 산출물:

- [location_record_table.json](/Users/user/test/analysis/location_record_table.json)
- [location_texts.json](/Users/user/test/analysis/location_texts.json)
- [location_bundle_family.md](/Users/user/test/analysis/location_bundle_family.md)

## 핵심 결론

- 기존 `0x18425C` 지역명 문자열 구간은 순수 standalone string bank 가 아니다.
- 현재 가장 안전한 해석은 아래와 같다.
  1. `0x184220..0x184244`: `10-entry` order/permutation table
  2. `0x184248..0x1843FF`: `10 * 0x2C` fixed-size location record table

## Order Table

- 범위: `0x184220..0x184244`
- 값:
  - `3, 4, 0, 2, 7, 9, 5, 1, 6, 8`

현재 해석:

- location record 들의 표시/선택 순서를 위한 permutation table 후보

## Location Record Table

- 범위: `0x184248..0x1843FF`
- row 수: `10`
- row 크기: `0x2C`
- row 구조:
  - `u32 field0`
  - `u32 field1`
  - `u32 field2`
  - `u32 field3`
  - `u32 field4`
  - `0x18-byte name field`

name field:

- row 시작 `+0x14`
- 첫 row name field: `0x18425C`

## 이름 예시

- `0x18425C`: `セントラルシティ`
- `0x184288`: `ヴィヴァス`
- `0x1842B4`: `リオール`
- `0x184338`: `オルヘンティノス城`
- `0x1843E8`: `クルス遺跡`

## Direct Ref 비교

- first record base `0x184248`: direct ref `12`
- first name field `0x18425C`: direct ref `4`

이 차이 때문에 현재는 문자열보다 record table 이 실제 소비 단위일 가능성이 더 높다.

## 좌표 후보

- `field1/field2` 는 [location_bundle_family.md](/Users/user/test/analysis/location_bundle_family.md) 에 정리된 `0x184820` node position pair table 앞 `10`개와 거의 일치한다.
- `8 / 10` 은 완전 일치하고, `ヴィヴァス`, `リオール` 2건만 작은 delta (`-8,0`, `-12,-8`) 가 있다.
- 다만 코드 기준으로는 단순 node ID 가 아니라, **location icon / hotspot 사각형의 좌상단 좌표** 로 보는 편이 더 정확하다.
- 근거: `0x06A418` hit-test 루틴은 `field1`, `field2` 와 companion descriptor 의 `(dim_a, dim_b) * 8` 을 조합해 클릭/선택 사각형을 만든다.

## Draw Field 해석

- `0x069E9C` 루틴은 활성 location row 를 순회하며 `field0`, `field1`, `field2`, `field4`, `field3` 를 helper `0x63000` 에 넘긴다.
- `0x06D4A8` 계열도 현재 선택된 row 의 같은 필드 조합을 helper `0x63424` 로 넘긴다.

현재 가장 안전한 해석:

- `field0`: location icon draw helper 가 받는 **asset / icon family ID** 후보
  - 값은 `99`, `100`, `101` 세 종류만 보인다.
- `field3`: location icon 의 **draw subtype / mode / palette 계열 파라미터** 후보
  - 값은 `3`, `4`, `5` 세 종류만 보인다.
- `field4`: location icon 의 **graphic variant / tile-base 계열 파라미터** 후보
  - 값이 `0x80`, `0x84`, `0x88`, `0x8C`, `0x100`, `0x104`, `0x108` 식으로 정렬된다.

즉 `field0/field3/field4` 는 현재로서는 좌표보다 **표시 파라미터** 로 보는 편이 가장 자연스럽다.

## 주의할 점

- 지역명 재삽입은 단순 `00` 종단 문자열 치환으로 끝나지 않을 수 있다.
- name field 가 row 안의 고정 크기 `0x18-byte` 슬롯이라면, 길이 초과 번역은 같은 row 경계를 깨뜨릴 수 있다.
- name field 주소는 `0x18425C + index * 0x2C` 로도 접근되므로, 이름만 따로 건드리더라도 row stride 를 깨뜨리면 선택/폭 계산 루틴까지 연쇄적으로 영향을 줄 수 있다.
