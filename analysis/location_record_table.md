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
- 따라서 `field1/field2` 는 단순 ID 보다 **location/node 좌표 계열 값** 으로 보는 편이 더 자연스럽다.

## 주의할 점

- 지역명 재삽입은 단순 `00` 종단 문자열 치환으로 끝나지 않을 수 있다.
- name field 가 row 안의 고정 크기 `0x18-byte` 슬롯이라면, 길이 초과 번역은 같은 row 경계를 깨뜨릴 수 있다.
