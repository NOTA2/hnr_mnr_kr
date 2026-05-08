# Project Control Tower

이 문서는 **작업 후 갱신하는 총괄 현황판**이다.

매 세션의 시작점은 이 문서가 아니라 [session_start.md](/Users/user/test/docs/session_start.md) 이다.

## 현재 단계

- 메인 단계: `데이터 구조 조사 + 텍스트 추출`
- 보조 단계: `텍스트 재삽입 기반 유지`
- 대기 단계: `폰트/문자폭`, `이미지 리소스`, `GUI`

## 현재 활성 트랙

- [data_structure_investigation.md](/Users/user/test/docs/tracks/data_structure_investigation.md)
- [text_extraction_progress.md](/Users/user/test/docs/tracks/text_extraction_progress.md)

## 현재 최우선 과제

1. `0x1849A0` handler table singular cluster slot 소비 경로 찾기
2. `0x184A0C` numeric tail 과 `0x06D070` 소비 방식 분리
3. `field3` exact palette/subtype 의미 추가 분리
4. `0x093D` / `0x093E` / `0x094B` 고정 인덱스 리소스와 주변 helper 의미를 더 분리

## 단계 상태

- 데이터 구조 조사: `IN PROGRESS`
- 텍스트 추출: `IN PROGRESS`
- 텍스트 재삽입: `BOOTSTRAPPED`
- 폰트/문자 매핑: `NOT STARTED`
- 이미지 리소스: `NOT STARTED`
- GUI/작업 워크플로우: `DEFERRED`

## 최근 검증된 핵심 진전

