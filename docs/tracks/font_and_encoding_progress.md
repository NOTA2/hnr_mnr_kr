# Font And Encoding Progress

읽기 규칙: 이 문서는 폰트/문자폭 조사가 활성 단계로 올라왔을 때만 읽는다.

이 문서는 폰트, 글리프, 문자 폭, 인코딩/테이블 조사 진행 상황을 기록합니다.

## 목적

- 한글 글리프를 넣을 수 있는 위치를 찾는다.
- 문자 폭 테이블과 표시 방식을 파악한다.
- 한글용 문자 매핑 전략을 세운다.

## 현재 상태

- 상태: `IN PROGRESS`

## 준비된 것

- 4bpp 타일 덤프 도구 사용 가능
- `.tbl` 기반 문자 테이블 처리 기본 지원

## 아직 확인되지 않은 것

- 실제 폰트 타일 위치
- 고정폭/가변폭 여부
- 문자 폭 테이블 위치
- 한글 글리프 삽입 가능 공간

## 최근 확인

- `0x0514xx` UI cluster 는 `0x075DD4` (`strlen`) 과 `0x03EB78` / `0x03ECCC` layout helper 를 반복 호출하는 **UI layout / slot setup 경로**에 가깝다.
- 같은 클러스터에서 따라간 `0x058720` 은 문자열 렌더러가 아니라, current tracked slot record (`0x714`) 의 좌표를 읽어 넘기는 position helper 다.
- 따라서 위 경로는 폰트/문자 매핑 자체를 찾는 direct route 로 보기 어렵다.
- 추가 확인:
  - `0x03EB78` 은 입력 바이트를 `A-Z`, `a-z`, `0-9` 범위와 비교해 `0x03003008` base 에 halfword tile index 를 쓴다.
  - `0x03ECCC` 는 `0x033658` 로 값을 4-byte 버퍼로 바꾼 뒤 `0x03EDB8` 을 통해 같은 tilemap base 에 숫자/기호를 배치한다.
  - 따라서 `0x03EB78 / 0x03ECCC / 0x03EDB8` 는 **일반 일본어 폰트 렌더러가 아니라 ASCII/숫자 UI glyph helper family** 로 보는 해석이 가장 강하다.
  - 이 helper family 는 한글 폰트 원본/문자폭 조사 대상에서 우선 제외한다.
- world-map Registry B raw companion 엔트리 `86`, `87`, `88` 을 헤더 뒤에서 바로 4bpp 덤프한 결과는 [registry_b_entry_86_tiles.png](/Users/user/test/analysis/registry_b_entry_86_tiles.png), [registry_b_entry_87_tiles.png](/Users/user/test/analysis/registry_b_entry_87_tiles.png), [registry_b_entry_88_tiles.png](/Users/user/test/analysis/registry_b_entry_88_tiles.png) 처럼 잡음에 가깝다.
- 그래서 현재는 이 raw companion 엔트리들을 **직접 폰트 raw tile 후보에서 우선 제외**한다.
- world-map 지역명 경로 `0x06A95A..0x06A972` 에서 `0x18425C + selected_location * 0x2C` 문자열 필드가 `0x014A98 -> 0x014ED0` 로 직접 전달된다.
- `0x014A98` 는 object field 와 플래그를 세팅하는 **text object / window entry setup helper** 에 가깝고, 실제 바이트 디코더로 보이지 않는다.
- `0x014ED0` 는 object `+0x0C` 문자열 포인터에서 현재 바이트를 읽으며:
  - `0x81..0x9F`, `0xE0..0xEF`: Shift-JIS multibyte lead byte 후보
  - `0x20..0x7E`: ASCII / halfwidth 경로
  - `0x00`: 문자열 종료
