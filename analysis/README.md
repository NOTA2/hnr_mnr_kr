# Analysis Guide

이 폴더는 **작업 산출물 전체 보관소**다.

토큰을 아끼려면 이 폴더를 통째로 읽지 말고, 아래 우선순위대로 필요한 문서만 연다.

## 지금 가장 자주 보는 문서

- 텍스트 추출 커버리지: [text_extraction_coverage.md](/Users/user/test/analysis/text_extraction_coverage.md)
- 공통 폰트 한글 전략: [common_fnt_hangul_strategy.md](/Users/user/test/analysis/common_fnt_hangul_strategy.md)
- 공통 텍스트 렌더러 경로: [text_renderer_path.md](/Users/user/test/analysis/text_renderer_path.md)
- 긴 실험 로그: [experiment_log.md](/Users/user/test/analysis/experiment_log.md)

## Text

- 뱅크/소스 요약: [text_bank_inventory.md](/Users/user/test/analysis/text_bank_inventory.md)
- 추출 100% 판정 기준: [text_extraction_coverage.md](/Users/user/test/analysis/text_extraction_coverage.md)
- entry `8` 장면 지도: [registry_a_entry8_cluster_overview.md](/Users/user/test/analysis/registry_a_entry8_cluster_overview.md)

## Font

- 공통 폰트 경로: [text_renderer_path.md](/Users/user/test/analysis/text_renderer_path.md)
- 한글 전략: [common_fnt_hangul_strategy.md](/Users/user/test/analysis/common_fnt_hangul_strategy.md)
- 현재 매핑 감사 JSON: [common_fnt_usage_audit.json](/Users/user/test/analysis/common_fnt_usage_audit.json)
- relocation 테스트 보고서: [font_chunk_relocation_test.json](/Users/user/test/analysis/font_chunk_relocation_test.json)

## Cold Structure

- registry 구조: [resource_registry_map.md](/Users/user/test/analysis/resource_registry_map.md)
- registry helper: [registry_accessor_helpers.md](/Users/user/test/analysis/registry_accessor_helpers.md)
- world-map / location: [location_bundle_family.md](/Users/user/test/analysis/location_bundle_family.md)
- effect/overlay 흐름: [effect_overlay_index_flow.md](/Users/user/test/analysis/effect_overlay_index_flow.md)

## 운영 규칙

- `.json` 대형 파일은 직접 열지 말고 필요한 키/범위만 짧은 스크립트나 `gba_kor_tool` 로 조회한다.
- 오래된 구조 분석은 삭제하지 않고 `Cold Structure` 로 내린다.
- 새 세션 기본 시작점은 이 폴더가 아니라 [session_start.md](/Users/user/test/docs/session_start.md) 다.
