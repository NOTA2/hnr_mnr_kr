# Registry Accessor Helpers

`0x17785C` 리소스 레지스트리는 단순 데이터 포인터 확인을 넘어서, 실제로 엔트리 필드를 읽는 Thumb helper 함수까지 확인되었다.

근거 산출물:

- [thumb_bl_to_03bc.json](/Users/user/test/analysis/thumb_bl_to_03bc.json)
- [thumb_bl_to_0414.json](/Users/user/test/analysis/thumb_bl_to_0414.json)
- [thumb_bl_to_03e4.json](/Users/user/test/analysis/thumb_bl_to_03e4.json)

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

- `0x017ED8` 와 `0x017EEC` 는 가까운 위치에서 각각 `0x03BC`, `0x0414` 를 호출한다.
- 이 패턴은 `같은 index에 대해 pointer -> length` 를 연속 조회하는 흐름이라, 단순 이름 조회보다 **리소스 로더/복사 루틴** 쪽에 가깝다.
- 반대로 `0x007578`, `0x007760`, `0x007824` 같은 호출부는 현재까지 `0x03BC` 만 확인되어, 길이 없이 포인터만 쓰는 경로일 가능성이 있다.

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

## Helper 3: `0x03E4`

`0x03E4` 부근 함수는 literal base 로 `0x17C7E4` 를 사용한다.

현재 확인 결과:

- BL 호출자: `0`
- `0x080003E5` Thumb 함수 포인터 값의 32비트 저장 흔적: `0`

따라서 현재 단계에서는 아래 둘 중 하나일 가능성이 있다.

- 직접 BL 대신 다른 분기 방식으로만 도달한다.
- 유사 코드가 다른 곳에 인라인/복제되어 실제 helper 로는 거의 쓰이지 않는다.

## 현재 해석

- `0x17785C` 는 상위 레지스트리 중에서도 실제 코드 accessor 가 이미 확인된 핵심 `pointer-length` 레지스트리다.
- `0x076530` 허브에 `0x17785C` 가 여러 번 들어 있는 점도, 이 레지스트리가 공용 기준표 역할을 할 가능성을 높인다.
- 반대로 `0x17C7E4` 는 상위 허브에 포함되어 있지만, 아직은 `0x17785C` 만큼 직접적인 accessor 사용 근거가 부족하다.

## 다음 유력 작업

1. `0x007578`, `0x007760`, `0x007824` 같은 `0x03BC` 단독 호출부를 더 해석해 `포인터만 쓰는 경로` 의 의미를 확인
2. `0x17785C` 와 `0x076530` 허브 사이의 연결 방식이 데이터 선택용인지, 로더 초기화용인지 확인
