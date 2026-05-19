# runtime pageflow 집중 대상

- 마지막 갱신: `2026-05-18`

## Entry8 집중 대상

- focus cluster 수: `12`

- cluster `38` `central` (`records=786`, `runs=589`, `high_chain_density`)
- cluster `18` `east_city` (`records=523`, `runs=314`, `high_chain_density`)
- cluster `61` `military` (`records=483`, `runs=274`, `high_chain_density`)
- cluster `55` `east_city` (`records=438`, `runs=342`, `moderate_chain_density`)
- cluster `20` `central` (`records=325`, `runs=138`, `high_chain_density`)
- cluster `41` `east_city` (`records=306`, `runs=176`, `high_chain_density`)
- cluster `62` `central` (`records=291`, `runs=191`, `high_chain_density`)
- cluster `26` `central` (`records=274`, `runs=167`, `high_chain_density`)
- cluster `11` `central` (`records=258`, `runs=89`, `high_chain_density`)
- cluster `70` `military` (`records=257`, `runs=113`, `high_chain_density`)

### Entry8 해석

- Entry8 page-flow 작업은 multi-record run 이 많은 chain-heavy cluster 를 먼저 봐야 한다. 그 구간이 외부 script 연쇄 압력이 가장 높기 때문이다.
- null-token multi-run 비중이 큰 cluster 는 독립 one-record 박스보다 script-driven chaining 후보일 가능성이 높다.

## Registry D 집중 대상

- 장문 multiline focus 수: `8`

- run `11` token `pre98:3A` (`records=1`, `chars=77`, `newlines=5`)
- run `15` token `pre98:3B` (`records=1`, `chars=66`, `newlines=5`)
- run `22` token `pre98:3A` (`records=1`, `chars=88`, `newlines=6`)
- run `24` token `pre98:3A` (`records=1`, `chars=82`, `newlines=6`)
- run `25` token `pre98:3B` (`records=2`, `chars=56`, `newlines=4`)
- run `113` token `pre98:4B` (`records=1`, `chars=52`, `newlines=4`)
- run `114` token `pre98:07` (`records=1`, `chars=49`, `newlines=4`)
- run `140` token `None` (`records=10`, `chars=90`, `newlines=6`)

### Registry D 해석

- Registry D page-flow 작업은 아주 작은 장문 multiline 계층부터 먼저 보면 된다.
- 나머지 Registry D 는 packed relocation 으로 길이 적용은 가능하므로, 자연스러운 번역을 진행하고 개행/page-flow 는 QA 로 조정한다.

## 현재 해석

- 이 파일은 일반 family/subprofile 보고서보다 한 단계 더 실무적인 다음 작업용 레이어다.
- 어떤 entry8 cluster 와 Registry D run 을 먼저 runtime/page QA 해야 하는지 정할 때 쓴다.
