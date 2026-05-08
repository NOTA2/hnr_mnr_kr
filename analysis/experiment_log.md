# Experiment Log

이 문서는 조사 과정에서 시도한 가설, 결과, 실패, 교훈을 기록합니다.

목표는 "같은 실수를 다시 하지 않기"입니다.

## 작성 규칙

- 각 항목은 `가설`, `시도`, `결과`, `판정`, `교훈`을 포함합니다.
- 실패도 성공만큼 중요하게 기록합니다.
- 다시 같은 시도를 할 때는 무엇이 달라졌는지 명시합니다.

## 2026-05-08

### 실험 1

- 가설: ROM 안의 일본어 문자열은 일부가 `cp932 + 00 terminator` 평문일 수 있다.
- 시도: `scan-text` 계열 탐색과 범위 추출을 사용해 문자열 후보를 검사했다.
- 결과: 시스템 메시지, 아이템, 지역명, 기술명 등 여러 문자열이 평문으로 확인되었다.
- 판정: `성공`
- 교훈: 이 게임은 최소한 일부 텍스트에 대해서는 직접 추출/번역/재삽입 경로가 가능하다.

### 실험 2

- 가설: 전체 ROM을 단순 `cp932` 후보 문자열로 스캔해도 바로 쓸 수 있는 텍스트가 많이 나올 것이다.
- 시도: 초기 단순 스캔으로 문자열 후보를 폭넓게 수집했다.
- 결과: 코드 조각과 잡음이 다수 섞였다.
- 판정: `부분 실패`
- 교훈: 일본어 비율, 의심스러운 ASCII 비율, 종료 바이트, 밀집도 같은 필터 없이는 결과를 바로 믿으면 안 된다.

### 실험 3

- 가설: `0x18425C` 지역명 뱅크는 일반 GBA 절대 포인터로 참조될 수 있다.
- 시도: `find-pointers` 로 `0x18425C` 참조를 검색했다.
- 결과: `0x06A574`, `0x06A9A8`, `0x08C06C`, `0x08C0C4` 에서 포인터가 확인되었다.
- 판정: `성공`
- 교훈: 적어도 일부 텍스트 뱅크는 표준적인 절대 포인터 방식으로 관리된다.

### 실험 4

- 가설: `0x3D2059` 와 `0x3D329C` 대형 텍스트 뱅크도 같은 절대 포인터 방식일 수 있다.
- 시도: `find-pointers` 로 직접 검색했다.
- 결과: 유효한 절대 포인터를 찾지 못했다.
- 판정: `실패`
- 교훈: 이 뱅크들에 대해 같은 검색을 반복하는 대신, 인덱스/구조체/상대 오프셋/간접 참조 가능성으로 전환해야 한다.

### 실험 5

- 가설: `0x3Dxxxx` 텍스트 뱅크는 3바이트 오프셋 흔적으로라도 잡힐 수 있다.
- 시도: `0x3D2059`, `0x3D329C`, `0x3D3D34` 의 하위 3바이트 패턴을 검색했다.
- 결과:
  - `0x3D2059`: 0 hits
  - `0x3D329C`: 0 hits
  - `0x3D3D34`: 2 hits (`0x517DEE`, `0x52061B`) but useful evidence로 보기 어려움
- 판정: `실패`
- 교훈: 단순 3바이트 오프셋 흔적 탐색만으로는 이 대형 뱅크의 참조 구조를 설명하기 어렵다.

### 실험 6

- 가설: 기술명은 한 곳에만 저장되어 있을 것이다.
- 시도: `0x3D2059` 계열 전투 기술 뱅크와 `0x08B62C` UI 기술 뱅크를 비교했다.
- 결과: 일부 기술명이 두 뱅크에 중복되는 것으로 보인다.
- 판정: `부분 성공`
- 교훈: 한 문자열을 한 번만 번역/교체하면 게임 전체가 다 반영된다고 가정하면 안 된다.

### 실험 7

- 가설: `0x3D2059` 전투 뱅크는 포인터 대상 문자열 모음이 아니라 순차적인 레코드 목록일 수 있다.
- 시도: `0x3D2040` 부근의 0종단 문자열을 필터 없이 순서대로 복원하고, 문자열 간격 패턴을 확인했다.
- 결과: `이름 -> 설명 -> 이름 -> 설명` 흐름이 이어지고, 일부 구간은 `ﾇﾙ` 자리표시자도 확인되었다.
- 판정: `성공`
- 교훈: 이 뱅크는 개별 문자열 포인터를 찾기보다 인덱스/레코드 접근 구조를 추적하는 편이 맞다.

### 실험 8

- 가설: `0x3D329C` 능력 뱅크는 `이름+0x0B+설명` 형태의 순차 문자열 목록일 수 있다.
- 시도: `0x3D327E` 부근의 0종단 문자열을 필터 없이 복원했다.
- 결과: `黒曜石　　　　　火山岩の一種`, `ブラックペーパー因縁がある黒い紙` 같은 결합 문자열 레코드가 연속 확인되었다.
- 판정: `성공`
- 교훈: 이 뱅크는 설명이 별도 포인터로 떨어진 구조가 아니라 결합 레코드 구조일 가능성이 높다.

### 실험 9

- 가설: `battle/ability` 뱅크에서 일부 레코드가 빠지는 이유는 추출 범위보다 필터 쪽 문제일 수 있다.
- 시도: 누락된 선두 레코드 `黒曜石　　　　　火山岩の一種` 의 printable 비율을 직접 계산했다.
- 결과: 전각 공백 `U+3000` 이 비정상 문자처럼 계산되어 printable 비율이 `0.6` 까지 떨어졌다.
- 판정: `성공`
- 교훈: 추출 필터에서 전각 공백을 허용 문자로 취급해야 패딩이 있는 일본어 설명 문자열을 놓치지 않는다.

### 실험 10

- 가설: 전각 공백 허용 후 추출 범위를 재보정하면 `battle/ability` 추출본이 더 완전해질 것이다.
- 시도: 추출 필터를 수정하고, 전투 뱅크를 `0x3D2036~0x3D2557`, 능력 뱅크를 `0x3D327E~0x3D6277` 로 다시 추출했다.
- 결과:
  - `battle_texts.json`: `52 -> 104`
  - `ability_texts.json`: `252 -> 409`
- 판정: `성공`
- 교훈: 문자열 필터와 범위 경계는 데이터 구조 조사와 같이 움직여야 하며, 추출본이 적다고 해서 원문이 없는 것으로 단정하면 안 된다.

### 실험 11

- 가설: `0x3Dxxxx` 영역은 더 큰 리소스 청크 디렉터리로 관리될 수 있다.
- 시도: ROM 전체에서 `0x083Dxxxx` 범위의 32비트 값을 찾고, 밀집 구간을 조사했다.
- 결과: `0x17C1C0` 부근에서 길이값과 `0x083Dxxxx` ROM 주소가 8바이트 간격으로 반복되는 테이블이 확인되었다.
- 판정: `성공`
- 교훈: 문자열 뱅크를 단일 텍스트 덩어리로만 보지 말고, 상위 리소스 청크 분할 구조 안에서 이해해야 한다.

### 실험 12

- 가설: `0x17C1C0` 부근 리소스 테이블은 직접 포인터로 참조될 수 있다.
- 시도: `find-pointers` 로 `0x17C1C0`, `0x17C1D0`, `0x17C1E4` 등을 직접 검색했다.
- 결과: 유효한 절대 포인터를 찾지 못했다.
- 판정: `실패`
- 교훈: 청크 디렉터리 접근도 직접 포인터가 아니라 상수 계산, 상대 주소, 혹은 다른 상위 테이블을 거칠 수 있다.

