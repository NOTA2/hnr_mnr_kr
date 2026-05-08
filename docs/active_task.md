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
- Registry D (`0x17C7E4..0x17CB04`) 는 아직 덜 추출된 대사/이벤트 텍스트의 핵심 후보다.
- Registry D 물리 범위 `0x7F3000..0x7F96E9` 를 슬라이딩 스캔하면 현재 `305`개 대사성 문자열이 잡힌다.
- 전체본은 [registry_d_full_sliding_texts.json](/Users/user/test/analysis/registry_d_full_sliding_texts.json), 번역용 작업 세트는 [translation_workset_registry_d_dialogue.json](/Users/user/test/analysis/translation_workset_registry_d_dialogue.json) 에 있다.
- `save_menu_texts.json` 류는 종단 바이트가 `0x10` 이라서 일반 `00` 종단 문자열과 분리해서 다뤄야 한다.
- 재삽입 도구 기본 기능은 이미 있다:
  - 같은 길이 이하 덮어쓰기
  - 자유 공간 주입
  - 포인터 갱신
  - `apply-translations` 일괄 반영
- 아직 **한글을 실제 ROM에 표시할 폰트/인코딩 경로는 확보되지 않았다.**
- 따라서 현재 병목은 데이터 구조보다 **폰트/문자 매핑/문자폭** 쪽이다.

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
- 추출 구조가 막힐 때만: [data_structure_investigation.md](/Users/user/test/docs/tracks/data_structure_investigation.md)

## 반복 금지

- helper 분석을 hot path 문서에 다시 올리지 않는다.
- 한글 표시 경로가 없는 상태에서 구조 분석만 계속 늘리지 않는다.
- `save_menu_texts` 를 `00` 종단 평문처럼 취급하지 않는다.
- 넓은 슬라이딩 스캔은 기본 `--limit 100` 에 걸릴 수 있으니, 전체 회수를 원할 때는 `--limit` 을 명시한다.
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
```

## 완료 조건

- Registry D 계열 대사 추출본을 더 구조화한다.
- 번역 작업 세트를 1개 이상 더 정리한다.
- 한글 표시를 위해 필요한 폰트/인코딩 경로를 최소 1개 확보한다.
- 첫 번째 실제 한글 패치 테스트 경로를 잡는다.

## 참고 지도

- 장기 우선순위는 [project_control_tower.md](/Users/user/test/docs/project_control_tower.md) 를 필요할 때만 본다.
