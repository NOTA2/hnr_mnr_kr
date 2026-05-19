# runtime 대사 세부 profile

- 마지막 갱신: `2026-05-18`

## Entry8

- `chain_heavy_singleline`: `42` clusters
- `chain_moderate_singleline`: `26` clusters
- `mostly_standalone_singleline`: `4` clusters

### Entry8 집중 cluster

- cluster `38` `central`: `records=786`, `runs=589`, `multi_runs=131`, `max_run=11`
- cluster `18` `east_city`: `records=523`, `runs=314`, `multi_runs=91`, `max_run=12`
- cluster `61` `military`: `records=483`, `runs=274`, `multi_runs=83`, `max_run=15`
- cluster `55` `east_city`: `records=438`, `runs=342`, `multi_runs=80`, `max_run=5`
- cluster `70` `military`: `records=257`, `runs=113`, `multi_runs=46`, `max_run=12`
- cluster `26` `central`: `records=274`, `runs=167`, `multi_runs=45`, `max_run=37`
- cluster `20` `central`: `records=325`, `runs=138`, `multi_runs=44`, `max_run=24`
- cluster `62` `central`: `records=291`, `runs=191`, `multi_runs=42`, `max_run=26`

### Entry8 해석

- Entry8 record 는 여전히 단일 줄 counted payload 이지만, runtime 흐름이 순수하게 one-record-per-box 는 아니다.
- 많은 cluster 가 multi-record 연속 상태 run 을 포함하므로, 남은 runtime 질문은 multiline 해독이 아니라 짧은 record 들이 어떻게 이어지는가이다.
- 번역은 chain-heavy cluster 를 외부 script 로 이어지는 대사 구간으로 보고, record 단위 줄을 짧게 유지한다.

## Registry D

- `single_line_short`: `runs=62`, `record_coverage=80`
- `short_or_one_break`: `runs=87`, `record_coverage=94`
- `mid_multiline`: `runs=50`, `record_coverage=52`
- `long_multiline`: `runs=8`, `record_coverage=18`

### Registry D 해석

- Registry D 는 하나의 거대한 multiline family 가 아니라, 짧은 단일 줄 전투/튜토리얼 대사, 한 번만 끊기는 설명 줄, 중간 길이 multiline 설명, 소수의 장문 manual/tutorial 계층으로 나뉜다.
- Registry D 는 packed relocation 으로 원문 byte 슬롯보다 긴 번역도 적용 가능하므로, 남은 runtime 위험은 길이 수용 여부보다 가장 긴 multiline 계층이 어떻게 페이지를 넘기는가라는 질문으로 줄어든다.
- 번역은 자연스러운 의미 보존과 기존 개행 보존을 우선하고, runtime page-turn QA 에서 잘림이 보이면 줄바꿈/문장 분할로 조정한다.

## 현재 해석

- Entry8 의 남은 불확실성은 source 전체가 아니라 chain-heavy 단일 줄 cluster 에 집중돼 있다.
- Registry D 의 남은 불확실성은 source 전체나 원문 슬롯 길이가 아니라, 매우 작은 장문 multiline 계층과 page-turn 동작에 집중돼 있다.
