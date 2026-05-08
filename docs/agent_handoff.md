# Agent Handoff

이 문서는 **지금 바로 다음 에이전트가 이어서 할 일**만 짧게 정리한 문서다.

전체 상태는 [project_control_tower.md](/Users/user/test/docs/project_control_tower.md), 시작 규칙은 [session_start.md](/Users/user/test/docs/session_start.md) 를 따른다.

## 현재 작업 초점

- 메인 초점: `데이터 구조 조사`
- 동반 초점: `텍스트 추출 범위 확대`

## 지금 가장 중요한 사실

- `0x17C1C0` 은 `length-pointer` 레이아웃의 예외적 디스크립터 테이블이다.
- `0x076530` 부근에는 여러 상위 레지스트리 경계를 가리키는 포인터 허브가 있다.
- `0x17785C` 레지스트리에는 실제 Thumb accessor `0x03BC`, `0x0414` 가 존재한다.
- `0x17CE0` 는 `(base, x, y)` 를 받아 `base + 2 * (x + y * 32)` 목적지 주소를 계산하는 helper 로 보인다.
- `0x17EB4` / `0x017ED8` / `0x017EEC` 는 같은 index 에 대해 포인터/길이를 읽은 뒤 DMA3 (`0x040000D4/0xD8/0xDC`) 로 halfword 복사를 시작하는 공용 루틴으로 보인다.
- 따라서 `0x17785C` 의 `pointer+length` 경로는 적어도 이 호출부에서는 텍스트가 아니라 그래픽/타일맵 리소스 쪽일 가능성이 높다.
- `0x007760` 단독 호출부는 고정 index `0x093D -> 0x3D2A40` binary table 에서 4바이트 레코드를 읽어 구조체 필드를 채운다.
- `0x007824` 단독 호출부는 고정 index `0x093E -> 0x3D2D60` resource 를 읽으며, 앞쪽 `7-byte` 레코드 (`5바이트 메타데이터 + u16 상대 문자열 오프셋`) 와 뒤쪽 `cp932` 문자열을 함께 사용한다.
- `0x007578` 단독 호출부는 고정 index `0x094B -> 0x3DDB30` binary table 경로로 보이며, 현재까지는 직접 평문 문자열 접근으로 보이지 않는다.
- `0x076530` 허브는 `0x0002C0` literal 을 통해 `0x000290` helper 에서 직접 참조된다.
- `0x000290` 는 허브 첫 4엔트리 (`0x17785C`, `0x17C2F4`, `0x17C384`, `0x17C71C`) 중 하나의 base pointer 를 선택해 반환하는 상위 registry selector helper 로 보인다.
- `0x0002CC` / `0x000304` 는 그 위에 쌓인 generic accessor 로, 선택된 registry 엔트리의 `pointer` / `length` 필드를 읽는다.
- direct `0x0002CC` 호출 `20`개 중 현재 고정 selector 로 확인된 값은 `1` 과 `3` 뿐이다.
- `selector=1` direct 호출 `8`개는 모두 `entry_index=0` 으로 `Registry A (0x17C2F4)` 첫 엔트리를 읽는다.
- `selector=3` direct 호출 `11`개는 `entry_index 0/2/3/5` 를 읽으며 `0x06F4xx`, `0x0704xx`, `0x0709xx` 군집으로 모인다.
- `0x000304` 의 유일한 BL 호출자는 `0x000392` 이고, 이는 `0x00033C` wrapper 내부 길이 조회다.
- `0x00033C` 의 알려진 BL 호출자 `6`개는 현재 모두 `selector=3` 을 넘긴다.
- `0x17C7E4` 는 허브에 들어 있지만 generic `0x000290` family 가 복사하는 첫 4엔트리 바깥에 남아 있고, 별도 direct helper `0x03E8` 계열로 접근된다.
- `0x03E8` helper 는 literal base `0x17C7E4` 를 읽고 `base + index * 8` 위치의 첫 `u32` 를 반환하는 pointer accessor 로 보인다.
- `0x03E8` BL 호출자는 `0x0106E6`, `0x010798`, `0x010892` 총 `3`개다.
- `Registry B (0x17C384)` 의 `115`개 엔트리는 `0x183D50` 에 완전히 같은 `pointer-length` 미러 테이블로 한 번 더 저장되어 있다.
- `0x183D50` 은 direct 포인터 참조 `22`개가 잡히며, code literal 과 data descriptor 배열 양쪽에서 실제로 소비된다.
- 공용 helper `0x068DF8` 는 `0x183D50 + index * 8` 에서 엔트리 포인터를 읽고, 선두 2바이트가 `ZP` 인지 검사한 뒤 `ZP`면 내부 decode 경로(`0x068E40`), 아니면 raw fallback (`0x068D54`) 로 분기한다.
- `0x068DF8` BL 호출자는 현재 `38`개가 확인되었다.
- 미러 테이블 엔트리 `50 / 115`개는 `ZP00` 또는 `ZP01` 헤더로 시작한다.
- `0x068DF8` caller 는 한 종류가 아니다. 일부 cluster 는 고정 index (`0x5A`, `0x29`, `0x28`, `0x13`, `0x0B`, `0x0E`, `0x0A`, `0x38`, `0x36`, `0x4A`) 를 직접 넘기고, 다른 cluster 는 global byte / 16-byte descriptor row 에서 index 를 읽어 온다.
- `0x1840F8..0x1841E7` 구간에는 `15`개의 `16-byte` companion descriptor 가 있으며, 현재 해석은 `destination_vram + registry_b_index + dim_a + dim_b` 다.
- 이 `15`개 descriptor 는 Registry B index `0x59`, `0x57`, `0x58`, `0x56`, `0x4E`, `0x4F`, `0x4B`, `0x4D`, `0x53`, `0x55`, `0x51`, `0x4C`, `0x52`, `0x54`, `0x6F` 를 사용한다.
- `0x1841E8..0x18421F` 구간에는 `7`개의 `8-byte` companion descriptor 가 있으며, 현재 해석은 `registry_b_index + destination_palette_ram` 다.
- 이 `7`개 palette descriptor 는 Registry B index `0x61`, `0x60`, `0x5F`, `0x5C`, `0x5D`, `0x5E`, `0x70` 를 사용한다.
- `0x184220` 이후에는 다른 metadata 와 문자열이 섞이기 시작하므로, `0x1840E8..` 전체를 한 가지 uniform struct 로 다시 가정하면 안 된다.
- 따라서 `selector=0` direct generic caller 부재는 `0x17785C` 의 전용 helper (`0x03BC`, `0x0414`) 로 설명 가능하고, `Registry B` 역시 dead registry 가 아니라 **미러 테이블 + ZP-aware helper family** 경로로 접근되는 live asset bank 로 보는 편이 맞다.
- 일부 메뉴/진행 메시지는 일반 `00` 종단 평문이 아니라 명령 스트림 내부 문자열이다.

