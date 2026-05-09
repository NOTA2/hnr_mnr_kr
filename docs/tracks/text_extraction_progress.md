# Text Extraction Progress

읽기 규칙: 텍스트 추출 작업을 직접 할 때만 읽는다. 세션 시작 시 기본으로 읽지 않는다.

이 문서는 추출 가능한 텍스트 데이터셋 확보 현황을 기록합니다.

## 목적

- 번역 가능한 JSON 데이터셋을 늘린다.
- 텍스트 뱅크별로 파일을 분리해 관리한다.

## 현재 상태

- 상태: `IN PROGRESS`

## 작업용 번역 세트

### 코어 UI 세트

- 파일: [translation_workset_core_ui.json](/Users/user/test/analysis/translation_workset_core_ui.json)
- 구성:
  - `system_messages`
  - `save_menu_texts`
  - `location_texts`
  - `ui_skill_texts`
- 레코드 수: `43`
- 목적:
  - 사람이 여러 JSON 파일을 오가지 않고 바로 번역 작업을 시작할 수 있게 하는 첫 workset
  - `save_menu_texts` 처럼 기존에 `translation` 필드가 없던 추출본도 같은 형식으로 정규화

### Registry D 대사 세트

- 파일: [translation_workset_registry_d_dialogue.json](/Users/user/test/analysis/translation_workset_registry_d_dialogue.json)
- 소스: [registry_d_full_sliding_texts.json](/Users/user/test/analysis/registry_d_full_sliding_texts.json)
- 레코드 수: `305`
- 목적:
  - 아직 따로 추출되지 않았던 튜토리얼/전투 전후 대사/이벤트 대사를 번역 가능한 한 파일로 묶기
  - command stream 성격이 섞인 mixed resource 에서도 실제 사람이 읽을 수 있는 텍스트를 바로 작업 세트로 전환

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

### Registry D 튜토리얼/이벤트 대사

- 테이블 범위: `0x17C7E4` ~ `0x17CB04`
- 물리 범위: `0x7F3000` ~ `0x7F96E9`
- 파일:
  - [registry_d_entries_scan.json](/Users/user/test/analysis/registry_d_entries_scan.json)
  - [registry_d_full_sliding_texts.json](/Users/user/test/analysis/registry_d_full_sliding_texts.json)
  - [registry_d_tutorial_dialogue_texts.json](/Users/user/test/analysis/registry_d_tutorial_dialogue_texts.json)
  - [registry_d_battle_dialogue_texts.json](/Users/user/test/analysis/registry_d_battle_dialogue_texts.json)
- 현재 확인:
  - Registry D 전체 물리 범위를 `scan-text --sliding` + terminator `0x0D/0x0C/0x00` 으로 보면 `305`개 텍스트가 잡힌다.
  - 텍스트가 확인된 엔트리는 현재 `81 / 100` 개다.
  - entry `0` / `92` 는 튜토리얼 계열 중복/변형 대사 묶음으로 보인다.
  - entry `33`, `47` 같은 큰 엔트리도 대사성 문자열을 다수 포함한다.
  - 초기 전수 스캔 때는 `scan-text` 기본 `--limit 100` 에 걸려 일부만 보였으므로, 넓은 범위 스캔에서는 반드시 limit 을 올려야 한다.

### Registry A entry 8 mixed script bank

- 상위 entry:
  - registry: `A`
  - index: `8`
  - 범위: `0x6B594C` ~ `0x772E58`
- 파일:
  - [registry_a_entry8_prefixed_texts.json](/Users/user/test/analysis/registry_a_entry8_prefixed_texts.json)
  - [registry_a_entry8_terminator_10_texts.json](/Users/user/test/analysis/registry_a_entry8_terminator_10_texts.json)
  - [terminator_10_late_dialogue_hits.json](/Users/user/test/analysis/terminator_10_late_dialogue_hits.json)
  - [terminator_10_global_hits.json](/Users/user/test/analysis/terminator_10_global_hits.json)
- 현재 확인:
  - 많은 레코드가 `01 FF <u16 문자수>` 헤더 뒤에 `cp932` 본문이 오는 command-stream 구조를 가진다.
  - 이 규칙으로 재추출한 [registry_a_entry8_prefixed_texts.json](/Users/user/test/analysis/registry_a_entry8_prefixed_texts.json) 은 현재 `9811`건이다.
  - 초반 리오르 대사, 진행 힌트, 플래그 미스 디버그성 문구, 후반 이벤트 대사까지 한 규칙으로 연속 회수된다.
  - 기존 `0x10` terminator 슬라이딩 스캔은 `1200`건에서 limit 에 걸렸고, entry 8 발견 및 밀집 구간 확인용 정찰 데이터로 유지한다.
  - `0x6B7B44` 이후로는 리오르/코넬로 초반부처럼 보이는 이벤트 대사가 밀집한다.
  - `0x772E00` save menu block 도 이 entry 안쪽에 포함되므로, entry 8 은 **대사 + 메뉴 + command-stream text** 가 섞인 대형 mixed script bank 후보로 보는 해석이 강하다.
  - `0x10` 종단 전역 스캔은 앞쪽 잡음이 섞이므로, 실제 사용 시에는 entry 8 같은 상위 범위로 좁혀 재스캔하는 편이 안전하다.

### Save/menu prefixed command-stream block

- 범위: `0x772E00` ~ `0x773260`
- 파일:
  - [save_menu_prefixed_texts.json](/Users/user/test/analysis/save_menu_prefixed_texts.json)
  - [save_menu_texts.json](/Users/user/test/analysis/save_menu_texts.json)
- 현재 확인:
  - `save menu` 도 같은 `01 FF <u16 문자수>` 구조로 현재 `12`건이 깔끔하게 잡힌다.
  - 예:
    - `今はアルがいないから`
    - `セーブはできないぞ`
    - `これまでの旅を記録する？`
    - `前の記録に上書きしてもいい？`
  - 따라서 `save_menu_texts.json` 의 `0x10` 종단 스캔본은 발견용/비교용, 실제 작업용 원본은 prefixed 추출본이 더 정확하다.

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
- Registry D 분석으로 본편성 대사/튜토리얼 텍스트가 대량으로 추가 확보되었다.
- Registry A entry 8 분석으로 `0x10` 종단 command-stream 대사 bank 가 훨씬 크게 존재한다는 근거가 생겼고, 지금은 `01 FF <문자수>` 헤더 기반으로 clean extraction 이 가능해졌다.
- 전각 공백 필터 문제를 수정하면서 `battle/ability` 추출본의 누락 문자열을 회수했다.
- 상위 리소스 청크 기준으로 보았을 때 `material_texts` 라는 별도 텍스트 묶음도 확인되었다.
- `material_texts` 뱅크는 순수 문자열 덩어리가 아니라, 앞단 binary record 와 뒷단 문자열 본문이 결합된 mixed resource 로 보인다.
- 다만 추출 JSON의 범위와 실제 디스크립터 엔트리 범위는 1:1 대응하지 않을 수 있다.
- 넓은 디스크립터 범위를 그대로 스캔하면 잡음이 섞이므로, 번역용 JSON은 계속 사람이 읽기 좋은 단위로 유지하는 편이 낫다.

## 다음 할 일

1. `01 FF <문자수>` 규칙이 Registry A entry `8` 외 다른 command-stream 뱅크에도 통하는지 확인하기
2. Registry A entry `8` 의 `9811`건을 장면/용도 기준으로 분할할지 결정하기
3. Registry D `305`개 대사를 장면/용도 기준으로 더 묶기
4. 메뉴 관련 텍스트 뱅크를 더 분리하기

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
