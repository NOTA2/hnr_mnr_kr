# 현재 한글 폰트 자산

이 폴더는 **현재 작업에 직접 쓰는 한글 폰트 기준**과 **최종 후보군 메타데이터**를 둔다.

현재 기본값은 `Galmuri11 (12px)` 아틀라스이고, 비교 후보군은 아래 `3`개였다.

- `MaruMinyaHangul (12px)`
- `Galmuri11 (12px)`
- `GalmuriMono (12px)`

## 기준 파일

- 프로필: [active_hangul_font_profile.json](/Users/user/test/confirmed_data/font_assets/active_hangul_font_profile.json)
- 아틀라스 원본: [galmuri11_12x12.png](/Users/user/test/third_party/font_atlases/finalists/galmuri11_12x12.png)
- 아틀라스 메타데이터: [galmuri11_12x12.metadata.json](/Users/user/test/third_party/font_atlases/finalists/galmuri11_12x12.metadata.json)
- 최종 후보 목록: [finalist_font_candidates.json](/Users/user/test/confirmed_data/font_assets/finalist_font_candidates.json)
- 추출 권장 규칙: [finalist_export_recommendation.md](/Users/user/test/confirmed_data/font_assets/finalist_export_recommendation.md)

## 원칙

- 앞으로 한글 glyph seed 는 이 아틀라스 하나를 기준으로 만든다.
- 최종 기본 기준은 `Galmuri11 (12px)` 이다.
- 벡터 폰트 seed 실험 결과는 archive 로 내리고, 현재 작업 경로에서는 쓰지 않는다.
- 전체 `11172`자를 ROM 에 한 번에 넣는 것이 아니라, **실제 번역 JSON 에서 쓰인 한글만 추출해 부분 glyph 세트** 를 만든다.
- 숫자/영문/기본 기호는 1차 한글화 기준 **원본 게임 공통 폰트**를 그대로 쓴다.

## 핵심 스크립트

```bash
python3 scripts/build_workbench_from_active_atlas.py \
  analysis/generated_workbenches/core_ui_active \
  confirmed_data/translation_worksets/translation_workset_core_ui.json

zsh scripts/build_translated_rom_with_active_atlas.sh \
  "Hagane no Renkinjutsushi - Meisou no Rondo (Japan).gba" \
  confirmed_data/translation_worksets/translation_workset_core_ui.json \
  patched_roms/core_ui_active
```
