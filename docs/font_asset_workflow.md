# Font Asset Workflow

이 문서는 **정식 한글 글리프 제작 방식**을 짧게 정리한 문서다.

## 원칙

- 임시 검증용 glyph 와 정식 glyph 를 구분한다.
- 임시 검증용 glyph 는 렌더러/매핑 확인용일 뿐, 최종 자산으로 쓰지 않는다.
- 정식 glyph 는 **레퍼런스 기반 + 외부 픽셀 에디터 수정** 흐름으로 만든다.

## 권장 흐름

1. seed manifest 를 만든다.
2. `prepare-fnt-glyph-set` 으로 편집용 `PGM` glyph 세트와 `.tbl` 을 뽑는다.
3. 외부 픽셀 에디터에서 `12x12` glyph 를 수정한다.
4. 수정한 `PGM` 들을 `append-fnt-glyph-set` 으로 ROM 에 다시 넣는다.
5. 짧은 문자열 치환으로 먼저 검증한다.
6. 그 다음에 더 긴 inject / repoint 테스트로 넘어간다.

## 현재 예시 파일

- seed manifest: [hangul_reference_seed_manifest.json](/Users/user/test/analysis/hangul_reference_seed_manifest.json)
- 테스트 glyph manifest: [hangul_test_manifest.json](/Users/user/test/analysis/hangul_test_manifest.json)
- 테스트 table: [hangul_test.tbl](/Users/user/test/analysis/hangul_test.tbl)
- core UI seed manifest: [hangul_core_ui_seed_manifest.json](/Users/user/test/analysis/hangul_core_ui_seed_manifest.json)
- core UI workbench: [hangul_core_ui_workbench](/Users/user/test/analysis/hangul_core_ui_workbench)
- core UI priority plan: [hangul_core_ui_priority_plan.md](/Users/user/test/analysis/hangul_core_ui_priority_plan.md)

## 유용한 명령

```bash
zsh scripts/build_core_ui_test_roms.sh \
  "Hagane no Renkinjutsushi - Meisou no Rondo (Japan).gba" \
  /private/tmp/hnr_rebuild_check

python3 -m gba_kor_tool prepare-fnt-glyph-set \
  "Hagane no Renkinjutsushi - Meisou no Rondo (Japan).gba" \
  0x3E0000 \
  --manifest analysis/hangul_reference_seed_manifest.json \
  --output-dir analysis/hangul_reference_workbench \
  --report analysis/hangul_reference_workbench_report.json

python3 -m gba_kor_tool append-fnt-glyph-set \
  /private/tmp/hnr_font_expand_test_mirror.gba \
  /private/tmp/hnr_font_hangul_artist_test.gba \
  0x800000 \
  --payload-length 0x42000 \
  --manifest analysis/hangul_reference_workbench/prepared_manifest.json \
  --report analysis/hangul_artist_append_report.json

python3 -m gba_kor_tool build-hangul-seed-manifest \
  analysis/hangul_core_ui_seed_manifest.json \
  analysis/translation_workset_core_ui.json \
  --field translation \
  --start-code 0xE940 \
  --table-output analysis/hangul_core_ui.tbl \
  --report analysis/hangul_core_ui_seed_report.json

python3 -m gba_kor_tool prepare-fnt-glyph-set \
  "Hagane no Renkinjutsushi - Meisou no Rondo (Japan).gba" \
  0x3E0000 \
  --manifest analysis/hangul_core_ui_seed_manifest.json \
  --output-dir analysis/hangul_core_ui_workbench \
  --report analysis/hangul_core_ui_workbench_report.json
```

## 메모

- production 단계에서는 AI가 즉석으로 만든 block glyph 를 다시 사용하지 않는다.
- 외부 툴에서 수정한 `PGM` 을 단일 truth source 로 보고, ROM 패치는 그 산출물만 사용한다.
- `build-hangul-seed-manifest` 는 번역 초안에서 실제 필요한 한글 글자를 뽑아 workbench 규모를 자동으로 정하는 용도다.
- 현재는 `priority48` workbench 가 첫 실제 문자열 테스트용으로 가장 현실적인 크기다.
- test ROM 적용 결과와 compact 대체 문구 기준은 [core_ui_test_rom_matrix.md](/Users/user/test/analysis/core_ui_test_rom_matrix.md) 를 본다.
- legacy placeholder glyph (`hangul_test_ga.pgm` 등) 는 더 이상 production test 기준으로 보지 않는다.
- 게임 시작 직후 바로 확인할 첫 QA 지점은 [startup_intro_texts.json](/Users/user/test/analysis/startup_intro_texts.json) / `/private/tmp/hnr_rebuild_check/hnr_startup_intro_test.gba` 쪽이다.
