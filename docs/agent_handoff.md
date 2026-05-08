# Agent Handoff

이 문서는 **지금 바로 다음 에이전트가 이어서 할 일**만 짧게 정리한 문서다.

전체 상태는 [project_control_tower.md](/Users/user/test/docs/project_control_tower.md), 시작 규칙은 [session_start.md](/Users/user/test/docs/session_start.md) 를 따른다.

## 현재 작업 초점

- 메인 초점: `데이터 구조 조사`
- 동반 초점: `텍스트 추출 범위 확대`

## 지금 가장 중요한 사실

- `0x17C1C0` 은 `length-pointer` 레이아웃의 예외적 디스크립터 테이블이다.
- `0x076530` 부근에는 여러 상위 레지스트리 경계를 가리키는 포인터 허브가 있다.
- `0x17785C` 레지스트리에는 실제 Thumb accessor `0x03BC`, `0x0414` 가 존재한다.
- `0x17CE0` 는 `(base, x, y)` 를 받아 `base + 2 * (x + y * 32)` 목적지 주소를 계산하는 helper 로 보인다.
- `0x17EB4` / `0x017ED8` / `0x017EEC` 는 같은 index 에 대해 포인터/길이를 읽은 뒤 DMA3 (`0x040000D4/0xD8/0xDC`) 로 halfword 복사를 시작하는 공용 루틴으로 보인다.
- 따라서 `0x17785C` 의 `pointer+length` 경로는 적어도 이 호출부에서는 텍스트가 아니라 그래픽/타일맵 리소스 쪽일 가능성이 높다.
- 일부 메뉴/진행 메시지는 일반 `00` 종단 평문이 아니라 명령 스트림 내부 문자열이다.

## 다음 한 단계 후보

1. `0x007578`, `0x007760`, `0x007824` 같은 `0x03BC` 단독 호출부를 더 해석해 `포인터만 쓰는 경로` 의 의미를 확인
2. `0x076530` 허브를 참조하는 상위 코드/데이터를 찾기
3. 대사/이벤트 평문 구간을 추가로 찾기

매 실행에서는 위 셋 중 **하나만** 고른다.

## 이 작업에 바로 필요한 문서

- [current_constraints.md](/Users/user/test/analysis/current_constraints.md)
- [data_structure_investigation.md](/Users/user/test/docs/tracks/data_structure_investigation.md)
- [text_extraction_progress.md](/Users/user/test/docs/tracks/text_extraction_progress.md)

## 필요할 때만 읽는 참고 문서

- 리소스 레지스트리 구조: [resource_registry_map.md](/Users/user/test/analysis/resource_registry_map.md)
- accessor 함수 메모: [registry_accessor_helpers.md](/Users/user/test/analysis/registry_accessor_helpers.md)
- 리소스 청크 예외 테이블: [resource_chunk_directory.md](/Users/user/test/analysis/resource_chunk_directory.md)
- 전체 참고 맵: [reference_map.md](/Users/user/test/docs/reference_map.md)

## 작업 규칙

1. ROM 바이너리는 커밋하지 않는다.
2. `.gba` ignore 상태를 유지한다.
3. 같은 실패 가설을 조건 변화 없이 반복하지 않는다.
4. 한 번에 큰 점프보다 검증 가능한 작은 단계 하나를 끝낸다.
5. 의미 있는 진전 뒤에는 총괄 문서, 관련 트랙 문서, 제약 요약, 실험 로그를 갱신한다.
