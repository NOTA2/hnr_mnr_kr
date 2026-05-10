# Session Start

이 파일은 **매 세션의 유일한 시작점**이다.

목표는 시작 컨텍스트를 작게 유지하고, 필요한 문서만 추가로 여는 것이다.

## 읽기 순서

기본으로는 아래 2개만 읽는다.

1. 이 문서
2. [active_task.md](/Users/user/test/docs/active_task.md)

그 외 문서는 [active_task.md](/Users/user/test/docs/active_task.md) 가 명시한 경우에만 연다.

## 기본 금지

- 시작하자마자 [agent_handoff.md](/Users/user/test/docs/agent_handoff.md), [current_constraints.md](/Users/user/test/analysis/current_constraints.md), 트랙 문서, 전체 JSON, [experiment_log.md](/Users/user/test/analysis/experiment_log.md) 를 읽지 않는다.
- 큰 JSON은 사람이 훑지 않는다. 필요한 값만 `python3 -m gba_kor_tool ...` 또는 짧은 스크립트로 조회한다.
- 같은 가설을 반복할 때는 무엇이 달라졌는지 먼저 기록한다.

## 현재 단계

- 메인: `폰트/문자 매핑 + 첫 한글 문자열 테스트 확장`
- 병행: `텍스트 추출 coverage 유지`, `text cluster 정리`
- 보류: `이미지`, `GUI`

## 실행 규칙

- 한 번의 실행에서 의미 있는 next step 하나를 끝낸다.
- 시작 경로에서 읽은 내용만으로 부족할 때만 참고 문서를 추가로 연다.
- 구조 해석이 바뀌면 새 사실과 금지 가정을 짧게 남긴다.

## 작업 후 갱신

의미 있는 진전이 있으면 아래만 우선 갱신한다.

1. [active_task.md](/Users/user/test/docs/active_task.md)
2. 현재 작업과 직접 관련된 분석 문서 1개
3. [experiment_log.md](/Users/user/test/analysis/experiment_log.md) 끝에 실험 1개 append

[project_control_tower.md](/Users/user/test/docs/project_control_tower.md) 는 단계/우선순위가 바뀐 경우에만 갱신한다.
