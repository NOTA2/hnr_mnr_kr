from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
STARTUP_PATH = ROOT / "confirmed_data" / "extracted_texts" / "startup_intro_texts.json"
OUTPUT_DIR = ROOT / "confirmed_data" / "text_layout"
OUTPUT_PATH = OUTPUT_DIR / "text_box_family_manifest.json"
README_PATH = OUTPUT_DIR / "README.md"


SHARED_R3_20_CALLERS = [
    "0x062182",
    "0x062262",
    "0x062836",
    "0x0628F4",
    "0x06295C",
    "0x062A1A",
    "0x062A70",
    "0x065AA4",
    "0x065B44",
    "0x065BF2",
    "0x065C8E",
    "0x06718A",
    "0x0671E8",
]


def build_manifest() -> dict:
    startup_records = json.loads(STARTUP_PATH.read_text(encoding="utf-8"))
    startup_lines = []
    for index, record in enumerate(startup_records, start=1):
        startup_lines.append(
            {
                "line_index": index,
                "offset": f"0x{record['offset']:06X}",
                "byte_length": record["byte_length"],
                "append_terminator": bool(record.get("append_terminator", True)),
                "source_text": record["text"],
            }
        )

    return {
        "version": 1,
        "last_updated": "2026-05-17",
        "families": [
            {
                "id": "startup_intro_fixed_slots",
                "status": "confirmed",
                "kind": "fixed_slot",
                "description": "시작 화면 첫 카드 4줄. 각 줄은 독립 고정 길이 슬롯이며 뒤 제어코드를 밀면 안 된다.",
                "rules": {
                    "append_terminator": False,
                    "allow_manual_newline": False,
                    "allow_auto_wrap": False,
                    "pad_behavior": "must stay within slot byte length",
                },
                "lines": startup_lines,
                "evidence": {
                    "raw_control_bytes_after_lines": [
                        "line1 -> 0x05FF",
                        "line2 -> 0x04FF",
                        "line3 -> 0x04FF",
                        "line4 -> 0x08FF",
                    ]
                },
            },
            {
                "id": "save_menu_prefixed_01ff",
                "status": "partially_confirmed",
                "kind": "command_stream",
                "description": "세이브/메뉴 block에서 확인된 01 FF <u16 char_count> command-stream 레코드.",
                "rules": {
                    "header_prefix": "01 FF",
                    "char_count_field": "u16 little-endian",
                    "append_terminator": False,
                    "allow_manual_newline": False,
                    "payload_followed_by_control_bytes": True,
                },
                "notes": [
                    "Current samples are save/menu prompts near 0x772E4A..0x7731B4.",
                    "The payload is followed immediately by command/control bytes such as 0x10FF, 0x04FF, 0x14FF, 0x08FF.",
                    "Translator-side tooling must preserve the command-stream structure and update char_count safely.",
                    "This family is more constrained than plain 0x00-terminated strings, but full page-flow semantics are not yet globally mapped.",
                ],
                "samples": [
                    {"offset": "0x772E64", "header_bytes": "01 FF 09 00", "text": "セーブはできないぞ"},
                    {"offset": "0x772F3A", "header_bytes": "01 FF 06 00", "text": "セーブ中だよ"},
                    {"offset": "0x773106", "header_bytes": "01 FF 0D 00", "text": "前のデータに上書きするぞ？"},
                ],
            },
            {
                "id": "shared_text_object_r3_20",
                "status": "code_derived",
                "kind": "shared_text_object",
                "description": "일반 UI/대사창 계열로 보이는 공용 text object family. 다수 caller 가 동일한 setup 인자를 쓴다.",
                "rules": {
                    "setup_r2": 136,
                    "setup_r3": 20,
                    "capacity_units_after_setup": 30,
                    "fullwidth_advance": 24,
                    "halfwidth_advance": 16,
                    "approx_fullwidth_chars_per_line": 20,
                    "approx_halfwidth_chars_per_line": 30,
                },
                "callers": SHARED_R3_20_CALLERS,
                "notes": [
                    "0x014A98 is the setup helper and transforms r3 with floor(3 * r3 / 2).",
                    "0x014ED0 increments obj+0x18 by 0x18 for multibyte/fullwidth and 0x10 for single-byte/halfwidth.",
                    "This family is code-derived and still needs gameplay-side visual confirmation before being treated as a hard translation limit.",
                ],
            },
            {
                "id": "world_map_location_r3_12",
                "status": "code_derived",
                "kind": "shared_text_object",
                "description": "월드맵 지역명 표시 family. world-map caller 0x06A972 가 별도 capacity 를 쓴다.",
                "rules": {
                    "setup_r2": 136,
                    "setup_r3": 12,
                    "capacity_units_after_setup": 18,
                    "fullwidth_advance": 24,
                    "halfwidth_advance": 16,
                    "approx_fullwidth_chars_per_line": 12,
                    "approx_halfwidth_chars_per_line": 18,
                },
                "callers": ["0x06A972"],
                "notes": [
                    "This is currently tied to the world-map location-name path only.",
                    "Like the shared r3=20 family, it is code-derived and should not yet be used as a universal translation limit.",
                ],
            },
        ],
    }


def build_readme() -> str:
    return """# Text Layout Data

이 폴더는 **텍스트 박스 규격 / 줄수 / 고정 슬롯 / 공용 렌더러 family** 같은 레이아웃 제약을 구조화해 둔 확정 데이터 저장소다.

## 현재 파일

- `text_box_family_manifest.json`
  - `confirmed`: 실제 바이트 구조까지 확인된 규칙
  - `code_derived`: 코드 분석으로는 강하게 좁혀졌지만, 아직 시각 QA가 부족한 규칙
- `text_layout_assignment_index.json`
  - source / workset 이 어떤 layout family 를 먼저 따라야 하는지 정리한 연결 인덱스

## 사용 원칙

- 번역팀 문서에는 **확정된 것**과 **코드 기반 잠정값**을 분리해서 쓴다.
- `code_derived` 값은 번역 길이 감을 잡는 참고치로만 쓰고, 전역 하드 제한처럼 단정하지 않는다.

## 재생성

```bash
python3 scripts/build_text_box_family_manifest.py
python3 scripts/build_text_layout_assignment_index.py
```
"""


def main() -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    manifest = build_manifest()
    OUTPUT_PATH.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    README_PATH.write_text(build_readme(), encoding="utf-8")
    print(f"wrote {OUTPUT_PATH}")
    print(f"wrote {README_PATH}")


if __name__ == "__main__":
    main()
