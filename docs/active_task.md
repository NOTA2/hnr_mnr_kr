# Active Task

이 파일은 **매 세션 시작 때 읽는 짧은 작업 카드**다.

## 현재 상태

- 한글 폰트 최종 후보군은 `3`개다.
  - `MaruMinyaHangul (12px)`
  - `Galmuri11 (12px)`
  - `GalmuriMono (12px)`
- 현재 active 기본값은 [maruminyahangul_12x12.png](/Users/user/test/third_party/font_atlases/maruminyahangul_12x12.png) 이고, 후보 원본 3개는 [finalists](/Users/user/test/third_party/font_atlases/finalists) 아래에 프로젝트 로컬로 복사해 두었다.
- 후보군 메타데이터와 export 기준은 [finalist_font_candidates.json](/Users/user/test/confirmed_data/font_assets/finalist_font_candidates.json), [finalist_export_recommendation.md](/Users/user/test/confirmed_data/font_assets/finalist_export_recommendation.md) 에 있다.
- 새 후보 bitmap PNG 에서 **반드시 필요한 것**은 `가..힣` 완성형 `11,172`자 atlas 다.
- 숫자/영문/기본 기호는 1차 한글화 기준으로 **원본 게임 공통 폰트**를 그대로 재사용한다.
- 첫 화면 즉시 비교용 startup showcase 세트는 [translation_workset_startup_font_showcase.json](/Users/user/test/confirmed_data/translation_worksets/translation_workset_startup_font_showcase.json) 이다.
- startup 비교 문구는 현재 원문 의미를 유지한 `대륙력 / １９１０년 ２월 / 리젠불 마을 / 형１１세 동생１０세` 기준으로 맞추고 있다.
- atlas importer 는 PNG 의 밝은 본체와 그림자 역할을 게임 원본 단계인 `0 / 17 / 34` 로 매핑하되, **이 화면에서는 밝은 본체가 `17`, 그림자가 `34` 역할** 이 되도록 반대로 넣는다.

## 지금 우선순위

1. 후보 `3`개 startup intro 비교
2. 폰트 확정
3. 남은 텍스트 추출 감사 마감
4. 번역/검수 workset 운영
5. 자동 재삽입 + 수동 glyph 수정 루프

## 바로 쓰는 파일

- 전체 추출 기준본: [all_extracted_texts_master.json](/Users/user/test/confirmed_data/translation_workspace/all_extracted_texts_master.json)
- 번역 작업 허브: [confirmed_data/translation_workspace/README.md](/Users/user/test/confirmed_data/translation_workspace/README.md)
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

## 추출 상태

- 주요 텍스트 소스는 대부분 확보됐다.
- 남은 일은 대형 신규 뱅크 탐색보다 **실플레이 기반 누락 회수와 예외 정리**에 가깝다.
- 추출 커버리지 기준은 [text_extraction_coverage.md](/Users/user/test/analysis/text_extraction_coverage.md) 를 본다.

## 주의

- 예전 벡터 seed 실험, compact test, placeholder glyph 결과는 [analysis/archive/font_trials](/Users/user/test/analysis/archive/font_trials) 아래로 내렸다.
- 새 세션에서는 `analysis` 루트를 통째로 읽지 말고, 필요한 경우 [analysis/README.md](/Users/user/test/analysis/README.md) 로 들어간다.