### 실험 13

- 가설: `0x3D2D60..0x3D3420` 청크에는 별도 텍스트 묶음이 있을 수 있다.
- 시도: 청크 전체를 `extract-range` 로 추출했다.
- 결과: 재료/속성명과 설명이 결합된 문자열 `43` 건이 확인되었다.
- 판정: `성공`
- 교훈: 청크 경계를 기준으로 보면 기존 `ability_texts` 외에 별도 카테고리의 번역 대상이 추가로 보일 수 있다.

### 실험 14

- 가설: `0x17C1C0` 테이블은 `pointer + length` 가 아니라 `length + pointer` 순서일 수 있다.
- 시도: `inspect-chunk-table` 명령으로 `pointer-length` 와 `length-pointer` 를 자동 점수화했다.
- 결과: `length-pointer score=175 valid=35`, `pointer-length score=0 valid=0` 이 나왔다.
- 판정: `성공`
- 교훈: 이 테이블을 다시 볼 때는 항상 `u32 length`, `u32 rom_address` 순서를 기본값으로 삼아야 한다.

### 실험 15

- 가설: `0x17C1C0` 테이블은 겹치지 않는 청크 디렉터리일 수 있다.
- 시도: 각 엔트리의 파일 범위를 계산하고 이전 엔트리와의 간격/겹침을 비교했다.
- 결과: `index 5`, `8`, `10`, `12`, `13`, `16`, `22` 등 여러 엔트리가 이전 엔트리와 겹쳤다.
- 판정: `실패`
- 교훈: 이 구조를 "단순 비중첩 청크 분할표"로 다시 가정하면 같은 해석 오류를 반복하게 된다.

### 실험 16

- 가설: 같은 테이블을 더 넓게 훑으면 곧바로 새로운 깨끗한 텍스트 뱅크를 많이 찾을 수 있다.
- 시도: `inspect-chunk-table` 로 `80`개 엔트리를 `--scan-text` 하여 텍스트 히트를 넓게 확인했다.
- 결과: 뒤쪽 엔트리에서도 `text_hits` 가 나오지만, 큰 바이너리 자원 내부의 잡음과 혼합 문자열이 섞여 있어 바로 번역 대상이라고 보기 어려웠다.
- 판정: `부분 실패`
- 교훈: `text_hits > 0` 만으로 새 텍스트 뱅크를 확정하지 말고, 범위 크기와 문자열 품질을 함께 봐야 한다.

### 실험 17

- 가설: `0x17C1C0` 주변을 조금 더 넓게 보면, 이 테이블을 간접적으로 가리키는 상위 포인터 범위를 찾을 수 있다.
- 시도: 직접 `0x17C1C0` 하나만 찾지 않고, `0x17C000..0x17D000` 범위 전체를 가리키는 32비트 포인터를 수집했다.
- 결과: `0x076534 -> 0x17C2F4`, `0x076538 -> 0x17C384`, `0x07653C -> 0x17C71C`, `0x076548 -> 0x17C7E4` 같은 상위 포인터가 확인되었다.
- 판정: `성공`
- 교훈: 직접 포인터가 안 잡힌다고 해서 주변 상위 레지스트리까지 없는 것은 아니다. 범위를 넓혀서 관련 구간 전체를 봐야 한다.

### 실험 18

- 가설: `0x076530` 부근 포인터들은 우연한 값이 아니라 여러 리소스 레지스트리 구간의 경계일 수 있다.
- 시도: `0x17C2F4..0x17C384`, `0x17C384..0x17C71C`, `0x17C71C..0x17C7E4`, `0x17C7E4..0x17CB04` 를 각각 엔트리 수로 환산해 `inspect-chunk-table` 로 해석했다.
- 결과: 네 구간 모두 연속된 유효 엔트리 묶음으로 읽혔고, 레이아웃은 공통적으로 `pointer-length` 쪽이 맞았다.
- 판정: `성공`
- 교훈: `0x076530` 부근은 개별 청크 포인터가 아니라, 여러 레지스트리의 시작/끝을 가리키는 상위 허브로 보는 편이 타당하다.

### 실험 19

- 가설: `0x17C1C0` 도 이 공통 상위 레지스트리와 같은 레이아웃일 것이다.
- 시도: `0x17C1C0` 과 `0x17C2F4` 이후 구간들의 자동 레이아웃 결과를 비교했다.
- 결과: `0x17C1C0` 은 `length-pointer`, 이후 레지스트리들은 `pointer-length` 로 갈렸다.
- 판정: `실패`
- 교훈: 같은 주변 주소대에 있다고 해서 같은 디스크립터 규칙을 공유한다고 가정하면 안 된다. `0x17C1C0` 은 예외 또는 보조 구조일 가능성을 따로 관리해야 한다.

### 실험 20

- 가설: `0x17CE98` 도 같은 종류의 청크/레지스트리 테이블일 수 있다.
- 시도: `0x17CE98` 부근 raw 데이터를 확인하고, 이를 참조하는 코드/데이터 위치를 비교했다.
- 결과: `0x17CE98` 부근은 길이/포인터 엔트리보다 주소 배열에 더 가까웠고, 디버그 메뉴 인근에서도 직접 참조되었다.
- 판정: `실패`
- 교훈: `0x17Cxxx` 대역의 모든 구조를 한 종류의 리소스 레지스트리로 묶어 해석하면 안 된다.

### 실험 21

- 가설: `0x17785C` 상위 레지스트리는 실제 코드에서 공용 accessor 함수로 접근할 수 있다.
- 시도: `find-thumb-bl` 기능을 추가하고, `0x03BC`, `0x0414` 를 호출하는 Thumb BL 위치를 전역 검색했다.
- 결과: `0x03BC` 는 `77`개 호출자, `0x0414` 는 `4`개 호출자가 확인되었다.
- 판정: `성공`
- 교훈: `0x17785C` 는 단순 데이터 후보가 아니라, 실제 공용 로더/조회 루틴에서 쓰이는 핵심 `pointer-length` 레지스트리로 취급해도 된다.

### 실험 22

- 가설: `0x03E4` 의 `0x17C7E4` helper 도 같은 방식으로 널리 호출될 것이다.
- 시도: `find-thumb-bl` 로 `0x03E4` 호출자를 찾고, `0x080003E5` Thumb 함수 포인터 저장 흔적도 검색했다.
- 결과: BL 호출자 `0`, 함수 포인터 흔적 `0` 이었다.
- 판정: `실패`
- 교훈: `0x17C7E4` 는 상위 허브에 포함되어 있어도, `0x17785C` 와 동일한 공용 accessor 패턴을 가정하면 안 된다.

### 실험 23

- 가설: `0x017ED8` / `0x017EEC` 같이 가까운 위치의 accessor 호출은 실제 리소스 로더 흐름일 수 있다.
- 시도: `0x017EB0..0x017F20` 부근 raw Thumb 코드를 확인해 `0x03BC` 와 `0x0414` 호출 위치를 비교했다.
- 결과: 두 호출은 같은 함수 안에서 거의 연속으로 나타나고, 이후 다른 처리 함수 호출로 이어진다.
- 판정: `성공`
- 교훈: `pointer만 쓰는 호출부` 와 `pointer+length를 함께 쓰는 호출부` 를 분리해 보면, 조회 루틴과 로더 루틴을 구분하는 데 도움이 된다.

### 실험 24

