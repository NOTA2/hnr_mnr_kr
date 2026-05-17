# Font And Encoding Progress

읽기 규칙: 이 문서는 폰트/문자폭 조사가 활성 단계로 올라왔을 때만 읽는다.

이 문서는 폰트, 글리프, 문자 폭, 인코딩/테이블 조사 진행 상황을 기록합니다.

## 목적

- 한글 글리프를 넣을 수 있는 위치를 찾는다.
- 문자 폭 테이블과 표시 방식을 파악한다.
- 한글용 문자 매핑 전략을 세운다.

## 현재 상태

- 상태: `IN PROGRESS`

## 준비된 것

- 4bpp 타일 덤프 도구 사용 가능
- `.tbl` 기반 문자 테이블 처리 기본 지원

## 아직 확인되지 않은 것

- 실제 폰트 타일 위치
- 고정폭/가변폭 여부
- 문자 폭 테이블 위치
- 한글 글리프 삽입 가능 공간

## 최근 확인

- 현재 프로젝트의 active 한글 glyph source 는 [maruminyahangul_12x12.png](/Users/user/test/third_party/font_atlases/maruminyahangul_12x12.png) 하나로 고정했다.
- 기준 설정은 [active_hangul_font_profile.json](/Users/user/test/confirmed_data/font_assets/active_hangul_font_profile.json) 에 기록했다.
- startup intro active workbench, core UI `priority48`, core UI `full80` workbench 는 모두 같은 atlas 에서 다시 생성되도록 정리했다.
- 임의의 번역 JSON 에서 실제 사용 한글만 뽑아 subset workbench 를 만드는 [build_workbench_from_active_atlas.py](/Users/user/test/scripts/build_workbench_from_active_atlas.py) 와, 그 결과를 바로 ROM 에 적용하는 [build_translated_rom_with_active_atlas.sh](/Users/user/test/scripts/build_translated_rom_with_active_atlas.sh) 를 추가했다.
- 예전 D2Coding / NanumSquare / SourceHan / 비교 시트와 workbench 는 [analysis/archive/font_trials/2026-05-17_pre_bitmap_lock](/Users/user/test/analysis/archive/font_trials/2026-05-17_pre_bitmap_lock) 로 내렸다.

- `0x0514xx` UI cluster 는 `0x075DD4` (`strlen`) 과 `0x03EB78` / `0x03ECCC` layout helper 를 반복 호출하는 **UI layout / slot setup 경로**에 가깝다.
- 같은 클러스터에서 따라간 `0x058720` 은 문자열 렌더러가 아니라, current tracked slot record (`0x714`) 의 좌표를 읽어 넘기는 position helper 다.
- 따라서 위 경로는 폰트/문자 매핑 자체를 찾는 direct route 로 보기 어렵다.
- 추가 확인:
  - `0x03EB78` 은 입력 바이트를 `A-Z`, `a-z`, `0-9` 범위와 비교해 `0x03003008` base 에 halfword tile index 를 쓴다.
  - `0x03ECCC` 는 `0x033658` 로 값을 4-byte 버퍼로 바꾼 뒤 `0x03EDB8` 을 통해 같은 tilemap base 에 숫자/기호를 배치한다.
  - 따라서 `0x03EB78 / 0x03ECCC / 0x03EDB8` 는 **일반 일본어 폰트 렌더러가 아니라 ASCII/숫자 UI glyph helper family** 로 보는 해석이 가장 강하다.
  - 이 helper family 는 한글 폰트 원본/문자폭 조사 대상에서 우선 제외한다.
