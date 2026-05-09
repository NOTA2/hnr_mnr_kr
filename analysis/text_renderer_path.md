# Text Renderer Path

한글 폰트/문자 매핑 조사용 핵심 텍스트 표시 경로 메모.

## 현재 결론

- world-map 지역명 표시 경로는 `0x06A95A..0x06A972` 에서 잡힌다.
- 이 경로는 location name field (`0x18425C + index * 0x2C`) 를 직접 계산해, object `0x03005FA0` 과 함께 `0x014A98`, `0x014ED0` 계열로 넘긴다.
- text object 생성 쪽에서는 `0x01499C` 가 font resource header 를 해석해 object 에 lookup table, glyph base, stride 를 심는 **font initializer** 로 보인다.
- `0x014A98` 는 문자 디코더라기보다 **text object / window entry setup helper** 로 보는 해석이 강하다.
- `0x014ED0` 는 실제로 문자열 바이트를 읽으며 Shift-JIS 분기를 수행하므로, 현재 가장 유력한 **공통 일본어 텍스트 처리 루프** 후보다.
- `0x014ED0` 아래에서는 문자코드가 object 내부 lookup 을 거쳐 실제 glyph source pointer 로 바뀌며, 이 경로가 한글 폰트/문자 매핑 조사에 직접 연결된다.
- 앞단 resource loader `0x000290 / 0x0002CC / 0x000304 / 0x00033C` 도 text/font 자산과 직접 연결된다.

## 확인된 사실

- world-map caller:
  - `0x06A95A`: `r0 = 0x03005FA0`
  - `r1 = 0x06008020`
  - stack arg: `0x18425C + selected_location * 0x2C`
  - `r2 = 0x88`, `r3 = 0x0C`
  - 이후 `bl 0x014A98`
  - 바로 다음 `0x06A972` 에서 `bl 0x014ED0`

- shared caller set:
  - `0x01499C` caller: `0x015A32`, `0x0618AE`, `0x064B66`, `0x069D7C`
  - `0x014A98` caller: `0x062182`, `0x062262`, `0x062836`, `0x0628F4`, `0x06295C`, `0x062A1A`, `0x062A70`, `0x065AA4`, `0x065B44`, `0x065BF2`, `0x065C8E`, `0x06718A`, `0x0671E8`, `0x06A972`
  - `0x014ED0` caller: 위와 거의 같은 화면군 + `0x015A6E`, `0x062D68`, `0x069F20`

- object engine:
  - `0x015A4C..0x015A80` 는 `0x03001540 + index * 0x2C` (`11` slots) 를 순회하며 `0x014ED0` 을 호출한다.
  - `0x0159FC..0x015A3A` 는 같은 `11`개 slot 에 대해 `0x0002CC(0, 1)` 결과를 `0x01499C` 로 넘겨 일괄 초기화한다.
  - 따라서 `0x014ED0` 는 single-shot helper 가 아니라 **공용 text object update/render engine** 에 가깝고, 그 앞단 font initializer 도 bulk slot 흐름을 가진다.

- resource loader 쪽:
- `0x000290(registry_slot)` 은 hub `0x08076530` 에서 32-bit pointer table 을 읽고, 선택한 registry base pointer 를 돌려준다.
  - `0x0002CC(entry_index, registry_slot)` 은 위 registry base 에서 `entry_index * 0x0A` record 를 계산한 뒤, record `+0x00` 의 pointer field 를 돌려준다.
  - `0x000304(entry_index, registry_slot)` 은 같은 record `+0x04` 의 length field 를 돌려준다.
  - `0x00033C(dest, entry_index, registry_slot)` 은 DMA3 를 기다린 뒤 `0x0002CC`, `0x000304` 결과를 써서 resource payload 를 `dest` 로 복사한다.
  - 따라서 현재 가장 안전한 record 해석은:
    - `+0x00`: payload pointer
    - `+0x04`: payload length
    - record size: `0x0A`
  - 이 loader 축은 이전에 잡아 둔 hub `0x076530` / registry 조사와 자연스럽게 이어진다.

