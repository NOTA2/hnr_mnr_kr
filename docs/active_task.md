# Active Task

이 파일은 **매 세션마다 읽는 작은 작업 카드**다.

지금부터는 데이터 구조 심화보다 **텍스트 추출 완료와 실제 한글화 작업 루프**를 우선한다.

## 현재 목표

- 아직 안 뽑힌 대사/이벤트 텍스트를 우선 회수하고, 번역 가능한 작업 세트로 정리한다.
- 한글 재삽입에 바로 필요한 폰트/인코딩 조건만 추가로 확보한다.

## 바로 필요한 사실

- 번역용 추출본은 이미 여러 개 있다.
- 핵심 추출본:
  - [system_messages.json](/Users/user/test/analysis/system_messages.json)
  - [save_menu_texts.json](/Users/user/test/analysis/save_menu_texts.json)
  - [location_texts.json](/Users/user/test/analysis/location_texts.json)
  - [ui_skill_texts.json](/Users/user/test/analysis/ui_skill_texts.json)
  - [item_texts.json](/Users/user/test/analysis/item_texts.json)
  - [battle_texts.json](/Users/user/test/analysis/battle_texts.json)
  - [ability_texts.json](/Users/user/test/analysis/ability_texts.json)
- [translation_workset_core_ui.json](/Users/user/test/analysis/translation_workset_core_ui.json) 는 `system + save + location + ui_skill` 을 합친 첫 작업용 세트다.
- 위 작업 세트는 `43`개 레코드이며, 시스템/세이브/지역명 앞부분은 이미 한국어 초안이 들어 있다.
- Registry D (`0x17C7E4..0x17CB04`) 는 한때 덜 추출된 대사/이벤트 텍스트의 핵심 후보였고, 지금은 전용 추출 규칙이 확보된 상태다.
- Registry D 물리 범위 `0x7F3000..0x7F96E9` 를 슬라이딩 스캔하면 현재 `305`개 대사성 문자열이 잡힌다.
- 전체본은 [registry_d_full_sliding_texts.json](/Users/user/test/analysis/registry_d_full_sliding_texts.json), 번역용 작업 세트는 [translation_workset_registry_d_dialogue.json](/Users/user/test/analysis/translation_workset_registry_d_dialogue.json) 에 있다.
- Registry D 의 많은 엔트리는 plain terminator 문자열이 아니라 `FC` 제어 바이트가 섞인 mixed script 형식이다.
- `scan-fc-script-text` 로 `FC 00 ... FC` anchor 기반 추출을 하면 [registry_d_fc_script_texts.json](/Users/user/test/analysis/registry_d_fc_script_texts.json) `244`건이 clean extraction 된다.
- 위 `244`건은 `82 / 100` 엔트리에서 나오고, per-entry 요약은 [registry_d_fc_script_summary.json](/Users/user/test/analysis/registry_d_fc_script_summary.json) 에 있다.
- 남은 [registry_d_unresolved_entries.json](/Users/user/test/analysis/registry_d_unresolved_entries.json) `18`개는 대부분 `2-byte sentinel/control stub` 이고, 현재 기준 실질적인 미추출 대사 후보는 거의 남지 않았다.
- entry `70` 도 raw bytes 재확인 결과 `FC` 가 매우 조밀한 command/control table 패턴이라, 현재는 **실질 대사 미추출 후보보다 control-only script table** 로 보는 해석이 더 강하다.
- 따라서 Registry D 는 이제 "나중에 다시 볼 미해결 대사 뱅크"가 아니라, **mixed-format 전용 추출 규칙이 잡힌 active extraction 대상** 이다.
- Registry A entry `8` (`0x6B594C..0x773248`) 는 지역명만 담긴 entry 가 아니라, `0x10` 종단 command-stream 대사/이벤트/메뉴가 함께 섞인 대형 mixed script bank 후보다.
- `Registry A entry 8` 안의 많은 대사는 `01 FF <u16 문자수>` 헤더 뒤에 `cp932` 본문이 오는 command-stream 구조로 보인다.
- 이 규칙으로 재추출한 [registry_a_entry8_prefixed_texts.json](/Users/user/test/analysis/registry_a_entry8_prefixed_texts.json) 은 현재 `9823`건이며, 초반 리오르 대사부터 진행 힌트/플래그 문구, save/menu 일부까지 광범위하게 포함한다.
- Registry A tail 중 entry `12` (`0x7A750C..0x7A8E98`) 은 현재 `22`건이 확인되어 [registry_a_entry12_texts.json](/Users/user/test/analysis/registry_a_entry12_texts.json) 으로 별도 확보했다.
- Registry A tail `9..17` 의 현재 분류는 [registry_a_tail_classification.json](/Users/user/test/analysis/registry_a_tail_classification.json) 에 정리했다.
- 상위 registry 단위 재검사 결과, 현재 `01 FF <u16 문자수>` 규칙이 강하게 잡힌 곳은 [prefixed_registry_scan_summary.json](/Users/user/test/analysis/prefixed_registry_scan_summary.json) 기준으로 **Registry A entry 8 하나뿐**이다.
- 따라서 다른 미추출 대사 구간은 같은 규칙의 반복이 아니라, 별도 mixed format / command stream 으로 우선 취급하는 편이 안전하다.
- Registry A entry 8 작업용 분할 지도는 [registry_a_entry8_cluster_summary.json](/Users/user/test/analysis/registry_a_entry8_cluster_summary.json) 에 있다.
- 현재 gap threshold `0x400` 기준 `72`개 클러스터로 나뉘며, 이후 번역/검수/재삽입은 이 클러스터 단위로 다루는 편이 좋다.
- 자동 태그/샘플이 붙은 상세 지도는 [registry_a_entry8_cluster_catalog.json](/Users/user/test/analysis/registry_a_entry8_cluster_catalog.json), 사람이 빠르게 보기 좋은 요약은 [registry_a_entry8_cluster_overview.md](/Users/user/test/analysis/registry_a_entry8_cluster_overview.md) 에 있다.
- cluster `71` 은 자동 태그상 `save_menu` 로 잡히지만, 실제로는 **일반 이벤트/진행 힌트 `228`건 + save/menu `12`건** 이 섞인 mixed hub 다.
- cluster `71` 의 save/menu 분리본은 [registry_a_entry8_cluster71_save_segment_texts.json](/Users/user/test/analysis/registry_a_entry8_cluster71_save_segment_texts.json) 이고, [save_menu_prefixed_texts.json](/Users/user/test/analysis/save_menu_prefixed_texts.json) 과 내용이 일치한다.
- cluster `71` 의 일반 이벤트/진행 힌트 분리본은 [registry_a_entry8_cluster71_pre_save_texts.json](/Users/user/test/analysis/registry_a_entry8_cluster71_pre_save_texts.json) 이다.
- 기존 [registry_a_entry8_terminator_10_texts.json](/Users/user/test/analysis/registry_a_entry8_terminator_10_texts.json) `1200`건은 entry 8 발견용 정찰 결과로 보관하고, 실제 작업은 prefixed 추출본을 우선한다.
- `save_menu_texts.json` 류는 종단 바이트가 `0x10` 이라서 일반 `00` 종단 문자열과 분리해서 다뤄야 한다.
- save/menu block `0x772E00..0x773260` 도 같은 규칙으로 [save_menu_prefixed_texts.json](/Users/user/test/analysis/save_menu_prefixed_texts.json) `12`건이 정리된다.
- 재삽입 도구 기본 기능은 이미 있다:
  - 같은 길이 이하 덮어쓰기
  - 자유 공간 주입
  - 포인터 갱신
  - `apply-translations` 일괄 반영
