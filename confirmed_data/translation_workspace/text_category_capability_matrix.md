# Text Category Capability Matrix

Last updated: 2026-06-10

이 문서는 번역 카테고리/source_group 별로 반각 사용, 전각 강제, repoint/relocation 가능성을 정리한 작업 기준이다. 실제 번역문은 이 문서 생성 과정에서 수정하지 않았다.

2026-06-10 기준으로 보이는 숫자와 숫자 주변 슬래시는 원문 폭을 따른다. 원문이 `1/5`, `マッチョ1` 처럼 반각이면 번역도 반각이고, 원문이 `１／５`, `体力を５０` 처럼 전각이면 번역도 전각이다. 아래 `halfwidth policy` 의 반각 허용/보존은 공백과 일부 기호에 대한 의미다.

## Summary

| category | source_group | halfwidth policy | expansion policy | evidence |
|---|---|---|---|---|
| 대사 Registry D | `registry_d_fc_script_texts` | 반각 사용 가능 | `packed_repoint_available` / apply report `packed_repointed: 244` | 244건 중 241건에 반각 공백/숫자/기호 사용 |
| 코어 UI | `system_messages` | 기존 반각 유지 | 대부분 direct repoint, 일부 in-place | 10건 중 7건에 반각 사용, apply report `repointed: 1`, `in_place: 9` |
| 코어 UI | `ui_skill_texts` | 기존 반각 유지 | direct repoint 가능 | 25건 중 19건에 반각 사용, apply report `repointed: 6`, `in_place: 19` |
| 코어 UI | `registry_a_map_labels` | 기존 반각 유지, 숫자는 원문 폭 기준 | in-place / 일부 fixed | 방/맵 번호는 원문 내 반각/전각 숫자 폭이 섞일 수 있으므로 숫자 묶음별로 원문 폭을 따른다 |
| 코어 UI | `location_texts` | 앞/뒤 공백 제거, 중간 공백만 전각 변환, ROM 적용 시 한글 폭 기준 라벨 offset 메타데이터 보정 | in-place/fixed + metadata patch | 월드맵 위치명은 record+0x28 라벨/스크롤 offset 이 원문 폭 기준으로 들어 있으므로 번역 폭으로 재계산. `text_layout_metadata_candidate_audit` strict 후보는 현재 이 그룹뿐 |
| 코어 UI | `save_menu_texts` | 전각 우선 | counted fixed/in-place | 12건 반각 사용 없음, `01 FF <char_count>` 계열 |
| 코어 UI | `choice_yes_no_texts` | 전각 우선 | counted fixed/in-place | 16건 반각 사용 없음, 선택지 spacing-sensitive |
| 게임 용어 | `item_texts` | 기존 반각 유지 | direct repoint 가능 | 49건 중 38건에 반각 사용, apply report `repointed: 14`, `in_place: 35` |
| 게임 용어 | `battle_texts` | 일반 반각은 허용하되 0x0B 앞 이름 필드는 자동 패딩 우선 | in-place slack / fixed | 0x0B 이름/설명 구분자는 GUI 구조 편집으로 앞/뒤 필드를 분리해 편집 |
| 게임 용어 | `ability_texts` | 일반 반각은 허용하되 0x0B 앞 이름 필드는 자동 패딩 우선 | in-place slack / fixed | ALCHEMY 패널 이름 필드에서 긴 1줄 문구가 끝 글자 클리핑을 유발할 수 있음. GUI 구조 편집으로 앞/뒤 필드를 분리해 편집 |
| 게임 용어 | `material_texts` | 일반 반각은 허용하되 0x0B 앞 이름 필드는 자동 패딩 우선 | in-place slack / fixed | 0x0B 이름/설명 구분자는 GUI 구조 편집으로 앞/뒤 필드를 분리해 편집 |
| 게임 용어 | `registry_a_entry12_texts` | 기존 반각 유지 | in-place slack / fixed | 22건 중 19건에 반각 사용 |
| 대사 Entry8 | `registry_a_entry8_prefixed_texts` | 전각 우선/반각 금지에 가깝게 운용 | 메인 빌드에서는 structural segment repoint 금지, fixed/in-place만 허용 | segment repoint 활성화 시 지역 전환 후 배경/스프라이트/조작 깨짐 재현, 비활성화 빌드 정상 진행 확인 |
| 이벤트 연출 텍스트 | `inline_event_texts` | 전각 우선/반각 금지에 가깝게 운용 | fixed in-place | 41건 중 반각 흔적 1건, 반각 공백 테스트 실패 |
| 오프닝/인트로 | `startup_intro_texts` | 전각 우선 | fixed slot | 반각 숫자/기호 렌더링 불안정 family |
| 크레딧 | `credits_texts` | 전각 공백 패딩 보존, 기존 반각 기호는 보수적으로 유지 | direct repoint 가능하지만 spacing-sensitive | 전각 padding 이 레이아웃 힌트 역할 |

