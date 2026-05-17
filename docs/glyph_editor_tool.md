# Glyph Editor Tool

startup intro 같은 `12x12` binary glyph 를 직접 고치기 위한 간단한 로컬 도구다.

## 실행

```bash
python3 scripts/run_glyph_editor.py \
  --manifest analysis/startup_intro_active_workbench/prepared_manifest.json
```

기본 주소:

```text
http://127.0.0.1:8765
```

## 기능

- manifest 안 glyph 목록 탐색
- `0 / 34` binary 픽셀 편집
- draw / erase 토글
- undo / redo
- clear / invert
- 상하좌우 1픽셀 shift
- 현재 glyph 를 `.pgm` 파일에 바로 저장
- active startup intro workbench 를 열었을 때는 `Save + Rebuild ROM` 으로 바로 [hnr_startup_intro_test.gba](/Users/user/test/patched_roms/startup_intro_active/hnr_startup_intro_test.gba) 재생성

## 단축키

- `D`: Draw
- `E`: Erase
- `Cmd/Ctrl + Z`: Undo
- `Cmd/Ctrl + Shift + Z` 또는 `Cmd/Ctrl + Y`: Redo
- `Cmd/Ctrl + S`: Save PGM
- `Cmd/Ctrl + Enter`: Save + Rebuild ROM
- `[` / `]`: 이전 / 다음 glyph
- `C`: Clear
- `I`: Invert
- `Arrow`: 1픽셀 shift

## 의도

- 자동 렌더링으로 1차 seed 를 만든 뒤
- 사람이 읽기 어려운 자소를 직접 다듬고
- 다시 startup intro ROM 을 빌드하는 루프를 빠르게 돌리기 위한 도구다.
- 기본 manifest 는 [startup_intro_active_workbench](/Users/user/test/analysis/startup_intro_active_workbench) 를 연다.
- 현재 이 active workbench 는 **사용자가 확정한 12x12 비트맵 atlas** 기준으로 생성된다.
- 예전 D2Coding / Galmuri / SourceHan 비교 경로는 [analysis/archive/font_trials/2026-05-17_pre_bitmap_lock](/Users/user/test/analysis/archive/font_trials/2026-05-17_pre_bitmap_lock) 로 내렸다.

## 다음 단계

glyph 수정 뒤에는 아래 명령으로 바로 다시 확인한다.

```bash
zsh scripts/build_startup_intro_test.sh \
  "Hagane no Renkinjutsushi - Meisou no Rondo (Japan).gba" \
  patched_roms/startup_intro_active
```

기본 실행은 매번 아래 경로를 **덮어쓴다**.

- workbench: [startup_intro_active_workbench](/Users/user/test/analysis/startup_intro_active_workbench)
- ROM output: `/Users/user/test/patched_roms/startup_intro_active/`

전체 active workbench 를 atlas 기준으로 다시 만들고 싶을 때는:

```bash
zsh scripts/rebuild_active_workbenches_from_atlas.sh
```
