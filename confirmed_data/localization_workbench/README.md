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

- `translation_workset_core_ui`: 코어 UI / 47개
- `translation_workset_gameplay_terms`: 게임 용어 / 386개
- `translation_workset_registry_d_dialogue`: 대사 Registry D / 244개
- `registry_a_entry8_clusters_manifest`: 대사 Entry8 / 9823개
- `image_review_units`: 이미지 작업 / 8개

## 사용 용도

- 텍스트를 카테고리별로 나눠 본다.
- 대사에는 dialogue_state_token 과 등록된 화자 선택값을 함께 본다.
- 진행 상태를 저장하고, 현재 검토 중인 category 를 이어서 연다.
- 이미지 교체 후보는 replacement_path 와 메모를 따로 관리한다.