- 가설: 메뉴에서 보이는 `"セーブ"` 계열 문구는 `00` 종단 평문이 아니라도 ROM 어딘가에 `cp932` 로 박혀 있을 수 있다.
- 시도:
  - `search-text "セーブ"` 로 히트 오프셋을 먼저 찾았다. (`0x772E64` 등)
  - 해당 구간 raw 바이트를 확인해 `... セーブ ... 0x10 0xFF ...` 패턴을 관측했다.
  - 기존 `extract-range` / delimited `scan-text` 로는 잡히지 않아, `scan-text` 에 **범위 제한 + 슬라이딩 스캔**을 추가하고 `terminator=0x10` 으로 추출했다.
- 결과: `0x772E64..0x773260` 블록에서 세이브/진행 관련 문자열 `5`개를 [save_menu_texts.json](/Users/user/test/analysis/save_menu_texts.json) 으로 확보했다.
- 판정: `성공`
- 교훈: 이 게임은 `00` 종단 평문뿐 아니라, 명령 스트림 내부에 텍스트가 섞인 저장 방식도 사용한다. 이런 경우에는 "범위 기반 delimited 추출"이 아니라 "슬라이딩 스캔"이 필요하다.

### 실험 25

- 가설: 크레딧 화면의 직책/회사/이름 텍스트도 `cp932 + 00 terminator` 평문이며, 표준 절대 포인터로 참조될 수 있다.
- 시도: `scan-text --start/--end` 로 `0x08C3AC` 부근의 후보를 확인한 뒤 `extract-range` 로 범위를 추출했다. 이후 `find-pointers` 로 `0x08C3AC` 참조 포인터를 탐색했다.
- 결과: `0x08C3AC~0x08CE00` 범위에서 크레딧 문자열 `10`건이 추출되었고, `0x184E20` 에서 `0x08C3AC` 를 가리키는 포인터 `1`건이 확인되었다.
- 판정: `성공`
- 교훈: "새 텍스트 뱅크 발견 → 범위 추출 → 포인터 검증" 흐름을 유지하면, 메뉴/대사 계열도 같은 방식으로 확장할 수 있다.

### 실험 26

- 가설: `0x017ED8` / `0x017EEC` 호출부는 같은 index 에 대해 `0x03BC` / `0x0414` 를 조회한 뒤 실제 리소스 로드나 복사를 수행하는 공용 루틴일 수 있다.
- 시도:
  - `capstone` 이 없는 환경이라, 원본 ROM halfword 를 임시 ARMv4T 오브젝트로 재조립한 뒤 `clang --target=armv4t-none-eabi` + `objdump --triple=thumbv4t-none-eabi` 로 `0x17EB4`, `0x17CE0` 주변을 디스어셈블했다.
  - 같은 결과에서 `0x03BC`, `0x0414`, `0x17CE0` 호출 순서와 `0x040000D4` / `0x040000D8` / `0x040000DC` 리터럴 사용 여부를 확인했다.
- 결과:
  - `0x17CE0` 는 `(base, x, y)` 를 받아 `base + 2 * (x + y * 32)` 를 계산하는 helper 로 해석되었다.
  - `0x17EB4` 는 같은 16비트 index 에 대해 `0x03BC` 로 source pointer, `0x0414` 로 byte length 를 읽는다.
  - 길이가 0이 아니면 `0x17CE0` 로 목적지 주소를 계산하고, DMA3 busy bit 를 폴링한 뒤 `0x040000D4` / `0x040000D8` / `0x040000DC` 에 source/destination/`(length >> 1) | 0x80000000` 를 써서 halfword 복사를 시작한다.
- 판정: `성공`
- 교훈: `0x17785C` 의 `pointer+length` 경로는 적어도 이 호출부에서는 텍스트 로더가 아니라 그래픽/타일맵 리소스 DMA 경로다. 다음 accessor 해석은 `0x03BC` 단독 호출부를 우선 봐야 한다.

### 실험 27

- 가설: 세션 시작 때 긴 문서와 전체 로그를 매번 읽는 구조는 토큰 낭비가 크고, 실제 필요한 문서만 읽도록 라우팅을 분리하는 편이 더 효율적이다.
- 시도: 시작용 요약 문서 `session_start.md`, 현재 제약 요약 `current_constraints.md`, 작업별 참고 맵 `reference_map.md` 를 만들고, 총괄/핸드오프/반복 방지 문서를 더 짧게 압축했다.
- 결과: 매 세션의 기본 읽기 경로를 `session_start -> agent_handoff -> current_constraints -> 활성 트랙 문서` 로 줄일 수 있게 되었다.
- 판정: `성공`
- 교훈: 전체 로그와 모든 참고 문서는 기본 입력이 아니라 선택적 참조로 두는 편이 장기 자동화와 후속 세션에 더 적합하다.

### 실험 28

- 가설: `0x007578`, `0x007760`, `0x007824` 같은 `0x03BC` 단독 호출부는 모두 단순 binary table 이 아니라, 일부는 텍스트 뱅크 앞단 메타데이터와 문자열 본문을 함께 읽을 수 있다.
- 시도:
  - 원본 ROM 슬라이스를 임시 ARMv4T 오브젝트로 재조립한 뒤 `clang --target=armv4t-none-eabi` + `objdump --triple=thumbv4t-none-eabi` 로 `0x755C`, `0x7754`, `0x7818`, `0x795C` 주변을 디스어셈블했다.
  - `0x17785C + index * 8` 엔트리를 직접 확인해 `0x093D`, `0x093E`, `0x094B` 의 포인터/길이를 읽었다.
  - 이어서 `extract-range` 와 raw hex 확인으로 각 target range 의 문자열 존재 여부를 비교했다.
- 결과:
  - `0x007760` 경로는 `0x093D -> 0x3D2A40 (0x0320)` binary 4-byte record table 을 읽는다.
  - `0x007824` 경로는 `0x093E -> 0x3D2D60 (0x06C0)` resource 를 읽고, 앞쪽 `7-byte` 레코드 (`5바이트 메타데이터 + u16 상대 문자열 오프셋`) 와 뒤쪽 `cp932` 문자열 영역을 함께 사용한다.
  - `0x795C` helper 는 같은 `0x093E` 레코드의 마지막 2바이트를 같은 뱅크 내부 상대 문자열 오프셋으로 해석해 실제 문자열 포인터를 만든다.
  - `0x007578` 경로는 `0x094B -> 0x3DDB30 (0x02C3)` binary table 을 읽으며, `extract-range` 기준 평문 hit 는 `0` 이었다.
- 판정: `성공`
- 교훈: `0x03BC` 단독 호출부를 "텍스트 아님" 또는 "문자열 포인터 직접 반환" 둘 중 하나로 단정하면 안 된다. binary record directory 와 in-bank 상대 문자열 포인터를 함께 보는 mixed resource 관점이 필요하다.

### 실험 29

- 가설: `0x076530` 허브는 단순 데이터 묶음이 아니라, ROM 초반의 공용 helper 가 직접 참조하는 상위 registry selector 구조일 수 있다.
- 시도:
  - `find-pointers` 로 `0x076530`, `0x17C2F4`, `0x17C384`, `0x17C71C`, `0x17C7E4` 직접 참조를 다시 조사했다.
  - `0x0240..0x0340` 슬라이스를 ARMv4T 오브젝트로 재조립해 `0x000290`, `0x0002CC`, `0x000304` 주변을 디스어셈블했다.
  - `find-thumb-bl` 로 `0x000290`, `0x0002CC`, `0x000304` 호출자를 수집했다.
