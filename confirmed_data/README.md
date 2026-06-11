# 확정 데이터

이 폴더는 **확정된 기준 작업 데이터**만 모아 둔 곳이다.

## 구성

- [extracted_texts](/Users/user/test/confirmed_data/extracted_texts/README.md)
- [font_assets](/Users/user/test/confirmed_data/font_assets/README.md)
- [text_layout](/Users/user/test/confirmed_data/text_layout/README.md)
- [dialogue_metadata](/Users/user/test/confirmed_data/dialogue_metadata/README.md)
- [translation_worksets](/Users/user/test/confirmed_data/translation_worksets/README.md)
- [translation_workspace](/Users/user/test/confirmed_data/translation_workspace/README.md)
- [localization_workbench](/Users/user/test/confirmed_data/localization_workbench/README.md)
- [image_inventory](/Users/user/test/confirmed_data/image_inventory/README.md)

역할별 분류와 정리 기준은
[data_role_inventory.md](/Users/user/test/docs/structure/data_role_inventory.md) 를 본다.

## 규칙

- `analysis/` 는 탐색/가설/실험용이다.
- `confirmed_data/` 는 실제 번역/검수/재삽입 입력으로 쓰는 안정 데이터다.
- 새 기준 추출본이 확정되면 이 폴더 아래로 올리고, 발견 과정과 보조 증거는 `analysis/` 에 남긴다.
- `confirmed_data/` 안에서도 기준본, GUI 상태, runtime evidence, generated
  index 를 구분한다. 큰 폴더라도 active role 이 닫히기 전에는 바로
  삭제하지 않는다.
