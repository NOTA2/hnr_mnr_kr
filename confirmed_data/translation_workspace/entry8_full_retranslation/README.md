# Entry8 Full Retranslation

Entry8 전체 재번역 작업 패키지다.

## Rules

- `confirmed_repoint`: 현재 conservative build에서 repoint 허용된 레코드. 의미와 자연스러움을 우선한다.
- `fixed_slot`: 원본 counted 슬롯 안에 들어가야 하는 레코드. `max_korean_chars` 이내로 번역하되, 허용 길이를 최대한 활용해 의미와 말투를 보존한다.
- `candidate_repoint_keep_conservative`: 구조상 repoint 후보지만 아직 플레이 안정 검증이 충분하지 않다. 이번 번역에서는 `fixed_slot`처럼 다루며, 역시 허용 길이 안에서 의미를 최대한 살린다.
- 짧은 접두/감탄사는 source_text에서 뒤 문장과 같은 unit으로 묶었지만, ROM 적용용 records는 분리되어 있다.
- Entry8은 반각 공백/반각 쉼표가 깨질 수 있으므로 번역문은 일반 한국어로 쓰되 빌드 정규화가 전각 공백/구두점으로 맞춘다.

## Summary

- Records: `10417`
- Units: `4715`
- Batches: `10`
- Length policies: `{'fixed_slot': 7929, 'candidate_repoint_keep_conservative': 2428, 'confirmed_repoint': 60}`