- world-map Registry B raw companion 엔트리 `86`, `87`, `88` 을 헤더 뒤에서 바로 4bpp 덤프한 결과는 [registry_b_entry_86_tiles.png](/Users/user/test/analysis/registry_b_entry_86_tiles.png), [registry_b_entry_87_tiles.png](/Users/user/test/analysis/registry_b_entry_87_tiles.png), [registry_b_entry_88_tiles.png](/Users/user/test/analysis/registry_b_entry_88_tiles.png) 처럼 잡음에 가깝다.
- 그래서 현재는 이 raw companion 엔트리들을 **직접 폰트 raw tile 후보에서 우선 제외**한다.
- world-map 지역명 경로 `0x06A95A..0x06A972` 에서 `0x18425C + selected_location * 0x2C` 문자열 필드가 `0x014A98 -> 0x014ED0` 로 직접 전달된다.
- `0x014A98` 는 object field 와 플래그를 세팅하는 **text object / window entry setup helper** 에 가깝고, 실제 바이트 디코더로 보이지 않는다.
- `0x014ED0` 는 object `+0x0C` 문자열 포인터에서 현재 바이트를 읽으며:
  - `0x81..0x9F`, `0xE0..0xEF`: Shift-JIS multibyte lead byte 후보
  - `0x20..0x7E`: ASCII / halfwidth 경로
  - `0x00`: 문자열 종료
- `0x015A4C..0x015A80` 는 `0x03001540 + index * 0x2C` text object `11`개를 순회하며 `0x014ED0` 을 호출하므로, 이 함수는 single-shot helper 가 아니라 **공용 text object update/render engine** 에 가깝다.
- 따라서 이제 general Japanese text renderer 후보는 `0x03EB78` family 가 아니라 **`0x014A98 / 0x014ED0 / 0x015A4C` family** 로 본다.
- `0x0152A2..0x0152C4` 에서는 현재 문자코드 `u16` 를 `obj + 0x04` 기반 `u16` lookup table 로 조회한 뒤, `obj + 0x1A` stride 와 `obj + 0x08` glyph base 를 이용해 실제 glyph source pointer 를 계산한다.
- 이후 `0x01570C / 0x01578C / 0x01580C / 0x01588C` writer family 가 glyph source 를 target 으로 복사하고, low-level halfword writer 는 `0x01590C` / `0x015984` 두 종류로 갈린다.
- `0x015608` 은 `obj + 0x1F` 와 `obj + 0x10` 을 사용해 `obj + 0x14` destination pointer 를 재계산하므로, text object 가 tile page 단위 cursor/state 를 따로 가진다는 점도 보였다.
- `0x01499C` 는 font resource initializer 후보로, `obj + 0x00 = resource_ptr`, `obj + 0x04 = lookup base`, `obj + 0x08 = glyph base`, `obj + 0x1A = resource[8] stride` 를 채운다.
- 이 함수는 `resource[7] & 0x80` 에 따라 lookup base 에 `+0x40000` 을 더하고, glyph base 는 그 뒤 `+0x20000` 위치로 잡는다.
- ROM 문자열 `0x08088318 = "FONT INITIALIZE ERROR"` 도 이 함수 주변에서 참조되어 역할과 맞는다.
- `0x000290 / 0x0002CC / 0x000304 / 0x00033C` 는 상위 resource loader family 로 보인다.
- `0x000290(registry_slot)` 은 hub `0x08076530` table 에서 registry base pointer 를 고르고, `0x0002CC(entry_index, registry_slot)` 은 그 registry 의 `0x0A` record 에서 payload pointer 를 돌려준다.
- `0x000304(entry_index, registry_slot)` 은 같은 record 의 length 를 돌려주고, `0x00033C(dest, entry_index, registry_slot)` 은 DMA3 로 payload 를 `dest` 로 복사한다.
- 현재까지 확인한 주요 caller (`0x015A28`, `0x0618A4`, `0x064B5C`, `0x069D72`) 는 모두 `0x0002CC(0, 1)` 뒤 `0x01499C` 를 호출하므로, **registry slot 1 entry 0 공통 font resource** 가 여러 text object 화면에서 재사용된다는 해석이 가장 강하다.
- hub 실제 값 기준 `slot 1 -> table base 0x17C2F4` 이고, entry `0` 은 `ptr=0x083E0000`, `len=0x3DDE8` 이다.
- 이 payload 시작부에는 `fnt\\0` magic 이 보이고, header 바이트는 `66 6E 74 00 0C 0F 00 0A 48 00 ...` 형태다.
- `resource[8] = 0x48` 과 writer loop 구조를 함께 보면, 현재 가장 강한 해석은 **glyph 1개 = 0x48 bytes = 12 rows * 6 bytes = 12x12 4bpp 계열** 이다.
- 샘플 lookup 확인 결과:
  - `0x30 ('0') -> 0x0001`
  - `0x82A0 ('あ') -> 0x0067`
  - `0x8341 ('ア') -> 0x00B7`
  - `0x835A ('セ') -> 0x00D0`
  - `0x838A ('リ') -> 0x00FF`
  - `0x93FA ('日') -> 0x051C`
