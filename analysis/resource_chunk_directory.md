# Resource Chunk Directory

초기에는 이 영역을 단순한 "청크 디렉터리"로 보았지만, 현재는 `0x17C1C0` 부근의 8바이트 엔트리 집합을 **겹치는 리소스 디스크립터 테이블**로 보는 편이 더 정확하다.

근거 산출물:

- [resource_chunks.json](/Users/user/test/analysis/resource_chunks.json)

## 확인 방법

아래 명령으로 테이블을 다시 점검할 수 있다.

```bash
python3 -m gba_kor_tool inspect-chunk-table \
  "Hagane no Renkinjutsushi - Meisou no Rondo (Japan).gba" \
  0x17C1C0 \
  --count 35 \
  --scan-text \
  --encoding cp932 \
  --terminator 00 \
  --require-japanese \
  --output analysis/resource_chunks.json
```

자동 판정 결과:

- `length-pointer`: `score=175`, `valid=35`
- `pointer-length`: `score=0`, `valid=0`

즉, 현재 확인된 레이아웃은 아래와 같다.

- `u32 length`
- `u32 rom_address`

## 현재 중요한 텍스트성 엔트리

| Index | Table Offset | File Range | Length | Text Hits | 메모 |
| --- | --- | --- | --- | --- | --- |
| 4 | `0x17C1E0` | `0x3D0E38..0x3D20E7` | `0x12B0` | `6` | 전투 관련 텍스트가 일부 포함된 상위 엔트리 |
| 7 | `0x17C1F8` | `0x3D1A88..0x3D268D` | `0x0C06` | `58` | 전투 텍스트가 밀집된 엔트리 |
| 17 | `0x17C248` | `0x3D2D60..0x3D307F` | `0x0320` | `13` | 재료/속성 텍스트 일부 포함 |
| 18 | `0x17C250` | `0x3D3420..0x3D3ADF` | `0x06C0` | `39` | 능력/기술 설명 계열 엔트리 |
| 19 | `0x17C258` | `0x3D3F98..0x3D4B0C` | `0x0B75` | `94` | 능력/기술 설명 계열 엔트리 |
| 20 | `0x17C260` | `0x3D4B14..0x3D568E` | `0x0B7B` | `92` | 능력/기술 설명 계열 엔트리 |
| 21 | `0x17C268` | `0x3D56D4..0x3D6291` | `0x0BBE` | `96` | 능력/기술 설명 계열 엔트리 |

## 핵심 해석

- 이 테이블은 `포인터 + 길이`가 아니라 `길이 + ROM 주소` 순서로 읽혀야 한다.
- 엔트리들은 주소 기준으로 대체로 오름차순이지만, 서로 **겹치거나 중첩**된다.
- 따라서 이 구조를 단순한 "겹치지 않는 청크 분할표"로 보면 안 된다.
- 현재 추출된 [battle_texts.json](/Users/user/test/analysis/battle_texts.json), [material_texts.json](/Users/user/test/analysis/material_texts.json), [ability_texts.json](/Users/user/test/analysis/ability_texts.json) 은 번역 작업을 위한 편의상 뽑은 범위이며, 테이블 엔트리와 1:1 대응하지 않는다.
- 특히 `battle_texts.json` 은 `0x3D2036..0x3D2557` 만 모아 둔 보기 쉬운 추출본이지, 단일 디스크립터 하나를 그대로 덤프한 결과가 아니다.

## 추가 관찰

- `index 5`, `8`, `10`, `12`, `13`, `16`, `22`, `23`, `24` 같은 엔트리는 이전 엔트리와 겹친다.
- 넓은 범위로 테이블을 더 스캔하면 이후 엔트리에서도 텍스트 히트가 나오지만, 큰 바이너리 자원 내부의 잡음이 섞이기 시작한다.
- 따라서 현재는 `0x3Dxxxx` 근처의 밀집 구간을 우선 조사 대상으로 유지하는 편이 안전하다.

## 아직 모르는 것

- 이 디스크립터 테이블을 어떤 코드나 상위 구조가 참조하는지
- 겹치는 엔트리가 부모/자식 관계인지, 다른 뷰인지, 메타데이터 분리인지
- 테이블 인덱스와 실제 게임 메뉴/전투 시스템 데이터가 어떻게 연결되는지
