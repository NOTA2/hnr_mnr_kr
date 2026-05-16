# Font Candidate Survey

2026-05-16 기준 startup intro `12x12` 한글 시드용 폰트 후보 정리.

## 결론

- 현재 문제의 핵심은 `NanumSquareR` 자체보다, **일반 벡터 UI 폰트를 12x12 GBA glyph 로 자동 축소/이진화하는 방식** 이다.
- 그래서 같은 방식으로 threshold 만 계속 조절하면 잡티는 줄어도 자소 구조가 쉽게 무너진다.
- 다음 우선순위는:
  1. **픽셀/비트맵 계열 한글 폰트**
  2. 그다음이 **작은 크기 힌팅이 강한 고정폭 폰트**

## 외부 조사

- [Galmuri](https://github.com/quiple/galmuri)
  - 공식 설명: Nintendo DS 계열 디자인을 바탕으로 한 비트맵 폰트.
  - Hangul glyph 를 포함한 bitmap 계열이라 현재 GBA `12x12` 실험과 가장 결이 가깝다.
- [Neo둥근모](https://github.com/neodgm/neodgm)
  - 공식 설명: 오래된 한국어 bitmap font 를 기반으로 한 TrueType font.
  - 다만 공식 가이드에서 **16px 배수 사용** 을 강하게 권장하므로, `12x12` 자동 축소에는 그대로 맞지 않을 수 있다.
- [D2Coding](https://github.com/naver/d2codingfont)
  - 공식 설명: 작은 크기 `8~18pt` 가독성과 힌팅을 고려한 고정폭 폰트.
  - bitmap 은 아니지만, 현재 로컬에 있고 작은 크기 대응이 비교적 낫다.

## 현재 로컬 후보

- `NanumSquareR.ttf`
- `NanumGothic.ttf`
- `NanumBarunGothic.ttf`
- `NanumSquareRoundR.ttf`
- `AppleSDGothicNeo.ttc`
- `D2Coding-Ver1.3.2-20180524.ttf`

## 로컬 비교 메모

- binary threshold 실험 기준, `NanumSquareR` 는 잡티를 없애면 자소 내부가 쉽게 무너진다.
- `AppleSDGothicNeo` 는 지나치게 얇아져서 정보량이 부족해진다.
- `D2Coding` 은 적어도 작은 크기에서 획이 완전히 붕괴하는 정도는 덜하다.
- 비교 시트: [startup_font_candidate_binary2_sheet.png](/Users/user/test/analysis/startup_font_candidate_binary2_sheet.png)

## 현재 판단

- **장기적으로는 Galmuri 같은 bitmap/pixel 계열 폰트로 전환** 하는 편이 가장 맞다.
- 다운로드 없이 바로 계속 가야 한다면, 로컬 후보 중에서는 **D2Coding** 이 다음 실험 후보로 가장 현실적이다.
- 어떤 폰트를 쓰더라도, 최종 단계에서는 자동 렌더링만으로 끝내지 말고 `PGM` 단위 수동 보정이 필요하다.
