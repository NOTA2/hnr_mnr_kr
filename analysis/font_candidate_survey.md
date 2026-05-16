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
- [laqieer/gba-free-fonts](https://github.com/laqieer/gba-free-fonts)
  - 공식 설명: GBA 개발에 바로 쓰는 `.fnt + atlas png` 폰트 모음.
  - `SourceHanSans/KR`, `SourceHanMono/KR` 는 한국어 glyph atlas 가 이미 있어, 현재 프로젝트의 `12x12 PGM workbench` 로 변환해 startup intro 비교 ROM 을 만들 수 있다.

## geminian 글 기준 재정리

- 참고 글: [쓸만한 무료 한글 픽셀 폰트들](https://geminian.tistory.com/33)
- 이 글은 현재 조건에 맞는 후보를 좁히는 데 도움이 된다.
- 특히 `Neo둥근모`, `PF스타더스트`, `갈무리`, `달무리`, `Silver`, `LanaPixel`, `램체`처럼 **원래부터 픽셀풍으로 설계된 폰트** 를 우선 후보로 두는 판단이 타당하다.
- 반대로 `굴림체` 같은 일반 시스템 폰트는 익숙한 모양이라는 장점이 있지만, 자동 축소 + 이진화만으로는 픽셀 폰트보다 결과 편차가 크다.

## 다음 후보 우선순위

1. `LanaPixel`
   - 글 기준 `9x9` 소형 다국어 픽셀 폰트라 현재 startup intro `12x12` 와 잘 맞을 가능성이 높다.
   - 지금은 원본 파일만 확보되면 즉시 비교 가능한 상태다.
2. `Silver`
   - 글 기준 얇은 다국어 픽셀 폰트라 일본어/한글 혼용 환경에도 유리할 수 있다.
3. `Neo둥근모`
   - 한글 픽셀 폰트로 매우 안정적이지만, `12x12` 로 줄였을 때 밀도를 따로 확인해야 한다.
4. `PF스타더스트`
   - 얇고 깔끔한 계열이라 작은 UI 테스트용으로 가치가 있다.
5. `굴림체`
   - 픽셀 폰트는 아니지만, 사용자가 형태를 선호하면 **수동 보정 전제 후보** 로는 충분히 시험할 가치가 있다.

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
- 실제 startup intro 비교 결과는 [startup_intro_font_compare.md](/Users/user/test/analysis/startup_intro_font_compare.md), [startup_intro_font_compare_sheet.png](/Users/user/test/analysis/startup_intro_font_compare_sheet.png) 를 본다.
- 반복 비교는 [startup_font_compare_candidates.json](/Users/user/test/analysis/startup_intro_font_compare_candidates.json) 과 [build_startup_font_compare.py](/Users/user/test/scripts/build_startup_font_compare.py) 조합으로 다시 만들 수 있다.

## 현재 판단

- 현재 startup intro active 실험축은 **`D2Coding-Ver1.3.2-20180524.ttf` `size11` `binary2 cutoff_ratio=0.2`** 이다.
- `Galmuri` 는 조사상 유망했지만, 현재 자동 렌더링 조건에서는 기대만큼 안정적이지 않아 보조 후보로 내렸다.
- `gba-free-fonts` 의 `SourceHanSansKR`, `SourceHanMonoKR` 는 **적용 가능** 하다. 다만 startup intro `12x12` binary 기준에서는 두 후보 모두 밀도가 높아 D2Coding 보다 더 뭉개져 보이는 편이다.
- `LanaPixel` 은 현재 기준으로 포맷 문제가 아니라 **원본 파일 확보 문제** 다. 파일만 얻으면 같은 workflow 에 넣을 수 있다.
- `굴림체` 는 현재 로컬에 없어 바로 시험하진 못했지만, [build_startup_intro_variant.py](/Users/user/test/scripts/build_startup_intro_variant.py) 의 `--font-path` 로 파일만 지정하면 즉시 비교 가능하다.
- 어떤 폰트를 쓰더라도, 최종 단계에서는 자동 렌더링만으로 끝내지 말고 `PGM` 단위 수동 보정이 필요하다.
