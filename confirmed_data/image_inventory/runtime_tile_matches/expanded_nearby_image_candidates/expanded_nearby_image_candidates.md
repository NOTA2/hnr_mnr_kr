# Expanded Nearby Image Candidates

확인된 일본어 UI 이미지 주변을 더 넓게 펼친 검토용 시트입니다.

## Outputs

- `screen_order_all`: `confirmed_data/image_inventory/runtime_tile_matches/expanded_nearby_image_candidates/screen_order_all_contact_sheet.png`
- `screen_order_unique`: `confirmed_data/image_inventory/runtime_tile_matches/expanded_nearby_image_candidates/screen_order_unique_contact_sheet.png`
- `field_menu_lz77_broad`: `confirmed_data/image_inventory/runtime_tile_matches/expanded_nearby_image_candidates/field_menu_lz77_broad_contact_sheet.png`

## Notes

- `screen_order_*`는 런타임 BG tilemap을 적용한 화면순 RLE 후보라 타일 밀림이 가장 적다.
- `lz77_*`는 ROM 주변 블록을 넓게 본 원본 후보라, 실제 적용 전 화면/팔레트/타일맵 검증이 필요하다.
- 영어만 보이는 워드마크는 한글화 대상에서 제외하고, 일본어가 보이는 후보만 다음 단계로 승격한다.
