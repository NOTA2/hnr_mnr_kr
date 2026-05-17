# Project Control Tower

이 문서는 장기 대시보드다.

새 세션의 시작점은 [session_start.md](/Users/user/test/docs/session_start.md) 이고, 실제 다음 작업은 [active_task.md](/Users/user/test/docs/active_task.md) 를 따른다.

## 단계

- 데이터 구조 조사: `PARKED EXCEPT TEXT EXTRACTION TARGETS`
- 텍스트 추출: `IN PROGRESS`
- 텍스트 재삽입: `IN PROGRESS`
- 폰트/문자 매핑: `IN PROGRESS`
- 이미지 리소스: `NOT STARTED`
- GUI/작업 워크플로우: `DEFERRED`

## 현재 우선순위

1. 최종 후보 `3`개 bitmap 폰트 startup intro 비교
2. 폰트 확정 뒤 남은 텍스트 추출 감사 마감
3. 번역 workset 운영과 재삽입 루프 고정
4. 이미지 리소스는 폰트 결정과 텍스트 루프 안정화 뒤 착수

## 최근 핵심 진전

- `build-translation-set` CLI 를 추가해 여러 추출 JSON 을 번역 작업용 JSON 한 개로 묶을 수 있게 했다.
- [translation_workset_core_ui.json](/Users/user/test/confirmed_data/translation_worksets/translation_workset_core_ui.json) 을 만들어 `system + save + location + ui_skill` 43개 레코드를 한 파일로 정리했다.
- 위 작업 세트의 시스템/세이브/지역명 앞부분에는 한국어 초안을 채우기 시작했다.
- `save_menu_texts` 처럼 `0x10` 종단을 쓰는 명령 스트림형 텍스트도 이제 같은 번역 workset 흐름에 넣을 수 있다.
- Registry D (`0x17C7E4..0x17CB04`) 전체 물리 범위 `0x7F3000..0x7F96E9` 를 넓은 슬라이딩 스캔으로 다시 훑어 `305`개 대사성 문자열을 확보했다.
- 위 결과를 [translation_workset_registry_d_dialogue.json](/Users/user/test/confirmed_data/translation_worksets/translation_workset_registry_d_dialogue.json) 으로 정리해, 튜토리얼/이벤트/전투 전후 대사를 바로 번역 가능한 workset 으로 전환했다.
- 이어서 `scan-fc-script-text` CLI 를 추가해 Registry D mixed script 형식 `FC 00 ... FC` anchor 에서 [registry_d_fc_script_texts.json](/Users/user/test/confirmed_data/extracted_texts/registry_d_fc_script_texts.json) `244`건을 clean extraction 했고, [registry_d_fc_script_summary.json](/Users/user/test/analysis/registry_d_fc_script_summary.json) 으로 `82 / 100` 엔트리 분포도 정리했다.
- stop byte `FC` 가 Shift-JIS trailing byte 와 충돌하는 케이스를 고쳐 entry `8` 대사도 추가 회수했고, 남은 non-hit `18`개는 [registry_d_unresolved_entries.json](/Users/user/test/analysis/registry_d_unresolved_entries.json) 으로 분리해 대부분이 control stub 임을 정리했다.
- Registry D entry `70` 도 raw bytes 를 다시 확인해 `FC` 밀집 control-only script table 쪽으로 더 강하게 분류했다.
- 넓은 범위 `scan-text` 는 기본 `--limit 100` 으로 잘릴 수 있다는 운영 함정을 확인했고, 이후 wide scan 에서는 limit 을 명시해야 한다.
- `scan-prefixed-text` CLI 를 추가해 `01 FF <u16 문자수>` command-stream 텍스트를 직접 추출할 수 있게 했다.
- Registry A entry `8` (`0x6B594C..0x773248`) 는 이제 [registry_a_entry8_prefixed_texts.json](/Users/user/test/confirmed_data/extracted_texts/registry_a_entry8_prefixed_texts.json) `9823`건으로 clean extraction 이 가능하다.
- 이어서 `summarize-text-clusters` CLI 를 추가해 entry `8` 을 `72`개 cluster 로 자동 태깅/샘플화한 [registry_a_entry8_cluster_catalog.json](/Users/user/test/analysis/registry_a_entry8_cluster_catalog.json) 과 [registry_a_entry8_cluster_overview.md](/Users/user/test/analysis/registry_a_entry8_cluster_overview.md) 를 만들었다.
- 이어서 [build_entry8_cluster_worksets.py](/Users/user/test/scripts/build_entry8_cluster_worksets.py) 로 entry `8` 추출본을 [registry_a_entry8_clusters](/Users/user/test/confirmed_data/translation_workspace/registry_a_entry8_clusters) 아래 `72`개 번역 workset 으로 자동 분할했고, 상위 인덱스 [registry_a_entry8_clusters_manifest.json](/Users/user/test/confirmed_data/translation_workspace/registry_a_entry8_clusters_manifest.json) 도 남겼다.
- 또 [build_master_text_workspace.py](/Users/user/test/scripts/build_master_text_workspace.py) 로 현재 known extracted text sources `12`개를 [all_extracted_texts_master.json](/Users/user/test/confirmed_data/translation_workspace/all_extracted_texts_master.json) `10752`건 기준본으로 묶고, [all_extracted_texts_manifest.json](/Users/user/test/confirmed_data/translation_workspace/all_extracted_texts_manifest.json) 에 source별 개수를 기록했다.
- 이어서 [build_translation_workspace.py](/Users/user/test/scripts/build_translation_workspace.py) 로 master set + entry8 cluster worksets + [translation_workspace/index.json](/Users/user/test/confirmed_data/translation_workspace/index.json) / [translation_workspace/README.md](/Users/user/test/confirmed_data/translation_workspace/README.md) 까지 한 번에 재생성하는 작업 허브를 만들었다.
- 사용자가 만든 번역팀용 MD `3`개도 [translation_team](/Users/user/test/docs/translation_team) 아래 프로젝트 안으로 복사했고, 실제 workset 연결 정보는 [translation_team_bundle.json](/Users/user/test/confirmed_data/translation_workspace/translation_team_bundle.json) 에 묶었다.
- cluster `71` 은 자동 태그상 `save_menu` 로 보이지만, 실제로는 일반 이벤트/진행 힌트 `228`건과 save/menu `12`건이 섞인 mixed hub 로 확인되어 [registry_a_entry8_cluster71_pre_save_texts.json](/Users/user/test/analysis/registry_a_entry8_cluster71_pre_save_texts.json) / [registry_a_entry8_cluster71_save_segment_texts.json](/Users/user/test/analysis/registry_a_entry8_cluster71_save_segment_texts.json) 으로 분리했다.
- Registry A tail 에서도 entry `12` (`0x7A750C..0x7A8E98`) 의 gameplay/item text `22`건을 [registry_a_entry12_texts.json](/Users/user/test/confirmed_data/extracted_texts/registry_a_entry12_texts.json) 으로 확보했고, [registry_a_tail_classification.json](/Users/user/test/analysis/registry_a_tail_classification.json) 으로 tail `9..17` 을 source/no-source 후보로 분류해 coverage 판단을 상위 registry inventory 기준으로 갱신하기 시작했다.
- 현재는 Registry A tail (`9..17`) 분류와 Registry D entry `70` 판정이 실질적으로 닫혀, 텍스트 추출 구조 분석은 "새 source 징후가 나올 때만 다시 여는 단계" 에 가깝다.
- save/menu block `0x772E00..0x773260` 도 같은 규칙으로 [save_menu_prefixed_texts.json](/Users/user/test/confirmed_data/extracted_texts/save_menu_prefixed_texts.json) `12`건이 정리되었다.
- 상위 registry 재검사 결과, `01 FF <u16 문자수>` 규칙이 강하게 맞는 곳은 현재 Registry A entry `8` 하나뿐이며, 요약은 [prefixed_registry_scan_summary.json](/Users/user/test/analysis/prefixed_registry_scan_summary.json) 에 있다.
- Registry A entry `8` 은 [registry_a_entry8_cluster_summary.json](/Users/user/test/analysis/registry_a_entry8_cluster_summary.json) 기준 gap threshold `0x400` 으로 `72`개 작업 cluster 로 나눌 수 있다.
- 폰트 쪽에서는 `0x0514xx` UI cluster 가 direct renderer 가 아니라 layout / slot setup 경로에 가깝고, Registry B raw companion 엔트리 `86..88` 도 direct raw font tile 후보가 아니라는 점을 먼저 정리했다.
- 폰트 쪽에서는 `0x03EB78 / 0x03ECCC / 0x03EDB8` helper family 도 일반 일본어 렌더러가 아니라 ASCII/숫자 UI glyph tilemap writer 쪽으로 좁혀졌다.
- world-map 지역명 caller `0x06A95A..0x06A972` 를 따라가 `0x014A98 -> 0x014ED0 -> 0x015A4C` 공통 text object family 를 찾았고, `0x014ED0` 가 Shift-JIS lead byte 범위를 직접 검사하는 general Japanese text loop 후보라는 점을 확인했다.
- 이어서 `0x0152A2..0x0152C4` 에서 문자코드가 `obj + 0x04` lookup table, `obj + 0x08` glyph base, `obj + 0x1A` stride 를 통해 glyph source pointer 로 바뀌는 흐름과 `0x01570C..0x015984` writer family 도 확인했다.
- `0x01499C` 가 font resource header 를 해석해 object 에 lookup base / glyph base / stride 를 심는 initializer 라는 점과, 주요 text object caller 가 공통 `0x0002CC(0, 1)` resource 를 공유한다는 점도 확인했다.
- 이어서 `0x000290 / 0x0002CC / 0x000304 / 0x00033C` loader family 가 hub `0x076530` pointer table 과 `0x0A` record 구조를 통해 이 공통 font resource 를 공급한다는 점도 확인했다.
- 추가로 공통 font resource 가 `0x17C2F4` table entry `0` -> ROM `0x3E0000` `fnt` payload 로 이어지고, `resource[8]=0x48` 및 writer loop 로부터 12x12 계열 glyph 포맷 후보까지 얻었다.
- `dump-fnt-glyph` 도구로 `'あ'`, `'ア'`, `'日'` 샘플 glyph 를 직접 덤프해 형태 확인까지 마쳤다.
- `inspect-fnt` 도구로 공통 `fnt` payload 전체 mapping manifest 를 추출해, 공통 font 쪽도 실제 추출본 확보 단계로 들어갔다.
- width/advance 도 `obj + 0x18` 누적, `obj + 0x20` capacity 구조로 좁혀졌고, 대표 caller 비교로 fullwidth/halfwidth 혼합 가변폭 레이아웃 해석도 교차검증했다.
- 이어서 `audit-fnt-usage` CLI 로 현재 추출 텍스트 기준 공통 font usage audit 을 고정했고, mapped code `1698` 중 현재 사용 `1411`, 미사용 `287`, glyph gap `0`, payload tail free `0` 이라는 결론을 얻었다.
- decoder 허용 Shift-JIS lead byte 공간 안에는 free code 가 많이 남아 있어, 현재 한글화 병목은 code space 가 아니라 **glyph 저장 공간** 으로 정리됐다.
- 그래서 공통 font 쪽 다음 단계는 `unused glyph 일부 치환` 과 `payload 확장/재배치` 중 첫 실제 테스트 전략을 고르는 것이다.
- `relocate-chunk` CLI 도 추가했고, 공통 font entry `0` 을 `0x800000`, `len=0x42000` 으로 옮긴 테스트 ROM 생성까지 검증했다.
- 이 과정에서 공통 font pointer 는 `0x17C2F4` entry `0` 뿐 아니라 mirror table `0x1823A0` entry `0` 도 함께 갱신해야 한다는 점을 확인했다.
- 이어서 `append-fnt-glyph-set` 과 테스트용 `PGM 12x12` glyph `가/나/다` 를 이용해 free code `0xE940..0xE942` 에 실제 한글 glyph 3개를 append 했다.
- 그 위에서 world-map 지역명 `ソリン` (`0x1842E0`) 을 `가나다` 로 제자리 치환한 `/private/tmp/hnr_font_hangul_string_test.gba` 도 만들었고, raw bytes 와 table-based `search-text` hit 로 문자열 1건을 검증했다.
- 따라서 지금은 "첫 실제 한글 재삽입 테스트 준비"가 아니라, **첫 한글 문자열 테스트 ROM 1건을 확보한 상태** 다.
- 또 placeholder 품질 glyph 를 정식 자산으로 쓰지 않도록, `prepare-fnt-glyph-set` 과 [font_asset_workflow.md](/Users/user/test/docs/font_asset_workflow.md) 를 추가해 **외부 픽셀 에디터 기반 정식 glyph 제작 경로** 도 열어 두었다.
- 운영 측면에서는 `analysis/` 루트에서 참조가 거의 없는 raw evidence 묶음을 [analysis/archive/data_structure_raw](/Users/user/test/analysis/archive/data_structure_raw) 로 내리고, [analysis/README.md](/Users/user/test/analysis/README.md) / [analysis/archive/README.md](/Users/user/test/analysis/archive/README.md) 기준으로 hot path 와 cold archive 를 분리했다.
- 현재 한글 폰트는 “완전 확정”이 아니라 최종 후보 `3`개 비교 단계다:
  - `MaruMinyaHangul (12px)`
  - `Galmuri11 (12px)`
  - `GalmuriMono (12px)`
