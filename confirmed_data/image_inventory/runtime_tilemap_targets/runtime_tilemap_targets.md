# Runtime Tilemap Localization Targets

런타임 BG tilemap에서 실제 한글화 대상 텍스트가 보이는 영역만 잘라낸 목록입니다.

- contact sheet: `confirmed_data/image_inventory/runtime_tilemap_targets/runtime_tilemap_targets_contact_sheet.png`
- total targets: `4`

| id | scene | bg | tile rect | seen | goal | unique tiles |
| --- | --- | ---: | --- | --- | --- | ---: |
| `alchemy_notebook_label_bg1` | `no_entry8_latest_ss2` | `1` | `[0, 0, 6, 2]` | 錬成手帳 | 연성수첩 | `12` |
| `battle_hud_actor_names_bg1` | `no_entry8_ss3` | `1` | `[0, 14, 16, 4]` | エド / アル | 에드 / 알 | `13` |
| `battle_attack_label_bg1` | `no_entry8_ss3` | `1` | `[24, 14, 6, 2]` | こうげき | 공격 | `12` |
| `card_list_controls_bg1` | `no_entry8_latest_ss3` | `1` | `[0, 0, 18, 20]` | ID / BACK / NEXT / いいえ | ID / 뒤로 / 다음 / 아니요 | `76` |

## Notes

- `alchemy_notebook_label_bg1`: ROM 블록 매칭이 잡히지 않아 런타임 폰트/문자 타일 가능성이 높은 BG tilemap 영역.
- `battle_hud_actor_names_bg1`: 전투 HUD 좌측 이름/수치 영역. 소형 글자 블록과 함께 검토할 대상.
- `battle_attack_label_bg1`: 전투 하단 명령 버튼 라벨. 화면에는 텍스트처럼 보이나 BG tilemap상 전용 타일로 배치된다.
- `card_list_controls_bg1`: 카드 리스트 UI 레이어. same-slot RLE 교체는 아직 압축 크기 초과라 tilemap/확장 전략 후보로 둔다.
