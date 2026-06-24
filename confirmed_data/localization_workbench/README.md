# Localization Workbench 데이터

이 폴더는 사람이 직접 번역/수정/진행 상태/이미지 교체 후보를 관리하기 위한 작업대 데이터다.

## 핵심 파일

- `workbench_dataset.json`
- `progress_state.json`
- `image_replacements.json`

## active 폰트

- `Galmuri11 (12px) active Hangul 12x12 bitmap atlas`

## 카테고리

- `translation_workset_opening_intro`: 오프닝/인트로 / 4개
- `translation_workset_core_ui`: 코어 UI / 149개
- `translation_workset_gameplay_terms`: 게임 용어 / 677개
- `translation_workset_credits`: 크레딧 / 83개
- `translation_workset_registry_d_dialogue`: 대사 Registry D / 245개
- `registry_a_entry8_clusters_manifest`: 대사 Entry8 / 10417개
- `translation_workset_inline_event_texts`: 이벤트 연출 텍스트 / 36개
- `image_group_field_menu_labels`: 필드/메뉴 라벨 / 4개
- `image_group_battle_command_buttons`: 전투 하단 버튼 / 5개
- `image_group_battle_popups_panels`: 전투 팝업/패널 / 2개
- `image_group_title_screen`: 타이틀 화면 / 6개
- `common_hud_tiles`: 공유 HUD 타일셋 / 256개
- `alchemy_tiles`: 연금술 타일셋 / 192개
- `registry_b_zp01_resources`: Registry B ZP01 / 13개
- `page_turn_rle_05_tiles`: 페이지 넘김 RLE 05 타일셋 / 128개
- `page_turn_rle_06_tiles`: 페이지 넘김 RLE 06 타일셋 / 300개
- `page_turn_rle_07_tiles`: 페이지 넘김 RLE 07 타일셋 / 300개
- `page_turn_rle_08_tiles`: 페이지 넘김 RLE 08 타일셋 / 300개
- `page_turn_rle_09_tiles`: 페이지 넘김 RLE 09 타일셋 / 300개
- `page_turn_rle_10_tiles`: 페이지 넘김 RLE 10 타일셋 / 300개
- `page_turn_rle_11_tiles`: 페이지 넘김 RLE 11 타일셋 / 300개

## 사용 용도

- 텍스트를 카테고리별로 나눠 본다.
- 대사에는 객관적 dialogue_state_token 을 참고 정보로 함께 본다.
- 진행 상태를 저장하고, 현재 검토 중인 category 를 이어서 연다.
- 이미지 교체 후보는 replacement_path 와 메모를 따로 관리한다.
