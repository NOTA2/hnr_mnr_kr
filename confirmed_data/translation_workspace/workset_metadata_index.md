# Workset 메타데이터 인덱스

- 마지막 갱신: `2026-05-18`
- 항목 수: `8`
- 용도: 번역팀이 실제 번역 시작 전에 workset 별 제약과 QA 범위를 빠르게 확인하는 인덱스

## 권장 읽기 순서

- 1. translation_workset_opening_intro 로 오프닝 첫 카드와 고정 슬롯 규칙을 확인한다.
- 2. translation_workset_core_ui 와 gameplay_terms, credits 로 실번역을 시작한다.
- 3. Registry D dialogue 와 entry8 cluster 는 대사 sidecar 와 runtime 주의사항을 함께 본다.

## Workset별 요약

### `translation_workset_opening_intro`

- 경로: `confirmed_data/translation_worksets/translation_workset_opening_intro.json`
- 레코드 수: `4`
- 목적: 게임 시작 직후 오프닝 고정 카드 4줄
- 상태: 바로 번역 시작 가능
- layout 전략: 단일 family `startup_intro_fixed_slots` 기준
- 줄바꿈 규칙: 수동 줄바꿈 금지
- source_group: `startup_intro_texts`
- 이미지 겹침 위험: 낮음
- 필수 보존 요소: append_terminator=false, 고정 byte_length, 뒤 제어코드 위치
- QA 필요 항목: 고정 슬롯 byte 길이 확인, 오프닝 첫 카드 4줄 시각 확인
- 참고:
  - 모든 레코드는 startup_intro_texts 에서 왔고, 게임 시작 직후 고정 카드 4줄이다.

### `translation_workset_core_ui`

- 경로: `confirmed_data/translation_worksets/translation_workset_core_ui.json`
- 레코드 수: `50`
- 목적: 시스템/세이브/지역명/UI 기술명 등 첫 실제 번역 진입 세트
- 상태: 바로 번역 시작 가능
- layout 전략: source_group 별 family 를 먼저 적용
- 줄바꿈 규칙: source_group 별 규칙 우선
- source_group: `location_texts, save_menu_texts, system_messages, ui_skill_texts`
- 이미지 겹침 위험: 중간
- 필수 보존 요소: save_menu 01 FF 헤더, location family 보수적 길이 유지
- QA 필요 항목: 메뉴/세이브/지역명 대표 화면 확인, 혼합 family 적용 확인
- source_group별 family:
  - `system_messages` -> `system_messages_plain_newline_00`
  - `save_menu_texts` -> `save_menu_prefixed_01ff`
  - `location_texts` -> `world_map_location_r3_12`
  - `ui_skill_texts` -> `ui_or_item_plain_00_record`
- 참고:
  - 이 workset 은 하나의 창 규격으로 보면 안 된다.
  - 반드시 source_group 별 family 를 먼저 적용한다.

### `translation_workset_gameplay_terms`

- 경로: `confirmed_data/translation_worksets/translation_workset_gameplay_terms.json`
- 레코드 수: `625`
- 목적: 아이템/전투/능력/재료/설명/Entry12 계열 전체 용어 세트
- 상태: 바로 번역 시작 가능
- layout 전략: source_group 별 family 를 먼저 적용
- 줄바꿈 규칙: 추가 줄바꿈 지양
- source_group: `ability_texts, battle_texts, item_texts, material_texts, registry_a_entry12_texts`
- 이미지 겹침 위험: 낮음
- 필수 보존 요소: 0x0B separator, 전각 공백 패딩, 짧고 명확한 설명문
- QA 필요 항목: 용어/설명문 길이 과팽창 방지, 0x0B / 패딩 보존 확인
- source_group별 family:
  - `item_texts` -> `ui_or_item_plain_00_record`
  - `ability_texts` -> `term_description_plain_00_optional_0b`
  - `material_texts` -> `term_description_plain_00_optional_0b`
  - `battle_texts` -> `term_description_plain_00_optional_0b`
  - `registry_a_entry12_texts` -> `ui_or_item_plain_00_record`
- 참고:
  - 아이템/전투/능력/재료/Entry12 텍스트를 전량 포함한 정식 용어 세트다.
  - 다만 runtime box family 가 미확정인 곳이 있어 설명문은 계속 짧게 유지하는 편이 안전하다.

### `translation_workset_credits`

- 경로: `confirmed_data/translation_worksets/translation_workset_credits.json`
- 레코드 수: `10`
- 목적: 엔딩 크레딧/스태프 표기 세트
- 상태: 바로 번역 시작 가능
- layout 전략: 단일 family `credits_padded_plain_00_record` 기준
- 줄바꿈 규칙: 기존 패딩/정렬 유지
- source_group: `credits_texts`
- 이미지 겹침 위험: 낮음
- 필수 보존 요소: 전각 공백 패딩, 크레딧 줄 길이 보수적 유지
- QA 필요 항목: 전각 공백 패딩 유지, 크레딧 화면 줄 정렬 확인
- 참고:
  - 크레딧은 일반 텍스트 record 로 추출되어 있으며, 이미지 자산이 아니다.