- 결과:
  - `0x076530` 직접 참조는 현재 `0x0002C0` literal 과 허브 내부 `0x076540` 자기참조만 확인되었다.
  - `0x000290` helper 는 `0x0002C0` literal 을 통해 `0x076530` 을 읽고, 허브 첫 `16`바이트를 로컬 버퍼로 복사한 뒤 첫 4엔트리 중 하나를 선택해 반환한다.
  - 이 첫 4엔트리는 `0x17785C`, `0x17C2F4`, `0x17C384`, `0x17C71C` 이다.
  - `0x0002CC` 는 선택된 registry 의 `pointer` 필드를, `0x000304` 는 `length` 필드를 읽는 generic accessor 로 해석된다.
  - BL 호출자 수는 `0x0002CC = 20`, `0x000304 = 1`, `0x000290 = 2` 였다.
  - `0x17C7E4` 는 허브 안에 있지만 이 generic helper family 가 복사하는 4엔트리 바깥에 남아 있다.
- 판정: `성공`
- 교훈: `0x076530` 허브는 "상위 registry selector + generic accessor family" 관점으로 다뤄야 한다. 또한 허브 전체가 단일한 규칙으로 소비된다고 가정하면 안 되고, `0x17C7E4` 같은 예외 축은 별도로 추적해야 한다.

### 실험 30

- 가설: `0x0002CC` direct caller 들은 registry selector 값 몇 개에 집중될 수 있고, 그 분포를 보면 어떤 상위 registry 가 실제로 공용 accessor family 를 쓰는지 좁힐 수 있다.
- 시도:
  - `find-thumb-bl` 로 `0x0002CC`, `0x000304`, `0x00033C` caller 목록을 다시 수집했다.
  - caller 가 몰린 주소대 (`0x000B04`, `0x005472`, `0x0091C6`, `0x015A28`, `0x01606A`, `0x0618A4`, `0x064B5C`, `0x069D72`, `0x06F47E..0x06F556`, `0x070470..0x070564`, `0x070904..0x0709F8`) 를 ARMv4T 오브젝트로 재조립해 직전 immediate setup 을 확인했다.
- 결과:
  - direct `0x0002CC` caller `20`개 중 고정 selector 로 확인된 값은 `1` 과 `3` 뿐이었다.
  - `selector=1` direct 호출 `8`개는 모두 `entry_index=0` 으로 `Registry A (0x17C2F4)` 첫 엔트리를 읽는다.
  - `selector=3` direct 호출 `11`개는 `entry_index 0/2/3/5` 를 읽으며 `0x06F4xx`, `0x0704xx`, `0x0709xx` 군집으로 모인다.
  - 남은 `1`개 (`0x000378`) 는 고정 selector 호출이 아니라 `0x00033C` wrapper 내부 공용 경로였다.
  - `0x000304` 의 유일한 BL 호출자 `0x000392` 도 같은 `0x00033C` wrapper 내부 길이 조회였다.
  - `0x00033C` 의 알려진 BL 호출자 `6`개는 현재 모두 `selector=3` 을 넘긴다.
- 판정: `성공`
- 교훈: generic hub accessor family 의 실제 사용은 전체 registry 에 고르게 퍼져 있지 않다. 현재 direct caller 기준으로는 `Registry A` 와 `Registry C` 로 편중되어 있고, `selector=0` / `2` 경로는 다른 helper 나 다른 상위 흐름을 통해 접근할 가능성을 우선 의심해야 한다.

### 실험 31

- 가설: `0x17C7E4` direct helper 가 없다는 이전 결론은 helper entry 주소를 `0x03E4` 로 잘못 잡은 결과일 수 있다.
- 시도:
  - `find-pointers` 로 `0x17C384`, `0x17C71C`, `0x17C7E4` 직접 참조를 다시 비교했다.
  - `find-thumb-bl` 를 `0x03E4` 와 `0x03E8` 양쪽에 다시 실행했다.
  - `0x03E8` 주변과 caller `0x0106E6`, `0x010798`, `0x010892` 슬라이스를 ARMv4T 오브젝트로 재조립해 Thumb 흐름을 확인했다.
- 결과:
  - `0x17C384`, `0x17C71C` 는 여전히 허브 내부 참조 `1`건씩만 확인되었다.
  - `0x17C7E4` 는 허브 항목 `0x076548` 외에 `0x000408` literal 이 추가로 확인되었다.
  - `find-thumb-bl 0x03E4` 결과는 여전히 `0`건이었지만, `find-thumb-bl 0x03E8` 에서는 caller `3`개 (`0x0106E6`, `0x010798`, `0x010892`) 가 확인되었다.
  - `0x03E8` helper 는 `0x17C7E4` literal base 위에서 `index * 8` 후 첫 `u32` 를 읽는 pointer accessor 로 해석된다.
  - 세 caller 는 공통적으로 `u16` index 를 읽어 `0x03E8` 을 호출하고, 반환 포인터를 구조체 `+0x8` 필드에 저장한다.
- 판정: `성공`
- 교훈: `0x17C7E4` 는 generic 허브 밖의 별도 direct helper 축으로 실제 사용된다. 따라서 `selector=0` 부재는 `0x17785C` 전용 helper 로 설명 가능하고, 현재 상위 registry 중 concrete access route 가 가장 비어 있는 축은 `Registry B (0x17C384)` 다.

### 실험 32

- 가설: `Registry B (0x17C384)` 는 실제 access route 가 없는 dead registry 가 아니라, 다른 ROM 위치에 있는 미러 테이블과 전용 loader helper 를 통해 소비될 수 있다.
- 시도:
  - `inspect-chunk-table` 로 `0x17C384` 부터 `115`개 `pointer-length` 엔트리를 [registry_b_entries.json](/Users/user/test/analysis/registry_b_entries.json), [registry_b_entries_textscan.json](/Users/user/test/analysis/registry_b_entries_textscan.json) 으로 분리했다.
  - 각 엔트리 포인터의 외부 xref 를 전수 조사해 [registry_b_pointer_xrefs.json](/Users/user/test/analysis/registry_b_pointer_xrefs.json) 으로 저장했다.
  - `0x183D50` 부근 raw table 을 직접 확인해 원본 `Registry B` 와 entry pointer / length 가 완전히 일치하는지 비교했고, 결과를 [registry_b_mirror_summary.json](/Users/user/test/analysis/registry_b_mirror_summary.json) 에 기록했다.
  - `0x183D50` direct ref 와 literal pool 이 걸리는 `0x068D20..0x068E80` 슬라이스를 ARMv4T 오브젝트로 재조립해 Thumb 흐름을 확인했다.
  - `find-thumb-bl 0x68DF8` 로 공용 helper caller 를 수집해 [thumb_bl_to_68df8.json](/Users/user/test/analysis/thumb_bl_to_68df8.json) 을 생성했다.
- 결과:
  - `Registry B` 엔트리 `115 / 115`개가 `0x183D50` 에 정확히 같은 `pointer-length` 미러 테이블로 다시 존재했다.
  - 원본 엔트리 포인터는 외부에서 모두 정확히 한 번씩 이 미러 테이블 위치에 다시 나타났다.
  - `0x183D50` base 자체는 direct ref `22`개가 확인되었고, `0x17C384` 원본 base 는 허브 참조 외에 거의 사용 흔적이 없다.
  - helper `0x068DF8` 는 `0x183D50 + index * 8` 엔트리를 읽고, 선두 2바이트가 `ZP` 인지 검사해 decode helper (`0x068E40` 부근) 또는 raw fallback (`0x068D54`) 로 분기한다.
  - `0x068DF8` BL caller 는 `38`개였다.
  - 미러 엔트리 `50 / 115`개는 `ZP00` 또는 `ZP01` 로 시작했다.
