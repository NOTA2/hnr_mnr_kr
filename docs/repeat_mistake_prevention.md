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
- 2줄 설명창은 윗줄을 먼저 채운다. 단, fixed-slot 단문에서 사용자가 확정한 `창을연성해 공격` 같은 byte 민감 문구는 공백을 다시 넣지 않는다.
- 위 규칙은 수동 공백 패딩을 넣으라는 뜻이 아니다. 번역문에는 실제 글자만 추가하고, `0x0B` 앞 최종 padding 은 `translation_normalization.py` 와 ROM 빌드 경로가 원문 폭 기준으로 복원하게 둔다.
- 예외: 전투 ITEM 팝업의 `체력 NN ...\x0b회복약` 계열은 `0x0B` 가 일반 줄바꿈이 아니라 같은 팝업 안의 뒤 필드 시작을 가르는 런타임 separator 다. `\n` 으로 바꾸면 설명이 엉뚱한 좌표에 찍힐 수 있으므로 쓰지 않는다.
- 전투 ITEM 팝업 회복약 계열에서 뒷필드가 기존 문자열 잔상을 남기면, `\x0b 회복약  ` 처럼 separator 뒤의 선행 공백과 설명 끝 trailing spaces 를 보존해 런타임 배치와 잔상 제거를 같이 확인한다. 이 계열은 GUI/정규화/빌드 경로가 뒤 필드의 앞뒤 공백을 trim 하면 안 된다.
- 영문 약어/버튼 표기는 반각 ASCII 로 남기지 않는다. 화면에서 `H`, `P` 같은 반각 영문 glyph 가 누락될 수 있으므로 `HP`, `AS`, `R 버튼` 대신 `ＨＰ`, `ＡＳ`, `Ｒ 버튼` 같은 **전각 영문**을 사용한다.
- 보이는 숫자와 숫자 주변 슬래시는 원문 폭을 따른다. 원문이 `1/5`, `マッチョ1` 처럼 반각이면 번역도 `1/5`, `마초1` 이고, 원문이 `１／５`, `体力を５０` 처럼 전각이면 번역도 `１／５`, `체력 ５０` 이다.
- 숫자 폭/공백 정규화는 반드시 원문 전체 문맥을 본다. `回復薬１` 같은 fixed item-name slot 은 `회복약１` 처럼 붙여야 하지만, `回復薬３を手に入れた` 같은 Entry8 이벤트 문장은 `회복약　３을　얻었다` 처럼 문장 공백을 보존해야 한다. 둘 다 `회복약+숫자` 라는 이유만으로 같은 규칙을 적용하지 말고, 변경 후 `scripts/audit_translation_normalization_regressions.py` 를 실행한다.
- 일본어/한자 자체를 제외한 원문 특수기호와 문장부호는 가능한 한 원문 형태를 유지한다. 단, 반각/전각 정책은 source family 별로 다르다. `Registry D`, 코어 UI, 게임 용어에서 이미 쓰인 반각 공백/일부 기호는 보존하고, 숫자는 원문 폭을 따른다. `Entry8`, 이벤트 연출 텍스트, 오프닝/세이브/선택지 계열은 전각 우선으로 둔다. 인명/고유명사 내부의 일본식 중점 `・`는 한국어에서 띄어쓰기로 바꾸고, `・・・` 말줄임표나 숫자 사이의 `・`는 보존한다.
- 반각 사용 가능성을 전역 규칙으로 단정하지 않는다. `Registry D` 는 packed relocation 과 반각 사용이 가능하고, 코어 UI/게임 용어는 현재 데이터의 반각 사용을 존중한다. `Entry8` 과 `inline_event_texts` 는 테스트상 반각 공백/기호가 불안정하므로 전각으로 맞춘다.
- `01 FF <char_count>` counted command-stream 계열은 일반 종단 문자열처럼 다루지 않는다. 특히 `save_menu_texts` 는:
  - terminator 를 새로 붙이지 않는다.
  - 번역문이 짧아도 `char_count` 를 줄여 command-stream 경계를 앞으로 당기지 않는다.
  - 원래 문자 수를 유지하도록 전각 공백으로 패딩한 뒤 같은 byte span 안에 덮어쓴다.
  - 반각 ASCII 공백/기호를 넣지 않는다.
