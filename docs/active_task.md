# Active Task

이 파일은 **매 세션 시작 때 읽는 짧은 작업 카드**다.

## 현재 상태

- 한글 폰트 최종 기준은 `Galmuri11 (12px)` 이다.
- 비교 후보 원본 `3`개는 [finalists](/Users/user/test/third_party/font_atlases/finalists) 아래에 프로젝트 로컬로 복사해 두었다.
- 현재 active 기본값은 [galmuri11_12x12.png](/Users/user/test/third_party/font_atlases/finalists/galmuri11_12x12.png) 이다.
- 후보군 메타데이터와 export 기준은 [finalist_font_candidates.json](/Users/user/test/confirmed_data/font_assets/finalist_font_candidates.json), [finalist_export_recommendation.md](/Users/user/test/confirmed_data/font_assets/finalist_export_recommendation.md) 에 있다.
- 새 후보 bitmap PNG 에서 **반드시 필요한 것**은 `가..힣` 완성형 `11,172`자 atlas 다.
- 숫자/영문/기본 기호는 1차 한글화 기준으로 **원본 게임 공통 폰트**를 그대로 재사용하되, 반각/전각은 source family별 정책을 따른다. `Registry D`, 코어 UI, 게임 용어에서 이미 안정적으로 쓰인 반각은 유지하고, `Entry8`, 이벤트 연출 텍스트, 오프닝/세이브/선택지 계열은 전각 우선으로 둔다.
- 인명/고유명사 내부의 `・`는 한국어에서 띄어쓰기로 통일한다. `・・・` 말줄임표와 숫자 사이의 `・`는 보존한다.
- 첫 화면 즉시 비교용 startup showcase 세트는 [translation_workset_startup_font_showcase.json](/Users/user/test/confirmed_data/translation_worksets/translation_workset_startup_font_showcase.json) 이다.
- startup 비교 문구는 현재 원문 의미를 유지한 `대륙력 / １９１０년 ２월 / 리젠블 마을 / 형１１세 동생１０세` 기준으로 맞추고 있다.
- atlas importer 는 PNG 의 밝은 본체와 그림자 역할을 게임 원본 단계인 `0 / 17 / 34` 로 매핑하되, **이 화면에서는 밝은 본체가 `17`, 그림자가 `34` 역할** 이 되도록 반대로 넣는다.
- startup 첫 카드 `4`줄은 일반 `00` 종단 문자열이 아니라 **고정 길이 슬롯** 이므로, `append_terminator: false` 로 처리한다.
- 텍스트 박스/공용 렌더러 family 규격은 [text_box_family_manifest.json](/Users/user/test/confirmed_data/text_layout/text_box_family_manifest.json) 에 분리해 둔다.
- source / workset 별 layout family 연결은 [text_layout_assignment_index.json](/Users/user/test/confirmed_data/text_layout/text_layout_assignment_index.json) 에 둔다.
- runtime family 우선순위 보고서는 [runtime_family_focus_report.md](/Users/user/test/confirmed_data/text_layout/runtime_family_focus_report.md) 를 본다.
- high-priority dialogue runtime 상세는 [runtime_dialogue_family_report.md](/Users/user/test/confirmed_data/text_layout/runtime_dialogue_family_report.md) 를 본다.
- high-priority dialogue runtime 세부 subprofile 은 [runtime_dialogue_subprofiles.md](/Users/user/test/confirmed_data/text_layout/runtime_dialogue_subprofiles.md) 를 본다.
- 실제 다음 runtime QA 우선순위는 [runtime_pageflow_focus.md](/Users/user/test/confirmed_data/text_layout/runtime_pageflow_focus.md) 를 본다.
- 남은 미확정이 기계적으로 어디까지 닫혔는지는 [runtime_resolution_gates.md](/Users/user/test/confirmed_data/translation_workspace/runtime_resolution_gates.md) 를 본다.
- `entry8` / `Registry D` 의 objective candidate group 은 [runtime_candidate_groups.md](/Users/user/test/confirmed_data/text_layout/runtime_candidate_groups.md) 를 본다.
- 대사 계열 state token sidecar 는 [confirmed_data/dialogue_metadata/README.md](/Users/user/test/confirmed_data/dialogue_metadata/README.md) 에 둔다.
- cluster/run 빠른 요약은 [dialogue_state_cluster_summary.md](/Users/user/test/confirmed_data/dialogue_metadata/dialogue_state_cluster_summary.md) 을 본다.
- save/menu prompt 는 `save_menu_prefixed_01ff` family 로 따로 분리해, `01 FF <u16 char_count>` 헤더와 뒤 제어코드를 보존하는 쪽으로 다룬다.
- `registry_a_entry8_prefixed_texts` 는 `entry8_prefixed_01ff_script_line`, `registry_d_fc_script_texts` 는 `registry_d_fc_stop_script_line` family 로 부분 확정했다.
- 위 두 source 는 같은 `shared_text_object_r3_20` 후보를 공유하지만, payload 성격은 각각 **single-line counted** / **multiline FC-delimited** 로 갈린다.
- `Registry D` 는 이제 entry 단위 packed relocation 이 적용된다. 번역문이 원문 byte 슬롯보다 길어져도 ROM 끝으로 entry 를 재패킹하고 `0x17C7E4` pointer-length table 을 갱신할 수 있다.
- 따라서 `Registry D` 대사는 초압축 번역보다 자연스러운 의미 보존을 우선하고, 화면 잘림은 삭제가 아니라 줄바꿈/page-flow QA 로 조정한다.
- 추가 개선 과제: 영문판처럼 ROM 을 16MB/32MB 로 확장하고, direct pointer/packed table 이 확인되는 source 부터 확장 영역 repoint 를 늘린다. 단, 당장 진행하지 않고 `ability/battle/material/entry8` 의 참조 구조를 더 닫은 뒤 별도 트랙으로 진행한다.
- `entry8` 의 남은 runtime 불확실성은 이제 source 전체가 아니라 **chain-heavy single-line cluster** 쪽에 더 몰려 있다.
- `Registry D` 의 남은 runtime 불확실성은 이제 source 전체가 아니라 **small long-multiline tier + page-turn behavior** 쪽에 더 몰려 있다.
- 현재 가장 먼저 볼 `entry8` focus cluster 는 `38, 18, 61, 55, 20, 41, 62, 26, 11, 70` 이다.
- 현재 가장 먼저 볼 `Registry D` focus run 은 `11, 15, 22, 24, 25, 113, 114, 140` 이다.
- 구조적으로는 known source `13`개 / known record `10756` 기준으로 닫혔고, 남은 핵심은 **visual page-turn / live playthrough / baked image review** 세 축으로 압축됐다.
- `ui_skill/item/entry12` 는 `ui_or_item_plain_00_record`, `battle/ability/material` 은 `term_description_plain_00_optional_0b`, `credits` 는 `credits_padded_plain_00_record` family 로 부분 확정했다.
- image-side 감사는 [confirmed_data/image_inventory/README.md](/Users/user/test/confirmed_data/image_inventory/README.md) 기준으로 시작됐다.
- 이미지 추출 준비 파이프라인은 [image_extraction_pipeline.md](/Users/user/test/confirmed_data/image_inventory/image_extraction_pipeline.md) 에 정리한다.
- image-side 감사는 이제 `review bucket` 이 아니라 `title_logo_wordmark / event_or_cutscene_text_cards / ui_panel_label_art / battle_result_or_reward_banners` 같은 **review unit** 기준으로 본다.
- 현재 GUI 기준 확정 한글화 이미지 작업 항목은 `0`개다. 하지만 이는 정적 contact sheet 기준 확정 항목이 없다는 뜻이며, 실제 플레이에서 보이는 미번역 이미지/타일은 [runtime_visual_asset_audit.md](/Users/user/test/confirmed_data/image_inventory/runtime_visual_asset_audit.md) 로 다시 추적한다.
- 지금까지 확인된 정적 후보들은 대체로 배경/연출/캐릭터/프레임/폰트 자산이며, `0x00534874` 는 전투 HUD 소형 폰트/글리프 시트로 분류했다.
- 전투 HUD 소형 폰트 후보 `0x00534874` 는 영문판 ROM 에서 동일 블록을 추출해 현재 review ROM 에 후처리 적용한다. 스크립트는 [apply_english_battle_hud_font.py](/Users/user/test/scripts/apply_english_battle_hud_font.py) 이다.
- 각 image review unit 의 세부 단위, 탐색 방식, 작업 폴더는 [image_text_inventory.md](/Users/user/test/confirmed_data/image_inventory/image_text_inventory.md) 를 본다.
- image-side 우선 review order 는 `title_logo_wordmark -> title_screen_static_menu_wordmarks -> event_or_cutscene_text_cards -> dialogue_window_frame_art` 순이다.
- `system_messages` / `save_menu` 는 residual runtime uncertainty 가 남아도, 현재는 **operationally bounded** 로 내려가 주요 blocker 에서 제외한다.
- 따라서 남은 핵심은 “대사 source 의 record 경계”보다 **runtime dialogue box/page family** 와 **실플레이/이미지 텍스트 감사** 쪽이다.
- `analysis/dialogue_speaker_probe.md` 는 representative dialogue scene `2`개에서 각 레코드 직전 control-gap 을 뽑은 첫 speaker-state 추적 산출물이다.
- 짧은 반복 gap (`04 FF 05 FF 0A 00` 등) 만 낀 연속 레코드는 같은 active speaker/turn 후보로, 더 큰 gap (`1B FF`, `2B FF` 포함) 전환은 state-change 후보로 추적할 수 있다.
- [confirmed_data/dialogue_metadata](/Users/user/test/confirmed_data/dialogue_metadata/README.md) 에는 source-wide `dialogue_state_token` 과 contiguous `state run` sidecar 가 생성된다.

