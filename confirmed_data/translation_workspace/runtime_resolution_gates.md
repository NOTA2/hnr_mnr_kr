# runtime 마감 관문

- 마지막 갱신: `2026-05-20`

## 구조적 마감 상태

- 상태: `closed_for_known_sources`
- 확인된 source 수: `13`
- 확인된 record 수: `10756`

## 기계적으로 거의 닫힌 runtime 범위

- 상태: `nearly_closed_except_visual_confirmation`
- entry8 focus cluster 수: `12`
- entry8 chain-heavy cluster 수: `42`
- Registry D 장문 multiline focus 수: `8`

## 이미지 검토 범위

- 상태: `in_progress`
- 검토 단위 수: `8`
- 우선 검토 단위: `title_logo_wordmark`
- 우선 검토 단위: `title_screen_static_menu_wordmarks`
- 우선 검토 단위: `event_or_cutscene_text_cards`
- 우선 검토 단위: `dialogue_window_frame_art`

## 사람 확인이 필요한 항목

- `live_playthrough_text_audit`: 실제 플레이 흐름으로 훑어봐야만 아직 방문하지 않은 runtime 분기에서 일본어 문자열이 더 남아 있는지 확인할 수 있다.
- `visual_page_turn_confirmation`: entry8 연쇄 표시와 Registry D 장문 multiline 사례의 대사창/page-flow 동작은 실제 화면 확인이 있어야만 완전히 닫을 수 있다.
- `baked_image_text_asset_review`: 실제 이미지에 구워진 텍스트는 asset 단위 검토와 이후 추출/교체 작업이 아직 필요하다.
- `entry8_structural_repoint_research`: Entry8 segment repoint 는 현재 review ROM에서 닫지 않는다. 별도 실험으로 분리하고, 지역 전환/맵 로딩/자동 이동 이벤트 검증을 통과하기 전까지 메인 빌드에 넣지 않는다.

## 현재 해석

- 기계적으로 닫을 수 있는 구조적 추출은 현재 알려진 source 기준 사실상 마감됐다.
- 현재 안정 빌드는 Entry8 structural segment repoint 를 끄고, Entry8 을 원본 길이 보존 방식으로 적용한다.
- 이제 남은 일의 대부분은 미발견 텍스트 뱅크 탐색이 아니라, 사람 눈으로 확인해야 하는 runtime 동작, 번역 품질 검수, 이미지 검토다.
