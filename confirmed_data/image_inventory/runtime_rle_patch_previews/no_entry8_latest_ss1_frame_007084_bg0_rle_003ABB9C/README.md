# Runtime RLE Patch Preview

- scene: `no_entry8_latest_ss1`
- frame: `frame_007084`
- BG: `0`
- RLE: `0x003ABB9C`
- matched screen tiles: `32`

## Files

- `context_crop.png`: 실제 BG 화면 배치 crop
- `context_crop_grid.png`: 실제 BG 화면 배치 crop + RLE 매칭 타일 격자
- `context_crop_4x.png`: 사람이 보기 좋은 4배 확대본
- `matched_tiles_screen_order.png`: 해당 RLE에서 온 타일만 화면 순서대로 재조립
- `matched_tiles_screen_order_grid.png`: 화면 순서 재조립 + 타일 격자
- `matched_tiles_screen_order_4x.png`: 사람이 보기 좋은 4배 확대본
- `tile_map.json`: 화면 타일 좌표와 RLE 원본 타일 index 매핑
