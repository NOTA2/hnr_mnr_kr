# Current Constraints

이 문서는 **지금 시점에 꼭 기억해야 하는 사실, 금지 가정, 미해결점**만 짧게 모은 작업용 요약이다.

전체 이력은 [experiment_log.md](/Users/user/test/analysis/experiment_log.md) 에 남긴다.

## 지금 확실한 사실

1. 일부 문자열은 `cp932 + 00` 평문이다.
2. 일부 메뉴/진행 메시지는 명령 스트림 내부 `cp932` 문자열이며 `0x10` 구분자를 쓴다.
3. `0x18425C` 지역명 뱅크는 절대 포인터가 확인됐다.
4. `0x3D2036` 전투 뱅크와 `0x3D327E` 능력 뱅크는 일반 절대 포인터가 바로 안 잡힌다.
5. `0x17C1C0` 테이블은 `length-pointer` 이고, 엔트리들이 서로 겹친다.
6. `0x076530` 부근에는 여러 상위 레지스트리 경계를 가리키는 포인터 허브가 있다.
7. `0x17C2F4`, `0x17C384`, `0x17C71C`, `0x17C7E4` 이후 상위 레지스트리들은 `pointer-length` 쪽이 맞다.
8. `0x17785C` 레지스트리에는 실제 Thumb accessor `0x03BC`, `0x0414` 가 있다.
9. `0x17CE0` 는 `base + 2 * (x + y * 32)` 목적지 주소를 계산한다.
10. `0x17EB4` / `0x017ED8` / `0x017EEC` 는 `0x17785C` 포인터/길이 엔트리를 DMA3 로 halfword 복사한다.
11. `0x03E8` helper 는 literal base `0x17C7E4` 를 사용하고, 현재 BL 호출자 `3`개 (`0x0106E6`, `0x010798`, `0x010892`) 가 확인되었다.
12. `0x007760` 단독 accessor 경로는 고정 index `0x093D` (`0x3D2A40`, 길이 `0x0320`) binary table 을 읽는다.
13. `0x007824` 단독 accessor 경로는 고정 index `0x093E` (`0x3D2D60`, 길이 `0x06C0`) 를 읽으며, 앞쪽 `7-byte` 레코드와 뒤쪽 `cp932` 문자열 영역을 함께 쓴다.
14. `0x007578` 단독 accessor 경로는 고정 index `0x094B` (`0x3DDB30`, 길이 `0x02C3`) binary table 을 읽으며 직접 평문 텍스트 경로는 아니다.
15. `0x0002C0` 의 `0x076530` 포인터는 `0x000290` helper 의 literal 이며, 이 helper 는 허브 첫 4엔트리 (`0x17785C`, `0x17C2F4`, `0x17C384`, `0x17C71C`) 중 하나를 선택해 반환한다.
16. `0x0002CC` / `0x000304` 는 `0x000290` 위에 쌓인 generic accessor 로, 선택된 registry 엔트리의 `pointer` / `length` 필드를 읽는다.
17. `0x17C7E4` 는 허브 안에 있으나 generic `0x000290` family 가 선택하는 첫 4엔트리에는 포함되지 않고, 별도 direct helper 계열로 관리되는 것으로 보인다.
18. direct `0x0002CC` 호출 `20`개 중 현재 고정 selector 로 확인된 값은 `1` 과 `3` 뿐이다.
19. `selector=1` direct 호출 `8`개는 모두 `entry_index=0` 으로 `Registry A (0x17C2F4)` 첫 엔트리를 읽는다.
20. `selector=3` direct 호출 `11`개는 `entry_index 0/2/3/5` 를 읽으며, `0x06F4xx` / `0x0704xx` / `0x0709xx` 군집으로 몰려 있다.
21. `0x000304` 의 유일한 BL 호출자는 `0x000392` 이며, 이는 `0x00033C` wrapper 내부 길이 조회다.
22. `0x00033C` 호출자 `6`개는 현재 모두 `selector=3` 을 넘긴다.
23. `selector=0` direct generic caller 부재는 `0x17785C` 전용 helper (`0x03BC`, `0x0414`) 가 이미 널리 쓰인다는 점으로 설명 가능하다.
24. `Registry B (0x17C384)` 의 `115`개 엔트리는 `0x183D50` 에 완전히 같은 `pointer-length` 미러 테이블로 한 번 더 저장되어 있다.
25. `0x183D50` 미러 테이블은 direct 포인터 참조 `22`개가 확인되며, 이는 `0x17C384` 의 허브 참조 `1`건보다 훨씬 강한 live access 근거다.
26. 공용 helper `0x068DF8` 는 `0x183D50 + index * 8` 엔트리를 읽고, 선두 2바이트가 `ZP` 인지 검사해 decode 또는 raw fallback 으로 분기한다.
27. `0x068DF8` BL 호출자는 현재 `38`개다.
28. `0x183D50` 미러 엔트리 중 `50 / 115`개가 `ZP00` 또는 `ZP01` 로 시작한다.
29. 따라서 `Registry B` 는 concrete access route 가 비어 있는 축이 아니라, **미러 테이블 + ZP-aware helper** 경로로 접근되는 mixed compressed/raw asset bank 로 보는 편이 맞다.
30. `0x068DF8` caller 들은 전부 같은 성격이 아니며, 고정 index 호출과 descriptor/global 기반 동적 index 호출이 섞여 있다.
31. `0x1840F8..0x1841E7` 구간은 `15 * 16-byte` companion descriptor 배열로 읽히며, 각 row 는 `destination_vram + registry_b_index + dim_a + dim_b` 패턴을 가진다.
32. `0x1841E8..0x18421F` 구간은 `7 * 8-byte` companion descriptor 배열로 읽히며, 각 row 는 `registry_b_index + destination_palette_ram` 패턴을 가진다.
33. `0x184220` 이후에는 다른 metadata 와 문자열이 섞이기 시작하므로, `0x1840E8..` 전체를 한 가지 uniform struct 로 다시 다루면 안 된다.
34. `0x184220..0x184244` 구간에는 `3, 4, 0, 2, 7, 9, 5, 1, 6, 8` 값의 `10-entry` permutation/order table 이 있다.
35. `0x184248..0x1843FF` 구간은 `10 * 0x2C` fixed-size location record table 이며, 각 row 는 `5 * u32 metadata + 0x18-byte name field` 구조로 읽힌다.
36. 기존 `0x18425C` 지역명 문자열은 독립 뱅크라기보다 첫 location record 의 name field (`record + 0x14`) 다.
37. `0x184248` record base direct ref 는 `12`개, `0x18425C` 첫 name field direct ref 는 `4`개가 확인되므로, 실제 소비 단위는 문자열보다 record table 쪽일 가능성이 높다.

