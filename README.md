# GBA 한글화 작업용 툴킷

이 폴더에는 GBA ROM을 한글화하기 전에 필요한 조사 작업을 빠르게 진행할 수 있는 Python CLI를 넣었습니다.

현재 들어 있는 ROM:

- `Hagane no Renkinjutsushi - Meisou no Rondo (Japan).gba`

이 툴은 아직 특정 게임 전용 패처가 아니라, 아래 작업을 먼저 진행하기 위한 "작업대" 역할에 집중합니다.

- ROM 헤더 확인
- 문자열 후보 스캔
- 특정 범위 문자열 추출
- 특정 문자열 바이트 검색
- 포인터 위치 찾기
- 길이/포인터 기반 리소스 테이블 점검
- GBA LZ77 압축 블록 스캔
- 4bpp 타일 덤프
- 간단한 문자열 교체 / 리포인트 주입
- 번역 JSON 일괄 적용
- ROM 해킹용 `.tbl` 문자 테이블 사용

## 실행 방법

Python 3.9 이상에서 바로 실행할 수 있습니다.

```bash
python3 -m gba_kor_tool --help
```

ROM 정보 확인:

```bash
python3 -m gba_kor_tool info "Hagane no Renkinjutsushi - Meisou no Rondo (Japan).gba"
```

CP932(일본어 Windows 코드페이지) 기준으로 `00` 종료 문자열 후보를 찾기:

```bash
python3 -m gba_kor_tool scan-text \
  "Hagane no Renkinjutsushi - Meisou no Rondo (Japan).gba" \
  --encoding cp932 \
  --terminator 00 \
  --min-chars 4 \
  --require-japanese \
  --limit 100
```

`FF` 종료 문자열 후보를 찾기:

```bash
python3 -m gba_kor_tool scan-text \
  "Hagane no Renkinjutsushi - Meisou no Rondo (Japan).gba" \
  --encoding cp932 \
  --terminator FF \
  --min-chars 4 \
  --require-japanese \
  --limit 100
```

특정 ROM 구간을 번역용 JSON으로 추출:

```bash
python3 -m gba_kor_tool extract-range \
  "Hagane no Renkinjutsushi - Meisou no Rondo (Japan).gba" \
  0x08AEFC \
  0x08B400 \
  --encoding cp932 \
  --terminator 00 \
  --output analysis/item_texts.json
```

특정 일본어 문자열 검색:

```bash
python3 -m gba_kor_tool search-text \
  "Hagane no Renkinjutsushi - Meisou no Rondo (Japan).gba" \
  "セーブ" \
  --encoding cp932
```

문자열 오프셋을 가리키는 포인터 찾기:

```bash
python3 -m gba_kor_tool find-pointers \
  "Hagane no Renkinjutsushi - Meisou no Rondo (Japan).gba" \
  0x123456
```

특정 Thumb helper 함수를 BL로 호출하는 위치 찾기:

```bash
python3 -m gba_kor_tool find-thumb-bl \
  "Hagane no Renkinjutsushi - Meisou no Rondo (Japan).gba" \
  0x03BC \
  --output analysis/thumb_bl_to_03bc.json
```

LZ77 압축 블록 스캔:

```bash
python3 -m gba_kor_tool scan-lz77 \
  "Hagane no Renkinjutsushi - Meisou no Rondo (Japan).gba" \
  --limit 50
```

길이+포인터 또는 포인터+길이 형태의 8바이트 청크 테이블 점검:

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

폰트/타일 후보 영역을 4bpp 이미지로 덤프:

```bash
python3 -m gba_kor_tool dump-4bpp \
  "Hagane no Renkinjutsushi - Meisou no Rondo (Japan).gba" \
  0x400000 \
  --tiles 256 \
  --columns 16 \
  --output font_dump.pgm
```

같은 길이 이하의 문자열을 제자리 교체:

```bash
python3 -m gba_kor_tool replace-text \
  "Hagane no Renkinjutsushi - Meisou no Rondo (Japan).gba" \
  patched.gba \
  --offset 0x123456 \
  --text "TEST" \
  --encoding ascii \
  --max-bytes 8 \
  --terminator 00
```

자유 공간에 새 문자열을 넣고 포인터를 새 위치로 갱신:

```bash
python3 -m gba_kor_tool inject-text \
  "Hagane no Renkinjutsushi - Meisou no Rondo (Japan).gba" \
  patched.gba \
  --pointer 0x234560 \
  --text "TEST" \
  --encoding ascii \
  --search-free-space-from 0x700000 \
  --terminator 00
```

번역 JSON의 `translation` 값을 한 번에 반영:

```bash
python3 -m gba_kor_tool apply-translations \
  "Hagane no Renkinjutsushi - Meisou no Rondo (Japan).gba" \
  analysis/item_texts.json \
  patched.gba \
  --encoding cp932 \
  --search-free-space-from 0x700000 \
  --report analysis/item_patch_report.json
```

## `.tbl` 사용

게임이 Shift-JIS가 아니라 전용 문자셋을 쓴다면 `.tbl` 파일을 만들어서 사용할 수 있습니다.

예시:

```text
00=<END>
01=あ
02=い
03=う
10=Ａ
11=Ｂ
8140=　
```

이후 `--encoding` 대신 `--table your.tbl` 를 사용하면 됩니다.

## 권장 작업 순서

1. `info` 로 ROM 기본 정보를 확인합니다.
2. `scan-lz77` 로 압축이 많이 쓰였는지 먼저 봅니다.
3. `scan-text` 를 `cp932`, `00`, `FF` 조합으로 돌려봅니다.
4. 메뉴에서 보이는 문구를 하나 정해서 `search-text` 로 직접 찾습니다.
5. 연속된 텍스트 블록이 보이면 `extract-range` 로 JSON으로 뽑아서 번역 목록을 만듭니다.
6. `translation` 필드를 채운 뒤 `apply-translations` 로 일괄 패치합니다.
7. 문자열이 안 잡히면 커스텀 인코딩이나 압축 스크립트일 가능성이 높으니 `.tbl` 과 폰트 타일부터 조사합니다.
8. 타일/폰트를 찾으면 한글 글리프를 넣고, 그 다음 문자열 삽입기로 넘어갑니다.

## 주의

- 이 툴은 ROM을 자동 번역해 주지 않습니다.
- GBA 게임은 보통 텍스트, 포인터, 폰트, 폭 테이블, 압축이 각각 다른 방식으로 섞여 있습니다.
- 그래서 첫 단계는 "게임 전용 데이터 형식 파악"이고, 이 툴은 그 작업을 빠르게 하도록 설계했습니다.