- font initializer `0x01499C`:
  - `obj + 0x00 = resource_ptr`
  - `resource_ptr + 0x10` 을 기본 베이스로 잡는다.
  - `resource[7] & 0x80` 이 켜져 있으면 lookup 베이스에 `+0x40000` 을 더한다.
  - 그 결과를 `obj + 0x04` 에 저장한다.
  - 이후 `obj + 0x08 = (obj + 0x04) + 0x20000`
  - `obj + 0x16` byte 에는 `resource[7] & 0x1F` 가 저장된다.
  - `obj + 0x1A` halfword 에는 `resource[8]` 값이 저장되며, 현재 glyph stride 후보로 쓰인다.
  - `obj + 0x1C`, `obj + 0x1D` 에는 initializer 인자 `r2` 가 복제된다.
  - `0x08088318` 에는 `"FONT INITIALIZE ERROR"` 문자열이 있어, 함수 역할과도 잘 맞는다.
  - 따라서 현재 가장 안전한 resource header 해석은:
    - `+0x00..+0x03`: magic `"fnt\\0"`
    - `+0x04`: width-like field 후보 `0x0C`
    - `+0x05`: height/line-like field 후보 `0x0F`
    - `+0x07`: font flags / layout bits
    - `+0x08`: glyph stride
    - `+0x10...`: lookup table region
    - `+0x20010...` 또는 `+0x60010...`: glyph data region
  - 실제 공통 resource payload 시작 `0x3E0000` 에서는 `66 6E 74 00 0C 0F 00 0A 48 00 ...` 가 보인다.

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
  - writer loop 를 보면 source 는 한 번에 `+6` byte, 총 `8 + 4 = 12` 행을 소비하므로, 현재 가장 강한 해석은 **glyph 1개 = `12 rows * 6 bytes = 0x48` bytes = 12x12 4bpp 계열 포맷** 이다.
  - 이는 `resource[8] = 0x48` stride 와도 정확히 맞는다.

- 샘플 lookup 확인:
  - `'0' (0x30) -> glyph index 0x0001`
  - `'あ' (0x82A0) -> 0x0067`
  - `'ア' (0x8341) -> 0x00B7`
  - `'セ' (0x835A) -> 0x00D0`
  - `'リ' (0x838A) -> 0x00FF`
  - `'漢' (0x8ABF) -> 0x01C6`
  - `'字' (0x8E9A) -> 0x032F`
  - `'日' (0x93FA) -> 0x051C`
  - `'本' (0x967B) -> 0x05DA`
  - 첫 nonzero lookup 들도 `0x30..0x39 -> 1..10`, `0x78 -> 11`, 이후 `0x8141` 계열 순으로 이어진다.
  - 따라서 공통 font resource 는 ASCII 전부를 포괄한다기보다, **숫자 + 일본어 중심의 custom code map** 으로 보는 편이 안전하다.

- glyph dump 검증:
  - [fnt_glyph_82A0_ah.pgm](/Users/user/test/analysis/fnt_glyph_82A0_ah.pgm), [fnt_glyph_8341_a_katakana.pgm](/Users/user/test/analysis/fnt_glyph_8341_a_katakana.pgm), [fnt_glyph_93FA_day.pgm](/Users/user/test/analysis/fnt_glyph_93FA_day.pgm) 을 `dump-fnt-glyph` 로 실제 덤프했다.
  - PGM 뷰어 제약 때문에 ASCII preview 로 확인했을 때, `'日'` 은 12x12 사각 프레임형 획이 꽤 분명했고 `'ア'` 도 대각선/수직형 패턴이 드러났다.
  - 따라서 `lookup -> glyph index -> stride 0x48 -> 12x12 계열 glyph` 해석은 이제 단순 수치 추정이 아니라 **샘플 글자 형태 검증까지 거친 가설** 이다.

