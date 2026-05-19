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
- script/control extractor 에서 stop byte 하나로 문자열을 끊을 때는, 해당 바이트가 Shift-JIS trailing byte 로 등장하는지 먼저 확인한다. `FC` 같은 값은 SJIS-aware stop 처리 없이 바로 구분자로 쓰면 entry `8` 같은 대사가 잘릴 수 있다.
- AI가 급하게 만든 테스트 glyph 는 **렌더러/매핑 검증용 placeholder** 로만 취급한다. 정식 한글 glyph 제작은 반드시 레퍼런스 기반 외부 픽셀 에디터 workflow 로 넘기고, ROM 패치는 그 산출물만 사용한다.
- `01 FF <char_count>` 계열 command-stream 문자열은 payload만 바꾸면 안 된다. review/build 경로에서도 `header_offset`, `prefix`, `char_count` 메타데이터를 끝까지 전달해 **헤더 글자수까지 함께 갱신**해야 한다.
- workbench dataset 재생성과 review ROM 빌드는 병렬로 돌리지 않는다. dataset이 먼저 갱신된 뒤 review ROM을 **순차적으로** 빌드해야 오래된 번역이 다시 들어가지 않는다.
- review ROM의 실제 적용 우선순위는 `manual_locked translation -> translation -> agent_draft -> original` 이다. `agent_draft` 가 `translation` 보다 앞서면, 길이 검증을 통과한 최종 번역이 다시 에이전트 초안으로 되돌아가 같은 문제를 반복할 수 있다.
- `battle_texts`/`ability_texts`/`material_texts` 의 `0x0B` 설명문에서 앞줄 이름 필드 여백을 버리지 않는다. 남는 폭이 있으면 조사/목적어/동사 조각을 앞줄에 넣어 자연스럽게 만든다. 예: `오토메일검을\x0b연성해 공격`, `벽을 연성해\x0b상대 공격`.
- 2줄 설명창은 윗줄을 먼저 채운다. `창을\x0b연성해 공격` 처럼 아랫줄이 길어 보이면, byte 와 첫 줄 표시 폭이 허용하는 한 `창을 연성해\x0b공격` 으로 바꾼다.
- 위 규칙은 수동 공백 패딩을 넣으라는 뜻이 아니다. 번역문에는 실제 글자만 추가하고, `0x0B` 앞 최종 padding 은 `translation_normalization.py` 와 ROM 빌드 경로가 원문 폭 기준으로 복원하게 둔다.
- 영문 약어/버튼 표기는 반각 ASCII 로 남기지 않는다. 화면에서 `H`, `P` 같은 반각 영문 glyph 가 누락될 수 있으므로 `HP`, `AS`, `R 버튼` 대신 `ＨＰ`, `ＡＳ`, `Ｒ 버튼` 같은 **전각 영문**을 사용한다.
- 일본어/한자 자체를 제외한 원문 특수기호와 문장부호는 가능한 한 원문 형태를 유지한다. 단, 반각/전각 정책은 source family 별로 다르다. `Registry D`, 코어 UI, 게임 용어에서 이미 쓰인 반각은 보존하고, `Entry8`, 이벤트 연출 텍스트, 오프닝/세이브/선택지 계열은 전각 우선으로 둔다. 인명/고유명사 내부의 일본식 중점 `・`는 한국어에서 띄어쓰기로 바꾸고, `・・・` 말줄임표나 숫자 사이의 `・`는 보존한다.
- 반각 사용 가능성을 전역 규칙으로 단정하지 않는다. `Registry D` 는 packed relocation 과 반각 사용이 가능하고, 코어 UI/게임 용어는 현재 데이터의 반각 사용을 존중한다. `Entry8` 과 `inline_event_texts` 는 테스트상 반각 공백/기호가 불안정하므로 전각으로 맞춘다.
- `01 FF <char_count>` counted command-stream 계열은 일반 종단 문자열처럼 다루지 않는다. 특히 `save_menu_texts` 는:
  - terminator 를 새로 붙이지 않는다.
  - 번역문이 짧아도 `char_count` 를 줄여 command-stream 경계를 앞으로 당기지 않는다.
  - 원래 문자 수를 유지하도록 전각 공백으로 패딩한 뒤 같은 byte span 안에 덮어쓴다.
  - 반각 ASCII 공백/기호를 넣지 않는다.
- review ROM 전체 재빌드는 `default_review_included` 와 source family 별 삽입 지원 상태를 따른다. `Registry D` 는 packed relocation 이 적용되어 기본 review ROM에 포함할 수 있지만, `entry8` 같은 counted 대사 family 는 별도 지원이 생기기 전까지 source 규칙을 다시 확인한다.
- `confirmed_data/localization_workbench/workbench_dataset.json` 는 **편집용 캐시**이지 번역의 source-of-truth 가 아니다. dataset 재생성 시 기존 dataset 값이 `confirmed_data/translation_worksets/*.json` 의 최신 번역을 다시 덮어쓰지 않도록 한다.

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
