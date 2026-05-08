# Registry Accessor Helpers

`0x17785C` 리소스 레지스트리는 단순 데이터 포인터 확인을 넘어서, 실제로 엔트리 필드를 읽는 Thumb helper 함수까지 확인되었다.

근거 산출물:

- [thumb_bl_to_03bc.json](/Users/user/test/analysis/thumb_bl_to_03bc.json)
- [thumb_bl_to_0414.json](/Users/user/test/analysis/thumb_bl_to_0414.json)
- [thumb_bl_to_03e4.json](/Users/user/test/analysis/thumb_bl_to_03e4.json)
- [thumb_bl_to_03e8.json](/Users/user/test/analysis/thumb_bl_to_03e8.json)
- [thumb_bl_to_68df8.json](/Users/user/test/analysis/thumb_bl_to_68df8.json)

## Helper 1: `0x03BC`

수동 Thumb 해석 기준으로 아래 성격에 가깝다.

- literal base: `0x17785C`
- index 입력을 `index * 8` 오프셋으로 변환
- `base + index * 8` 위치의 첫 번째 `u32` 반환

즉, `pointer-length` 레지스트리의 **포인터 필드 accessor** 로 보는 해석이 가장 자연스럽다.

호출자 수:

- `77`개 BL 호출 확인

대표 호출 위치:

- `0x007578`
- `0x007760`
- `0x007824`
- `0x017ED8`
- `0x01C9BC`

고정 index 호출부 메모:

- `0x007578`: literal index `0x094B` -> registry entry `0x3DDB30`, length `0x02C3`
- `0x007760`: literal index `0x093D` -> registry entry `0x3D2A40`, length `0x0320`
- `0x007824`: literal index `0x093E` -> registry entry `0x3D2D60`, length `0x06C0`

## Helper 2: `0x0414`

수동 Thumb 해석 기준으로 아래 성격에 가깝다.

- literal base: `0x17785C`
- index 입력을 `index * 8 + 4` 오프셋으로 변환
- 해당 위치의 `u32` 반환

즉, 같은 `pointer-length` 레지스트리의 **길이 필드 accessor** 로 보는 해석이 가장 자연스럽다.

호출자 수:

- `4`개 BL 호출 확인

대표 호출 위치:

- `0x00048A`
- `0x0005BC`
- `0x0008F4`
- `0x017EEC`

## 호출 패턴 메모

- 더 상위에는 `0x076530` 허브를 직접 쓰는 generic helper family (`0x000290`, `0x0002CC`, `0x000304`) 가 별도로 존재한다.
- `0x017ED8` 와 `0x017EEC` 는 가까운 위치에서 각각 `0x03BC`, `0x0414` 를 호출한다.
- 이 패턴은 `같은 index에 대해 pointer -> length` 를 연속 조회하는 흐름이라, 단순 이름 조회보다 **리소스 로더/복사 루틴** 쪽에 가깝다.
- 반대로 `0x007578`, `0x007760`, `0x007824` 같은 호출부는 현재까지 `0x03BC` 만 확인되어, 길이 없이 포인터만 쓰는 경로일 가능성이 있다.
- 다만 `포인터만 쓰는 경로` 도 모두 순수 binary lookup 은 아니다. `0x007824` 경로는 binary record 와 같은 리소스 내부 문자열 본문을 함께 사용한다.

## Generic Hub Helpers

### `0x000290`

- literal: `0x076530`
- 동작:
  - 허브 첫 `16`바이트를 로컬 버퍼로 복사
  - 입력 index 로 첫 4엔트리 중 하나를 선택해 반환

선택 대상:

1. `0x17785C`
2. `0x17C2F4`
3. `0x17C384`
4. `0x17C71C`

즉 `0x076530` 허브의 **상위 registry selector helper** 로 보는 해석이 가장 자연스럽다.

### `0x0002CC`

- 입력: `entry_index`, `registry_selector`
- 동작:
  - `0x000290` 으로 registry base 선택
  - `base + entry_index * 8` 의 첫 `u32` 반환

즉 selected registry 의 **generic pointer accessor** 다.

현재 BL 호출자 수:

- `20`

현재 caller 분류:

- `selector=1`, `entry_index=0` direct 호출 `8`개:
  - `0x000B04`
  - `0x005472`
  - `0x0091C6`
  - `0x015A28`
  - `0x01606A`
  - `0x0618A4`
  - `0x064B5C`
  - `0x069D72`
- `selector=3`, `entry_index=0/2/3/5` direct 호출 `11`개:
  - `0x06F47E`
  - `0x06F48C`
  - `0x06F556`
  - `0x070470`
  - `0x070480`
  - `0x070552`
  - `0x070564`
  - `0x070904`
  - `0x070914`
  - `0x0709E6`
  - `0x0709F8`
- 나머지 `1`개:
  - `0x000378` (`0x00033C` wrapper 내부)

