# Experiment Log

이 문서는 조사 과정에서 시도한 가설, 결과, 실패, 교훈을 기록합니다.

목표는 "같은 실수를 다시 하지 않기"입니다.

## 작성 규칙

- 각 항목은 `가설`, `시도`, `결과`, `판정`, `교훈`을 포함합니다.
- 실패도 성공만큼 중요하게 기록합니다.
- 다시 같은 시도를 할 때는 무엇이 달라졌는지 명시합니다.
- 실험 번호는 **각 날짜 섹션 안에서만** 순차 증가합니다.
- 새 항목은 해당 날짜 섹션의 **맨 끝에만 append** 하고, 기존 항목 중간에 끼워 넣지 않습니다.

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
- 결과: `黒曜石　　　　　
火山岩の一種`, `ブラックペーパー
因縁がある黒い紙` 같은 결합 문자열 레코드가 연속 확인되었다.
- 판정: `성공`
- 교훈: 이 뱅크는 설명이 별도 포인터로 떨어진 구조가 아니라 결합 레코드 구조일 가능성이 높다.

### 실험 9

- 가설: `battle/ability` 뱅크에서 일부 레코드가 빠지는 이유는 추출 범위보다 필터 쪽 문제일 수 있다.
- 시도: 누락된 선두 레코드 `黒曜石　　　　　
火山岩の一種` 의 printable 비율을 직접 계산했다.
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

### 실험 26

- 가설: Registry A entry `8` 의 `0x10` 종단 mixed script 대사는 `01 FF <u16 문자수>` 헤더를 가진 command-stream 문자열일 수 있다.
- 시도:
  - `scan-prefixed-text` CLI 를 추가했다.
  - 최종 확인 기준으로 실제 entry `8` 범위 `0x6B594C..0x773248` 를 `prefix=01 FF`, `count-size=2`, `little-endian`, `cp932` 로 스캔했다.
  - 같은 규칙을 `0x772E00..0x773260` save/menu block 에도 적용했다.
- 결과:
  - Registry A entry `8` 에서 [registry_a_entry8_prefixed_texts.json](/Users/user/test/confirmed_data/extracted_texts/registry_a_entry8_prefixed_texts.json) `9823`건이 clean 하게 추출되었다.
  - 초반 리오르 대사 `医者になりたいんだけど、`, `教えてくれる？` 부터 후반 진행 힌트와 디버그성 플래그 문구까지 한 규칙으로 회수되었다.
  - save/menu block 도 [save_menu_prefixed_texts.json](/Users/user/test/confirmed_data/extracted_texts/save_menu_prefixed_texts.json) `12`건이 정리되었다.
- 판정: `성공`
- 교훈: 이 계열 텍스트는 `0x10` terminator 슬라이딩 스캔보다 `01 FF <문자수>` 헤더 기반 추출이 훨씬 정확하다.

### 실험 27

- 가설: `scan-prefixed-text` 초안 구현에서 `cp932` 를 incremental decoder 로 처리해도 정확히 문자 수를 셀 수 있을 것이다.
- 시도: `01 FF <u16 문자수>` 헤더 뒤 payload 를 incremental decode 하면서 문자 수만큼 읽는 방식으로 구현했다.
- 결과:
  - `教えてくれる？` 같은 분명한 샘플이 깨진 문자열로 해석되었다.
  - 원인은 lead byte 시험 과정에서 같은 바이트가 decoder state 에 중복 투입된 것이었다.
- 판정: `실패`
- 교훈: `cp932` 문자수 헤더 추출에서는 상태형 incremental decode 를 쓰지 말고, 현재 위치의 짧은 바이트 조각을 독립적으로 strict decode 하며 전진해야 한다.

### 실험 28

- 가설: `01 FF <u16 문자수>` 규칙은 Registry A entry `8` 뿐 아니라 Registry B/C/D 의 다른 mixed resource 대사 뱅크에도 재사용될 수 있다.
- 시도:
  - Registry A (`0x17C2F4..0x17C384`), B (`0x17C384..0x17C71C`), C (`0x17C71C..0x17C7E4`), D (`0x17C7E4..0x17CB04`) 각 엔트리 전체에 같은 prefixed scan 조건을 적용했다.
  - 결과는 [prefixed_registry_scan_summary.json](/Users/user/test/analysis/prefixed_registry_scan_summary.json) 에 저장했다.
- 결과:
  - 현재 히트가 강하게 나온 곳은 Registry A entry `8` 하나뿐이었다.
  - Registry B/C/D 에서는 같은 규칙으로 유의미한 일본어 텍스트 묶음이 잡히지 않았다.
- 판정: `부분 성공`
- 교훈: `01 FF <문자수>` 는 지금 단계에서는 범용 command-stream 규칙이 아니라, Registry A entry `8` 계열 전용 포맷으로 우선 취급하는 편이 안전하다.

### 실험 29

- 가설: Registry A entry `8` 의 `9823`건은 하나의 거대한 작업 단위로 두기보다 gap 기반 cluster 로 나누면 후속 번역/검수/재삽입이 쉬워질 것이다.
- 시도:
  - [registry_a_entry8_prefixed_texts.json](/Users/user/test/confirmed_data/extracted_texts/registry_a_entry8_prefixed_texts.json) 의 offset 차이를 기준으로 여러 threshold 를 시험했다.
  - `0x400` gap 을 넘을 때 새 cluster 로 분리하는 요약을 [registry_a_entry8_cluster_summary.json](/Users/user/test/analysis/registry_a_entry8_cluster_summary.json) 으로 만들었다.
- 결과:
  - threshold `0x400` 기준 `72`개 cluster 가 만들어졌다.
  - 각 cluster 는 `start/end/count/first_text/last_text` 만 가진 compact summary 라서 작업 단위 지도 역할을 하기에 적당했다.
- 판정: `성공`
- 교훈: 대형 mixed bank 는 바로 번역 세트로 던지기보다, gap-cluster 요약을 중간 레이어로 두는 편이 이후 토큰 사용과 작업 추적 모두에 유리하다.

### 실험 30

- 가설: `0x03EB78 / 0x03ECCC / 0x03EDB8` helper family 는 일본어 폰트 렌더러가 아니라 UI 숫자/ASCII glyph writer 일 수 있다.
- 시도:
  - 해당 함수들과 호출부 `0x051700`, `0x051820` 부근을 짧게 디스어셈블했다.
  - `0x03EB78` 의 문자 범위 비교와 `0x03ECCC -> 0x033658 -> 0x03EDB8` 흐름을 확인했다.
- 결과:
  - `0x03EB78` 은 `A-Z`, `a-z`, `0-9` 범위를 비교하며 `0x03003008` base 에 halfword tile index 를 쓴다.
  - `0x03ECCC` 는 값을 4-byte 버퍼로 만든 뒤 `0x03EDB8` 을 통해 같은 타일맵 base 에 숫자/기호를 배치한다.
- 판정: `성공`
- 교훈: 이 helper family 는 일반 일본어/한글 폰트 경로가 아니라 ASCII/숫자 UI helper 로 먼저 제외해야 한다. 같은 경로를 general font renderer 로 다시 의심하면 시간을 낭비한다.

### 실험 31

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

### 실험 32

- 가설: 세션 시작 때 긴 문서와 전체 로그를 매번 읽는 구조는 토큰 낭비가 크고, 실제 필요한 문서만 읽도록 라우팅을 분리하는 편이 더 효율적이다.
- 시도: 시작용 요약 문서 `session_start.md`, 현재 제약 요약 `current_constraints.md`, 작업별 참고 맵 `reference_map.md` 를 만들고, 총괄/핸드오프/반복 방지 문서를 더 짧게 압축했다.
- 결과: 매 세션의 기본 읽기 경로를 `session_start -> agent_handoff -> current_constraints -> 활성 트랙 문서` 로 줄일 수 있게 되었다.
- 판정: `성공`
- 교훈: 세션 시작 경로는 append-only 로그와 분리해서 작게 유지해야 자동화와 후속 세션의 토큰 낭비를 줄일 수 있다.

## 2026-05-09

### 실험 1

- 가설: Registry D (`0x17C7E4..0x17CB04`) 는 몇 개의 샘플 대사만 들어 있는 예외 엔트리가 아니라, 아직 추출되지 않은 튜토리얼/이벤트 대사를 넓게 담고 있을 수 있다.
- 시도:
  - `inspect-chunk-table` 로 Registry D `100`개 엔트리의 `pointer-length` 범위와 샘플 텍스트를 다시 확인했다.
  - 물리 범위 `0x7F3000..0x7F96E9` 에 대해 `scan-text --sliding --terminator 0x0D --terminator 0x0C --terminator 0x00 --min-chars 6 --require-japanese` 를 적용했다.
  - entry `0`, `25`, `34`, `92` 는 별도 범위 스캔으로도 재확인했다.
- 결과:
  - Registry D 전체 물리 범위에서 현재 `305`개의 대사성 문자열을 회수했다.
  - 텍스트가 잡힌 엔트리는 `81 / 100` 개다.
  - 튜토리얼 설명, 전투 개시/종료 대사, 이벤트 짧은 문장이 한 레지스트리 안에 넓게 분산되어 있었다.
- 판정: `성공`
- 교훈: "sample_text_entries 몇 개만 텍스트"처럼 보이는 registry 라도, mixed resource 구조에서는 전체 물리 범위를 슬라이딩 스캔해야 실제 텍스트량이 보인다.

### 실험 2

- 가설: Registry D 전체 대사를 한 번에 스캔하면 그대로 번역 workset 으로 올릴 수 있을 것이다.
- 시도:
  - `scan-text` 결과를 [registry_d_full_sliding_texts.json](/Users/user/test/analysis/registry_d_full_sliding_texts.json) 으로 저장했다.
  - `build-translation-set` 으로 [translation_workset_registry_d_dialogue.json](/Users/user/test/confirmed_data/translation_worksets/translation_workset_registry_d_dialogue.json) 을 만들었다.
  - 첫 전수 스캔 뒤 `records=100` 만 나온 이유를 확인하기 위해 parser default 를 점검했다.
- 결과:
  - `scan-text` 기본 `--limit` 이 `100` 이라서 첫 wide scan 결과가 잘려 있었다.
  - `--limit 500` 으로 재실행하자 Registry D 전체 회수본 `305`건과 대응 workset 이 정상적으로 만들어졌다.
- 판정: `성공`
- 교훈: 넓은 범위 스캔 결과를 근거 문서로 삼기 전에는 기본 limit 에 잘리지 않았는지 먼저 확인해야 한다.

### 실험 3

- 가설: `save_menu_texts` 에서 보인 `0x10` terminator command-stream 형식은 국지적인 예외가 아니라, 더 큰 대사/메뉴 bank 에 반복 사용될 수 있다.
- 시도:
  - ROM 전체를 `scan-text --sliding --terminator 0x10 --min-chars 4 --require-japanese --limit 400` 조건으로 훑었다.
  - 결과를 오프셋 클러스터로 묶어 늦은 구간의 밀집 영역을 확인했다.
  - 이후 Registry A entry `8` 범위 `0x6B594C..0x773248` 를 같은 조건으로 다시 스캔했다.
- 결과:
  - 전역 `0x10` 스캔에서 `0x6B7B44` 이후 대사성 문자열이 대량으로 나타났다.
  - Registry A entry `8` 재스캔에서는 현재 `1200`건까지 회수되었고, 이미 limit 에 걸렸다.
  - `0x772E00` save menu block 도 이 entry 안쪽에 포함되어 있었다.
- 판정: `성공`
- 교훈: `0x10` 종단 텍스트는 save menu 예외가 아니라, 상위 mixed script bank 안에 넓게 퍼진 형식이다. 전역 스캔만 믿지 말고, registry entry 범위로 다시 좁혀 재추출해야 한다.

### 실험 4

- 가설: 최근 따라간 `0x0514xx` UI cluster 가 실제 폰트/문자 매핑 렌더러에 바로 닿을 수 있다.
- 시도:
  - `0x0514D0..0x051980`, `0x058720`, `0x075DD4` 를 디스어셈블해 호출 관계를 확인했다.
  - Registry B raw companion 엔트리 `86`, `87`, `88` 은 헤더 뒤를 바로 4bpp 로 덤프해 시각적으로 확인했다.
- 결과:
  - `0x075DD4` 는 `strlen` 계열이고, `0x0514xx` 클러스터는 문자열 길이로 UI slot/layout 을 조정하는 경향이 강했다.
  - `0x058720` 은 문자열 렌더러가 아니라 tracked slot record 좌표를 넘기는 position helper 쪽이었다.
  - raw companion 엔트리 `86..88` 4bpp 덤프는 글자판이 아니라 잡음에 가까웠다.
- 판정: `부분 성공`
- 교훈: UI layout 경로와 실제 문자 렌더러를 섞어 보면 폰트 추적이 빗나간다. raw companion asset 도 헤더/압축/별도 포맷 가능성을 먼저 배제해야 한다.

### 실험 5

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

### 실험 6

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

### 실험 7

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

### 실험 8

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

### 실험 9

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

### 실험 10

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

### 실험 11

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

### 실험 12

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

### 실험 13

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

### 실험 14

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

### 실험 15

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

### 실험 16

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

### 실험 17

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

### 실험 18

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

### 실험 19

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

### 실험 20

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

### 실험 21

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

### 실험 22

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

### 실험 23

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

### 실험 24

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

### 실험 25

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

### 실험 26

- 가설: `0x184A0C` row 의 `word1` / `word2` 는 descriptor selector 와 별개로, 실제 object positioning 에 쓰이는 raw coordinate pair 일 수 있다.
- 시도:
  - `0x047A88` 전체 슬라이스를 다시 읽어 `word1` / `word2` stack slot 사용 횟수를 확인했다.
  - detached slice 의 BL target 은 `slice_start + local_target` 으로 다시 환산해 실제 helper `0x0587BC`, `0x058870` 를 찾았다.
  - `0x0587BC` / `0x058870` 를 직접 읽어 `word1` / `word2` 가 어떤 object field 로 들어가는지 확인했다.
- 결과:
  - `0x047A88` 안에서 `word1` / `word2` 는 각각 한 번만 읽히고, sign-extended 16-bit pair 로 `0x0587BC` 에 함께 전달된다.
  - `0x0587BC` 는 두 축에 같은 scalar transform helper `0x075560` 을 각각 적용한다.
  - 변환 결과는 current active object/entry 의 `+0x08` / `+0x0C` 에 저장된다.
  - 이어지는 `0x058870` 은 이 `+0x08` / `+0x0C` 값을 다른 active entry 로 복사하는 흐름을 가진다.
  - `word4` 는 `0x047A88` 에서 `[r7 + 0x1C]` 로 한 번만 읽히고, `0` 여부에 따라 optional branch 를 건너뛴다.
  - 따라서 현재 가장 안전한 해석은 `word1` / `word2` 가 **raw positional pair (x/y 계열)** 라는 것이다.
  - 따라서 `word4` 는 현재 **boolean / mode flag** 로 보는 편이 가장 안전하다.
  - 다만 `0x075560` 의 exact scaling rule 과 `word4` 가 켜는 side-path 의 정확한 의미는 이번 단계에서 확정하지 않았다.
- 판정: `성공`
- 교훈: `word1 low nibble` selector 분석과 `word1` 전체 좌표 역할은 동시에 참일 수 있다. 같은 word 가 selector bit 와 raw position encoding 을 함께 담는 packed field 일 가능성을 열어 두고 진행한다.

### 실험 27

- 가설: `0x0587BC` 가 부르는 `0x075560` 은 좌표값을 어떤 bespoke fixed-point 로 바꾸는 것이 아니라, signed int 를 직접 float 비트패턴으로 포장하는 helper 일 수 있다.
- 시도:
  - `0x075560` 내부 BL target 을 실제 ROM 주소로 환산해 `0x074D44`, `0x074DFC` helper 를 직접 읽었다.
  - `0x074D44` / `0x074DFC` 의 bitfield 처리 방식을 확인해 IEEE-754 single pack/unpack 형태와 맞는지 비교했다.
  - 대표 정수값 `0`, `1`, `400`, `427`, `475`, `-1`, `-400` 의 표준 float bit pattern 도 함께 계산해 기준을 잡았다.
- 결과:
  - `0x074DFC` 는 32-bit 값을 sign / exponent / mantissa 성분으로 풀어 임시 구조체에 저장하는 unpacker 로 보인다.
  - `0x074D44` 는 반대로 임시 구조체의 sign / exponent / mantissa 를 조합해 32-bit 값을 만드는 packer 로 보인다.
  - `0x075560` 첫 helper 는 signed int 를 정규화한 뒤 위 packer 로 넘기는 흐름을 가진다.
  - 따라서 `0x0587BC` 가 `word1` / `word2` 에 적용하는 변환은 bespoke scale 변환보다 **signed integer -> IEEE-754 single float 포장** 으로 보는 해석이 가장 강하다.
  - 이 기준이면 `word1 = 0x190`, `word2 = 0x1AB` 같은 값은 각각 `400.0f`, `427.0f` 좌표로 저장되는 흐름과 잘 맞는다.
