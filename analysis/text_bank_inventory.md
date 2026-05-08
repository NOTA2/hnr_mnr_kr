# Text Bank Inventory

현재까지 확인된 주요 일본어 평문 텍스트 뱅크 목록입니다.

## 직접 포인터가 확인된 뱅크

### 시스템 메시지

- 범위: `0x088540` ~ `0x088620`
- 파일: [system_messages.json](/Users/user/test/analysis/system_messages.json)
- 특징: 통신/에러 메시지
- 포인터 예시: `0x0885F4 -> 0x088558`

### 아이템/이벤트 문자열

- 범위: `0x08AEFC` ~ `0x08B400`
- 파일: [item_texts.json](/Users/user/test/analysis/item_texts.json)
- 특징: 이벤트 증표, 부품, 전달 아이템
- 포인터 예시: `0x18328C -> 0x08AF70`

### 지역명

- 범위: `0x18425C` ~ `0x1843F3`
- 파일: [location_texts.json](/Users/user/test/analysis/location_texts.json)
- 특징: 도시/맵/던전 이름
- 포인터 예시:
  - `0x06A574 -> 0x18425C`
  - `0x06A9A8 -> 0x18425C`
  - `0x08C06C -> 0x18425C`
  - `0x08C0C4 -> 0x18425C`

### 크레딧(타이틀) 텍스트

- 범위: `0x08C3AC` ~ `0x08CE00`
- 파일: [credits_texts.json](/Users/user/test/analysis/credits_texts.json)
- 특징: 크레딧 화면에서 쓰이는 직책/회사/이름 문자열
- 포인터 예시: `0x184E20 -> 0x08C3AC`

## 직접 포인터가 아직 안 잡힌 뱅크

### 전투 기술명/설명

- 범위: `0x3D2036` ~ `0x3D2557`
- 파일: [battle_texts.json](/Users/user/test/analysis/battle_texts.json)
- 특징: 기술명과 설명이 순차적인 0종단 문자열 목록으로 저장됨
- 주의: 문자열 내부에 `0x0B` 제어 코드가 섞여 있음
- 현재 추출 수: `104`
- 상태: 절대 포인터 미확인

### 대형 기술/능력 텍스트 뱅크

- 범위: `0x3D327E` ~ `0x3D6277`
- 파일: [ability_texts.json](/Users/user/test/analysis/ability_texts.json)
- 특징: `이름+0x0B+설명` 형태의 순차적인 0종단 문자열 목록
- 주의: 문자열 내부에 `0x0B` 제어 코드가 섞여 있음
- 현재 추출 수: `409`
- 상태: 절대 포인터 미확인

### 재료/속성 텍스트

- 범위: `0x3D2D60` ~ `0x3D3420`
- 파일: [material_texts.json](/Users/user/test/analysis/material_texts.json)
- 특징: 재료명/속성명과 설명이 결합된 문자열
- 주의: 문자열 내부에 `0x0B` 제어 코드와 전각 공백 패딩이 섞여 있음
- 현재 추출 수: `43`
- 상태: 청크 디렉터리 내부 한 섹션으로 보임

## 별도 UI 텍스트 뱅크

### UI 기술 텍스트

- 범위: `0x08B62C` ~ `0x08B809`
- 파일: [ui_skill_texts.json](/Users/user/test/analysis/ui_skill_texts.json)
- 특징: `0x3D2059` 계열과 일부 명칭이 겹치지만 설명 문장이 다름
- 해석: 메뉴/UI 전용 문자열 복제본일 가능성 있음

## 명령 스트림 내부 텍스트

### 세이브/진행 관련 메뉴 메시지

- 블록 범위: `0x772E00` ~ `0x773260`
- 파일: [save_menu_texts.json](/Users/user/test/analysis/save_menu_texts.json)
- 특징:
  - `00` 종단 평문 덩어리 형태가 아니라, 명령/파라미터 바이트 사이에 `cp932` 텍스트가 삽입된 형태로 보임
  - 문자열 종단/구분 바이트로 `0x10` 사용 사례 확인

### Registry D 튜토리얼/이벤트 대사

- 테이블 범위: `0x17C7E4` ~ `0x17CB04`
- 물리 범위: `0x7F3000` ~ `0x7F96E9`
- 파일:
  - [registry_d_full_sliding_texts.json](/Users/user/test/analysis/registry_d_full_sliding_texts.json)
  - [translation_workset_registry_d_dialogue.json](/Users/user/test/analysis/translation_workset_registry_d_dialogue.json)
- 특징:
  - `pointer-length` Registry D 엔트리 안에 command byte 와 함께 대사가 섞여 있다.
  - `scan-text --sliding` + terminator `0x0D/0x0C/0x00` 로 현재 `305`개 문자열을 회수했다.
  - 튜토리얼 설명, 전투 개시 대사, 이벤트성 짧은 문장이 다수 포함된다.
  - 넓은 범위 스캔에서는 기본 `--limit 100` 때문에 일부만 보일 수 있으므로 limit 명시가 필요하다.

### Registry A entry 8 command-stream 대사/메뉴 bank

- 범위: `0x6B594C` ~ `0x772E58`
- 파일:
  - [registry_a_entry8_terminator_10_texts.json](/Users/user/test/analysis/registry_a_entry8_terminator_10_texts.json)
  - [terminator_10_late_dialogue_hits.json](/Users/user/test/analysis/terminator_10_late_dialogue_hits.json)
- 특징:
  - `0x10` 종단 기준 슬라이딩 스캔으로 대사/이벤트/메뉴 문자열이 대량 회수된다.
  - 현재 추출은 `1200`건에서 limit 에 걸린 상태다.
  - `0x772E00` save menu block 도 같은 entry 안쪽에 포함된다.
  - 현재는 **대형 mixed script bank** 로 보는 해석이 가장 강하다.

## 현재 해석

- 이 게임은 일본어 평문이 여러 군데에 분산 저장되어 있다.
- 모든 텍스트가 같은 참조 방식을 쓰지 않는 것으로 보인다.
- 즉, 한 개의 "통합 텍스트 삽입 규칙"만으로 끝나지 않을 가능성이 높다.
- 한글화는 텍스트 뱅크별로 처리 전략을 나눠야 할 수 있다.
- `0x3Dxxxx` 일부 뱅크는 포인터 테이블보다는 순차적 레코드 배열일 가능성이 높다.
- `0x17C1C0` 부근에는 `u32 length + u32 rom_address` 리소스 디스크립터 테이블이 있다.
- 이 테이블은 일부 엔트리가 서로 겹치므로, `battle_texts` / `ability_texts` 범위를 단순한 청크 경계로 오해하면 안 된다.
- 현재 추출 JSON들은 번역 작업 편의를 위해 묶은 보기용 데이터셋이며, 실제 디스크립터 경계와 1:1 대응하지 않을 수 있다.