- 판정: `성공`
- 교훈: `Registry B` 는 "selector=2 generic caller 가 안 보이는 미해결 축" 이 아니라, **hub base 와 다른 미러/loader 계층** 에서 소비되는 live asset bank 로 봐야 한다. 다음 질문은 access route 존재 여부가 아니라, `0x68DF8` caller 들이 실제로 어떤 index 군과 companion descriptor 를 쓰는가다.

### 실험 33

- 가설: `0x068DF8` caller 는 모두 같은 성격의 direct asset lookup 이 아니라, fixed index 경로와 descriptor-driven 경로가 섞여 있을 수 있다.
- 시도:
  - caller 가 몰린 cluster (`0x061A40..0x061E10`, `0x064C40..0x065930`, `0x0662F0..0x0663C0`, `0x067E90..0x068620`, `0x06A090..0x06A120`, `0x06D070..0x06D100`) 를 ARMv4T 오브젝트로 재조립해 Thumb 흐름을 확인했다.
  - 각 cluster 에서 `0x068DF8` 호출 직전 `r1` 설정 방식을 추적했다.
- 결과:
  - 여러 cluster 에서 fixed index 호출이 직접 확인되었다. 대표적으로 `0x5A`, `0x29`, `0x28`, `0x13`, `0x0B`, `0x0E`, `0x0A`, `0x38`, `0x36`, `0x4A` 가 보인다.
  - 반면 다른 경로에서는 global byte 나 테이블 엔트리에서 읽은 값을 가공해 index 로 사용한다.
  - `0x06A0FC` / `0x06D0D8` 계열은 `16-byte` descriptor row 의 `+4` 필드 값을 `0x068DF8` index 로 넘기는 루프 구조를 가진다.
  - `0x061D18` 계열은 테이블 값에 `-1` 보정을 걸어 index 로 쓰는 동적 경로를 가진다.
- 판정: `성공`
- 교훈: `0x068DF8` 는 단순 고정 sprite loader 하나가 아니라, **fixed bootstrap asset + descriptor-driven asset selection** 이 섞인 공용 helper 다. 따라서 다음 단계는 단순 caller 수집보다 descriptor table 원본과 global state 의미를 정리하는 쪽이 더 가치가 크다.

### 실험 34

- 가설: `0x183D50` 미러 테이블 바로 뒤 `0x1840E8` 영역은 Registry B asset 을 목적지 메모리로 배치하는 companion descriptor block 일 수 있다.
- 시도:
  - `0x1840E8..0x1842C8` raw 값을 직접 확인해 VRAM (`0x0601xxxx`) / palette RAM (`0x050002xx`) 패턴을 찾았다.
  - `find-pointers` 로 `0x1840E8`, `0x1841E8` direct ref 를 각각 조사했다.
  - `registry_b_entries.json` 와 대조해 descriptor 안의 index 값이 실제 Registry B 엔트리로 이어지는지 확인했다.
- 결과:
  - `0x1840F8..0x1841E7` 에 `15 * 16-byte` row 가 존재하며, `destination_vram + registry_b_index + dim_a + dim_b` 로 읽는 해석이 가장 자연스럽다.
  - `0x1841E8..0x18421F` 에 `7 * 8-byte` row 가 존재하며, `registry_b_index + destination_palette_ram` 로 읽는 해석이 가장 자연스럽다.
  - 타일 descriptor 의 index 는 `0x59`, `0x57`, `0x58`, `0x56`, `0x4E`, `0x4F`, `0x4B`, `0x4D`, `0x53`, `0x55`, `0x51`, `0x4C`, `0x52`, `0x54`, `0x6F` 였다.
  - palette descriptor 의 index 는 `0x61`, `0x60`, `0x5F`, `0x5C`, `0x5D`, `0x5E`, `0x70` 였다.
  - `0x184220` 이후에는 다른 metadata 와 문자열이 이어져, 전체 `0x1840E8..` 영역이 uniform struct 는 아니라는 경계도 확인되었다.
- 판정: `성공`
- 교훈: 미러 테이블 뒤를 한 덩어리로 취급하지 말고, 최소한 `tile descriptor array`, `palette descriptor array`, `metadata/string tail` 로 나눠서 추적해야 한다.

### 실험 35

- 가설: `0x184220` 이후 tail 은 잡다한 문자열 뭉치가 아니라, order table 과 fixed-size location record table 로 이어질 수 있다.
- 시도:
  - `location_texts.json` 의 지역명 오프셋 간격을 비교해 record stride 후보를 확인했다.
  - `0x184220..0x1843FF` raw 값을 직접 읽어 `u32` 필드와 name field 경계를 재구성했다.
  - `find-pointers` 로 `0x184248` record base 와 `0x18425C` first name field 의 direct ref 수를 비교했다.
- 결과:
  - `0x184220..0x184244` 는 `3, 4, 0, 2, 7, 9, 5, 1, 6, 8` 값의 `10-entry` permutation/order table 로 보인다.
  - `0x184248..0x1843FF` 는 `10 * 0x2C` fixed-size location record table 로 읽힌다.
  - 각 row 는 `5 * u32 metadata + 0x18-byte name field` 구조로 보이며, 이름은 row 시작 `+0x14` 에 들어 있다.
  - 기존 `0x18425C` 지역명 문자열은 첫 location record (`0x184248`) 의 name field 로 재해석되었다.
  - direct ref 는 `0x184248 = 12`, `0x18425C = 4` 로 확인되어, 실제 소비 단위는 문자열보다 record table 일 가능성이 높다.
- 판정: `성공`
- 교훈: 이미 문자열이 추출되었다고 해서 그 구간을 곧바로 standalone text bank 로 확정하면 안 된다. fixed-size record 안의 name field 일 수 있으므로, stride 와 base pointer 를 함께 확인해야 한다.

### 실험 36

- 가설: `location record table` 뒤쪽 tail 은 추가적인 world-map/location bundle 로 이어지고, 이 안에는 route/script/handler 성격의 여러 하위 테이블이 함께 들어 있을 수 있다.
- 시도:
  - `0x08BFD0`, `0x08C060`, `0x08C1D0` descriptor bundle 주변 포인터를 자동 주석 달아 어떤 ROM table 들이 반복 참조되는지 정리했다.
  - `0x184420`, `0x184820`, `0x184888`, `0x1849A0`, `0x1849D4`, `0x184A0C` 직접 포인터 ref 수를 비교했다.
  - `0x184888` 의 `10-entry` pointer table 을 따라가 각 block 이 다시 `10-slot` pointer matrix 인지 확인하고, non-null slot bytecode 를 `FF` terminator 까지 추출했다.
  - `location record field1/field2` 와 `0x184820` 좌표쌍의 앞 `10`개를 비교했다.
- 결과:
  - `0x184420..0x1844AF` 에 `18 * (u32, u32)` pair table 이 있다.
  - `0x1844B0..0x1847F7` 은 `FF` 종료 bytecode 가 밀집한 route/command region 으로 보인다.
  - `0x184888` 에는 `10-entry` route script block table 이 있고, 각 block 은 다시 `10-slot` pointer matrix 로 읽힌다.
  - 이 matrix 의 non-null slot 은 위 bytecode region 을 가리키며, 현재는 per-location route/transition command table 후보로 보는 편이 가장 안전하다.
  - `0x184820` 에는 `13 * (x, y)` node position pair table 후보가 있고, location record `field1/field2` 와는 `8 / 10` 완전 일치, 나머지 `2 / 10` 은 작은 delta 만 보였다.
  - `0x184950` 에는 `10 * (x, y)` label position pair 후보가 있다.
  - `0x1849A0` 은 `13-entry` Thumb handler pointer table, `0x1849D4` 는 `7-entry` special pair table 후보로 정리되었다.