- 판정: `성공`
- 교훈: detached slice 분석에서는 내부 BL target 재환산이 매우 중요하다. 좌표계 해석을 할 때는 “어떤 수치 형식으로 저장되는가”와 “원본 데이터가 packed metadata 를 함께 담는가”를 분리해서 봐야 한다.

### 실험 28

- 가설: `0x03CA68` dispatch table 분석을 effect row `word1 low nibble` 에 직접 연결한 것은 caller 경로를 충분히 확인하지 않은 오해일 수 있다. 대신 `word4 != 0` side-path 가 실제 overlay slot maintenance 를 수행할 가능성이 높다.
- 시도:
  - `0x047A88` slice 의 실제 `0x02B96C` call site (`0x047DEE`, `0x047E26`) 직전 레지스터 세팅을 다시 읽었다.
  - nonzero side-path 내부 BL target 을 실제 ROM 주소로 환산해 `0x044320`, `0x03CFC0`, `0x03D090`, `0x075D4C` 를 직접 읽었다.
  - side-path literal pool 에서 global 오프셋 `0x033C`, `0x033E`, `0x0574`, `0x0AF4`, `0x0BF4` 도 다시 추출했다.
- 결과:
  - `0x047DEE`, `0x047E26` 에서 `0x02B96C` 직전 `r2` 는 `word3`, `r1` 은 `0` 으로 세팅된다.
  - 따라서 이전의 "`word1 low nibble` 이 effect row 경로에서 `0x03CA68` dispatch 를 고른다"는 해석은 현재 철회하는 편이 안전하다.
  - `word4 != 0` side-path 는 global `0x03001450 + 0x33C/+0x33E` 의 두 tracked slot 을 읽고, slot `8..23` 범위의 세 병렬 block (`+0x0574`, `+0x0AF4`, `+0x0BF4`) 을 순회한다.
  - helper `0x075D4C` 는 사실상 memset 계열이므로, 이 side-path 는 tracked slot 두 개를 제외한 block 들을 0으로 지우는 흐름으로 읽힌다.
  - `0x044320` 은 `+0x0574` block 의 플래그 비트를 clear/set 하는 helper 로 보인다.
  - 따라서 `word4` 는 현재 **overlay slot maintenance mode flag** 로 보는 해석이 가장 강하다.
- 판정: `성공`
- 교훈: helper-family 차원의 구조 해석과 특정 caller 경로의 실제 인자 전달은 반드시 분리해서 적어야 한다. caller 직전 레지스터를 보지 않으면 같은 실수를 반복하게 된다.

### 실험 29

- 가설: `word4 != 0` side-path 가 읽는 `0x03001450 + 0x33C/+0x33E` 는 막연한 상태값이 아니라, 실제 slot `8..23` clearing 루프와 짝을 이루는 tracked raw slot id 필드일 수 있다.
- 시도:
  - `0x047CFC..0x047D84` 루프를 다시 읽어 `+0x33C/+0x33E` 값이 어떤 비교식에 들어가는지 확인했다.
  - `0x044320`, `0x0443B4`, `0x03D6F0` 를 이어서 읽어 same slot record 에 대한 flag set/check/sync 흐름인지 비교했다.
  - helper caller 목록도 다시 확인해 이 조합이 `0x047A88` 전용인지, 다른 overlay builder 들과 공유되는지 점검했다.
- 결과:
  - `0x047CFC..0x047D2C` 에서는 `+0x33C` 와 `+0x33E` halfword 를 읽은 뒤 각각 `+8` 보정해서 현재 loop slot `8..23` 과 직접 비교한다.
  - 따라서 `+0x33C/+0x33E` 는 적어도 **raw tracked slot id 2개** 로 보는 해석이 가장 강하다.
  - `0x044320(slot, flag)` 는 `+0x0574 + (slot + 8) * 0x34` record 의 상위 플래그를 clear/set 하고, `0x0443B4(slot)` 는 같은 플래그가 살아 있는지 검사하는 helper 로 보인다.
  - `0x03D6F0` 는 `+0x33E` 와 `+0x33C` 를 함께 읽어 `0x0443B4` / `0x044320` 를 호출하는 정합성 보조 루틴처럼 보인다.
  - 다만 `0x03D6F0` 안의 `+0x33E == 1` 비교는 아직 sentinel 인지 real slot special-case 인지 확정하지 않았다.
  - `0x03D768` caller 목록은 `0x047DCC`, `0x048EE8`, `0x04F688`, `0x04FCA8`, `0x04FF2C`, `0x050BA4` 로, 이 slot maintenance 흐름이 world-map 한 군데가 아니라 여러 overlay builder family 에서 재사용되는 helper 군일 가능성을 높인다.
- 판정: `성공`
- 교훈: slot clearing 루프는 단순 memset 범위를 보는 것만으로는 부족하다. loop index 와 tracked field 를 같은 좌표계로 환산하는 비교식 (`raw slot + 8`) 까지 확인해야 “상태값”과 “slot id” 를 구분할 수 있다.

### 실험 30

- 가설: `0x03D6F0` 첫 분기에서 보였던 `+0x33E == 1` 비교는 register ALU opcode 를 잘못 읽은 착시일 수 있다. 올바르게 읽으면 second tracked slot 의 sentinel 의미가 드러날 가능성이 있다.
- 시도:
  - ad-hoc Thumb slice 출력을 CLI `dump-thumb` 로 정리해 `0x047CFC..0x047D84`, `0x03D6F0..0x03D75A` 를 다시 읽었다.
  - `0x42C8`, `0x4288`, `0x5EC8`, `0x5E88` 같은 자주 나오는 ALU / `ldrsh` 패턴을 명시적으로 decode 해서 비교식을 다시 확인했다.
- 결과:
  - `0x047CFC..0x047D2C` 에서는 `+0x33C` / `+0x33E` halfword 를 읽어 `+8` 보정 뒤 slot `8..23` 와 비교하는 흐름이 더 명확해졌다.
  - `0x03D704` 의 `0x42C8` 은 `cmp r0, r1` 이 아니라 `cmn r0, r1` 이다.
  - 따라서 `0x03D6F0` 첫 분기는 `+0x33E == 1` special-case 가 아니라, sign-extended halfword 기준 **`+0x33E == -1` sentinel** 검사로 읽는 편이 자연스럽다.
  - 이 해석이면 `+0x33E` 는 "두 번째 tracked slot 없음" 상태를 가질 수 있는 optional slot field 후보로 좁혀진다.
  - `dump-thumb` CLI 가 추가되어, 같은 종류의 world-map / overlay / font 인접 Thumb slice 확인을 반복 스크립트 없이 재사용할 수 있게 되었다.
- 판정: `성공`
- 교훈: Thumb ALU register opcode (`0x4000` 계열) 를 `.hword` 로 흘리면 sentinel 해석이 완전히 뒤집힐 수 있다. `cmp` 와 `cmn` 구분은 특히 tracked state / sentinel 분석에서 반드시 직접 확인해야 한다.

### 실험 31

- 가설: `0x33C/+0x33E` tracked field 는 passive state 가 아니라, 별도 allocator 가 피해야 하는 reserved slot set 으로 쓰일 수 있다. 이 경우 allocator 출력 버퍼와 consumer 를 함께 보면 구조가 더 명확해질 것이다.
- 시도:
  - `0x0443F8` 본체와 후반부를 더 길게 읽어 `0x0300503C`, `0x03005240`, `0x03005284` 역할을 정리했다.
  - `0x0443F8` direct caller 를 다시 찾고, 유일한 caller `0x059034` 를 따라가 반환값 사용 방식을 확인했다.
  - `0x03005284` consumer (`0x047A28`, `0x045B98` 계열) 도 짧게 읽어 선택 결과 버퍼인지 점검했다.
- 결과:
  - `0x0443F8` 는 `0x0300503C` 를 slot iterator 로 써서 후보 slot `0..15` 를 훑는다.
  - 루프는 현재 tracked slot `0x33C/+0x33E` 와 겹치는 후보를 건너뛰고, `+0x574` active flag, `+0x57C` / `+0xBA4` / `+0xBA6` 위치/경계 값, `0x03005240` 의 `16 * 4-byte` per-slot state table 을 함께 사용한다.
  - 선택된 후보는 `0x03005284` 에 `slot id` 또는 `-1` sentinel 로 남는다.
  - `0x0443F8` direct caller 는 현재 `0x059034` 하나이며, caller 는 성공 시 반환 slot id 를 `slot + 0x5A` runtime id 로 변환해 후속 object 구축에 사용한다.
  - `0x045B98` / `0x047A28` 은 `0x03005284` 를 읽는 consumer 로 보이므로, `0x03005284` 는 selected candidate slot buffer 로 보는 해석이 강하다.
  - `0x044B7C` 시작부는 `0x33E` 를 읽어 `0x714` table 기반 후속 object 흐름으로 들어가므로, `+0x33E` 는 optional second tracked slot consumer 경로도 가진다.
- 판정: `성공`
- 교훈: tracked field 를 이해하려면 read/clear helper만 보면 부족하다. allocator (`iterate -> exclude tracked -> emit candidate`) 와 consumer (`candidate buffer`) 를 함께 봐야 실제 lifecycle 이 보인다.

### 실험 32

- 가설: `0x03005240` 은 막연한 scratch 가 아니라 allocator 전용 `16 * 4-byte` per-slot state table 이며, `0x03005284` candidate 는 별도 pending pair 로 한 단계 더 승격될 수 있다.
- 시도:
  - `0x0412D0..0x04137A` init slice 와 `0x0446E2..0x04473C`, `0x044AE0..0x044B74` 를 다시 읽어 `0x03005240` field 쓰임을 비교했다.
  - `0x045D6C/0x045D94`, `0x045EEE/0x045F16`, `0x04679E` 를 읽어 `0x03005284`, `0x482`, `0x484` 의 staging 흐름을 정리했다.
  - `0x0478B8` 과 `0x04B7F0` 를 함께 읽어 `0x484` 의 derived companion 의미와 pending pair consumer 여부를 점검했다.
- 결과:
  - `0x0412D0..0x04137A` 는 `0x03005284 = -1` 을 기록하고, `0x03005240[16]` 각 entry 의 `+0` / `+2` halfword 를 모두 지운다.
  - `0x0446E2..0x04473C` 는 새 candidate 를 잡을 때 `0x03005240[candidate].+0 |= 1` 을 세우고, `0x044AE0` 의 반환값을 `+2` 에 저장한다.
  - `0x044AE0` 는 global bounds 비교로 `1/2/4/8` bit 를 조합한 edge/boundary mask 를 만들므로, 현재 가장 안전한 `0x03005240` entry 해석은 `u16 in_use_flag`, `u16 edge_mask` 다.
  - `0x045D6C/0x045D94` 와 `0x045EEE/0x045F16` 은 `0x03005284` 를 읽어 `0x482 = raw slot`, `0x484 = 0x0478B8(slot)` pair 로 staging 한 뒤 `0x0458DC` 를 호출한다.
  - `0x0478B8(slot)` 은 slot record `0x714[slot]` 와 bundle `0x0CD4[slot]` 의 좌표/방향 정보를 섞어 companion id 를 만들고, 필요하면 `0x02C1AC(slot, derived_dir)` fallback 으로 보정한다.
  - `0x04B7F0` 는 `0x482/0x484` pending pair 와 기존 `0x33E` tracked slot 을 함께 읽는 consumer 로 보이므로, `0x03005284 -> 0x482/0x484` 는 tracked-slot machinery 앞단의 pending promotion buffer 로 보는 해석이 가장 강해졌다.
- 판정: `성공`
- 교훈: allocator 결과를 곧바로 tracked field 에 연결하려고 하면 중간 staging pair 를 놓치기 쉽다. candidate buffer, derived companion, tracked field 를 서로 다른 단계로 나눠 보는 편이 안정적이다.

### 실험 33

- 가설: `0x33E` 는 읽기 전용 상태가 아니라 상위 state 전환 함수에서 sentinel 로 직접 초기화될 수 있다.
- 시도:
  - `0x04F000..0x051200` 범위의 `0x033E` literal ref 를 다시 좁혀 보고, 실제 store 가 있는지 확인했다.
  - `0x050FF8..0x05103C` 를 직접 읽어 `0x033E` 주변 명령이 read 인지 write 인지 분리했다.
- 결과:
  - `0x051022..0x051034` 는 base `0x03005014` 에 `0x033E` 를 더한 주소를 만든 뒤, 기존 halfword 에 `0xFFFF` 를 OR 해서 `strh` 한다.
  - sign-extended consumer 기준으로 이 값은 `-1` sentinel 이므로, 이 코드는 특정 state flag 조건에서 **`0x33E = -1` direct clear writer** 로 읽는 편이 자연스럽다.
  - 따라서 `+0x33E` 는 purely derived field 가 아니라, 상위 state 흐름에서 explicit reset 을 받는 tracked slot field 로 더 좁혀졌다.
- 판정: `성공`
- 교훈: writer 탐색이 막힐 때는 consumer helper 주변만 돌지 말고, 상태 전환 루틴이 몰린 상위 range 를 좁혀 보는 편이 효율적이다.

### 실험 34

- 가설: `0x33C` 가 literal scan 에 거의 안 잡히는 이유는 "미사용" 이 아니라, `0xCF << 2` 같은 계산식 접근 때문일 수 있다.
- 시도:
  - `0x04F000..0x051200` 전체 window 를 다시 덤프하고, `21CF/20CF/22CF/23CF/24CF` 패턴을 grep 해서 `0xCF << 2` 접근 후보만 따로 모았다.
  - 그중 `0x050F3E..0x050F56` 과 `0x04F4BA..0x04F524` 를 다시 읽어 `0x33C` consumer 와 slot maintenance 루프 연관성을 점검했다.
- 결과:
  - `0x050F3E..0x050F56` 는 base `0x03005014` 에 `0xCF << 2` 를 더해 얻은 halfword 를 읽고, 다른 slot id 와 함께 `0x044320` 으로 넘긴다.
  - `0x04F4BA..0x04F524` 도 같은 `0xCF << 2` 접근 뒤 `+8` 보정 비교를 사용해 slot clearing 루프에서 제외 대상을 고른다.
  - 따라서 `0x33C` 계열은 literal `0x0000033C` hit 가 없어도 실제로는 활성 consumer 경로에 들어 있으며, 이 field 는 `0x033E` 와 마찬가지로 tracked raw slot 축으로 보는 해석이 더 강해졌다.
- 판정: `성공`
- 교훈: `find-u32-refs` 는 매우 유용하지만, 구조 필드가 작은 곱셈/shift 조합으로 만들어지는 경우에는 별도 immediate-pattern 검색이 필요하다.

### 실험 35

- 가설: 일반 일본어 텍스트 렌더러는 `0x03EB78` ASCII/숫자 helper family 와 별개로 존재하며, world-map 지역명 표시 경로를 따라가면 공통 text object engine 을 잡을 수 있을 것이다.
- 시도:
  - world-map location 선택 경로 `0x06A95A..0x06A972` 를 다시 읽어 지역명 필드가 어떤 helper 로 넘어가는지 확인했다.
  - `0x014A98`, `0x014ED0`, `0x015A4C..0x015A80` 를 직접 덤프해 object field 접근과 문자열 바이트 분기 여부를 비교했다.
  - `find-thumb-bl` 로 `0x014A98`, `0x014ED0` caller 를 전역 확인해 특정 화면 전용인지 shared family 인지 점검했다.
- 결과:
  - `0x06A95A..0x06A972` 는 `0x18425C + selected_location * 0x2C` 문자열 필드를 `0x03005FA0` object 와 함께 `0x014A98` 에 넘긴 뒤, 바로 `0x014ED0` 을 호출한다.
  - `0x014A98` 는 object field `+0x10`, `+0x14`, `+0x20..+0x24` 주변을 세팅하는 setup helper 로 보이며, 직접적인 문자 디코더로 읽히지 않는다.
  - `0x014ED0` 는 object `+0x0C` 문자열 포인터에서 현재 바이트를 읽고, `0x81..0x9F` / `0xE0..0xEF` 를 Shift-JIS multibyte lead byte 후보로, `0x20..0x7E` 를 ASCII / halfwidth 로 분기한다.
  - `0x015A4C..0x015A80` 는 `0x03001540 + index * 0x2C` text object `11`개를 순회하며 `0x014ED0` 을 호출한다.
  - 따라서 현재 가장 유력한 general Japanese text renderer 후보는 `0x03EB78` family 가 아니라 **`0x014A98 / 0x014ED0 / 0x015A4C` family** 다.
- 판정: `성공`
- 교훈: 폰트 조사에서는 "문자열 길이를 재는 UI helper" 와 "실제 바이트 인코딩을 분기하는 text engine" 을 분리해야 한다. 인코딩 범위를 직접 비교하는 루프를 먼저 잡아야 glyph table 과 width lookup 으로 안정적으로 내려갈 수 있다.

### 실험 36

- 가설: `0x014ED0` 아래에는 문자코드를 glyph source pointer 로 바꾸는 공통 lookup 이 있을 것이고, 이를 잡으면 한글 폰트 치환의 핵심 object field 를 식별할 수 있을 것이다.
- 시도:
  - `0x015220..0x015640` 을 직접 읽어 `0x014ED0` 내부에서 현재 문자코드가 어디에 쓰이는지 추적했다.
  - 이어서 `0x015608`, `0x01570C`, `0x01578C`, `0x01580C`, `0x01588C`, `0x01590C`, `0x015984` 를 덤프해 glyph copy writer 구조를 비교했다.