## 다음 한 단계 후보

1. `0x184220` 이후 tail metadata/string block 과 `0x08BFF8` / `0x08C0A8` / `0x08C210` data descriptor ref 를 분리하기
2. `0x093D` / `0x094B` binary resource 의미를 더 분리하기
3. 대사/이벤트 평문 구간을 추가로 찾기

매 실행에서는 위 셋 중 **하나만** 고른다.

## 이 작업에 바로 필요한 문서

- [current_constraints.md](/Users/user/test/analysis/current_constraints.md)
- [data_structure_investigation.md](/Users/user/test/docs/tracks/data_structure_investigation.md)
- [text_extraction_progress.md](/Users/user/test/docs/tracks/text_extraction_progress.md)

## 필요할 때만 읽는 참고 문서

- 리소스 레지스트리 구조: [resource_registry_map.md](/Users/user/test/analysis/resource_registry_map.md)
- accessor 함수 메모: [registry_accessor_helpers.md](/Users/user/test/analysis/registry_accessor_helpers.md)
- Registry B 미러 산출물: [registry_b_mirror_summary.json](/Users/user/test/analysis/registry_b_mirror_summary.json)
- Registry B companion descriptor 산출물: [registry_b_companion_descriptors.json](/Users/user/test/analysis/registry_b_companion_descriptors.json)
- 리소스 청크 예외 테이블: [resource_chunk_directory.md](/Users/user/test/analysis/resource_chunk_directory.md)
- 전체 참고 맵: [reference_map.md](/Users/user/test/docs/reference_map.md)

## 작업 규칙

1. ROM 바이너리는 커밋하지 않는다.
2. `.gba` ignore 상태를 유지한다.
3. 같은 실패 가설을 조건 변화 없이 반복하지 않는다.
4. 한 번에 큰 점프보다 검증 가능한 작은 단계 하나를 끝낸다.
5. 의미 있는 진전 뒤에는 총괄 문서, 관련 트랙 문서, 제약 요약, 실험 로그를 갱신한다.