- 따라서 이 공통 font resource 는 범용 ASCII 폰트보다 **숫자 + 일본어 중심 custom lookup font** 로 보는 편이 안전하다.
- [fnt_glyph_82A0_ah.pgm](/Users/user/test/analysis/fnt_glyph_82A0_ah.pgm), [fnt_glyph_8341_a_katakana.pgm](/Users/user/test/analysis/fnt_glyph_8341_a_katakana.pgm), [fnt_glyph_93FA_day.pgm](/Users/user/test/analysis/fnt_glyph_93FA_day.pgm) 를 `dump-fnt-glyph` 로 직접 덤프했고, ASCII preview 기준으로 `'日'` / `'ア'` 형태가 드러난다.
- 따라서 현재는 `slot 1 entry 0 -> fnt payload -> lookup table -> 12x12 glyph` 흐름을 **실제 샘플 글자까지 확인된 공통 폰트 경로** 로 본다.
- [common_fnt_manifest.json](/Users/user/test/analysis/common_fnt_manifest.json) 도 이제 생성 가능하다.
- 이 manifest 는 `0x3E0000` 공통 `fnt` payload 전체 lookup table 에서 **nonzero mapping 1698개**를 실제 문자코드/문자/glyph index/glyph offset 형태로 정리한다.
- 요약하면:
  - nonzero mappings: `1698`
  - max glyph index: `0x06A2`
  - glyph coverage end: `0x41DDE8`
  - decoded entries: `ASCII 11`, `non-ASCII 1687`, `undecodable 0`
- 따라서 폰트 쪽도 이제는 “될 것 같은 경로를 검증” 수준을 넘어, **공통 font mapping을 실제 JSON 추출본으로 확보한 단계** 다.
- 새 [common_fnt_usage_audit.json](/Users/user/test/analysis/common_fnt_usage_audit.json) 도 생성 가능하다.
- 이 audit 는 현재 추출 텍스트 `105707`자 기준으로:
  - mapped code `1698`
  - 실제 사용 mapped code `1411`
  - 현재 미사용 mapped code `287`
  - rare used (`<=2회`) mapped code `394`
  - glyph gap `0`
  - payload tail free bytes `0`
  를 집계한다.
- 즉 **현재 payload 안에는 한글 glyph 를 그대로 추가할 여유가 없고**, 본격 한글화는 `unused glyph 일부 치환` 또는 `payload 확장/재배치` 전략이 필요하다.
- 반면 decoder 허용 Shift-JIS lead byte 공간 (`0x81..0x9F`, `0xE0..0xEF`) 안의 free code 는 여전히 많아서, 병목은 code space 가 아니라 glyph space 다.
- `relocate-chunk` CLI 도 추가했다.
- 이 도구로 공통 font entry `0` 을 더 큰 위치로 복사하고 table pointer/length 를 갱신하는 테스트가 가능하다.
- 실제 검증:
  - `0x17C2F4` entry `0` 을 `0x800000`, `len=0x42000` 으로 옮긴 테스트 ROM 생성 성공
  - 새 위치 `0x800000` 는 `inspect-fnt` 기준으로 여전히 정상 `fnt` payload 로 읽힘