- 아직 **한글을 실제 ROM에 표시할 문자 매핑/재삽입 전략은 확보되지 않았다.**
- 다만 최근 확인으로는:
  - `0x0514xx` UI cluster 는 실제 문자 렌더러보다 **문자열 길이 기반 layout / slot setup** 경로에 가깝다.
  - `0x03EB78 / 0x03ECCC / 0x03EDB8` helper family 는 일반 일본어 렌더러가 아니라, `0x03003008` tilemap base 에 **ASCII/숫자 UI glyph** 를 찍는 쪽으로 보인다.
  - 따라서 이 helper family 는 **한글 폰트 원본/문자폭 경로 후보에서 우선 제외**한다.
  - world-map Registry B raw companion 엔트리 `86..89` 는 헤더 뒤를 바로 4bpp 로 덤프해도 글자판이 아니라 잡음이라, **직접 폰트 raw tiles** 후보에서는 우선 제외한다.
  - world-map 지역명 표시는 `0x06A95A..0x06A972` 에서 `0x18425C + location * 0x2C` 문자열 필드를 `0x014A98 -> 0x014ED0` 로 넘긴다.
  - `0x014A98` 는 문자 디코더라기보다 **text object / window entry setup helper** 에 가깝다.
  - `0x014ED0` 는 문자열 바이트를 직접 읽으며 `0x81..0x9F`, `0xE0..0xEF` 를 Shift-JIS multibyte lead byte 후보로, `0x20..0x7E` 를 ASCII / halfwidth 로 분기한다.
  - `0x015A4C..0x015A80` 는 `0x03001540 + index * 0x2C` text object `11`개를 순회하며 `0x014ED0` 을 호출한다.
  - `0x01499C` 는 font resource initializer 후보로, `obj + 0x04 = lookup base`, `obj + 0x08 = glyph base`, `obj + 0x1A = stride` 를 채운다.
  - 이 함수는 `resource[7] & 0x80` 에 따라 lookup base 에 `+0x40000` 을 더하고, glyph base 는 그 뒤 `+0x20000` 위치로 잡는다.
  - `0x000290 / 0x0002CC / 0x000304 / 0x00033C` 는 상위 resource loader family 이고, hub `0x076530` pointer table 에서 registry base 를 고른 뒤 `0x0A` record 의 pointer / length 를 꺼내 쓴다.
  - 현재 공통 font resource 후보는 `slot 1 / entry 0 = table 0x17C2F4 entry 0 = ROM 0x3E0000..0x41DDE7` 이다.
  - 이 payload 시작부에는 `fnt\\0` magic 이 보이고, header 의 `resource[8] = 0x48` 은 glyph stride 와 맞는다.
  - `0x0152A2..0x0152C4` 는 현재 문자코드 `u16` 를 `obj + 0x04` lookup table 로 바꾼 뒤, `obj + 0x1A` stride 와 `obj + 0x08` glyph base 로 실제 glyph source pointer 를 계산한다.
  - `0x01570C / 0x01578C / 0x01580C / 0x01588C` 는 이 glyph source 를 tile target 으로 복사하는 writer family 이고, `0x01590C` / `0x015984` 가 그 하위 halfword writer 다.
  - 현재까지 확인한 주요 text object 초기화 경로는 모두 `0x0002CC(0, 1)` 뒤 `0x01499C` 를 호출하므로, registry slot `1` entry `0` 공통 font resource 를 공유하는 해석이 가장 강하다.
  - writer loop 와 stride 를 함께 보면, 현재 가장 강한 해석은 `glyph 1개 = 0x48 bytes = 12x12 4bpp 계열` 이다.
  - `dump-fnt-glyph` 로 `'あ'`, `'ア'`, `'日'` 를 실제 덤프했을 때 12x12 문자 형태가 드러나므로, 이 경로는 샘플 글자 수준까지 검증됐다.
  - `inspect-fnt` 로 공통 `fnt` payload 전체 mapping manifest [common_fnt_manifest.json](/Users/user/test/analysis/common_fnt_manifest.json) 도 생성 가능하며, 현재 nonzero mapping `1698`개가 실제 문자/glyph index 쌍으로 정리된다.
  - 새 `audit-fnt-usage` 집계 기준 [common_fnt_usage_audit.json](/Users/user/test/analysis/common_fnt_usage_audit.json) 에서, 현재 추출본 `105707`자 기준 mapped code `1698` 중 `1411`이 실제로 쓰였고 `287`은 아직 안 쓰였다.
  - 하지만 glyph index `1..1698` 에 **빈칸이 전혀 없고**, payload 길이 `0x3DDE8` 기준 tail free bytes 도 `0` 이다.
  - 즉 한글 code point 는 lookup zero slot 에 추가할 수 있어도, **glyph 자체는 payload 확장/재배치 없이는 본격 추가가 어렵다.**
  - decoder 허용 Shift-JIS lead byte 공간 (`0x81..0x9F`, `0xE0..0xEF`) 안에는 아직 free code 가 `7337`개 있으므로, 병목은 code space 가 아니라 glyph space 다.
  - `relocate-chunk` 실험으로 공통 font entry `0` 을 `0x800000`, `len=0x42000` 으로 옮긴 테스트 ROM 을 만들 수 있었고, 새 위치도 `inspect-fnt` 로 정상 해석된다.
  - 다만 이때는 상위 registry table `0x17C2F4` entry `0` 뿐 아니라, 같은 pointer-length 내용을 가진 mirror table `0x1823A0` entry `0` 도 함께 갱신해야 한다.
  - `append-fnt-glyph` 실험으로 확장된 payload 끝에 새 glyph slot `0x06A3` 을 추가하고, free code `0xE940` 를 여기에 연결하는 경로도 검증됐다.
  - 이어서 `append-fnt-glyph-set` 으로 실제 `PGM 12x12` 테스트 glyph `가/나/다` 를 `0xE940..0xE942` 에 붙였고, [font_append_hangul_test.json](/Users/user/test/analysis/font_append_hangul_test.json) 기준 새 glyph index `0x06A3..0x06A5` 가 기록됐다.
  - 테스트용 문자 테이블은 [hangul_test.tbl](/Users/user/test/analysis/hangul_test.tbl) 이고, 현재 `E940=가`, `E941=나`, `E942=다` 로 잡혀 있다.
  - world-map 지역명 `ソリン` (`0x1842E0`) 은 공통 renderer 경로를 직접 타는 짧은 텍스트라서 첫 실제 한글 문자열 적용 대상으로 적합했다.
  - `/private/tmp/hnr_font_hangul_string_test.gba` 에서 위 위치를 `가나다` 로 제자리 치환했고, raw bytes `E940 E941 E942 00` 과 `search-text --table analysis/hangul_test.tbl` hit `1`건으로 검증했다.
  - 따라서 지금은 "첫 실제 한글 재삽입 테스트 직전" 이 아니라, **공통 font 확장 + 한글 glyph append + 한글 문자열 1건 치환** 까지 닫힌 상태다.
  - 다만 위 `가/나/다` glyph 는 placeholder 품질이므로, production 단계에서는 [font_asset_workflow.md](/Users/user/test/docs/font_asset_workflow.md) 기준으로 **레퍼런스 기반 외부 픽셀 에디터 workflow** 를 사용한다.
  - 이를 위해 `prepare-fnt-glyph-set` 으로 편집용 `PGM` glyph 세트와 `.tbl` 을 뽑아 외부 툴에서 다듬고 다시 `append-fnt-glyph-set` 으로 가져오는 경로를 추가했다.
  - 현재 seed manifest 는 [hangul_reference_seed_manifest.json](/Users/user/test/analysis/hangul_reference_seed_manifest.json), 실제 편집용 workbench 는 [prepared_manifest.json](/Users/user/test/analysis/hangul_reference_workbench/prepared_manifest.json), [prepared.tbl](/Users/user/test/analysis/hangul_reference_workbench/prepared.tbl) 기준으로 생성해 두었다.
  - 또 `build-hangul-seed-manifest` 로 번역 JSON 에서 필요한 한글 글자를 자동 수집할 수 있게 했고, 현재 [translation_workset_core_ui.json](/Users/user/test/analysis/translation_workset_core_ui.json) 기준 `80`글자 seed manifest [hangul_core_ui_seed_manifest.json](/Users/user/test/analysis/hangul_core_ui_seed_manifest.json) 와 workbench [hangul_core_ui_workbench](/Users/user/test/analysis/hangul_core_ui_workbench) 를 생성해 두었다.
  - 여기에 더해 `slice-hangul-seed-manifest` 로 상위 빈도 subset 도 자동 분리할 수 있게 했고, 현재는 [hangul_core_ui_priority24_workbench](/Users/user/test/analysis/hangul_core_ui_priority24_workbench) 와 [hangul_core_ui_priority48_workbench](/Users/user/test/analysis/hangul_core_ui_priority48_workbench) 를 만들었다.
  - coverage 기준으로는 [hangul_core_ui_priority_plan.md](/Users/user/test/analysis/hangul_core_ui_priority_plan.md) 의 `priority48` 이 첫 실제 문자열 테스트용으로 가장 균형이 좋다. 현재 `5`개 문자열을 통째로 커버한다.
  - 요약 전략은 [common_fnt_hangul_strategy.md](/Users/user/test/analysis/common_fnt_hangul_strategy.md) 에 정리했다.
  - width/advance 는 `obj + 0x18` 에 누적되며, multibyte 는 `+0x18`, halfwidth 는 `+0x10` 이다. `(obj + 0x18) >> 4` 와 `obj + 0x20` 비교로 줄 수용량을 판단한다.
  - world-map `r3=0x0C` 는 capacity `18`, 대표 일반 화면군 `r3=20` 은 capacity `30` 으로 변환되어, 이 엔진이 fullwidth / halfwidth 혼합 가변폭형 레이아웃을 가진다는 해석이 강하다.
  - 따라서 현재 가장 유력한 공통 일본어 텍스트 경로는 **`0x014A98 / 0x014ED0 / 0x015A4C` family** 다.
