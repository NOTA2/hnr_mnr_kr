# 분석 안내

이 폴더는 **탐색/가설/실험용 분석 보관소**다. 확정된 canonical 텍스트와 번역 workspace 는 이제 [confirmed_data](/Users/user/test/confirmed_data/README.md) 아래로 분리했다.

토큰을 아끼려면 이 폴더를 통째로 읽지 말고, 아래 순서만 따른다.

## 먼저 열기

- 텍스트 추출 상태: [text_extraction_coverage.md](/Users/user/test/analysis/text_extraction_coverage.md)
- 폰트/한글 전략: [common_fnt_hangul_strategy.md](/Users/user/test/analysis/common_fnt_hangul_strategy.md)
- 공통 렌더러 경로: [text_renderer_path.md](/Users/user/test/analysis/text_renderer_path.md)
- 현재 startup intro active workbench: [startup_intro_active_workbench](/Users/user/test/analysis/startup_intro_active_workbench)

## 현재 텍스트

- 뱅크/소스 요약: [text_bank_inventory.md](/Users/user/test/analysis/text_bank_inventory.md)
- 추출 100% 판정 기준: [text_extraction_coverage.md](/Users/user/test/analysis/text_extraction_coverage.md)
- Registry A entry `8` 장면 지도: [registry_a_entry8_cluster_overview.md](/Users/user/test/analysis/registry_a_entry8_cluster_overview.md)
- 확정 추출본은 [confirmed_data/extracted_texts](/Users/user/test/confirmed_data/extracted_texts/README.md) 아래를 본다.

## 현재 폰트

- 공통 폰트 경로: [text_renderer_path.md](/Users/user/test/analysis/text_renderer_path.md)
- 한글 전략: [common_fnt_hangul_strategy.md](/Users/user/test/analysis/common_fnt_hangul_strategy.md)
- 현재 매핑 감사 JSON: [common_fnt_usage_audit.json](/Users/user/test/analysis/common_fnt_usage_audit.json)
- 시작 화면 전용 active workbench: [startup_intro_active_workbench](/Users/user/test/analysis/startup_intro_active_workbench)
- 실제 번역 subset workbench: [generated_workbenches](/Users/user/test/analysis/generated_workbenches/README.md)
- active atlas profile 은 [confirmed_data/font_assets](/Users/user/test/confirmed_data/font_assets/README.md) 를 본다.

## 안정 참조 문서

- 구조 초기 요약: [initial_findings.md](/Users/user/test/analysis/initial_findings.md)
- registry 구조: [resource_registry_map.md](/Users/user/test/analysis/resource_registry_map.md)
- registry helper: [registry_accessor_helpers.md](/Users/user/test/analysis/registry_accessor_helpers.md)
- world-map / location: [location_bundle_family.md](/Users/user/test/analysis/location_bundle_family.md)
- effect/overlay 흐름: [effect_overlay_index_flow.md](/Users/user/test/analysis/effect_overlay_index_flow.md)

## 보관 문서

- cleanup 전에 `analysis/` 전체의 keep/hold/delete-local 기준은
  [analysis_retention_matrix.md](/Users/user/test/docs/cleanup/analysis_retention_matrix.md) 를 본다.
- raw disassembly / caller / helper / scratch evidence 는 [archive/README.md](/Users/user/test/analysis/archive/README.md) 아래로 내렸다.
- 예전 폰트 후보 비교와 벡터 seed 실험은 [archive/font_trials/2026-05-17_pre_bitmap_lock](/Users/user/test/analysis/archive/font_trials/2026-05-17_pre_bitmap_lock) 아래로 내렸다.
- 예전 core UI compact ROM, seed manifest, placeholder glyph, startup 전용 임시 workbench 는 [archive/font_trials/2026-05-17_finalist_pool_cleanup](/Users/user/test/analysis/archive/font_trials/2026-05-17_finalist_pool_cleanup) 아래로 내렸다.
- 현재 루트에는 **지금도 직접 여는 요약, workbench, 적용 리포트, 탐색 결과** 만 남긴다.

## 운영 규칙

- canonical 번역 입력 데이터가 필요하면 먼저 [confirmed_data](/Users/user/test/confirmed_data/README.md) 를 연다.
- `.json` 대형 파일은 직접 열지 말고 필요한 키/범위만 `gba_kor_tool` 이나 짧은 조회 명령으로 본다.
- raw evidence 가 필요할 때만 `analysis/archive/` 아래를 연다.
- 새 세션 기본 시작점은 이 폴더가 아니라 [session_start.md](/Users/user/test/docs/session_start.md) 다.
