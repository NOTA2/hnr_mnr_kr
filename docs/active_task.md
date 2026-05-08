# Active Task

이 파일은 **매 세션마다 읽는 작은 작업 카드**다.

긴 배경은 링크로만 보관하고, 여기에는 다음 작업에 필요한 최소 사실만 둔다.

## 현재 목표

- `0x184A0C` effect/overlay row 의 `word1` / `word2` exact coordinate format 과 `word4` 의미를 더 좁힌다.

## 바로 필요한 사실

- `0x184A0C..0x184AD3` 은 `10 * 0x14` row, 각 row 는 `5 * u32` 다.
- `0x06CFB8` 은 `0x03002FFC == 0x10` 일 때 `0x03005FF8` 를 index 로 row 를 읽는다.
- row 는 `0x047A88` 에 `r0=word0`, `r1=word1`, `r2=word2`, `r3=word3`, `[sp]=word4`, `[sp+4]=0` 형태로 전달된다.
- `0x03005FF8` 은 effect 전용 state 가 아니라 world-map 선택/hover location index byte 로 보는 해석이 강하다.
- `0x03005FF8` direct writer 는 현재 `0x06A52E` 로 확인되며, hit-test loop index `0..9` 를 저장한다.
- `word0` 은 `0x0561F8` 을 통해 `*(0x03005014) + 0x90` byte 에 저장되고, `0x184420` hotspot/location lookup 의 hotspot id 와 row별로 정확히 매칭된다.
- 따라서 `word0` 은 **location 대표 hotspot/cell id** 로 보는 해석이 가장 강하다.
- `word1 low nibble` 은 `0x03CA68` 에 전달되고, 내부 `0x182530` 16-entry table 로 dispatch 된다.
- 위 table 의 entry `0..3` 은 `*(0x03001450) + 0x270/0x274` descriptor family 에서 halfword field `+0x02, +0x04, +0x06, +0x08` low 10-bit 를 읽는다.
- entry `4..15` 는 모두 같은 fallback accessor 로 모이며, descriptor field `+0x00` low 8-bit 를 base 로 읽은 뒤 `+ (nibble - 4)` 로 보정된다.
- 현재 `0x184A0C` row 에서 실제로 쓰인 `word1 low nibble` 값은 `0, 1, 4, 8, 14` 다.
- `0x047A88` 안에서 `word1` / `word2` stack slot 은 각각 한 번만 읽히며, 둘은 sign-extended 16-bit pair 로 `0x0587BC` 에 함께 전달된다.
- `0x0587BC` 는 두 축에 같은 scalar transform helper `0x075560` 을 적용한 뒤, active object/entry 의 `+0x08` / `+0x0C` 에 결과를 저장한다.
- 따라서 현재 가장 안전한 해석은 `word1` / `word2` 가 **raw positional pair (x/y 계열)** 라는 것이다. 다만 exact fixed-point scale 은 아직 미확정이다.
- `word4` 는 `0x047A88` 에서 다섯 번째 인자로 `[r7 + 0x1C]` 에서 한 번 읽히고, `0` 여부만 검사해 optional branch 를 켜거나 끈다.
- 따라서 현재 `word4` 는 연속 수치보다 **boolean / mode flag** 로 보는 해석이 가장 안전하다.
- `word3` 은 `0x02B96C` 의 세 번째 인자로 전달되고, 내부에서 `& 7` 로 제한된 뒤 `0x0383F8` 에 전달된다.
- `0x0383F8` 은 `0x1824F0` 의 8-entry Thumb function pointer table (`0x0377E0..0x037AB8`) 을 index 한다.
- 위 8개 accessor 는 공통 descriptor 의 halfword field `+0x04, +0x06, +0x08, +0x0A, +0x0C, +0x0E, +0x10, +0x12` 에서 각각 low 10-bit 값을 읽는다.
- 현재 `0x184A0C` row 에서 실제로 쓰인 `word3` 값은 대부분 `0`, row `2` 만 `6` 이다.

## 이번 작업에서 열 문서

- 필수: [effect_overlay_index_flow.md](/Users/user/test/analysis/effect_overlay_index_flow.md)
- 필요 시: [location_bundle_family.md](/Users/user/test/analysis/location_bundle_family.md)의 `Effect / Overlay Parameter Table` 절
- 큰 JSON [effect_overlay_index_refs.json](/Users/user/test/analysis/effect_overlay_index_refs.json) 은 통계 재검증이 필요할 때만 연다.

## 반복 금지

- `0x06B8B0` 시작부 `strb #0` 을 `0x03005FF8` 초기화로 보지 않는다. 이 write 는 `0x03005FE8` 쪽이다.
- `0x06A5B2` 의 `strb #2` 를 `0x03005FF8` write 로 보지 않는다. 이 write 는 `0x03006018 = 2` state 전환이다.
- literal pool 값만 보고 code entry 로 취급하지 않는다. 실제 `ldr` instruction 의 PC-relative target 을 확인한다.
- detached Thumb slice 를 `.org 0` 으로 디스어셈블했을 때는 BL target 을 그대로 ROM 주소로 읽지 않는다. 필요하면 `actual = slice_start + local_target` 으로 다시 맞춘다.

## 유용한 명령

```bash
python3 -m gba_kor_tool find-u32-refs "Hagane no Renkinjutsushi - Meisou no Rondo (Japan).gba" 0x03005ff8 --start 0x69000 --end 0x6e000 --preview 8
```

## 완료 조건

- `0x075560` 변환 전후를 기준으로 `word1` / `word2` 의 exact scale 또는 packing 규칙을 1개 이상 좁힌다.
- 가능하면 아직 해석되지 않은 `word4` 의 boolean / mode 역할을 1개 이상 확인한다.
- 관련 분석 문서와 [experiment_log.md](/Users/user/test/analysis/experiment_log.md) 에 짧게 기록한다.

## 참고 지도

- 전체 참고 문서 위치는 [reference_map.md](/Users/user/test/docs/reference_map.md) 를 필요할 때만 본다.
- 장기 대시보드는 [project_control_tower.md](/Users/user/test/docs/project_control_tower.md) 이지만 시작 시 읽지 않는다.