- 따라서 현재 병목은 데이터 구조보다 **폰트/문자 매핑/문자폭** 쪽이다.
- 폰트/문자 매핑 작업은 중단한 것이 아니라, 텍스트 source inventory 를 거의 닫은 뒤 **첫 실제 한글 재삽입 테스트를 이미 1건 검증한 단계** 로 올라왔다.
- 현재 판단상 다음 실전 과제는 "더 긴 한글 문자열의 repoint/inject" 와 "여러 화면에 공통 font 확장본이 실제로 안전하게 퍼지는지" 확인하는 것이다.
- 즉, 현재는 **특별한 새 text source 징후가 나오지 않는 한** 텍스트 추출용 구조 분석을 더 깊게 파기보다 폰트/재삽입 쪽을 우선한다.
- 텍스트 추출 구조 분석이 다시 바로 올라오는 조건은:
  - 실제 플레이에서 새 일본어가 나옴
  - cluster 라벨링 과정에서 미분류 text source 의심 구간이 튀어 나옴
  - 재삽입 중 특정 화면이 다른 별도 text bank 를 쓰는 정황이 드러남
- "텍스트를 100% 다 뽑았는가?"에 대한 현재 판정 기준과 상태는 [text_extraction_coverage.md](/Users/user/test/analysis/text_extraction_coverage.md) 에 정리했다.

