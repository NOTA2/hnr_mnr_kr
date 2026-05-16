# Font Asset Workflow

이 문서는 **정식 한글 글리프 제작 방식**을 짧게 정리한 문서다.

## 원칙

- 임시 검증용 glyph 와 정식 glyph 를 구분한다.
- 임시 검증용 glyph 는 렌더러/매핑 확인용일 뿐, 최종 자산으로 쓰지 않는다.
- 정식 glyph 는 **레퍼런스 기반 + 외부 픽셀 에디터 수정** 흐름으로 만든다.

## 권장 흐름

1. seed manifest 를 만든다.
2. `prepare-fnt-glyph-set` 으로 편집용 `PGM` glyph 세트와 `.tbl` 을 뽑는다.
3. `audit-pgm-glyph-set` 으로 blank glyph 가 없는지 먼저 검사한다.
4. 외부 픽셀 에디터에서 `12x12` glyph 를 수정한다.
5. 수정한 `PGM` 들을 `append-fnt-glyph-set` 으로 ROM 에 다시 넣는다.
6. 짧은 문자열 치환으로 먼저 검증한다.
7. 그 다음에 더 긴 inject / repoint 테스트로 넘어간다.

## 레퍼런스 폰트 기반 seed

- AI가 즉석으로 그리는 대신, **실제 폰트에서 seed glyph 를 뽑고 그걸 손보는 방식** 을 우선한다.
- 현재는 macOS 설치 폰트 이름을 기준으로 seed 를 뽑는 [render_reference_font_workbench.swift](/Users/user/test/scripts/render_reference_font_workbench.swift) 도 추가했다.
- 이 스크립트는 최종 자산 생성기라기보다, `12x12` workbench 의 **첫 초안(seed)** 을 만드는 용도다.

## 현재 예시 파일

- seed manifest: [hangul_reference_seed_manifest.json](/Users/user/test/analysis/hangul_reference_seed_manifest.json)
- 테스트 glyph manifest: [hangul_test_manifest.json](/Users/user/test/analysis/hangul_test_manifest.json)
- 테스트 table: [hangul_test.tbl](/Users/user/test/analysis/hangul_test.tbl)
- core UI seed manifest: [hangul_core_ui_seed_manifest.json](/Users/user/test/analysis/hangul_core_ui_seed_manifest.json)
- core UI workbench: [hangul_core_ui_workbench](/Users/user/test/analysis/hangul_core_ui_workbench)
- core UI priority plan: [hangul_core_ui_priority_plan.md](/Users/user/test/analysis/hangul_core_ui_priority_plan.md)

## 유용한 명령

```bash
zsh scripts/build_startup_intro_test.sh \
  "Hagane no Renkinjutsushi - Meisou no Rondo (Japan).gba" \
  patched_roms/rebuild_check

zsh scripts/build_core_ui_test_roms.sh \
  "Hagane no Renkinjutsushi - Meisou no Rondo (Japan).gba" \
  patched_roms/rebuild_check

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

python3 -m gba_kor_tool audit-pgm-glyph-set \
  analysis/hangul_core_ui_workbench/prepared_manifest.json \
  --fail-on-blank

swift scripts/render_reference_font_workbench.swift \
  --font-name "Apple SD Gothic Neo" \
  --manifest analysis/startup_intro_missing_manifest.json \
  --output-dir /tmp/startup_font_seed \
  --report /tmp/startup_font_seed_report.json
```

## 메모

- production 단계에서는 AI가 즉석으로 만든 block glyph 를 다시 사용하지 않는다.
- 외부 툴에서 수정한 `PGM` 을 단일 truth source 로 보고, ROM 패치는 그 산출물만 사용한다.
- `build-hangul-seed-manifest` 는 번역 초안에서 실제 필요한 한글 글자를 뽑아 workbench 규모를 자동으로 정하는 용도다.
- 현재는 `priority48` workbench 가 첫 실제 문자열 테스트용으로 가장 현실적인 크기다.
- blank glyph 가 하나라도 남아 있으면, 빌드가 되더라도 화면에서 조용히 빈칸처럼 보일 수 있다.
- 그래서 이제는 `audit-pgm-glyph-set` 로 **비어 있는 glyph 를 먼저 잡는 것** 을 기본 절차로 둔다.
- 최종 자산은 공개 라이선스 폰트를 기준으로 뽑는 편이 안전하다. 특히 `12x12` 계열에선 픽셀풍인 `Galmuri` 가 유리하고, 일반 UI 기준으론 `Pretendard` 나 `Noto Sans KR` 를 seed 로 쓴 뒤 수동 보정하는 방식이 현실적이다.
- test ROM 적용 결과와 compact 대체 문구 기준은 [core_ui_test_rom_matrix.md](/Users/user/test/analysis/core_ui_test_rom_matrix.md) 를 본다.
- legacy placeholder glyph (`hangul_test_ga.pgm` 등) 는 더 이상 production test 기준으로 보지 않는다.
- 게임 시작 직후 바로 확인할 첫 QA 지점은 [startup_intro_texts.json](/Users/user/test/analysis/startup_intro_texts.json) / `/Users/user/test/patched_roms/rebuild_check/hnr_startup_intro_test.gba` 쪽이다.
- 시작 화면만 빠르게 다시 만들려면 [build_startup_intro_test.sh](/Users/user/test/scripts/build_startup_intro_test.sh) 를 먼저 쓴다.