- 결과:
  - `0x0152A2..0x0152C4` 에서 현재 문자코드 `u16` 는 `obj + 0x04` 기반 `u16` lookup table 로 조회된다.
  - 조회값은 `obj + 0x1A` (`ldrh [obj + 26]`) 와 곱해지고, `obj + 0x08` base pointer 에 더해져 glyph source pointer 가 된다.
  - 현재 가장 안전한 해석은 `obj + 0x04 = char_code -> glyph index/offset table`, `obj + 0x08 = glyph data base`, `obj + 0x1A = glyph stride` 다.
  - `0x01570C / 0x01578C / 0x01580C / 0x01588C` 는 이 glyph source 를 tile target 으로 풀어쓰는 writer family 이고, 실제 low-level halfword writer 는 `0x01590C` / `0x015984` 두 종류로 갈린다.
  - `0x015608` 은 `obj + 0x1F` 와 `obj + 0x10` 을 사용해 `obj + 0x14` destination pointer 를 다시 계산하므로, text object 가 tile page 단위 cursor/state 를 별도로 가진다는 점도 확인됐다.
- 판정: `성공`
- 교훈: font/encoding 조사에서는 "문자열을 어떻게 읽는가" 다음에 "문자코드를 어떤 object field 조합으로 glyph source 로 바꾸는가"를 잡아야 실제 치환 설계가 가능해진다. lookup table, glyph base, stride, destination cursor 를 분리해서 기록하는 편이 재탐색을 줄인다.

### 실험 37

- 가설: `0x01499C` 는 단순 object clear 가 아니라, 실제 font resource header 를 해석해 lookup table / glyph base / stride 를 object 에 세팅하는 initializer 일 것이다. 주요 화면이 같은 인자로 이 함수를 부르면 공통 font resource 사용 여부도 확인할 수 있다.
- 시도:
  - `0x01499C..0x014BAE` 와 이어지는 `0x014AE0..0x014BAE` 를 직접 읽어 object field write 패턴을 정리했다.
  - `0x015A32`, `0x0618AE`, `0x064B66`, `0x069D7C` caller 를 비교해 `0x0002CC` 인자와 후속 초기화 흐름을 맞춰 봤다.
  - 보조 근거로 `0x08088318` 주변 ROM 문자열도 확인했다.
- 결과:
  - `0x01499C` 는 `obj + 0x00 = resource_ptr`, `obj + 0x04 = lookup base`, `obj + 0x08 = glyph base`, `obj + 0x1A = resource[8] stride` 를 채우는 initializer 로 읽힌다.
  - `resource[7] & 0x80` 이 켜져 있으면 lookup base 는 `resource + 0x10 + 0x40000` 이 되고, glyph base 는 그 뒤 `+0x20000` 위치가 된다.
  - `obj + 0x16` 에는 `resource[7] & 0x1F` 가 저장되고, initializer 인자 `r2` 는 `obj + 0x1C`, `obj + 0x1D` 에 복제된다.
  - `0x08088318` 문자열은 `"FONT INITIALIZE ERROR"` 로 확인되어 함수 역할과 잘 맞는다.
  - 주요 caller `0x015A28`, `0x0618A4`, `0x064B5C`, `0x069D72` 는 모두 `0x0002CC(0, 1)` 뒤 `0x01499C` 를 호출한다.
  - 따라서 현재까지 확인된 general text object 화면은 **공통 font resource pair `(0, 1)`** 를 공유하는 해석이 가장 강하다.
- 판정: `성공`
- 교훈: font path 조사에서는 text loop 자체만 보면 부족하다. object 생성 시점에서 어떤 resource header 가 lookup table 과 glyph base 를 심는지 먼저 고정해 두면, 이후 한글 글리프 치환은 “런타임 구조 추측”이 아니라 “공통 asset 교체” 문제로 좁혀진다.

### 실험 38

- 가설: `0x0002CC(0, 1)` 는 막연한 allocator 가 아니라, 이미 정리해 둔 hub `0x076530` / registry 계열을 따라 resource pointer 를 꺼내는 공통 loader 일 것이다. 이게 맞으면 text font resource 의 상위 위치도 더 직접적으로 설명할 수 있다.
- 시도:
  - `0x000290..0x00033C` 를 직접 읽어 인자 사용 방식과 record stride 를 정리했다.
  - `0x00033C` 가 `0x0002CC`, `0x000304` 를 어떻게 쓰는지 같이 확인해 pointer / length 역할을 분리했다.
  - 이를 앞서 확인한 `0x01499C` caller 의 `0x0002CC(0, 1)` 패턴과 연결했다.
- 결과:
  - `0x000290(registry_slot)` 은 hub `0x08076530` table 에서 선택한 registry base pointer 를 돌려준다.
  - `0x0002CC(entry_index, registry_slot)` 은 해당 registry base 에서 `entry_index * 0x0A` record 를 계산하고, record `+0x00` 의 payload pointer 를 돌려준다.
  - `0x000304(entry_index, registry_slot)` 은 같은 record `+0x04` 의 length 를 돌려준다.
  - `0x00033C(dest, entry_index, registry_slot)` 은 DMA3 를 기다린 뒤 위 pointer / length 를 사용해 payload 를 `dest` 로 복사한다.
  - 따라서 현재 가장 안전한 상위 record 해석은 `record size = 0x0A`, `+0x00 = pointer`, `+0x04 = length` 다.
  - 이 구조를 적용하면 `0x01499C` 가 쓰는 공통 font resource 는 **registry slot `1` entry `0`** 으로 읽는 편이 가장 자연스럽다.
- 판정: `성공`
- 교훈: lower-level text engine 분석과 상위 registry loader 분석을 분리해 두면 각각 애매할 수 있다. 하지만 둘을 연결하면 “공통 font asset이 어떤 entry인가”까지 바로 내려가므로, 다음 단계인 raw tile / lookup 배치 확인이 훨씬 짧아진다.

### 실험 39

- 가설: `slot 1 / entry 0` 공통 font resource 는 실제로 `fnt` 형식 payload 일 것이고, header 와 glyph stride 를 보면 glyph 포맷까지 어느 정도 역산할 수 있을 것이다.
- 시도:
  - `0x17C2F4` table entry `0` pointer/length 를 실제 ROM offset 로 환산했다.
  - payload 시작 `0x3E0000` 과 lookup/glyph 후보 구간을 raw hex 로 확인했다.
  - 샘플 문자 몇 개를 `cp932` 코드로 바꿔 `obj + 0x04` lookup table 값도 직접 읽었다.
- 결과:
  - entry `0` 은 `ptr=0x083E0000`, `len=0x3DDE8` 이므로 실제 payload 범위는 `0x3E0000..0x41DDE7` 이다.
  - payload 시작부에는 `66 6E 74 00` 즉 `fnt\\0` magic 이 보이고, 앞 12바이트는 `66 6E 74 00 0C 0F 00 0A 48 00 DE 77` 형태다.
  - `resource[8] = 0x48` 은 `0x01499C` 가 object stride 로 복사하는 값과 정확히 일치한다.
  - writer loop 는 source 를 한 번에 `+6` byte, 총 `8 + 4 = 12` 행 소비하므로 현재 가장 강한 해석은 **glyph 1개 = `12 rows * 6 bytes = 0x48` bytes = 12x12 4bpp 계열 포맷** 이다.
  - 샘플 lookup 값도 실제 일본어 문자에서 유효하게 나온다. 예를 들어 `0x82A0 ('あ') -> 0x0067`, `0x8341 ('ア') -> 0x00B7`, `0x835A ('セ') -> 0x00D0`, `0x838A ('リ') -> 0x00FF`, `0x93FA ('日') -> 0x051C` 다.
  - 따라서 이 payload 는 더 이상 막연한 “텍스트 관련 blob”이 아니라, **공통 일본어 폰트 resource** 로 취급해도 될 만큼 좁혀졌다.
- 판정: `성공`
- 교훈: 공통 font payload 의 magic/header/lookup sample 을 함께 확인하면, 이후 한글화 작업은 “맞을지도 모르는 후보”를 파는 단계에서 벗어나 실제 교체 대상 asset 을 다루는 단계로 넘어갈 수 있다.

### 실험 40

- 가설: `0x3E0000` 공통 `fnt` payload 의 glyph 가 정말 12x12 계열이라면, 샘플 문자 몇 개를 직접 덤프했을 때 적어도 대략적인 획 형태가 보여야 한다.
- 시도:
  - `dump-fnt-glyph` CLI 를 `gba_kor_tool` 에 추가해 `fnt` header, lookup table, glyph base, stride 를 자동 해석하도록 했다.
  - 공통 payload `0x3E0000` 에서 `--code 0x82A0 ('あ')`, `0x8341 ('ア')`, `0x93FA ('日')` 를 실제로 덤프했다.
  - PGM 뷰어 제약 때문에 결과는 ASCII preview 로 다시 확인했다.
- 결과:
  - `fnt_glyph_82A0_ah.pgm`, `fnt_glyph_8341_a_katakana.pgm`, `fnt_glyph_93FA_day.pgm` 이 생성되었고, 모두 `12x12`, `stride=0x48`, 올바른 glyph index / glyph offset 으로 출력되었다.
  - ASCII preview 기준으로 `'日'` 은 사각 프레임형 획이 분명했고, `'ア'` 도 상단 가로획과 대각/수직 계열 패턴이 드러났다.
  - `'あ'` 는 작은 해상도라 획이 더 뭉개지지만, 적어도 무작위 노이즈가 아니라 문자형 패턴을 유지한다.
  - 따라서 `lookup -> glyph index -> glyph_base + index * 0x48 -> 12x12 계열 glyph` 흐름은 샘플 글자 형태까지 확인된 상태가 되었다.
- 판정: `성공`
- 교훈: 글자 자산 분석은 숫자와 포인터만으로 끝내지 않는 편이 좋다. 샘플 glyph 를 바로 덤프해 보면 잘못된 stride/row packing 가설을 빨리 걸러낼 수 있고, 한글 폰트 삽입 대상이 진짜 맞는지도 빠르게 확인할 수 있다.

### 실험 41

- 가설: 공통 `fnt` payload 는 샘플 glyph 몇 개만 덤프 가능한 수준이 아니라, 전체 lookup mapping 자체를 JSON 추출본으로 뽑을 수 있을 것이다. 이게 되면 폰트 쪽도 "검증"이 아니라 실제 추출 단계로 올릴 수 있다.
- 시도:
  - `inspect-fnt` CLI 를 추가해 payload header, lookup base, glyph base, stride 를 읽고 전체 `0x10000` 코드 공간을 스캔하도록 했다.
  - 공통 payload `0x3E0000` 에 대해 manifest 를 [common_fnt_manifest.json](/Users/user/test/analysis/common_fnt_manifest.json) 으로 출력했다.
- 결과:
  - 공통 `fnt` payload 전체 mapping에서 nonzero entry `1698`개가 실제로 추출되었다.
  - decoded entry 기준으로 `ASCII 11`, `non-ASCII 1687`, `undecodable 0` 이다.
  - 최대 glyph index 는 `0x06A2`, glyph coverage end 는 `0x41DDE8` 로 계산되었다.
  - preview 상으로도 `0x0030 ('0') -> 0x0001`, `0x8141 ('、') -> 0x000C`, `0x8341 ('ア') -> 0x00B7` 같은 mapping 이 바로 확인된다.
  - 따라서 폰트 쪽도 이제는 "공통 font mapping 전체를 실제 추출본으로 확보한 단계" 라고 말할 수 있다.
- 판정: `성공`
- 교훈: 한글화 준비에서 "텍스트는 추출됐지만 폰트는 아직 감" 같은 애매한 상태를 오래 끌지 않는 편이 좋다. 공통 font asset 에 대해 전체 manifest 를 한 번 뽑아 두면, 이후 작업은 구조 추정이 아니라 glyph 배치/대체 전략 문제로 빠르게 전환된다.

### 실험 42

- 가설: 공통 text engine 은 단순 고정폭이 아니라 fullwidth / halfwidth 를 다르게 누적하는 레이아웃 구조를 이미 가지고 있을 것이다. 이게 맞으면 한글 폭 설계는 새 엔진 추가보다 기존 advance 규칙에 맞추는 쪽으로 갈 수 있다.
- 시도:
  - `0x014ED0..0x01525E`, `0x015220..0x015278` 을 다시 읽어 `obj + 0x18`, `obj + 0x20` 관련 연산을 정리했다.
  - 대표 caller `0x06A972` 와 `0x062182`, `0x065AA4`, `0x06718A` 의 `r3` 인자를 비교했다.
- 결과:
  - multibyte Shift-JIS 경로는 `obj + 0x18 += 0x18`, single-byte / halfwidth 경로는 `obj + 0x18 += 0x10` 이다.
  - `(obj + 0x18) >> 4` 값이 `obj + 0x20` 과 비교되고, 넘치면 `0x015608` 으로 page/cursor 전환이 일어난다.
  - `0x014A98` 는 setup 인자 `r3` 를 `floor(3 * r3 / 2)` 로 변환해 `obj + 0x20` 에 넣는다.
  - world-map 지역명 `r3=0x0C` 는 capacity `18`, 대표 일반 화면군 `r3=20` 은 capacity `30` 으로 변환되므로, 해석상 각각 `fullwidth 12자 / halfwidth 18자`, `fullwidth 20자 / halfwidth 30자` 한도와 맞는다.
  - 따라서 이 텍스트 엔진은 **fullwidth / halfwidth 혼합 가변폭형 레이아웃** 으로 보는 해석이 가장 강하다.
- 판정: `성공`
- 교훈: 한글화에서 폭 처리가 걱정된다고 해서 곧바로 새 width table 부터 만들 필요는 없다. 먼저 기존 엔진이 어떤 단위로 advance 를 누적하는지 잡아 두면, 한글 glyph 를 fullwidth 그룹으로 맞출지 halfwidth 계열로 변형할지 훨씬 명확해진다.

### 실험 43

- 가설: Registry D 에서 plain terminator sliding scan 으로만 보이던 대사 상당수는, 실제로 `FC` 제어 바이트가 섞인 mixed-format 스크립트 안에 있고 `FC 00` anchor 뒤를 기준으로 더 깔끔하게 추출될 것이다.
- 시도:
  - `registry_d_entries_scan.json` 과 실제 엔트리 raw bytes 를 다시 대조해 `text_hits == 0` 인 큰 엔트리들의 시작 패턴을 확인했다.
  - 그 결과 다수 엔트리에서 `FC 00` 뒤에 `cp932` 본문이 오고, 다음 `FC` 이전에 `0D 0C`, `0A 0B` 같은 줄/페이지 제어가 섞인다는 점을 잡았다.
  - 이를 바탕으로 `scan-fc-script-text` CLI 를 추가하고, Registry D 전체 물리 범위 `0x7F3000..0x7F96E9` 에 직접 적용했다.
- 결과:
  - Registry D `100`개 엔트리 중 `82`개는 `FC 00` anchor 를 포함했고, 실제 clean extraction 은 `81 / 100` 엔트리에서 성립했다.
  - [registry_d_fc_script_texts.json](/Users/user/test/confirmed_data/extracted_texts/registry_d_fc_script_texts.json) 에 현재 `240`건이 정리됐고, 줄바꿈/페이지 제어 바이트는 사람이 읽기 쉬운 줄바꿈으로 정규화됐다.
  - top entry 분포는 `0=20`, `92=17`, `33=15`, `47=10`, `24=7`, `32=7`, `54=7` 이다.
  - 따라서 기존 [registry_d_full_sliding_texts.json](/Users/user/test/analysis/registry_d_full_sliding_texts.json) `305`건은 discovery coverage 용, `FC` anchor 추출본 `240`건은 실제 작업용 원본이라는 역할 분리가 가능해졌다.
- 판정: `성공`
- 교훈: mixed-format 대사 뱅크에서는 plain terminator scan 만 반복하지 말고, 먼저 엔트리 시작 패턴과 제어 바이트 빈도를 확인해 전용 extractor 후보를 세우는 편이 훨씬 빠르다. 특히 Registry D 는 이제 "추가 구조 분석이 필요한 미해결 구간"이 아니라, **전용 추출 규칙이 확보된 active extraction 구간** 으로 취급해야 한다.

### 실험 44

- 가설: `scan-fc-script-text` 의 stop byte `FC` 처리는 Shift-JIS 2바이트 문자의 trailing byte 와 충돌할 수 있고, 이 경우 일부 Registry D 엔트리 대사가 잘려서 누락될 것이다.
- 시도:
  - `FC` 추출 non-hit 엔트리 중 길이가 남아 있는 entry `8` 과 `70` 을 raw bytes 로 다시 확인했다.
  - entry `8` 에서 `... 8B 43 8D 87 93 FC 82 EA ...` 처럼 `0xFC` 가 실제 문자 바이트로 등장하는 케이스를 확인했다.
  - 이를 반영해 `scan-fc-script-text` stop 탐색을 SJIS-aware 로 바꿔, 바로 앞 바이트가 lead byte 면 stop 으로 취급하지 않게 수정한 뒤 Registry D 전체를 재추출했다.
