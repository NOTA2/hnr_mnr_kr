# 이미지 검토 인벤토리

이 폴더는 **이미지에 구워진 텍스트 inventory / 이미지 자산 검토 상태**를 모아두는 곳이다.

## 현재 파일

- `image_text_inventory.json`
- `image_text_inventory.md`
- `image_extraction_pipeline.json`
- `image_extraction_pipeline.md`
- `lz77_blocks.json`
- `workspaces/`

## 사용 원칙

- 기준 추출 텍스트와 이미지에 구워진 텍스트는 분리해서 관리한다.
- 이 inventory 는 막연한 bucket 이 아니라 실제 검토 단위에 가까운 `review_units` 중심으로 유지한다.
- 각 review unit 은 이후 추출 산출물을 모을 전용 workspace 를 갖는다.
- `lz77_blocks.json` 은 전역 후보 스캔 결과이며, title/logo/card/UI 자산 탐색의 시작점으로 쓴다.

## 재생성

```bash
python3 scripts/build_image_text_inventory.py
python3 scripts/build_image_extraction_pipeline.py
```
