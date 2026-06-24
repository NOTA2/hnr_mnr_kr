# Localization Workbench

이 문서는 **사람이 직접 번역/수정/진행 상태/이미지 교체 후보 관리**를 할 수 있도록 만든 작업대의 사용법을 정리한다.

## 목적

이 작업대는 아래를 한곳에서 다루기 위한 것이다.

- 카테고리별 텍스트 관리
- 대사 항목의 `dialogue_state_token` 확인
- 번역 에이전트 초안과 최종 적용 번역 분리
- 수동 잠금으로 사람이 확정한 번역 보호
- 진행 상태 저장
- 현재 카테고리 기준 고정 이름 테스트 ROM 재빌드
- 이미지 교체 후보 경로/메모 관리
- 수정한 이미지 파일 업로드 후 교체 경로 자동 반영
- 원본 이미지와 교체 이미지를 나란히 비교하고 다운로드

## 실행

### 데이터 재생성

```bash
python3 scripts/build_localization_workbench_dataset.py
```

### GUI 서버 실행

```bash
python3 scripts/run_localization_workbench.py
```

브라우저:

```text
http://127.0.0.1:8766
```

주의:

- 번역 GUI는 `file://`로 직접 열면 안 된다.
- 반드시 `python3 scripts/run_localization_workbench.py` 실행 후 `http://127.0.0.1:8766`으로 접속해야 한다.
- 테스트 ROM은 원래대로 `.gba` 파일을 에뮬레이터에서 열면 된다.

### 자동 가져오기

서버는 시작할 때 아래 폴더를 자동 스캔한다.

- [agent_inbox](/Users/user/test/confirmed_data/localization_workbench/agent_inbox)

이 폴더 안에 번역 에이전트 팀 결과 JSON을 넣어 두고 서버를 실행하면:

1. 자동으로 dataset에 병합한다.
2. 가져온 파일은 [imported_agent_results](/Users/user/test/confirmed_data/localization_workbench/imported_agent_results) 로 이동한다.
3. 리포트는 [import_reports](/Users/user/test/confirmed_data/localization_workbench/import_reports) 에 남는다.
4. 잠기지 않은 번역은 workbench dataset뿐 아니라 대응하는 `translation_worksets/*.json` 과 관련 source JSON에도 자동 동기화된다.

즉, 꼭 GUI의 `번역 결과 가져오기` 버튼을 누르지 않아도 된다.
버튼은 서버를 이미 켜 둔 상태에서 추가 JSON을 즉시 넣고 싶을 때만 쓰면 된다.

## 공통 문자 정규화

작업대는 현재 추출본 전체를 기준으로 만든 공통 정규화 프로필을 사용한다.

- 프로필 파일: [translation_normalization_profile.json](/Users/user/test/confirmed_data/font_assets/translation_normalization_profile.json)
- 이 프로필은 `build_localization_workbench_dataset.py` 실행 시 자동 갱신된다.

현재 자동 변환되는 대표 규칙:

- `...` → `…`
- 공백 ` ` → 전각 공백 `　`
- 숫자와 숫자 주변 슬래시는 원문 폭을 따른다. 원문이 `0-9`, `1/5`처럼 반각이면 번역도 반각이고, 원문이 `０-９`, `１／５`처럼 전각이면 번역도 전각이다.
- 단, 원문에 숫자 폭 단서가 없는 `startup_intro_texts` 오프닝 첫 카드처럼 전용 렌더러가 반각 숫자를 안정적으로 표시하지 못하는 family 는 전각 숫자를 기본값으로 둔다.
- `!` → `！`
- `?` → `？`
- `~` → `～`
- `(` → `（`
- `)` → `）`
- `/` → `／`
- `-` → `－`
- `@` → `＠`
- `$` → `＄`
- 영문 약어는 전각 영문 우선: `HP` → `ＨＰ`, `AS` → `ＡＳ`, `R 버튼` → `Ｒ 버튼`

