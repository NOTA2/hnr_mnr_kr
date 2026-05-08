# Active Task

이 파일은 **매 세션마다 읽는 작은 작업 카드**다.

긴 배경은 링크로만 보관하고, 여기에는 다음 작업에 필요한 최소 사실만 둔다.

## 현재 목표

- tracked slot allocator / promotion 구조를 더 좁혀 `0x03005284 -> 0x482/0x484 -> 0x33C/+0x33E` 승격 파이프라인을 연결한다.

## 바로 필요한 사실

- `0x184A0C..0x184AD3` 은 `10 * 0x14` row, 각 row 는 `5 * u32` 다.
- `0x06CFB8` 은 `0x03002FFC == 0x10` 일 때 `0x03005FF8` 를 index 로 row 를 읽는다.
- row 는 `0x047A88` 에 `r0=word0`, `r1=word1`, `r2=word2`, `r3=word3`, `[sp]=word4`, `[sp+4]=0` 형태로 전달된다.
- `0x03005FF8` 은 effect 전용 state 가 아니라 world-map 선택/hover location index byte 로 보는 해석이 강하다.
- `0x03005FF8` direct writer 는 현재 `0x06A52E` 로 확인되며, hit-test loop index `0..9` 를 저장한다.
- `word0` 은 `0x0561F8` 을 통해 `*(0x03005014) + 0x90` byte 에 저장되고, `0x184420` hotspot/location lookup 의 hotspot id 와 row별로 정확히 매칭된다.
- 따라서 `word0` 은 **location 대표 hotspot/cell id** 로 보는 해석이 가장 강하다.
- `0x047A88` 안에서 `word1` / `word2` stack slot 은 각각 한 번만 읽히며, 둘은 sign-extended 16-bit pair 로 `0x0587BC` 에 함께 전달된다.
- `0x0587BC` 는 두 축에 같은 scalar transform helper `0x075560` 을 적용한 뒤, active object/entry 의 `+0x08` / `+0x0C` 에 결과를 저장한다.
- `0x075560` 은 내부적으로 signed int 를 IEEE-754 single float 비트패턴으로 포장한다.
- 따라서 현재 가장 안전한 해석은 `word1` / `word2` 가 **직접적인 signed integer 좌표쌍** 이고, runtime object 에는 float 형태로 저장된다는 것이다.
- `0x02B96C -> 0x03CA68` dispatch table 자체는 존재하지만, `0x047A88` effect row 경로의 실제 call site (`0x047DEE`, `0x047E26`) 에서는 두 번째 인자 `r1` 이 `0` 으로 고정된다.
- 따라서 이전의 "`word1 low nibble` 이 이 dispatch 를 고른다"는 해석은 **effect row 경로에 대해서는 틀렸을 가능성이 높다**.
- `word4` 는 `0x047A88` 에서 다섯 번째 인자로 `[r7 + 0x1C]` 에서 한 번 읽히고, `0` 여부만 검사해 optional branch 를 켜거나 끈다.
- `word4 != 0` 이면 `0x03001450 + 0x33C/+0x33E` 의 두 halfword 를 읽고, `+8` 보정 후 실제 slot `8..23` 과 직접 비교한다.
- 따라서 `+0x33C/+0x33E` 는 적어도 **raw tracked slot id 2개** 로 보는 해석이 강하다.
- 같은 side-path 는 tracked slot 둘을 제외한 slot `8..23` 의 세 병렬 block (`+0x0574`, `+0x0AF4`, `+0x0BF4`) 을 `0x075D4C` 로 지운다.
- `0x044320(slot, flag)` 는 `+0x0574 + (slot + 8) * 0x34` record 의 상위 플래그를 clear/set 하고, `0x0443B4(slot)` 는 같은 플래그가 살아 있는지 검사하는 helper 로 보는 해석이 강하다.
- `0x03D6F0` 는 `+0x33E` 와 `+0x33C` 를 함께 읽어 `0x0443B4` / `0x044320` 를 호출하는 정합성 보조 루틴으로 보인다.
- 여기서 첫 비교는 `cmp` 가 아니라 `cmn` 이므로, 실제 특수값은 `+0x33E == -1` sentinel 이다. 즉 두 번째 tracked slot 은 optional field 일 가능성이 높다.
- `0x0443F8` 는 global `0x0300503C` 를 slot iterator 로 써서 후보 slot `0..15` 를 훑고, 현재 tracked slot `0x33C/+0x33E` 와 겹치는 후보는 건너뛴다.
- 이 함수는 `0x03005240` 의 `16 * 4-byte` per-slot state table 을 갱신하면서 후보를 검사하고, 최종 선택 결과를 `0x03005284` 에 `slot id` 또는 `-1` sentinel 로 남긴다.
- `0x0412D0..0x04137A` 초기화 경로는 `0x03005284 = -1` 을 넣고, `0x03005240[16]` 각 entry 의 `+0` / `+2` halfword 를 모두 지운다.
- 현재 가장 안전한 `0x03005240` entry 해석은 `u16 in_use_flag`, `u16 edge_mask` 다.
- `0x044AE0` 는 global bounds 비교로 `1/2/4/8` bit 를 조합한 edge/boundary mask 를 계산하고, `0x0446E2..0x04473C` 는 이 값을 `0x03005240[candidate].+2` 에 저장한다.
- 현재 확인된 `0x0443F8` direct caller 는 `0x059034` 하나이며, 이 caller 는 성공 시 반환 slot id 를 받은 뒤 `slot + 0x5A` runtime id 로 변환해 후속 object 구축에 쓴다.
- `0x045B98` 계열과 `0x047A28` 은 `0x03005284` 를 읽는 consumer 라서, `0x03005284` 는 일회성 scratch 가 아니라 **selected candidate slot buffer** 로 보는 해석이 강하다.
- `0x045D6C/0x045D94` 와 `0x045EEE/0x045F16` 은 `0x03005284` 를 읽어 `0x482 = raw slot`, `0x484 = 0x0478B8(slot)` derived companion id 를 staging 한 뒤 `0x0458DC` 를 호출한다.
- `0x0478B8(slot)` 은 slot record `0x714[slot]` 와 bundle `0x0CD4[slot]` 의 좌표/방향 정보를 섞어 companion id 를 만든다. 필요하면 `0x02C1AC(slot, derived_dir)` fallback 으로 보정한다.
- `0x04B7F0` 는 `0x482/0x484` pending pair 와 기존 `0x33E` tracked slot 을 함께 읽는 consumer 로 보인다.
- `0x051022` 는 현재 확인된 `0x33E` direct clear writer 이며, 특정 state flag 조건에서 `0x33E = -1` sentinel 을 기록한다.
- 따라서 현재 `word4` 는 연속 수치보다 **overlay slot maintenance mode flag** 로 보는 해석이 가장 안전하다.
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
- `cmp` / `cmn` 같은 register ALU opcode 는 즉시값 비교처럼 보일 수 있으니, `0x4000` 계열 Thumb ALU op 를 따로 확인한다.
- `0x33C` 처럼 literal hit 가 안 보이는 field 는 `0xCF << 2` 같은 계산식으로 접근할 수 있다. literal scan 결과만으로 "writer/read가 없다"고 결론내리지 않는다.

## 유용한 명령

```bash
python3 -m gba_kor_tool find-u32-refs "Hagane no Renkinjutsushi - Meisou no Rondo (Japan).gba" 0x03005ff8 --start 0x69000 --end 0x6e000 --preview 8
```

## 완료 조건

- `0x33C/+0x33E` tracked field writer 또는 promotion path 를 1개 이상 더 잡는다.
- `0x0443F8 -> 0x03005284 -> 0x482/0x484 -> consumer` 흐름을 구조 설명 수준으로 굳힌다.
- 관련 분석 문서와 [experiment_log.md](/Users/user/test/analysis/experiment_log.md) 에 짧게 기록한다.

## 참고 지도

- 전체 참고 문서 위치는 [reference_map.md](/Users/user/test/docs/reference_map.md) 를 필요할 때만 본다.
- 장기 대시보드는 [project_control_tower.md](/Users/user/test/docs/project_control_tower.md) 이지만 시작 시 읽지 않는다.
