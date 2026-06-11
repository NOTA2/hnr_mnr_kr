# HNR MNR Korean Patch v0.1.0

이 배포물은 GBA 게임 `Hagane no Renkinjutsushi - Meisou no Rondo (Japan)`의
한국어 패치입니다. 1차 검수 완료본을 기준으로 제작했습니다.

원본 또는 패치 완료된 `.gba` 파일은 포함하지 않습니다. 사용자는 본인이 소유한
정상적인 일본판 원본 ROM에 `.bps` 패치를 직접 적용해야 합니다.

## 포함 파일

- `hnr_mnr_ko_v0.1.0.bps`: BPS 패치 파일
- `checksums.sha256`: 원본/패치/적용 결과 검증용 SHA256
- `NOTICE.txt`: 폰트 및 배포 고지
- `LICENSES/Galmuri_OFL_1.1.txt`: Galmuri 폰트 라이선스

## 필요한 원본 ROM

- 파일: `Hagane no Renkinjutsushi - Meisou no Rondo (Japan).gba`
- 크기: `8388608` bytes
- SHA256:
  `49df5e9e128302733fb1465104153923a4a5c0ef36efd8b77a0006bbc0a629d8`

파일명은 달라도 되지만, SHA256이 위 값과 같은 깨끗한 일본판 원본 ROM을
사용해야 합니다.

## Windows 패치 방법

1. Floating IPS/FLIPS를 실행합니다.
2. `Apply Patch`를 선택합니다.
3. `hnr_mnr_ko_v0.1.0.bps`를 선택합니다.
4. 본인이 가진 일본판 원본 `.gba`를 선택합니다.
5. 새 `.gba` 파일 이름을 정해 저장합니다.
6. 생성된 `.gba`를 mGBA 같은 에뮬레이터에서 실행합니다.

브라우저에서 적용하려면 RomPatcher.js/RomPatcher.app에서도 BPS 패치를 적용할 수
있습니다. 이 경우에도 원본 ROM 파일은 사용자가 직접 선택해야 합니다.

## 적용 결과 검증값

패치 적용 후 생성되는 ROM의 SHA256은 아래와 같아야 합니다.

`c22a2922f25fcf7b10d435f161fe22cd2cd24894e64b2a08818c4ef72cdd2f6d`

## 주의

- 이 패치는 무료 배포용입니다.
- 원본 게임 ROM 또는 패치가 적용된 ROM을 공유하지 마세요.
- 게임 원저작권은 원 권리자에게 있습니다.
- 이 패치에는 Galmuri에서 파생한 비트맵 글리프 데이터가 포함되어 있습니다.
