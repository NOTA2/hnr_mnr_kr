# Text Renderer Path

한글 폰트/문자 매핑 조사용 핵심 텍스트 표시 경로 메모.

## 현재 결론

- world-map 지역명 표시 경로는 `0x06A95A..0x06A972` 에서 잡힌다.
- 이 경로는 location name field (`0x18425C + index * 0x2C`) 를 직접 계산해, object `0x03005FA0` 과 함께 `0x014A98`, `0x014ED0` 계열로 넘긴다.
- `0x014A98` 는 문자 디코더라기보다 **text object / window entry setup helper** 로 보는 해석이 강하다.
- `0x014ED0` 는 실제로 문자열 바이트를 읽으며 Shift-JIS 분기를 수행하므로, 현재 가장 유력한 **공통 일본어 텍스트 처리 루프** 후보다.
- `0x014ED0` 아래에서는 문자코드가 object 내부 lookup 을 거쳐 실제 glyph source pointer 로 바뀌며, 이 경로가 한글 폰트/문자 매핑 조사에 직접 연결된다.

## 확인된 사실

- world-map caller:
  - `0x06A95A`: `r0 = 0x03005FA0`
  - `r1 = 0x06008020`
  - stack arg: `0x18425C + selected_location * 0x2C`
  - `r2 = 0x88`, `r3 = 0x0C`
  - 이후 `bl 0x014A98`
  - 바로 다음 `0x06A972` 에서 `bl 0x014ED0`

- shared caller set:
  - `0x014A98` caller: `0x062182`, `0x062262`, `0x062836`, `0x0628F4`, `0x06295C`, `0x062A1A`, `0x062A70`, `0x065AA4`, `0x065B44`, `0x065BF2`, `0x065C8E`, `0x06718A`, `0x0671E8`, `0x06A972`
  - `0x014ED0` caller: 위와 거의 같은 화면군 + `0x015A6E`, `0x062D68`, `0x069F20`

- object engine:
- `0x015A4C..0x015A80` 는 `0x03001540 + index * 0x2C` (`11` slots) 를 순회하며 `0x014ED0` 을 호출한다.
- 따라서 `0x014ED0` 는 single-shot helper 가 아니라 **공용 text object update/render engine** 에 가깝다.

- glyph lookup / writer 쪽:
  - `0x0152A2..0x0152C4` 에서 현재 문자코드 `u16` 를 `obj + 0x04` 기반 `u16` 테이블로 조회한다.
  - 조회된 값은 `obj + 0x1A` (`ldrh [obj + 26]`) 와 곱해지고, `obj + 0x08` base pointer 에 더해져 glyph source pointer 가 된다.
  - 즉 현재 가장 안전한 해석은:
    - `obj + 0x04`: `char_code -> glyph index/offset` lookup table
    - `obj + 0x08`: glyph data base
    - `obj + 0x1A`: glyph stride / per-glyph unit size
  - 이후 `0x01570C`, `0x01578C`, `0x01580C`, `0x01588C` 가 이 glyph source 를 target pointer 에 복사한다.
  - low-level copy helper 는 두 종류:
    - `0x01590C`
    - `0x015984`
  - 두 helper 는 glyph source 의 halfword 3개를 target 주변에 배치하되, 쓰는 위치가 약간 달라서 서로 다른 tile orientation / layout variant 후보로 보인다.

- page / cursor update 쪽:
  - `0x015608` 은 `obj + 0x1F` byte 를 갱신하고, `obj + 0x10` base 와 결합해 `obj + 0x14` current destination pointer 를 다시 계산한다.
  - 계산에는 `obj + 0x1F << 10` 계열이 보이므로, text object 가 0x400-byte tile page 단위로 이동하는 해석이 강하다.

## `0x014ED0` 에서 보인 문자 분기

- `obj + 12` 포인터에서 현재 바이트를 읽는다.
- first byte 검사:
  - `0x81..0x9F` 또는 `0xE0..0xEF` 범위는 multibyte Shift-JIS lead byte 후보로 분기
  - `0x20..0x7E` 범위는 ASCII / halfwidth 경로로 보이는 분기
  - `0x00` 은 문자열 종료
- 즉 이 함수는 숫자 helper 나 layout helper 가 아니라, 실제 **문자 인코딩 규칙을 의식하는 루프**다.

## 현재 해석

- `0x03EB78 / 0x03ECCC / 0x03EDB8` 는 ASCII/숫자 UI glyph helper family
- `0x014A98 / 0x014ED0 / 0x015A4C` 는 general text object family
- `0x0152A2..0x0152C4` 는 general text object family 안의 **문자코드 -> glyph source** lookup 핵심 지점
- `0x01570C..0x015984` 는 glyph source 를 tile target 으로 풀어쓰는 writer family
- 한글화용 폰트/문자 매핑은 이제 후자 쪽을 우선 조사해야 한다.

## 다음 질문

1. `obj + 0x04` lookup table 과 `obj + 0x08` glyph base 를 실제로 채우는 writer / initializer 는 어디인가?
2. width/advance 값은 object field (`+0x18`, `+0x1A`, `+0x1C`, `+0x20` 부근) 중 어디에 누적되는가?
3. `0x01570C / 0x01578C / 0x01580C / 0x01588C` 네 variant 가 가로/세로 또는 8x4 / 4x8 복사 중 어떤 역할 차이를 갖는가?
4. `0x014A98` caller 들이 공통 font asset 을 쓰는지, 화면군마다 다른 glyph source 를 쓰는지?