### `0x000304`

- 입력: `entry_index`, `registry_selector`
- 동작:
  - `0x000290` 으로 registry base 선택
  - `base + entry_index * 8 + 4` 의 `u32` 반환

즉 selected registry 의 **generic length accessor** 다.

현재 BL 호출자 수:

- `1`

현재 caller:

- `0x000392` (`0x00033C` wrapper 내부)

즉 generic length accessor 는 현재 직접 호출되지 않고, `0x00033C` 안에서만 확인된다.

## 확인된 로더 루틴: `0x17EB4`

`0x17ED8` / `0x17EEC` 는 실제로 아래 흐름 안에 들어 있다.

- 입력:
  - `r0`: 목적지 base pointer
  - `r1`: `0x17785C` 레지스트리 index
  - `r2`, `r3`: 목적지 좌표성 16비트 인자
- 동작:
  - 같은 index 로 `0x03BC` 를 호출해 source pointer 를 읽는다.
  - 같은 index 로 `0x0414` 를 호출해 byte length 를 읽는다.
  - 길이가 0이면 그대로 종료한다.
  - `0x17CE0` 를 호출해 `base + 2 * (x + y * 32)` 목적지 주소를 계산한다.
  - DMA3 busy bit 를 폴링한 뒤, `0x040000D4` / `0x040000D8` / `0x040000DC` 에 source/destination/`(length >> 1) | 0x80000000` 를 기록해 halfword 복사를 시작한다.

즉 이 경로는 **레지스트리 엔트리를 VRAM/버퍼 쪽으로 DMA 전송하는 공용 그래픽 로더** 로 보는 해석이 가장 자연스럽다.

## 보조 helper: `0x17CE0`

- 입력: `base pointer`, `x`, `y`
- 계산식: `base + 2 * (x + y * 32)`
- 의미: 32열 halfword 단위 목적지 오프셋 계산

이 helper 때문에 `0x17EB4` 는 텍스트 조립보다 **타일맵 또는 16비트 엔트리 버퍼 채우기** 와 더 가깝다.

## 단독 accessor 경로 메모

### `0x007578` 호출부

- registry index `0x094B`
- target entry: `0x3DDB30`, length `0x02C3`
- `0x65` 바이트 간격 레코드를 고르는 흐름이 보인다.
- `extract-range` 결과 평문 `cp932` hit 는 `0` 이었다.

즉 이 경로는 현재까지 **직접 텍스트보다는 binary gameplay table 조회** 에 더 가깝다.

### `0x007760` 호출부

- registry index `0x093D`
- target entry: `0x3D2A40`, length `0x0320`
- 선택된 엔트리에서 `4-byte` 레코드를 읽어 구조체의 `+2 .. +5` 바이트 필드를 채운다.
- 이어지는 helper 는 같은 구조체에서 파생된 추가 포인터/값을 계산한다.

즉 이 경로는 **문자열 본문 직접 조회라기보다 UI/재료 metadata lookup** 에 가깝다.

### `0x007824` 호출부

- registry index `0x093E`
- target entry: `0x3D2D60`, length `0x06C0`
- 뱅크 앞쪽에는 `5-byte metadata + u16 relative string offset` 형태의 `7-byte` 레코드가 반복된다.
- `0x795C` helper 는 같은 레코드의 뒤 2바이트를 조합해 같은 뱅크 내부 문자열 포인터를 만든다.
- 뱅크 뒤쪽에는 실제 `cp932` 재료/속성명 문자열이 이어진다.

즉 이 경로는 **binary header + in-bank text body** 가 결합된 mixed resource lookup 이다.

## Helper 3: `0x03E8`

수동 Thumb 해석 기준으로 아래 성격에 가깝다.

- literal base: `0x17C7E4`
- index 입력을 `index * 8` 오프셋으로 변환
- `base + index * 8` 위치의 첫 번째 `u32` 반환

즉, `0x17C7E4` 레지스트리의 **포인터 필드 accessor** 로 보는 해석이 가장 자연스럽다.

호출자 수:

- `3`개 BL 호출 확인

대표 호출 위치:

- `0x0106E6`
- `0x010798`
- `0x010892`

caller 관찰 메모:

- 세 caller 모두 local/stack 근처 table 에서 `u16` index 를 읽은 뒤 `0x03E8` 을 호출한다.
- 반환된 포인터는 공통적으로 구조체의 `+0x8` 필드 쪽에 저장된다.
- 따라서 `0x17C7E4` 는 단순 허브 장식이 아니라, 실제 object/setup 흐름에서 참조되는 live registry 로 취급해야 한다.

이전 실패 기록:

- [thumb_bl_to_03e4.json](/Users/user/test/analysis/thumb_bl_to_03e4.json) 는 `0x03E4` 가 실제 callable helper 라는 가설을 검증하다 실패한 산출물이다.
- 현재는 `0x03E8` 이 올바른 helper entry 로 보는 편이 맞다.