- 판정: `성공`
- 교훈: location/world-map 계열 데이터는 문자열, 좌표, 이동 규칙, handler 가 한 묶음으로 저장될 수 있다. 이후에는 `string bank` 만 보는 접근보다 **bundle 단위 구조화**가 훨씬 효율적이다.

### 실험 37

- 가설: `0x184888` route block table 이 가리키는 `0x1844B0..0x1847F7` 시퀀스는 opcode script 가 아니라, `13`개 node 위에서 목적지까지 이동 경로를 나열한 path list 일 수 있다.
- 시도:
  - [location_bundle_tables.json](/Users/user/test/analysis/location_bundle_tables.json) 의 `route_script_block_table` 전 엔트리를 다시 읽어, 각 block 의 null slot 패턴을 비교했다.
  - 모든 시퀀스에서 `FF` 를 제외한 byte 값의 전체 집합을 모아 범위를 확인했다.
  - block 별 시퀀스를 사람이 읽기 쉬운 형태로 다시 나열해, `00 0A 01 FF`, `02 0B 01 0A 00 FF`, `09 08 07 06 0C 0B 01 FF` 같은 패턴이 실제로 "출발 node -> 중간 node -> 도착 node" 식으로 읽히는지 비교했다.
- 결과:
  - 모든 block 은 자기 자신의 slot 하나만 `null` 이었다. 즉 `block 0 -> slot 0`, `block 1 -> slot 1`, ..., `block 9 -> slot 9` 패턴이 고정이다.
  - non-null slot 은 항상 다른 `9`개 목적지에 대해 하나씩 채워져 있었다.
  - `FF` 를 제외한 route byte 값은 현재 정확히 `0..12` 만 사용한다.
  - 이 값 집합은 `0x184820` 의 `13 * (x, y)` node position table, `0x1849A0` 의 `13-entry` handler table 과 크기가 정확히 맞는다.
  - 따라서 현재 최선 해석은 `0..9 = location node`, `0x0A..0x0C = connector / transit node`, `FF = terminator` 이고, 각 slot payload 는 "출발 location 에서 목적지 location 으로 가는 node path" 다.
- 판정: `성공`
- 교훈: 겉보기에는 bytecode 처럼 보여도, 실제로는 opcode 가 아니라 그래프 경로 데이터일 수 있다. 특히 값 범위가 작고 self-slot null 패턴이 강할 때는 script 보다 path matrix 가능성을 먼저 검토해야 한다.

### 실험 38

- 가설: `0x184420` 의 `18 * (u32, u32)` table 은 route graph edge 목록이 아니라, world-map hit-test 결과를 location index 로 바꾸는 lookup table 일 수 있다.
- 시도:
  - `0x06A1F8` 를 포함하는 `0x06A09C` 계열 초기화/선택 루틴을 ARMv4T 슬라이스로 다시 읽었다.
  - `0x184420` literal xref 와 loop count 를 확인하고, table 값을 location 별로 묶어 보았다.
- 결과:
  - `0x06A1F8` 부근 루틴은 helper `0x561D4` 반환값과 `0x184420` 첫 필드를 `18`건 순회 비교한다.
  - 일치하면 둘째 필드를 current-location byte (`0x03006020`) 로 기록한다.
  - table 을 location 별로 묶으면 `0 -> [14,18,24,30,34]`, `6 -> [38,41,46,47]`, `9 -> [62,64]` 처럼 반복 location index 군집이 나타난다.
- 판정: `성공`
- 교훈: `0x184420` 은 route path matrix 와 같은 성격이 아니다. 현재는 **hotspot/cell id -> location index lookup** 으로 보는 해석이 가장 강하다.

### 실험 39

- 가설: location record 의 `field1/field2` 는 단순 node 좌표가 아니라, 실제 world-map icon / hotspot hit box 원점일 수 있고 `field0/field3/field4` 는 draw helper 파라미터일 수 있다.
- 시도:
  - `0x06A418` hit-test 루틴과 `0x069E9C`, `0x06D4A8` draw caller 를 ARMv4T 슬라이스로 다시 읽었다.
  - `0x184248` location record, `0x1840F8` companion descriptor, `0x18425C` name field stride 관계를 함께 대조했다.
- 결과:
  - `0x06A418` 은 활성 location 에 대해 `field1`, `field2` 와 descriptor `(dim_a, dim_b) * 8` 을 비교해 hit-test 사각형을 만든다.
  - 따라서 `field1/field2` 는 현재 **location icon / hotspot 좌상단 좌표** 로 보는 편이 가장 정확하다.
  - 같은 함수는 선택된 location index 를 `0x030009CC` 에 저장하고, `0x18425C + index * 0x2C` 형태로 이름 field 주소를 계산해 폭 계산 helper 를 호출한다.
  - `0x069E9C` / `0x06D4A8` 는 row 의 `field0`, `field1`, `field2`, `field4`, `field3` 를 helper `0x63000` / `0x63424` 로 직접 넘긴다.
  - 따라서 `field0/field3/field4` 는 좌표보다 **표시 파라미터** 쪽에 가깝고, 현재 최선 해석은 `field0 = asset/icon family ID`, `field3 = draw subtype/mode`, `field4 = graphic/tile-base variant` 다.
- 판정: `성공`
- 교훈: location record 는 "문자열 + 메타데이터" 정도가 아니라, 실제 world-map 선택/표시 로직에 직접 물리는 UI struct 다.

### 실험 40

- 가설: `0x1849D4` special pair table 은 단순 숫자 목록이 아니라, special location 과 event/script/message ID 를 이어 주는 매핑일 수 있다.
- 시도:
  - `0x06D430`, `0x06D5A8` 주변 code xref 를 다시 읽고 literal 값을 확인했다.
  - special pair 첫 필드와 location record index, 둘째 필드와 helper 입력값 사용 방식을 분리해서 보았다.
- 결과:
  - `0x06D5A8` 루틴은 `7`개 엔트리를 순회하며, **둘째 필드** (`0x3E1..0x3EF`) 를 helper `0x47EB0` 에 넘긴 뒤, 반환값을 **첫 필드** location index 로 색인되는 배열 슬롯에 저장한다.
  - `0x06D430` 루틴은 별도의 `0..6` selector 로 같은 table 을 인덱싱하고, **첫 필드** 를 location slot 번호처럼 사용해 플래그를 세운다.
  - 같은 흐름에서 `0x06A838` helper 는 `0x030009A0 + location_index * 4` 값을 읽어 location 활성 여부를 판정한다.
- 판정: `성공`
- 교훈: `special_pair_table` 은 현재 **location index -> special event/script/message id** 매핑으로 보는 편이 가장 강하다. 또한 location 활성/비활성은 record field 가 아니라 별도 runtime array 가 맡는다.

### 실험 41

- 가설: location record `field3` / `field4` 의 정확한 역할은 caller 쪽 값 분포만으로는 부족하고, draw helper 내부에서 어느 sprite bitfield 에 꽂히는지 봐야 더 좁힐 수 있다.
- 시도:
  - `0x069E9C`, `0x06D4A8` caller 와 `0x63000`, `0x63424` helper pair 를 ARMv4T 슬라이스로 다시 읽었다.
  - caller 가 row 의 어느 필드를 register / stack 으로 넘기는지와, helper 가 attr halfword/byte 를 어떤 방식으로 수정하는지 대조했다.
