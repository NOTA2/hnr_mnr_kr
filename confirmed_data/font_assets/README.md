# Active Hangul Font Assets

이 폴더는 **현재 확정된 한글 폰트 기준**만 둔다.

지금 프로젝트의 active 한글 폰트 소스는 사용자가 선택한 `12x12` 비트맵 atlas 다.

## 기준 파일

- profile: [active_hangul_font_profile.json](/Users/user/test/confirmed_data/font_assets/active_hangul_font_profile.json)
- atlas source: [maruminyahangul_12x12.png](/Users/user/test/third_party/font_atlases/maruminyahangul_12x12.png)
- atlas metadata: [maruminyahangul_12x12.metadata.json](/Users/user/test/third_party/font_atlases/maruminyahangul_12x12.metadata.json)

## 원칙

- 앞으로 한글 glyph seed 는 이 atlas 하나를 기준으로 만든다.
- 벡터 폰트 seed 실험 결과는 archive 로 내리고, active 경로에서는 쓰지 않는다.
- 전체 `11172`자를 ROM 에 한 번에 넣는 것이 아니라, **실제 번역 JSON 에서 쓰인 한글만 추출해 subset glyph set** 을 만든다.

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