- 중요한 추가 규칙:
  - 공통 font pointer 는 `0x17C2F4` entry `0` 만 있는 것이 아니다.
  - `0x1823A0` 에 **같은 pointer-length 엔트리 mirror** 가 있고, 이쪽도 함께 갱신해야 한다.
- 따라서 실제 한글용 font 확장 patch 는 최소한 `registry entry + mirror table` 동시 갱신을 기본 절차로 삼아야 한다.
- `append-fnt-glyph` CLI 도 추가했다.
- 이 도구로 확장된 `fnt` payload 끝에 새 glyph slot을 append 하고, free code 에 새 lookup mapping 을 기록할 수 있다.
- 실제 검증:
  - `/private/tmp/hnr_font_expand_test_mirror.gba` 위에서 free code `0xE940` 에 source glyph `0x93FA ('日')` 를 복제
  - 새 glyph index `0x06A3`
  - 새 glyph offset `0x83DDE8`
  - `inspect-fnt` 기준 nonzero mapping `1698 -> 1699`
  - 새 glyph bytes 는 source glyph 와 동일
- 따라서 지금은 **payload 재배치 + 새 code/glyph append** 까지 끝난 상태이고, 다음 실질 과제는 실제 한글 glyph bitmap 입력이다.
- 이어서 `append-fnt-glyph-set` 으로 실제 테스트용 `PGM 12x12` glyph `가/나/다` 를 한 번에 append 했다.
- 결과는 [font_append_hangul_test.json](/Users/user/test/analysis/font_append_hangul_test.json) 에 정리했고:
  - `0xE940 -> glyph 0x06A3`
  - `0xE941 -> glyph 0x06A4`
  - `0xE942 -> glyph 0x06A5`
  - `inspect-fnt` 기준 nonzero mapping `1698 -> 1701`
- 테스트용 테이블 [hangul_test.tbl](/Users/user/test/analysis/hangul_test.tbl) 도 만들었고, 현재 `E940=가`, `E941=나`, `E942=다` 를 사용한다.
- 이 상태에서 world-map 지역명 `ソリン` (`0x1842E0`) 을 `/private/tmp/hnr_font_hangul_string_test.gba` 에서 `가나다` 로 제자리 치환했다.
- 검증:
  - raw bytes: `E940 E941 E942 00`
  - `search-text /private/tmp/hnr_font_hangul_string_test.gba 가나다 --table analysis/hangul_test.tbl` hit `1`
- 따라서 공통 renderer 경로에 대해 **확장 font + 새 한글 glyph + 실제 문자열 치환** 까지 한 번은 닫혔다.
- 다만 현재 `가/나/다` 는 품질 검증용 placeholder glyph 이고, 정식 제작용 bitmap 으로 보아서는 안 된다.
- production 단계에서는 [font_asset_workflow.md](/Users/user/test/docs/font_asset_workflow.md) 기준으로, 레퍼런스 glyph 를 편집용 `PGM` 으로 뽑아 외부 픽셀 에디터에서 다듬고 다시 가져오는 흐름을 기본으로 삼는다.
- 이를 위해 `prepare-fnt-glyph-set` CLI 를 추가했고, seed manifest 에서 편집용 `PGM` 세트와 `.tbl` 을 생성할 수 있다.
- 현재 seed manifest 는 [hangul_reference_seed_manifest.json](/Users/user/test/analysis/hangul_reference_seed_manifest.json) 이고, 생성된 작업 폴더는 [hangul_reference_workbench](/Users/user/test/analysis/hangul_reference_workbench) 이다.
- 이어서 `build-hangul-seed-manifest` CLI 를 추가해 번역 JSON에서 필요한 한글 글자를 자동 추출할 수 있게 했다.
- 현재 [translation_workset_core_ui.json](/Users/user/test/confirmed_data/translation_worksets/translation_workset_core_ui.json) 기준으로:
  - unique Hangul chars: `80`
  - seed manifest: [hangul_core_ui_seed_manifest.json](/Users/user/test/analysis/hangul_core_ui_seed_manifest.json)
  - table: [hangul_core_ui.tbl](/Users/user/test/analysis/hangul_core_ui.tbl)
  - workbench: [hangul_core_ui_workbench](/Users/user/test/analysis/hangul_core_ui_workbench)
