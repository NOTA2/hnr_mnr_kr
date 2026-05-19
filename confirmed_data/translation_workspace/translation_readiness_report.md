# 번역 준비도 보고서

- 마지막 갱신: `2026-05-18`

## 작업 세트

- `translation_workset_opening_intro` (`ready_with_fixed_slot_rules`)
  모든 record 가 확정된 startup_intro_fixed_slots family 에 속한다.
  게임 시작 직후 오프닝 고정 카드 4줄이므로 정확한 byte 길이 슬롯과 append_terminator=false 를 사용한다.
- `translation_workset_core_ui` (`ready_with_source_specific_rules`)
  혼합 workset 이므로 source_group 별 family 규칙을 먼저 적용한다.
  system_messages/save_menu 는 runtime 불확실성이 조금 남아 있지만 record 구조는 이미 실사용 가능하다.
- `translation_workset_gameplay_terms` (`ready_conservative`)
  item/ui/battle/ability/material/entry12 family 는 record 구조가 객관적으로 확인됐고 정식 workset 에 전량 편입됐다.
  이 계열은 아직 packed bank relocation 이 없으므로 expansion audit 을 기준으로 한다. 슬롯 여유나 direct repoint 가 있으면 자연스러운 표현을 우선하고, 없으면 byte 한계를 지킨다. 0x0B 는 논리 구분자로 보존하고, 이름 필드 padding 은 번역자가 직접 맞추는 대신 빌드 도구가 원문 폭 기준으로 복원한다. 0x0B 앞 이름 필드에 여백이 있으면 수동 공백이 아니라 조사/목적어/동사 조각 같은 실제 글자로 활용한다. 2줄 설명창은 윗줄을 먼저 채우고, byte 와 첫 줄 표시 폭이 허용할 때만 남은 짧은 의미를 아랫줄로 넘긴다.
- `translation_workset_credits` (`ready_with_spacing_conservatism`)
  크레딧 문자열은 전량 workset 에 편입됐다.
  전각 공백 패딩과 줄 정렬을 보수적으로 유지한다.
- `translation_workset_registry_d_dialogue` (`ready_with_packed_relocation`)
  Registry D entry 는 ROM 끝으로 재패킹하고 pointer-length table 을 갱신할 수 있으므로 원문 byte 슬롯보다 긴 번역도 적용 가능하다.
  번역은 지나친 축약보다 자연스러운 의미 보존을 우선한다.
  기존 명시적 개행을 보존한다.
  runtime page-flow 는 시각 QA 로 확인하고, 잘림이 보이면 번역 삭제보다 줄바꿈/문장 분할로 조정한다.
- `registry_a_entry8_clusters_manifest` (`ready_with_singleline_conservatism`)
  source 데이터가 명시적으로 다르게 말하지 않는 한, record 를 짧은 counted 단일 줄 payload 로 본다.
  수동 줄바꿈을 넣지 않는다.

## live playthrough 가 아직 필요한 항목

- 마지막 미발견 문자열 훑기
- 대사 runtime 의 시각적 page-turn 확인
- 기준 추출 source 밖에 있는 이미지 구워진 텍스트 확인

## 현재 해석

- 대부분의 기준 workset 은 source 별 레이아웃 규칙만 지키면 live playthrough 전에도 번역 시작이 가능하다.
- Registry D 는 더 이상 원문 슬롯 길이에 맞춘 초압축 번역이 기본값이 아니다.
- 이제 live playthrough 는 알려진 source 번역 시작의 전제조건이 아니라, 마지막 QA 훑기 역할에 가깝다.
- 이 보고서는 '번역을 시작할 수 있음' 과 'runtime/page QA 가 완전히 닫힘' 을 구분하기 위해 존재한다.