즉 사용자는 GUI에서 반각 기호를 그대로 입력해도 되고, 저장/가져오기/ROM 적용 전에 안전한 형태로 자동 보정된다.

영문 표기 정책:

- 게임 내 공통 폰트/렌더러는 반각 ASCII 영문이 화면에 누락될 수 있으므로, 번역문에 영문 약어를 남겨야 할 때는 **전각 영문**을 사용한다.
- 예: `HP` 금지, `ＨＰ` 사용. `AS` 금지, `ＡＳ` 사용. `R 버튼` 금지, `Ｒ 버튼` 사용.
- 숫자와 숫자 주변 슬래시는 원문 폭을 따른다. 원문에 숫자 폭 단서가 없는 경우에만 family별 기본값을 쓴다. 영문자 자체는 반각 ASCII로 남기지 않는다.

주의:

- 현재 자동 변환은 **문자 단위 안전 치환**이다.
- 문장 의미가 달라지는 치환(예: `.` → `。`, `,` → `、`)은 아직 자동으로 하지 않는다.

## 주요 파일

- [workbench_dataset.json](/Users/user/test/confirmed_data/localization_workbench/workbench_dataset.json)
- [progress_state.json](/Users/user/test/confirmed_data/localization_workbench/progress_state.json)
- [image_replacements.json](/Users/user/test/confirmed_data/localization_workbench/image_replacements.json)
- [uploaded_image_replacements](/Users/user/test/confirmed_data/localization_workbench/uploaded_image_replacements)

## 고정 이름 테스트 ROM

현재 저장된 전체 적용 번역을 기준으로 아래 파일을 항상 덮어쓴다.

- [hnr_localization_review.gba](/Users/user/test/patched_roms/current_review/hnr_localization_review.gba)

즉 사용자는 에뮬레이터에서 **항상 같은 ROM 파일만 열어두고**, GUI 쪽에서 저장/재빌드 후 다시 확인하면 된다.

## 번역 에이전트 연동 규칙

- `translation`:
  - 실제 ROM 적용에 쓰는 **최종 적용 번역**
- `agent_draft`:
  - 번역 에이전트가 제안한 **초안**
  - AI/에이전트 번역이 적용된 항목은 되돌림 백업으로도 쓸 수 있도록 항상 채운다.
  - dataset 재생성 시 기존 `agent_draft` 가 있으면 보존하고, 비어 있는데 `translation` 이 있으면 현재 번역을 초안으로 시드한다.
- `agent_comment`:
  - 에이전트가 남기는 설명, 차선책, 주의 메모
- `manual_locked=true`:
  - 사람이 직접 확정한 번역이므로, 에이전트가 `translation` 을 덮어쓰면 안 된다
  - 이 경우 에이전트는 `agent_draft` 와 `agent_comment` 만 갱신해야 한다
  - GUI에서 번역문을 에이전트 초안과 다르게 직접 수정하고 저장하면, 이 잠금은 자동으로 켜진다

### 실제 적용 규칙

- `manual_locked=true` 이고 `translation` 이 있으면 그 값이 ROM에 들어간다.
- 그 외에는 `translation` 이 있으면 그 값을 우선 적용한다.
- `translation` 이 비어 있을 때만 `agent_draft` 를 적용한다.
- 둘 다 없으면 원문이 들어간다.

### GUI/ROM/source 동기화 원칙

로컬라이제이션 작업대에서 보이는 값은 사람이 검수하고 수정하는 기준이다. 따라서 어떤 스크립트가 ROM에 넣는 실제 적용값을 바꾸면 아래가 함께 맞아야 한다.

- GUI의 `translation` / `effective_translation`
- 저장되는 workset/source JSON 또는 해당 항목의 override JSON
- 추출/재추출 스크립트의 기본값
- `전체 적용 ROM 재빌드` 경로
- 실제 적용 리포트

