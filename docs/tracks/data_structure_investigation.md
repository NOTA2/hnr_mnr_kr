# Data Structure Investigation

읽기 규칙: 이 문서는 현재 활성 트랙이므로 세션 시작 시 읽는다.

이 문서는 ROM 내부 구조 조사 진행 상황만 따로 기록합니다.

## 목적

- 텍스트 저장 형식 파악
- 포인터/참조 구조 파악
- 제어 코드 파악
- 폰트/이미지/압축 구조로 넘어가기 위한 기반 확보

## 현재 상태

- 상태: `IN PROGRESS`

## 확인된 사실

### 텍스트 저장 형식

- 일부 문자열은 `cp932 + 00 terminator` 형태의 평문이다.
- 평문 문자열은 ROM 여러 위치에 분산되어 있다.
- 일부 메뉴/진행 메시지는 `00` 종단 평문이 아니라, **명령 스트림 내부에 박힌 `cp932` 문자열**로 보이며 `0x10` 종단/구분을 사용하는 사례가 확인되었다. (`0x772E64` 부근)

### 포인터 구조

- 지역명 뱅크 `0x18425C` 는 일반 GBA 절대 포인터가 확인되었다.
- 시스템 메시지와 아이템 계열도 절대 포인터 예시가 확인되었다.
- `0x3D2059` 와 `0x3D329C` 대형 뱅크는 같은 방식의 절대 포인터가 바로 잡히지 않았다.
- `0x3D2036` 전투 뱅크는 순차적인 0종단 문자열 목록으로 보인다.
- `0x3D327E` 능력 뱅크는 순차적인 `이름+0x0B+설명` 목록으로 보인다.
- `0x17C1C0` 부근에는 `u32 length + u32 rom_address` 형식의 리소스 디스크립터 테이블이 존재한다.
- 이 테이블은 `pointer + length` 로 읽으면 깨지고, `length + pointer` 로 읽으면 연속 엔트리가 유효하게 나온다.
- 이 테이블은 여러 엔트리가 서로 겹치므로 단순한 비중첩 청크 경계표가 아니다.
- 현재 텍스트가 강하게 보이는 엔트리는 `index 4`, `7`, `17`, `18`, `19`, `20`, `21` 이다.
- `0x076530` 부근에는 `0x17C2F4`, `0x17C384`, `0x17C71C`, `0x17C7E4` 를 가리키는 상위 포인터 허브가 있다.
- 이 상위 구간들은 `pointer-length` 레지스트리로 해석되며, `0x17C1C0` 과는 레이아웃이 다르다.
- `0x0002C0` 에는 `0x076530` 을 가리키는 direct pointer literal 이 있고, `0x000290` helper 가 이 값을 통해 허브 첫 4엔트리를 로컬 버퍼로 복사한 뒤 하나를 선택해 반환한다.
- `0x0002CC` 는 `(entry_index, registry_selector)` 를 받아 선택된 허브 registry 의 `pointer` 필드를 읽는 generic accessor 로 보인다.
- `0x000304` 는 같은 방식으로 `length` 필드를 읽는 generic accessor 로 보인다.
- `0x0002CC` 의 BL 호출자는 현재 `20`개, `0x000304` 의 BL 호출자는 현재 `1`개가 확인되었다.
- direct `0x0002CC` 호출 `20`개를 분류하면, 현재 고정 selector 는 `1` 과 `3` 만 확인된다.
- `selector=1` direct 호출 `8`개 (`0x000B04`, `0x005472`, `0x0091C6`, `0x015A28`, `0x01606A`, `0x0618A4`, `0x064B5C`, `0x069D72`) 는 모두 `entry_index=0` 으로 `Registry A (0x17C2F4)` 첫 엔트리를 읽는다.
- `selector=3` direct 호출 `11`개 (`0x06F47E`, `0x06F48C`, `0x06F556`, `0x070470`, `0x070480`, `0x070552`, `0x070564`, `0x070904`, `0x070914`, `0x0709E6`, `0x0709F8`) 는 `entry_index 0/2/3/5` 를 읽는다.
- 남은 `0x000378` 호출은 고정 selector 가 아니라 `0x00033C` wrapper 내부 공용 경로다.
- `0x00033C` 의 알려진 BL 호출자 `6`개는 현재 모두 `selector=3` 을 넘긴다.
- `0x17C7E4` 에 대해서는 별도 direct helper `0x03E8` 이 확인되었고, literal base `0x17C7E4` + `index * 8` 의 첫 `u32` 를 읽는 pointer accessor 로 보인다.
- `0x03E8` BL 호출자는 `0x0106E6`, `0x010798`, `0x010892` 총 `3`개다.
- `Registry B (0x17C384)` 의 `115`개 엔트리는 `0x183D50` 에 완전히 같은 `pointer-length` 미러 테이블로 한 번 더 저장되어 있다.
- `0x183D50` 에 대한 direct pointer ref 는 현재 `22`개가 확인되었다.
- 공용 helper `0x068DF8` 는 `0x183D50 + index * 8` 에서 엔트리 포인터를 읽고, 선두 2바이트가 `ZP` 인지 검사한 뒤 decode helper (`0x068E40`) 또는 raw fallback (`0x068D54`) 로 분기한다.
- `0x068DF8` BL 호출자는 현재 `38`개다.
- 미러 엔트리 중 `50 / 115`개는 `ZP00` 또는 `ZP01` 헤더를 가진다.
- `0x068DF8` caller 패턴은 mixed 다. 일부는 fixed index (`0x5A`, `0x29`, `0x28`, `0x13`, `0x0B`, `0x0E`, `0x0A`, `0x38`, `0x36`, `0x4A`) 를 직접 넘기고, 일부는 global byte 또는 `16-byte` descriptor row 에서 index 를 읽어 온다.
- `0x1840F8..0x1841E7` 구간에는 `15`개의 `16-byte` companion descriptor 가 존재하며, 현재 해석은 `destination_vram + registry_b_index + dim_a + dim_b` 다.
- `0x1841E8..0x18421F` 구간에는 `7`개의 `8-byte` companion descriptor 가 존재하며, 현재 해석은 `registry_b_index + destination_palette_ram` 다.
- `0x184220` 이후에는 별도 metadata 와 문자열이 섞이기 시작하므로, 이 전체 구간을 하나의 struct family 로 다시 묶으면 안 된다.
- `0x17CE98` 부근은 청크 디스크립터보다 주소 배열에 더 가깝다.
- `0x17785C` 레지스트리는 `0x03BC` / `0x0414` Thumb helper 로 직접 접근되는 것이 확인되었다.
- 수동 해석 기준으로 `0x03BC` 는 포인터 필드, `0x0414` 는 길이 필드 accessor 에 가깝다.
- `0x17CE0` 는 `(base, x, y)` 를 받아 `base + 2 * (x + y * 32)` 를 계산하는 목적지 주소 helper 다.
- `0x17EB4` 함수 안의 `0x017ED8` / `0x017EEC` 호출은 같은 index 에 대해 `0x03BC` / `0x0414` 를 연속 호출한 뒤, DMA3 레지스터 `0x040000D4` / `0x040000D8` / `0x040000DC` 로 `length >> 1` halfword 복사를 수행한다.
- 따라서 `0x17785C` 레지스트리는 적어도 일부 경로에서 텍스트가 아니라 타일/타일맵 계열 그래픽 리소스 공급원으로 쓰인다.
- `0x007578` 단독 accessor 호출부는 고정 index `0x094B` (`0x3DDB30`, 길이 `0x02C3`) binary table 을 읽는다.
- `0x007760` 단독 accessor 호출부는 고정 index `0x093D` (`0x3D2A40`, 길이 `0x0320`) binary table 을 읽고 `4-byte` 레코드를 구조체 필드에 복사한다.
- `0x007824` 단독 accessor 호출부는 고정 index `0x093E` (`0x3D2D60`, 길이 `0x06C0`) 를 읽으며, 앞쪽 `7-byte` 레코드에서 메타데이터와 상대 문자열 오프셋을 꺼내 뒤쪽 `cp932` 문자열 구간과 연결한다.
- 같은 `0x093E` 경로 안의 helper `0x795C` 는 `record[5:7]` 상대 오프셋을 사용해 같은 리소스 내부 문자열 포인터를 만든다.