### `translation_workset_registry_d_dialogue`

- 경로: `confirmed_data/translation_worksets/translation_workset_registry_d_dialogue.json`
- 레코드 수: `244`
- 목적: 튜토리얼/이벤트/전투 전후 대사 세트
- 상태: 번역 시작 가능, 페이지 QA 후속 필요
- layout 전략: 단일 family `registry_d_fc_stop_script_line` 기준
- 줄바꿈 규칙: 기존 개행만 보존, 새 개행은 보수적으로
- source_group: `registry_d_fc_script_texts`
- 이미지 겹침 위험: 낮음
- 필수 보존 요소: FC-delimited 구조, adjacent control stream, dialogue_state sidecar 참고
- QA 필요 항목: 기존 개행 보존, 장문 run page-turn 확인, 화자 state token 참고
- 참고:
  - FC stop-byte 기준의 record 경계는 확정됐다.
  - 다만 장문 run 의 실제 page-turn 동작은 시각 QA 로 한 번 더 확인해야 한다.

### `registry_a_entry8_clusters_manifest`

- 경로: `confirmed_data/translation_workspace/registry_a_entry8_clusters_manifest.json`
- 레코드 수: `72`
- 목적: 대형 스토리/이벤트 뱅크를 cluster 단위로 나눈 인덱스
- 상태: 번역 시작 가능, cluster 단위 운영 권장
- layout 전략: cluster 단위로 나눈 뒤 entry8 single-line 규칙을 적용
- 줄바꿈 규칙: 수동 줄바꿈 금지
- source_group: `registry_a_entry8_prefixed_texts`
- 이미지 겹침 위험: 낮음
- 필수 보존 요소: 01 FF 헤더, char_count, 제어코드 인접 구조, dialogue_state sidecar 참고
- QA 필요 항목: chain-heavy cluster 우선 점검, 후반 cluster 의 page-flow 확인
- source_group별 family:
  - `registry_a_entry8_prefixed_texts` -> `entry8_prefixed_01ff_script_line`
- 참고:
  - cluster 를 한 번에 다 번역하지 말고 primary_tag / runtime focus 순서로 나누는 편이 안전하다.

### `translation_workset_intro_full_test`

- 경로: `confirmed_data/translation_worksets/translation_workset_intro_full_test.json`
- 레코드 수: `18`
- 목적: 인트로 확장 QA 세트
- 상태: 테스트/검증 전용
- layout 전략: source_group 별 family 를 먼저 적용
- 줄바꿈 규칙: 실제 번역 기준이 아니라 검증용
- source_group: `registry_a_entry8_prefixed_texts, startup_intro_texts`
- 이미지 겹침 위험: 낮음
- 필수 보존 요소: family 혼합 구조, source_group 별 규칙
- QA 필요 항목: 여러 family 혼합 동작 확인, 시작 카드 이후 인트로 흐름 확인
- source_group별 family:
  - `startup_intro_texts` -> `startup_intro_fixed_slots`
  - `location_texts` -> `world_map_location_r3_12`
  - `registry_a_entry8_prefixed_texts` -> `entry8_prefixed_01ff_script_line`
- 참고:
  - 여러 family 를 한 파일에서 함께 검증하는 QA 세트다.
  - 이 세트에서 보이는 길이/줄 수를 전역 제한으로 일반화하면 안 된다.

### `translation_workset_intro_full_compact_test`

- 경로: `confirmed_data/translation_worksets/translation_workset_intro_full_compact_test.json`
- 레코드 수: `18`
- 목적: 인트로 compact QA 세트
- 상태: 테스트/검증 전용
- layout 전략: source_group 별 family 를 먼저 적용
- 줄바꿈 규칙: 실제 번역 기준이 아니라 검증용
- source_group: `registry_a_entry8_prefixed_texts, startup_intro_texts`
- 이미지 겹침 위험: 낮음
- 필수 보존 요소: family 혼합 구조, source_group 별 규칙
- QA 필요 항목: compact 문구 가독성 확인, pointer 없는 상황 검증
- source_group별 family:
  - `startup_intro_texts` -> `startup_intro_fixed_slots`
  - `location_texts` -> `world_map_location_r3_12`
  - `registry_a_entry8_prefixed_texts` -> `entry8_prefixed_01ff_script_line`
- 참고:
  - pointer 없는 상황에서 compact 문구로 시각 QA 를 돌리는 검증 세트다.
