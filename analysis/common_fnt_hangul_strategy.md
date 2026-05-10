# Common FNT Hangul Strategy

공통 `fnt` payload (`0x3E0000`) 에 대한 한글 삽입 전략 메모.

근거 데이터셋:

- [common_fnt_manifest.json](/Users/user/test/analysis/common_fnt_manifest.json)
- [common_fnt_usage_audit.json](/Users/user/test/analysis/common_fnt_usage_audit.json)

## 핵심 결론

- lookup table 쪽은 이미 `0x0000..0xFFFF` 전체 코드 공간을 덮는다.
- 따라서 **새 문자 코드 포인트를 추가하는 것 자체는 어렵지 않다.**
- 하지만 glyph 쪽은 `glyph_index 1..1698` 이 **빈칸 없이 전부 차 있다.**
- 공통 payload 길이 `0x3DDE8` 기준 `tail_free_bytes = 0` 이다.
- 즉, **현재 payload 안에 한글 글리프를 그대로 추가할 빈칸은 없다.**

## 현재 추출본 기준 사용량

- 현재 감사에 사용한 추출 텍스트 총 문자 수: `105707`
- 현재 추출본에서 실제로 쓰인 mapped code: `1411`
- mapped 상태지만 현재 추출본에서 안 쓰인 code: `287`
- rare used (`<= 2회`) mapped code: `394`

중요:

- 여기서 `unused 287` 은 "현재까지 추출된 텍스트 기준"이다.
- 즉 완전한 전역 unused 라고 단정하면 안 된다.
- 특히 숫자/기호/알파벳은 미추출 UI 나 이미지성 표기에서 다시 나올 수 있으므로 우선 재활용 후보로 삼지 않는 편이 안전하다.

## 재활용 후보 분포

현재 `unused 287` 의 대략적인 분포:

- ASCII single-byte: `11`
- fullwidth punctuation/symbol: `9`
- hiragana: `3`
- katakana: `4`
- kanji plane: `198`
- user area (`0xE000..`): `6`

따라서 **가장 현실적인 1차 재활용 후보는 희귀 한자와 user area glyph** 다.

## decoder 가 실제로 받을 수 있는 새 코드 공간

공통 text renderer `0x014ED0` 는 현재:

- `0x81..0x9F`
- `0xE0..0xEF`

를 Shift-JIS 2바이트 lead byte 로 처리한다.

즉 한글용 새 코드 포인트도 이 lead-byte 공간 안에서 잡는 것이 안전하다.

현재 mapped 되지 않은 free code 는 decoder 허용 공간 안에만도 `7337`개가 있다.

대표적인 큰 free block:

- `0x8440..0x84FF` (`192`)
- `0x8540..0x85FF` (`192`)
- `0x8640..0x86FF` (`192`)
- `0xE940..0xE9FF` (`192`)
- `0xEA40..0xEAFF` (`192`)
- `0xEB40..0xEBFF` (`192`)
- `0xEC40..0xECFF` (`192`)
- `0xED40..0xEDFF` (`192`)
- `0xEE40..0xEEFF` (`192`)
- `0xEF40..0xEFFF` (`192`)

결론적으로 **코드 포인트 부족은 문제가 아니고, glyph 저장 공간 부족이 진짜 병목** 이다.

## 한글화 관점의 의미

### 치환-only 전략

- 현재 mapped glyph 중 안 쓰이는 `287`개만 재활용하는 전략
- 장점:
  - payload 확장 없이도 시도 가능
  - 첫 UI/짧은 메뉴/개념 검증에는 유용할 수 있음
- 한계:
  - full-game 한국어에는 보통 너무 적다
  - 번역문이 제한된 syllable inventory 안에 들어와야 한다

### 확장/재배치 전략

- 공통 `fnt` payload 를 더 큰 자유 공간으로 옮기거나 ROM 뒤에 확장
- glyph data 를 추가하고 registry pointer/length 를 갱신
- lookup table 의 zero slot 에 한글 code -> 새 glyph index 를 기록
- 장점:
  - 전체 한글화에 필요한 글자 수를 현실적으로 확보 가능
- 현재 판단:
  - **정식 한글화는 이 방향이 주력 전략이 될 가능성이 높다.**

## 바로 다음 권장 작업

1. 한글용 code range 를 decoder 허용 공간 안에서 1개 정한다.
권장 시작 후보: `0xE940..`
2. 공통 `fnt` payload 를 확장/재배치하는 patch 절차를 실행한다.
현재 [font_chunk_relocation_test.json](/Users/user/test/analysis/font_chunk_relocation_test.json) 기준으로, `relocate-chunk` 로 font entry `0` 을 `0x800000`, `len=0x42000` 로 옮기는 실험은 성공했다.
3. 단, 이때는 `0x17C2F4` entry `0` 만 바꾸면 끝이 아니라, 같은 entry 를 담은 mirror table `0x1823A0` 도 함께 갱신해야 한다.
4. 최소 `10~20` 글자 정도의 테스트용 한글 glyph 를 붙여 첫 표시 실험을 한다.
5. 그 뒤에 실제 번역문에서 필요한 glyph inventory 규모를 계산한다.

## 재배치 실험에서 확인된 점

- `relocate-chunk` 로 공통 font payload 를 ROM 끝 `0x800000` 으로 복사하고 길이를 `0x42000` 으로 늘린 테스트 ROM 을 만들 수 있다.
- 이 테스트 ROM 은 `inspect-fnt 0x800000` 기준으로 여전히 정상 `fnt` payload 로 읽힌다.
- 원본 `0x083E0000` direct word hit 는 `3`개였고:
  - `0x17C2F4`: 상위 registry table entry
  - `0x1823A0`: 같은 pointer-length 엔트리의 mirror table
  - `0x51B1A0`: 현재는 코드보다 raw data 성격이 강한 잔여 hit
- 따라서 실제 patch 경로에서는 최소한 **registry entry + mirror table** 동시 갱신을 기본 규칙으로 삼아야 한다.

## append 실험에서 확인된 점

- `append-fnt-glyph` 로 확장된 `fnt` payload 끝에 **새 glyph slot을 append** 하고, free code 에 새 lookup mapping 을 넣는 실험도 성공했다.
- 테스트:
  - payload: `0x800000`
  - payload length: `0x42000`
  - target code: `0xE940`
  - source glyph: `0x93FA ('日')`
- 결과:
  - 새 glyph index `0x06A3`
  - 새 glyph offset `0x83DDE8`
  - `0xE940 -> 0x06A3` lookup 기록 성공
  - 새 glyph bytes 는 source glyph 와 동일함
  - `inspect-fnt` 기준 nonzero mapping 도 `1698 -> 1699` 로 증가
- 즉, 지금은 **재배치된 payload 위에 새 code/glyph 를 실제로 추가하는 경로까지 검증된 상태** 다.

이제 남은 핵심은 "기존 일본어 glyph 복제"가 아니라 **실제 한글 glyph bitmap 을 넣는 단계** 다.
