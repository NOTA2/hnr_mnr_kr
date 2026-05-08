# Font And Encoding Progress

읽기 규칙: 이 문서는 폰트/문자폭 조사가 활성 단계로 올라왔을 때만 읽는다.

이 문서는 폰트, 글리프, 문자 폭, 인코딩/테이블 조사 진행 상황을 기록합니다.

## 목적

- 한글 글리프를 넣을 수 있는 위치를 찾는다.
- 문자 폭 테이블과 표시 방식을 파악한다.
- 한글용 문자 매핑 전략을 세운다.

## 현재 상태

- 상태: `IN PROGRESS`

## 준비된 것

- 4bpp 타일 덤프 도구 사용 가능
- `.tbl` 기반 문자 테이블 처리 기본 지원

## 아직 확인되지 않은 것

- 실제 폰트 타일 위치
- 고정폭/가변폭 여부
- 문자 폭 테이블 위치
- 한글 글리프 삽입 가능 공간

## 최근 확인

- `0x0514xx` UI cluster 는 `0x075DD4` (`strlen`) 과 `0x03EB78` / `0x03ECCC` layout helper 를 반복 호출하는 **UI layout / slot setup 경로**에 가깝다.
- 같은 클러스터에서 따라간 `0x058720` 은 문자열 렌더러가 아니라, current tracked slot record (`0x714`) 의 좌표를 읽어 넘기는 position helper 다.
- 따라서 위 경로는 폰트/문자 매핑 자체를 찾는 direct route 로 보기 어렵다.
- world-map Registry B raw companion 엔트리 `86`, `87`, `88` 을 헤더 뒤에서 바로 4bpp 덤프한 결과는 [registry_b_entry_86_tiles.png](/Users/user/test/analysis/registry_b_entry_86_tiles.png), [registry_b_entry_87_tiles.png](/Users/user/test/analysis/registry_b_entry_87_tiles.png), [registry_b_entry_88_tiles.png](/Users/user/test/analysis/registry_b_entry_88_tiles.png) 처럼 잡음에 가깝다.
- 그래서 현재는 이 raw companion 엔트리들을 **직접 폰트 raw tile 후보에서 우선 제외**한다.

## 다음 할 일

1. 실제 문자 렌더러가 `strlen/layout` 앞단이 아니라 어디인지 더 찾기
2. 글자 폭 테이블 존재 여부 확인
3. 지역명/메뉴 표시용 폰트가 공용인지 확인
4. ZP/raw graphics 중 폰트 후보 asset 분리

## 진행 로그

### 2026-05-08

- 조사 도구만 준비됨

### 2026-05-09

- 한글 재삽입의 실제 병목이 폰트/문자 매핑/문자폭이라는 점을 명시하고 우선순위를 상향
- `0x0514xx` UI cluster 와 `0x058720` 을 따라가 본 결과, 이 경로는 문자 렌더링보다 layout / position 보조 루틴에 가깝다는 점을 확인
- Registry B raw companion 엔트리 `86..88` 을 4bpp 로 직접 덤프했지만 글자판이 아니라 잡음에 가까워, direct raw font 후보에서는 우선 제외