금지:

- ROM 적용 스크립트 안에서만 몰래 다른 값을 쓰고 GUI에는 옛 값을 남기는 것.
- "전용 보정" 이라는 이유로 사용자가 GUI에서 확인하거나 수정할 수 없는 값을 만드는 것.
- 재추출이나 서버 재시작 후 GUI 값이 이전 값으로 되돌아가는 구조를 방치하는 것.

예외:

- 렌더러/폰트/슬롯 제약 때문에 사람용 원 번역과 실제 HUD 적용값이 다를 수는 있다. 이 경우에도 GUI에는 실제 적용값을 보여주고, 필요하면 원 번역과 보정 이유를 별도 필드나 메모로 함께 노출한다.
- 동적 주입 항목은 `workbench_dataset.json` 검색만으로 확인하지 않는다. 예를 들어 `전투 HUD 이름 테이블` 은 [run_localization_workbench.py](/Users/user/test/scripts/run_localization_workbench.py) 가 서버 시작 시 주입하므로, 주입 함수와 저장 JSON, 추출 스크립트, 적용 스크립트를 같이 갱신한다.
- 동적 주입/검증 경로는 무거운 이미지 의존성을 top-level 로 가져오지 않는다. GUI 데이터 확인에 필요한 상수나 정규화 함수만 import 할 때 Pillow 실패로 서버/검증이 막히지 않도록, 폰트 렌더링이나 PNG 처리가 필요한 함수 안에서만 lazy import 한다.

즉 원하는 흐름은 이렇게 된다.

1. 번역 에이전트 팀이 `agent_draft` / `agent_comment` 를 채운다.
2. 사람이 GUI에서 초안을 보고 필요하면 수정한다.
3. 사람이 직접 확정한 항목은 `수동 잠금`을 켜거나, 직접 수정 후 저장하면 자동으로 잠긴다.
4. 사용자는 `전체 적용 ROM 재빌드`만 눌러 고정 이름 리뷰 ROM을 다시 만든다.

### 가져오기 흐름

1. 번역 에이전트 팀이 workset JSON 또는 같은 구조의 결과 JSON을 만든다.
2. GUI 왼쪽 패널에서 `번역 에이전트 결과 JSON 가져오기`로 파일을 선택한다.
3. `번역 결과 가져오기`를 누르면:
   - 잠기지 않은 항목은 `translation` 과 `agent_draft` 에 자동 반영된다.
   - `manual_locked=true` 인 항목은 `translation` 을 유지하고, `agent_draft` / `agent_comment` 만 갱신한다.
   - 반영된 `translation` 은 workbench dataset뿐 아니라 대응하는 workset/source JSON에도 자동 동기화된다.
4. 사용자는 필요하면 GUI에서 일부 문장을 직접 수정한다.
5. `전체 적용 ROM 재빌드`를 누르면 고정 이름 리뷰 ROM에 바로 반영된다.

가져오기 리포트는 아래에 남는다.

- [import_reports](/Users/user/test/confirmed_data/localization_workbench/import_reports)

## 현재 범위

### 텍스트

- 코어 UI
- 오프닝/인트로
- 게임 용어
- Registry D 대사
- Entry8 cluster 대사
- 이벤트 연출 텍스트

주의:

- 게임 시작 직후 첫 카드 4줄은 테스트용 코어 UI가 아니라 **정식 `오프닝/인트로` 카테고리**에서 관리한다.
- 이후 이어지는 인트로 대사/이벤트 문장은 대부분 `Entry8` 또는 `Registry D` 쪽에서 관리한다.
- 같은 문장을 여러 카테고리에 중복 노출하지 않도록 source/workset 기준으로 한 번만 보이게 유지한다.
- `Entry8` 화면에 보이는 선택지가 모두 `대사 Entry8` 항목으로 잡히는 것은 아니다. 질문/대사는 `registry_a_entry8_prefixed_texts` 로 잡히지만, 제어 바이트 사이에 직접 박힌 선택지 블록은 `이벤트 연출 텍스트` / `inline_event_texts` fixed slot 으로 관리한다.
- 예: `translation_workset_inline_event_texts:006FFF86` `　物々交換　等価交換`, `translation_workset_inline_event_texts:0070010C` `　科学技術　魔術`. 둘 다 헤더 없는 고정 슬롯이므로 `append_terminator=false` 로 원본 byte 길이 안에서만 교체한다.
- 따라서 실플레이에서 Entry8 질문은 번역됐는데 선택지만 일본어로 남으면, GUI에서 `대사 Entry8` 뿐 아니라 `이벤트 연출 텍스트` 를 같이 검색한다.

### 이미지/타일

- 사용자가 `.ss` 저장상태를 주면, 저장상태 캡처 자체를 GUI 항목으로 등록하지 않는다.
- mGBA 저장상태에서 런타임 타일을 덤프하고 ROM 압축 블록과 매칭한 뒤, 한글화 가능한 실제 ROM 블록만 `image:*` 항목으로 등록한다.
- 하나의 블록이 잡히면 같은 LZ77/RLE 인접 구간도 함께 훑어 같은 계열 라벨을 추가로 찾는다.
- 원시 타일이 어긋나 보이는 경우에는 사람이 눈대중으로 맞추지 않고, VRAM의 BG `screenblock` tilemap, scroll, OAM sprite 데이터를 이용해 실제 화면 배치로 다시 렌더링한다.
- tilemap 재렌더링 PNG는 교체 대상이 아니라 분석 지도다. 실제 교체는 이 지도에서 확인한 글자/버튼을 ROM의 LZ77/RLE 그래픽 블록, raw tilemap, 또는 텍스트 렌더러로 역추적한 뒤 진행한다.
- BG `screenblock`이 ROM에 raw tilemap으로 존재하는지 먼저 검색하고, raw hit가 없으면 압축 그래픽 블록/런타임 생성 루틴 쪽으로 추적한다.
- `RLE 레이아웃 비교 시트`, `RLE 전체 후보 시트`, 전체 갤러리처럼 사람이 판별하기 어려운 대량 시트는 GUI에 노출하지 않는다.
- GUI에는 `0x005323AC` 같은 교체 가능한 개별 ROM 오프셋 후보와 그 미리보기만 남긴다.

## 상태 토큰 방식

- `dialogue_state_token` 은 객관적 상태 토큰이다.
- GUI는 이 값을 읽기 전용 참고 정보로 보여준다.
- 화자명 확정/연결 UI는 실제 번역 QA에 도움이 크지 않아 제거했다.
- 말투 판단이 필요하면 확정 화자명 대신 장면 맥락과 state/run sidecar 를 참고한다.

### 이미지

- 이미지 review unit 목록
- 원본 이미지 경로가 채워진 항목은 GUI에서 바로 미리보기/다운로드 가능
- 교체 예정 파일 경로
- 교체 이미지 업로드 후 원본/교체본 비교 가능
- 메모와 진행 상태
- GUI에서 업로드한 수정본 파일 보관

## 주의

- `dialogue_state_token` 은 화자 이름 확정값이 아니다.
- GUI는 더 이상 사람이 직접 “이 토큰은 이 캐릭터다”라고 붙이는 보조 레이어를 저장하지 않는다.
- 이미지 파일 교체는 현재 **업로드/경로/메모/진행 상태 관리**까지 준비된 상태이며, 실제 ROM 삽입 루프는 다음 단계에서 연결한다.
- 원본 이미지가 아직 추출되지 않은 항목은 미리보기에 “연결되지 않음”으로 보인다.
- 원본 자산이 프로젝트 안 경로로 준비되면, 해당 경로를 이미지 항목에 넣는 즉시 비교/다운로드 UI가 활성화된다.
