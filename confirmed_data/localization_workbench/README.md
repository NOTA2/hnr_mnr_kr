# Localization Workbench 데이터

이 폴더는 사람이 직접 번역/수정/진행 상태/화자 라벨/이미지 교체 후보를 관리하기 위한 작업대 데이터다.

## 핵심 파일

- `workbench_dataset.json`
- `speaker_aliases.json`
- `speaker_registry.json`
- `progress_state.json`
- `image_replacements.json`

## active 폰트

- `Galmuri11 (12px) active Hangul 12x12 bitmap atlas`

## 카테고리

- `translation_workset_opening_intro`: 오프닝/인트로 / 4개
- `translation_workset_core_ui`: 코어 UI / 149개
- `translation_workset_gameplay_terms`: 게임 용어 / 656개
- `translation_workset_credits`: 크레딧 / 28개
- `translation_workset_registry_d_dialogue`: 대사 Registry D / 244개
- `registry_a_entry8_clusters_manifest`: 대사 Entry8 / 10417개
- `translation_workset_inline_event_texts`: 이벤트 연출 텍스트 / 41개
- `image_review_units`: 이미지 작업 / 14개

## 사용 용도

- 텍스트를 카테고리별로 나눠 본다.
- 대사에는 dialogue_state_token 과 등록된 화자 선택값을 함께 본다.
- 진행 상태를 저장하고, 현재 검토 중인 category 를 이어서 연다.
- 이미지 교체 후보는 replacement_path 와 메모를 따로 관리한다.
- Entry8 후보 검수에는 `entry8_no_space_slack_candidates.json` 탭이 포함된다. 이 탭은 공백이 하나도 없고 byte 여유가 남은 항목을 모아두며, 자동 제안은 현재값 그대로 두고 사용자가 직접 전각 공백을 넣는 검수용이다.

## 안전 기능

- 텍스트 임시 변경은 저장 전 용량/길이 정책을 검증한다.
- 여러 텍스트 항목 저장은 서버 batch 저장으로 처리하며, 소스 동기화가 실패하면 workbench dataset 을 저장 전 상태로 되돌린다.
- 전체 ROM 재빌드는 현재 항목만이 아니라 남아 있는 모든 임시 변경을 먼저 저장/검증한 뒤 시작한다.
- 브라우저에 남아 있는 임시 변경은 `임시 변경 백업`으로 JSON 파일로 내보내고, `백업 불러오기`로 복구할 수 있다.
- 임시 변경이 남아 있으면 페이지 이탈 전에 브라우저가 경고한다.
- 서버 API 오류는 JSON 형태로 반환되어 GUI에서 원인을 읽기 쉽게 표시한다.