- 결과:
  - [registry_d_fc_script_texts.json](/Users/user/test/confirmed_data/extracted_texts/registry_d_fc_script_texts.json) 은 `240 -> 244` 건으로 늘었고, [registry_d_fc_script_summary.json](/Users/user/test/analysis/registry_d_fc_script_summary.json) 기준 hit 엔트리도 `81 -> 82` 로 증가했다.
  - entry `8` 에서 `こいつで最後か！\n気合入れて\nとっとと片付けるッ`, `よろしくお願いします`, `全力で向かってきなさい` 등 `4`건이 추가 회수됐다.
  - 반면 entry `70` 은 `FC` 바이트가 지나치게 조밀한 control-only script table 형태로 남아, plausible cp932 대사가 없다는 점이 더 강해졌다.
  - 남은 non-hit `18`개는 [registry_d_unresolved_entries.json](/Users/user/test/analysis/registry_d_unresolved_entries.json) 으로 분리했고, 대부분 `2-byte sentinel/control stub` 이다.
- 판정: `성공`
- 교훈: command/script extractor 에서 제어 바이트 하나를 stop marker 로 쓰더라도, Shift-JIS 같은 multibyte 인코딩에서는 그 바이트가 텍스트 본문에 trailing byte 로 나타날 수 있다. 따라서 mixed-format 추출기에는 **stop 조건에도 인코딩 awareness** 를 넣어야 같은 누락을 반복하지 않는다.

### 실험 45

- 가설: "텍스트 100% 추출" 여부는 총개수 카운터보다 상위 registry/source inventory 로 판단해야 하며, Registry A tail 에도 아직 별도 text source 가 남아 있을 수 있다.
- 시도:
  - Registry A 전체 `18`개 엔트리를 다시 경계 기준으로 확인했다.
  - tail 영역 `entry 9..17` 에 대해 plain text hit 를 재스캔했고, 특히 `entry 12 (0x7A750C..0x7A8E98)` 를 별도로 추출했다.
  - 추출본을 기존 [item_texts.json](/Users/user/test/confirmed_data/extracted_texts/item_texts.json) 및 [translation_workset_gameplay_terms.json](/Users/user/test/confirmed_data/translation_worksets/translation_workset_gameplay_terms.json) 과 대조했다.
- 결과:
  - entry `12` 에서 [registry_a_entry12_texts.json](/Users/user/test/confirmed_data/extracted_texts/registry_a_entry12_texts.json) `20`건이 실제로 잡혔다.
  - 내용은 회복약 설명, 이벤트 해결 증표, 파츠, 전달 서류 같은 gameplay/item 계열이다.
  - `20`건 중 `14`건은 기존 `item_texts` / gameplay workset 과 중복이고, `6`건은 아직 gameplay workset 에 없는 텍스트였다.
  - 따라서 Registry A tail 도 전부 dead/binary 로 단정하면 안 되며, 추출 완료 판정은 **"현재까지 뽑은 파일 수"가 아니라 상위 source inventory 를 모두 점검했는가**로 판단해야 한다는 점이 더 분명해졌다.
- 판정: `성공`
- 교훈: 텍스트 커버리지를 말할 때는 "총 문자열 수"를 찾으려 하기보다, 렌더러와 loader 가 공급받는 bank / registry entry 목록을 먼저 닫아야 한다. 새로운 entry-level text source 가 발견되면, 그 즉시 coverage 문서와 inventory 기준을 같이 갱신해야 한다.

### 실험 46

- 가설: Registry A tail entry `12` 는 plain extract 만으로는 일부 문자열을 놓칠 수 있고, tail 전체 `9..17` 도 text source / binary / false-positive 후보로 한 번 더 분류해야 coverage 판단이 흔들리지 않는다.
- 시도:
  - tail 전체 `0x773248..0x7C0CDC` 범위에 대해 `prefixed`, `fc-script`, `sliding`, `plain extract` 를 교차 적용했다.
  - entry `12` 는 sliding scan 결과를 기준으로 다시 정규화해 [registry_a_entry12_texts.json](/Users/user/test/confirmed_data/extracted_texts/registry_a_entry12_texts.json) 을 갱신했다.
  - tail `9..17` 전체는 [registry_a_tail_classification.json](/Users/user/test/analysis/registry_a_tail_classification.json) 으로 분류했다.
  - 이어서 [translation_workset_gameplay_terms.json](/Users/user/test/confirmed_data/translation_worksets/translation_workset_gameplay_terms.json) 에 entry `12` 신규 텍스트를 합쳤다.
- 결과:
  - `prefixed` / `fc-script` 규칙은 tail `9..17` 에서 추가 hit `0` 이었다.
  - entry `12` 는 `20 -> 22` 건으로 보정됐고, 누락되던 `幻の機械鎧の素材　１／５`, `幻の機械鎧の素材　３／５` 도 회수됐다.
  - entry `15` 에서 보이던 `8-byte` 3건은 대형 binary 구간 안의 short cp932 false-positive 후보로 분류했고, tail 나머지 `9..11`, `13..14`, `16..17` 은 현재 기준 no confirmed text source 로 정리했다.
  - gameplay terms workset 는 entry `12` 신규 `6`건이 반영되도록 갱신됐다.
- 판정: `성공`
- 교훈: coverage audit 에서는 "새 규칙이 더 먹히는가"와 "이미 잡힌 bank 의 추출본이 완전한가"를 같이 봐야 한다. 특히 작은 bank 는 plain extract 결과를 그대로 확정하지 말고, sliding 결과와 대조해 누락 여부를 한 번 더 확인하는 편이 안전하다.

### 실험 47

- 가설: Registry A entry `8` 은 이미 `9823`건이 추출됐어도 너무 커서 실제 작업 단위로 쓰기 어렵다. 각 cluster 에 자동 태그와 샘플을 붙이면 "미추출 문제"와 "정리 부족 문제"를 분리하는 데 큰 도움이 될 것이다.
- 시도:
  - `summarize-text-clusters` CLI 를 `gba_kor_tool` 에 추가했다.
  - 입력 JSON의 `offset/text` 레코드를 gap threshold 기준으로 cluster 화하고, `sample_texts`, `tags`, `primary_tag` 를 자동으로 붙이게 했다.
  - 이 도구를 entry `8` 추출본에 적용해 [registry_a_entry8_cluster_catalog.json](/Users/user/test/analysis/registry_a_entry8_cluster_catalog.json) 과 [registry_a_entry8_cluster_catalog.md](/Users/user/test/analysis/registry_a_entry8_cluster_catalog.md) 를 생성했다.
  - 사람이 빨리 훑는 용도로 [registry_a_entry8_cluster_overview.md](/Users/user/test/analysis/registry_a_entry8_cluster_overview.md), 태그 분포용 [registry_a_entry8_cluster_tag_summary.json](/Users/user/test/analysis/registry_a_entry8_cluster_tag_summary.json) 도 만들었다.
- 결과:
  - entry `8` 은 `72`개 cluster 로 재구성됐고, 이제 각 cluster 에 대해 `range`, `record_count`, `primary_tag`, `tags`, `sample_texts` 를 바로 볼 수 있다.
  - 자동 분포 기준으로 primary tag 는 `military 18`, `central 15`, `east_city 10`, `liore 5`, `bank 5`, `cat_quest 4` 등으로 나뉘었다.
  - cluster `71` 은 `save_menu` 태그가 붙지만, 실제로는 save/menu 전용이 아니라 후기 진행 prompt 와 일반 이벤트 대사가 함께 섞인 mixed hub 라는 점도 드러났다.
  - 따라서 entry `8` 은 이제 "큰 bank 하나"가 아니라, **장면/용도 후보를 가진 작업 지도** 로 다룰 수 있게 되었다.
- 판정: `성공`
- 교훈: 대형 mixed bank 는 "추출 성공"만으로는 충분하지 않다. 실제 한글화 준비에서는 cluster catalog 같은 중간 레이어가 있어야, 텍스트가 덜 뽑힌 건지 아니면 이미 뽑았는데 정리만 안 된 건지 빠르게 구분할 수 있다.

### 실험 48

- 가설: Registry A entry `8` 의 cluster `71` 은 자동 태그상 `save_menu` 로 보이지만, 실제로는 save/menu source 와 일반 이벤트 대사가 한데 섞인 mixed hub 일 것이다. 또 Registry D entry `70` 은 끝까지 대사 후보가 아니라 control-only script table 일 가능성이 높다.
- 시도:
  - [registry_a_entry8_cluster_catalog.json](/Users/user/test/analysis/registry_a_entry8_cluster_catalog.json) 의 cluster `71` 범위를 기준으로, save/menu block 시작점 `0x772E00` 전후를 나눠 추출본을 재분리했다.
  - 분리본을 [save_menu_prefixed_texts.json](/Users/user/test/confirmed_data/extracted_texts/save_menu_prefixed_texts.json) 과 직접 대조했다.
  - Registry D entry `70` 은 raw bytes 전체를 다시 덤프해 `FC` 밀집도와 명령 반복 패턴을 확인했다.
- 결과:
  - cluster `71` 은 일반 이벤트/진행 힌트 `228`건과 save/menu `12`건으로 분리됐고, save/menu 쪽은 [registry_a_entry8_cluster71_save_segment_texts.json](/Users/user/test/analysis/registry_a_entry8_cluster71_save_segment_texts.json) 이 [save_menu_prefixed_texts.json](/Users/user/test/confirmed_data/extracted_texts/save_menu_prefixed_texts.json) 과 정확히 일치했다.
  - 따라서 cluster `71` 의 `save_menu` 태그는 “이 cluster 안에 save block 이 들어 있다”는 뜻이지, cluster 전체가 save menu 전용이라는 뜻은 아니라는 점이 정리됐다.
  - Registry D entry `70` 은 `FC 04 00 FC 03 4B ...` 같은 짧은 제어 명령이 과도하게 반복되고, plausible cp932 대사가 전혀 잡히지 않아 control-only script table 해석이 더 강해졌다.
- 판정: `성공`
- 교훈: 자동 태그는 작업 진입점으로는 유용하지만, 실제 source 경계와 1:1 대응한다고 가정하면 안 된다. 또 "마지막 미해결 텍스트 후보"처럼 보이는 엔트리도 raw command density 를 직접 보면 빠르게 control-only 로 닫을 수 있다.

### 실험 49

- 가설: 공통 `fnt` payload 는 lookup code 공간보다 glyph 저장 공간이 먼저 한계에 닿았을 가능성이 크다. 이게 맞으면 한글화의 병목은 새 code point 설계가 아니라 glyph 확장/재배치가 된다.
- 시도:
  - `audit-fnt-usage` CLI 를 `gba_kor_tool` 에 추가했다.
  - 공통 payload `0x3E0000`, 길이 `0x3DDE8` 에 대해 현재 확보한 주요 추출본 전체를 입력으로 usage audit 을 돌렸다.
  - 동시에 decoder 가 실제로 받는 Shift-JIS lead byte 공간 (`0x81..0x9F`, `0xE0..0xEF`) 안의 free code block 도 따로 집계했다.
  - ROM 전체 `0xFF` 자유 공간도 길이별로 다시 훑어 payload 확장이 기존 빈칸만으로 가능한지 점검했다.
- 결과:
  - [common_fnt_usage_audit.json](/Users/user/test/analysis/common_fnt_usage_audit.json) 기준 mapped code 는 `1698`, 현재 추출 텍스트 `105707`자 중 실제 사용 mapped code 는 `1411`, 현재 미사용 mapped code 는 `287`, rare used (`<=2회`) mapped code 는 `394`였다.
  - 하지만 glyph index 는 `1..1698` 이 **빈칸 없이 연속** 이고, payload 길이 `0x3DDE8` 기준 tail free bytes 도 `0` 이었다.
  - 반면 decoder 허용 공간 안의 free code 는 `7337`개였고, `0x8440..0x84FF`, `0x8540..0x85FF`, `0xE940..0xE9FF` 같은 큰 빈 block 들도 확인됐다.
  - ROM 안의 기존 `0xFF` 자유 공간은 최대 `0xF84` 바이트 수준이라, in-place 여유 공간만으로는 full-game 한글 glyph inventory 를 넣기 어렵다는 점도 확인됐다.
- 판정: `성공`
- 교훈: 공통 font 를 볼 때 "빈 code point 가 있는가"와 "glyph 를 저장할 물리 공간이 있는가"를 분리해서 봐야 한다. 이 게임은 전자가 아니라 후자가 먼저 막히므로, 다음 단계는 code table 추가보다 **payload 확장/재배치 전략** 쪽으로 가야 한다.

### 실험 50

- 가설: 공통 font payload 는 registry entry pointer/length 를 더 큰 위치로 옮기는 방식으로 확장 가능할 것이다. 다만 실제로는 상위 registry table 외에 mirror table 도 함께 갱신해야 할 수 있다.
- 시도:
  - `relocate-chunk` CLI 를 `gba_kor_tool` 에 추가했다.
  - 먼저 `0x17C2F4` entry `0` 만 `0x800000`, `len=0x42000` 으로 옮기는 테스트 ROM 을 만들었다.
  - 이어서 원본 `0x083E0000` literal hit 를 전역 검색해 추가 direct 참조를 점검했다.
  - 그 결과 `0x1823A0` 가 `0x17C2F4` 와 동일한 pointer-length 엔트리 배열이라는 점을 확인했고, mirror table 갱신 옵션을 도구에 추가했다.
  - 최종적으로 `0x17C2F4` entry `0` + `0x1823A0` entry `0` 을 함께 `0x08800000`, `len=0x42000` 으로 갱신한 테스트 ROM 을 다시 생성했다.
- 결과:
  - [font_chunk_relocation_test.json](/Users/user/test/analysis/font_chunk_relocation_test.json) 기준으로 공통 font payload 는 새 위치 `0x800000` 에 정상 복사됐고, 새 pointer/length 가 기록되었다.
  - `inspect-fnt /private/tmp/hnr_font_expand_test_mirror.gba 0x800000` 결과도 정상이라, 새 위치 payload 자체는 올바른 `fnt` 로 읽힌다.
  - 원본 `0x083E0000` word hit 는 `3`개였고, 의미 있는 갱신 대상은 최소 `0x17C2F4`, `0x1823A0` 두 곳으로 좁혀졌다.
  - `0x1823A0` 는 단일 descriptor 가 아니라 `0x17C2F4` 와 같은 pointer-length 엔트리 배열의 mirror 로 확인되었다.
- 판정: `성공`
- 교훈: resource relocation 은 pointer 하나만 바꾸는 작업으로 보면 안 된다. 이 게임처럼 registry mirror/accessor table 이 별도로 존재할 수 있으므로, 실제 payload 재배치 전에는 **literal hit -> mirror 구조 -> 동시 갱신 대상** 을 먼저 닫아야 한다.

### 실험 51

- 가설: 텍스트 추출 쪽은 "아직도 계속 구조 분석을 더 해야 하는 상태"와 "실질적으로 닫히고 폰트/재삽입이 우선인 상태"를 구분해서 문서에 명시해야 한다. 이 구분이 없으면 작업 우선순위가 다시 흔들릴 수 있다.
- 시도:
  - [text_extraction_coverage.md](/Users/user/test/analysis/text_extraction_coverage.md), [text_extraction_progress.md](/Users/user/test/docs/tracks/text_extraction_progress.md), [active_task.md](/Users/user/test/docs/active_task.md) 를 다시 읽고 현재 완료 조건 `1~4` 를 재판정했다.
  - 그 결과를 기준으로 docs/analysis 안내 문서와 legacy handoff 문서도 함께 정리했다.
- 결과:
  - Registry A tail (`9..17`) 분류는 현재 실무 기준으로 닫힌 상태로 정리됐다.
  - Registry D entry `70` 판정도 현재 실무 기준으로 닫힌 상태로 정리됐다.
  - 남은 핵심 텍스트 추출 과제는 Registry A entry `8` cluster 장면/용도 라벨링과 실제 플레이 검증으로 좁혀졌다.
  - 따라서 특별한 새 text source 징후가 없는 한, 현재 우선순위는 폰트/재삽입 쪽이라는 점을 문서에 명시했다.
- 판정: `성공`
- 교훈: coverage 문서는 단순 현황표가 아니라 **작업 우선순위 전환 기준** 이어야 한다. 닫힌 항목과 아직 열린 항목을 분리해 적지 않으면, 끝난 구조 분석을 다시 반복하기 쉽다.

### 실험 52

- 가설: 공통 `fnt` payload 재배치가 끝난 뒤에는, 실제로 새 glyph slot 과 새 code lookup 도 append 할 수 있어야 한글 glyph 삽입 실험으로 넘어갈 수 있다.
- 시도:
  - `append-fnt-glyph` CLI 를 `gba_kor_tool` 에 추가했다.
  - 입력 source 는 실제 한글 bitmap 대신 기존 glyph 복제로 먼저 검증하기 위해 `0x93FA ('日')` 를 사용했다.
  - 재배치 테스트 ROM `/private/tmp/hnr_font_expand_test_mirror.gba` 에서 free code `0xE940` 로 새 glyph append 를 실행했다.
  - 이후 `inspect-fnt` 와 raw lookup/glyph byte 비교로 결과를 다시 검증했다.
