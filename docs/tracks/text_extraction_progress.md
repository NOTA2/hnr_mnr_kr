# Text Extraction Progress

읽기 규칙: 이 문서는 현재 활성 트랙이므로 세션 시작 시 읽는다.

이 문서는 추출 가능한 텍스트 데이터셋 확보 현황을 기록합니다.

## 목적

- 번역 가능한 JSON 데이터셋을 늘린다.
- 텍스트 뱅크별로 파일을 분리해 관리한다.

## 현재 상태

- 상태: `IN PROGRESS`

## 확보된 추출본

### 시스템 메시지

- 파일: [system_messages.json](/Users/user/test/analysis/system_messages.json)
- 범위: `0x088540` ~ `0x088620`

### 아이템/이벤트 문자열

- 파일: [item_texts.json](/Users/user/test/analysis/item_texts.json)
- 범위: `0x08AEFC` ~ `0x08B400`

### 지역명

- 파일: [location_texts.json](/Users/user/test/analysis/location_texts.json)
- 범위: `0x18425C` ~ `0x1843F3`

### 전투 기술명/설명

- 파일: [battle_texts.json](/Users/user/test/analysis/battle_texts.json)
- 범위: `0x3D2036` ~ `0x3D2557`
- 현재 추출 수: `104`

### 대형 능력 텍스트 뱅크

- 파일: [ability_texts.json](/Users/user/test/analysis/ability_texts.json)
- 범위: `0x3D327E` ~ `0x3D6277`
- 현재 추출 수: `409`

### 재료/속성 텍스트

- 파일: [material_texts.json](/Users/user/test/analysis/material_texts.json)
- 범위: `0x3D2D60` ~ `0x3D3420`
- 현재 추출 수: `43`
- 특징:
  - 뱅크 앞쪽에는 `7-byte` binary record directory 가 있고, 추출된 `cp932` 문자열은 그 뒤쪽 본문 영역에 놓여 있다.

### UI 기술 텍스트

- 파일: [ui_skill_texts.json](/Users/user/test/analysis/ui_skill_texts.json)
- 범위: `0x08B62C` ~ `0x08B809`

### 세이브/진행 관련 메뉴 메시지

- 파일: [save_menu_texts.json](/Users/user/test/analysis/save_menu_texts.json)
- 범위(블록): `0x772E00` ~ `0x773260`
- 특징:
  - 일반적인 `00` 종단 평문 블록이 아니라, **명령 스트림 내부에 박힌 `cp932` 문자열**로 보임
  - 해당 블록에서는 `0x10` 이 문자열 종단(또는 구분) 역할을 하는 것으로 관측됨
  - `extract-range` 로는 잡히지 않아 `scan-text --sliding` 으로 추출함

### 크레딧(타이틀) 텍스트

- 파일: [credits_texts.json](/Users/user/test/analysis/credits_texts.json)
- 범위: `0x08C3AC` ~ `0x08CE00`
- 현재 추출 수: `10`

### 리소스 디스크립터 테이블 덤프

- 파일: [resource_chunks.json](/Users/user/test/analysis/resource_chunks.json)
- 범위: `0x17C1C0` 부근 35개 엔트리
- 용도: 텍스트 JSON 범위와 실제 리소스 디스크립터 관계를 확인하는 기준표

## 현재 해석

- 번역 가능한 텍스트 뱅크는 이미 여러 개 확보되었다.
- 아이템/기술/지역/UI가 서로 다른 파일로 분리되기 시작해서 작업 관리가 쉬워졌다.
- 아직 대사/이벤트 본문 텍스트는 충분히 확보되지 않았다.
- 전각 공백 필터 문제를 수정하면서 `battle/ability` 추출본의 누락 문자열을 회수했다.
- 상위 리소스 청크 기준으로 보았을 때 `material_texts` 라는 별도 텍스트 묶음도 확인되었다.
- `material_texts` 뱅크는 순수 문자열 덩어리가 아니라, 앞단 binary record 와 뒷단 문자열 본문이 결합된 mixed resource 로 보인다.
- 다만 추출 JSON의 범위와 실제 디스크립터 엔트리 범위는 1:1 대응하지 않을 수 있다.
- 넓은 디스크립터 범위를 그대로 스캔하면 잡음이 섞이므로, 번역용 JSON은 계속 사람이 읽기 좋은 단위로 유지하는 편이 낫다.

## 다음 할 일

1. 대사/이벤트 평문 구간을 더 찾기
2. 메뉴 관련 텍스트 뱅크를 더 분리하기
3. 중복 저장되는 문자열 뱅크 관계를 파악하기
4. 추출본별 번역 우선순위를 나누기

## 진행 로그

### 2026-05-08

- 시스템 메시지 추출
- 아이템/이벤트 문자열 추출
- 지역명 추출
- 전투 기술명/설명 추출
- 대형 능력 텍스트 뱅크 추출
- UI 기술 텍스트 추출
- 세이브 관련 메뉴 메시지 추출(명령 스트림 내 `cp932`, 종단 바이트 `0x10`)
- 크레딧(타이틀) 텍스트 추출
- 전투/능력 텍스트 뱅크 시작점과 누락 문자열을 재보정
- 청크 디렉터리 기반으로 재료/속성 텍스트 뱅크를 별도 추출
- `inspect-chunk-table` 로 리소스 디스크립터 테이블 덤프 생성
- `0x3D2D60` 재료 뱅크 앞단에 있는 `7-byte` record directory 를 확인
