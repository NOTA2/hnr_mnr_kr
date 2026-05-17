# Image Inventory

이 폴더는 **이미지에 구워진 텍스트 inventory / 이미지 자산 검토 상태**를 모아두는 곳이다.

## 현재 파일

- `image_text_inventory.json`
- `image_text_inventory.md`

## 사용 원칙

- canonical extracted text 와 baked image text 는 분리해서 관리한다.
- 이 inventory 는 막연한 bucket 이 아니라 실제 검토 단위에 가까운 `review_units` 중심으로 유지한다.

## 재생성

```bash
python3 scripts/build_image_text_inventory.py
```
