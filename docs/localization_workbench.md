# Localization Workbench

이 문서는 **사람이 직접 번역/수정/화자 라벨링/이미지 교체 후보 관리**를 할 수 있도록 만든 작업대의 사용법을 정리한다.

## 목적

이 작업대는 아래를 한곳에서 다루기 위한 것이다.

- 카테고리별 텍스트 관리
- 대사 항목의 `dialogue_state_token` 확인
- 사람이 직접 붙이는 화자 이름/역할 저장
- 진행 상태 저장
- 현재 카테고리 기준 고정 이름 테스트 ROM 재빌드
- 이미지 교체 후보 경로/메모 관리
- 수정한 이미지 파일 업로드 후 교체 경로 자동 반영

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

## 주요 파일

- [workbench_dataset.json](/Users/user/test/confirmed_data/localization_workbench/workbench_dataset.json)
- [speaker_aliases.json](/Users/user/test/confirmed_data/localization_workbench/speaker_aliases.json)
- [progress_state.json](/Users/user/test/confirmed_data/localization_workbench/progress_state.json)
- [image_replacements.json](/Users/user/test/confirmed_data/localization_workbench/image_replacements.json)
- [uploaded_image_replacements](/Users/user/test/confirmed_data/localization_workbench/uploaded_image_replacements)

## 고정 이름 테스트 ROM

현재 선택한 카테고리를 기준으로 아래 파일을 항상 덮어쓴다.

- [hnr_localization_review.gba](/Users/user/test/patched_roms/current_review/hnr_localization_review.gba)

즉 사용자는 에뮬레이터에서 **항상 같은 ROM 파일만 열어두고**, GUI 쪽에서 저장/재빌드 후 다시 확인하면 된다.

## 현재 범위

### 텍스트

- 시작 화면
- 코어 UI
- 게임 용어
- Registry D 대사
- Entry8 cluster 대사

### 이미지

- 이미지 review unit 목록
- 교체 예정 파일 경로
- 메모와 진행 상태
- GUI에서 업로드한 수정본 파일 보관

## 주의

- `dialogue_state_token` 은 화자 이름 확정값이 아니다.
- 사람이 직접 “이 토큰은 이 캐릭터다”라고 붙이는 보조 레이어를 따로 저장한다.
- 이미지 파일 교체는 현재 **업로드/경로/메모/진행 상태 관리**까지 준비된 상태이며, 실제 ROM 삽입 루프는 다음 단계에서 연결한다.
