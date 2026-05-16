# Text Reinsertion Progress

읽기 규칙: 이 문서는 재삽입 안정화가 현재 작업의 직접 목표일 때만 읽는다.

이 문서는 추출한 문자열을 ROM에 다시 넣는 작업의 진행 상황을 기록합니다.

## 목적

- 번역문을 안전하게 재삽입한다.
- 포인터 수정 규칙을 정리한다.
- 제어 코드가 있는 문자열도 안정적으로 처리한다.

## 현재 상태

- 상태: `IN PROGRESS`

## 구현된 것

- 같은 길이 이하 문자열 제자리 교체
- 자유 공간 문자열 주입
- 포인터 갱신
- 번역 JSON 일괄 적용 기본 기능
- `.tbl` 기반 custom 2-byte code 인코딩
- 확장된 공통 font payload 를 전제로 한 테스트 문자열 치환 1건
- `.tbl` + 기존 `cp932` fallback 혼합 인코딩
- core UI batch test ROM 생성 및 적용 리포트

## 아직 부족한 것

- 게임별 텍스트 뱅크별 예외 처리
- 절대 포인터가 바로 안 잡히는 뱅크 대응
- 제어 코드 친화적인 삽입 검증
- 더 긴 한글 문자열의 inject / repoint 테스트
- 실제 화면 렌더링 확인

## 다음 할 일

1. `priority48 compact` 또는 `full80 compact` ROM 기준으로 실제 화면 렌더링을 확인
2. `full80` 기본 번역에서 남은 `4 skipped_no_pointer` save/menu/지명 케이스의 간접 참조 구조를 찾거나 inject/repoint 대안을 만든다
3. `0x3Dxxxx` 계열 문자열에 대한 삽입 가능성 판단
4. 제어 코드가 섞인 문자열 삽입 테스트
5. 실패/예외 사례 문서화
6. 번역 JSON 리포트 개선

## 진행 로그

### 2026-05-08

- `apply-translations` 기본 기능 추가
- 테스트 JSON으로 1건 패치 성공

### 2026-05-09

- `build-translation-set` 로 여러 추출 JSON을 번역 작업용 JSON 한 개로 묶는 흐름 추가
- `save_menu_texts` 같이 `translation` 필드가 없던 추출본도 재삽입 workset 에 넣을 수 있게 정리

### 2026-05-10

- 공통 `fnt` 확장본과 [hangul_test.tbl](/Users/user/test/analysis/hangul_test.tbl) 을 이용해, world-map 지역명 `ソリン` (`0x1842E0`) 을 `가나다` 로 제자리 치환한 `/private/tmp/hnr_font_hangul_string_test.gba` 를 만들었다
- raw bytes `E940 E941 E942 00` 과 `search-text --table analysis/hangul_test.tbl` hit `1` 로 문자열 치환을 검증했다
- 따라서 재삽입 쪽도 이제 "도구만 준비됨"이 아니라, **확장 font 를 전제로 한 실제 한글 문자열 1건 검증** 단계로 올라왔다
- `priority48` glyph 세트를 붙인 font ROM `/private/tmp/hnr_font_core_ui_priority48_font.gba` 와 `full80` glyph 세트를 붙인 font ROM `/private/tmp/hnr_font_core_ui_full80_font.gba` 를 만들었다
- `priority48` 기본 번역 ROM `/private/tmp/hnr_core_ui_priority48_text_test.gba` 는 `4 in_place, 1 skipped_no_pointer`, compact ROM `/private/tmp/hnr_core_ui_priority48_compact_text_test.gba` 는 `5 in_place` 까지 확인했다
- `full80` 기본 번역 ROM `/private/tmp/hnr_core_ui_full80_text_test.gba` 는 `15 in_place, 4 skipped_no_pointer`, compact ROM `/private/tmp/hnr_core_ui_full80_compact_text_test.gba` 는 `19 in_place` 까지 확인했다
- 이어서 시작 화면 전용 문자열 `4`건도 [startup_intro_texts.json](/Users/user/test/confirmed_data/extracted_texts/startup_intro_texts.json) 으로 분리했고, 부족한 `8`글자를 보충한 뒤 `/Users/user/test/patched_roms/startup_intro_active/hnr_startup_intro_test.gba` 기준 `4 in_place` 까지 확인했다
- 요약 표는 [core_ui_test_rom_matrix.md](/Users/user/test/analysis/core_ui_test_rom_matrix.md) 에 정리했다
- 이후 반복 검증을 쉽게 하려고, 시작 화면만 빠르게 다시 만드는 [build_startup_intro_test.sh](/Users/user/test/scripts/build_startup_intro_test.sh) 도 추가했다
