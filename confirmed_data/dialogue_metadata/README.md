# Dialogue Metadata

이 폴더는 **화자 이름 추정**이 아니라, 대사 직전 제어군에서 뽑은 **객관적 state token** 과 **state run** 을 담는다.

현재 원칙:

- `dialogue_state_token` 은 confirmed speaker ID 가 아니다.
- 같은 token 을 공유하는 줄은 같은 active portrait/state 후보로 묶어 볼 수 있다.
- `state run` 은 연속된 동일 token 묶음이며, 번역 시 같은 톤/호흡을 유지할 후보군으로 본다.

## Files

- `entry8_dialogue_state_index.json`: Registry A entry 8 script-line state tokens
- `registry_d_dialogue_state_index.json`: Registry D FC-script state tokens
- `entry8_dialogue_state_runs.json`: Entry 8 cluster-local contiguous state runs
- `registry_d_dialogue_state_runs.json`: Registry D contiguous state runs

- Entry8 clusters with runs: `73`
- Registry D total runs: `207`

## Translation use

- 같은 run 안의 줄들은 우선 같은 화자 상태 후보로 보고 말투 일관성을 체크한다.
- run 이 바뀌면 speaker/state/portrait 전환 후보로 본다.
- 확정 화자명은 별도 근거가 생기기 전까지 추가하지 않는다.