- 즉 이제는 "몇 글자를 먼저 그릴까?"를 감으로 정하지 않고, **현재 번역 초안 기준 실제 필요 글자 세트**를 바로 편집 자산으로 올릴 수 있다.
- 여기에 더해 `slice-hangul-seed-manifest` CLI 로 상위 빈도 subset 도 자동 분리할 수 있게 했다.
- 현재 준비된 배치:
  - [hangul_core_ui_priority24_workbench](/Users/user/test/analysis/hangul_core_ui_priority24_workbench): 24글자, 완성 문장 커버 `0`
  - [hangul_core_ui_priority48_workbench](/Users/user/test/analysis/hangul_core_ui_priority48_workbench): 48글자, 완성 문장 커버 `5`
  - [hangul_core_ui_workbench](/Users/user/test/analysis/hangul_core_ui_workbench): 80글자, 완성 문장 커버 `19`
- 상세 기준은 [hangul_core_ui_priority_plan.md](/Users/user/test/analysis/hangul_core_ui_priority_plan.md), 수치 근거는 [hangul_core_ui_priority_coverage.json](/Users/user/test/analysis/hangul_core_ui_priority_coverage.json) 에 있다.
- 따라서 당장 외부 툴에서 다듬을 첫 production batch 는 `priority48` 로 두는 편이 가장 현실적이다.
- 이 `priority48` / `full80` 세트는 실제 test ROM 생성까지 이어졌다. 현재 상태는 [core_ui_test_rom_matrix.md](/Users/user/test/analysis/core_ui_test_rom_matrix.md) 에 정리했다.
- 즉 폰트 쪽은 이제 "glyph 세트를 준비했다" 단계가 아니라, **glyph 세트별로 실제 문자열 배치가 얼마나 들어가는지까지 검증된 단계** 다.
- 큰 free code block 예:
  - `0x8440..0x84FF`
  - `0x8540..0x85FF`
  - `0x8640..0x86FF`
  - `0xE940..0xE9FF`
  - `0xEA40..0xEAFF`
- 따라서 code point 설계보다 먼저 glyph 저장 전략을 결정해야 한다.
- 전략 요약은 [common_fnt_hangul_strategy.md](/Users/user/test/analysis/common_fnt_hangul_strategy.md) 에 있다.
- width/advance 쪽도 한 단계 좁혀졌다.
  - `0x01502C` multibyte 경로는 `obj + 0x18 += 0x18`
  - `0x0150CC` single-byte 경로는 `obj + 0x18 += 0x10`
  - `0x01525E..0x015278` 은 `(obj + 0x18) >> 4` 를 `obj + 0x20` 과 비교해 overflow 시 `0x015608` 으로 넘긴다.
  - `0x014A98` 는 setup 인자 `r3` 를 그대로 저장하는 대신 `floor(3 * r3 / 2)` 로 바꿔 `obj + 0x20` 에 넣는다.
  - world-map 지역명 화면의 `r3=0x0C` 는 `obj + 0x20=18` 로 변환되므로, 현재 해석상 `fullwidth 12자` 또는 `halfwidth 18자` 정도의 capacity 와 맞는다.
  - 다른 대표 caller `0x062182`, `0x065AA4`, `0x06718A` 는 `r3=20` 을 쓰므로, 같은 규칙이면 `obj + 0x20=30` 이고 `fullwidth 20자` / `halfwidth 30자` 한도와 맞는다.
