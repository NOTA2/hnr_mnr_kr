# Finalist Font Atlases

이 폴더는 최종 후보군 `3`개의 `12x12` bitmap atlas PNG 를 놓는 위치다.

## 기대 파일명

- `galmuri11_12x12.png`
- `galmurimono12_12x12.png`

현재 `MaruMinyaHangul` 은 이미:

- [maruminyahangul_12x12.png](/Users/user/test/third_party/font_atlases/maruminyahangul_12x12.png)

에 있다.

## 권장 export 설정

- 문자 집합: `한글 음절 -> 11,172자`
- 타일 크기: `12x12`
- 열 수: `64`
- 안티앨리어싱 없음
- 검은 배경, 흰 글자
- row-major 순서

## 왜 한글만 먼저 뽑는가

- 현재 프로젝트는 새 후보 atlas 에서 **한글 glyph 만 추출**한다.
- 숫자/영문/기본 기호는 원본 게임 폰트를 그대로 재사용한다.
- 따라서 후보 비교 1차에서는 `가..힣` 완성형 atlas 만 있으면 충분하다.
