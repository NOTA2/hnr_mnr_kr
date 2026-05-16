# Glyph Editor Tool

startup intro 같은 `12x12` binary glyph 를 직접 고치기 위한 간단한 로컬 도구다.

## 실행

```bash
python3 scripts/run_glyph_editor.py \
  --manifest analysis/startup_intro_d2coding_workbench/prepared_manifest.json
```

기본 주소:

```text
http://127.0.0.1:8765
```

## 기능

- manifest 안 glyph 목록 탐색
- `0 / 34` binary 픽셀 편집
- draw / erase
- clear / invert
- 상하좌우 1픽셀 shift
- 현재 glyph 를 `.pgm` 파일에 바로 저장

## 의도

- 자동 렌더링으로 1차 seed 를 만든 뒤
- 사람이 읽기 어려운 자소를 직접 다듬고
- 다시 startup intro ROM 을 빌드하는 루프를 빠르게 돌리기 위한 도구다.

## 다음 단계

glyph 수정 뒤에는 아래 명령으로 바로 다시 확인한다.

```bash
python3 scripts/build_startup_intro_variant.py D2Coding 20
```

또는 active workbench 기준으로 바로 다시 확인한다.

```bash
zsh scripts/build_startup_intro_test.sh \
  "Hagane no Renkinjutsushi - Meisou no Rondo (Japan).gba" \
  patched_roms/rebuild_check
```
