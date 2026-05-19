# Text Category Capability Matrix

Last updated: 2026-05-20

이 문서는 번역 카테고리/source_group 별로 반각 사용, 전각 강제, repoint/relocation 가능성을 정리한 작업 기준이다. 실제 번역문은 이 문서 생성 과정에서 수정하지 않았다.

## Summary

| category | source_group | halfwidth policy | expansion policy | evidence |
|---|---|---|---|---|
| 대사 Registry D | `registry_d_fc_script_texts` | 반각 사용 가능 | `packed_repoint_available` / apply report `packed_repointed: 244` | 244건 중 241건에 반각 공백/숫자/기호 사용 |
| 코어 UI | `system_messages` | 기존 반각 유지 | 대부분 direct repoint, 일부 in-place | 10건 중 7건에 반각 사용, apply report `repointed: 1`, `in_place: 9` |
| 코어 UI | `ui_skill_texts` | 기존 반각 유지 | direct repoint 가능 | 25건 중 19건에 반각 사용, apply report `repointed: 6`, `in_place: 19` |
| 코어 UI | `registry_a_map_labels` | 기존 반각 유지 | in-place / 일부 fixed | 48건 전부 반각 숫자/콜론 사용 |
| 코어 UI | `location_texts` | 기존 반각 유지 | 일부 direct repoint, 일부 in-place/fixed | 10건 중 3건에 반각 공백 사용 |
| 코어 UI | `save_menu_texts` | 전각 우선 | counted fixed/in-place | 12건 반각 사용 없음, `01 FF <char_count>` 계열 |
| 코어 UI | `choice_yes_no_texts` | 전각 우선 | counted fixed/in-place | 16건 반각 사용 없음, 선택지 spacing-sensitive |
| 게임 용어 | `item_texts` | 기존 반각 유지 | direct repoint 가능 | 49건 중 38건에 반각 사용, apply report `repointed: 14`, `in_place: 35` |
| 게임 용어 | `battle_texts` | 기존 반각 유지 | in-place slack / fixed | 104건 중 37건에 반각 사용 |
| 게임 용어 | `ability_texts` | 기존 반각 유지 | in-place slack / fixed | 413건 중 228건에 반각 사용 |
| 게임 용어 | `material_texts` | 기존 반각 유지 | in-place slack / fixed | 44건 전부 반각 공백 또는 숫자 사용 |
| 게임 용어 | `registry_a_entry12_texts` | 기존 반각 유지 | in-place slack / fixed | 22건 중 19건에 반각 사용 |
| 대사 Entry8 | `registry_a_entry8_prefixed_texts` | 전각 우선/반각 금지에 가깝게 운용 | 메인 빌드에서는 structural segment repoint 금지, fixed/in-place만 허용 | segment repoint 활성화 시 지역 전환 후 배경/스프라이트/조작 깨짐 재현, 비활성화 빌드 정상 진행 확인 |
| 이벤트 연출 텍스트 | `inline_event_texts` | 전각 우선/반각 금지에 가깝게 운용 | fixed in-place | 41건 중 반각 흔적 1건, 반각 공백 테스트 실패 |
| 오프닝/인트로 | `startup_intro_texts` | 전각 우선 | fixed slot | 반각 숫자/기호 렌더링 불안정 family |
| 크레딧 | `credits_texts` | 전각 공백 패딩 보존, 기존 반각 기호는 보수적으로 유지 | direct repoint 가능하지만 spacing-sensitive | 전각 padding 이 레이아웃 힌트 역할 |

## Operating Rules

- `Registry D`, 코어 UI, 게임 용어에서 이미 안정적으로 쓰인 반각 공백/숫자/기호는 번역문에서 임의로 전각화하지 않는다.
- `Entry8`, `inline_event_texts`, `startup_intro_texts`, `save_menu_texts`, `choice_yes_no_texts` 는 전각 공백/숫자/기호를 우선한다.
- 원문 특수기호는 일본어/한자 자체가 아닌 한 보존을 우선한다. 단, 전각 우선 계열에서 원문이 반각 기호라면 같은 의미의 전각 기호로 보존한다.
- `Entry8` 및 이벤트 연출 텍스트에서는 특수기호/문장부호 바로 뒤에 공백을 추가하지 않는다. 게임 화면에서는 기호 자체의 폭이 여백처럼 보이므로 `、　`, `。　`, `？　`, `！　`, `…　`, `・　` 같은 형태를 만들지 않는다.
- 인명/고유명사 내부의 일본식 중점 `・`는 한국어 번역에서 띄어쓰기로 바꾼다. `・・・` 말줄임표와 `１・２` 같은 숫자 사이의 `・`는 보존 대상이다. 2026-05-19 현재 최종 review ROM 기준 `・` 포함 레코드는 4건이며, 이름/고유명사 내부 `・`는 0건이다.
- repoint 가능성은 반각 가능성과 별개다. `Registry D` 는 packed relocation 가능, `item_texts`/`ui_skill_texts`/대부분 `system_messages` 는 direct repoint 가능, `battle_texts`/`ability_texts`/`material_texts` 는 아직 packed bank relocation 이 없다.
- `Entry8` structural segment repoint 는 현재 메인라인 기능이 아니라 실험 기능으로만 취급한다. 2026-05-20 안정 빌드 기준 `entry8_segment_repointed: 0건`이어야 하며, 번역은 원본 counted record/slot 안에 들어가는 경우만 적용한다.
- `Entry8` 구조 실험을 재개할 때는 반드시 별도 테스트 ROM/별도 환경변수로만 켜고, 지역 전환/맵 로딩/자동 이동 이벤트를 포함한 runtime 검증을 통과하기 전까지 review ROM에 반영하지 않는다.
