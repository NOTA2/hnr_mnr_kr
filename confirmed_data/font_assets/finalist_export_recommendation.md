# Finalist Bitmap Export Recommendation

현재 최종 후보군은 아래 3개다.

- `MaruMinyaHangul (12px)`
- `Galmuri11 (12px)`
- `GalmuriMono (12px)`

## 추천 문자 집합

현재 파이프라인 기준으로 가장 추천하는 preset 은:

- `한글 음절 -> 11,172자`

이유:

1. 지금 프로젝트는 **새 한글 glyph 만 unused code 에 추가**하는 방식이다.
2. 숫자/영문/기본 기호는 우선 **원본 게임 공통 폰트**를 그대로 재사용한다.
3. 따라서 새 후보 PNG 에서 반드시 필요한 것은 `U+AC00..U+D7A3` 완성형 `11172`자다.
4. 이 순서는 row-major `가..힣` atlas 로 바로 importer 에 넣기 가장 쉽다.

## 이 preset 을 1순위로 쓰는 조건

- 세 후보 모두 같은 generator/export 조건으로 bitmap PNG 를 뽑을 수 있을 때
- `12x12`, `64`열, row-major 순서를 맞출 수 있을 때

## 추가 권장 설정

- 타일 크기: `12x12`
- 열 수: `64`
- 안티앨리어싱 없는 흰 글자 / 검은 배경
- 확대/축소 없이 원본 픽셀 그대로
- 글자 순서: row-major

## 더 필요한 파일

현재 프로젝트 안에서 바로 쓸 수 있는 것은 `MaruMinyaHangul` atlas 뿐이다.

추가로 필요:

- `third_party/font_atlases/finalists/galmuri11_12x12.png`
- `third_party/font_atlases/finalists/galmurimono12_12x12.png`

## 숫자/기호를 같은 스타일로 바꾸고 싶을 때

1차 한글화에는 필수가 아니지만, 나중에 숫자/기호까지 같은 계열로 맞추고 싶다면 **보조 atlas** 를 하나 더 만들면 된다.

그때는 custom charset 로 아래 정도를 별도 추출하면 충분하다.

- 숫자 `0-9`
- 공백
- 기본 기호 `! ? . , … : ; / - + % ( )`
- 필요 시 `A-Z`, `a-z`

## custom charset 가 필요한 경우

만약 generator 에서 위 preset 이 문제를 일으키면, fallback 으로 custom charset 를 쓸 수 있다.

이 경우 최소 기준은:

- 현재 번역에 실제로 쓰인 한글
- 필요 시 숫자/공백/기호 보조 세트

현재 번역 기준 비한글 문자 리포트는 아래 파일을 본다.

- [current_translation_charset_report.json](/Users/user/test/confirmed_data/font_assets/current_translation_charset_report.json)
- [current_translation_charset_non_hangul.txt](/Users/user/test/confirmed_data/font_assets/current_translation_charset_non_hangul.txt)