- 세 후보에서 새로 뽑아야 하는 bitmap seed 는 현재 파이프라인 기준 **한글 완성형 `11,172`자 atlas** 다.
- 숫자/영문/기본 기호는 1차 한글화 기준으로 원본 게임 공통 폰트를 그대로 재사용한다.
- 후보군 메타데이터와 export 기준은 [finalist_font_candidates.json](/Users/user/test/confirmed_data/font_assets/finalist_font_candidates.json), [finalist_export_recommendation.md](/Users/user/test/confirmed_data/font_assets/finalist_export_recommendation.md) 에 있다.
- startup intro `4`줄만이 아니라, 시작 카드 뒤의 인트로 문장/리오르 표기/호명까지 포함한 [translation_workset_intro_full_test.json](/Users/user/test/confirmed_data/translation_worksets/translation_workset_intro_full_test.json) 도 만들었다.
- 길이 때문에 일부가 `skipped_no_pointer` 로 남는 문제를 피하려고, 폰트 QA 전용 [translation_workset_intro_full_compact_test.json](/Users/user/test/confirmed_data/translation_worksets/translation_workset_intro_full_compact_test.json) 도 만들었고 현재 `18 in_place` 로 확인했다.
- build script:
  - [build_intro_full_test.sh](/Users/user/test/scripts/build_intro_full_test.sh)
  - [build_intro_full_compact_test.sh](/Users/user/test/scripts/build_intro_full_compact_test.sh)
