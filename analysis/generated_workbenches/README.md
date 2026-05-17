# Generated Workbenches

이 폴더는 **active Hangul atlas** 기준으로, 실제 번역 JSON 에서 필요한 글자만 뽑아 만든 subset workbench 보관용이다.

핵심 명령:

```bash
python3 scripts/build_workbench_from_active_atlas.py \
  analysis/generated_workbenches/<slug> \
  <translation-json> [...]
```

기본 규칙:

- glyph source 는 [active_hangul_font_profile.json](/Users/user/test/confirmed_data/font_assets/active_hangul_font_profile.json) 를 따른다.
- 결과물은 `seed_manifest.json`, `prepared_manifest.json`, `prepared.tbl`, `workbench_report.json` 이다.
- 이 폴더의 workbench 는 **실제 번역 subset** 이므로, startup intro active workbench 와는 역할이 다르다.
