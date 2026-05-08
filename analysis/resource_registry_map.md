# Resource Registry Map

`0x17C1C0` 근처의 디스크립터만 따로 보면 구조를 오해하기 쉬워서, 상위 레지스트리 포인터 흐름을 따로 정리한다.

근거 산출물:

- [resource_registry_summary.json](/Users/user/test/analysis/resource_registry_summary.json)
- [resource_chunk_directory.md](/Users/user/test/analysis/resource_chunk_directory.md)
- [registry_accessor_helpers.md](/Users/user/test/analysis/registry_accessor_helpers.md)

## 핵심 발견

- `0x17C000..0x17D000` 범위로 포인터 검색 범위를 넓히면, `0x17C2F4`, `0x17C384`, `0x17C71C`, `0x17C7E4` 를 가리키는 참조가 확인된다.
- 특히 `0x076530` 부근에는 여러 레지스트리 시작/끝 지점을 묶어 들고 있는 작은 허브 구조가 보인다.
- 이 허브 바로 뒤에는 ASCII 문자열 `DECODE AREA OVER` 가 존재한다.
- `0x0002C0` 에 있는 `0x076530` literal 은 이 허브를 직접 쓰는 가장 상위 helper (`0x000290`) 와 연결된다.

## 포인터 허브

`0x076530` 부근 값:

- `0x076530 -> 0x17785C`
- `0x076534 -> 0x17C2F4`
- `0x076538 -> 0x17C384`
- `0x07653C -> 0x17C71C`
- `0x076540 -> 0x076530`
- `0x076544 -> 0x17785C`
- `0x076548 -> 0x17C7E4`
- `0x07654C -> 0x17785C`

이 값만으로도 단일 테이블 하나가 아니라, 여러 레지스트리 범위를 상위 구조가 나눠 관리하고 있을 가능성이 높다.

## 직접 참조와 helper 해석

직접 포인터 검색 결과:

- `0x076530` 을 직접 가리키는 값은 현재 `0x0002C0` 과 허브 내부 자기참조 `0x076540` 뿐이다.

`0x000290` helper 해석:

- `0x0002C0` literal 로 `0x076530` 을 읽는다.
- 허브 시작 `16`바이트를 로컬 버퍼에 복사한다.
- 입력 index 에 따라 첫 4엔트리 중 하나를 반환한다.

즉 이 helper 는 아래 4개 registry base 중 하나를 고르는 **상위 registry selector** 로 보인다.

1. `0x17785C`
2. `0x17C2F4`
3. `0x17C384`
4. `0x17C71C`

그 위에 쌓인 공용 accessor:

- `0x0002CC`: `(entry_index, registry_selector)` -> 선택된 registry 의 `pointer` 필드 반환
- `0x000304`: `(entry_index, registry_selector)` -> 선택된 registry 의 `length` 필드 반환

현재 BL 호출자 수:

- `0x0002CC`: `20`
- `0x000304`: `1`

현재 fixed selector 분류:

- `selector=1`: direct 호출 `8`개, 모두 `entry_index=0`
- `selector=3`: direct 호출 `11`개, `entry_index 0/2/3/5`
- 나머지 `1`개 (`0x000378`) 는 `0x00033C` wrapper 내부 공용 경로

`0x00033C` wrapper:

- `0x0002CC` + `0x000304` 를 함께 쓰는 작은 로더/설정 helper 로 보인다.
- 현재 확인된 BL 호출자 `6`개는 모두 `selector=3` 을 넘긴다.

반면 `0x17C7E4` 는 허브 안에 들어 있지만, 이 `0x000290` family 가 복사하는 첫 4엔트리 바깥에 남아 있다.

별도 direct helper 근거:

- `0x17C7E4` 직접 포인터 검색 결과는 `0x076548` 허브 항목 외에 `0x000408` literal 이 추가로 확인된다.
- 이 literal 을 쓰는 `0x03E8` helper 는 `0x17C7E4 + index * 8` 위치의 첫 `u32` 를 반환하는 pointer accessor 로 보인다.
- `0x03E8` BL 호출자는 `0x0106E6`, `0x010798`, `0x010892` 총 `3`개다.