- 결과:
  - [font_append_test.json](/Users/user/test/analysis/font_append_test.json) 기준으로 새 glyph index `0x06A3`, 새 glyph offset `0x83DDE8` 이 기록되었다.
  - `0xE940 -> 0x06A3` lookup 매핑이 실제 ROM에 반영되었다.
  - 새 glyph bytes 는 source glyph `0x93FA ('日')` 와 완전히 동일했다.
  - `inspect-fnt` 기준 nonzero mapping 도 `1698 -> 1699` 로 증가했다.
- 판정: `성공`
- 교훈: 재배치만으로는 충분하지 않고, **새 code + 새 glyph slot append** 가 실제로 되는지까지 확인해야 진짜 삽입 경로가 닫힌다. 이제 남은 핵심은 glyph append 인프라가 아니라, 실제 한글 bitmap 을 어떤 세트와 순서로 넣을지다.

### 실험 53

- 가설: 공통 `fnt` 확장본에 실제 한글 glyph bitmap 을 붙인 뒤, 공통 renderer 경로를 쓰는 짧은 문자열 하나를 custom `.tbl` 로 치환하면 첫 실제 한글 문자열 테스트 ROM 까지 닫을 수 있다.
- 시도:
  - `append-fnt-glyph-set` CLI 를 추가해 [hangul_test_manifest.json](/Users/user/test/analysis/hangul_test_manifest.json) 기준 `가/나/다` `PGM 12x12` glyph 를 free code `0xE940..0xE942` 에 append 했다.
  - 테스트용 테이블 [hangul_test.tbl](/Users/user/test/analysis/hangul_test.tbl) 을 만들고 `E940=가`, `E941=나`, `E942=다` 로 매핑했다.
  - 공통 renderer 경로가 이미 잡힌 world-map 지역명 `ソリン` (`0x1842E0`) 을 `/private/tmp/hnr_font_hangul_test.gba` 에서 `가나다` 로 제자리 치환해 `/private/tmp/hnr_font_hangul_string_test.gba` 를 만들었다.
  - raw bytes 와 `search-text --table analysis/hangul_test.tbl` 로 결과를 다시 확인했다.
- 결과:
  - [font_append_hangul_test.json](/Users/user/test/analysis/font_append_hangul_test.json) 기준 새 glyph index `0x06A3..0x06A5` 와 새 code `0xE940..0xE942` 가 기록되었다.
  - [font_hangul_string_test.json](/Users/user/test/analysis/font_hangul_string_test.json) 기준 문자열 위치 `0x1842E0` 에 raw bytes `E940 E941 E942 00` 이 기록되었다.
  - `search-text /private/tmp/hnr_font_hangul_string_test.gba 가나다 --table analysis/hangul_test.tbl` 는 `0x1842E0` hit `1` 을 반환했다.
- 판정: `성공`
- 교훈: 이제 "font 를 옮길 수 있다", "glyph 를 붙일 수 있다" 수준을 넘어서, **공통 font 확장 + 실제 한글 glyph + 실제 문자열 1건 치환** 까지 한 번은 닫혔다. 다음 단계는 같은 길이 치환을 넘어서, 더 긴 한글 문자열의 inject / repoint 와 실제 화면 렌더링 확인이다.

### 실험 54

- 가설: placeholder 품질의 테스트 glyph 를 그대로 정식 제작에 쓰면 품질 문제가 반복된다. 레퍼런스 glyph 를 편집용 `PGM` 세트로 내보내고 외부 픽셀 에디터에서 수정한 뒤 다시 가져오는 workflow 가 필요하다.
- 시도:
  - `prepare-fnt-glyph-set` CLI 를 `gba_kor_tool` 에 추가했다.
  - seed manifest [hangul_reference_seed_manifest.json](/Users/user/test/analysis/hangul_reference_seed_manifest.json) 을 만들고, 기존 일본어 glyph `0x8341`, `0x838A`, `0x93FA` 를 각각 `가/나/다` 작업용 seed 로 연결했다.
  - 원본 ROM `0x3E0000` 공통 `fnt` payload 기준으로 편집용 작업 폴더 [hangul_reference_workbench](/Users/user/test/analysis/hangul_reference_workbench) 와 [hangul_reference_workbench_report.json](/Users/user/test/analysis/hangul_reference_workbench_report.json) 을 생성했다.
- 결과:
  - 편집용 `PGM` 파일 `hangul_ga.pgm`, `hangul_na.pgm`, `hangul_da.pgm` 과 [prepared_manifest.json](/Users/user/test/analysis/hangul_reference_workbench/prepared_manifest.json), [prepared.tbl](/Users/user/test/analysis/hangul_reference_workbench/prepared.tbl) 이 생성되었다.
  - 따라서 이제는 AI가 대충 만든 block glyph 대신, **외부 픽셀 에디터에서 사람이 다듬은 glyph 자산** 을 다시 `append-fnt-glyph-set` 으로 가져오는 경로가 준비되었다.
- 판정: `성공`
- 교훈: 한글 glyph 품질 문제는 렌더러 분석으로 해결되지 않는다. 검증용 placeholder 와 정식 자산 제작 workflow 를 분리하고, 정식 단계에서는 반드시 레퍼런스 기반 외부 편집 산출물을 단일 truth source 로 삼아야 한다.

### 실험 55

- 가설: 정식 한글 workbench 는 손으로 글자 목록을 관리하면 곧 어긋난다. 번역 JSON 초안에서 실제 필요한 한글 글자를 자동 추출해 seed manifest 로 만들면, glyph 제작 범위를 현재 번역 상태와 동기화할 수 있다.
- 시도:
  - `build-hangul-seed-manifest` CLI 를 `gba_kor_tool` 에 추가했다.
  - [translation_workset_core_ui.json](/Users/user/test/confirmed_data/translation_worksets/translation_workset_core_ui.json) 의 `translation` 필드에서 한글 음절을 추출해 [hangul_core_ui_seed_manifest.json](/Users/user/test/analysis/hangul_core_ui_seed_manifest.json), [hangul_core_ui.tbl](/Users/user/test/analysis/hangul_core_ui.tbl), [hangul_core_ui_seed_report.json](/Users/user/test/analysis/hangul_core_ui_seed_report.json) 을 생성했다.
  - 이어서 이 manifest 를 `prepare-fnt-glyph-set` 에 넣어 [hangul_core_ui_workbench](/Users/user/test/analysis/hangul_core_ui_workbench) 편집용 세트를 만들었다.
- 결과:
  - 현재 core UI 번역 초안 기준 필요한 한글 음절은 `80`개로 집계되었다.
  - top 빈도 예시는 `이 7`, `까 4`, `다 4`, `스 4`, `저 4` 였다.
  - [hangul_core_ui_workbench](/Users/user/test/analysis/hangul_core_ui_workbench) 에 `80`개 `PGM` glyph 와 [prepared_manifest.json](/Users/user/test/analysis/hangul_core_ui_workbench/prepared_manifest.json), [prepared.tbl](/Users/user/test/analysis/hangul_core_ui_workbench/prepared.tbl) 이 생성되었다.
- 판정: `성공`
- 교훈: 앞으로 한글 glyph 제작 범위는 감으로 정하지 말고, **현재 번역 초안에서 자동 추출한 character inventory** 를 기준으로 workbench 를 키워야 한다. 이렇게 하면 번역과 폰트 작업이 같은 글자 집합을 보게 된다.

### 실험 56

- 가설: 전체 `80`글자 workbench 는 첫 아트 패스로는 크고, 단순 상위 빈도 `24`글자는 또 너무 작다. 상위 빈도 subset 을 여러 크기로 잘라 문자열 커버를 비교하면, 첫 production batch 크기를 더 현실적으로 정할 수 있다.
- 시도:
  - `slice-hangul-seed-manifest` CLI 를 `gba_kor_tool` 에 추가했다.
  - [hangul_core_ui_seed_report.json](/Users/user/test/analysis/hangul_core_ui_seed_report.json) 기준으로 `priority24`, `priority48` manifest / table / workbench 를 만들었다.
  - [translation_workset_core_ui.json](/Users/user/test/confirmed_data/translation_worksets/translation_workset_core_ui.json) 의 현재 번역 초안을 기준으로, 각 subset 이 완성 문자열을 몇 건까지 전부 커버하는지 [hangul_core_ui_priority_coverage.json](/Users/user/test/analysis/hangul_core_ui_priority_coverage.json) 으로 집계했다.
- 결과:
  - `priority24`: 완성 문자열 커버 `0`
  - `priority48`: 완성 문자열 커버 `5`
  - `full80`: 완성 문자열 커버 `19`
  - `priority48` 에서 바로 테스트 가능한 대표 문자열은 `통신 중...`, `저장 중이다…`, `리오르`, `이스트 시티`, `레돈도` 였다.
  - 따라서 첫 production batch 는 `priority24` 보다 [hangul_core_ui_priority48_workbench](/Users/user/test/analysis/hangul_core_ui_priority48_workbench) 쪽이 더 실용적이라는 결론을 얻었다.
- 판정: `성공`
- 교훈: "자주 나오는 글자"만으로 첫 배치를 정하면 실제 화면 문장이 하나도 안 닫힐 수 있다. 첫 glyph 배치는 **빈도 + 완성 문자열 커버** 를 함께 보고 정해야 한다.

### 실험 57

- 가설: 한글 custom code 와 기존 일본어/ASCII/기호가 섞인 문자열을 실제로 넣으려면, `.tbl` 에 없는 문자는 기존 `cp932` 로 fallback 인코딩되어야 한다. 이 조건이 맞으면 priority/full batch test ROM 을 바로 만들 수 있다.
- 시도:
  - `encode_text` 를 수정해, table 매칭에 실패한 문자는 지정한 `encoding` 으로 fallback 인코딩되도록 바꿨다.
  - [core_ui_priority48_coverable_translations.json](/Users/user/test/analysis/core_ui_priority48_coverable_translations.json) `5`건, [core_ui_full80_coverable_translations.json](/Users/user/test/analysis/core_ui_full80_coverable_translations.json) `19`건을 만들었다.
  - 각각의 glyph set 을 `/private/tmp/hnr_font_core_ui_priority48_font.gba`, `/private/tmp/hnr_font_core_ui_full80_font.gba` 에 append 한 뒤 `apply-translations` 를 실행했다.
- 결과:
  - `priority48` 기본 번역은 [core_ui_priority48_apply_report.json](/Users/user/test/analysis/core_ui_priority48_apply_report.json) 기준 `4 in_place, 1 skipped_no_pointer`
  - `full80` 기본 번역은 [core_ui_full80_apply_report.json](/Users/user/test/analysis/core_ui_full80_apply_report.json) 기준 `15 in_place, 4 skipped_no_pointer`
  - skip 된 `4`건은 모두 번역이 원문보다 약간 길어 direct pointer 탐색이 필요해진 케이스였다.
- 판정: `성공`
- 교훈: 실제 한글화 테스트에서는 table-only 인코딩으로는 부족하다. **custom Hangul mapping + 기존 cp932 fallback** 이 있어야 mixed UI 문자열을 바로 돌려볼 수 있다.

### 실험 58

- 가설: 아직 포인터 구조를 못 찾은 save/menu / 일부 지명 문자열도, 우선 compact test 번역으로 줄이면 전부 in-place 패치가 가능할 수 있다.
- 시도:
  - `저장 중이다… -> 저장 중...`
  - `지금까지의 여정을 저장할까? -> 여정을 저장할까?`
  - `이대로 여행을 계속할까? -> 여행을 계속할까?`
  - `크루스 유적 -> 크루스유적`
  - 위 compact 대체를 반영한 [core_ui_priority48_compact_test_translations.json](/Users/user/test/analysis/core_ui_priority48_compact_test_translations.json), [core_ui_full80_compact_test_translations.json](/Users/user/test/analysis/core_ui_full80_compact_test_translations.json) 을 만들고 다시 `apply-translations` 를 실행했다.
- 결과:
  - [core_ui_priority48_compact_apply_report.json](/Users/user/test/analysis/core_ui_priority48_compact_apply_report.json): `5 in_place`
  - [core_ui_full80_compact_apply_report.json](/Users/user/test/analysis/core_ui_full80_compact_apply_report.json): `19 in_place`
  - 결과 ROM 은 `/private/tmp/hnr_core_ui_priority48_compact_text_test.gba`, `/private/tmp/hnr_core_ui_full80_compact_text_test.gba`
  - `search-text` 검증으로 `저장 중...`, `크루스유적`, `이스트 시티` 등 실제 문자열 hit 도 다시 확인했다.
- 판정: `성공`
- 교훈: 포인터 구조가 아직 안 닫힌 구간도, **compact test 번역본** 을 병행하면 시각 QA 와 렌더러 확인을 먼저 진행할 수 있다. 구조 조사와 화면 QA 를 완전히 직렬로 둘 필요는 없다.

### 실험 59

- 가설: 최근 본 이상한 `가` 스크린샷은 현재 `priority48/full80` production test 자산이 아니라, 예전 legacy placeholder glyph (`hangul_test_ga.pgm`) 에서 나온 결과일 가능성이 크다. 이 차이를 문서와 재생성 스크립트로 분리해 두면 혼동을 줄일 수 있다.
- 시도:
  - `hangul_test_ga.pgm` 내용을 다시 확인했고, 스크린샷 모양과 같은 계열의 단순 block placeholder 임을 재확인했다.
  - 반대로 현재 `hangul_core_ui_workbench` 의 seed glyph 는 blank template 라는 점도 확인했다.
  - 최신 compact/basic test ROM 을 원본 ROM에서 다시 만드는 [build_core_ui_test_roms.sh](/Users/user/test/scripts/build_core_ui_test_roms.sh) 를 추가하고, `/private/tmp/hnr_rebuild_check` 에서 끝까지 재생성해 검증했다.
- 결과:
  - 재생성 스크립트는 `font_expand_base`, `priority48/full80 font`, `basic/compact test ROM 4종`, 각 apply report 를 한 번에 다시 만들었다.
  - 따라서 앞으로는 `/private/tmp` 청소 여부와 상관없이 최신 test ROM 을 항상 같은 절차로 다시 만들 수 있다.
  - 또 현재 production test 기준은 [core_ui_test_rom_matrix.md](/Users/user/test/analysis/core_ui_test_rom_matrix.md) 와 스크립트 재생성 결과로 고정됐다.
- 판정: `성공`
- 교훈: placeholder 검증 자산과 production test 자산을 섞어 보면 판단이 흔들린다. 한글 표시 품질을 볼 때는 **legacy placeholder ROM 을 버리고, 재생성 가능한 최신 compact/basic test ROM** 만 기준으로 삼아야 한다.

### 실험 60

- 가설: 사용자 입장에서 `priority48` 나 `save/menu` 보다, 게임 시작 직후 바로 보이는 intro 텍스트가 첫 QA 지점으로 훨씬 적합하다. 이 화면의 한글화를 먼저 닫으면 실제 폰트 품질 확인이 쉬워진다.
- 시도:
  - 시작 화면에 뜨는 4조각을 [startup_intro_texts.json](/Users/user/test/confirmed_data/extracted_texts/startup_intro_texts.json) 으로 분리했다.
  - 번역:
    - `大陸暦` -> `대륙력`
    - `１９１０年　２月` -> `1910년 2월`
    - `　　リゼンブール村` -> `리젠불 마을`
    - `　兄１１歳　　弟１０歳` -> `형 11세    동생 10세`
  - 현재 `full80` glyph 세트에 없는 `륙, 력, 년, 월, 마, 형, 동, 생` 8글자를 [startup_intro_missing_manifest.json](/Users/user/test/analysis/startup_intro_missing_manifest.json) 과 [startup_intro_missing_workbench](/Users/user/test/analysis/startup_intro_missing_workbench) 로 준비했다.
  - 이를 `full80` font ROM 위에 append 한 뒤, merged table [hangul_core_ui_plus_startup.tbl](/Users/user/test/analysis/hangul_core_ui_plus_startup.tbl) 을 사용해 `/private/tmp/hnr_rebuild_check/hnr_startup_intro_test.gba` 를 만들었다.
- 결과:
  - [startup_intro_apply_report.json](/Users/user/test/analysis/startup_intro_apply_report.json) 기준 `4 in_place`
  - `search-text` 로 `대륙력`, `형 11세    동생 10세` 도 실제 ROM 안에서 다시 확인했다.
  - 따라서 이제 첫 시각 QA 는 `priority48 compact` 보다도 **시작 화면 intro test ROM** 을 우선 기준으로 잡을 수 있다.
- 판정: `성공`
- 교훈: 테스트 지점은 기술적으로 다루기 쉬운 곳보다 **사용자가 바로 접근할 수 있는 화면** 을 우선하는 편이 훨씬 효율적이다. 앞으로 초기 QA 기준점은 시작 화면 intro 를 최우선으로 둔다.

### 실험 61