## Operating Rules

- `Registry D`, 코어 UI, 게임 용어에서 이미 안정적으로 쓰인 반각 공백/일부 기호는 번역문에서 임의로 전각화하지 않는다. 숫자와 숫자 주변 슬래시는 source_group 기본값보다 원문 폭을 먼저 따른다.
- `ability_texts`, `battle_texts`, `material_texts`처럼 원문에 0x0B 이름/설명 구분자가 있는 게임 용어는 0x0B 앞 이름 필드를 긴 문장으로 채우지 않는다. `거대 손을\\x0B연성해 공격`처럼 이름/대상은 앞 필드에 두고, 동작 설명은 뒤 필드로 넘긴다. 이름 필드 패딩은 빌드 정규화가 원문 폭 기준으로 전각/반각 공백을 자동 합성하므로 수동 공백으로 맞추지 않는다. GUI에서는 구조 편집 패널로 앞/뒤 필드를 분리해 수정한다.
- `location_texts` 월드맵 위치명은 GUI/데이터셋과 ROM 문자열 양쪽 모두 앞/뒤 정렬 공백을 넣지 않는다. 저장 시 앞/뒤 공백은 제거하고 중간 공백만 전각 공백으로 변환한다. ROM 적용 단계에서는 문자열에 공백을 추가하지 않고, 각 location record 의 `name_offset + 0x14` (`record+0x28`) 라벨/스크롤 offset 값을 한글 표시 폭 기준으로 재계산한다.
- `location_texts` 같은 별도 표시폭 메타데이터 구조는 `scripts/audit_text_layout_metadata_candidates.py` 로 감사를 먼저 통과해야 적용 대상에 추가한다. 2026-06-04 감사 기준 strict 후보는 `location_texts` 하나이며, suspicious 후보는 없다. 새 후보가 확인되면 `scripts/build_localization_review_rom.py` 의 `TEXT_LAYOUT_METADATA_PATCH_RULES` 에 source_group별 규칙을 추가한다.
- `Entry8`, `inline_event_texts`, `startup_intro_texts`, `save_menu_texts`, `choice_yes_no_texts` 는 전각 공백/기호를 우선하되, 숫자와 숫자 주변 슬래시는 원문 폭을 먼저 따른다.
- 원문 특수기호는 일본어/한자 자체가 아닌 한 보존을 우선한다. 단, 전각 우선 계열에서 원문이 반각 기호라면 같은 의미의 전각 기호로 보존한다.
- `Entry8` 및 이벤트 연출 텍스트에서는 특수기호/문장부호 바로 뒤에 공백을 추가하지 않는다. 게임 화면에서는 기호 자체의 폭이 여백처럼 보이므로 `、　`, `。　`, `？　`, `！　`, `…　`, `・　` 같은 형태를 만들지 않는다.
- 인명/고유명사 내부의 일본식 중점 `・`는 한국어 번역에서 띄어쓰기로 바꾼다. `・・・` 말줄임표와 `１・２` 같은 숫자 사이의 `・`는 보존 대상이다. 2026-05-19 현재 최종 review ROM 기준 `・` 포함 레코드는 4건이며, 이름/고유명사 내부 `・`는 0건이다.
- repoint 가능성은 반각 가능성과 별개다. `Registry D` 는 packed relocation 가능, `item_texts`/`ui_skill_texts`/대부분 `system_messages` 는 direct repoint 가능, `battle_texts`/`ability_texts`/`material_texts` 는 아직 packed bank relocation 이 없다.
- `Entry8` structural segment repoint 는 현재 메인라인 기능이 아니라 실험 기능으로만 취급한다. 2026-05-20 안정 빌드 기준 `entry8_segment_repointed: 0건`이어야 하며, 번역은 원본 counted record/slot 안에 들어가는 경우만 적용한다.
- `Entry8` 구조 실험을 재개할 때는 반드시 별도 테스트 ROM/별도 환경변수로만 켜고, 지역 전환/맵 로딩/자동 이동 이벤트를 포함한 runtime 검증을 통과하기 전까지 review ROM에 반영하지 않는다.
