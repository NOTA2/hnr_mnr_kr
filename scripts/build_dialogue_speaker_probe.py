from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ROM_PATH = ROOT / "Hagane no Renkinjutsushi - Meisou no Rondo (Japan).gba"
ENTRY8_PATH = ROOT / "confirmed_data" / "extracted_texts" / "registry_a_entry8_prefixed_texts.json"
OUT_JSON = ROOT / "analysis" / "dialogue_speaker_probe.json"
OUT_MD = ROOT / "analysis" / "dialogue_speaker_probe.md"


SCENES = [
    {
        "id": "liore_intro_hunger_thirst",
        "label": "Liore early arrival hunger/thirst exchange",
        "texts": [
            "腹へったぁ…",
            "のど渇いたぁ…",
            "はいはい、もう心配ないよ。",
            "街に着いたからね",
        ],
    },
    {
        "id": "tutorial_blood_exchange",
        "label": "Tutorial blood exchange scene",
        "texts": [
            "なにと交換するの？",
            "いいから、",
            "指だせ。",
            "オレたちの血も必要なんだ。",
            "イタッ！！",
            "この血で魂の情報はよしっ",
        ],
    },
]


def load_rows() -> list[dict]:
    return json.loads(ENTRY8_PATH.read_text())


def hex_bytes(blob: bytes) -> str:
    return blob.hex(" ")


def row_text(row: dict) -> str:
    return row.get("text") or row.get("decoded_text") or ""


def find_first_index(rows: list[dict], text: str) -> int:
    for i, row in enumerate(rows):
        if row_text(row) == text:
            return i
    raise ValueError(f"Could not find text: {text}")


def row_summary(rows: list[dict], rom: bytes, idx: int) -> dict:
    row = rows[idx]
    header = row["header_offset"]
    offset = row["offset"]
    prev_end = rows[idx - 1]["offset"] + rows[idx - 1]["byte_length"] if idx > 0 else header
    gap = rom[prev_end:header]
    before = rom[max(0, header - 0x20):header]
    return {
        "index": idx,
        "header_offset": header,
        "offset": offset,
        "char_count": row["char_count"],
        "byte_length": row["byte_length"],
        "text": row_text(row),
        "control_gap_length": len(gap),
        "control_gap_hex": hex_bytes(gap),
        "header_prefix_hex": hex_bytes(rom[header:offset]),
        "preceding_32_bytes_hex": hex_bytes(before),
    }


def build_probe() -> dict:
    rows = load_rows()
    rom = ROM_PATH.read_bytes()
    scenes = []
    for scene in SCENES:
        entries = []
        for text in scene["texts"]:
            idx = find_first_index(rows, text)
            entries.append(row_summary(rows, rom, idx))
        scenes.append(
            {
                "id": scene["id"],
                "label": scene["label"],
                "status": "speaker_not_objectively_identified_yet",
                "entries": entries,
                "observations": [
                    "Consecutive records with only short repetitive control gaps are candidate same-turn / same-active-speaker lines.",
                    "Larger control-gap changes between adjacent records are candidate speaker/portrait/state transitions, but not proven speaker IDs yet.",
                ],
            }
        )
    return {
        "version": 1,
        "note": (
            "This probe does not assign speaker IDs. It captures objective per-record control gaps around representative "
            "dialogue lines so portrait/speaker state tracing can continue without relying on guesswork."
        ),
        "source_file": str(ENTRY8_PATH.relative_to(ROOT)),
        "scenes": scenes,
    }


def write_markdown(data: dict) -> str:
    lines = [
        "# Dialogue Speaker Probe",
        "",
        data["note"],
        "",
    ]
    for scene in data["scenes"]:
        lines.append(f"## {scene['label']}")
        lines.append("")
        lines.append(f"- Status: `{scene['status']}`")
        for obs in scene["observations"]:
            lines.append(f"- {obs}")
        lines.append("")
        for entry in scene["entries"]:
            lines.append(f"### `{entry['text']}`")
            lines.append("")
            lines.append(f"- Index: `{entry['index']}`")
            lines.append(f"- Header: `{hex(entry['header_offset'])}`")
            lines.append(f"- Text offset: `{hex(entry['offset'])}`")
            lines.append(f"- Control gap length: `{entry['control_gap_length']}`")
            lines.append(f"- Control gap: `{entry['control_gap_hex']}`")
            lines.append(f"- Header prefix: `{entry['header_prefix_hex']}`")
            lines.append("")
    return "\n".join(lines) + "\n"


def main() -> None:
    data = build_probe()
    OUT_JSON.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n")
    OUT_MD.write_text(write_markdown(data))
    print(f"Wrote {OUT_JSON}")
    print(f"Wrote {OUT_MD}")


if __name__ == "__main__":
    main()