## 지금 우선순위

1. 대사 계열 runtime dialogue box/page family 추가 연결
2. portrait/dialogue scene 의 control-gap 기반 speaker-state 추적
3. 남은 텍스트 추출 감사 마감
4. Galmuri11 기준 재삽입/QA 루프 고정
5. 번역/검수 workset 운영
6. 이미지/타일 후보 추가 분류 및 예외 자산 추적
7. 자동 재삽입 + 수동 glyph 수정 루프

## 바로 쓰는 파일

- 전체 추출 기준본: [all_extracted_texts_master.json](/Users/user/test/confirmed_data/translation_workspace/all_extracted_texts_master.json)
- 번역 작업 허브: [confirmed_data/translation_workspace/README.md](/Users/user/test/confirmed_data/translation_workspace/README.md)
- workset 메타데이터 인덱스: [workset_metadata_index.md](/Users/user/test/confirmed_data/translation_workspace/workset_metadata_index.md)
- 로컬라이제이션 작업대 안내: [localization_workbench.md](/Users/user/test/docs/localization_workbench.md)
- 로컬라이제이션 작업대 데이터: [workbench_dataset.json](/Users/user/test/confirmed_data/localization_workbench/workbench_dataset.json)
- 고정 리뷰 ROM: [hnr_localization_review.gba](/Users/user/test/patched_roms/current_review/hnr_localization_review.gba)
- 번역 시작 가능 상태 요약: [translation_readiness_report.md](/Users/user/test/confirmed_data/translation_workspace/translation_readiness_report.md)
- 사용자 QA 안내: [user_qa_guide.md](/Users/user/test/docs/user_qa_guide.md)
- startup intro `4`줄: [startup_intro_texts.json](/Users/user/test/confirmed_data/extracted_texts/startup_intro_texts.json)
- 첫 화면 비교용 `4`줄: [translation_workset_startup_font_showcase.json](/Users/user/test/confirmed_data/translation_worksets/translation_workset_startup_font_showcase.json)
- 확장 intro 테스트 세트: [translation_workset_intro_full_test.json](/Users/user/test/confirmed_data/translation_worksets/translation_workset_intro_full_test.json)
- 현재 startup active workbench: [startup_intro_active_workbench](/Users/user/test/analysis/startup_intro_active_workbench)
- glyph 편집 툴: [glyph_editor.html](/Users/user/test/tools/glyph_editor.html)

