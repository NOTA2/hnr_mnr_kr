# 이미지 추출 파이프라인 준비

- 마지막 갱신: `2026-05-18`
- 상태: `prepared`
- 목표: 이미지에 구워진 텍스트 자산을 review unit 단위로 찾고, 덤프/수정/교체 가능한 작업 폴더를 준비한다.

## 우선 review unit 순서

- `title_logo_wordmark` (순서=1)
  - 작업 폴더: `confirmed_data/image_inventory/workspaces/01_title_logo_wordmark`
  - 탐색 방식: 타이틀 화면 진입 스크린샷 확보 -> LZ77 후보 스캔 -> 4bpp 덤프 비교
- `title_screen_static_menu_wordmarks` (순서=2)
  - 작업 폴더: `confirmed_data/image_inventory/workspaces/02_title_screen_static_menu_wordmarks`
  - 탐색 방식: 타이틀 화면 캡처 -> 후보 타일 시트 덤프 -> 라벨별 분리 가능성 확인
- `event_or_cutscene_text_cards` (순서=3)
  - 작업 폴더: `confirmed_data/image_inventory/workspaces/03_event_or_cutscene_text_cards`
  - 탐색 방식: 대표 장면 스크린샷 수집 -> 카드성 오버레이 후보 LZ77 블록 탐색 -> 덤프 비교
- `dialogue_window_frame_art` (순서=4)
  - 작업 폴더: `confirmed_data/image_inventory/workspaces/04_dialogue_window_frame_art`
  - 탐색 방식: 대사창 스크린샷 -> 프레임/판넬 후보 아트 덤프 -> 텍스트 유무 확인
- `portrait_headshot_assets` (순서=5)
  - 작업 폴더: `confirmed_data/image_inventory/workspaces/05_portrait_headshot_assets`
  - 탐색 방식: 대표 대사 장면 스크린샷 -> portrait 후보 아트 덤프 -> 동일 인물 변형 수집
- `ui_panel_label_art` (순서=6)
  - 작업 폴더: `confirmed_data/image_inventory/workspaces/06_ui_panel_label_art`
  - 탐색 방식: 메뉴/인벤토리/상태창 스크린샷 -> 패널 후보 시트 덤프 -> 텍스트 여부 확인
- `ui_icon_badge_wordmarks` (순서=7)
  - 작업 폴더: `confirmed_data/image_inventory/workspaces/07_ui_icon_badge_wordmarks`
  - 탐색 방식: 대표 UI 캡처 -> 작은 4bpp 배지 후보 덤프 -> 문자인지 아이콘인지 구분
- `battle_result_or_reward_banners` (순서=8)
  - 작업 폴더: `confirmed_data/image_inventory/workspaces/08_battle_result_or_reward_banners`
  - 탐색 방식: 전투 결과 화면 캡처 -> 배너 후보 LZ77/4bpp 덤프 -> 고정 워드마크 여부 확인

## 작업 단계

- `1. 대표 화면 확보`: 각 review unit 별로 실제 게임 화면 스크린샷 또는 참고 이미지를 모아, 무엇을 찾아야 하는지 고정한다.
- `2. 후보 자산 탐색`: LZ77 scan, 4bpp dump, raw tile dump 를 써서 해당 화면과 닮은 후보 자산을 찾는다.
- `3. 덤프 시각 비교`: 후보 덤프를 PNG/타일 시트 형태로 모아 실제 화면과 비교하고, 맞는 후보만 남긴다.
- `4. 편집용 산출물 분리`: 수정 대상이 확인되면 exports 폴더에 편집용 산출물을 만들고, notes 폴더에 포맷/팔레트/압축 여부를 기록한다.
- `5. 교체 전략 결정`: 원위치 덮어쓰기, 재압축 후 교체, 포인터 재배치 중 어느 방식이 필요한지 결정한다.

## 도구 참고

- `scan_lz77`: `python3 -m gba_kor_tool scan-lz77 <rom>`
- `dump_4bpp`: `python3 -m gba_kor_tool dump-4bpp <rom> <offset> <tile-count> <output>`
- `decompress_lz77`: `python3 -m gba_kor_tool decompress-lz77 <rom> <offset> <output>`

## 작업 폴더 구조

- 루트: `confirmed_data/image_inventory/workspaces`
- 하위 폴더: `candidates, dumps, exports, notes`
- 생성 수: `32`

## 첫 목표

- `01_title_logo_wordmark`
- `02_title_screen_static_menu_wordmarks`
- `03_event_or_cutscene_text_cards`

## 비고

- 이 문서는 실제 이미지 교체를 완료했다는 뜻이 아니라, review unit 별 추출/덤프/정리 루프를 바로 시작할 수 있게 scaffold 를 준비한 것이다.