- `0x015A4C..0x015A80` 는 `0x03001540 + index * 0x2C` text object `11`개를 순회하며 `0x014ED0` 을 호출하므로, 이 함수는 single-shot helper 가 아니라 **공용 text object update/render engine** 에 가깝다.
- 따라서 이제 general Japanese text renderer 후보는 `0x03EB78` family 가 아니라 **`0x014A98 / 0x014ED0 / 0x015A4C` family** 로 본다.
- `0x0152A2..0x0152C4` 에서는 현재 문자코드 `u16` 를 `obj + 0x04` 기반 `u16` lookup table 로 조회한 뒤, `obj + 0x1A` stride 와 `obj + 0x08` glyph base 를 이용해 실제 glyph source pointer 를 계산한다.
- 이후 `0x01570C / 0x01578C / 0x01580C / 0x01588C` writer family 가 glyph source 를 target 으로 복사하고, low-level halfword writer 는 `0x01590C` / `0x015984` 두 종류로 갈린다.
- `0x015608` 은 `obj + 0x1F` 와 `obj + 0x10` 을 사용해 `obj + 0x14` destination pointer 를 재계산하므로, text object 가 tile page 단위 cursor/state 를 따로 가진다는 점도 보였다.
- `0x01499C` 는 font resource initializer 후보로, `obj + 0x00 = resource_ptr`, `obj + 0x04 = lookup base`, `obj + 0x08 = glyph base`, `obj + 0x1A = resource[8] stride` 를 채운다.
- 이 함수는 `resource[7] & 0x80` 에 따라 lookup base 에 `+0x40000` 을 더하고, glyph base 는 그 뒤 `+0x20000` 위치로 잡는다.
- ROM 문자열 `0x08088318 = "FONT INITIALIZE ERROR"` 도 이 함수 주변에서 참조되어 역할과 맞는다.
- `0x000290 / 0x0002CC / 0x000304 / 0x00033C` 는 상위 resource loader family 로 보인다.
- `0x000290(registry_slot)` 은 hub `0x08076530` table 에서 registry base pointer 를 고르고, `0x0002CC(entry_index, registry_slot)` 은 그 registry 의 `0x0A` record 에서 payload pointer 를 돌려준다.
- `0x000304(entry_index, registry_slot)` 은 같은 record 의 length 를 돌려주고, `0x00033C(dest, entry_index, registry_slot)` 은 DMA3 로 payload 를 `dest` 로 복사한다.
- 현재까지 확인한 주요 caller (`0x015A28`, `0x0618A4`, `0x064B5C`, `0x069D72`) 는 모두 `0x0002CC(0, 1)` 뒤 `0x01499C` 를 호출하므로, **registry slot 1 entry 0 공통 font resource** 가 여러 text object 화면에서 재사용된다는 해석이 가장 강하다.

## 다음 할 일

1. `0x0002CC(0, 1)` 의 registry slot `1` 이 기존 Registry B 분류와 정확히 대응하는지 확인
2. `0x014ED0` 또는 그 하위 helper 에서 width/advance 누적 field 확인
3. `0x01570C / 0x01578C / 0x01580C / 0x01588C` 네 writer variant 차이 확인
4. slot `1` entry `0` payload 원본의 raw tile / lookup 배치를 확인

## 진행 로그

### 2026-05-08

- 조사 도구만 준비됨

### 2026-05-09

- 한글 재삽입의 실제 병목이 폰트/문자 매핑/문자폭이라는 점을 명시하고 우선순위를 상향
- `0x0514xx` UI cluster 와 `0x058720` 을 따라가 본 결과, 이 경로는 문자 렌더링보다 layout / position 보조 루틴에 가깝다는 점을 확인
- Registry B raw companion 엔트리 `86..88` 을 4bpp 로 직접 덤프했지만 글자판이 아니라 잡음에 가까워, direct raw font 후보에서는 우선 제외
- `0x03EB78 / 0x03ECCC / 0x03EDB8` 를 추가로 따라가 본 결과, 이 helper family 는 일반 일본어 폰트가 아니라 ASCII/숫자 UI glyph tilemap writer 쪽이라는 점을 확인
- world-map 지역명 표시 경로에서 `0x014A98 -> 0x014ED0` 공통 text object family 를 잡았고, `0x014ED0` 가 Shift-JIS lead byte 범위를 직접 검사하는 general Japanese text loop 후보라는 점을 확인
- `0x0152A2..0x0152C4` 에서 문자코드가 `obj + 0x04` lookup table 과 `obj + 0x08` glyph base 를 거쳐 glyph source pointer 로 바뀌는 흐름을 확인
- `0x01499C` 가 font resource header 를 해석해 object 에 lookup base, glyph base, stride 를 심는 initializer 라는 점과, 주요 text object 화면이 모두 `0x0002CC(0, 1)` 공통 resource 를 쓴다는 점을 확인
- `0x000290 / 0x0002CC / 0x000304 / 0x00033C` loader family 가 hub `0x076530` 쪽 registry record 를 통해 이 공통 font resource 를 공급한다는 점을 확인
