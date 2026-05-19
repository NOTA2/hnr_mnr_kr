# Entry8 Runtime Stability Notes

- Last updated: `2026-05-20`
- Main review ROM: `patched_roms/current_review/hnr_localization_review.gba`

## 결론

현재 안정 빌드에서는 Entry8 structural segment repoint/relocation 을 사용하지 않는다.

Entry8 에는 segment table 과 counted text record 가 있어 구조적으로 repoint 가능성이 보이지만, 지금 구현으로 segment 를 재배치하면 지역 전환 뒤 배경, 스프라이트, 조작 상태가 깨지는 런타임 문제가 재현됐다. 따라서 메인라인에서는 Entry8 을 Registry D처럼 자유롭게 긴 문장으로 확장하지 않는다.

## 재현됐던 증상

- 특정 지역 전환 뒤 플레이어 조작이 멈춤.
- 배경이 깨지거나 전혀 다른 캐릭터로 보임.
- 대화창은 뜨지만 지역명/맵 상태가 정상 표시되지 않음.
- 일본판 save state 를 패치 ROM에 가져와도 같은 지점에서 그래픽/진행 문제가 발생.
- Entry8 segment repoint 를 끈 빌드에서는 같은 진행이 정상화됨.

## 현재 빌드 정책

- `ENTRY8_ALLOW_STRUCTURAL_REPOINT` 기본값은 `0`.
- `ENTRY8_VARIABLE_OFFSETS` 기본값은 빈 값.
- `ENTRY8_PATCH_OPCODE_OFFSETS` 기본값은 `0`.
- Entry8 은 원본 record/slot 길이를 보존하는 in-place 적용만 메인라인에서 허용한다.
- Entry8 구조 재배치는 별도 실험 ROM에서만 켠다.

## 현재 안정 빌드의 Entry8 적용 결과

- `entry8_segment_repointed: 0건`
- `entry8_in_place_length_preserved: 10102건`
- `entry8_segment0_in_place_length_preserved: 241건`
- `entry8_boundary_crossing_in_place_length_preserved: 21건`

이 값은 Entry8 번역을 포기했다는 뜻이 아니다. 현재 번역본 중 실제 ROM에 적용되는 Entry8 항목들은 원본 counted record/slot 안에 들어가며, segment 재배치 없이 안정적으로 들어간다는 뜻이다.

## 액션 이름 의미

- `entry8_in_place_length_preserved`: 일반 Entry8 counted text record 를 원본 byte 범위 안에서 교체했고 전체 길이를 보존했다.
- `entry8_segment0_in_place_length_preserved`: segment 0에 속한 Entry8 record 를 특수 취급하되 원본 길이 안에서 보존 교체했다.
- `entry8_boundary_crossing_in_place_length_preserved`: record 범위가 segment 경계와 민감하게 맞닿아 있어 재배치하지 않고 원본 범위 안에서 보존 교체했다.
- `entry8_segment_repointed`: Entry8 segment 를 새 위치로 옮겨 길이를 바꾸는 실험 경로다. 현재 메인 빌드에서는 0건이어야 한다.

## 나중에 다시 시도할 조건

Entry8 structural repoint 를 다시 열려면 다음 조건을 모두 만족해야 한다.

1. segment table 외에 이벤트 명령, local offset, opcode operand, 맵/캐릭터 로딩 참조까지 추적한다.
2. 지역 전환 직전 save state 로 원본 ROM과 패치 ROM을 비교한다.
3. mGBA runtime probe 로 BG/OAM/IOREG/VRAM 상태를 비교한다.
4. 오프닝, 리올, 센트럴, 군부, 병원, 은행, 고양이 퀘스트 등 서로 다른 cluster 계열을 통과 검증한다.
5. 안정성이 확인되기 전까지 `hnr_localization_review.gba`에는 반영하지 않는다.

## 관련 안전장치

- map label 계열은 fixed map header record 안에 있어 `0xFF` 패딩을 쓰면 맵 로딩이 깨질 수 있다. 이 계열은 `0x00` padding 을 사용한다.
- `.ss1`/`.ss2` mGBA savestate 는 PNG header 로 시작해도 유효한 savestate 일 수 있다. 비교용으로는 문제가 발생한 뒤의 savestate 보다 문제 직전 savestate 가 더 유용하다.