- ROM 적용 스크립트 안에만 존재하는 "전용 보정값" 을 만들지 않는다. 사용자는 GUI에서 검수/수정하고 `전체 적용 ROM 재빌드`로 확인하므로, 적용값을 바꾸면 반드시 GUI 표시/편집값, 저장 JSON/source-of-truth, 재추출 결과, 재빌드 경로까지 같은 값으로 연결한다.
- 예외적으로 렌더러 제약 때문에 내부 표시값과 사람이 보는 번역값이 달라져야 하면, GUI 항목에 실제 적용값과 원 번역/이유를 함께 노출한다. "ROM에는 맞게 들어가지만 GUI에는 옛 값이 보이는" 상태는 실패로 본다.
- 전투 HUD 이름처럼 동적 GUI 주입 항목은 특히 주의한다. `workbench_dataset.json` 에 정적으로 없더라도 `run_localization_workbench.py` 가 주입하는 표시값과 `extract_*` 기본값, 저장된 override JSON, 최종 적용 스크립트가 같은 정책을 써야 한다. 예: `マッチョ1..4`, `キメラ5/7` 의 숫자 제거는 `apply_battle_hud_name_font.py` 전용 보정으로만 두지 않고 GUI/저장/재추출에도 반영한다.
- 전투 HUD 이름 폰트는 물리적으로 `120`타일이지만, 데이터 패치만으로 한글 독립 글자에 안전하게 쓸 수 있는 직접 1바이트 슬롯은 `92`개뿐이다. `0xDE/0xDF` 탁점/반탁점 조합으로 보이는 `+7` 슬롯은 프리뷰상 가능해 보여도 런타임에서 앞 글자에 붙는 마커로 처리되어 글자 오출력/밀림을 만들 수 있으므로 사용하지 않는다. 남은 물리 타일 `60`, `95-99`, `105-119` 등을 쓰려면 단순 폰트 삽입이 아니라 이름 렌더러 ASM 패치가 필요하다.
- GUI/검증용 import 경로가 Pillow 같은 이미지 처리 의존성을 top-level 로 요구하게 만들지 않는다. 예를 들어 `run_localization_workbench.py` 가 전투 HUD 상수만 읽으려고 `apply_battle_hud_name_font.py` 를 import 할 때, 폰트 이미지 패치용 PIL import 실패로 `WorkbenchStore()` 검증이 막히면 안 된다. 이미지 라이브러리는 실제 이미지/폰트 작업 함수 안에서 lazy import 한다.
- review ROM 전체 재빌드는 `default_review_included` 와 source family 별 삽입 지원 상태를 따른다. `Registry D` 는 packed relocation 이 적용되어 기본 review ROM에 포함할 수 있지만, `entry8` 같은 counted 대사 family 는 별도 지원이 생기기 전까지 source 규칙을 다시 확인한다.
- `confirmed_data/localization_workbench/workbench_dataset.json` 는 **편집용 캐시**이지 번역의 source-of-truth 가 아니다. dataset 재생성 시 기존 dataset 값이 `confirmed_data/translation_worksets/*.json` 의 최신 번역을 다시 덮어쓰지 않도록 한다.
- `inline_event_texts` 후보 중에는 Entry8 counted text 또는 gameplay term 내부/인접 바이트에서 잡힌 부분 문자열 false positive 가 있을 수 있다. 같은 `offset` 중복만 dedupe 하면 부족하며, `offset..offset+byte_length` 범위가 다른 정식 텍스트 레코드와 겹치는 inline 후보는 적용하지 않는다. 예: `translation_workset_inline_event_texts:006FE1E0` 은 `cluster_27_armor_parts:006FE1D4` 의 뒷부분 `６で錬成可能！` 이고, `translation_workset_inline_event_texts:007A8550` 은 회복약 이름/설명 레코드와 겹치므로 skip 해야 한다.
- 반대로 실제 이벤트 연출 한 줄이 여러 inline 조각으로 나뉘는 경우도 있다. 제어 바이트 사이의 앞/뒤 조각을 모두 별도 `inline_event_texts` fixed slot 으로 등록해야 하며, 뒤 조각만 잡고 앞 조각을 Entry8 문맥으로 착각하지 않는다. 예: `0x007312C6` `脱がんでいい、` + 제어 바이트 + `0x007312DC` `脱がんで！` 는 같은 화면 문장을 이루는 두 inline 조각이다.
- Entry8 대사 바로 앞의 짧은 감탄사도 별도 inline fixed slot 으로 출력될 수 있다. 사용자가 “앞 대사”라고 지적한 경우 해당 Entry8 offset 앞쪽 0x40~0x80 바이트를 원본 ROM에서 직접 확인하고, `rom_text_extraction_gap_audit.json` 의 broad candidate 도 같이 대조한다. 예: `cluster_20_central:006EDB5A` 직전 `0x006EDB48` `うわっ！`, `cluster_00_liore:006B8D88` 직전 `0x006B8D5E` `　おおーっ！`, `cluster_18_east_city:006E7530` 직전 `0x006E7518` `だぁーっ！` 는 누락된 inline 이벤트 텍스트였다.
- Entry8 질문 뒤의 선택지처럼 `01 FF <char_count>` 헤더가 없는 printable Shift-JIS 블록도 있다. 기존 Entry8 추출기는 counted line 만 잡기 때문에, 제어 바이트 사이에 `전각공백 + 선택지1 + 전각공백 + 선택지2` 형태로 박힌 선택지 fixed slot 을 놓칠 수 있다. 이런 항목은 `registry_a_entry8_prefixed_texts` 로 넣지 말고 `inline_event_texts` 로 등록해 `append_terminator=false`, `header_offset/prefix/char_count=null`, 원본 byte span 유지로 in-place 적용한다. 예: `0x006FFF86` `　物々交換　等価交換` -> `　물물교환　등가교환` (`20/20` bytes), `0x0070010C` `　科学技術　魔術` -> `　과학기술　마술` (`16/16` bytes).
- 사용자가 Entry8 화면의 선택지/메뉴가 일본어로 남았다고 지적하면, 가까운 Entry8 record 만 검색해서 “이미 추출됨”으로 끝내지 않는다. 해당 record 뒤쪽 0x80~0x120 바이트를 ROM에서 직접 디코드하고, `0x81 0x40` 로 시작하는 전각공백 선택지 run 이 workbench 범위와 겹치지 않는지 확인한다. 2026-06-11 기준 Entry8 전체에서 이 패턴의 미등록 후보는 위 두 건을 추가한 뒤 `0`개로 확인했다.

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
