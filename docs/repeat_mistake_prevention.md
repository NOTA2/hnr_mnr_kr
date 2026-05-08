# Repeat Mistake Prevention

이 문서는 **항상 유지되는 공통 운영 규칙**만 담는다.

현재 프로젝트 전용 함정과 금지 가정은 [current_constraints.md](/Users/user/test/analysis/current_constraints.md) 에서 본다.

## 핵심 규칙

1. 추측과 확인된 사실을 섞지 않는다.
2. 실패한 시도는 반드시 기록한다.
3. 같은 실험을 다시 할 때는 무엇이 달라졌는지 적는다.
4. 한 단계에서 하나의 의미 있는 진전만 만든다.
5. 구조 해석이 바뀌면 관련 문서와 로그를 같이 갱신한다.
6. literal pool 근처를 볼 때는 값 주소만 보지 말고, 실제 `ldr` instruction 의 PC-relative target 을 계산한다.
7. 시작 시 읽는 문서는 [session_start.md](/Users/user/test/docs/session_start.md) 와 [active_task.md](/Users/user/test/docs/active_task.md) 로 제한한다.
8. detached binary slice 를 `.org 0` 으로 디스어셈블했을 때는 BL target 을 로컬 오프셋으로 먼저 보고, 필요하면 `actual = slice_start + local_target` 으로 다시 환산한다.
9. helper-family 수준에서 확인한 인자 의미를 특정 caller 경로에 바로 투영하지 않는다. 실제 call site 직전 레지스터 값(`r0..r3`)을 다시 확인한다.

## 컨텍스트 예산 규칙

- `Hot Path`: 매 세션 읽어도 되는 작은 문서. 현재는 `session_start.md`, `active_task.md` 뿐이다.
- `Active Summary`: 필요 시 여는 요약 문서. 트랙 문서, control tower, current constraints 가 여기에 속한다.
- `Cold Evidence`: 전체 실험 로그, 대형 JSON, 상세 분석 문서. 작업이 직접 요구할 때만 일부를 조회한다.
- 큰 JSON은 통째로 읽지 말고 명령으로 필요한 범위만 추출한다.
- 같은 정보를 여러 hot path 문서에 중복해 쓰지 않는다. hot path 에는 링크와 현재 next step 만 둔다.

## 최근 추가된 주의점

- `0x06B8B0` 시작부의 `strb #0` 을 `0x03005FF8` 초기화로 기록하지 않는다. 해당 write 는 `0x03005FE8` 쪽이다.
- `0x06A5B2` 의 `strb #2` 를 `0x03005FF8` write 로 기록하지 않는다. 해당 write 는 `0x03006018 = 2` state 전환이다.
- 특정 global 의 writer/reader 를 분리할 때는 `find-u32-refs` 결과의 `access=write_byte/read_byte` 를 먼저 확인한 뒤 수동 disassembly 로 보강한다.
- Thumb register-ALU (`0x4000` 계열) 는 `.hword` 로 넘기지 않는다. `cmp` 와 `cmn` 을 혼동하면 sentinel 해석이 뒤집힐 수 있다.
- literal hit 가 없는 field 도 곧바로 배제하지 않는다. `0x33C` 처럼 `0xCF << 2` 같은 계산식으로 접근하는 경우는 별도 패턴 검색으로 다시 본다.
- `scan-text` 의 기본 `--limit` 은 `100` 이다. 넓은 범위를 전수 스캔할 때는 결과가 잘렸는지 먼저 확인하고, 필요하면 `--limit` 을 명시한다.

## 작업 전 최소 체크

1. [session_start.md](/Users/user/test/docs/session_start.md)
2. [active_task.md](/Users/user/test/docs/active_task.md)

기본적으로는 **전체 실험 로그나 모든 분석 문서를 처음부터 다 읽지 않는다.**

## 작업 후 최소 체크

1. [project_control_tower.md](/Users/user/test/docs/project_control_tower.md)
2. 관련 트랙 문서 최소 1개
3. [current_constraints.md](/Users/user/test/analysis/current_constraints.md)
4. [experiment_log.md](/Users/user/test/analysis/experiment_log.md)
5. 필요 시 [initial_findings.md](/Users/user/test/analysis/initial_findings.md)

단, 토큰 절약을 위해 매 실행마다 위 전체를 기계적으로 열지 않는다. 우선 [active_task.md](/Users/user/test/docs/active_task.md) 를 갱신하고, 구조/우선순위가 바뀐 문서만 추가로 갱신한다.

## 언제 전체 로그를 읽는가

- 현재 작업이 이전 실패와 강하게 겹칠 때
- 구조 해석이 충돌해서 과거 판단 근거를 다시 확인해야 할 때
- 장기 흐름을 정리하거나 문서를 재구성할 때

그 외에는 [experiment_log.md](/Users/user/test/analysis/experiment_log.md) 를 참고용으로만 사용한다.