- 결과:
  - caller 는 `field4` 를 `r3`, `field3` 를 stack arg 로 넘긴다.
  - `0x63000` / `0x63424` 는 거의 같은 구조의 sprite/OAM build helper 로 보인다.
  - helper 내부에서 `r3` (`field4`) 는 sprite attr2 low 10-bit tile index 쪽에 더해진다.
  - stack arg (`field3`) 는 sprite attr2 high byte 상위 nibble 쪽에 더해진다.
  - 따라서 현재 최선 해석은 `field4 = tile-base / graphic variant offset`, `field3 = palette bank / draw subtype` 이다.
- 판정: `성공`
- 교훈: draw field 는 막연한 metadata 가 아니라, 실제 sprite template bitfield 로 바로 연결된다. 이후에는 값 분포보다 **register/bitfield 연결**을 우선 본다.

### 실험 42

- 가설: location/world-map bundle 하위 table 들은 개별 direct ref 만으로 소비되지 않고, 더 큰 정적 constant cluster 안에서 runtime global 과 함께 재조합될 수 있다.
- 시도:
  - `0x184248`, `0x18425C`, `0x184420`, `0x184820`, `0x1848B0`, `0x1849A0`, `0x1849D4`, `0x1840F8`, `0x1841E8`, `0x184A0C` 에 대해 unaligned direct-pointer scan 을 다시 수행했다.
  - `0x08BFA0..0x08C2C0` 구간 raw `u32` 값을 little-endian 으로 풀어, 정적 table pointer 와 `0x03002Fxx` / `0x03005Fxx` / `0x030060xx` / `0x030009xx` runtime global 이 어떻게 섞여 있는지 확인했다.
- 결과:
  - `0x08BFC8..0x08C2B8` 구간에는 location/world-map bundle 관련 static constant 가 조밀하게 반복 배치되어 있다.
  - `0x184248`, `0x18425C`, `0x184420`, `0x184820`, `0x1848B0`, `0x1849D4`, `0x1840F8`, `0x1841E8` 는 이 cluster 안에서 여러 번 재등장한다.
  - 반면 `0x1849A0` handler table 은 현재 `0x069E94`, `0x08BFC8` 두 건만 잡혀, direct literal 보다 상위 cluster slot 으로 소비될 가능성이 더 강해졌다.
  - `0x184A0C` 도 `0x06D070`, `0x08C1FC` direct ref 가 있어, location bundle tail 끝을 `0x184A0B` 로 단정하면 안 된다.
- 판정: `성공`
- 교훈: direct ref 수가 적다고 dead table 로 치면 안 된다. 특히 location/world-map 계열은 **static constant cluster + runtime global** 묶음으로 소비되는 경로를 같이 봐야 한다.

### 실험 43

- 가설: `0x184A0C` numeric tail 은 단순 미해석 꼬리가 아니라, 고정 크기 effect/overlay parameter table 일 수 있다.
- 시도:
  - `0x184A0C` raw word 를 `5 * u32` row 로 펼쳐 보았다.
  - `0x06D070` direct ref 주변을 Thumb 슬라이스로 다시 읽어, 실제 코드 시작점인지 literal pool 값인지 분리했다.
  - `0x047A88` helper 와 그 BL caller (`0x051E96`, `0x051FFE`, `0x06D050`) 를 비교했다.
- 결과:
  - `0x184A0C..0x184AD3` 은 `10 * 0x14` row 로 깔끔하게 끊긴다.
  - 바로 뒤 `0x184AD4` 부터는 `0x087E0000`, `0x00002B18` 로 시작하는 별도 pointer/length 계열 데이터가 이어진다.
  - `0x06D070` 은 함수 시작점이 아니라, `0x06CFB8` 계열 함수의 literal pool 안에 있는 `0x08184A0C` 값이다.
  - 해당 함수는 `0x03002FFC == 0x10` 일 때 `0x03005FF8` byte 를 index 로 사용해 `0x184A0C + index * 0x14` row 를 읽는다.
  - row 의 `5`개 word 는 `0x047A88` 로 `r0=word0`, `r1=word1`, `r2=word2`, `r3=word3`, `[sp]=word4`, `[sp+4]=0` 형태로 전달된다.
  - `0x047A88` 의 다른 caller 도 구조체 필드를 같은 helper 로 넘기므로, 이 table 은 텍스트나 포인터 배열보다 정적 effect/overlay spawn parameter table 로 보는 해석이 강하다.
- 판정: `성공`
- 교훈: literal pool 주소를 code entry 로 착각하지 말고, 참조한 instruction 까지 역으로 따라가야 한다. `0x184A0C` 는 이제 "미해석 tail" 이 아니라 별도 fixed-size parameter table 로 다룬다.

### 실험 44

- 가설: `0x03005FF8` 은 `0x184A0C` effect table 만을 위한 독립 index 가 아니라, world-map 선택/hover location index 로 먼저 정해지고 여러 경로에서 재사용될 수 있다.
- 시도:
  - `find-u32-refs` CLI 를 추가해 특정 `u32` 값의 literal hit 와 Thumb literal load 후보를 자동으로 뽑도록 했다.
  - `0x03005FF8` 값을 `0x069000..0x06DFFF` 범위에서 검색해 [effect_overlay_index_refs.json](/Users/user/test/analysis/effect_overlay_index_refs.json) 으로 저장했다.
  - 자동 분류 결과의 `write_byte` / `read_byte` 후보를 수동 disassembly 로 대조했다.
- 결과:
  - 해당 범위에서 `0x03005FF8` literal value hit 는 `10`개, Thumb literal load 는 `27`개였다.
  - 자동 접근 분류는 `write_byte` `1`개, `read_byte` `26`개로 갈렸다.
  - 확인된 direct writer 는 `0x06A52E` 하나이며, hit-test loop index `0..9` 를 `0x03005FF8` 에 `strb` 로 저장한다.
  - `0x06A93E` / `0x06A95E` 는 selected location display 계산에 이 값을 읽고, `0x06B8CA..0x06C07C` 군집은 current-location byte `0x03006020` 과 함께 route/path matrix 계산에 읽는다.
  - `0x06CEC0` 은 `0x03005FF8` selected index 를 `0x03006020` current-location byte 로 복사한 뒤 transition 좌표 계산을 시작한다.
  - `0x06CFB8` 계열은 같은 selected index 를 `0x184A0C` effect/overlay parameter row 선택에 사용한다.
  - 기존에 헷갈리기 쉬웠던 `0x06B8B0` 시작부 `strb #0` 은 `0x03005FF8` 이 아니라 `0x03005FE8` write 였고, `0x06A5B2` 의 `strb #2` 도 `0x03006018` state write 였다.
- 판정: `성공`
- 교훈: `0x03005FF8` 은 현재 **선택/hover location index byte** 로 보는 편이 가장 강하다. effect table 의 row 수 `10`은 location 수 `10`과 정렬되며, 앞으로는 이 값 자체보다 `0x184A0C` row 내부 파라미터 의미를 좁히는 것이 더 유리하다.

### 실험 45