### 제어 코드

- `0x0B` 가 문자열 중간에 섞여 있으며 줄바꿈 또는 문장 분리 코드로 보인다.

### 추출 필터 교정

- 전각 공백 `U+3000` 이 많은 문자열이 기존 추출 필터에서 누락되고 있었다.
- 원인: 전각 공백이 비정상 문자처럼 계산되어 printable 비율이 과도하게 낮아졌다.
- 조치: 추출 필터에서 `U+3000` 을 허용 문자로 처리하도록 수정했다.

## 현재 해석

- 이 게임은 텍스트 뱅크마다 참조 방식이 다를 가능성이 높다.
- 따라서 전체 ROM에 단일한 삽입 규칙 하나만 적용하기는 어려울 수 있다.
- 특히 `0x3Dxxxx` 대형 뱅크는 절대 포인터형이라기보다 인덱스 기반 접근일 가능성이 더 높아졌다.
- 동시에 이 뱅크들은 더 큰 리소스 디스크립터 테이블 안에 포함되어 있으며, 일부 엔트리는 부모/자식 또는 하위 뷰 관계일 가능성이 있다.
- 다만 `0x17C1C0` 은 공통 상위 레지스트리 허브에서 직접 잡히지 않아, 예외적 보조 디스크립터일 가능성을 따로 관리해야 한다.
- 현재까지는 `0x17785C` 쪽이 실제 코드 accessor 근거가 가장 강한 공용 레지스트리다.
- 그러나 가장 상위 구조만 보면, `0x17785C` 는 `0x076530` 허브 첫 엔트리이기도 하며 `0x000290` / `0x0002CC` / `0x000304` generic family 를 통해 다른 상위 registry (`0x17C2F4`, `0x17C384`, `0x17C71C`) 와 같은 계층에서 선택될 수 있다.
- 다만 `pointer + length` 를 모두 쓰는 `0x17EB4` 경로는 DMA 기반 그래픽 복사 루틴으로 굳어졌으므로, 텍스트 로더를 찾으려면 이제 `0x03BC` 단독 호출부를 우선적으로 해석하는 편이 낫다.
- 그리고 `0x03BC` 단독 호출부는 전부 같은 성격이 아니다. 일부는 순수 binary table (`0x093D`, `0x094B`) 를 읽고, 일부는 binary header + 문자열 본문이 결합된 mixed resource (`0x093E`) 를 읽는다.
- 따라서 앞으로는 "이 호출부가 텍스트인가 아닌가"를 이분법으로 보지 말고, "고정 index -> record directory -> 상대 문자열 오프셋" 같은 중간 단계를 포함해 해석해야 한다.
- 반면 `0x17C7E4` 는 허브에 포함되어도 `0x000290` family 가 복사하는 4엔트리 바깥에 있어, 상위 registry 묶음 안에서도 별도 취급되는 예외 축으로 보인다.
- 또한 현재 관찰된 generic hub accessor 사용은 모든 registry 에 고르게 퍼져 있지 않다. direct `0x0002CC` 는 `Registry A` 와 `Registry C` 에만 고정으로 붙어 있다.
- `selector=0` direct 사용이 안 보이는 점은 `0x17785C` 전용 helper (`0x03BC`, `0x0414`) 가 이미 널리 쓰인다는 점으로 어느 정도 설명된다.
- 그리고 `Registry B` 역시 실제로는 `0x17C384` 원본 base 가 아니라 `0x183D50` 미러 테이블과 `0x068DF8` 공용 helper family 쪽에서 소비되는 것으로 보인다.
- 따라서 이제 미해결점은 "Registry B 에 concrete access route 가 있는가"가 아니라, "caller 들이 어떤 index 군과 companion descriptor 를 쓰는가"와 "`0x184220` 이후 tail 이 어떤 상위 descriptor 에 묶이는가"로 바뀌었다.

