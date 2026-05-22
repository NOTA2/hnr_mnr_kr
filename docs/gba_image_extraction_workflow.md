# GBA Image Extraction Workflow

## 기준

- GBA의 일반적인 배경 그래픽은 `8x8 tile data + screenblock tilemap + palette` 조합이다.
- 그래서 ROM의 4bpp/RLE/LZ77 블록을 그냥 가로로 펼친 이미지는 실제 화면과 순서가 다를 수 있다.
- 런타임 VRAM/세이브 상태 기반 crop은 위치 추적용 참고자료일 뿐, 그 자체를 한글화 편집 원본으로 보지 않는다.

## 사용 가능한 편집 원본 조건

한글화 작업대에 직접 노출하는 이미지는 아래 조건을 모두 만족해야 한다.

- ROM offset이 확인된 RLE/LZ77/raw 그래픽 블록이다.
- 원본 payload가 tile 단위로 되돌아갈 수 있다.
- `tile_map.json`이 화면 위치와 원본 tile index를 연결한다.
- no-op 삽입 테스트 또는 동일 수준의 검증으로 다시 ROM에 적용 가능하다.
- `context_crop*.png` 같은 런타임 참고 이미지는 후보 갤러리에서 제외한다.
- LZ77 필드/메뉴 라벨과 RLE 타이틀/전투 이미지는 GUI 업로드 후 자동 적용 대상이다.

## 현재 분리

- `confirmed_data/image_inventory/runtime_rle_screen_order/screen_order_manifest.json`
  - `replacement_target=true`: 편집 원본으로 사용 가능
  - `replacement_target=false`: 런타임/세이브 기반 참고자료
- `confirmed_data/image_inventory/localization_targets/actual_localization_targets.json`
  - 바로 한글화에 사용할 수 있는 대상만 남긴 목록
- GUI 확인/수정:
  - `python3 scripts/run_localization_workbench.py --host 127.0.0.1 --port 8766`
  - 브라우저에서 `http://127.0.0.1:8766`
  - 카테고리 `이미지 작업`에서 원본 PNG 확인, 다운로드/수정, 업로드
  - 업로드하면 해당 항목은 자동 적용을 시도하고, `이미지 교체 전체 적용`은 현재 등록된 교체 이미지를 한꺼번에 다시 적용한다.
  - 결과가 마음에 들지 않으면 `현재 이미지 원상복구`로 해당 항목만 되돌리거나, `이미지 교체 전체 원상복구`로 모든 교체 이미지를 비활성화한 뒤 리뷰 ROM을 다시 만든다.
  - 원상복구는 업로드 PNG 파일을 삭제하지 않고 `previous_replacement_path`/`replacement_history`에 경로를 남긴다.
  - `이미지 수정 프롬프트 생성` 패널은 편집 원본의 가로/세로와 확인된 원문/권장 번역을 자동으로 채우고, 사용자가 이미지 위에서 드래그한 영역을 `x/y/width/height`로 채운다.

## 현재 바로 편집 가능한 묶음

- 필드/메뉴 LZ77 라벨: `confirmed_data/image_inventory/edit_packs/field_menu_labels`
- 타이틀 메뉴 RLE 라벨: `confirmed_data/image_inventory/edit_packs/title_screen`
  - `PUSH START`/`はじめから`/`つづきから`/`通信`은 8열 raw 타일 펼침이 아니라 32열 화면형 레이아웃으로 편집한다.
- 타이틀 로고/저작권 RLE 화면순 항목: `confirmed_data/image_inventory/runtime_rle_screen_order/timeline_with_rle/frame_001200_bg0_rle_007E0000`

## 수동 정렬 보정

타일은 맞는데 몇 픽셀 밀려 보이면 아래 도구로 숫자를 넣어 보정한다.

```bash
python3 scripts/tune_runtime_rle_alignment.py \
  confirmed_data/image_inventory/runtime_rle_screen_order/no_entry8_latest_ss1/frame_007084_bg0_rle_003AF23C/tile_map.json \
  --shift-x 0 \
  --shift-y 0
```

- `--shift-x`: 양수면 재조립 타일을 오른쪽으로 이동
- `--shift-y`: 양수면 재조립 타일을 아래로 이동
- `--add-shift-x`, `--add-shift-y`: 현재 값에 더해서 미세 조정
- 보정값은 `tile_map.json`의 `alignment_adjustment_pixels`에 저장되고, 이후 ROM 적용에도 같은 값이 쓰인다.

## 이번에 고친 밀림 원인

- 기존 코드는 BG scroll의 1~7픽셀 잔여값을 무시했다.
- 예: `frame_007084`는 BG scroll이 x/y 2픽셀이어서 타일 재조립이 2픽셀씩 밀릴 수 있었다.
- 이제 `fine_scroll_pixels`를 `tile_map.json`에 저장하고, preview와 apply 양쪽에서 같은 좌표식을 쓴다.
