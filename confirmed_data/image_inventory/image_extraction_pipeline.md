# 이미지 추출 파이프라인 준비

- 마지막 갱신: `2026-06-12`
- 상태: `prepared`
- 목표: 이미지에 구워진 텍스트 자산을 review unit 단위로 찾고, 덤프/수정/교체 가능한 작업 폴더를 준비한다.

## 우선 review unit 순서

- `title_logo_wordmark` (순서=1)
  - 작업 폴더: `confirmed_data/image_inventory/workspaces/01_title_logo_wordmark`
  - 작업 폴더 상태: `active_scaffold`
  - 탐색 방식: 타이틀 화면 런타임 케이스 등록 -> 영문판/일판 LZ77 diff 확인 -> 후보가 안 보이면 VRAM/tilemap/palette 역추적
- `title_screen_static_menu_wordmarks` (순서=2)
  - 작업 폴더: `confirmed_data/image_inventory/workspaces/02_title_screen_static_menu_wordmarks`
  - 작업 폴더 상태: `active_scaffold`
  - 탐색 방식: 타이틀 화면 런타임 케이스 등록 -> 영문판/일판 LZ77 diff 확인 -> 후보가 안 보이면 VRAM/tilemap/palette 역추적
- `event_or_cutscene_text_cards` (순서=3)
  - 작업 폴더: `confirmed_data/image_inventory/workspaces/03_event_or_cutscene_text_cards`
  - 작업 폴더 상태: `active_scaffold`
  - 탐색 방식: 대표 장면 스크린샷 수집 -> 카드성 오버레이 후보 LZ77 블록 탐색 -> 덤프 비교
- `dialogue_window_frame_art` (순서=4)
  - 작업 폴더: `confirmed_data/image_inventory/workspaces/04_dialogue_window_frame_art`
  - 작업 폴더 상태: `active_scaffold`
  - 탐색 방식: 대사창 스크린샷 -> 프레임/판넬 후보 아트 덤프 -> 텍스트 유무 확인
- `portrait_headshot_assets` (순서=5)
  - 작업 폴더: `confirmed_data/image_inventory/workspaces/05_portrait_headshot_assets`
  - 작업 폴더 상태: `active_scaffold`
  - 탐색 방식: 대표 대사 장면 스크린샷 -> portrait 후보 아트 덤프 -> 동일 인물 변형 수집
- `ui_panel_label_art` (순서=6)
  - 작업 폴더: `confirmed_data/image_inventory/workspaces/06_ui_panel_label_art`
  - 작업 폴더 상태: `active_scaffold`
  - 탐색 방식: 메뉴/인벤토리/상태창 스크린샷 -> 패널 후보 시트 덤프 -> 텍스트 여부 확인
- `ui_icon_badge_wordmarks` (순서=7)
  - 작업 폴더: `confirmed_data/image_inventory/workspaces/07_ui_icon_badge_wordmarks`
  - 작업 폴더 상태: `pruned_summary`
  - 요약: `confirmed_data/image_inventory/workspaces/07_ui_icon_badge_wordmarks/README.md`
  - 탐색 방식: 대표 UI 캡처 -> 작은 4bpp 배지 후보 덤프 -> 문자인지 아이콘인지 구분
- `battle_result_or_reward_banners` (순서=8)
  - 작업 폴더: `confirmed_data/image_inventory/workspaces/08_battle_result_or_reward_banners`
  - 작업 폴더 상태: `active_scaffold`
  - 탐색 방식: 전투 결과 화면 캡처 -> 배너 후보 LZ77/4bpp 덤프 -> 고정 워드마크 여부 확인

## 작업 단계

- `1. 대표 화면 확보`: 각 review unit 별로 실제 게임 화면 스크린샷 또는 참고 이미지를 최소 대표 케이스로 모아, 무엇을 찾아야 하는지 고정한다. 모든 화면을 수작업 수집하는 방식으로 진행하지 않는다.
- `2. 영문판/일판 ROM 차이 확인`: 영문 패치 ROM 이 같은 화면을 수정했다면 같은 오프셋 LZ77 diff, 확장 영역 LZ77 후보, raw/tile 후보를 먼저 비교한다.
- `3. 후보 자산 탐색`: LZ77 scan, 4bpp dump, raw tile dump 를 쓰되, 결과가 보이지 않으면 실패가 아니라 tilemap/palette 분리 가능성으로 본다.
- `4. 런타임 타일맵 추적`: 후보가 contact sheet 에 드러나지 않는 화면은 VRAM/tilemap/palette/OAM 조합으로 재구성되는 자산으로 보고 런타임 덤프나 스크린샷 기반 역추적을 수행한다.
- `5. 덤프 시각 비교`: 후보 덤프를 PNG/타일 시트 형태로 모아 실제 화면과 비교하고, 맞는 후보만 남긴다.
- `6. 편집용 산출물 분리`: 수정 대상이 확인되면 exports 폴더에 편집용 산출물을 만들고, notes 폴더에 포맷/팔레트/압축 여부를 기록한다.
- `7. 교체 전략 결정`: 원위치 덮어쓰기, 재압축 후 교체, 포인터 재배치 중 어느 방식이 필요한지 결정한다.

## 도구 참고

- `scan_lz77`: `python3 -m gba_kor_tool scan-lz77 <rom>`
- `dump_4bpp`: `python3 -m gba_kor_tool dump-4bpp <rom> <offset> <tile-count> <output>`
- `decompress_lz77`: `python3 -m gba_kor_tool decompress-lz77 <rom> <offset> <output>`
- `runtime_case`: `python3 scripts/register_runtime_visual_case.py <screenshot> --case-id <id> --visible-text <text> --context <context> --source-type unknown`
- `english_diff`: `python3 scripts/compare_english_patch_lz77_graphics.py`

## 후보 스캔 기준

- LZ77 scan 파일: `confirmed_data/image_inventory/lz77_blocks.json`
- 존재 여부: `True`
- 블록 수: `518`
- 메모: review unit 후보 탐색의 출발점으로 쓰는 전역 LZ77 스캔 결과다.

## 작업 폴더 구조

- 루트: `confirmed_data/image_inventory/workspaces`
- 하위 폴더: `candidates, dumps, exports, notes`
- 생성 수: `28`

## 첫 목표

- `01_title_logo_wordmark`
- `02_title_screen_static_menu_wordmarks`
- `03_event_or_cutscene_text_cards`

## 비고

- 이 문서는 실제 이미지 교체를 완료했다는 뜻이 아니라, review unit 별 추출/덤프/정리 루프를 바로 시작할 수 있게 scaffold 를 준비한 것이다. 타이틀처럼 contact sheet 에 바로 보이지 않는 그래픽은 런타임 tilemap-aware 추적으로 승격한다.
