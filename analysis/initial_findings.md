# 초기 조사 메모

대상 ROM:

- `Hagane no Renkinjutsushi - Meisou no Rondo (Japan).gba`

## 확인된 점

- ROM 헤더 제목은 `HAGANERONDO`
- 일부 문자열은 `cp932` + `00` 종료 형태로 평문 저장되어 있음
- 따라서 이 게임은 최소한 일부 영역에서 직접 추출/번역/재삽입이 가능함

## 추출된 구간

### 시스템 메시지

- 범위: `0x088540` ~ `0x088620`
- 산출물: [system_messages.json](/Users/user/test/analysis/system_messages.json)

예시:

- `0x088558`: `通信中・・・`
- `0x088568`: `通信エラー！\nケーブルを確認してください`

### 아이템/이벤트 관련 문자열

- 범위: `0x08AEFC` ~ `0x08B400`
- 산출물: [item_texts.json](/Users/user/test/analysis/item_texts.json)

예시:

- `0x08AEFC`: `東方軍司令部で受け取った書類`
- `0x08AF70`: `アルの左足`
- `0x08AFC0`: `すべてのイベントをクリアした証`

### 맵/지역명 문자열

- 범위: `0x184248` ~ `0x1843FF` (`10 * 0x2C` fixed-size location record)
- 산출물: [location_texts.json](/Users/user/test/analysis/location_texts.json)
- 구조 산출물: [location_record_table.json](/Users/user/test/analysis/location_record_table.json)

예시:

- `0x18425C`: `セントラルシティ`
- `0x184338`: `オルヘンティノス城`
- `0x1843E8`: `クルス遺跡`

### 전투 기술명/설명 문자열

- 범위: `0x3D2036` ~ `0x3D2557`
- 산출물: [battle_texts.json](/Users/user/test/analysis/battle_texts.json)
- 현재 추출 수: `104`

예시:

- `0x3D2036`: `壁錬成`
- `0x3D203D`: `壁を錬成し　　　相手を攻撃`
- `0x3D2059`: `撃鉄靠掌`
- `0x3D2173`: `雷を纏わせた刀で敵を斬る`
- `0x3D2231`: `石像錬成`

### 대형 기술/능력 텍스트 뱅크

- 범위: `0x3D327E` ~ `0x3D6277`
- 산출물: [ability_texts.json](/Users/user/test/analysis/ability_texts.json)
- 현재 추출 수: `409`

예시:

- `0x3D327E`: `黒曜石　　　　　火山岩の一種`
- `0x3D329C`: `ブラックペーパー因縁がある黒い紙`
- `0x3D3835`: `エド式大砲`
- `0x3D3DC0`: `金色の輝きを放つ爆弾を錬成`

### 재료/속성 텍스트 뱅크

- 범위: `0x3D2D60` ~ `0x3D3420`
- 산출물: [material_texts.json](/Users/user/test/analysis/material_texts.json)
- 현재 추출 수: `43`

예시:

- `0x3D2EB6`: `チタン　　　　　軽くて硬い金属`
- `0x3D301E`: `ダイヤモンド　　地球上で一番硬い`
- `0x3D33C2`: `錬成できません　質量が７以上`

### UI 기술 텍스트 뱅크

- 범위: `0x08B62C` ~ `0x08B809`
- 산출물: [ui_skill_texts.json](/Users/user/test/analysis/ui_skill_texts.json)

예시:

- `0x08B62C`: `クロスダーツ`
- `0x08B668`: `目にもとまらぬ超高速の抜刀術`
- `0x08B7F4`: `壁を錬成し相手を攻撃`

## 확인한 포인터 예시

- `0x088558` 를 가리키는 포인터: `0x0885F4`
- `0x08AF70` 를 가리키는 포인터: `0x18328C`
- `0x08AF1C` 를 가리키는 포인터: `0x1832A4`
- `0x18425C` 를 가리키는 포인터: `0x06A574`, `0x06A9A8`, `0x08C06C`, `0x08C0C4`

## 추가 관찰