## 분석 보존 위치

- 예전에 정리한 world-map / effect / tracked-slot 분석은 지운 것이 아니다.
- 보존 문서:
  - [data_structure_investigation.md](/Users/user/test/docs/tracks/data_structure_investigation.md)
  - [effect_overlay_index_flow.md](/Users/user/test/analysis/effect_overlay_index_flow.md)
- hot path 에서만 내린 이유는 **시작 토큰을 줄이기 위해서**다.

## 이번 작업에서 열 문서

- 필수: [text_extraction_progress.md](/Users/user/test/docs/tracks/text_extraction_progress.md)
- 필요 시: [text_reinsertion_progress.md](/Users/user/test/docs/tracks/text_reinsertion_progress.md)
- 필요 시: [font_and_encoding_progress.md](/Users/user/test/docs/tracks/font_and_encoding_progress.md)
- 필요 시: [font_asset_workflow.md](/Users/user/test/docs/font_asset_workflow.md)
- 추출 구조가 막힐 때만: [data_structure_investigation.md](/Users/user/test/docs/tracks/data_structure_investigation.md)

## 반복 금지

- helper 분석을 hot path 문서에 다시 올리지 않는다.
- 한글 표시 경로가 없는 상태에서 구조 분석만 계속 늘리지 않는다.
- `save_menu_texts` 를 `00` 종단 평문처럼 취급하지 않는다.
- `01 FF <문자수>` 구조를 찾을 때는 incremental decode 같은 상태형 해석을 쓰지 말고, 현재 바이트 조각을 독립 `cp932` decode 로 판정한다.
- 넓은 슬라이딩 스캔은 기본 `--limit 100` 에 걸릴 수 있으니, 전체 회수를 원할 때는 `--limit` 을 명시한다.
- `0x10` 종단 전역 스캔은 앞쪽 바이너리 잡음도 섞으므로, 클러스터 범위와 상위 registry entry 를 함께 확인한다.
- `0x03EB78 / 0x03ECCC / 0x03EDB8` 를 general font renderer 로 되짚지 않는다. 현재 증거는 ASCII/숫자 tilemap helper 쪽이다.
- 공통 일본어 텍스트 경로를 따라갈 때는 `0x014ED0` 의 multibyte / ASCII 분기 아래 glyph lookup 과 width 누적만 우선 추적한다.
- literal scan 결과만으로 "더 조사할 게 없다"고 결론내리지 않지만, 실제 한글화와 직접 연결되지 않는 deep dive 도 늘리지 않는다.

