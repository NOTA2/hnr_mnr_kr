# Project Structure

이 폴더는 프로젝트를 단순히 삭제 위주로 줄이는 것이 아니라, 다음 작업과 다음 GBA
한글화 프로젝트에도 재사용할 수 있게 구조화하기 위한 기준 문서다.

## 문서

- `current_layout.md`: 지금 repo가 실제로 어떤 역할별 폴더를 갖고 있는지 정리한다.
- `target_layout.md`: 최종적으로 지향할 깔끔한 구조를 정의한다.
- `migration_map.md`: 현재 경로에서 목표 구조로 옮길 때의 단계와 호환성 전략을 정리한다.
- `../starter_kit/gba_localization_agent.md`: 이 프로젝트에서 얻은 정리/회고 규칙을
  다른 GBA 한글화 프로젝트에도 쓸 수 있게 중립화한 에이전트 초안이다.

## 원칙

- 막바지 QA 중인 프로젝트를 깨지 않기 위해, 대량 이동은 dependency trace 이후에만 한다.
- 먼저 active 경로 의존성을 줄이고, 그 다음 파일 이동 또는 untrack을 한다.
- `confirmed_data/`는 지금 당장 이름을 바꾸지 않는다. 현재 스크립트와 GUI가 강하게 의존한다.
- `analysis/`는 곧바로 삭제하지 않는다. 회고와 스타트킷으로 옮길 교훈을 먼저 요약한다.
- 새 구조는 이 repo 전용 산출물과 범용 GBA 한글화 스타트킷을 분리해야 한다.