- `0x18425C` 지역명 문자열은 일반적인 GBA 절대 포인터가 실제로 확인되었다.
- 다만 이 구간은 순수 standalone string bank 가 아니라, `0x184248..0x1843FF` 의 `10 * 0x2C` fixed-size location record table 안쪽 name field 추출본으로 보는 편이 맞다.
- 각 location record 는 `5 * u32 metadata + 0x18-byte name field` 구조로 읽히며, 첫 name field 가 `0x18425C` 다.
- `0x184220..0x184244` 앞쪽에는 `3, 4, 0, 2, 7, 9, 5, 1, 6, 8` 값의 `10-entry` order table 도 붙어 있다.
- `0x184248` record base direct ref 는 `12`개, `0x18425C` first name field direct ref 는 `4`개가 확인되어, 실제 소비 단위는 문자열보다 record table 쪽일 가능성이 높다.
- `0x184420..0x1844AF` table 은 현재 `(hotspot_id, location_index)` lookup table 로 보는 해석이 가장 강하다.
- `0x06A1F8` 부근 루틴은 helper `0x561D4` 반환값과 이 table 첫 필드를 비교하고, 일치하면 둘째 필드를 current-location byte 로 기록한다.
- `0x1844B0..0x1847F7` 에는 `FF` 종료 경로 시퀀스가 밀집한 route region 이 있다.
- `0x184888` 에는 `10-entry` route block pointer table 이 있으며, 각 block 은 다시 `10-slot` pointer matrix 로 읽힌다.
- 각 block 은 자기 자신의 slot 하나만 `null` 이고, 나머지 `9`개 목적지 slot 은 route 시퀀스를 가진다.
- route 시퀀스는 `FF` 를 제외하면 현재 `0..12` 값만 사용하므로, opcode script 보다 `13-node` 기반 path matrix 로 보는 해석이 더 강하다.
- `0x184820` 의 `13 * (x, y)` node position pair table 후보는 location record `field1/field2` 와 거의 일치한다. (`8 / 10` 완전 일치)
- 코드 기준으로는 `field1/field2` 가 location icon / hotspot 사각형의 좌상단 좌표, `0x184820` 이 node/cursor anchor 좌표 쪽에 더 가깝다.
- `field0`, `field3`, `field4` 는 draw helper `0x63000` / `0x63424` 로 직접 전달되는 표시 파라미터다.
- 현재는 `field0 = asset/icon family ID 후보`, `field3 = draw subtype/mode 후보`, `field4 = graphic/tile-base variant 후보` 로 보는 해석이 가장 자연스럽다.
- `0x1849A0` 에는 `13-entry` Thumb handler pointer table, `0x1849D4` 에는 `7-entry` special pair table이 있다.
- `0x1849D4` 는 현재 `(location_index, special event/script/message id)` 매핑으로 보는 해석이 가장 강하다.
- 현재는 `0..9 = location node`, `0x0A..0x0C = connector / transit node`, `0x1849A0 = 13-node handler table` 로 보는 해석이 가장 자연스럽다.
- `0x3D2059` 와 `0x3D329C` 대형 텍스트 뱅크는 같은 방식의 절대 포인터가 바로 잡히지 않았다.
- 따라서 `0x3Dxxxx` 영역은 직접 포인터 대신 인덱스/구조체/상대 오프셋/압축 해제 후 참조 같은 별도 구조를 쓸 가능성이 있다.
- `0x08B62C` UI 기술 텍스트는 `0x3D2059` 전투 기술 텍스트와 일부 이름이 겹친다.
- 즉, 같은 개념의 문자열이 서로 다른 용도의 텍스트 뱅크에 중복 저장되어 있을 가능성이 높다.
- `0x3D2059` 와 `0x3D329C` 계열 문자열 내부에는 `0x0B` 제어 코드가 줄바꿈/문장 분리 용도로 섞여 있다.
- `0x3D2036` 전투 뱅크는 순차적인 `이름/설명` 0종단 문자열 목록에 가깝다.
- `0x3D327E` 능력 뱅크는 순차적인 `이름+0x0B+설명` 0종단 문자열 목록에 가깝다.
- 이 두 뱅크는 "문자열 하나당 포인터 하나"보다 "인덱스 기반 접근" 가능성이 더 높다.
- 전각 공백 `U+3000` 를 비정상 문자처럼 취급하던 추출 필터 때문에 일부 설명 문자열과 첫 레코드가 누락되고 있었다.
- `0x17C1C0` 부근에 `u32 length + u32 rom_address` 형식의 리소스 디스크립터 테이블이 존재한다.
- 이 테이블은 `pointer + length` 로 읽으면 전부 깨지지만, `length + pointer` 로 읽으면 최소 `35`개 엔트리가 연속으로 유효하다.
- 이 엔트리들은 단순한 비중첩 청크 분할표가 아니라 서로 겹치거나 중첩되는 리소스 디스크립터 묶음으로 보인다.
- `battle_texts.json`, `material_texts.json`, `ability_texts.json` 은 이 디스크립터 테이블의 범위를 사람이 보기 쉽게 재조합한 추출본이다.
- `0x076530` 부근에는 `0x17C2F4`, `0x17C384`, `0x17C71C`, `0x17C7E4` 를 가리키는 상위 포인터 허브가 존재한다.
- `0x076530` 허브는 `0x0002C0` literal 을 통해 `0x000290` helper 에서 직접 쓰이며, 이 helper 는 허브 첫 4엔트리 (`0x17785C`, `0x17C2F4`, `0x17C384`, `0x17C71C`) 중 하나를 선택해 반환한다.
- 그 위에 `0x0002CC` / `0x000304` generic accessor 가 존재하며, 선택된 registry 엔트리의 포인터/길이 필드를 읽는다.
- direct `0x0002CC` 호출 `20`개 중 현재 고정 selector 로 확인된 값은 `1` 과 `3` 뿐이다.
- `selector=1` direct 호출 `8`개는 모두 `entry_index=0` 으로 `Registry A (0x17C2F4)` 첫 엔트리를 읽는다.
- `selector=3` direct 호출 `11`개는 `entry_index 0/2/3/5` 를 읽으며, `0x06F4xx` / `0x0704xx` / `0x0709xx` 군집에 몰린다.
- `0x000304` 는 현재 `0x00033C` wrapper 내부에서만 확인된다.
- 이 상위 레지스트리 범위들은 공통적으로 `pointer-length` 레이아웃에 가깝고, `0x17C1C0` 테이블만 예외적으로 `length-pointer` 쪽이 맞는다.
- `0x17C7E4` 는 허브 안에 있으면서도 이 generic helper family 바깥에 남아 있고, 별도 direct helper `0x03E8` 계열로 다뤄진다.
- `0x03E8` BL 호출자는 `0x0106E6`, `0x010798`, `0x010892` 총 `3`개이며, helper 본체는 `0x17C7E4 + index * 8` 의 첫 `u32` 를 읽는 pointer accessor 로 보인다.
- 따라서 `0x17C1C0` 은 공통 레지스트리의 메인 경로라기보다 예외적인 보조 디스크립터 또는 하위 분해표일 가능성이 있다.
- `0x17785C` 레지스트리에는 실제 Thumb helper accessor (`0x03BC`, `0x0414`) 가 존재하며, 각각 포인터 필드와 길이 필드를 읽는 함수로 보인다.
- `0x03BC` 는 BL 호출자 `77`개, `0x0414` 는 `4`개가 확인되었다.
- 따라서 `selector=0` direct generic caller 부재는 `0x17785C` 전용 helper family 가 이미 널리 쓰인다는 점으로 설명 가능하다.
- `Registry B (0x17C384)` 의 `115`개 엔트리는 `0x183D50` 에 완전히 같은 `pointer-length` 미러 테이블로 한 번 더 저장되어 있다.
- `0x183D50` 에 대한 direct ref 는 `22`개가 확인되며, shared helper `0x068DF8` 는 `38`개 caller 를 가진다.
- `0x068DF8` 는 `0x183D50 + index * 8` 엔트리 선두의 `ZP` magic 을 검사해 decode helper 또는 raw fallback 으로 분기한다.
- 미러 엔트리 `50 / 115`개가 `ZP00` / `ZP01` 로 시작하므로, `Registry B` 는 mixed compressed/raw asset bank 로 보는 편이 맞다.
- `0x068DF8` caller 는 모두 같은 방식이 아니며, fixed index 호출과 descriptor/global 기반 동적 index 호출이 섞여 있다.
- `0x1840F8..0x1841E7` 구간에는 `15 * 16-byte` companion descriptor 배열이 있고, `destination_vram + registry_b_index + 2개 치수값` 패턴으로 읽힌다.
- `0x1841E8..0x18421F` 구간에는 `7 * 8-byte` palette companion descriptor 배열이 있고, `registry_b_index + destination_palette_ram` 패턴으로 읽힌다.
- 이 두 배열은 Registry B 미러 asset 을 VRAM / palette RAM 으로 배치하는 동반 metadata 로 보는 해석이 가장 자연스럽다.
- 반면 `0x184220` 이후에는 다른 metadata 와 문자열이 이어지므로, `0x1840E8..` 전체를 한 종류 구조로 취급하면 안 된다.
- `0x03BC` 단독 호출부 중 일부는 고정 index 로 특정 리소스 엔트리를 읽는다.
  - `0x093D -> 0x3D2A40` (`0x0320`, binary 4-byte record table)
  - `0x093E -> 0x3D2D60` (`0x06C0`, 재료 문자열 뱅크 + 앞단 7-byte record directory)
  - `0x094B -> 0x3DDB30` (`0x02C3`, binary table)
- `0x3D2D60` 재료 뱅크는 순수 문자열 묶음이 아니라, 앞쪽 `7-byte` 레코드 (`5바이트 메타데이터 + u16 상대 문자열 오프셋`) 와 뒤쪽 `cp932` 본문이 결합된 mixed resource 로 보인다.

## 다음 우선순위

1. `field3` exact subtype 과 `0x63000` / `0x63424` helper signature 를 더 분리한다.
2. `0x1849A0` handler table 과 `0x06A864` / `0x06D600` special overlay 흐름을 더 분리한다.
3. `0x093D` / `0x094B` binary table 이 어떤 게임 데이터 분류인지 확인한다.
4. 폰트 타일과 문자 폭 테이블을 찾아 한글 글리프 삽입 준비를 시작한다.
5. 수정된 추출본을 기준으로 번역 대상 JSON을 정리한다.
