# Registry B Companion Descriptors

근거 산출물:

- [registry_b_companion_descriptors.json](/Users/user/test/analysis/registry_b_companion_descriptors.json)
- [registry_b_entries.json](/Users/user/test/analysis/registry_b_entries.json)
- [registry_b_mirror_summary.json](/Users/user/test/analysis/registry_b_mirror_summary.json)

## 핵심 결론

- `0x1840E8` 전체를 한 종류 구조로 보면 안 된다.
- 현재 가장 안전한 분리는 아래 셋이다.
  1. `0x1840F8..0x1841E7`: 타일 companion descriptor 배열
  2. `0x1841E8..0x18421F`: palette companion descriptor 배열
  3. `0x184220` 이후: location order/record table 로 이어지는 metadata/string tail

## 타일 descriptor 배열

- 범위: `0x1840F8..0x1841E7`
- 개수: `15`
- row 크기: `16-byte`
- 현재 해석:
  - `u32 destination_vram`
  - `u32 registry_b_index`
  - `u32 dim_a`
  - `u32 dim_b`

관찰 포인트:

- 목적지 주소가 모두 VRAM `0x0601xxxx` 로 향한다.
- index 값은 실제 Registry B 엔트리와 정확히 연결된다.
- 사용된 index:
  - `0x59`, `0x57`, `0x58`, `0x56`, `0x4E`, `0x4F`, `0x4B`, `0x4D`, `0x53`, `0x55`, `0x51`, `0x4C`, `0x52`, `0x54`, `0x6F`

## Palette descriptor 배열

- 범위: `0x1841E8..0x18421F`
- 개수: `7`
- row 크기: `8-byte`
- 현재 해석:
  - `u32 registry_b_index`
  - `u32 destination_palette_ram`

관찰 포인트:

- 목적지 주소가 palette RAM `0x05000200..0x050002C0` 로 향한다.
- 사용된 index:
  - `0x61`, `0x60`, `0x5F`, `0x5C`, `0x5D`, `0x5E`, `0x70`

## Direct Ref

- `0x1840E8` direct ref:
  - `0x06A984`
  - `0x08C0A8`
- `0x1841E8` direct ref:
  - `0x06A17C`
  - `0x06D158`
  - `0x08BFF8`
  - `0x08C210`

## 이어지는 구조

- `0x184220..0x184244`:
  - `10-entry` order/permutation table
- `0x184248..0x1843FF`:
  - `10 * 0x2C` fixed-size location record table
  - 자세한 내용은 [location_record_table.md](/Users/user/test/analysis/location_record_table.md) 참고
- `0x184420..0x184A0C`:
  - route bytecode / node position / handler / special pair 를 포함한 location bundle tail
  - 자세한 내용은 [location_bundle_family.md](/Users/user/test/analysis/location_bundle_family.md) 참고

## 주의할 점

- `0x184220` 이후에는 수치 metadata 와 문자열이 이어지므로, 같은 struct 의 연장으로 단정하면 안 된다.
- 이 영역은 `Registry B` 미러 table (`0x183D50`) 과 매우 가깝지만, "미러 엔트리 본체"와 "미러 asset 배치용 descriptor"를 구분해서 읽어야 한다.
