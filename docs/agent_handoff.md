# Agent Handoff

이 문서는 다음 에이전트가 현재 상태를 빠르게 이해하고, 사용자 개입 없이도 안전하게 다음 작업을 이어갈 수 있도록 정리한 작업 지침입니다.

## 프로젝트 목표

`Hagane no Renkinjutsushi - Meisou no Rondo (Japan).gba` 를 한국어로 현지화할 수 있는 툴체인과 작업 흐름을 만든다.

최종적으로는 아래 기능을 목표로 한다.

- 텍스트 추출
- 번역 데이터 편집
- 텍스트 재삽입
- 포인터 자동 수정
- 한글 폰트 삽입
- 이미지 추출/교체
- 나중에 GUI 워크플로우 제공

## 현재 상태

완료:

- ROM 헤더 확인 가능
- 문자열 스캔 가능
- 범위 지정 문자열 추출 가능
- 포인터 탐색 가능
- LZ77 후보 스캔 가능
- 4bpp 덤프 가능
- 문자열 제자리 교체 가능
- 자유 공간 주입 및 포인터 갱신 가능
- 번역 JSON 일괄 적용 기본 기능 추가

확인된 분석 결과:

- 일부 문자열은 `cp932 + 00 terminator` 형태의 평문이다.
- 시스템 메시지와 아이템 관련 문자열이 실제로 추출되었다.
- 참조 포인터 예시가 확인되었다.
- 지역명 텍스트 뱅크(`0x18425C` 부근)가 추가로 확인되었다.
- 전투 기술/능력 텍스트 대형 뱅크(`0x3D2059`, `0x3D329C`)가 확인되었다.
- `0x3Dxxxx` 대형 뱅크는 일반 GBA 절대 포인터가 바로 잡히지 않는다.
- UI 기술 텍스트 뱅크(`0x08B62C`)가 별도로 존재하며 일부 기술명이 중복된다.
- `0x3Dxxxx` 계열 문자열 안에는 `0x0B` 제어 코드가 섞여 있다.

참고 파일:

- [README.md](/Users/user/test/README.md)
- [initial_findings.md](/Users/user/test/analysis/initial_findings.md)
- [text_bank_inventory.md](/Users/user/test/analysis/text_bank_inventory.md)
- [item_texts.json](/Users/user/test/analysis/item_texts.json)
- [system_messages.json](/Users/user/test/analysis/system_messages.json)
- [location_texts.json](/Users/user/test/analysis/location_texts.json)
- [battle_texts.json](/Users/user/test/analysis/battle_texts.json)
- [ability_texts.json](/Users/user/test/analysis/ability_texts.json)
- [ui_skill_texts.json](/Users/user/test/analysis/ui_skill_texts.json)

## 가장 중요한 작업 원칙

1. ROM 바이너리 자체는 커밋하지 않는다.
2. `.gba` 는 계속 `.gitignore` 상태로 유지한다.
3. 사용자보다 앞서 무리하게 GUI를 만들지 않는다.
4. 먼저 내부 엔진과 게임 구조 파악을 끝낸다.
5. 한 번에 큰 점프보다, 검증 가능한 작은 단계로 진행한다.
6. 새 조사 결과는 문서에 남긴다.

## 다음 우선순위

### 1순위

텍스트 추출 범위를 더 넓혀서 번역 가능한 데이터셋을 늘린다.

구체 작업:

- 메뉴 문자열 구간 찾기
- 대사/이벤트 문자열이 평문인지 압축인지 확인
- `0x3Dxxxx` 텍스트 뱅크의 참조 구조를 확인
- 새로 찾은 범위를 JSON으로 추출

### 2순위

폰트와 표시 계층을 조사한다.

구체 작업:

- 4bpp 타일 덤프로 폰트 후보 찾기
- 고정폭/가변폭 여부 판단
- 문자 폭 테이블 존재 여부 확인
- 한글 추가 가능 영역 추정

### 3순위

일괄 삽입기의 안정성을 높인다.

구체 작업:

- 제어 코드가 섞인 문자열 처리 전략 정리
- 리포인트 시 포인터 후보 다중 갱신 검증
- 긴 문자열 삽입 리포트 개선
- 실패 사례를 문서화

### 4순위

번역 작업용 GUI 설계 초안을 만든다.

단, 아래가 먼저다:

- 추출 데이터 구조 안정화
- 삽입 엔진 안정화
- 폰트/매핑 방향 결정

## 권장 작업 방식

한 번 실행에서 딱 하나의 의미 있는 진전을 만드는 것을 기본 원칙으로 한다.

예:

- 새 텍스트 구간 1개 찾기
- 폰트 후보 영역 1개 검증
- 삽입기 예외 1개 해결
- 분석 메모 1회 업데이트

## 실행 명령 예시

ROM 정보:

```bash
python3 -m gba_kor_tool info "Hagane no Renkinjutsushi - Meisou no Rondo (Japan).gba"
```

문자열 스캔:

```bash
python3 -m gba_kor_tool scan-text \
  "Hagane no Renkinjutsushi - Meisou no Rondo (Japan).gba" \
  --encoding cp932 \
  --terminator 00 \
  --require-japanese \
  --limit 100
```

범위 추출:

```bash
python3 -m gba_kor_tool extract-range \
  "Hagane no Renkinjutsushi - Meisou no Rondo (Japan).gba" \
  0x08AEFC \
  0x08B400 \
  --encoding cp932 \
  --terminator 00 \
  --output analysis/item_texts.json
```

번역 적용:

```bash
python3 -m gba_kor_tool apply-translations \
  "Hagane no Renkinjutsushi - Meisou no Rondo (Japan).gba" \
  analysis/item_texts.json \
  patched.gba \
  --encoding cp932 \
  --search-free-space-from 0x700000 \
  --report analysis/item_patch_report.json
```

## 문서 업데이트 규칙

새 조사 결과가 있으면 아래 중 최소 하나를 갱신한다.

- [initial_findings.md](/Users/user/test/analysis/initial_findings.md)
- 이 문서
- README 사용 예시

## 당장 다음 에이전트가 시작할 일

1. `0x3D2059` 와 `0x3D329C` 뱅크가 절대 포인터 대신 어떤 방식으로 참조되는지 확인한다.
2. `0x18425C` 지역명 뱅크를 기준으로 폰트 표시와 메뉴 사용 위치를 역추적해 본다.
3. 대사/이벤트 평문 구간이 더 있는지 `scan-text` 로 추가 탐색한다.
4. 의미 있는 결과가 나오면 분석 문서를 갱신하고, 폰트 조사 단계로 넘어갈 수 있을지 판단한다.
