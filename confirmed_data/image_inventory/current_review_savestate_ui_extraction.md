# Current Review Savestate UI Extraction

입력 저장상태: `patched_roms/current_review/hnr_localization_review.ss1` ~ `hnr_localization_review.ss9`

## 생성물

- 저장상태 화면 contact sheet: `confirmed_data/image_inventory/runtime_user_captures/current_review_ss_contact_sheet.png`
- 한글화 UI crop contact sheet: `confirmed_data/image_inventory/runtime_tilemap_targets/runtime_tilemap_targets_contact_sheet.png`
- 저장상태별 BG/OBJ 렌더: `confirmed_data/image_inventory/runtime_tilemaps/current_review_ss*/`
- 저장상태별 ROM 블록 매칭: `confirmed_data/image_inventory/runtime_tile_matches/current_review_ss*/`
- 화면순 RLE 재조립 contact sheet: `confirmed_data/image_inventory/runtime_rle_screen_order/current_review_ss_screen_order_contact_sheet.png`
- 전투 하단 커맨드 raw edit pack: `confirmed_data/image_inventory/edit_packs/battle_command_buttons/`
- 카드 책자 오른쪽 탭 edit pack: `confirmed_data/image_inventory/edit_packs/card_book_right_tabs/`

## 이번 저장상태에서 새로 뽑은 UI

| id | 저장상태 | 보이는 문구 | 목표 | 처리 |
| --- | --- | --- | --- | --- |
| `current_review_battle_attack_command_bg1` | `ss1` | `こうげき` | 공격 | ROM raw 4bpp `0x003ABF5C`, GUI 직접 교체 가능 |
| `current_review_battle_alchemy_command_bg1` | `ss2` | `れんせい` | 연성 | ROM raw 4bpp `0x003AC25C`, GUI 직접 교체 가능 |
| `current_review_battle_notebook_command_bg1` | `ss3` | `てちょう` | 수첩 | ROM raw 4bpp `0x003AC0DC`, GUI 직접 교체 가능 |
| `current_review_battle_item_command_bg1` | `ss4` | `アイテム` | 아이템 | ROM raw 4bpp `0x003AC3DC`, GUI 직접 교체 가능 |
| `battle_bottom_special_command` | 인접 ROM 블록 | `ひっさつ` | 필살기 | ROM raw 4bpp `0x003AC55C`, GUI 직접 교체 가능 |
| `current_review_alchemy_popup_bg0` | `ss5` | `錬成 / もどる` | 연성 / 돌아가기 | 기존 GUI `연성/사용/버리기/돌아가기 팝업` 항목에서 교체 |
| `current_review_card_alchemy_panel_bg1` | `ss5` | `2枚` | 2장 | CARD/ALCHEMY는 영어라 제외, 일본어 `枚`만 기존 GUI 화면순 RLE 항목에서 교체 |
| `current_review_card_list_controls_bg1` | `ss6` | `いいえ` | 아니요 | ID/BACK/NEXT는 영어라 제외, 일본어 `いいえ`만 기존 GUI `카드 리스트/BACK/NEXT UI` 항목에서 교체 |
| `card_book_right_category_tabs` | `ss6`~`ss9` | `金属 / 石 / 自然 / 無機` | 금속 / 돌 / 자연 / 무기 | RLE `0x003A3540`의 오른쪽 탭만 분리한 GUI 직접 교체 항목 |

## 판정

- `ss1`~`ss4` 하단 버튼 문구는 BG1 tilemap에 올라가지만, 원본은 압축 LZ77/RLE가 아니라 ROM의 raw 4bpp 48x16px 블록이다. 타일맵 엔트리는 네 상태 모두 같은 VRAM tile slot `0x0211`~`0x021C`를 가리키고, 게임이 선택 커맨드에 맞는 raw 블록을 같은 슬롯에 복사한다.
- 각 raw 블록은 `6x2 tiles`, `0x180 bytes`라서 압축 크기 초과/repoint 문제가 없다. GUI 업로드 시 같은 오프셋에 0x180바이트를 직접 덮어쓴다.
- `ss5`의 팝업/패널과 `ss6`의 카드 리스트는 ROM RLE 블록과 매칭됐다. 이미 GUI의 직접 교체 가능 항목으로 연결되어 있으므로 새 중복 항목은 만들지 않는다.
- `ss6`~`ss9` 오른쪽 책자 탭은 `金属 / 石 / 自然 / 無機` 4개 카테고리다. 전체 카드 리스트 RLE `0x003A3540` 안에 포함되지만, 편집 실수를 줄이기 위해 오른쪽 탭 전용 crop/tile_map을 별도 등록했다.
- `ss7`~`ss9`는 카드 리스트의 선택/카테고리 상태만 다른 변형으로 보이며, 기본 교체 대상은 `0x003A3540` 카드 리스트 항목과 동일하다.
- 영어 워드마크는 번역 대상에서 제외한다. 그래픽 후보 판정은 일본어가 픽셀 이미지로 박힌 경우만 한글화 대상으로 본다.
