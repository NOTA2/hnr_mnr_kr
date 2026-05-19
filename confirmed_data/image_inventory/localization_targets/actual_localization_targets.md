# Actual Localization Tilemap/Image Targets

실제 화면에서 일본어/영문 UI가 보이거나 한글화 필요성이 높은 그래픽/타일맵 후보만 추린 목록입니다.

- contact sheet: `confirmed_data/image_inventory/localization_targets/actual_localization_targets_contact_sheet.png`
- total targets: `11`

| id | label | status | offset | seen | goal |
| --- | --- | --- | --- | --- | --- |
| `field_obj_alchemy_label` | 필드 OBJ 라벨 錬成 | `registered_in_gui` | `0x005323AC` | 錬成 | 연성 |
| `field_obj_aseyashi_label` | 필드 OBJ 라벨 アセやし | `registered_in_gui` | `0x0053257C` | アセやし | 아세야자 |
| `field_menu_status_label` | 필드/메뉴 라벨 ステータス | `registered_in_gui` | `0x00532764` | ステータス | 상태 |
| `field_menu_save_label` | 필드/메뉴 라벨 セーブ | `registered_in_gui` | `0x0053293C` | セーブ | 저장 |
| `battle_popup_alchemy_commands` | 전투 팝업 錬成/つかう/すてる/もどる | `registered_in_gui` | `0x003AF23C` | 錬成 / つかう / すてる / もどる | 연성 / 사용 / 버리기 / 돌아가기 |
| `battle_card_alchemy_panel` | 전투 CARD/ALCHEMY 패널 | `registered_in_gui` | `0x003A206C` | CARD / ALCHEMY / 2枚 | 카드 / 연성 / 2장 |
| `card_list_frame_controls` | 카드 리스트 ID/BACK/NEXT/いいえ UI | `extracted_needs_repoint_or_slot_strategy` | `0x003A3540` | ID / BACK / NEXT / いいえ | ID / 뒤로 / 다음 / 아니요 |
| `title_logo_copyright` | 타이틀 로고/부제/저작권 | `registered_in_gui` | `0x007E0000` | 鋼の錬金術師 / 迷走の輪舞曲 / 저작권 | 강철의 연금술사 / 미주의 윤무곡 또는 확정 제목 / 저작권 |
| `alchemy_notebook_label` | 연성수첩 메뉴 라벨 | `needs_source_trace` | `-` | 錬成手帳 | 연성수첩 |
| `battle_hud_names_attack` | 전투 HUD エド/アル/こうげき | `partially_registered` | `-` | エド / アル / こうげき | 에드 / 알 / 공격 |
| `battle_attack_label` | 전투 명령 こうげき | `needs_source_trace` | `-` | こうげき | 공격 |

## Notes

- `field_obj_alchemy_label`: 사용자 ss1 OBJ 레이어에서 실제 표시 확인. LZ77 이미지 블록 후보로 GUI에 등록되어 있다.
- `field_obj_aseyashi_label`: 사용자 ss2 OBJ 레이어에서 실제 표시 확인. 고유명/지명 여부는 별도 번역 정책 확인이 필요하다.
- `field_menu_status_label`: 주변 LZ77 스캔으로 얻은 메뉴 라벨 후보. 실제 화면 추가 확인 시 우선 검증 대상.
- `field_menu_save_label`: 주변 LZ77 스캔으로 얻은 메뉴 라벨 후보. 실제 화면 추가 확인 시 우선 검증 대상.
- `battle_popup_alchemy_commands`: 화면순 RLE 편집 및 적용 no-op 테스트 통과.
- `battle_card_alchemy_panel`: 화면순 RLE 편집 및 적용 no-op 테스트 통과. 일본어 `枚`가 보이는 실제 한글화 대상.
- `card_list_frame_controls`: 화면순 추출은 완료. 현재 same-slot no-op 적용은 RLE 압축 크기 초과로 GUI 교체 대상에서 제외.
- `title_logo_copyright`: 화면순 RLE 편집 및 적용 no-op 테스트 통과. 가장 큰 이미지 한글화 대상.
- `alchemy_notebook_label`: 런타임 BG1 tilemap에서 실제 표시 확인. 아직 ROM 블록/텍스트 렌더러 역추적 필요.
- `battle_hud_names_attack`: HUD 소형 글자/명령 라벨. 일부는 영문판 소형 글자 블록과 관련 가능성이 높고 추가 역추적 대상.
- `battle_attack_label`: 전투 하단 명령 버튼 라벨만 별도 crop으로 분리했다. 글자 타일 출처 역추적 대상.
