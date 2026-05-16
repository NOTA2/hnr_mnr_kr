# Startup Intro Font Compare

2026-05-16 기준 시작 화면 `14`글자 startup intro 비교 메모.

## 비교 ROM

- D2Coding: [hnr_startup_intro_d2coding.gba](/Users/user/test/patched_roms/font_compare/hnr_startup_intro_d2coding.gba)
- Source Han Sans KR: [hnr_startup_intro_source_han_sans_kr.gba](/Users/user/test/patched_roms/font_compare/hnr_startup_intro_source_han_sans_kr.gba)
- Source Han Mono KR: [hnr_startup_intro_source_han_mono_kr.gba](/Users/user/test/patched_roms/font_compare/hnr_startup_intro_source_han_mono_kr.gba)

## 비교 시트

- glyph 시트: [startup_intro_font_compare_sheet.png](/Users/user/test/analysis/startup_intro_font_compare_sheet.png)
- nonzero pixel 요약: [startup_intro_font_compare_summary.json](/Users/user/test/analysis/startup_intro_font_compare_summary.json)

## 적용 가능 여부

- `gba-free-fonts` 는 **직접 적용 불가** 가 아니라, `.fnt + atlas png` 를 우리 `12x12 PGM workbench` 로 바꾸는 변환 단계가 필요했다.
- 이번에 [import_bmfont_workbench.py](/Users/user/test/scripts/import_bmfont_workbench.py) 로 그 변환 단계를 추가했기 때문에, `SourceHanSansKR` 와 `SourceHanMonoKR` 는 이제 startup intro 비교가 가능하다.
- 반면 `LanaPixel` 은 공식 배포 페이지가 자동 다운로드에 걸려 현재 세션에서 원본 파일을 안정적으로 확보하지 못했다.
- 즉 `LanaPixel` 은 **포맷 문제** 가 아니라 **원본 파일 부재 문제** 다. 파일만 확보되면 현재 workflow 에 바로 넣을 수 있다.

## 현재 판단

- `SourceHanSansKR`, `SourceHanMonoKR` 는 모두 startup intro 에 실제 적용 가능하다.
- 다만 현재 `12x12` binary seed 기준에서는 두 후보 모두 획 밀도가 높아, 시작 화면에선 `D2Coding` 보다 더 뭉개져 보일 가능성이 높다.
- 그래서 현재 active 기준은 계속 `D2Coding 20% cutoff` 를 유지한다.