- 가설: 시작 화면 intro 를 첫 QA 기준으로 쓰려면, core UI 전체 matrix 를 다시 만드는 큰 스크립트 말고 **intro 전용 재생성 경로** 가 따로 있어야 반복 검증이 빨라진다.
- 시도:
  - [build_startup_intro_test.sh](/Users/user/test/scripts/build_startup_intro_test.sh) 를 추가해, `font_expand_base -> full80 font append -> startup 보충 glyph append -> startup intro apply` 만 수행하도록 분리했다.
  - [core_ui_test_rom_matrix.md](/Users/user/test/analysis/core_ui_test_rom_matrix.md) 에 startup intro 의 고정 확인 오프셋 `0x703D70, 0x703D7E, 0x703D94, 0x703DAC` 와 새 재생성 명령을 적었다.
  - [active_task.md](/Users/user/test/docs/active_task.md), [text_reinsertion_progress.md](/Users/user/test/docs/tracks/text_reinsertion_progress.md), [font_asset_workflow.md](/Users/user/test/docs/font_asset_workflow.md) 도 같은 기준으로 맞췄다.
- 결과:
  - 앞으로는 시작 화면 QA 를 위해 불필요한 다른 테스트 ROM 들까지 다시 만들 필요가 없어졌다.
  - startup intro 는 이제 "가장 먼저 보기 좋은 테스트 지점"을 넘어서, **전용 재생성 경로가 있는 1차 QA 기준선** 이 됐다.
- 판정: `성공`
- 교훈: 실제 검수에서 자주 보는 화면은, 데이터보다 **재생성 절차가 짧은 전용 루프** 를 먼저 만들어 두는 편이 훨씬 효율적이다.

### 실험 62

- 가설: `analysis/` 루트에 raw evidence 가 너무 많이 남아 있으면, 다음 세션에서 hot file 과 cold file 이 섞여 불필요한 탐색 비용이 커진다. 참조가 거의 없는 raw evidence 만 archive 로 내리면 다음 작업이 더 안정적이다.
- 시도:
  - `helper_*.txt`, `helper_cluster_*.txt`, `caller_*.txt`, `read_*.txt`, `write_*.txt`, `refs_*.json`, `init_*.txt`, 위치/문자 보조 스냅샷 등을 [archive/data_structure_raw](/Users/user/test/analysis/archive/data_structure_raw) 로 이동했다.
  - 루트 진입점 [README.md](/Users/user/test/analysis/README.md) 를 hot path / active text / active font / archive 기준으로 다시 썼다.
  - archive 안내 문서 [archive/README.md](/Users/user/test/analysis/archive/README.md), [data_structure_raw/README.md](/Users/user/test/analysis/archive/data_structure_raw/README.md) 를 추가하고, [reference_map.md](/Users/user/test/docs/reference_map.md) 에도 archive 진입점을 걸었다.
- 결과:
  - `analysis/` 루트에서 지금 직접 여는 파일과 예전 raw evidence 가 분리됐다.
  - archive 를 열지 않아도 현재 한글화 hot path 를 따라가는 데 필요한 파일만 빠르게 찾을 수 있게 됐다.
- 판정: `성공`
- 교훈: 증거를 지우는 것보다 **루트 노이즈를 줄이고 archive 경로를 명시하는 것** 이 장기 작업에 훨씬 안전하다.

### 실험 63

- 가설: 패치 ROM 출력이 `/private/tmp` 와 프로젝트 폴더에 섞여 있으면 확인 경로가 흔들린다. 프로젝트 내부 출력 폴더 하나로 고정하고 전체를 gitignore 처리하면 이후 작업이 단순해진다.
- 시도:
  - 프로젝트 루트에 `patched_roms/` 폴더를 기준 출력 위치로 정하고, `.gitignore` 에 `patched_roms/*` 와 `!patched_roms/.gitkeep` 규칙을 추가했다.
  - [core_ui_test_rom_matrix.md](/Users/user/test/analysis/core_ui_test_rom_matrix.md), [active_task.md](/Users/user/test/docs/active_task.md), [font_asset_workflow.md](/Users/user/test/docs/font_asset_workflow.md), [text_reinsertion_progress.md](/Users/user/test/docs/tracks/text_reinsertion_progress.md) 의 예시 경로를 `patched_roms/rebuild_check` 기준으로 갱신했다.
- 결과:
  - 앞으로 패치 ROM 은 프로젝트 내부 `patched_roms/` 아래에 두면서도 git 추적에서는 제외할 수 있게 됐다.
  - 경로 기준이 하나로 고정되어 QA 와 재생성 문서도 덜 흔들리게 됐다.
- 판정: `성공`
- 교훈: 산출물 위치를 일찍 고정해 두면, 실제 한글화 반복 테스트에서 경로 혼선이 크게 줄어든다.

### 실험 64

- 가설: 시작 화면에서 일부 글자만 보이고 나머지가 빈칸처럼 사라진 이유는 렌더러보다 **workbench glyph 자체가 비어 있기 때문** 일 가능성이 높다. blank glyph 를 빌드 전에 자동 검출하면 같은 혼선을 막을 수 있다.
- 시도:
  - `hangul_core_ui_workbench/*.pgm` 와 `startup_intro_missing_workbench/*.pgm` 의 nonzero pixel count 를 직접 확인했다.
  - 그 결과 core UI workbench 쪽은 샘플 `10/10` 이 모두 `nonzero=0`, 반면 startup intro 추가 `8`글자는 모두 nonzero 픽셀이 있었다.
  - 이어서 `audit-pgm-glyph-set` CLI 를 추가하고, [build_startup_intro_test.sh](/Users/user/test/scripts/build_startup_intro_test.sh) / [build_core_ui_test_roms.sh](/Users/user/test/scripts/build_core_ui_test_roms.sh) 가 기본적으로 blank glyph 검사 후 빌드하도록 바꿨다.
- 결과:
  - 원인은 폰트 엔진 자체보다는 **비어 있는 Hangul workbench** 로 확정됐다.
  - 이제는 실제 픽셀이 없는 glyph 세트로는 test ROM 이 조용히 생성되지 않고, blank glyph 수를 먼저 알려 주게 됐다.
- 판정: `성공`
- 교훈: 한글 테스트에서 “아무것도 안 보임”은 코드 경로 문제일 수도 있지만, 그 전에 **glyph bitmap 존재 여부를 자동 검사** 해야 한다.

### 실험 65

- 가설: startup intro 는 full80 공용 세트에 묶어 둘 필요가 없다. `NanumSquareR.ttf` 기준 startup 전용 workbench 를 만들면, blank core UI 세트와 분리해서 바로 검증할 수 있다.
- 시도:
  - [startup_intro_texts.json](/Users/user/test/confirmed_data/extracted_texts/startup_intro_texts.json) 에서 [startup_intro_seed_manifest.json](/Users/user/test/analysis/startup_intro_seed_manifest.json) `14`글자를 다시 만들었다.
  - Swift 경로 대신 [render_reference_font_workbench.py](/Users/user/test/scripts/render_reference_font_workbench.py) 를 추가하고, `/Users/user/Library/Fonts/NanumSquareR.ttf` 를 사용해 [startup_intro_nanumsquare_workbench](/Users/user/test/analysis/startup_intro_nanumsquare_workbench) 를 생성했다.
  - 새 workbench 는 `14 / 14` nonblank glyph 상태임을 `audit-pgm-glyph-set` 로 확인했다.
  - [build_startup_intro_test.sh](/Users/user/test/scripts/build_startup_intro_test.sh) 는 이제 full80 공용 세트 없이, startup 전용 workbench 만 append 해서 ROM 을 만든다.
- 결과:
  - `/Users/user/test/patched_roms/startup_nanumsquare_check/hnr_startup_intro_test.gba` 빌드가 다시 통과했고, `대륙력` / `리젠불 마을` search hit 도 유지됐다.
  - 따라서 startup intro 는 이제 **NanumSquareR 기반 seed glyph 로 독립 검증 가능한 상태** 가 됐다.
- 판정: `성공`
- 교훈: 초반 검증 화면은 공용 세트와 분리한 **작은 전용 workbench** 로 닫는 편이 훨씬 안정적이다.

### 실험 66

- 가설: startup intro `NanumSquareR` seed 가 화면에서 1픽셀 위로 들려 보이는 이유는 실제 baseline 이 아니라, seed 렌더링 때 `y_offset=-1` 을 준 탓일 가능성이 높다.
- 시도:
  - [startup_intro_nanumsquare_workbench_report.json](/Users/user/test/analysis/startup_intro_nanumsquare_workbench_report.json) 의 렌더링 설정을 다시 확인했다.
  - 대표 glyph 들의 row occupancy 를 계산해 top row 사용과 bottom row 여백을 함께 봤다.
  - startup intro seed 기준값을 `y_offset=0` 으로 되돌리고, 같은 manifest 로 workbench 와 test ROM 을 다시 만들었다.
- 결과:
  - 기존 seed 는 실제로 `y_offset=-1` 이었고, 대표 glyph 다수가 상단 행 점유가 크고 하단 2행이 비는 패턴이었다.
  - `y_offset=0` 으로 다시 렌더링한 뒤 대표 glyph 분포는 한 줄 아래로 이동했고, [startup_intro_nanumsquare_workbench_report.json](/Users/user/test/analysis/startup_intro_nanumsquare_workbench_report.json) 도 새 기준값을 반영하게 됐다.
  - 이어서 [build_startup_intro_test.sh](/Users/user/test/scripts/build_startup_intro_test.sh) 로 [hnr_startup_intro_test.gba](/Users/user/test/patched_roms/rebuild_check/hnr_startup_intro_test.gba) 를 다시 빌드했고, 적용 결과는 여전히 `4 in_place` 다.
  - 따라서 이번 증상은 렌더러 버그보다 **seed baseline 설정 문제** 로 보는 편이 자연스럽다.
- 판정: `성공`
- 교훈: 참조 폰트 seed 는 "보인다"만으로 끝내지 말고, 실제 픽셀 분포와 화면 확대샷 기준으로 baseline 도 따로 검증해야 한다.

### 실험 67

- 가설: startup intro 에서 빨강/파랑 speckle 처럼 깨져 보인 원인은 `NanumSquareR` 자체보다, anti-alias grayscale 이 그대로 공통 `fnt` 4bpp palette index 로 들어간 탓일 가능성이 높다.
- 시도:
  - 공통 원본 glyph dump 들의 실제 픽셀 값을 다시 확인했다.
  - startup intro seed PGM 과 ROM에 append 된 glyph nibble 값을 각각 대조했다.
  - [render_reference_font_workbench.py](/Users/user/test/scripts/render_reference_font_workbench.py) 에서 seed 를 기본적으로 `0/17/34` native 3-level 로 양자화하도록 바꾸고, `audit-pgm-glyph-set` 에 허용값 검사 옵션을 추가했다.
  - [build_startup_intro_test.sh](/Users/user/test/scripts/build_startup_intro_test.sh) 와 [build_core_ui_test_roms.sh](/Users/user/test/scripts/build_core_ui_test_roms.sh) 가 startup intro workbench 에 대해 `--allowed-values 0,17,34 --fail-on-disallowed` 를 강제하도록 묶었다.
- 결과:
  - 공통 원본 glyph dump 는 실제로 `0,17,34` 세 값만 썼다.
  - startup intro seed 도 새 경로에서는 `0,17,34` 만 남고, append 뒤 실제 ROM glyph nibble 도 `0,1,2` 만 쓰는 것으로 확인됐다.
  - 따라서 speckle 증상은 폰트 파일 자체보다 **anti-alias grayscale 을 native palette 단계로 제한하지 않았던 seed 생성 흐름** 에서 왔다고 보는 편이 자연스럽다.
- 판정: `성공`
- 교훈: 이 게임 공통 font 에 새 glyph 를 넣을 때는 “흰색이면 된다”가 아니라, **원본 glyph 가 실제로 쓰는 palette 단계까지 맞춰서** 넣어야 한다.

### 실험 68

- 가설: startup intro 에서 형태가 무너지는 문제는 단순 회색 단계 때문만이 아니라, `NanumSquareR` 같은 일반 UI 벡터 폰트를 `12x12` binary glyph 로 강하게 축소하는 방식 자체에 더 큰 원인이 있을 수 있다.
- 시도:
  - 공식 자료 기준으로 `Galmuri`, `Neo둥근모`, `D2Coding` 같은 한국어 폰트 후보를 다시 조사했다.
  - 동시에 로컬에 이미 있는 `NanumSquareR`, `NanumGothic`, `NanumBarunGothic`, `NanumSquareRoundR`, `AppleSDGothicNeo`, `D2Coding` 을 같은 `12x12 binary2` 조건으로 비교했다.
  - 비교 결과를 [font_candidate_survey.md](/Users/user/test/analysis/font_candidate_survey.md) 와 [startup_font_candidate_binary2_sheet.png](/Users/user/test/analysis/startup_font_candidate_binary2_sheet.png) 로 남겼다.
- 결과:
  - `NanumSquareR` 는 회색을 없애면 잡티는 줄지만 자소 내부 구조가 쉽게 붕괴했다.
  - `AppleSDGothicNeo` 는 너무 얇아지는 쪽으로 무너졌고, 로컬 후보 중에서는 `D2Coding` 이 상대적으로 덜 망가졌다.
  - 공식 성격상 현재 목표와 가장 잘 맞는 장기 후보는 bitmap/pixel 계열인 `Galmuri` 쪽으로 좁혀졌다.
- 판정: `성공`
- 교훈: `12x12` GBA 한글화에서 중요한 건 "유명한 한글 폰트"가 아니라, **작은 픽셀 격자에서 무너지지 않는 bitmap/pixel 성격** 이다.

### 실험 69

- 가설: `Galmuri11` 같이 원래부터 bitmap 계열 성격이 강한 폰트는 `NanumSquareR` 보다 `12x12` binary glyph 에 더 잘 맞을 가능성이 높다.
- 시도:
  - `npm install --no-save galmuri` 로 공식 패키지를 프로젝트 안에 가져왔다.
  - `Galmuri11`, `Galmuri11-Condensed`, `Galmuri11-Bold`, `GalmuriMono11` 을 같은 `12x12 binary2` 조건으로 비교했다.
  - 이어서 `Galmuri11.ttf` 에 대해 `font-size 10/11/12` 를 비교하고, [startup_font_candidate_galmuri_sheet.png](/Users/user/test/analysis/startup_font_candidate_galmuri_sheet.png), [startup_font_galmuri11_size_sheet.png](/Users/user/test/analysis/startup_font_galmuri11_size_sheet.png) 로 저장했다.
  - 최종적으로 `Galmuri11.ttf` `font-size=10` `y_offset=0` `binary2 threshold=160` 으로 [startup_intro_galmuri11_workbench](/Users/user/test/analysis/startup_intro_galmuri11_workbench) 를 만들고, [build_startup_intro_test.sh](/Users/user/test/scripts/build_startup_intro_test.sh) / [build_core_ui_test_roms.sh](/Users/user/test/scripts/build_core_ui_test_roms.sh) 의 startup 경로를 이 세트로 바꿨다.
- 결과:
  - `Galmuri11` 계열이 `NanumSquareR` 보다 자소 구조를 덜 잃었고, 현재 기준으로는 `size10` 이 가장 덜 무너졌다.
  - 새 startup intro ROM [hnr_startup_intro_test.gba](/Users/user/test/patched_roms/rebuild_check/hnr_startup_intro_test.gba) 도 다시 빌드 완료했다.
  - 따라서 startup intro active 경로는 현재 **NanumSquareR 에서 Galmuri11 으로 전환된 상태** 다.
- 판정: `성공`
- 교훈: 실제 GBA 한글화에서는 “벡터 한글 폰트 + 강한 이진화”보다, **애초에 픽셀 구조가 있는 폰트를 작은 칸에 맞추는 쪽** 이 훨씬 유리하다.

### 실험 70

- 가설: `Galmuri` 가 기대만큼 안정적이지 않다면, 현재 로컬 후보 중에서는 `D2Coding` 을 더 공격적으로 튜닝한 쪽이 startup intro 기준 1차 실험에 더 적합할 수 있다.
- 시도:
  - `D2Coding-Ver1.3.2-20180524.ttf` 를 `size 9/10/11/12`, threshold `128/144/160/176` 로 다시 비교했다.
  - 비교 시트를 [startup_font_d2coding_size_sheet.png](/Users/user/test/analysis/startup_font_d2coding_size_sheet.png) 로 저장했다.
  - 최종적으로 `size=11`, `threshold=144` 를 골라 [startup_intro_d2coding_workbench](/Users/user/test/analysis/startup_intro_d2coding_workbench) 를 만들고, startup build script 의 active 경로를 이 workbench 로 바꿨다.
  - [build_startup_intro_test.sh](/Users/user/test/scripts/build_startup_intro_test.sh) 로 [hnr_startup_intro_test.gba](/Users/user/test/patched_roms/rebuild_check/hnr_startup_intro_test.gba) 를 다시 빌드했다.
- 결과:
  - startup intro active 경로는 현재 `D2Coding size11 threshold144` 기준으로 전환됐다.
  - 동시에 [run_glyph_editor.py](/Users/user/test/scripts/run_glyph_editor.py) 와 [glyph_editor.html](/Users/user/test/tools/glyph_editor.html) 로, workbench `.pgm` 를 직접 수정할 수 있는 로컬 에디터도 준비했다.