- 이미지 추출은 “텍스트 추출 이후만 가능”은 아니다. 현재 판단은 **폰트 결정 + 텍스트 루프 안정화 후**, 번역 진행과 병렬로 image inventory / extraction 을 시작하는 편이 맞다.

- `0x184A0C..0x184AD3` 을 `10 * 0x14` effect/overlay parameter table 후보로 분리했다.
- `0x03005FF8` 은 world-map 선택/hover location index byte 로 보는 해석이 강해졌다.
- 확인된 direct writer 는 `0x06A52E` 이며, hit-test loop index `0..9` 를 저장한다.
- `0x06CEC0` 은 selected index 를 current-location byte `0x03006020` 으로 복사한다.
- `0x184A0C` row `word0` 은 `0x184420` hotspot/location lookup 과 row별로 정확히 맞아 location 대표 hotspot/cell id 로 좁혀졌다.
- `word1` / `word2` 는 sign-extended integer 좌표쌍이며, runtime object 에는 float 형태로 저장된다는 해석이 가장 강하다.
- `word3` 은 `0x02B96C` 내부에서 `& 7` 로 제한된 뒤 `0x0383F8 -> 0x1824F0` 8-entry accessor table 로 이어진다.
- 이 accessor 들은 공통 descriptor 의 halfword field `+0x04 .. +0x12` 에서 low 10-bit 값을 읽으므로, `word3` 은 descriptor field selector 로 보는 해석이 가장 강하다.
- 현재 effect/overlay row 에서 실제 사용된 `word3` 값은 `0` 과 `6` 뿐이다.
- `word4 != 0` side-path 는 `0x03001450 + 0x33C/+0x33E` 의 raw tracked slot id 두 개를 읽어, 나머지 slot `8..23` 의 병렬 block 을 지우는 maintenance 경로로 좁혀졌다.
- `0x044320` / `0x0443B4` / `0x03D6F0` 는 같은 tracked slot record 플래그를 set/check/sync 하는 helper 군으로 보는 해석이 강하다.
- `0x03D6F0` 첫 비교는 `cmp` 가 아니라 `cmn` 이므로, `+0x33E` 는 `-1` sentinel 을 갖는 optional second tracked slot field 후보로 좁혀졌다.
- `0x0443F8` 는 tracked slot `0x33C/+0x33E` 를 피해서 slot `0..15` 후보를 훑는 allocator 로 보이며, 선택 결과를 `0x03005284` 에 남긴다.
- `0x03005240` 은 이 allocator 가 갱신하는 `16 * 4-byte` per-slot state table 후보로 좁혀졌다.
- `0x0412D0..0x04137A` 는 `0x03005284 = -1` 과 `0x03005240[16]` clear 를 수행하는 allocator init 경로로 좁혀졌다.
- `0x044AE0` 는 `0x03005240[candidate].+2` 에 저장되는 edge/boundary mask helper 로 좁혀졌다.
- `0x0443F8` direct caller 는 현재 `0x059034` 하나이며, caller 는 반환 slot id 를 `slot + 0x5A` runtime id 로 변환해 후속 object 구축에 사용한다.
- `0x045D6C/0x045D94` 와 `0x045EEE/0x045F16` 은 `0x03005284` candidate 를 `0x482 = raw slot`, `0x484 = 0x0478B8(slot)` pair 로 staging 한 뒤 `0x0458DC` 를 호출한다.
- `0x04B7F0` 는 `0x482/0x484` pending pair 와 기존 `0x33E` tracked slot 을 함께 읽는 consumer 로 보인다.
- `0x051022` 는 특정 state flag 조건에서 `0x33E = -1` sentinel 을 기록하는 direct clear writer 다.
- `find-u32-refs` CLI 로 `u32` literal hit 와 Thumb literal load 후보를 추적할 수 있게 했다.

## 안정화된 큰 구조

- `0x17C1C0`: 예외적인 `length-pointer` 리소스 디스크립터
- `0x076530`: 상위 registry hub
- `0x17785C`: `0x03BC` / `0x0414` 전용 accessor 축
- `0x183D50`: Registry B 미러, `0x068DF8` ZP-aware helper 경로
- `0x184248..`: location/world-map bundle
- `0x3Dxxxx`: 텍스트와 binary record 가 섞인 mixed resource 구간

## 운영 정책

- 시작 시 이 문서를 읽지 않는다.
- 단계나 우선순위가 바뀐 경우에만 갱신한다.
- 매 실행마다 갱신해야 하는 문서는 [active_task.md](/Users/user/test/docs/active_task.md) 이다.