## 유용한 명령

```bash
python3 -m gba_kor_tool build-translation-set \
  analysis/translation_workset_core_ui.json \
  analysis/system_messages.json \
  analysis/save_menu_texts.json \
  analysis/location_texts.json \
  analysis/ui_skill_texts.json

python3 -m gba_kor_tool scan-text \
  "Hagane no Renkinjutsushi - Meisou no Rondo (Japan).gba" \
  --start 0x7F3000 \
  --end 0x7F96E9 \
  --sliding \
  --terminator 0x0D \
  --terminator 0x0C \
  --terminator 0x00 \
  --min-chars 6 \
  --require-japanese \
  --limit 500 \
  --output analysis/registry_d_full_sliding_texts.json

python3 -m gba_kor_tool scan-fc-script-text \
  "Hagane no Renkinjutsushi - Meisou no Rondo (Japan).gba" \
  --start 0x7F3000 \
  --end 0x7F96E9 \
  --require-japanese \
  --min-japanese-ratio 0.3 \
  --output analysis/registry_d_fc_script_texts.json

python3 -m gba_kor_tool scan-text \
  "Hagane no Renkinjutsushi - Meisou no Rondo (Japan).gba" \
  --start 0x6B594C \
  --end 0x773248 \
  --sliding \
  --terminator 0x10 \
  --min-chars 4 \
  --require-japanese \
  --limit 1200 \
  --output analysis/registry_a_entry8_terminator_10_texts.json

python3 -m gba_kor_tool scan-prefixed-text \
  "Hagane no Renkinjutsushi - Meisou no Rondo (Japan).gba" \
  --start 0x6B594C \
  --end 0x773248 \
  --require-japanese \
  --output analysis/registry_a_entry8_prefixed_texts.json

python3 -m gba_kor_tool summarize-text-clusters \
  analysis/registry_a_entry8_prefixed_texts.json \
  --gap-threshold 0x400 \
  --output analysis/registry_a_entry8_cluster_catalog.json
```

## 완료 조건

- Registry A entry `8` / Registry D 계열 대사 추출본을 더 구조화한다.
- Registry D mixed script 쪽은 `scan-fc-script-text` 기반 clean extraction 을 기본 원본으로 올린다.
- Registry A entry `8` 72개 클러스터를 장면/용도 기준으로 조금 더 이름 붙여 관리한다.
- `01 FF <문자수>` 규칙이 안 통하는 나머지 mixed resource 대사 뱅크 형식을 찾는다.
- 번역 단계에 들어가기 전까지는 추출본과 구조 근거를 계속 분리 정리한다.
- 한글 표시를 위해 필요한 폰트/인코딩 경로를 최소 1개 확보한다.
- 첫 번째 실제 한글 패치 테스트를 더 긴 문자열 / repoint 흐름으로 확장한다.

## 참고 지도

- 장기 우선순위는 [project_control_tower.md](/Users/user/test/docs/project_control_tower.md) 를 필요할 때만 본다.
