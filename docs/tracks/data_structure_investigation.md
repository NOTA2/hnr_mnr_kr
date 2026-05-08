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
- `0x184220..0x184244` 구간에는 `3, 4, 0, 2, 7, 9, 5, 1, 6, 8` 값의 `10-entry` permutation/order table 이 있다.
- `0x184248..0x1843FF` 구간은 `10 * 0x2C` fixed-size location record table 이며, 각 row 는 `5 * u32 metadata + 0x18-byte name field` 구조로 읽힌다.
- 첫 name field `0x18425C` 는 기존에 문자열 뱅크로 추출됐지만, 실제로는 첫 location record (`0x184248`) 의 `+0x14` 필드다.
- `0x184248` record base direct ref 는 `12`개, `0x18425C` first name field direct ref 는 `4`개가 확인되었다.
- `0x184420..0x1844AF` 구간의 `18 * (u32, u32)` table 은 현재 `(hotspot_id, location_index)` lookup table 로 보는 해석이 가장 강하다.
- `0x1844B0..0x1847F7` 구간에는 `FF` 종료 경로 시퀀스가 밀집해 있다.
- `0x184888` 구간은 `10-entry` route block pointer table 이며, 각 block 은 다시 `10-slot` pointer matrix 로 읽힌다.
- 이 matrix 의 non-null slot 은 `0x1844B0..0x1847F7` 시퀀스를 가리킨다.
- 모든 block 은 자기 자신의 slot 하나만 `null` 이다. 즉 `block n -> slot n` 패턴이 고정이다.
- route 시퀀스는 `FF` 를 제외하면 현재 `0..12` 값만 사용한다.
- `0x184820` 구간은 `13 * (x, y)` node position pair table 후보다.
- location record `field1/field2` 와 `0x184820` node pair 앞 `10`개는 `8 / 10` 완전 일치, `2 / 10` 작은 delta 패턴을 보인다.
- 코드 기준으로 `field1/field2` 는 location icon / hotspot 사각형의 좌상단 좌표로 보는 편이 더 정확하다.
- `field0`, `field3`, `field4` 는 helper `0x63000` / `0x63424` 로 직접 전달되는 draw 파라미터다.
- caller/helper 내부 wiring 기준으로 보면 `field4` 는 `r3` 를 통해 attr2 low 10-bit tile index 쪽을, `field3` 는 stack arg 를 통해 attr2 high-byte 상위 nibble 쪽을 조정한다.
- 따라서 현재 가장 안전한 해석은 `field0 = asset/icon family ID 후보`, `field3 = palette bank / draw subtype 후보`, `field4 = graphic/tile-base variant 후보` 다.
- `0x184950` 구간에는 `10 * (x, y)` label position pair 후보가 있다.
- `0x1849A0` 구간에는 `13-entry` Thumb handler pointer table 이 있고, 현재는 위 `13-node` 축과 정렬될 가능성을 우선 둔다.
- `0x1849D4` 구간은 현재 `(location_index, special event/script/message id)` 의미의 `7-entry` special pair table 로 보는 해석이 가장 강하다.
- `0x06A838` helper 는 `0x030009A0 + location_index * 4` 플래그를 읽어 활성 여부를 판정하므로, location 활성/비활성은 record field 가 아니라 별도 runtime array 가 맡는다.
- `0x08BFC8..0x08C2B8` 구간에는 location/world-map bundle table 과 `0x03002Fxx` / `0x03005Fxx` / `0x030060xx` / `0x030009xx` runtime global 을 함께 묶는 dense static constant cluster 가 있다.
- 이 cluster 안에서 `0x1849A0` handler table 은 사실상 `1`회만 재등장하지만, `0x184248`, `0x1849D4`, `0x184820`, `0x1840F8`, `0x1841E8` 는 여러 번 반복된다.
- `0x184A0C` 이후 table 도 direct ref (`0x06D070`, `0x08C1FC`) 가 있어, location bundle family 경계를 `0x184A0B` 에서 기계적으로 끊으면 안 된다.
- `0x184A0C..0x184AD3` 은 현재 `10 * 0x14` effect/overlay parameter table 후보로 보는 해석이 가장 강하다.
- `0x06CFB8` 계열 함수는 `0x03002FFC == 0x10` 일 때 `0x03005FF8` byte 를 index 로 써서 `0x184A0C + index * 0x14` row 를 읽고, `5`개 word 를 helper `0x047A88` 로 넘긴다.
- `0x047A88` 의 다른 caller (`0x051E96`, `0x051FFE`) 도 구조체 필드를 같은 helper 로 넘기므로, `0x184A0C` table 은 텍스트나 포인터 배열이 아니라 정적 effect/overlay spawn parameter table 로 보는 편이 맞다.
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
- 그리고 `0x184220` tail 은 단순한 문자열 꼬리가 아니라, `order table + location record table + hotspot lookup + route path matrix + node/handler bundle` 까지 이어지는 구조다.
- 여기에 더해, 상위 소비 단위도 개별 table 하나보다 `static constant cluster + runtime global` 묶음일 가능성이 커졌다.
- 특히 `0x184888` 경로는 opcode script 보다 `13-node` 기반 path matrix 로 보는 해석이 더 강하다.
- `0x184420` 은 path edge table 이 아니라 hit-test / hotspot id -> location index lookup table 로 보는 편이 맞다.
- `0x1849D4` 는 단순 숫자쌍이 아니라 location index -> special event/script/message id 매핑으로 읽는 편이 맞다.
- 따라서 이제 미해결점은 "`field3` exact palette/subtype 의미", "`0x1849A0` singular cluster slot 소비 경로", "`0x03005FF8` effect index 선택 경로", "`0x47EB0` / `0x561D4` helper 의미" 쪽으로 더 좁아졌다.

## 근거 문서

- [analysis/initial_findings.md](/Users/user/test/analysis/initial_findings.md)
- [analysis/text_bank_inventory.md](/Users/user/test/analysis/text_bank_inventory.md)

## 다음 할 일

1. `field3` exact palette/subtype 의미 확인
2. `0x1849A0` handler table singular cluster slot 소비 경로 찾기
3. `0x03005FF8` effect/overlay table index 선택 경로 확인
4. `0x47EB0` / `0x561D4` helper 의미 추가 분리
5. 왜 `0x17C1C0` 이 상위 허브와 다른 레이아웃을 유지하는지 설명할 구조 찾기
6. 겹치는 엔트리의 관계를 부모/자식/메타데이터 관점에서 분류
7. `0x3D2036` 전투 기술 뱅크 참조 방식 확인
8. `0x3D327E` 대형 능력 뱅크 참조 방식 확인
9. 폰트 조사에 들어가기 전 텍스트 뱅크 유형 분류 확정

## 진행 로그

- 세부 실험 이력은 [experiment_log.md](/Users/user/test/analysis/experiment_log.md) 를 본다.
- 이 문서는 활성 트랙 문서이므로, 중복 로그보다 **현재 구조 해석과 다음 질문** 위주로 유지한다.