## Helper 4: `0x68DF8`

수동 Thumb 해석 기준으로 아래 성격에 가깝다.

- literal base: `0x183D50`
- 입력 index 를 `index * 8` 오프셋으로 변환해 **Registry B mirror table** 엔트리를 읽는다.
- 엔트리 포인터 선두 2바이트가 `0x5A 0x50` (`"ZP"`) 인지 검사한다.
- `ZP` 가 맞으면 내부 decode 경로 (`0x68E40` 부근) 로, 아니면 raw fallback (`0x68D54`) 로 분기한다.

즉, 이 helper 는 `Registry B` 미러 테이블 전용의 **ZP-aware resource accessor/loader** 로 보는 해석이 가장 자연스럽다.

호출자 수:

- `38`개 BL 호출 확인

대표 호출 위치:

- `0x061A6E`
- `0x064C5E`
- `0x067EAA`
- `0x06847A`
- `0x06A0AA`
- `0x06D086`

보조 관찰:

- `0x68D54` 는 `0x68DF8` 의 raw fallback 경로로만 BL 호출 `1`개가 확인되었다. (`0x068E34`)
- 따라서 public/shared entry 는 사실상 `0x68DF8` 쪽으로 보는 편이 맞다.
- `0x183D50` 미러 테이블 엔트리 `50 / 115`개가 `ZP00` 또는 `ZP01` 로 시작하므로, 이 helper 가 compressed/raw mixed bank 를 처리한다는 정황과 맞아떨어진다.
- 이 helper 주변에는 미러 테이블 바로 뒤의 companion descriptor block 도 붙어 있다.
  - `0x1840F8..0x1841E7`: `destination_vram + registry_b_index + dim_a + dim_b`
  - `0x1841E8..0x18421F`: `registry_b_index + destination_palette_ram`
  - `0x184220` 이후는 별도 metadata/string tail 로 보이므로, 같은 구조가 아니다.

caller 패턴 요약:

- fixed index 직접 호출 예:
  - `0x061A6E` cluster: `0x5A`, `0x29`, `0x28`, `0x13`, `0x0B`
  - `0x064C5E` cluster: `0x5A`, `0x0E`, `0x0B`
  - `0x06630E` / `0x067EAA` cluster: `0x0A`
  - `0x06A0AA` / `0x06D086` cluster: `0x38`, `0x36`, `0x4A`
- dynamic / table-driven 호출 예:
  - `0x061D18` cluster: 테이블 엔트리에서 읽은 값에 `-1` 보정 후 index 로 사용
  - `0x067F1E` cluster: global byte 를 읽어 파생된 테이블 경로와 함께 index 를 선택
  - `0x06A0FC` / `0x06D0D8` cluster: `16-byte` descriptor row 의 `+4` 필드 값을 index 로 사용

즉 `0x68DF8` caller 는 단순한 고정 asset lookup 하나가 아니라, **fixed asset bootstrap + descriptor-driven asset selection** 두 계층이 섞여 있다.

## 현재 해석

- `0x17785C` 는 상위 레지스트리 중에서도 실제 코드 accessor 가 이미 확인된 핵심 `pointer-length` 레지스트리다.
- `0x076530` 허브에 `0x17785C` 가 여러 번 들어 있는 점도, 이 레지스트리가 공용 기준표 역할을 할 가능성을 높인다.
- `0x17C7E4` 역시 상위 허브 바깥 예외 축이지만, 이제는 `0x03E8` direct helper 와 `3`개 caller 가 확인되어 실제 accessor 사용 근거가 충분하다.
- 그리고 `0x17785C` 는 전용 helper (`0x03BC`, `0x0414`) 뿐 아니라, `0x076530` 허브 generic family 의 selector `0` 으로도 접근될 수 있다.
- 따라서 `selector=0` direct generic caller 가 안 보이는 점은 큰 이상이라기보다, 이미 전용 helper family 가 널리 쓰인 결과일 가능성이 높다.
- `Registry B` 도 이제는 concrete access route 가 비어 있는 축이 아니라, `0x183D50` 미러 테이블과 `0x68DF8` helper family 를 통해 직접 소비되는 축으로 보는 편이 맞다.
- 또 `0x000304` 는 사실상 `0x00033C` wrapper 뒤에서만 보이므로, generic `pointer+length` pair 사용도 모든 registry 에 고르게 퍼져 있지 않다.
- `0x03BC` 단독 호출은 "텍스트 아님" 또는 "문자열 포인터 직접 반환" 둘 중 하나로 단순화할 수 없다.
- 실제로는 binary table, mixed record directory, in-bank 상대 문자열 포인터가 섞여 있다.

## 다음 유력 작업

1. `0x68DF8` caller 들이 참조하는 descriptor table / global state 정리
2. `0x093D` / `0x094B` binary table 이 어떤 게임 분류를 담는지 추가 분리
