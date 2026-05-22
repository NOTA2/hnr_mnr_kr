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
- `translation_workset_registry_d_dialogue`: 대사 Registry D / 245개
- `registry_a_entry8_clusters_manifest`: 대사 Entry8 / 10417개
- `translation_workset_inline_event_texts`: 이벤트 연출 텍스트 / 41개
- `image_group_field_menu_labels`: 필드/메뉴 라벨 / 4개
- `image_group_battle_command_buttons`: 전투 하단 버튼 / 5개
- `image_group_battle_popups_panels`: 전투 팝업/패널 / 3개
- `image_group_card_book_ui`: 카드/책자 UI / 13개
- `image_group_title_screen`: 타이틀 화면 / 6개
- `image_group_reference_candidates`: 참고/비대상/확장 후보 / 4개
- `image_group_other`: 기타 이미지 후보 / 0개
- `common_hud_tiles`: 공유 HUD 타일셋 / 256개
- `alchemy_tiles`: 연금술 타일셋 / 192개
- `registry_b_zp01_resources`: Registry B ZP01 / 13개

## 사용 용도

- 텍스트를 카테고리별로 나눠 본다.
- 대사에는 dialogue_state_token 과 등록된 화자 선택값을 함께 본다.
- 진행 상태를 저장하고, 현재 검토 중인 category 를 이어서 연다.
- 이미지 교체 후보는 replacement_path 와 메모를 따로 관리한다.
