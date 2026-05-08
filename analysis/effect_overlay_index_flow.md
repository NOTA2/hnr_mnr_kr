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

- `word4 != 0` 이 켜는 slot maintenance side-path 가 실제로 어떤 overlay / object 군을 보존/삭제하는지 아직 남아 있다.
- `0x03CA68` dispatch table 분석은 helper-family 차원에서 유효하지만, effect row 경로의 실제 인자 매핑과는 분리해서 다시 정리할 필요가 있다.
- 현재 direct literal scan 에서는 `0x06A52E` 만 writer 로 보이지만, static cluster 를 통한 간접 writer 가능성은 아직 완전히 배제하지 않는다.

## Row Parameter Semantics

`0x047A88` 내부에서 확인된 연결:

- `word0` 은 `0x047B00` 에서 `0x0561F8` 로 전달된다.
- `0x0561F8` 은 `*(0x03005014) + 0x90` byte 에 이 값을 저장한다.
- `0x0561D4` 는 같은 byte 를 읽어 반환한다.
- 이 getter 값은 기존 `0x184420` hotspot/location lookup 경로에서도 비교값으로 쓰인다.
- 따라서 `word0` 은 effect asset id 라기보다 **location 대표 hotspot/cell id** 로 보는 해석이 가장 강하다.

`word0` 과 `0x184420` lookup 의 일치:

| effect row / location | word0 | `0x184420` match |
| --- | --- | --- |
| `0` | `0x1E` | hotspot `0x1E` -> location `0` |
| `1` | `0x0D` | hotspot `0x0D` -> location `1` |
| `2` | `0x01` | hotspot `0x01` -> location `2` |
| `3` | `0x0A` | hotspot `0x0A` -> location `3` |
| `4` | `0x37` | hotspot `0x37` -> location `4` |
| `5` | `0x41` | hotspot `0x41` -> location `5` |
| `6` | `0x26` | hotspot `0x26` -> location `6` |
| `7` | `0x05` | hotspot `0x05` -> location `7` |
| `8` | `0x3B` | hotspot `0x3B` -> location `8` |
| `9` | `0x3E` | hotspot `0x3E` -> location `9` |

`word3` 은 아직 최종 의미 확정 전이지만, 아래까지는 확인됐다.

- `0x047DEE` / `0x047E26` 에서 `word3` 이 `0x02B96C` 의 `r2` 로 전달된다.
- `0x02B96C` 는 세 번째 인자를 `& 7` 로 제한한다.
- 제한된 값은 `0x0383F8` 의 두 번째 인자로 전달된다.
- `0x0383F8` 은 `0x1824F0` 의 8-entry Thumb function pointer table (`0x0377E0..0x037AB8`) 을 index 한다.
- 이 8개 accessor 는 공통 descriptor 의 halfword field `+0x04, +0x06, +0x08, +0x0A, +0x0C, +0x0E, +0x10, +0x12` 에서 각각 low 10-bit 값을 읽는다.
- 따라서 현재 가장 강한 해석은 **descriptor field selector 역할을 하는 3-bit variant index** 다.
- 현재 `0x184A0C` row 에서 실제 사용된 값은 `0` 과 `6` 뿐이며, row `2` 만 `6` 을 쓴다.

`0x03CA68` helper-family 에 대해서는 아래까지 확인됐지만, 이것을 effect row `word1` 에 직접 연결하는 해석은 수정이 필요하다.

- `0x02B96C` 는 두 번째 인자를 `& 0x0F` 로 제한한 뒤 `0x03CA68` 에 전달한다.
- `0x03CA68` 은 `0x182530` 16-entry Thumb function pointer table 로 dispatch 한다.
- table entry `0..3` 은 각각 `0x03CAC0`, `0x03CB3C`, `0x03CBB8`, `0x03CC34` 로 이어진다.
- 이 4개 accessor 는 `*(0x03001450) + 0x270/0x274` descriptor family 에서 halfword field `+0x02, +0x04, +0x06, +0x08` low 10-bit 를 읽는다.
- table entry `4..15` 는 모두 `0x03CCB0` fallback accessor 로 이어진다.
- fallback accessor 는 같은 descriptor 의 field `+0x00` low 8-bit 를 base 로 읽고, `0x03CA68` 복귀 후 `+ (nibble - 4)` 보정을 받는다.
- 다만 `0x047A88` effect row 경로의 실제 call site (`0x047DEE`, `0x047E26`) 에서는 `0x02B96C` 의 두 번째 인자 `r1` 이 `0` 으로 고정된다.
- 따라서 이전의 "`word1 low nibble` 이 effect row 경로에서 이 dispatch 를 고른다"는 해석은 현재 철회하는 편이 안전하다.