- 따라서 이 텍스트 엔진은 단순 고정폭이 아니라, **fullwidth / halfwidth 를 다른 advance 로 취급하는 가변폭형 레이아웃** 을 가진다.

## 다음 할 일

1. slot `1` 을 기존 Registry A/B/C/D 분류와 충돌 없이 다시 명시
2. `obj + 0x18 / +0x20` 해석을 실제 UI 줄폭/박스 크기와 더 대조
3. `0x01570C / 0x01578C / 0x01580C / 0x01588C` 네 writer variant 차이 확인
4. 공통 renderer 경로가 아닌 다른 대표 화면도 같은 확장 font 를 문제없이 쓰는지 확인
5. 같은 길이 치환을 넘어서, 더 긴 한글 문자열의 inject / repoint 테스트를 1건 수행
6. decoder 허용 free code block 중 한글용 code range 를 더 넓게 예약할지 결정
7. 테스트 glyph `가/나/다` 를 넘어 실제 초반 UI/지명용 `10~20` 글자 세트를 만든다
8. 필요하면 `0x01570C / 0x01578C / 0x01580C / 0x01588C` writer variant 차이를 다시 확인해 화면별 예외를 줄인다

## 진행 로그

### 2026-05-08

- 조사 도구만 준비됨

### 2026-05-09

