# Dialogue Metadata

이 폴더는 **화자 이름 추정**이 아니라, 대사 직전 제어군에서 뽑은 **객관적 state token** 을 담는다.

현재 원칙:

- `dialogue_state_token` 은 confirmed speaker ID 가 아니다.
- 같은 token 을 공유하는 줄은 같은 active portrait/state 후보로 묶어 볼 수 있다.
- 번역팀에서 화자 정보가 필요할 때도, 우선은 `candidate / unresolved` 레이어로 다룬다.

## Files

- `entry8_dialogue_state_index.json`: Registry A entry 8 script-line state tokens
- `registry_d_dialogue_state_index.json`: Registry D FC-script state tokens

## Top Entry8 tokens

- `1bff:0100`: 105 lines
- `1bff:0B00`: 102 lines
- `1bff:0280`: 73 lines
- `1bff:0180`: 72 lines
- `2bff:0800`: 67 lines
- `1bff:0900`: 66 lines
- `1bff:0200`: 63 lines
- `1bff:0B80`: 63 lines
- `1bff:0980`: 54 lines
- `1bff:1280`: 53 lines

## Top Registry D tokens

- `pre98:3A`: 25 lines
- `pre98:3C`: 23 lines
- `pre98:3B`: 21 lines
- `pre98:0B`: 15 lines
- `pre98:07`: 8 lines
- `pre98:25`: 6 lines
- `pre98:6A`: 6 lines
- `pre98:1A`: 5 lines
- `pre98:13`: 4 lines
- `pre98:03`: 4 lines

