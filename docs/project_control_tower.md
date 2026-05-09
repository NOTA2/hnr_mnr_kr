# Project Control Tower

이 문서는 장기 대시보드다.

새 세션의 시작점은 [session_start.md](/Users/user/test/docs/session_start.md) 이고, 실제 다음 작업은 [active_task.md](/Users/user/test/docs/active_task.md) 를 따른다.

## 단계

- 데이터 구조 조사: `PARKED EXCEPT TEXT EXTRACTION TARGETS`
- 텍스트 추출: `IN PROGRESS`
- 텍스트 재삽입: `BOOTSTRAPPED`
- 폰트/문자 매핑: `IN PROGRESS`
- 이미지 리소스: `NOT STARTED`
- GUI/작업 워크플로우: `DEFERRED`

## 현재 우선순위

1. 번역 작업용 텍스트 세트 확대와 정리
2. 한글 표시를 위한 폰트/문자 매핑/문자폭 경로 확보
3. 첫 번째 실제 한글 재삽입 테스트
4. 이미지 리소스는 텍스트 루프가 돈 뒤에 착수

## 최근 핵심 진전

- `build-translation-set` CLI 를 추가해 여러 추출 JSON 을 번역 작업용 JSON 한 개로 묶을 수 있게 했다.
- [translation_workset_core_ui.json](/Users/user/test/analysis/translation_workset_core_ui.json) 을 만들어 `system + save + location + ui_skill` 43개 레코드를 한 파일로 정리했다.
- 위 작업 세트의 시스템/세이브/지역명 앞부분에는 한국어 초안을 채우기 시작했다.
- `save_menu_texts` 처럼 `0x10` 종단을 쓰는 명령 스트림형 텍스트도 이제 같은 번역 workset 흐름에 넣을 수 있다.
- Registry D (`0x17C7E4..0x17CB04`) 전체 물리 범위 `0x7F3000..0x7F96E9` 를 넓은 슬라이딩 스캔으로 다시 훑어 `305`개 대사성 문자열을 확보했다.
- 위 결과를 [translation_workset_registry_d_dialogue.json](/Users/user/test/analysis/translation_workset_registry_d_dialogue.json) 으로 정리해, 튜토리얼/이벤트/전투 전후 대사를 바로 번역 가능한 workset 으로 전환했다.
- 넓은 범위 `scan-text` 는 기본 `--limit 100` 으로 잘릴 수 있다는 운영 함정을 확인했고, 이후 wide scan 에서는 limit 을 명시해야 한다.
- `scan-prefixed-text` CLI 를 추가해 `01 FF <u16 문자수>` command-stream 텍스트를 직접 추출할 수 있게 했다.
- Registry A entry `8` (`0x6B594C..0x773248`) 는 이제 [registry_a_entry8_prefixed_texts.json](/Users/user/test/analysis/registry_a_entry8_prefixed_texts.json) `9823`건으로 clean extraction 이 가능하다.
- save/menu block `0x772E00..0x773260` 도 같은 규칙으로 [save_menu_prefixed_texts.json](/Users/user/test/analysis/save_menu_prefixed_texts.json) `12`건이 정리되었다.
- 상위 registry 재검사 결과, `01 FF <u16 문자수>` 규칙이 강하게 맞는 곳은 현재 Registry A entry `8` 하나뿐이며, 요약은 [prefixed_registry_scan_summary.json](/Users/user/test/analysis/prefixed_registry_scan_summary.json) 에 있다.
- Registry A entry `8` 은 [registry_a_entry8_cluster_summary.json](/Users/user/test/analysis/registry_a_entry8_cluster_summary.json) 기준 gap threshold `0x400` 으로 `72`개 작업 cluster 로 나눌 수 있다.
- 폰트 쪽에서는 `0x0514xx` UI cluster 가 direct renderer 가 아니라 layout / slot setup 경로에 가깝고, Registry B raw companion 엔트리 `86..88` 도 direct raw font tile 후보가 아니라는 점을 먼저 정리했다.
- 폰트 쪽에서는 `0x03EB78 / 0x03ECCC / 0x03EDB8` helper family 도 일반 일본어 렌더러가 아니라 ASCII/숫자 UI glyph tilemap writer 쪽으로 좁혀졌다.
- world-map 지역명 caller `0x06A95A..0x06A972` 를 따라가 `0x014A98 -> 0x014ED0 -> 0x015A4C` 공통 text object family 를 찾았고, `0x014ED0` 가 Shift-JIS lead byte 범위를 직접 검사하는 general Japanese text loop 후보라는 점을 확인했다.
- 이어서 `0x0152A2..0x0152C4` 에서 문자코드가 `obj + 0x04` lookup table, `obj + 0x08` glyph base, `obj + 0x1A` stride 를 통해 glyph source pointer 로 바뀌는 흐름과 `0x01570C..0x015984` writer family 도 확인했다.
- `0x01499C` 가 font resource header 를 해석해 object 에 lookup base / glyph base / stride 를 심는 initializer 라는 점과, 주요 text object caller 가 공통 `0x0002CC(0, 1)` resource 를 공유한다는 점도 확인했다.
- 이어서 `0x000290 / 0x0002CC / 0x000304 / 0x00033C` loader family 가 hub `0x076530` pointer table 과 `0x0A` record 구조를 통해 이 공통 font resource 를 공급한다는 점도 확인했다.

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