## 바로 쓰는 명령

startup active workbench 재생성:

```bash
zsh scripts/rebuild_active_workbenches_from_atlas.sh
```

startup intro 테스트 ROM:

```bash
zsh scripts/build_startup_intro_test.sh \
  "Hagane no Renkinjutsushi - Meisou no Rondo (Japan).gba" \
  patched_roms/startup_intro_active
```

후보 `3`개 startup showcase ROM 일괄 생성:

```bash
python3 scripts/build_finalist_startup_tests.py
```

위 명령으로 생성된 비교용 GBA 모음:

- [finalists](/Users/user/test/patched_roms/font_compare/finalists)

확장 intro 테스트 ROM:

```bash
zsh scripts/build_intro_full_test.sh \
  "Hagane no Renkinjutsushi - Meisou no Rondo (Japan).gba" \
  patched_roms/intro_full_active
```

활성 atlas 로 임의 번역 JSON subset workbench 생성:

```bash
python3 scripts/build_workbench_from_active_atlas.py \
  analysis/generated_workbenches/<slug> \
  <translation-json>
```

활성 atlas 로 번역 ROM 생성:

```bash
zsh scripts/build_translated_rom_with_active_atlas.sh \
  "Hagane no Renkinjutsushi - Meisou no Rondo (Japan).gba" \
  <translation-json> \
  <output-dir> \
  <slug>
```

로컬라이제이션 작업대 데이터 재생성:

```bash
python3 scripts/build_localization_workbench_dataset.py
```

로컬라이제이션 작업대 GUI:

```bash
python3 scripts/run_localization_workbench.py
```

## 추출 상태

- 주요 텍스트 소스는 대부분 확보됐다.
- 남은 일은 대형 신규 뱅크 탐색보다 **실플레이 기반 누락 회수와 예외 정리**에 가깝다.
- 추출 커버리지 기준은 [text_extraction_coverage.md](/Users/user/test/analysis/text_extraction_coverage.md) 를 본다.
- [extraction_audit_status.json](/Users/user/test/confirmed_data/translation_workspace/extraction_audit_status.json) 기준으로, known source 의 **구조적 추출은 닫힌 상태**다.
- `image_text_inventory` 는 더 이상 `pending` 만이 아니라 **started / in_progress** 상태다.

## 주의

- 예전 벡터 seed 실험, compact test, placeholder glyph 결과는 [analysis/archive/font_trials](/Users/user/test/analysis/archive/font_trials) 아래로 내렸다.
- 새 세션에서는 `analysis` 루트를 통째로 읽지 말고, 필요한 경우 [analysis/README.md](/Users/user/test/analysis/README.md) 로 들어간다.
