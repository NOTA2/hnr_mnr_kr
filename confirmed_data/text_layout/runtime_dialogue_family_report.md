# runtime 대사 family 보고서

- 마지막 갱신: `2026-05-18`

## entry8_singleline_counted_dialogue_profile

- source_group: `registry_a_entry8_prefixed_texts`
- record family: `entry8_prefixed_01ff_script_line`
- runtime 후보: `shared_text_object_r3_20`
- record 수: `9823`
- 최대 글자 수: `19`
- 글자 수 95퍼센타일: `14`
- 개행 포함 record 수: `0`
- 최대 명시적 개행 수: `0`
- 개행 기준 최대 렌더 줄 수: `1`

- payload 대부분이 짧은 counted line 이며, 현재 추출 텍스트 안에는 명시적 개행 바이트가 없다.
- 남은 핵심 불확실성은 record 경계가 아니라, 이 짧은 줄들이 runtime 에서 어떻게 이어져 보이는가이다.
- runtime page-flow 가 시각적으로 확인되기 전까지는 외부 script control 로 이어질 수 있는 짧은 단일 줄 record 로 보고 번역을 짧게 유지한다.

## registry_d_multiline_fc_dialogue_profile

- source_group: `registry_d_fc_script_texts`
- record family: `registry_d_fc_stop_script_line`
- runtime 후보: `shared_text_object_r3_20`
- record 수: `244`
- 최대 글자 수: `90`
- 글자 수 95퍼센타일: `38`
- 개행 포함 record 수: `166`
- 최대 명시적 개행 수: `6`
- 개행 기준 최대 렌더 줄 수: `7`

- 많은 payload 가 이미 명시적 개행을 포함하므로, 보이는 박스/page 흐름 일부는 인접 제어코드뿐 아니라 추출 텍스트 내부에도 직접 들어 있다.
- 이 source 도 같은 r3=20 후보 렌더러 family 를 공유하지만, multiline payload 가 흔하기 때문에 runtime 동작은 entry8 과 실질적으로 다르다.
- 현재 삽입기는 Registry D entry 단위 packed relocation 을 지원하므로, 원문 byte 슬롯 길이에 맞추려고 번역을 과도하게 줄일 필요는 없다.
- runtime page-turn 동작은 시각 QA 로 확인하고, 화면 잘림이 보이면 의미 삭제보다 줄바꿈/문장 분할로 조정한다.

## 현재 해석

- 상위 우선순위 대사 runtime 작업은 더 이상 하나의 큰 미해결 덩어리가 아니다.
- 이제 shared r3=20 후보 family 위의 두 profile, 즉 entry8 의 단일 줄 counted script line 과 Registry D 의 multiline FC 구분 payload 로 좁혀졌다.
- 따라서 남은 blocker 는 record 경계 탐색이 아니라 시각적 page 확인이다.
