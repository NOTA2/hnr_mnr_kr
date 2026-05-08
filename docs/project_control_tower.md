# Project Control Tower

이 문서는 프로젝트 전체 진행 상황을 한눈에 보는 총괄 현황판입니다.

새 세션이나 새 에이전트는 이 문서를 가장 먼저 읽고, 그 다음 관련 트랙 문서로 이동합니다.

반복 실수 방지를 위해 아래 문서도 함께 확인합니다.

- [repeat_mistake_prevention.md](/Users/user/test/docs/repeat_mistake_prevention.md)
- [experiment_log.md](/Users/user/test/analysis/experiment_log.md)

## 현재 결론

현재는 아래 두 단계를 동시에 진행 중입니다.

1. 데이터 구조 조사
2. 텍스트 추출

이유:

- 텍스트를 추출하면서 저장 구조를 같이 파악할 수 있기 때문입니다.
- 어떤 텍스트 뱅크는 일반 포인터가 잡히고, 어떤 뱅크는 별도 참조 구조를 쓰는지 같은 정보는 두 작업이 함께 진행될 때 가장 빨리 드러납니다.

## 전체 단계 상태

### 1. 데이터 구조 조사

- 상태: `IN PROGRESS`
- 현재 판단:
  - 일부 문자열은 `cp932 + 00 terminator` 평문
  - 일부 뱅크는 절대 포인터 확인
  - 일부 대형 뱅크는 절대 포인터 미확인
  - `0x0B` 제어 코드 사용 확인
  - `0x17C1C0` 부근 `u32 length + u32 rom_address` 디스크립터 테이블 확인
  - 해당 테이블은 겹치는 엔트리를 포함
  - `0x076530` 부근에서 여러 상위 리소스 레지스트리 경계를 가리키는 포인터 허브 확인
  - 상위 레지스트리들은 주로 `pointer-length`, `0x17C1C0` 은 예외적으로 `length-pointer`
  - `0x17785C` 레지스트리를 읽는 Thumb accessor (`0x03BC`, `0x0414`) 확인
- 상세 문서: [data_structure_investigation.md](/Users/user/test/docs/tracks/data_structure_investigation.md)

### 2. 텍스트 추출

- 상태: `IN PROGRESS`
- 현재 판단:
  - 시스템 메시지, 아이템, 지역명, 전투 기술, 능력, UI 기술 텍스트 추출본 확보
  - 추출 가능한 텍스트 뱅크가 계속 늘어나는 중
  - 디스크립터 테이블과 별도로 보기 쉬운 번역용 JSON 묶음을 유지 중
- 상세 문서: [text_extraction_progress.md](/Users/user/test/docs/tracks/text_extraction_progress.md)

### 3. 텍스트 재삽입

- 상태: `BOOTSTRAPPED`
- 현재 판단:
  - 제자리 덮어쓰기 가능
  - 자유 공간 주입 및 포인터 갱신 기본 기능 있음
  - 게임별 예외 규칙은 아직 조사 필요
- 상세 문서: [text_reinsertion_progress.md](/Users/user/test/docs/tracks/text_reinsertion_progress.md)

### 4. 폰트/문자 매핑

- 상태: `NOT STARTED`
- 현재 판단:
  - 조사 도구는 준비됨
  - 폰트 타일 위치, 폭 테이블, 한글 추가 방식은 아직 미확정
- 상세 문서: [font_and_encoding_progress.md](/Users/user/test/docs/tracks/font_and_encoding_progress.md)

### 5. 이미지 리소스

- 상태: `NOT STARTED`
- 현재 판단:
  - 추후 별도 축으로 조사 예정
- 상세 문서: [image_resource_progress.md](/Users/user/test/docs/tracks/image_resource_progress.md)

### 6. GUI/작업 워크플로우

- 상태: `DEFERRED`
- 현재 판단:
  - 내부 엔진과 데이터 구조가 더 안정화된 뒤 진행
- 상세 문서: [tooling_and_gui_progress.md](/Users/user/test/docs/tracks/tooling_and_gui_progress.md)

## 현재 가장 중요한 포인트

1. `0x007578`, `0x007760`, `0x017ED8`, `0x017EEC` 같은 accessor 호출부 해석
2. `0x076530` 포인터 허브를 누가 참조하는지 파악
3. 대사/이벤트 평문 구간 추가 탐색
4. 폰트 조사로 넘어갈 수 있을 만큼 텍스트 구조를 더 분리