- 가설: 세션 시작 시 읽는 문서를 `session_start.md -> agent_handoff.md -> current_constraints.md -> 활성 트랙 문서` 로 유지하면, 실제 작업 전부터 불필요한 컨텍스트를 과하게 소비한다.
- 시도:
  - 문서 크기를 `wc -c` 로 확인했다.
  - 새 hot path 문서 [active_task.md](/Users/user/test/docs/active_task.md) 를 만들고, [session_start.md](/Users/user/test/docs/session_start.md) 를 이 파일만 읽도록 바꿨다.
  - [agent_handoff.md](/Users/user/test/docs/agent_handoff.md), [current_constraints.md](/Users/user/test/analysis/current_constraints.md), [data_structure_investigation.md](/Users/user/test/docs/tracks/data_structure_investigation.md), [project_control_tower.md](/Users/user/test/docs/project_control_tower.md) 를 링크 중심 요약으로 압축했다.
  - [reference_map.md](/Users/user/test/docs/reference_map.md) 를 `Hot Path / Active Summaries / Cold Evidence` 구조로 재정리했다.
- 결과:
  - 새 기본 시작 경로는 `session_start.md` + `active_task.md` 두 파일이다.
  - 두 파일 합계는 약 `4.3KB` 로, 기존 기본 시작 경로였던 `session_start + agent_handoff + current_constraints + data_structure + text_extraction` 의 약 `49KB` 대비 훨씬 작아졌다.
  - 긴 분석 로그, 대형 JSON, 상세 트랙 문서는 시작 경로에서 제거하고 필요 시 링크/명령으로 접근하도록 바뀌었다.
- 판정: `성공`
- 교훈: 장기 프로젝트 문서는 "얼마나 많이 기록했는가"보다 "기본 경로에서 무엇을 읽지 않는가"가 더 중요하다. 증거는 보존하되, hot path 에는 현재 next step 과 금지 가정만 둔다.

### 실험 46

- 가설: `0x184A0C` effect/overlay row 의 `word0` 은 effect asset id 자체가 아니라, location/world-map 선택 체계에서 쓰는 hotspot/cell id 일 수 있다.
- 시도:
  - `0x047A88` 본체를 Thumb 슬라이스로 다시 읽어 `word0` / `word3` 사용 지점을 분리했다.
  - `0x0561F8` / `0x0561D4` helper 를 확인해 같은 runtime byte 의 setter/getter 관계를 확인했다.
  - `0x184A0C` row `word0` 값 `10`개와 `0x184420` hotspot/location lookup table 을 비교했다.
  - `word3` 이 전달되는 `0x02B96C` 도 짧게 추적해 세 번째 인자 사용 방식을 확인했다.
- 결과:
  - `0x047A88` 은 `word0` 을 `0x0561F8` 로 넘긴다.
  - `0x0561F8` 은 `*(0x03005014) + 0x90` byte 에 값을 저장하고, `0x0561D4` 는 같은 byte 를 읽어 반환한다.
  - `word0` 값 `10`개는 `0x184420` hotspot/location lookup 의 hotspot id 와 정확히 `1:1` 매칭된다.
  - 매칭된 location index 도 effect row index 와 모두 같다.
  - 따라서 `word0` 은 effect asset id 보다는 **location 대표 hotspot/cell id** 로 보는 해석이 가장 강하다.
  - `word3` 은 `0x047DEE` / `0x047E26` 에서 `0x02B96C` 의 세 번째 인자로 전달되고, `0x02B96C` 내부에서 `& 7` 로 제한된 뒤 `0x0383F8` 에 전달된다.
- 판정: `성공`
- 교훈: effect table 의 첫 word 는 새 asset namespace 가 아니라 이미 확인된 hotspot/location namespace 와 재결합될 수 있다. `word3` 은 별도 3-bit object/subresource variant 축으로 이어서 보면 된다.

### 실험 47

- 가설: `0x184A0C` effect/overlay row 의 `word3` 은 막연한 effect subtype 이 아니라, `0x03CA68` 이 돌려준 공통 descriptor 안에서 **어느 field 를 읽을지 고르는 selector** 일 수 있다.
- 시도:
  - `0x0383F8` 를 Thumb 슬라이스로 다시 읽어, `word3 & 7` 이후 실제 분기 구조를 확인했다.
  - `0x1824F0` 에 있는 8개 엔트리를 raw word 로 덤프해 데이터인지 코드 포인터인지 구분했다.
  - `0x1824F0` 가 가리키는 `0x0377E0..0x037AB8` accessor 들을 연속 block 으로 읽어 공통 패턴을 비교했다.
  - `0x184A0C` row 의 실제 `word3` 사용값도 다시 집계했다.
- 결과:
  - `0x0383F8` 은 두 번째 인자를 `& 7` 로 제한한 뒤 `0x1824F0` 의 8-entry table 을 index 한다.
  - `0x1824F0` 엔트리 값은 `0x080377E1`, `0x08037849`, `0x080378B1`, `0x08037919`, `0x08037981`, `0x080379E9`, `0x08037A51`, `0x08037AB9` 로, 모두 Thumb 함수 포인터다.
  - 이 8개 함수는 같은 descriptor 를 읽되, halfword field offset 만 `+0x04, +0x06, +0x08, +0x0A, +0x0C, +0x0E, +0x10, +0x12` 로 순차적으로 다르다.
  - 각 accessor 는 해당 halfword 의 low 10-bit 값을 반환한다.
  - 현재 `0x184A0C` row 에서 실제 쓰이는 `word3` 값은 `0` 과 `6` 뿐이며, row `2` 만 `6` 을 사용한다.
- 판정: `성공`
- 교훈: `word3` 은 frame 번호처럼 독립 의미를 가진 값보다, 공통 descriptor 안의 **필드 선택축** 으로 보는 편이 훨씬 안전하다. 다음은 이 descriptor 를 고르는 `word1 low nibble` 과 `word2` 의미를 좁히는 것이 가장 효율적이다.

### 실험 48

- 가설: `0x184A0C` row 의 `word1 low nibble` 은 단순 플래그가 아니라, `0x03CA68` 이 사용하는 descriptor family 내부 field / slot selector 일 수 있다.
- 시도:
  - `0x182530` table 을 raw word 로 덤프해 `word1 & 0x0F` 가 어떤 엔트리로 dispatch 되는지 확인했다.
  - `0x03CA68` 본체와 table 이 가리키는 `0x03CAC0`, `0x03CB3C`, `0x03CBB8`, `0x03CC34`, `0x03CCB0` 쪽을 Thumb 슬라이스로 다시 읽었다.
  - 현재 `0x184A0C` row 들의 `word1 low nibble` 분포도 다시 집계했다.
- 결과:
  - `0x182530` 은 16-entry Thumb function pointer table 이다.
  - entry `0..3` 은 각각 `0x03CAC0`, `0x03CB3C`, `0x03CBB8`, `0x03CC34` 로 이어지고, `*(0x03001450) + 0x270/0x274` descriptor family 의 halfword field `+0x02, +0x04, +0x06, +0x08` low 10-bit 를 읽는다.
  - entry `4..15` 는 모두 `0x03CCB0` fallback accessor 로 모인다.
  - fallback accessor 는 같은 descriptor 의 field `+0x00` low 8-bit 를 base 로 읽고, `0x03CA68` 복귀 후 `+ (nibble - 4)` 보정을 받아 최종 값을 만든다.
  - 따라서 `word1 low nibble` 은 registry family 자체보다, **하나의 descriptor family 안에서 어떤 field / slot 을 고를지 정하는 축** 으로 보는 해석이 가장 강하다.
  - 현재 effect/overlay row 의 실제 low nibble 값은 `0, 1, 4, 8, 14` 이다.
- 판정: `성공`
- 교훈: `word1` 은 16가지 완전 독립 타입보다, `0..3` direct field + `4..15` shared range selector 구조로 보는 편이 훨씬 자연스럽다. 다음은 `word2` 와 `word1` 상위 비트를 좁히는 것이 가장 효율적이다.
