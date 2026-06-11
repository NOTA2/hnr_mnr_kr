# Actual Localization Tilemap/Image Targets

실제 화면에서 일본어 UI가 보이는 그래픽/타일맵 후보만 추린 목록입니다. 영어 워드마크는 번역 대상에서 제외합니다.

- contact sheet: `confirmed_data/image_inventory/localization_targets/actual_localization_targets_contact_sheet.png`
- total targets: `24`

| id | label | status | offset | seen | goal |
| --- | --- | --- | --- | --- | --- |
| `field_obj_alchemy_label` | 필드 OBJ 라벨 錬成 | `registered_in_gui` | `0x005323AC` | 錬成 | 연성 |
| `field_obj_item_label` | 필드 OBJ 라벨 アイテム | `registered_in_gui` | `0x0053257C` | アイテム | 아이템 |
| `field_menu_status_label` | 필드/메뉴 라벨 ステータス | `registered_in_gui` | `0x00532764` | ステータス | 상태 |
| `field_menu_save_label` | 필드/메뉴 라벨 セーブ | `registered_in_gui` | `0x0053293C` | セーブ | 저장 |
| `battle_bottom_attack_command` | 전투 하단 커맨드 こうげき | `registered_in_gui` | `0x003ABF5C` | こうげき | 공격 |
| `battle_bottom_notebook_command` | 전투 하단 커맨드 てちょう | `registered_in_gui` | `0x003AC0DC` | てちょう | 수첩 |
| `battle_bottom_alchemy_command` | 전투 하단 커맨드 れんせい | `registered_in_gui` | `0x003AC25C` | れんせい | 연성 |
| `battle_bottom_item_command` | 전투 하단 커맨드 アイテム | `registered_in_gui` | `0x003AC3DC` | アイテム | 아이템 |
| `battle_bottom_special_command` | 전투 하단 커맨드 ひっさつ | `registered_in_gui` | `0x003AC55C` | ひっさつ | 필살기 |
| `card_book_right_category_tabs` | 카드 책자 오른쪽 탭 金属/石/自然/無機 | `registered_in_gui` | `0x003A3540` | 金属 ／ 石 ／ 自然 ／ 無機 | 금속 ／ 돌 ／ 자연 ／ 무기 |
| `title_new_game` | 타이틀 はじめから | `registered_in_gui` | `0x007E9404` | はじめから | 처음부터 |
| `title_continue` | 타이틀 つづきから | `registered_in_gui` | `0x007E95E0` | つづきから | 이어하기 |
| `title_link` | 타이틀 通信 | `registered_in_gui` | `0x007E97A4` | 通信 | 통신 |
| `battle_confirm_ok_yes_no_popup` | 전투 확인 팝업 OK?/はい/いいえ | `registered_in_gui` | `0x003ABB9C` | OK? ／ はい ／ いいえ | OK? ／ 예 ／ 아니요 |
| `battle_popup_alchemy_commands` | 전투 팝업 錬成/つかう/すてる/もどる | `registered_in_gui` | `0x003AF23C` | 錬成 ／ つかう ／ すてる ／ もどる | 연성 ／ 사용 ／ 버리기 ／ 돌아가기 |
| `battle_card_alchemy_panel` | 전투 카드 패널 2枚 | `registered_in_gui` | `0x003A206C` | 2枚 | 2장 |
| `card_list_frame_controls` | 카드 리스트 いいえ UI | `registered_in_gui` | `0x003A3540` | いいえ | 아니요 |
| `card_list_iie_variant_003A5E50` | 카드 리스트 いいえ UI 변형 1 | `registered_in_gui` | `0x003A5E50` | いいえ | 아니요 |
| `card_list_iie_variant_003A6E24` | 카드 리스트 いいえ UI 변형 2 | `registered_in_gui` | `0x003A6E24` | いいえ | 아니요 |
| `card_list_iie_variant_003A7C3C` | 카드 리스트 いいえ UI 변형 3 | `registered_in_gui` | `0x003A7C3C` | いいえ | 아니요 |
| `card_list_iie_variant_003A8894` | 카드 리스트 いいえ UI 변형 4 | `registered_in_gui` | `0x003A8894` | いいえ | 아니요 |
| `card_list_iie_variant_003A9624` | 카드 리스트 いいえ UI 변형 5 | `registered_in_gui` | `0x003A9624` | いいえ | 아니요 |
| `card_list_iie_variant_003AA4C0` | 카드 리스트 いいえ UI 변형 6 | `registered_in_gui` | `0x003AA4C0` | いいえ | 아니요 |
| `title_logo_copyright` | 타이틀 로고/부제 | `registered_in_gui` | `0x007E0000` | 鋼の錬金術師 ／ 迷走の輪舞曲 | 강철의 연금술사 ／ 미주의 윤무곡 또는 확정 제목 |

## Notes

