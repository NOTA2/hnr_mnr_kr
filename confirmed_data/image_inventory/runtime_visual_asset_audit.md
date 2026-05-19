# Runtime Visual Asset Audit

- 상태: `reopened_runtime_screenshot_required`
- 마지막 갱신: `2026-05-19`

정적 LZ77/raw contact sheet 에서는 한글화 대상 이미지 라벨이 거의 보이지 않았지만, 실제 플레이에서는 번역해야 할 이미지/타일 텍스트가 다수 보일 수 있다. 따라서 이미지 감사를 닫지 않고 **실플레이 스크린샷 기반 역추적**으로 진행한다.

## 왜 정적 추출만으로 부족한가

- GBA 화면의 텍스트형 그래픽은 LZ77 타일만 펼쳐서는 안 보일 수 있다.
- 실제 화면은 타일 그래픽 + 타일맵 + 팔레트 + OAM/sprite + 런타임 문자열 렌더링 조합이다.
- 일부는 구워진 이미지가 아니라 소형 폰트/글리프 시트와 문자열 테이블 조합일 수 있다.
- 따라서 앞으로는 플레이 스크린샷을 기준으로 문제 화면을 등록하고, 각 화면에서 보이는 일본어를 source type 별로 역분류한다.

## 현재 확인된 케이스

- `battle_hud_small_font_00534874`: `font_or_glyph_sheet` / `patched_from_english_rom` / 전투 HUD 의 작은 캐릭터 이름/수치 글자

## 열린 케이스

- `title_screen_logo_and_menu`: `unknown` / 鋼の錬金術師 / 迷走の輪舞曲 / つづきから / はじめから / 通信 / screenshot=`confirmed_data/image_inventory/runtime_screenshots/title_screen_logo_and_menu.png`
  - context: 타이틀 화면 로고와 고정 메뉴
  - notes: 정적 LZ77 contact sheet 와 영문판 same-offset diff 로는 바로 확정되지 않음. VRAM/tilemap 기반 역추적 필요.
- `title_screen_main_logo_menu`: `unknown` / 鋼の錬金術師 / 迷走の輪舞曲 / つづきから / はじめから / 通信 / screenshot=`confirmed_data/image_inventory/runtime_screenshots/title_screen_main_logo_menu.png`
  - context: 타이틀 화면 메인 로고, 부제, 메뉴 라벨, 저작권 표기
  - notes: 한글화 필요가 확인된 대표 케이스. 모든 플레이 화면을 수작업 수집하는 방식이 아니라, 타이틀/메뉴/전투/도감/결과처럼 대표 화면을 등록한 뒤 영문판 diff 와 VRAM/tilemap-aware 역추적으로 자산 위치를 찾는다.

## 앞으로의 처리 순서

1. 미번역 이미지/타일이 보이는 플레이 스크린샷을 케이스로 등록한다.
2. 보이는 문구가 일반 문자열, 폰트/글리프, 타일맵 UI, 구운 이미지 중 무엇인지 분류한다.
3. 영문판 동일 화면 또는 동일 ROM 블록과 비교한다.
4. 정적 contact sheet 에 보이지 않는 경우에는 누락으로 닫지 않고 VRAM/tilemap/palette 추적으로 승격한다.
5. 실제 교체가 필요한 경우에만 GUI 이미지 작업 항목으로 승격한다.