## 지금 반복하면 안 되는 가정

1. 모든 텍스트 뱅크가 같은 구조라고 가정하지 않는다.
2. `0x17Cxxx` 주변 디스크립터가 모두 같은 레이아웃이라고 가정하지 않는다.
3. `text_hits > 0` 만으로 새 텍스트 뱅크라고 확정하지 않는다.
4. `0x17C1C0` 을 공통 상위 레지스트리의 메인 경로라고 단정하지 않는다.
5. `0x17C7E4` 도 `0x17785C` 와 같은 accessor 패턴일 거라고 가정하지 않는다.
6. `0x03BC` 단독 호출부가 곧바로 순수 문자열 포인터를 반환한다고 가정하지 않는다.
7. `0x076530` 허브의 모든 포인터가 같은 helper family 에서 직접 사용된다고 가정하지 않는다.
8. `0x0002CC` generic accessor 가 모든 registry selector 를 비슷한 빈도로 쓸 거라고 가정하지 않는다.
9. `0x1840E8..` 전체를 한 종류의 descriptor 배열이라고 가정하지 않는다.
10. `0x18425C` 지역명 구간을 순수 standalone string bank 라고 가정하지 않는다.

## 지금 가장 유력한 다음 질문

1. `0x184248` location record 의 `field0..field4` 는 각각 어떤 게임 의미를 가지는가
2. `0x08BFD0` / `0x08C060` / `0x08C1D0` descriptor bundle 은 `0x184248`, `0x1840F8`, `0x1841E8` 을 어떻게 묶는가
3. `0x093D` binary table 은 `0x093E` 재료 문자열 뱅크와 어떤 관계인가
4. `0x094B` / `0x12DF8(0x63)` 경로는 어떤 게임 데이터 분류를 읽는가

## 문서 사용 규칙

- 작업 시작 전에는 이 문서만 읽고, 필요한 경우에만 전체 실험 로그를 연다.
- 새 사실이 안정적으로 검증되면 이 문서를 먼저 갱신하고, 그 다음 전체 실험 로그를 갱신한다.