- `field_obj_alchemy_label`: 사용자 ss1 OBJ 레이어에서 실제 표시 확인. LZ77 이미지 블록 후보로 GUI에 등록되어 있다.
- `field_obj_item_label`: 사용자 ss2 OBJ 레이어에서 실제 표시 확인. 기존 판독 アセやし는 픽셀 폰트의 アイテム 오독으로 정정했다.
- `field_menu_status_label`: 주변 LZ77 스캔으로 얻은 메뉴 라벨 후보. 실제 화면 추가 확인 시 우선 검증 대상.
- `field_menu_save_label`: 주변 LZ77 스캔으로 얻은 메뉴 라벨 후보. 실제 화면 추가 확인 시 우선 검증 대상.
- `battle_bottom_attack_command`: 전투 하단 버튼은 BG1 타일맵이 같은 VRAM 슬롯을 가리키고, 원본 픽셀은 ROM raw 4bpp 0x180바이트 블록에서 복사된다. GUI 업로드 시 같은 오프셋에 직접 적용한다.
- `battle_bottom_notebook_command`: 전투 하단 버튼은 BG1 타일맵이 같은 VRAM 슬롯을 가리키고, 원본 픽셀은 ROM raw 4bpp 0x180바이트 블록에서 복사된다. GUI 업로드 시 같은 오프셋에 직접 적용한다.
- `battle_bottom_alchemy_command`: 전투 하단 버튼은 BG1 타일맵이 같은 VRAM 슬롯을 가리키고, 원본 픽셀은 ROM raw 4bpp 0x180바이트 블록에서 복사된다. GUI 업로드 시 같은 오프셋에 직접 적용한다.
- `battle_bottom_item_command`: 전투 하단 버튼은 BG1 타일맵이 같은 VRAM 슬롯을 가리키고, 원본 픽셀은 ROM raw 4bpp 0x180바이트 블록에서 복사된다. GUI 업로드 시 같은 오프셋에 직접 적용한다.
- `battle_bottom_special_command`: 전투 하단 버튼은 BG1 타일맵이 같은 VRAM 슬롯을 가리키고, 원본 픽셀은 ROM raw 4bpp 0x180바이트 블록에서 복사된다. GUI 업로드 시 같은 오프셋에 직접 적용한다.
- `card_book_right_category_tabs`: ss6~ss9 책자 오른쪽 세로 탭 4개. RLE 0x003A3540 전체 카드 리스트 블록에서 오른쪽 탭 영역만 분리한 GUI 직접 교체 항목.
- `title_new_game`: 타이틀 RLE 블록을 32열 화면형 레이아웃으로 재추출한 4배 편집 PNG. GUI 업로드 시 same-slot RLE 적용 대상.
- `title_continue`: 타이틀 RLE 블록을 32열 화면형 레이아웃으로 재추출한 4배 편집 PNG. GUI 업로드 시 same-slot RLE 적용 대상.
- `title_link`: 타이틀 RLE 블록을 32열 화면형 레이아웃으로 재추출한 4배 편집 PNG. GUI 업로드 시 same-slot RLE 적용 대상.
- `battle_confirm_ok_yes_no_popup`: 사용자가 제공한 current_review ss2에서 확인. 화면순 RLE 편집 PNG와 tile_map이 정상 생성되어 GUI 직접 교체 대상으로 등록한다.
- `battle_popup_alchemy_commands`: 화면순 RLE 편집 및 적용 no-op 테스트 통과.
- `battle_card_alchemy_panel`: 화면순 RLE 편집 및 적용 no-op 테스트 통과. CARD/ALCHEMY는 영어 워드마크라 번역 대상에서 제외하고, 일본어 `枚`만 실제 한글화 대상으로 본다.
- `card_list_frame_controls`: 화면순 추출 및 no-op 적용 확인 완료. ID/BACK/NEXT는 영어 워드마크라 번역 대상에서 제외하고, 일본어 `いいえ`만 실제 한글화 대상으로 본다.
- `card_list_iie_variant_003A5E50`: 주변 RLE 확장 추출에서 확인한 카드 리스트 UI 변형. 영어 ID/BACK/NEXT는 제외하고 일본어 `いいえ`만 실제 한글화 대상으로 본다.
- `card_list_iie_variant_003A6E24`: 주변 RLE 확장 추출에서 확인한 카드 리스트 UI 변형. 영어 ID/BACK/NEXT는 제외하고 일본어 `いいえ`만 실제 한글화 대상으로 본다.
- `card_list_iie_variant_003A7C3C`: 주변 RLE 확장 추출에서 확인한 카드 리스트 UI 변형. 영어 ID/BACK/NEXT는 제외하고 일본어 `いいえ`만 실제 한글화 대상으로 본다.
- `card_list_iie_variant_003A8894`: 주변 RLE 확장 추출에서 확인한 카드 리스트 UI 변형. 영어 ID/BACK/NEXT는 제외하고 일본어 `いいえ`만 실제 한글화 대상으로 본다.
- `card_list_iie_variant_003A9624`: 주변 RLE 확장 추출에서 확인한 카드 리스트 UI 변형. 영어 ID/BACK/NEXT는 제외하고 일본어 `いいえ`만 실제 한글화 대상으로 본다.
- `card_list_iie_variant_003AA4C0`: 주변 RLE 확장 추출에서 확인한 카드 리스트 UI 변형. 영어 ID/BACK/NEXT는 제외하고 일본어 `いいえ`만 실제 한글화 대상으로 본다.
- `title_logo_copyright`: 화면순 RLE 편집 및 적용 no-op 테스트 통과. 저작권/영문 표기는 제외하고 일본어 로고/부제만 실제 한글화 대상으로 본다.