- 판정: `성공`
- 교훈: 자동 선택이 계속 마음에 들지 않을 때는 폰트 후보를 바꾸는 것과 별개로, **즉시 수동 보정 가능한 도구** 를 같이 두는 편이 훨씬 낫다.

### 실험 71

- 가설: `년` 같은 글자에서 빠지는 획이 계속 생기면, threshold 기반 binary 변환보다 **0이 아니면 전부 켜는 쪽** 이 startup intro 1차 확인에는 더 낫다.
- 시도:
  - [startup_intro_d2coding_workbench](/Users/user/test/analysis/startup_intro_d2coding_workbench) 를 같은 `D2Coding` `size11` 기준으로 다시 만들되, `binary_threshold=1` 로 낮췄다.
  - 대표 glyph `년`, `대` 의 nonzero pixel 분포를 다시 확인했고, 이어서 [build_startup_intro_test.sh](/Users/user/test/scripts/build_startup_intro_test.sh) 로 [hnr_startup_intro_test.gba](/Users/user/test/patched_roms/rebuild_check/hnr_startup_intro_test.gba) 를 다시 빌드했다.
- 결과:
  - 현재 startup intro D2 workbench 는 사실상 `0이 아니면 전부 켜기` binary glyph 가 됐다.
  - 실제 append 뒤 ROM glyph nibble 도 여전히 `0,2` 만 유지했고, startup intro ROM 재빌드도 정상 완료했다.
- 판정: `성공`
- 교훈: 작은 한글 glyph 에서 획 유실이 심할 때는, 미세한 anti-alias 정리보다 **획 보존 우선 정책** 을 먼저 시험하는 편이 낫다.

### 실험 72

- 가설: `0이 아니면 전부 켜기`는 획은 살리지만 너무 두꺼워질 수 있으므로, glyph 별 최대 밝기 기준으로 **하위 20%만 잘라내는 비율 컷** 이 startup intro 에 더 균형이 좋을 수 있다.
- 시도:
  - [render_reference_font_workbench.py](/Users/user/test/scripts/render_reference_font_workbench.py) 의 `binary_cutoff_ratio` 경로를 사용해 [startup_intro_d2coding_workbench](/Users/user/test/analysis/startup_intro_d2coding_workbench) 를 `cutoff_ratio=0.2` 로 다시 생성했다.
  - `년`, `대` 의 effective threshold 와 row occupancy 를 다시 확인했고, 이어서 [build_startup_intro_test.sh](/Users/user/test/scripts/build_startup_intro_test.sh) 로 [hnr_startup_intro_test.gba](/Users/user/test/patched_roms/rebuild_check/hnr_startup_intro_test.gba) 를 다시 빌드했다.
- 결과:
  - 현재 `년`, `대` 의 effective threshold 는 `51` 로 계산되며, `년`의 nonzero pixel 은 `41`, `대`는 `55` 로 다시 올라왔다.
  - append 뒤 실제 ROM glyph nibble 은 여전히 `0,2` 만 유지했고, startup intro ROM 재빌드도 정상 완료했다.
- 판정: `성공`
- 교훈: 고정 threshold 하나보다, glyph 밝기 분포를 따라가는 **비율 컷** 이 작은 한글 glyph 에 더 유연하게 맞는다.

### 실험 73

- 가설: startup intro 폰트 실험을 매번 대화로 지시하면 토큰 낭비가 크므로, `폰트명 + 하위 N%` 만 주면 workbench 와 ROM 이 같이 만들어지는 단일 실행 스크립트가 필요하다.
- 시도:
  - [build_startup_intro_variant.py](/Users/user/test/scripts/build_startup_intro_variant.py) 를 추가했다.
  - 이 스크립트는 `D2Coding`, `Galmuri11`, `NanumSquareR` preset 과 직접 `--font-path` 를 지원한다.
  - 예시로 `python3 scripts/build_startup_intro_variant.py D2Coding 20` 을 실제 실행해 workbench, glyph audit, font append, startup intro ROM 생성을 끝까지 검증했다.
- 결과:
  - 생성 경로:
    - workbench: [startup_intro_d2coding_p20_workbench](/Users/user/test/analysis/startup_intro_d2coding_p20_workbench)
    - ROM: [hnr_startup_intro_test.gba](/Users/user/test/patched_roms/startup_variants/d2coding_p20/hnr_startup_intro_test.gba)
  - 따라서 이제 startup intro 폰트 실험은 대화 없이도 **`폰트명 + 퍼센트` 한 줄** 로 재현 가능하다.
- 판정: `성공`
- 교훈: 비교 실험이 반복될수록, 해석 도구보다 **사용자가 직접 돌릴 수 있는 wrapper script** 가 생산성을 더 크게 올린다.

### 실험 74

- 가설: `폰트명 + 퍼센트` wrapper 가 매번 새 폴더를 만들면 오히려 관리 비용이 커지므로, 기본값은 **단일 active workbench / 단일 output ROM 경로를 덮어쓰는 방식** 이 더 낫다.
- 시도:
  - [build_startup_intro_variant.py](/Users/user/test/scripts/build_startup_intro_variant.py) 기본 경로를 [startup_intro_active_workbench](/Users/user/test/analysis/startup_intro_active_workbench) 와 `/Users/user/test/patched_roms/startup_intro_active/` 로 고정했다.
  - 같은 기준에 맞춰 [build_startup_intro_test.sh](/Users/user/test/scripts/build_startup_intro_test.sh), [build_core_ui_test_roms.sh](/Users/user/test/scripts/build_core_ui_test_roms.sh), [run_glyph_editor.py](/Users/user/test/scripts/run_glyph_editor.py) 의 기본 startup intro 경로도 active 경로로 맞췄다.
- 결과:
  - 기본 실험 경로가 더 이상 `font+percent` 별 폴더를 증식시키지 않고, 항상 같은 workbench 와 같은 startup intro ROM 을 갱신하게 됐다.
  - 비교 보존이 필요할 때만 `--output-name` 을 주는 구조로 정리됐다.
- 판정: `성공`
- 교훈: 반복 튜닝 작업은 “비교 파일을 많이 남기는 것”보다 **active 산출물 1세트와 선택적 named snapshot** 구조가 관리에 훨씬 유리하다.

### 실험 75

- 가설: `gba-free-fonts` 의 한국어 atlas 는 우리 게임 포맷에 직접 꽂을 수는 없어도, startup intro `12x12` seed workbench 로 변환하면 **실제 비교 ROM** 까지는 만들 수 있다.
- 시도:
  - `SourceHanSans/KR`, `SourceHanMono/KR` 자산과 라이선스를 [third_party/gba_free_fonts](/Users/user/test/third_party/gba_free_fonts) 아래 최소 범위만 복사했다.
  - [import_bmfont_workbench.py](/Users/user/test/scripts/import_bmfont_workbench.py) 를 추가해 `.fnt + atlas png` 에서 `12x12 PGM workbench` 를 생성하게 했다.
  - 이 경로를 [build_startup_intro_variant.py](/Users/user/test/scripts/build_startup_intro_variant.py) 에 연결해 `SourceHanSansKR`, `SourceHanMonoKR` preset 으로 startup intro ROM 을 실제 생성했다.
- 결과:
  - `SourceHanSansKR`, `SourceHanMonoKR` 둘 다 startup intro `4 in_place` ROM 생성까지 끝났다.
  - 비교 ROM 은 [startup_intro_font_compare.md](/Users/user/test/analysis/startup_intro_font_compare.md) 와 `/Users/user/test/patched_roms/font_compare/` 아래에 정리했다.
- 판정: `성공`
- 교훈: `gba-free-fonts` 는 “직접 적용 불가”가 아니라, **우리 커스텀 fnt 포맷과의 브리지 단계가 필요했던 것** 이다.

### 실험 76

- 가설: startup intro glyph 수정을 빠르게 반복하려면, glyph editor 가 단순 저장만 하는 구조보다 **저장 후 즉시 ROM 재빌드** 까지 포함해야 한다.
- 시도:
  - [run_glyph_editor.py](/Users/user/test/scripts/run_glyph_editor.py) 에 `/rebuild` endpoint 를 추가했다.
  - [glyph_editor.html](/Users/user/test/tools/glyph_editor.html) 에 `Save + Rebuild ROM` 버튼과 active output 경로 표시를 추가했다.
- 결과:
  - active startup intro workbench 를 열었을 때는 PGM 저장 직후 [hnr_startup_intro_test.gba](/Users/user/test/patched_roms/startup_intro_active/hnr_startup_intro_test.gba) 를 같은 브라우저 루프 안에서 다시 만들 수 있게 됐다.
- 판정: `성공`
- 교훈: startup intro 같은 짧은 QA 루프는 “glyph 수정”과 “실제 ROM 확인”을 붙여야 생산성이 오른다.

### 실험 77

- 가설: 폰트가 아직 확정되지 않았더라도, Registry A entry `8` 의 대형 대사 뱅크를 cluster별 번역 workset 으로 먼저 쪼개 두면 이후 번역/검수 루프에 바로 들어갈 수 있다.
- 시도:
  - [build_entry8_cluster_worksets.py](/Users/user/test/scripts/build_entry8_cluster_worksets.py) 를 추가했다.
  - [registry_a_entry8_prefixed_texts.json](/Users/user/test/confirmed_data/extracted_texts/registry_a_entry8_prefixed_texts.json) 과 [registry_a_entry8_cluster_catalog.json](/Users/user/test/analysis/registry_a_entry8_cluster_catalog.json) 을 입력으로 받아, [registry_a_entry8_clusters](/Users/user/test/confirmed_data/translation_workspace/registry_a_entry8_clusters) 아래 cluster별 번역 JSON을 생성하게 했다.
  - 상위 인덱스 [registry_a_entry8_clusters_manifest.json](/Users/user/test/confirmed_data/translation_workspace/registry_a_entry8_clusters_manifest.json) 에 `record_count`, `primary_tag`, `sample_texts`, output file 경로를 함께 기록했다.
- 결과:
  - entry `8` 대형 bank 가 `72`개 cluster 번역 workset 으로 분리되었다.
  - 이제 이후 번역은 `entry8 전체 9823건` 을 한 번에 보는 대신, `cluster_00_liore.json` 같은 작은 단위로 바로 시작할 수 있다.
- 판정: `성공`
- 교훈: 추출이 충분히 진행된 뒤에는 새 source 를 더 찾는 것보다, **번역자가 실제로 잡을 수 있는 작업 단위로 재구성하는 것** 이 더 큰 진전이다.

### 실험 78

- 가설: “지금까지 뽑힌 전체 텍스트” 기준 파일을 따로 고정해 두면, 폰트 확정과 무관하게 번역/검수 준비를 바로 시작할 수 있다.
- 시도:
  - [build_master_text_workspace.py](/Users/user/test/scripts/build_master_text_workspace.py) 를 추가했다.
  - `system / item / location / battle / ability / material / ui skill / save menu / Registry D / Registry A entry 8 / Registry A entry 12 / credits` `12`개 소스를 합쳐 [all_extracted_texts_master.json](/Users/user/test/confirmed_data/translation_workspace/all_extracted_texts_master.json) 을 생성했다.
  - source별 개수와 포함 범위를 [all_extracted_texts_manifest.json](/Users/user/test/confirmed_data/translation_workspace/all_extracted_texts_manifest.json) 에 기록했다.
- 결과:
  - 현재 known extracted text sources 기준으로 `10752`건 마스터 작업 세트가 생겼다.
  - 이제 “큰 줄기 텍스트는 다 모은 상태에서 폰트를 고르는 중”이라는 기준점을 명확하게 유지할 수 있다.
- 판정: `성공`
- 교훈: 100% 추출 판정과 별개로, **현재 확보분의 안정적인 기준본** 을 갖는 것은 번역/검수/재삽입 모든 단계의 출발점이 된다.

### 실험 79

- 가설: 번역 준비 파일이 늘어날수록 `translation_workspace` 안에도 진입점이 필요하다. master set, cluster worksets, 우선 workset 을 한 군데서 가리키는 index/README 가 있으면 다음 단계 전환이 더 쉬워진다.
- 시도:
  - [build_translation_workspace.py](/Users/user/test/scripts/build_translation_workspace.py) 를 추가했다.
  - 이 스크립트가 [build_master_text_workspace.py](/Users/user/test/scripts/build_master_text_workspace.py) 와 [build_entry8_cluster_worksets.py](/Users/user/test/scripts/build_entry8_cluster_worksets.py) 를 함께 호출하도록 했다.
  - 결과로 [translation_workspace/index.json](/Users/user/test/confirmed_data/translation_workspace/index.json) 과 [translation_workspace/README.md](/Users/user/test/confirmed_data/translation_workspace/README.md) 를 생성하게 했다.
- 결과:
  - 이제 `translation_workspace` 폴더만 열어도 전체 기준본, entry8 cluster 세트, 우선 번역 순서를 한 번에 확인할 수 있다.
  - 이후 번역/검수 단계는 이 인덱스를 출발점으로 잡으면 된다.
- 판정: `성공`
- 교훈: 대형 JSON 을 만드는 것만으로는 충분하지 않고, **사람이 바로 다음 행동을 정할 수 있는 작업 허브** 까지 있어야 실제 생산성이 오른다.

### 실험 80

- 가설: 현재 추출본에 대해 “이 텍스트가 아이템인지, 대사인지, UI인지” 같은 성격은 source 기준으로 객관적으로 정리할 수 있지만, 화자 정보는 별도 script metadata 분석 없이는 확정할 수 없다.
- 시도:
  - [build_text_taxonomy_manifest.py](/Users/user/test/scripts/build_text_taxonomy_manifest.py) 를 추가했다.
  - [all_extracted_texts_master.json](/Users/user/test/confirmed_data/translation_workspace/all_extracted_texts_master.json) 을 기준으로 source_group -> content_type 매핑을 [text_taxonomy_manifest.json](/Users/user/test/confirmed_data/translation_workspace/text_taxonomy_manifest.json) 에 기록했다.
  - speaker / speaker_id 같은 명시 필드가 현재 추출 JSON에는 없다는 점도 같이 명시했다.
- 결과:
  - source 기반으로는 `system_message`, `location_name`, `save_menu_message`, `dialogue_or_event_script` 같은 객관적 분류표를 만들었다.
  - 반면 “이 대사가 어떤 캐릭터의 대사인가?”는 현재 추출 구조만으로는 비자의적으로 확정할 수 없다는 경계가 분명해졌다.
- 판정: `성공`
- 교훈: 작업 태그와 실제 메타데이터를 섞지 않으려면, **객관적으로 확정 가능한 분류와 아직 미확정인 정보** 를 문서에서 분리해야 한다.

### 실험 81

- 가설: 사용자가 따로 만든 번역/검수 에이전트 MD를 프로젝트 안에 고정하고, 현재 workset 허브와 연결해 두면 나중에 실제 번역 단계로 넘어갈 때 준비 비용이 크게 줄어든다.
- 시도:
  - 사용자가 제공한 `common / translation / review` MD `3`개를 [translation_team](/Users/user/test/docs/translation_team) 아래로 복사했다.
  - [translation_team/README.md](/Users/user/test/docs/translation_team/README.md) 를 추가해 읽는 순서, 권장 workset 시작점, 화자 정보 주의점을 정리했다.
  - [translation_team_bundle.json](/Users/user/test/confirmed_data/translation_workspace/translation_team_bundle.json) 에 team docs / workspace docs / 추천 작업 순서를 기계적으로 읽기 쉬운 형태로 묶었다.
- 결과:
  - 이제 프로젝트 안에서 번역팀 문서와 실제 추출 workset 허브가 연결되었다.
  - 나중에 번역을 시작할 때는 `translation_team_bundle.json` 또는 `translation_team/README.md` 만 보면 바로 진입 가능하다.
- 판정: `성공`
- 교훈: 번역팀용 규칙 문서와 실제 작업 데이터가 분리돼 있으면 다음 단계 전환이 느려진다. **규칙 문서와 workset 허브를 같은 프로젝트 안에서 연결해 두는 것** 이 중요하다.

### 실험 82

- 가설: 사용자가 만든 `12x12` 한글 atlas 가 `64`열 row-major `U+AC00..U+D7A3` 순서를 따른다면, giant 문자 목록을 별도 파일로 계속 관리하지 않고도 startup intro 테스트까지 바로 연결할 수 있다.
- 시도:
  - atlas 파일을 프로젝트 안 [maruminyahangul_12x12.png](/Users/user/test/third_party/font_atlases/maruminyahangul_12x12.png) 로 복사했다.
  - [maruminyahangul_12x12.metadata.json](/Users/user/test/third_party/font_atlases/maruminyahangul_12x12.metadata.json) 에 `tile size / columns / rows / unicode range / order` 메타데이터를 기록했다.
  - [import_hangul_syllable_atlas.py](/Users/user/test/scripts/import_hangul_syllable_atlas.py) 를 추가해 atlas 를 startup intro seed manifest 기준 workbench 로 변환했다.
  - [build_startup_intro_from_atlas.sh](/Users/user/test/scripts/build_startup_intro_from_atlas.sh) 로 startup intro 테스트 ROM 을 실제 생성했다.
