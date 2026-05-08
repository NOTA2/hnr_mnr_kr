# Repeat Mistake Prevention

이 문서는 **항상 유지되는 공통 운영 규칙**만 담는다.

현재 프로젝트 전용 함정과 금지 가정은 [current_constraints.md](/Users/user/test/analysis/current_constraints.md) 에서 본다.

## 핵심 규칙

1. 추측과 확인된 사실을 섞지 않는다.
2. 실패한 시도는 반드시 기록한다.
3. 같은 실험을 다시 할 때는 무엇이 달라졌는지 적는다.
4. 한 단계에서 하나의 의미 있는 진전만 만든다.
5. 구조 해석이 바뀌면 관련 문서와 로그를 같이 갱신한다.

## 작업 전 최소 체크

1. [session_start.md](/Users/user/test/docs/session_start.md)
2. [agent_handoff.md](/Users/user/test/docs/agent_handoff.md)
3. [current_constraints.md](/Users/user/test/analysis/current_constraints.md)
4. 현재 활성 트랙 문서만

기본적으로는 **전체 실험 로그나 모든 분석 문서를 처음부터 다 읽지 않는다.**

## 작업 후 최소 체크

1. [project_control_tower.md](/Users/user/test/docs/project_control_tower.md)
2. 관련 트랙 문서 최소 1개
3. [current_constraints.md](/Users/user/test/analysis/current_constraints.md)
4. [experiment_log.md](/Users/user/test/analysis/experiment_log.md)
5. 필요 시 [initial_findings.md](/Users/user/test/analysis/initial_findings.md)

## 언제 전체 로그를 읽는가

- 현재 작업이 이전 실패와 강하게 겹칠 때
- 구조 해석이 충돌해서 과거 판단 근거를 다시 확인해야 할 때
- 장기 흐름을 정리하거나 문서를 재구성할 때

그 외에는 [experiment_log.md](/Users/user/test/analysis/experiment_log.md) 를 참고용으로만 사용한다.