## 근거 문서

- [analysis/initial_findings.md](/Users/user/test/analysis/initial_findings.md)
- [analysis/text_bank_inventory.md](/Users/user/test/analysis/text_bank_inventory.md)

## 다음 할 일

1. `0x184220` 이후 tail metadata/string block 구조 확인
2. `0x08BFF8` / `0x08C0A8` / `0x08C210` data descriptor 와 `0x183D50` / `0x1840E8` / `0x1841E8` 연결 구조 확인
3. `0x093D` 와 `0x094B` binary table 이 각각 어떤 게임 데이터 분류를 담는지 분리
4. 왜 `0x17C1C0` 이 상위 허브와 다른 레이아웃을 유지하는지 설명할 구조 찾기
5. 겹치는 엔트리의 관계를 부모/자식/메타데이터 관점에서 분류
6. `0x3D2036` 전투 기술 뱅크 참조 방식 확인
7. `0x3D327E` 대형 능력 뱅크 참조 방식 확인
8. 폰트 조사에 들어가기 전 텍스트 뱅크 유형 분류 확정

## 진행 로그

### 2026-05-08

- 평문 `cp932 + 00` 문자열 존재 확인
- 절대 포인터가 직접 잡히는 뱅크와 잡히지 않는 뱅크를 구분
- `0x0B` 제어 코드 존재 확인
- `0x3D2036` 전투 뱅크가 순차적 이름/설명 목록 구조임을 확인
- `0x3D327E` 능력 뱅크가 순차적 결합 문자열 목록 구조임을 확인
- 전각 공백 때문에 추출 누락이 생기던 필터 문제를 수정
- `inspect-chunk-table` 로 `0x17C1C0` 테이블이 `length + pointer` 형식임을 확인
- 같은 테이블 엔트리들이 서로 겹친다는 점을 확인
- `0x076530` 부근 포인터 허브와 그 아래 `pointer-length` 상위 레지스트리 범위를 확인
- `0x17C1C0` 이 주변 공통 레지스트리와 다른 예외 레이아웃임을 확인
- `find-thumb-bl` 기능으로 `0x17785C` 레지스트리 accessor 호출자들을 정리
- `0x17CE0` 가 32열 halfword 목적지 계산 helper 임을 확인
- `0x17EB4` / `0x017ED8` / `0x017EEC` 경로가 `0x17785C` 엔트리를 DMA3 로 복사하는 그래픽 리소스 로더임을 확인
- `0x007578` / `0x007760` / `0x007824` 단독 accessor 경로가 각각 `0x094B` / `0x093D` / `0x093E` 고정 index 리소스로 이어진다는 점을 확인
- `0x3D2D60` 재료 뱅크 앞쪽에 `7-byte` 레코드 디렉터리가 있고, 뒤쪽 텍스트는 그 상대 오프셋으로 연결된다는 점을 확인
- `0x076530` 허브가 `0x0002C0` literal 을 통해 `0x000290` helper 에서 직접 쓰이며, `0x0002CC` / `0x000304` generic registry accessor 의 기반이라는 점을 확인
- direct `0x0002CC` 호출들이 `selector=1` 과 `3` 두 군집으로 갈리고, `0x000304` 는 `0x00033C` wrapper 내부 길이 조회로만 보인다는 점을 확인
- `0x17C7E4` 전용 helper 는 `0x03E4` 가 아니라 `0x03E8` 이며, BL caller `3`개와 `pointer accessor` 패턴이 실제로 확인된다는 점을 확인
- `Registry B` 원본 테이블이 `0x183D50` 에 완전히 같은 미러 테이블로 한 번 더 저장되며, 이 쪽이 실제 live access path 로 보인다는 점을 확인
- `0x068DF8` helper 가 `0x183D50` 엔트리 선두의 `ZP` magic 을 검사해 decode 또는 raw fallback 으로 분기하고, BL caller `38`개를 가진다는 점을 확인
- `0x068DF8` caller 들이 fixed index 경로와 descriptor/global 기반 동적 index 경로로 나뉜다는 점을 확인
- `0x1840F8..0x1841E7` 구간이 `15 * 16-byte` 타일 companion descriptor 배열이며, Registry B index 와 VRAM 목적지를 함께 담는다는 점을 확인
- `0x1841E8..0x18421F` 구간이 `7 * 8-byte` palette companion descriptor 배열이며, Registry B index 와 palette RAM 목적지를 함께 담는다는 점을 확인
- `0x184220` 이후부터는 별도 metadata 와 문자열 tail 이 섞이기 시작한다는 점을 확인
