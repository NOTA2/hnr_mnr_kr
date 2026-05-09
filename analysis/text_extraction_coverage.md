# Text Extraction Coverage

이 문서는 "텍스트를 100% 다 추출했는가?"를 어떻게 판단할지와, 현재 기준 상태를 정리한다.

## 먼저 결론

- ROM 안에 **전체 텍스트 총량이 적혀 있는 단일 카운터**가 있다고 가정하면 안 된다.
- 따라서 `100% 완료`는 숫자 하나를 찾는 문제가 아니라, **텍스트를 공급하는 구조를 전부 식별했는가**의 문제다.
- 실무적으로는 아래 4가지를 모두 만족할 때 `operational 100%` 에 가깝다고 본다.

## 100% 판정 기준

1. 공통 텍스트 렌더러/로더가 읽는 상위 공급원을 목록화했다.
2. 각 공급원마다 실제 추출 규칙을 최소 1개 확보했다.
3. 남은 non-hit 영역이 텍스트 미회수인지, control/data stub 인지 분류됐다.
4. 대표 플레이 흐름에서 새 일본어 문자열이 더 이상 나오지 않는다.

즉 "모든 문자열 수"를 세는 방식이 아니라, **텍스트 source inventory 를 닫는 방식**으로 판정한다.

## 현재 inventory 기준

### 이미 추출 규칙이 확보된 공급원

- standalone plain bank
  - [system_messages.json](/Users/user/test/analysis/system_messages.json): `4`
  - [item_texts.json](/Users/user/test/analysis/item_texts.json): `47`
  - [location_texts.json](/Users/user/test/analysis/location_texts.json): `10`
  - [credits_texts.json](/Users/user/test/analysis/credits_texts.json): `10`
  - [battle_texts.json](/Users/user/test/analysis/battle_texts.json): `104`
  - [ability_texts.json](/Users/user/test/analysis/ability_texts.json): `409`
  - [material_texts.json](/Users/user/test/analysis/material_texts.json): `43`
  - [ui_skill_texts.json](/Users/user/test/analysis/ui_skill_texts.json): `24`
- command-stream / mixed bank
  - [save_menu_prefixed_texts.json](/Users/user/test/analysis/save_menu_prefixed_texts.json): `12`
  - [registry_d_fc_script_texts.json](/Users/user/test/analysis/registry_d_fc_script_texts.json): `244`
  - [registry_a_entry8_prefixed_texts.json](/Users/user/test/analysis/registry_a_entry8_prefixed_texts.json): `9823`

### 상위 registry 관점에서 본 상태

- Registry A (`18` entries)
  - entry `8`: `01 FF <u16 문자수>` 규칙으로 대형 mixed script bank 추출 완료
  - entry `8` 은 [registry_a_entry8_cluster_catalog.json](/Users/user/test/analysis/registry_a_entry8_cluster_catalog.json) / [registry_a_entry8_cluster_overview.md](/Users/user/test/analysis/registry_a_entry8_cluster_overview.md) 기준으로 `72`개 cluster 작업 지도로 재구성됐다.
  - cluster `71` 은 [registry_a_entry8_cluster71_pre_save_texts.json](/Users/user/test/analysis/registry_a_entry8_cluster71_pre_save_texts.json) `228`건 일반 이벤트/진행 힌트와 [registry_a_entry8_cluster71_save_segment_texts.json](/Users/user/test/analysis/registry_a_entry8_cluster71_save_segment_texts.json) `12`건 save/menu block 으로 다시 분리해 둘 수 있다.
  - entry `12`: gameplay/item text `22`건 확인. [registry_a_entry12_texts.json](/Users/user/test/analysis/registry_a_entry12_texts.json) 으로 별도 확보
  - entry `12` 의 `22`건 중 `16`건은 기존 `item_texts` / gameplay terms 와 중복이고, `6`건은 기존 workset 에 없던 텍스트다.
  - tail `9..17` 의 현재 분류는 [registry_a_tail_classification.json](/Users/user/test/analysis/registry_a_tail_classification.json) 에 정리했다.
  - entry `9..11`, `13..17` 은 현재 기준으로 clean text 공급원이라고 확정되지 않았다.
- Registry B (`115` entries)
  - 현 단계에서는 live text bank 근거가 약하다.
  - direct font / asset / companion 소비 쪽 근거가 더 강하며, 텍스트 추출 주력 대상은 아니다.
- Registry C (`25` entries)
  - 현재 텍스트 hit 없음.
- Registry D (`100` entries)
  - `FC 00 ... FC` mixed script 규칙으로 `244`건 추출
  - hit entry `82 / 100`
  - 남은 [registry_d_unresolved_entries.json](/Users/user/test/analysis/registry_d_unresolved_entries.json) `18`개 중 대부분은 `2-byte sentinel/control stub`
  - entry `70` 도 현재는 raw bytes 패턴상 `control-only script table` 로 보는 쪽이 강해, 실질 미확인 대사 후보는 거의 남지 않았다.

## 현재 상태 평가

### 강하게 커버됐다고 볼 수 있는 영역

- 시스템 메시지
- 지역명
- UI 기술명
- 전투 기술명/설명
- 능력/재료 계열 용어
- save/menu command-stream
- Registry D 이벤트/튜토리얼 대사 다수
- Registry A entry `8` 대형 스토리/이벤트/메뉴 mixed bank

### 아직 100%라고 단정하면 안 되는 이유

- Registry A entry `8` 이 매우 큰 bank 라서, 내부 cluster 구조는 잡았지만 장면/용도 라벨링이 아직 덜 됐다.
- Registry A entry `8` 은 cluster `71` save/menu 분리까지는 끝났지만, 나머지 cluster 수동 라벨링은 아직 덜 됐다.
- Registry A entry `12` 같이 상위 registry 관점에서 뒤늦게 보이는 text source 가 추가로 있을 수 있다.
- 대표 렌더러가 읽는 자원은 많이 좁혀졌지만, 실제 플레이 전수 확인은 아직 안 했다.
- 따라서 지금은 **"대부분의 핵심 텍스트 공급원은 잡았지만, 100% 단정은 이르다"** 가 가장 정확하다.

## 실무적 완료 조건

아래를 만족하면 `텍스트 추출 operational 100%` 로 선언해도 무리가 적다.

1. Registry A tail (`9..17`) 의 text/no-text 성격을 더 분류한다.
2. Registry D unresolved `18`개 중 entry `70` 을 최종적으로 control-only 로 확정하거나 텍스트를 회수한다.
3. Registry A entry `8` cluster 에 장면/용도 라벨을 붙인다.
4. 실제 플레이 샘플에서 새 일본어가 더 나오지 않는지 1회 이상 확인한다.

## 현재 한 줄 판단

- **정확한 총개수 기반 100% 판정은 불가능**
- **source inventory 기반으로는 많이 왔고, 아직 소수 미확인 공급원이 남아 있음**
- **현재 체감 상태는 "거의 다 왔지만, 선언 전 마지막 감사 단계"**
