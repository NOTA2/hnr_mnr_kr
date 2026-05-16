# Analysis Guide

이 폴더는 **작업 산출물 전체 보관소**지만, 이제는 `hot path` 와 `archive` 를 분리해 두었다.

토큰을 아끼려면 이 폴더를 통째로 읽지 말고, 아래 순서만 따른다.

## First Open

- 텍스트 추출 상태: [text_extraction_coverage.md](/Users/user/test/analysis/text_extraction_coverage.md)
- 폰트/한글 전략: [common_fnt_hangul_strategy.md](/Users/user/test/analysis/common_fnt_hangul_strategy.md)
- 공통 렌더러 경로: [text_renderer_path.md](/Users/user/test/analysis/text_renderer_path.md)
- 현재 테스트 ROM 기준: [core_ui_test_rom_matrix.md](/Users/user/test/analysis/core_ui_test_rom_matrix.md)

## Active Text

- 뱅크/소스 요약: [text_bank_inventory.md](/Users/user/test/analysis/text_bank_inventory.md)
- 추출 100% 판정 기준: [text_extraction_coverage.md](/Users/user/test/analysis/text_extraction_coverage.md)
- Registry A entry `8` 장면 지도: [registry_a_entry8_cluster_overview.md](/Users/user/test/analysis/registry_a_entry8_cluster_overview.md)
- 시작 화면 첫 QA 세트: [startup_intro_texts.json](/Users/user/test/analysis/startup_intro_texts.json)

## Active Font

- 공통 폰트 경로: [text_renderer_path.md](/Users/user/test/analysis/text_renderer_path.md)
- 한글 전략: [common_fnt_hangul_strategy.md](/Users/user/test/analysis/common_fnt_hangul_strategy.md)
- 현재 매핑 감사 JSON: [common_fnt_usage_audit.json](/Users/user/test/analysis/common_fnt_usage_audit.json)
- core UI workbench: [hangul_core_ui_workbench](/Users/user/test/analysis/hangul_core_ui_workbench)
- 시작 화면 전용 workbench: [startup_intro_nanumsquare_workbench](/Users/user/test/analysis/startup_intro_nanumsquare_workbench)

## Stable References

- 구조 초기 요약: [initial_findings.md](/Users/user/test/analysis/initial_findings.md)
- registry 구조: [resource_registry_map.md](/Users/user/test/analysis/resource_registry_map.md)
- registry helper: [registry_accessor_helpers.md](/Users/user/test/analysis/registry_accessor_helpers.md)
- world-map / location: [location_bundle_family.md](/Users/user/test/analysis/location_bundle_family.md)
- effect/overlay 흐름: [effect_overlay_index_flow.md](/Users/user/test/analysis/effect_overlay_index_flow.md)

## Archive

- raw disassembly / caller / helper / scratch evidence 는 [archive/README.md](/Users/user/test/analysis/archive/README.md) 아래로 내렸다.
- 현재 루트에는 **지금도 직접 여는 요약, workbench, 적용 리포트, 주요 추출본** 만 남긴다.

## 운영 규칙

- `.json` 대형 파일은 직접 열지 말고 필요한 키/범위만 `gba_kor_tool` 이나 짧은 조회 명령으로 본다.
- raw evidence 가 필요할 때만 `analysis/archive/` 아래를 연다.
- 새 세션 기본 시작점은 이 폴더가 아니라 [session_start.md](/Users/user/test/docs/session_start.md) 다.