`word1` / `word2` pair 에 대해서도 아래까지는 확인됐다.

- `0x047A88` 안에서 `word1` / `word2` stack slot 은 각각 한 번만 읽힌다.
- 두 값은 sign-extended 16-bit pair 로 helper `0x0587BC` 에 함께 전달된다.
- `0x0587BC` 는 현재 active object/entry 를 찾은 뒤, 두 축에 같은 scalar transform helper `0x075560` 을 각각 적용한다.
- 변환 결과는 active object/entry 의 `+0x08` / `+0x0C` 에 저장된다.
- `0x075560` 은 내부적으로 signed int 를 IEEE-754 single float bit pattern 으로 포장한다. 하위 helper 는 `0x074D44` packer, `0x074DFC` unpacker 로 보인다.
- 따라서 현재 가장 안전한 해석은 `word1` / `word2` 가 **직접적인 signed integer 좌표쌍** 이고, runtime object 에는 float 형태로 저장된다는 것이다.
- 다만 `word1 low nibble` selector 분석과 이 좌표 경로가 같은 field 를 다중 용도로 재사용하는지 여부는 아직 열어 둔다.

`word4` 에 대해서도 아래까지는 확인됐다.

- `0x047A88` 는 다섯 번째 인자를 `[r7 + 0x1C]` 에서 읽는다.
- 이 값은 `0` 여부만 검사되며, `0` 이면 `0x020C` 쪽 공통 경로로 바로 건너뛴다.
- `word4 != 0` 이면 global `0x03001450 + 0x33C/+0x33E` 의 두 halfword 를 읽고, 각각 `+8` 보정 후 slot `8..23` 과 직접 비교한다.
- 따라서 `+0x33C/+0x33E` 는 적어도 **raw tracked slot id 2개** 로 보는 해석이 강하다.
- 이 side-path 는 slot `8..23` 의 세 병렬 block (`+0x0574`, `+0x0AF4`, `+0x0BF4`) 을 `0x075D4C` 로 지우되, tracked slot `+8` 두 개는 건너뛴다.
- `0x044320(slot, flag)` 는 `+0x0574 + (slot + 8) * 0x34` record 의 상위 플래그를 clear/set 하고, `0x0443B4(slot)` 는 같은 플래그가 살아 있는지 검사하는 helper 로 보는 해석이 강하다.
- `0x03D6F0` 는 `+0x33E` 와 `+0x33C` 를 함께 읽어 `0x0443B4` / `0x044320` 를 호출하는 정합성 보조 루틴으로 보인다.
- `0x03D6F0` 첫 비교는 `cmp` 가 아니라 `cmn` 이므로, 실제 특수값은 `+0x33E == -1` sentinel 로 읽는 편이 자연스럽다.
- 따라서 `+0x33E` 는 "두 번째 tracked slot 없음" 상태를 가질 수 있는 optional slot field 후보로 좁혀진다.
- `0x0443F8` 는 global `0x0300503C` 를 slot iterator 로 사용해 후보 slot `0..15` 를 훑는다.
- 이 루프는 현재 tracked slot `0x33C/+0x33E` 와 겹치는 후보를 건너뛰고, `+0x574` active flag, `+0x57C` / `+0xBA4` / `+0xBA6` 위치/경계 값, `0x03005240` 의 `16 * 4-byte` per-slot state table 을 함께 사용한다.
- 선택된 후보는 `0x03005284` 에 `slot id` 또는 `-1` sentinel 로 남는다.
- 현재 확인된 `0x0443F8` direct caller 는 `0x059034` 하나이며, 이 caller 는 성공 시 반환 slot id 를 `slot + 0x5A` runtime id 로 변환해 후속 object 구축에 사용한다.
- `0x045B98` 계열과 `0x047A28` 은 `0x03005284` 를 읽는 consumer 이므로, `0x03005284` 는 selected candidate slot buffer 로 보는 해석이 강하다.
- `0x044B7C` 는 시작부터 `0x33E` 를 읽어 `0x714` table 기반 후속 object 흐름으로 들어가므로, `+0x33E` 는 optional second tracked slot consumer 경로도 가진다.
- 따라서 현재 가장 안전한 해석은 `word4` 가 **overlay slot maintenance mode flag** 라는 것이다.
