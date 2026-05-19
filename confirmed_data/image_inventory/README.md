# 이미지 검토 인벤토리

이 폴더는 **이미지에 구워진 텍스트 inventory / 이미지 자산 검토 상태**를 모아두는 곳이다.

## 현재 파일

- `image_text_inventory.json`
- `image_text_inventory.md`
- `image_extraction_pipeline.json`
- `image_extraction_pipeline.md`
- `workspaces/`

## 사용 원칙

- 기준 추출 텍스트와 이미지에 구워진 텍스트는 분리해서 관리한다.
- GUI의 역할은 편집 가능한 원본 PNG 다운로드, 사용자가 수정한 PNG 업로드, 업로드된 교체본의 자동 적용 트리거까지만 담당한다.
- 어떤 이미지/타일을 추출해야 하는지 판정하고, 수정 가능한 PNG로 재구성하고, 업로드 이미지를 ROM 블록으로 변환/패치하는 책임은 추출/적용 스크립트가 가진다.
- 이 inventory 는 막연한 bucket 이 아니라 실제 검토 단위에 가까운 `review_units` 중심으로 유지한다.
- 각 review unit 은 이후 추출 산출물을 모을 전용 workspace 를 갖는다.
- `.ss` 저장상태 기반 분석은 캡처 화면을 등록하는 용도가 아니다. 캡처에서 런타임 타일을 뽑고 ROM 블록과 매칭한 뒤, 교체 가능한 개별 이미지 블록만 GUI 후보로 승격한다.
- 한 후보를 찾으면 주변 LZ77/RLE 블록도 같이 훑어 같은 라벨 묶음의 추가 후보를 찾는다.
- 원시 타일 배열만으로 글자가 어긋나 보이면 BG `screenblock` tilemap/scroll/OAM 데이터를 렌더링해 실제 화면 배치로 다시 확인한다.
- tilemap/OAM 렌더링 결과는 교체 파일이 아니라 내부 조합 방식을 찾기 위한 분석 지도다. 이 지도에서 보이는 글자를 ROM raw tilemap, LZ77/RLE 그래픽 블록, 또는 텍스트 렌더러로 역추적해야 실제 교체가 가능하다.
- 사람이 알아보기 어려운 RLE 레이아웃/전체 후보 시트는 GUI에 노출하지 않고, 실제 텍스트가 보이는 선별 후보만 남긴다.
- RLE 조각은 기본적으로 `scripts/build_readable_rle_layouts.py`로 8/16/24/32-column 4배 확대본을 만들고, savestate와 연결된 경우 `scripts/build_runtime_rle_patch_previews.py`로 실제 화면 배치 재조립본과 `tile_map.json`을 함께 만든다.
- 이미지 수정은 찢어진 원시 RLE 시트가 아니라 `runtime_rle_patch_previews`의 확대/재조립 PNG를 기준으로 설계하고, 실제 삽입은 `tile_map.json`의 RLE tile index 매핑에 맞춰 raw tile/RLE 블록 쪽에 반영한다.
- 영문판은 이미지/RLE 수정 레퍼런스로 적극 사용한다. `scripts/compare_english_patch_rle_graphics.py`로 same-offset RLE diff를 뽑으면 영문판이 실제로 고친 이미지 블록 목록과 4배 확대 PNG를 얻을 수 있다.
- 영문판이 같은 오프셋을 수정한 경우, 한국어 교체 작업은 일본판 원본만 보지 말고 영문판의 타일 수, 축약 방식, 배치 방식을 먼저 참고한다.

## 재생성

```bash
python3 scripts/build_image_text_inventory.py
python3 scripts/build_image_extraction_pipeline.py
PYTHONPATH=.vendor python3 scripts/build_readable_rle_layouts.py
PYTHONPATH=.vendor python3 scripts/build_runtime_rle_patch_previews.py --probe-dir confirmed_data/image_inventory/runtime_user_captures/no_entry8_latest_ss1 --bg 0 --rle-offset 0x003AF23C
PYTHONPATH=.vendor python3 scripts/compare_english_patch_rle_graphics.py
```
