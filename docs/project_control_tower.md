# Project Control Tower

이 문서는 **작업 후 갱신하는 총괄 현황판**이다.

매 세션의 시작점은 이 문서가 아니라 [session_start.md](/Users/user/test/docs/session_start.md) 이다.

## 현재 단계

- 메인 단계: `데이터 구조 조사 + 텍스트 추출`
- 보조 단계: `텍스트 재삽입 기반 유지`
- 대기 단계: `폰트/문자폭`, `이미지 리소스`, `GUI`

## 현재 활성 트랙

- [data_structure_investigation.md](/Users/user/test/docs/tracks/data_structure_investigation.md)
- [text_extraction_progress.md](/Users/user/test/docs/tracks/text_extraction_progress.md)

## 현재 최우선 과제

1. `0x0002CC` / `0x000304` generic hub accessor 호출부에서 registry selector 값 분류
2. `0x093D` / `0x093E` / `0x094B` 고정 인덱스 리소스와 주변 helper 의미를 더 분리
3. 대사/이벤트 평문 구간 추가 탐색
4. 폰트 조사로 넘어갈 수 있을 만큼 텍스트 구조를 더 분리

## 단계 상태

- 데이터 구조 조사: `IN PROGRESS`
- 텍스트 추출: `IN PROGRESS`
- 텍스트 재삽입: `BOOTSTRAPPED`
- 폰트/문자 매핑: `NOT STARTED`
- 이미지 리소스: `NOT STARTED`
- GUI/작업 워크플로우: `DEFERRED`

## 최근 검증된 핵심 진전

- `0x17C1C0` 테이블이 `length-pointer` 레이아웃이라는 점 확인
- `0x076530` 부근 상위 포인터 허브와 여러 `pointer-length` 레지스트리 범위 확인
- `0x17785C` 레지스트리 accessor (`0x03BC`, `0x0414`) 와 호출자 목록 확인
- `0x17CE0` 가 `base + 2 * (x + y * 32)` 목적지 계산 helper 임을 확인
- `0x17EB4` / `0x017ED8` / `0x017EEC` 경로가 `0x17785C` 엔트리를 DMA3 (`0x040000D4/0xD8/0xDC`) 로 복사하는 공용 루틴임을 확인
- `0x007760` / `0x007824` 단독 accessor 경로가 각각 `0x093D -> 0x3D2A40`, `0x093E -> 0x3D2D60` 고정 리소스 엔트리를 읽는다는 점 확인
- `0x3D2D60` 재료 뱅크 앞쪽에 `5바이트 메타데이터 + u16 상대 문자열 오프셋` 7바이트 레코드 구간이 있고, 뒤쪽에 `cp932` 문자열이 이어진다는 점 확인
- `0x007578` 단독 accessor 경로가 `0x094B -> 0x3DDB30` binary table 을 읽으며 직접 평문 문자열 경로는 아니라는 점 확인
- `0x076530` 허브를 직접 가리키는 포인터가 `0x0002C0` literal 하나뿐이며, 이 값이 `0x000290` helper 의 상위 registry selector 로 쓰인다는 점 확인
- `0x0002CC` / `0x000304` 가 `0x000290` 위에 쌓인 generic `pointer-length` accessor 로 보이며, 각각 selected registry 의 포인터/길이 필드를 반환한다는 점 확인
- 세이브/진행 메뉴 텍스트와 크레딧 텍스트 추출

## 작업 후 최소 갱신 규칙

의미 있는 진전이 있었다면 아래는 항상 갱신한다.

1. 이 문서
2. 관련 트랙 문서 최소 1개
3. [current_constraints.md](/Users/user/test/analysis/current_constraints.md)
4. [experiment_log.md](/Users/user/test/analysis/experiment_log.md)
5. 필요 시 [initial_findings.md](/Users/user/test/analysis/initial_findings.md)

## 읽기 규칙

- 시작할 때 이 문서를 먼저 읽지 않는다.
- 현재 단계만 빠르게 확인하거나, 작업 후 상태를 갱신할 때 사용한다.
- 어떤 참고 문서를 열어야 할지 모르면 [reference_map.md](/Users/user/test/docs/reference_map.md) 를 본다.