- 한글 재삽입의 실제 병목이 폰트/문자 매핑/문자폭이라는 점을 명시하고 우선순위를 상향
- `0x0514xx` UI cluster 와 `0x058720` 을 따라가 본 결과, 이 경로는 문자 렌더링보다 layout / position 보조 루틴에 가깝다는 점을 확인
- Registry B raw companion 엔트리 `86..88` 을 4bpp 로 직접 덤프했지만 글자판이 아니라 잡음에 가까워, direct raw font 후보에서는 우선 제외
- `0x03EB78 / 0x03ECCC / 0x03EDB8` 를 추가로 따라가 본 결과, 이 helper family 는 일반 일본어 폰트가 아니라 ASCII/숫자 UI glyph tilemap writer 쪽이라는 점을 확인
- world-map 지역명 표시 경로에서 `0x014A98 -> 0x014ED0` 공통 text object family 를 잡았고, `0x014ED0` 가 Shift-JIS lead byte 범위를 직접 검사하는 general Japanese text loop 후보라는 점을 확인
- `0x0152A2..0x0152C4` 에서 문자코드가 `obj + 0x04` lookup table 과 `obj + 0x08` glyph base 를 거쳐 glyph source pointer 로 바뀌는 흐름을 확인
- `0x01499C` 가 font resource header 를 해석해 object 에 lookup base, glyph base, stride 를 심는 initializer 라는 점과, 주요 text object 화면이 모두 `0x0002CC(0, 1)` 공통 resource 를 쓴다는 점을 확인
- `0x000290 / 0x0002CC / 0x000304 / 0x00033C` loader family 가 hub `0x076530` 쪽 registry record 를 통해 이 공통 font resource 를 공급한다는 점을 확인
- 공통 font resource 가 실제로 `0x17C2F4` table entry `0` -> ROM `0x3E0000` `fnt` payload 로 이어지고, `resource[8]=0x48` 과 writer loop 로부터 12x12 계열 glyph 포맷 후보를 얻었다
- `dump-fnt-glyph` CLI 를 추가해 `'あ'`, `'ア'`, `'日'` 샘플 glyph 를 실제로 덤프했고, 형태 확인까지 마쳤다
- `inspect-fnt` CLI 를 추가해 [common_fnt_manifest.json](/Users/user/test/analysis/common_fnt_manifest.json) 을 생성했고, 공통 `fnt` payload 전체 mapping 1698개를 실제 추출본으로 확보했다
- `obj + 0x18` / `obj + 0x20` 기반 width/advance 누적 구조를 잡고, world-map `r3=0x0C` 와 일반 화면군 `r3=20` caller 비교로 가변폭형 레이아웃 해석도 교차검증했다
- 이후 텍스트 추출 쪽은 coverage audit 위주로 잠깐 우선했고, 폰트/문자 매핑은 **첫 실제 한글 재삽입 테스트 직전 단계**로 다시 올릴 계획을 명시했다
- `audit-fnt-usage` CLI 를 추가해 실제 추출 텍스트 기준 font usage audit 을 재현 가능하게 만들었고, 그 결과 glyph gap `0`, payload tail free `0`, decoder-space free code `7337` 이라는 결론을 고정했다
- 따라서 지금 시점의 핵심 판단은 "한글 code point 는 충분히 배정 가능하지만, glyph 는 payload 확장/재배치 없이는 full-game 규모로 넣기 어렵다" 이다
- `relocate-chunk` CLI 를 추가해 공통 font payload relocation 실험을 재현 가능하게 만들었고, mirror table `0x1823A0` 도 함께 갱신해야 한다는 추가 조건을 확인했다
- `append-fnt-glyph` CLI 를 추가해 확장된 payload 끝에 새 glyph slot과 새 code mapping 을 실제로 append 할 수 있음을 검증했다
- `append-fnt-glyph-set` CLI 와 테스트용 `PGM 12x12` glyph `가/나/다` 세트를 추가해, 실제 한글 glyph 3개를 `0xE940..0xE942` 에 append 했다
- 테스트용 테이블 [hangul_test.tbl](/Users/user/test/analysis/hangul_test.tbl) 을 만들고, world-map 지역명 `ソリン` (`0x1842E0`) 을 `가나다` 로 제자리 치환한 `/private/tmp/hnr_font_hangul_string_test.gba` 까지 검증했다
- 따라서 지금은 **font relocation + 한글 glyph append + 실제 문자열 1건 치환** 까지 완료된 상태다
- 이어서 `prepare-fnt-glyph-set` CLI 와 [hangul_reference_seed_manifest.json](/Users/user/test/analysis/hangul_reference_seed_manifest.json) 를 추가해, 정식 제작용 glyph 작업을 위한 외부 편집 workflow 도 문서화했다
- 이후 startup intro 테스트에서 일부 글자만 보이고 나머지가 빈칸처럼 사라진 증상을 다시 확인했다.
- 원인을 점검한 결과 [hangul_core_ui_workbench](/Users/user/test/analysis/hangul_core_ui_workbench) 는 현재 `80 / 80` blank glyph 상태였고, [startup_intro_missing_workbench](/Users/user/test/analysis/startup_intro_missing_workbench) 의 보충 `8`글자만 nonzero 픽셀이 있었다.
- 그래서 `audit-pgm-glyph-set` CLI 를 추가해, blank glyph 가 하나라도 있으면 빌드 전에 바로 잡도록 했다.
- 그 뒤 Swift 경로는 핵심 흐름에서 내리고, [render_reference_font_workbench.py](/Users/user/test/scripts/render_reference_font_workbench.py) 기반 Python 경로로 바꿨다.
- 현재 startup intro 는 [startup_intro_seed_manifest.json](/Users/user/test/analysis/startup_intro_seed_manifest.json) `14`글자를 [startup_intro_nanumsquare_workbench](/Users/user/test/analysis/startup_intro_nanumsquare_workbench) 로 렌더링해 독립 build 경로를 갖는다.
- 이 경로는 최종 글리프 완성본이 아니라 **실제 폰트 기반 seed** 를 만드는 용도이며, 현재 시작점은 `NanumSquareR.ttf` 로 고정했다.
- startup intro seed 의 첫 설정은 `y_offset=-1` 이었지만, 실제 확대 화면 기준으로 top row 점유가 과하고 bottom row 여백이 2줄 남아 **1픽셀 위로 들린 것처럼 보이는 상태** 였다.
- 따라서 startup intro `NanumSquareR` seed 기준 baseline 은 현재 `y_offset=0` 으로 다시 맞췄다.
- 추가 확인으로, 공통 `fnt` 원본 glyph 는 실제로 `0,17,34` 세 값만 쓰는 3-level palette 계열임을 다시 대조했다.
- 따라서 `NanumSquareR` seed 에서 나온 anti-alias grayscale 을 그대로 append 하면 startup 화면처럼 빨강/파랑 speckle 이 섞일 수 있고, 현재는 seed 생성 단계에서 **native 3-level (`0/17/34`) 양자화** 를 기본값으로 강제한다.
- startup intro build script 는 이제 blank glyph 검사뿐 아니라 `--allowed-values 0,17,34 --fail-on-disallowed` 검사도 통과해야 한다.
- 이후 시각 QA 결과, 회색을 줄여도 `NanumSquareR` 는 `12x12` binary glyph 에서 자소 구조가 쉽게 무너졌다.
- 그래서 현재 startup intro 쪽은 **완전 2단계(`0/34`) binary glyph** 를 기본 실험축으로 돌리면서, 동시에 폰트 후보를 다시 고르는 단계로 넘어갔다.
- 요약 판단과 외부 조사 결과는 [font_candidate_survey.md](/Users/user/test/analysis/font_candidate_survey.md) 에 정리했다.
- 그 후 `Galmuri` 패키지를 받아 `Galmuri11.ttf` 도 실제 후보로 비교했지만, 현재 자동 렌더링 조건에서는 기대만큼 안정적이지 않았다.
- 그래서 startup intro active workbench 는 지금 [startup_intro_active_workbench](/Users/user/test/analysis/startup_intro_active_workbench) 로 다시 옮겼다.
- 현재 active 설정은 `font-size=11`, `y_offset=0`, `binary2 cutoff_ratio=0.2` 이다.
- 즉 glyph 별 최대 밝기 기준으로 **하위 20%만 잘라내는 비율 컷** 경로다.
- 비교용 시트는 [startup_font_d2coding_size_sheet.png](/Users/user/test/analysis/startup_font_d2coding_size_sheet.png), [startup_font_candidate_galmuri_sheet.png](/Users/user/test/analysis/startup_font_candidate_galmuri_sheet.png), [startup_font_galmuri11_size_sheet.png](/Users/user/test/analysis/startup_font_galmuri11_size_sheet.png) 에 남겼다.
- 추가로 `gba-free-fonts` 의 `SourceHanSansKR`, `SourceHanMonoKR` 는 [import_bmfont_workbench.py](/Users/user/test/scripts/import_bmfont_workbench.py) 로 startup intro 에 실제 비교 적용 가능하다는 것을 확인했고, 결과는 [startup_intro_font_compare.md](/Users/user/test/analysis/startup_intro_font_compare.md) 와 [startup_intro_font_compare_sheet.png](/Users/user/test/analysis/startup_intro_font_compare_sheet.png) 에 남겼다.
- 사용자 제공 atlas [maruminyahangul_12x12.png](/Users/user/test/third_party/font_atlases/maruminyahangul_12x12.png) 도 project-local 로 복사했다.
- [import_hangul_syllable_atlas.py](/Users/user/test/scripts/import_hangul_syllable_atlas.py) 를 추가해, `12x12`, `64`열, row-major `U+AC00..U+D7A3` atlas 를 startup intro seed manifest 기준 workbench 로 직접 변환할 수 있게 했다.
- 이 atlas 기반 startup intro 테스트 ROM 은 [hnr_startup_intro_maruminyahangul12.gba](/Users/user/test/patched_roms/font_compare/maruminyahangul12_startup/hnr_startup_intro_maruminyahangul12.gba) 이다.
- 위 atlas 는 표준 완성형 순서를 그대로 따르므로, 현재는 giant 문자 목록 대신 [maruminyahangul_12x12.metadata.json](/Users/user/test/third_party/font_atlases/maruminyahangul_12x12.metadata.json) 으로 순서 규칙을 관리한다.
