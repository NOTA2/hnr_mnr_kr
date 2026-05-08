# Effect / Overlay Index Flow

근거 산출물:

- [effect_overlay_index_refs.json](/Users/user/test/analysis/effect_overlay_index_refs.json)
- [location_bundle_family.md](/Users/user/test/analysis/location_bundle_family.md)

## 핵심 결론

- `0x03005FF8` 은 독립 effect 상태값이라기보다, **world-map 에서 현재 선택/hover 된 location index byte** 로 보는 해석이 가장 강하다.
- 직접 literal scan 기준으로 `0x069000..0x06DFFF` code slice 안의 확인된 writer 는 `0x06A52E` 한 곳이다.
- 이 writer 는 loop index 를 byte 로 저장하며, 직전 조건상 값 범위가 `0..9` 로 제한된다.
- 이 범위는 `0x184248` location record `10`개, `0x184A0C` effect/overlay parameter row `10`개와 맞는다.
- 따라서 `0x06CFB8` 이 `0x184A0C + 0x03005FF8 * 0x14` 를 읽는 것은 "선택된 location 에 맞는 effect/overlay row 선택" 으로 보는 편이 자연스럽다.

## 확인된 흐름

| 역할 | 코드 위치 | 동작 |
| --- | --- | --- |
| 선택 index write | `0x06A52E` | `0x03006018 == 0` 이고 hit-test loop index 가 `0..9` 범위일 때, loop index 를 `0x03005FF8` 에 `strb` 로 저장한다. |
| 선택 label/display read | `0x06A93E`, `0x06A95E` | `0x03006018 == 2` 일 때 `0x03005FF8` 를 읽어 `0x184248 + index * 0x2C` location record 쪽 값을 사용한다. |
| 현재 location 비교 | `0x06B0FE` | `0x03005FF8` 와 current-location byte `0x03006020` 를 비교한다. 같으면 `0x03005FFC = 7` 로 상태를 바꾸는 흐름이 있다. |
| route/path matrix read | `0x06B8CA..0x06C07C` | `0x03006020` 과 `0x03005FF8` 를 함께 읽어 `0x184888` route matrix / `0x184820` node position 계열 계산에 사용한다. |
| 선택 확정/copy | `0x06CEC0` | `0x03005FF8` byte 를 `0x03006020` current-location byte 로 복사한 뒤, selected location record 와 companion descriptor 를 이용해 transition 좌표를 만든다. |
| effect row consume | `0x06CFE4..0x06D034` | `0x03002FFC == 0x10` 일 때 `0x03005FF8` 를 index 로 `0x184A0C` row 의 `5`개 word 를 읽어 `0x047A88` 에 전달한다. |

## 참조 강도

- `find-u32-refs` 로 `0x069000..0x06DFFF` 범위를 조사한 결과:
  - `0x03005FF8` literal value hit: `10`개
  - Thumb literal load: `27`개
  - 자동 접근 분류: `write_byte` `1`개, `read_byte` `26`개
- 위 결과는 [effect_overlay_index_refs.json](/Users/user/test/analysis/effect_overlay_index_refs.json) 에 저장했다.

## 반복하면 안 되는 착각

- `0x06B8B0` 시작부의 `strb #0` 은 `0x03005FF8` 초기화가 아니다. 해당 literal 은 `0x03005FE8` 쪽이다.
- `0x06A5B2` 의 `strb #2` 도 `0x03005FF8` write 가 아니다. 이 코드는 state byte `0x03006018 = 2` 를 설정한다.
- `0x08C0xx` 주변의 `0x03005FF8` 값들은 현재 static constant cluster / data bundle 로 보는 편이 안전하다. 실제 code xref 로 쓰려면 참조 instruction 을 별도로 확인해야 한다.

## 남은 질문

- `0x184A0C` row 의 `word0` / `word3` 이 `0x047A88` 내부에서 정확히 어떤 effect subtype 을 바꾸는지 아직 남아 있다.
- 현재 direct literal scan 에서는 `0x06A52E` 만 writer 로 보이지만, static cluster 를 통한 간접 writer 가능성은 아직 완전히 배제하지 않는다.