- 결과:
  - atlas `768x2100` 는 `12x12`, `64 x 175`, 총 `11200`칸으로 해석되었고, `11172`자 완성형을 담고 `28`칸이 남았다.
  - startup intro 기준 `14`글자 workbench 와 [hnr_startup_intro_maruminyahangul12.gba](/Users/user/test/patched_roms/font_compare/maruminyahangul12_startup/hnr_startup_intro_maruminyahangul12.gba) 생성까지 완료했다.
  - 현재 이 atlas 는 giant 문자 목록 대신 메타데이터 파일 하나로 순서 규칙을 안정적으로 관리할 수 있다.
- 판정: `성공`
- 교훈: 표준 완성형 순서를 그대로 따르는 atlas 는 별도 문자 전개표보다 **명확한 메타데이터 + importer** 조합이 더 작고 안전한 truth source 가 된다.

### 실험 83

- 가설: 사용자가 확정한 `12x12` bitmap atlas 를 project-wide active source 로 고정하면, 이전 벡터 seed 비교를 버리고도 startup intro / core UI / 일반 번역 JSON 적용까지 한 경로로 정리할 수 있다.
- 시도:
  - [active_hangul_font_profile.json](/Users/user/test/confirmed_data/font_assets/active_hangul_font_profile.json) 과 [confirmed_data/font_assets/README.md](/Users/user/test/confirmed_data/font_assets/README.md) 를 추가했다.
  - [build_workbench_from_active_atlas.py](/Users/user/test/scripts/build_workbench_from_active_atlas.py) 로 번역 JSON 의 `translation` 필드에서 실제 사용 한글 subset 을 뽑아 atlas workbench 를 만들게 했다.
  - [build_translated_rom_with_active_atlas.sh](/Users/user/test/scripts/build_translated_rom_with_active_atlas.sh) 로 subset workbench 생성 -> glyph audit -> font append -> apply-translations 를 한 번에 묶었다.
  - 예전 `startup_intro_active_workbench`, `hangul_core_ui_workbench`, `hangul_core_ui_priority48_workbench` 와 폰트 후보 비교 산출물은 [analysis/archive/font_trials/2026-05-17_pre_bitmap_lock](/Users/user/test/analysis/archive/font_trials/2026-05-17_pre_bitmap_lock) 로 내렸다.
  - [rebuild_active_workbenches_from_atlas.sh](/Users/user/test/scripts/rebuild_active_workbenches_from_atlas.sh) 로 active startup/core UI workbench 들을 새 atlas 기준으로 다시 생성했다.
  - 이어서 core UI 번역 JSON [translation_workset_core_ui.json](/Users/user/test/confirmed_data/translation_worksets/translation_workset_core_ui.json) 을 같은 경로로 실제 ROM 에 적용했다.
- 결과:
  - startup intro active workbench `14`글자, core UI `priority48`, core UI `full80` workbench 가 모두 새 atlas 기반으로 교체되었다.
  - generic active-atlas 경로로 [core_ui_active_translated.gba](/Users/user/test/patched_roms/core_ui_active/core_ui_active_translated.gba) 생성에 성공했고, 현재 workset 기준 `15`건이 반영되었다.
  - 이제 이후 한글 폰트 작업은 “폰트 후보 비교”가 아니라 **같은 active atlas 로 subset glyph set 을 만들고, 필요한 픽셀만 수동 수정하는 단계** 로 정리되었다.
- 판정: `성공`
- 교훈: full-game 한글화에서는 “가장 예쁜 seed 후보 찾기”보다, **하나의 안정적인 atlas source 를 정하고 translation subset -> workbench -> ROM 경로를 고정하는 것** 이 장기적으로 더 큰 진전이다.

### 실험 84

- 가설: 최종 후보군이 `MaruMinyaHangul / Galmuri11 / GalmuriMono` `3`개로 줄어든 지금은, 새 후보 PNG 에서 반드시 필요한 문자 집합과 현재 파이프라인이 실제로 요구하는 비한글 범위를 분리해 적어 두는 편이 낫다.
- 시도:
  - [finalist_font_candidates.json](/Users/user/test/confirmed_data/font_assets/finalist_font_candidates.json) 를 추가해 최종 후보군 메타데이터를 프로젝트 안에 고정했다.
  - [build_font_charset_report.py](/Users/user/test/scripts/build_font_charset_report.py) 로 현재 번역 기준 문자 집합 리포트 [current_translation_charset_report.json](/Users/user/test/confirmed_data/font_assets/current_translation_charset_report.json), [current_translation_charset_non_hangul.txt](/Users/user/test/confirmed_data/font_assets/current_translation_charset_non_hangul.txt) 를 생성했다.
  - 그 결과를 바탕으로 [finalist_export_recommendation.md](/Users/user/test/confirmed_data/font_assets/finalist_export_recommendation.md) 와 [third_party/font_atlases/finalists/README.md](/Users/user/test/third_party/font_atlases/finalists/README.md) 를 작성했다.
- 결과:
  - 현재 파이프라인에서 새 후보 atlas 로 꼭 뽑아야 하는 것은 **한글 완성형 `11,172`자** 라는 점이 분명해졌다.
  - 숫자/영문/기본 기호는 1차 한글화 기준으로 원본 게임 공통 폰트를 그대로 재사용하면 된다.
  - 현재 번역 기준 비한글 사용 범위도 별도 리포트로 남겨서, 나중에 “숫자/기호도 같은 스타일로 맞출지”를 따로 판단할 수 있게 되었다.
- 판정: `성공`
- 교훈: 폰트 generator preset 은 “많이 들어 있는 것”보다, **현재 삽입 파이프라인이 실제로 무엇을 새로 요구하는지** 에 맞춰 고르는 편이 더 안전하다.

### 실험 85

- 가설: startup intro `4`줄만으로는 폰트 QA 범위가 좁다. 시작 카드 뒤의 인트로 문장과 리오르 표기/호명까지 묶은 workset, 그리고 길이를 줄여 `in_place` 비율을 높인 compact workset 을 함께 준비하면 후보 비교가 훨씬 쉬워진다.
- 시도:
  - [translation_workset_intro_full_test.json](/Users/user/test/confirmed_data/translation_worksets/translation_workset_intro_full_test.json) 를 만들어 시작 카드 뒤의 인트로 문장 `14`건을 추가로 묶었다.
  - 빌드 스크립트 [build_intro_full_test.sh](/Users/user/test/scripts/build_intro_full_test.sh) 를 추가해 실제 ROM 적용까지 확인했다.
  - 길이 문제로 `skipped_no_pointer` 가 남는 줄들을 줄이기 위해 [translation_workset_intro_full_compact_test.json](/Users/user/test/confirmed_data/translation_worksets/translation_workset_intro_full_compact_test.json) 와 [build_intro_full_compact_test.sh](/Users/user/test/scripts/build_intro_full_compact_test.sh) 도 만들었다.
  - 동시에 예전 vector/font compare 산출물, compact ROM 요약표, placeholder glyph, 오래된 seed manifest 들은 [analysis/archive/font_trials/2026-05-17_finalist_pool_cleanup](/Users/user/test/analysis/archive/font_trials/2026-05-17_finalist_pool_cleanup) 아래로 내렸다.
- 결과:
  - 일반 intro 확장 테스트 ROM [intro_full_active_translated.gba](/Users/user/test/patched_roms/intro_full_active/intro_full_active_translated.gba) 는 `10 in_place`
  - compact intro 테스트 ROM [intro_full_compact_active_translated.gba](/Users/user/test/patched_roms/intro_full_compact_active/intro_full_compact_active_translated.gba) 는 `18 in_place`
  - `analysis` 루트에는 startup active workbench, generated subset workbench, 현재도 직접 여는 요약만 남도록 정리되었다.
- 판정: `성공`
- 교훈: 폰트 QA 는 “정확한 번역”보다 먼저 **실제 화면에서 다양한 자모 조합을 많이 밟는 테스트 세트** 가 있어야 효율이 오른다.

### 실험 86

- 가설: 사용자가 새로 제공한 `MaruMinyaHangul`, `Galmuri11`, `GalmuriMono` `12x12` atlas 를 프로젝트 로컬로 교체/복사한 뒤에도, 기존 `11,172` 완성형 import 흐름에 바로 태울 수 있을 것이다.
- 시도:
  - `/Users/user/Downloads` 의 `maruminyahangul_12x12.png`, `Galmuri11_12x12.png`, `GalmuriMono11_12x12.png` 를 프로젝트의 `third_party/font_atlases/` 와 `third_party/font_atlases/finalists/` 로 복사했다.
  - 각 PNG 의 실제 크기와 tile grid 를 확인했다.
- 결과:
  - 세 파일 모두 `768 x 2100`, `12x12`, `64`열로 읽혔다.
  - 전체 tile 수는 `64 x 175 = 11200` 으로, `11172` 완성형 한글을 담기에 충분했다.
- 판정: `성공`
- 교훈: 최종 후보군은 giant 문자 목록을 따로 붙이지 않아도, `가..힣` row-major atlas 규칙만 맞으면 바로 project-local truth source 로 사용할 수 있다.

### 실험 87

- 가설: 이전에 만든 `intro_full` 테스트는 사용자가 실제로 처음 보는 "시작 직후 첫 화면" 비교용으로도 충분할 것이다.
- 시도:
  - 사용자가 "확장 번역인데 첫 화면이 똑같다"고 보고한 뒤, `translation_workset_intro_full_test.json` 의 적용 위치를 다시 확인했다.
- 결과:
  - `intro_full` 세트는 첫 카드 자체를 바꾼 것이 아니라, 첫 카드 뒤에 이어지는 인트로 문장/리오르/호명까지 추가한 세트였다.
  - 그래서 첫 화면만 보면 기존 startup intro 와 동일해 보이는 것이 맞았다.
- 판정: `실패`
- 교훈: 폰트 비교 QA 는 "뒤쪽 인트로까지 넓힌 세트"가 아니라 **사용자가 즉시 보는 첫 카드 자체**를 바꾸는 전용 showcase 세트가 필요하다.

### 실험 88

- 가설: 첫 카드 `4`줄을 비교용 한글 문장으로 바꾼 startup showcase 세트를 만들면, 최종 후보 `3`개를 같은 조건에서 즉시 비교할 수 있다.
- 시도:
  - [translation_workset_startup_font_showcase.json](/Users/user/test/confirmed_data/translation_worksets/translation_workset_startup_font_showcase.json) 을 만들었다.
  - [build_startup_intro_from_atlas.sh](/Users/user/test/scripts/build_startup_intro_from_atlas.sh) 가 임의 translation JSON 을 받을 수 있게 수정했다.
  - [build_finalist_startup_tests.py](/Users/user/test/scripts/build_finalist_startup_tests.py) 를 이 showcase 세트 기준으로 동작하게 바꾸고, 후보 `3`개 ROM 을 일괄 생성했다.
- 결과:
  - 다음 `3`개 비교 ROM 이 생성되었다.
    - [hnr_startup_intro_maruminyahangul12.gba](/Users/user/test/patched_roms/font_compare/maruminyahangul12/hnr_startup_intro_maruminyahangul12.gba)
    - [hnr_startup_intro_galmuri11_12px.gba](/Users/user/test/patched_roms/font_compare/galmuri11_12px/hnr_startup_intro_galmuri11_12px.gba)
    - [hnr_startup_intro_galmurimono12_12px.gba](/Users/user/test/patched_roms/font_compare/galmurimono12_12px/hnr_startup_intro_galmurimono12_12px.gba)
  - 각 ROM 모두 첫 카드 `4`줄이 교체되는 것으로 build report 가 확인되었다.
- 판정: `성공`
- 교훈: 사용자가 바로 보는 첫 화면을 기준으로 같은 문자열을 깔아야, 폰트 차이를 가장 빠르고 공정하게 비교할 수 있다.

### 실험 89

- 가설: 사용자가 준 bitmap atlas 는 이미 `흰 본체 + 회색 그림자` 를 포함하므로, importer 에서 이를 이진화하면 원본보다 흐리고 납작하게 보일 것이다.
- 시도:
  - atlas 원본 픽셀을 확인해 실제 RGB 값이 `(255,255,255)` 본체, `(123,123,123)` 그림자, `(0,0,0)` 배경으로 구성되어 있음을 확인했다.
  - [import_hangul_syllable_atlas.py](/Users/user/test/scripts/import_hangul_syllable_atlas.py) 를 수정해 bright pixel 을 `34` 하나로 뭉개지 않고, source atlas 의 grayscale 값을 그대로 PGM 으로 보존하게 했다.
  - atlas 기반 build script 의 glyph audit 허용값도 `0,123,255` 로 바꿨다.
  - 이후 후보 `3`개 startup showcase ROM 을 다시 빌드했다.
- 결과:
  - raw atlas 픽셀은 실제로 `흰 본체(255) / 회색 그림자(123) / 검정 배경(0)` 구성이었다.
  - 하지만 이 값을 그대로 fnt 로 넣으면, 이 화면 팔레트에서는 중간 단계가 회색이 아니라 **파란색 계열** 로 매핑되었다.
- 판정: `부분 실패`
- 교훈: atlas 의 RGB 값을 그대로 보존하는 것과, 게임이 실제 사용하는 **팔레트 index 단계** 를 맞추는 것은 다르다.

### 실험 90

- 가설: startup intro 화면의 원본 일본어 glyph 는 `0 / 17 / 34` 단계만 쓰므로, atlas 도 "본체/그림자 역할"을 이 단계로 강제 매핑해야 원본과 같은 계열 색으로 나온다.
- 시도:
  - 원본 glyph `大 / 陸 / 年 / 月 / 村` 을 직접 덤프해 pixel value 를 확인했다.
  - 모두 `0 / 17 / 34` 만 쓰는 것을 확인했다.
  - [import_hangul_syllable_atlas.py](/Users/user/test/scripts/import_hangul_syllable_atlas.py) 를 수정해 source atlas 의 밝은 픽셀은 `34`, 중간 톤 픽셀은 `17`, 배경은 `0` 으로 맵핑하게 바꿨다.
  - atlas 기반 build script 의 glyph audit 허용값도 다시 `0,17,34` 로 맞췄다.
- 결과:
  - 새 workbench glyph 는 실제로 `0 / 17 / 34` 값만 사용했다.
  - 즉 흰 본체와 그림자 역할이 게임 원본 intro glyph 와 같은 단계로 정렬되었다.
- 판정: `성공`
- 교훈: bitmap atlas 의 shadow color 는 그 RGB 자체가 중요한 게 아니라, **게임 내 목표 palette index 단계에 어떤 역할로 맵핑되느냐** 가 더 중요하다.

### 실험 91

- 가설: startup 폰트 비교는 넓은 한글 범위보다 먼저, 원문 의미를 유지한 첫 카드 번역으로 보는 편이 사용자 판단에 더 적합하다.
- 시도:
  - [translation_workset_startup_font_showcase.json](/Users/user/test/confirmed_data/translation_worksets/translation_workset_startup_font_showcase.json) 을 `대륙력 / 1910년 2월 / 리젠불 마을 / 형 11세 동생 10세` 로 바꿨다.
  - [build_finalist_startup_tests.py](/Users/user/test/scripts/build_finalist_startup_tests.py) 가 빌드된 `3`개 GBA 를 [finalists](/Users/user/test/patched_roms/font_compare/finalists) 폴더로 한 번 더 모으도록 수정했다.
- 결과:
  - 비교 대상은 여전히 후보 `3`개지만, 이제 첫 화면의 내용도 원문 의미와 맞고 결과 GBA 도 한 폴더에서 바로 열 수 있게 되었다.
- 판정: `성공`
- 교훈: 폰트 비교 ROM 은 문장 의미까지 크게 바꾸기보다, **원문 의미를 유지한 상태에서 폰트만 비교 가능하게** 만드는 편이 사용자가 판단하기 쉽다.

### 실험 92

- 가설: startup intro 화면에서 사용자가 본 "회색/흰색이 뒤집힌 느낌"은 단계 수 부족이 아니라, 실제 팔레트 역할에서 `17` 과 `34` 의 의미를 반대로 넣었기 때문일 수 있다.
- 시도:
  - 원본 glyph 가 `0 / 17 / 34` 단계를 쓴다는 사실은 유지하되, atlas importer 에서 밝은 본체를 `17`, 그림자 톤을 `34` 로 바꾸었다.
  - startup showcase 문구도 원문 의미와 레이아웃을 더 따르도록 `대륙력 / １９１０년　２월 / 　　리젠불 마을 / 형１１세　　동생１０세` 쪽으로 다시 맞췄다.
  - 후보 `3`개 ROM 을 다시 빌드하고, 한 폴더 [finalists](/Users/user/test/patched_roms/font_compare/finalists) 로 수집했다.
- 결과:
  - 새 workbench 는 여전히 `0 / 17 / 34` 만 사용하지만, 역할은 `본체=17`, `그림자=34` 로 뒤집혔다.
  - 첫 카드 `4`줄은 모두 `in_place` 로 다시 반영되었다.
- 판정: `성공`
- 교훈: 같은 단계값이라도 실제 화면 팔레트에서 어느 단계가 더 밝게 보이는지까지 맞춰야, 본체/그림자 관계가 원본과 같은 느낌으로 나온다.