- `0x17C1C0` 테이블이 `length-pointer` 레이아웃이라는 점 확인
- `0x076530` 부근 상위 포인터 허브와 여러 `pointer-length` 레지스트리 범위 확인
- `0x17785C` 레지스트리 accessor (`0x03BC`, `0x0414`) 와 호출자 목록 확인
- `0x17CE0` 가 `base + 2 * (x + y * 32)` 목적지 계산 helper 임을 확인
- `0x17EB4` / `0x017ED8` / `0x017EEC` 경로가 `0x17785C` 엔트리를 DMA3 (`0x040000D4/0xD8/0xDC`) 로 복사하는 공용 루틴임을 확인
- `0x007760` / `0x007824` 단독 accessor 경로가 각각 `0x093D -> 0x3D2A40`, `0x093E -> 0x3D2D60` 고정 리소스 엔트리를 읽는다는 점 확인
- `0x3D2D60` 재료 뱅크 앞쪽에 `5바이트 메타데이터 + u16 상대 문자열 오프셋` 7바이트 레코드 구간이 있고, 뒤쪽에 `cp932` 문자열이 이어진다는 점 확인
- `0x007578` 단독 accessor 경로가 `0x094B -> 0x3DDB30` binary table 을 읽으며 직접 평문 문자열 경로는 아니라는 점 확인
- `0x076530` 허브를 직접 가리키는 포인터가 `0x0002C0` literal 하나뿐이며, 이 값이 `0x000290` helper 의 상위 registry selector 로 쓰인다는 점 확인
- `0x0002CC` / `0x000304` 가 `0x000290` 위에 쌓인 generic `pointer-length` accessor 로 보이며, 각각 selected registry 의 포인터/길이 필드를 반환한다는 점 확인
- direct `0x0002CC` 호출 `20`개 중 현재 고정 selector 는 `1` 과 `3` 만 확인되며, `selector=1` 은 `entry 0` 단일 패턴, `selector=3` 은 `entry 0/2/3/5` 군집 패턴으로 갈린다는 점 확인
- `0x000304` 의 유일한 BL 호출자는 `0x000392` 이고, 이는 `0x00033C` wrapper 내부 길이 조회라는 점 확인
- `0x17C7E4` 전용 helper 가 기존 추정 `0x03E4` 가 아니라 실제 BL 호출이 있는 `0x03E8` 이며, `0x0106E6`, `0x010798`, `0x010892` 3개 caller 를 가진다는 점 확인
- `0x03E8` 는 `0x17C7E4 + index * 8` 의 첫 `u32` 를 읽는 pointer accessor 로 보이며, 이로 인해 현재 concrete access route 가 비어 있는 상위 registry 는 사실상 `0x17C384` 뿐이라는 점 확인
- `Registry B (0x17C384)` 의 `115`개 엔트리가 `0x183D50` 에 동일한 `pointer-length` 미러 테이블로 한 번 더 저장된다는 점 확인
- `0x183D50` 은 direct ref `22`개를 가지며, 공용 helper `0x068DF8` 가 `38`개 caller 를 통해 이 미러 테이블을 실제로 소비한다는 점 확인
- `0x068DF8` 는 엔트리 선두 `ZP` magic 을 검사해 decode 또는 raw fallback 으로 분기하며, `Registry B` 가 mixed compressed/raw asset bank 라는 근거를 제공한다는 점 확인
- `0x068DF8` caller 들이 고정 index 호출과 descriptor/global 기반 동적 index 호출로 나뉜다는 점 확인
- `0x1840F8..0x1841E7` 이 `15 * 16-byte` companion descriptor 배열이며, `destination_vram + registry_b_index + 2개 치수값` 패턴으로 읽힌다는 점 확인
- `0x1841E8..0x18421F` 이 `7 * 8-byte` palette companion descriptor 배열이며, `registry_b_index + destination_palette_ram` 패턴으로 읽힌다는 점 확인
- `0x184220` 이후에는 다른 metadata 와 문자열이 섞여 시작하므로, `0x1840E8..` 전체를 uniform struct 로 보면 안 된다는 경계 확인
- `0x184220..0x184244` 이 `10-entry` permutation/order table 이며, 그 뒤 `0x184248..0x1843FF` 가 `10 * 0x2C` fixed-size location record table 이라는 점 확인
- 기존 `location_texts.json` 은 standalone string bank 라기보다 location record table 내부 name field 추출본이라는 점 확인
- `0x184420..0x1844AF` 이 `(hotspot_id, location_index)` lookup table 이고, `0x1844B0..0x1847F7` 이 route path 시퀀스 영역이라는 점 확인
- `0x184888` 이 `10-entry` route block table 이고, 각 block 이 다시 `10-slot` matrix 로 읽히며 자기 자신의 slot 하나만 `null` 이라는 점 확인
- route 시퀀스가 `FF` 를 제외하면 `0..12` 값만 사용하므로, opcode script 보다 `13-node` 기반 path matrix 해석이 더 강하다는 점 확인
- `0x184820` 이 `13 * (x, y)` node position pair table 후보이고, location record `field1/field2` 와 거의 일치하지만, 코드 기준으로는 location icon / hotspot 좌상단 원점과 node anchor 관계로 보는 편이 더 정확하다는 점 확인
- `field0`, `field3`, `field4` 가 draw helper `0x63000` / `0x63424` 로 직접 전달되는 표시 파라미터라는 점 확인
- `0x63000` / `0x63424` 내부에서 `field4` 가 sprite attr2 low 10-bit tile index 쪽, `field3` 가 attr2 high-byte 상위 nibble 쪽을 조정한다는 점 확인
- `0x1849D4` 가 `(location_index, special event/script/message id)` 매핑으로 읽히며, `0x06D5A8` 이 둘째 필드를 runtime 객체로 바꿔 첫 필드 location slot 에 저장한다는 점 확인
- `0x06A838` helper 가 `0x030009A0 + location_index * 4` 활성 플래그를 읽는다는 점 확인
- `0x08BFC8..0x08C2B8` 구간에 location/world-map bundle 하위 table 과 runtime global 을 함께 묶는 dense static constant cluster 가 있다는 점 확인
- `0x1849A0` handler table 은 direct ref 가 `2`건뿐이고, `0x184248` / `0x1849D4` / `0x184820` / `0x1840F8` 등은 같은 cluster 안에서 반복 소비된다는 점 확인
- `0x184A0C` numeric tail 도 `0x06D070`, `0x08C1FC` live ref 가 있어 tail 경계를 더 보수적으로 잡아야 한다는 점 확인
- 세이브/진행 메뉴 텍스트와 크레딧 텍스트 추출

## 작업 후 최소 갱신 규칙

의미 있는 진전이 있었다면 아래는 항상 갱신한다.

1. 이 문서
2. 관련 트랙 문서 최소 1개
3. [current_constraints.md](/Users/user/test/analysis/current_constraints.md)
4. [experiment_log.md](/Users/user/test/analysis/experiment_log.md)
5. 필요 시 [initial_findings.md](/Users/user/test/analysis/initial_findings.md)

## 읽기 규칙

- 시작할 때 이 문서를 먼저 읽지 않는다.
- 현재 단계만 빠르게 확인하거나, 작업 후 상태를 갱신할 때 사용한다.
- 어떤 참고 문서를 열어야 할지 모르면 [reference_map.md](/Users/user/test/docs/reference_map.md) 를 본다.
