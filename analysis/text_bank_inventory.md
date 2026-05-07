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

## 직접 포인터가 아직 안 잡힌 뱅크

### 전투 기술명/설명

- 범위: `0x3D2059` ~ `0x3D251A`
- 파일: [battle_texts.json](/Users/user/test/analysis/battle_texts.json)
- 특징: 기술명과 짧은 설명이 섞여 있음
- 주의: 문자열 내부에 `0x0B` 제어 코드가 섞여 있음
- 상태: 절대 포인터 미확인

### 대형 기술/능력 텍스트 뱅크

- 범위: `0x3D329C` ~ `0x3D6277`
- 파일: [ability_texts.json](/Users/user/test/analysis/ability_texts.json)
- 특징: 기술명, 기술 설명, 아이템성 설명문 다수 포함
- 주의: 문자열 내부에 `0x0B` 제어 코드가 섞여 있음
- 상태: 절대 포인터 미확인

## 별도 UI 텍스트 뱅크

### UI 기술 텍스트

- 범위: `0x08B62C` ~ `0x08B809`
- 파일: [ui_skill_texts.json](/Users/user/test/analysis/ui_skill_texts.json)
- 특징: `0x3D2059` 계열과 일부 명칭이 겹치지만 설명 문장이 다름
- 해석: 메뉴/UI 전용 문자열 복제본일 가능성 있음

## 현재 해석

- 이 게임은 일본어 평문이 여러 군데에 분산 저장되어 있다.
- 모든 텍스트가 같은 참조 방식을 쓰지 않는 것으로 보인다.
- 즉, 한 개의 "통합 텍스트 삽입 규칙"만으로 끝나지 않을 가능성이 높다.
- 한글화는 텍스트 뱅크별로 처리 전략을 나눠야 할 수 있다.
