# Runtime Tilemap Localization Targets

런타임 BG tilemap에서 실제 한글화 대상 텍스트가 보이는 영역만 잘라낸 목록입니다.

- contact sheet: `confirmed_data/image_inventory/runtime_tilemap_targets/runtime_tilemap_targets_contact_sheet.png`
- total targets: `12`

| id | scene | bg | tile rect | seen | goal | unique tiles |
| --- | --- | ---: | --- | --- | --- | ---: |
| `current_review_battle_attack_command_bg1` | `current_review_ss1` | `1` | `[23, 14, 7, 5]` | こうげき | 공격 | `15` |
| `current_review_battle_alchemy_command_bg1` | `current_review_ss2` | `1` | `[23, 14, 7, 5]` | れんせい | 연성 | `3` |
| `current_review_battle_notebook_command_bg1` | `current_review_ss3` | `1` | `[23, 14, 7, 5]` | てちょう | 수첩 | `15` |
| `current_review_battle_item_command_bg1` | `current_review_ss4` | `1` | `[23, 14, 7, 5]` | アイテム | 아이템 | `15` |
| `current_review_battle_enemy_name_bg1` | `current_review_ss2` | `1` | `[21, 13, 7, 1]` | メインビースト | 메인비스트 | `7` |
| `current_review_alchemy_popup_bg0` | `current_review_ss5` | `0` | `[8, 2, 12, 13]` | 錬成 / もどる | 연성 / 돌아가기 | `93` |
| `current_review_card_alchemy_panel_bg1` | `current_review_ss5` | `1` | `[6, 0, 22, 18]` | CARD / ALCHEMY / 2枚 | 카드 / 연성 / 2장 | `101` |
| `current_review_card_list_controls_bg1` | `current_review_ss6` | `1` | `[0, 0, 18, 20]` | ID / BACK / NEXT / いいえ | ID / 뒤로 / 다음 / 아니요 | `76` |
| `alchemy_notebook_label_bg1` | `no_entry8_latest_ss2` | `1` | `[0, 0, 6, 2]` | 錬成手帳 | 연성수첩 | `12` |
| `battle_hud_actor_names_bg1` | `no_entry8_ss3` | `1` | `[0, 14, 16, 4]` | エド / アル | 에드 / 알 | `13` |
| `battle_attack_label_bg1` | `no_entry8_ss3` | `1` | `[24, 14, 6, 2]` | こうげき | 공격 | `12` |
| `card_list_controls_bg1` | `no_entry8_latest_ss3` | `1` | `[0, 0, 18, 20]` | ID / BACK / NEXT / いいえ | ID / 뒤로 / 다음 / 아니요 | `76` |

## Notes

- `current_review_battle_attack_command_bg1`: 사용자 ss1. 전투 하단 우측 버튼 라벨. ROM 이미지 블록 매칭은 아직 없어서 런타임 폰트/문자 타일 후보로 분리.
- `current_review_battle_alchemy_command_bg1`: 사용자 ss2. 전투 하단 우측 버튼 라벨. ROM 이미지 블록 매칭은 아직 없어서 런타임 폰트/문자 타일 후보로 분리.
- `current_review_battle_notebook_command_bg1`: 사용자 ss3. 전투 하단 우측 버튼 라벨. ROM 이미지 블록 매칭은 아직 없어서 런타임 폰트/문자 타일 후보로 분리.
- `current_review_battle_item_command_bg1`: 사용자 ss4. 전투 하단 우측 버튼 라벨. ROM 이미지 블록 매칭은 아직 없어서 런타임 폰트/문자 타일 후보로 분리.
- `current_review_battle_enemy_name_bg1`: 사용자 ss2 우측 적 이름. 일반 대사 텍스트보다 작은 BG1 HUD 글리프 계열이다. 화면에서는 7개 runtime tile(0x0EE-0x0F4, palette 12)로 보이며, ROM의 HUD 이름 테이블에서는 `ﾒｲﾝﾋﾞｰｽﾄ`(0x003D18D8)로 확인된다. 기존에 メイビースト로 읽었던 것은 중간 `ン`이 빠진 오독이었다.
- `current_review_alchemy_popup_bg0`: 사용자 ss5. RLE 0x003AF23C와 매칭되는 화면순 팝업. 기존 GUI의 연성/사용/버리기/돌아가기 팝업 항목에서 교체 가능.
- `current_review_card_alchemy_panel_bg1`: 사용자 ss5. RLE 0x003A206C와 매칭되는 화면순 패널. 기존 GUI의 전투 카드/ALCHEMY 패널 항목에서 교체 가능.
- `current_review_card_list_controls_bg1`: 사용자 ss6. RLE 0x003A3540와 매칭되는 카드 리스트 UI. 기존 GUI의 카드 리스트/BACK/NEXT UI 항목에서 교체 가능.
- `alchemy_notebook_label_bg1`: ROM 블록 매칭이 잡히지 않아 런타임 폰트/문자 타일 가능성이 높은 BG tilemap 영역.
- `battle_hud_actor_names_bg1`: 전투 HUD 좌측 이름/수치 영역. 소형 글자 블록과 함께 검토할 대상.
- `battle_attack_label_bg1`: 전투 하단 명령 버튼 라벨. 화면에는 텍스트처럼 보이나 BG tilemap상 전용 타일로 배치된다.
- `card_list_controls_bg1`: 카드 리스트 UI 레이어. RLE 0x003A3540 화면순 항목은 GUI 교체 대상으로 승격했고, 압축 초과 시 repoint로 적용한다.