- 전체 manifest 추출:
  - [common_fnt_manifest.json](/Users/user/test/analysis/common_fnt_manifest.json) 은 `inspect-fnt` 로 생성한 공통 `fnt` payload 전체 mapping dump 다.
  - 현재 요약:
    - nonzero mappings: `1698`
    - decoded entries: `ASCII 11`, `non-ASCII 1687`, `undecodable 0`
    - max glyph index: `0x06A2`
    - glyph coverage end: `0x41DDE8`
  - 따라서 font 쪽도 이제는 “가능성 검증”만이 아니라, **공통 mapping 전체를 실제 추출본으로 다룰 수 있는 단계** 다.

- page / cursor update 쪽:
  - `0x015608` 은 `obj + 0x1F` byte 를 갱신하고, `obj + 0x10` base 와 결합해 `obj + 0x14` current destination pointer 를 다시 계산한다.
  - 계산에는 `obj + 0x1F << 10` 계열이 보이므로, text object 가 0x400-byte tile page 단위로 이동하는 해석이 강하다.

- 공통 폰트 resource 가설:
  - `0x015A28`, `0x0618A4`, `0x064B5C`, `0x069D72` 는 모두 `0x0002CC(0, 1)` 뒤 `0x01499C` 를 호출한다.
  - `0x0002CC` 내부를 보면 두 번째 인자 `1` 은 hub `0x076530` pointer table 의 slot 선택, 첫 번째 인자 `0` 은 해당 registry 안의 `0x0A` record index 로 읽힌다.
  - hub table 실제 값은 `slot 1 -> 0x17C2F4`, `slot 2 -> 0x17C384`, `slot 3 -> 0x17C71C`, `slot 6 -> 0x17C7E4` 이다.
  - 따라서 현재까지 확인된 주요 text object 초기화 경로는 **registry slot `1` entry `0` = table base `0x17C2F4` 의 entry 0** 공통 font resource 를 공유하는 해석이 가장 강하다.
  - 이 entry 는 pointer-length 기준 `ptr=0x083E0000`, `len=0x3DDE8` 이며, file offset 으로는 `0x3E0000..0x41DDE7` 이다.

## `0x014ED0` 에서 보인 문자 분기

- `obj + 12` 포인터에서 현재 바이트를 읽는다.
- first byte 검사:
  - `0x81..0x9F` 또는 `0xE0..0xEF` 범위는 multibyte Shift-JIS lead byte 후보로 분기
  - `0x20..0x7E` 범위는 ASCII / halfwidth 경로로 보이는 분기
  - `0x00` 은 문자열 종료
- 즉 이 함수는 숫자 helper 나 layout helper 가 아니라, 실제 **문자 인코딩 규칙을 의식하는 루프**다.

## 현재 해석

- `0x03EB78 / 0x03ECCC / 0x03EDB8` 는 ASCII/숫자 UI glyph helper family
- `0x01499C` 는 general text object family 앞단의 **font resource initializer**
- `0x014A98 / 0x014ED0 / 0x015A4C` 는 general text object family
- `0x0152A2..0x0152C4` 는 general text object family 안의 **문자코드 -> glyph source** lookup 핵심 지점
- `0x01570C..0x015984` 는 glyph source 를 tile target 으로 풀어쓰는 writer family
- `0x000290 / 0x0002CC / 0x000304 / 0x00033C` 는 위 family 가 기대하는 font/blob resource 를 공급하는 loader family
- 한글화용 폰트/문자 매핑은 이제 후자 쪽을 우선 조사해야 한다.

## 다음 질문

1. slot `1` 을 이전 문서의 Registry A/B/C/D 분류와 어떻게 대응시킬지 명시적으로 정리
2. width/advance 값은 object field (`+0x18`, `+0x1A`, `+0x1C`, `+0x20` 부근) 중 어디에 누적되는가?
3. `0x01570C / 0x01578C / 0x01580C / 0x01588C` 네 variant 가 가로/세로 또는 8x4 / 4x8 복사 중 어떤 역할 차이를 갖는가?
4. common manifest 기준으로 한글용 신규/대체 glyph index 전략을 어떻게 세울지
