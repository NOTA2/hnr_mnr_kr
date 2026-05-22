# Image Resource Progress

읽기 규칙: 이 문서는 이미지 리소스 조사가 활성 단계로 올라왔을 때만 읽는다.

이 문서는 텍스트가 아닌 이미지/UI 리소스 조사 진행 상황을 기록합니다.

## 목적

- 타이틀, 버튼, UI 이미지, 튜토리얼 그림 같은 리소스를 추출하고 교체할 수 있게 한다.

## 현재 상태

- 상태: `IN PROGRESS`
- 기준: 런타임/세이브 기반 재구성 crop은 참고자료로만 유지하고, ROM offset 및 적용 경로가 확인된 편집 원본만 한글화 대상에 올린다.

## 예상 조사 항목

- 이미지 데이터 위치
- 압축 여부
- 타일/팔레트 구조
- 재삽입 가능 여부

## 다음 할 일

1. 텍스트 구조와 폰트 조사가 어느 정도 안정화된 뒤 시작
2. 주요 UI 이미지 후보 영역 찾기
3. 압축 루틴 재사용 가능성 확인

## 진행 로그

### 2026-05-21

- RLE screen-order 산출물에서 `replacement_target=true/false`를 분리했다.
- `context_crop*.png`는 세이브 상태 기반 참고자료로 분류하고, workbench 편집 원본/candidate gallery에서 제외했다.
- BG fine scroll 잔여 픽셀을 반영해 화면순 RLE 미리보기와 적용 좌표가 같은 기준을 쓰도록 수정했다.
- 수동 보정 도구 `scripts/tune_runtime_rle_alignment.py`를 추가했다.
- 바로 한글화 가능한 실제 대상 목록은 `confirmed_data/image_inventory/localization_targets/actual_localization_targets.json`으로 축소했다.
- 필드/메뉴 라벨 4개는 LZ77 자동 적용 대상으로 연결했다.
- 타이틀 메뉴 RLE edit pack을 재추출하고, 예전 raw 로고 항목 대신 화면순 로고 항목을 사용하도록 정리했다.
- GUI에 `이미지 교체 전체 적용` 버튼을 추가했다.

### 2026-05-08

- 아직 착수하지 않음
