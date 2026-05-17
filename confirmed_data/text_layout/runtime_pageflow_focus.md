# Runtime Pageflow Focus

- last_updated: `2026-05-17`

## Entry8 Focus

- focus_cluster_count: `12`

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

### Entry8 Reading

- Entry8 page-flow work should focus first on chain-heavy clusters with many multi-record runs, because that is where external sequencing pressure is highest.
- Clusters dominated by null-token multi-runs are especially strong candidates for script-driven chaining rather than self-contained one-record boxes.

## Registry D Focus

- long_multiline_focus_count: `8`

- run `11` token `pre98:3A` (`records=1`, `chars=77`, `newlines=5`)
- run `15` token `pre98:3B` (`records=1`, `chars=66`, `newlines=5`)
- run `22` token `pre98:3A` (`records=1`, `chars=88`, `newlines=6`)
- run `24` token `pre98:3A` (`records=1`, `chars=82`, `newlines=6`)
- run `25` token `pre98:3B` (`records=2`, `chars=56`, `newlines=4`)
- run `113` token `pre98:4B` (`records=1`, `chars=52`, `newlines=4`)
- run `114` token `pre98:07` (`records=1`, `chars=49`, `newlines=4`)
- run `140` token `None` (`records=10`, `chars=90`, `newlines=6`)

### Registry D Reading

- Registry D page-flow work should focus first on the very small long-multiline tier.
- The rest of Registry D is already narrow enough that translation can proceed conservatively with newline preservation.

## Operational Reading

- This file is the practical next-step layer above the general family/subprofile reports.
- Use it to decide which concrete entry8 clusters and Registry D runs deserve runtime/page QA first.
