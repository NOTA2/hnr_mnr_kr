# Localization Workbench

이 문서는 **사람이 직접 번역/수정/화자 라벨링/이미지 교체 후보 관리**를 할 수 있도록 만든 작업대의 사용법을 정리한다.

## 목적

이 작업대는 아래를 한곳에서 다루기 위한 것이다.

- 카테고리별 텍스트 관리
- 대사 항목의 `dialogue_state_token` 확인
- 사람이 직접 붙이는 화자 이름/역할 저장
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
- `0-9` → `０-９`
- `!` → `！`
- `?` → `？`
- `~` → `～`
- `(` → `（`
- `)` → `）`
- `/` → `／`
- `-` → `－`
- `@` → `＠`
- `$` → `＄`

즉 사용자는 GUI에서 반각 기호를 그대로 입력해도 되고, 저장/가져오기/ROM 적용 전에 안전한 형태로 자동 보정된다.

주의:

- 현재 자동 변환은 **문자 단위 안전 치환**이다.
- 문장 의미가 달라지는 치환(예: `.` → `。`, `,` → `、`)은 아직 자동으로 하지 않는다.

## 주요 파일

- [workbench_dataset.json](/Users/user/test/confirmed_data/localization_workbench/workbench_dataset.json)
- [speaker_aliases.json](/Users/user/test/confirmed_data/localization_workbench/speaker_aliases.json)
- [speaker_registry.json](/Users/user/test/confirmed_data/localization_workbench/speaker_registry.json)
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

주의:

- 게임 시작 직후 첫 카드 4줄은 테스트용 코어 UI가 아니라 **정식 `오프닝/인트로` 카테고리**에서 관리한다.
- 이후 이어지는 인트로 대사/이벤트 문장은 대부분 `Entry8` 또는 `Registry D` 쪽에서 관리한다.
- 같은 문장을 여러 카테고리에 중복 노출하지 않도록 source/workset 기준으로 한 번만 보이게 유지한다.

## 화자 관리 방식

- `dialogue_state_token` 은 여전히 객관적 상태 토큰이다.
- 실제 화자명은 **`speaker_registry.json` 에 먼저 등록**한다.
- 각 대사 토큰에는 GUI에서 **등록된 화자를 선택**해 연결한다.
- 이렇게 해서 자유 입력 오타를 줄이고, 같은 캐릭터 표기를 일관되게 유지한다.

### 이미지

- 이미지 review unit 목록
- 원본 이미지 경로가 채워진 항목은 GUI에서 바로 미리보기/다운로드 가능
- 교체 예정 파일 경로
- 교체 이미지 업로드 후 원본/교체본 비교 가능
- 메모와 진행 상태
- GUI에서 업로드한 수정본 파일 보관

## 주의

- `dialogue_state_token` 은 화자 이름 확정값이 아니다.
- 사람이 직접 “이 토큰은 이 캐릭터다”라고 붙이는 보조 레이어를 따로 저장한다.
- 이미지 파일 교체는 현재 **업로드/경로/메모/진행 상태 관리**까지 준비된 상태이며, 실제 ROM 삽입 루프는 다음 단계에서 연결한다.
- 원본 이미지가 아직 추출되지 않은 항목은 미리보기에 “연결되지 않음”으로 보인다.
- 원본 자산이 프로젝트 안 경로로 준비되면, 해당 경로를 이미지 항목에 넣는 즉시 비교/다운로드 UI가 활성화된다.