## 최근 주요 진전

### 2026-05-08

- ROM 조사용 CLI 작업대 구축
- 문자열 스캔, 범위 추출, 포인터 탐색, 일괄 번역 적용 기본 기능 추가
- `scan-text` 에 범위 제한 + 슬라이딩 스캔 옵션 추가 (명령 스트림 내 텍스트 추출용)
- 시스템 메시지, 아이템/이벤트 문자열 추출
- 지역명 텍스트 뱅크 확인
- 전투 기술/설명 텍스트 뱅크 확인
- 대형 능력 텍스트 뱅크 확인
- UI 기술 텍스트 뱅크 확인
- 세이브/진행 관련 메뉴 메시지 블록(`0x772E00..0x773260`)에서 `cp932 + terminator 0x10` 문자열 `5`개 추출
- 크레딧(타이틀) 텍스트 뱅크(`0x08C3AC..0x08CE00`)에서 문자열 `10`개 추출 및 포인터(`0x184E20`) 확인
- 일부 뱅크는 일반 절대 포인터가 확인되지만, `0x3Dxxxx` 대형 뱅크는 다른 참조 구조일 가능성 확인
- 총괄 현황판, 트랙 문서, 반복 실수 방지 규칙, 실험 로그 체계 추가
- `0x3Dxxxx` 뱅크가 순차 문자열 레코드 구조에 가깝다는 근거 확보
- 전각 공백 필터 문제를 수정해 `battle/ability` 추출 누락을 회수
- `inspect-chunk-table` 명령 추가
- `0x17C1C0` 부근 테이블이 `u32 length + u32 rom_address` 형식임을 확인
- 디스크립터 엔트리들이 서로 겹친다는 점을 확인
- `material_texts.json` 별도 추출
- `resource_chunks.json` 생성
- `0x076530` 부근 상위 포인터 허브와 `0x17C2F4/0x17C384/0x17C71C/0x17C7E4` 레지스트리 경계 확인
- `resource_registry_map.md`, `resource_registry_summary.json` 생성
- `find-thumb-bl` 명령 추가
- `0x17785C` 레지스트리의 Thumb accessor (`0x03BC`, `0x0414`) 호출자 목록 생성

## 세션 시작 규칙

새 세션에서 시작할 때 순서는 항상 아래와 같습니다.

1. 이 문서를 읽는다.
2. [repeat_mistake_prevention.md](/Users/user/test/docs/repeat_mistake_prevention.md) 를 읽는다.
3. [experiment_log.md](/Users/user/test/analysis/experiment_log.md) 를 읽는다.
4. 현재 `IN PROGRESS` 상태인 트랙 문서를 읽는다.
5. [docs/agent_handoff.md](/Users/user/test/docs/agent_handoff.md) 를 읽는다.
6. 한 번에 한 가지 의미 있는 진전만 만든다.
7. 작업 후 이 문서와 관련 트랙 문서를 갱신한다.

## 문서 갱신 규칙

의미 있는 작업이 있었으면 항상 아래를 갱신합니다.

1. 이 문서
2. 관련 트랙 문서 1개 이상
3. [analysis/experiment_log.md](/Users/user/test/analysis/experiment_log.md)
4. 필요 시 [analysis/initial_findings.md](/Users/user/test/analysis/initial_findings.md)

## 관련 문서

- [docs/agent_handoff.md](/Users/user/test/docs/agent_handoff.md)
- [docs/korean_localization_workflow.md](/Users/user/test/docs/korean_localization_workflow.md)
- [docs/repeat_mistake_prevention.md](/Users/user/test/docs/repeat_mistake_prevention.md)
- [analysis/text_bank_inventory.md](/Users/user/test/analysis/text_bank_inventory.md)
- [analysis/experiment_log.md](/Users/user/test/analysis/experiment_log.md)
- [analysis/resource_chunk_directory.md](/Users/user/test/analysis/resource_chunk_directory.md)
- [analysis/resource_chunks.json](/Users/user/test/analysis/resource_chunks.json)
- [analysis/resource_registry_map.md](/Users/user/test/analysis/resource_registry_map.md)
- [analysis/resource_registry_summary.json](/Users/user/test/analysis/resource_registry_summary.json)
- [analysis/registry_accessor_helpers.md](/Users/user/test/analysis/registry_accessor_helpers.md)