## 현재 확인된 상위 레지스트리 범위

### Registry A

- 범위: `0x17C2F4..0x17C384`
- 엔트리 수: `18`
- 레이아웃: `pointer-length`
- 특징:
  - 연속적인 대형 리소스 구간을 가리킨다.
  - `0x6B594C` 지역/맵 문자열, `0x7A750C` 아이템 설명 계열처럼 사람이 읽을 수 있는 텍스트 구간도 일부 포함한다.

### Registry B

- 범위: `0x17C384..0x17C71C`
- 엔트리 수: `115`
- 레이아웃: `pointer-length`
- 특징:
  - 대부분 바이너리성 리소스로 보인다.
  - 현재 필터 기준으로는 텍스트성이 강한 엔트리가 거의 없다.
  - 현재까지는 허브 내부 포인터 외 concrete accessor/helper 경로가 확인되지 않았다.

### Registry C

- 범위: `0x17C71C..0x17C7E4`
- 엔트리 수: `25`
- 레이아웃: `pointer-length`
- 특징:
  - 현재 기준으로는 텍스트 히트가 없다.

### Registry D

- 범위: `0x17C7E4..0x17CB04`
- 엔트리 수: `100`
- 레이아웃: `pointer-length`
- 특징:
  - 일부 대사성 텍스트가 확인된다.
  - 예: `錬成であっさり終わらせる！`, `ちったぁ活躍しておかねえとな`

## `0x17C1C0` 테이블과의 관계

- `0x17C1C0` 테이블은 물리적으로는 이 레지스트리 묶음 바로 앞에 붙어 있다.
- 하지만 현재 확인된 상위 허브 포인터는 `0x17C2F4` 부터 시작하며, `0x17C1C0` 을 직접 가리키지 않는다.
- 또한 `0x17C1C0` 만 `length-pointer` 레이아웃이고, 상위 레지스트리들은 모두 `pointer-length` 쪽이 맞는다.

추가로:

- `0x17785C` 레지스트리는 `0x03BC`, `0x0414` helper 함수로 직접 접근하는 코드 경로가 확인되었다.
- `0x17C7E4` 레지스트리도 `0x03E8` direct helper 와 `3`개 BL caller 가 확인되어, generic family 밖의 별도 accessor 축으로 보는 근거가 생겼다.

현재 가장 안전한 해석은 아래와 같다.

- `0x17C1C0` 은 공통 레지스트리 체계의 일부라기보다 예외적인 보조 디스크립터일 수 있다.
- 혹은 상위 리소스의 하위 뷰/세부 분해표일 수 있다.
- `0x076530` 허브도 단일 평면 구조가 아니라, 최소한 "generic selector 가 쓰는 첫 4엔트리" 와 "별도 direct helper 로 빠지는 `0x17C7E4` 축" 으로 분리해서 봐야 한다.
- 또한 generic accessor 의 실제 direct 사용은 현재 `Registry A` 와 `Registry C` 로 편중되어 있다.
- `selector=0` direct generic 사용이 안 보이는 점은 `0x17785C` 전용 helper (`0x03BC`, `0x0414`) 로 설명 가능하다.
- 그 결과 현재 상위 registry 중 concrete access route 가 비어 있는 축은 사실상 `Registry B (0x17C384)` 뿐이다.

## 추가 관찰

- `0x17CE98` 는 여러 코드/데이터 위치에서 반복 참조되지만, 청크 디스크립터처럼 보이지는 않는다.
- `0x17CE98` 부근은 길이/포인터 테이블이 아니라 주소 배열에 더 가깝다.
- 따라서 `0x17CE98` 를 같은 방식의 청크 레지스트리로 취급하면 안 된다.

## 다음 유력 작업

1. `Registry B (0x17C384)` 의 concrete access route 찾기
2. `0x17C1C0` 이 왜 이 공통 레지스트리 묶음 밖에 있는지 설명할 상위 데이터 찾기
3. `0x093D` / `0x094B` 고정 인덱스 binary resource 의미 분리
