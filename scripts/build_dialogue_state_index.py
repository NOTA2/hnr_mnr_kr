from __future__ import annotations

import json
from collections import Counter, defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ROM_PATH = ROOT / "Hagane no Renkinjutsushi - Meisou no Rondo (Japan).gba"
ENTRY8_PATH = ROOT / "confirmed_data" / "extracted_texts" / "registry_a_entry8_prefixed_texts.json"
REGD_PATH = ROOT / "confirmed_data" / "extracted_texts" / "registry_d_fc_script_texts.json"
OUT_DIR = ROOT / "confirmed_data" / "dialogue_metadata"


def load_json(path: Path):
    return json.loads(path.read_text())


def row_text(row: dict) -> str:
    return row.get("text") or row.get("decoded_text") or ""


def collect_entry8() -> dict:
    rows = load_json(ENTRY8_PATH)
    rom = ROM_PATH.read_bytes()
    entries = []
    token_counter = Counter()
    token_examples = defaultdict(list)

    for i, row in enumerate(rows):
        header = row["header_offset"]
        prev_end = rows[i - 1]["offset"] + rows[i - 1]["byte_length"] if i > 0 else header
        gap = rom[prev_end:header]
        last_27ff = None
        last_1bff = None
        last_2bff = None
        for j in range(0, len(gap) - 3):
            if gap[j] == 0x27 and gap[j + 1] == 0xFF:
                last_27ff = f"{gap[j+2]:02X}{gap[j+3]:02X}"
            if gap[j] == 0x1B and gap[j + 1] == 0xFF:
                last_1bff = f"{gap[j+2]:02X}{gap[j+3]:02X}"
            if gap[j] == 0x2B and gap[j + 1] == 0xFF:
                last_2bff = f"{gap[j+2]:02X}{gap[j+3]:02X}"

        state_token = None
        if last_27ff is not None:
            state_token = f"27ff:{last_27ff}"
        elif last_1bff is not None:
            state_token = f"1bff:{last_1bff}"
        elif last_2bff is not None:
            state_token = f"2bff:{last_2bff}"

        if state_token:
            token_counter[state_token] += 1
            if len(token_examples[state_token]) < 5:
                token_examples[state_token].append(row_text(row))

        entries.append(
            {
                "offset": row["offset"],
                "header_offset": row["header_offset"],
                "text": row_text(row),
                "char_count": row["char_count"],
                "byte_length": row["byte_length"],
                "control_gap_length": len(gap),
                "last_27ff_token": last_27ff,
                "last_1bff_token": last_1bff,
                "last_2bff_token": last_2bff,
                "dialogue_state_token": state_token,
            }
        )

    summary = []
    for token, count in token_counter.most_common():
        summary.append(
            {
                "dialogue_state_token": token,
                "count": count,
                "sample_texts": token_examples[token],
            }
        )

    return {
        "source_group": "registry_a_entry8",
        "status": "objective_state_tokens_only",
        "note": (
            "These are control-gap-derived state tokens, not confirmed speaker IDs. "
            "They help group lines that likely share the same active portrait/state."
        ),
        "summary": summary,
        "records": entries,
    }


def collect_registry_d() -> dict:
    rows = load_json(REGD_PATH)
    entries = []
    token_counter = Counter()
    token_examples = defaultdict(list)
    for row in rows:
        before = row.get("before_bytes", "").split()
        state_token = None
        for i in range(len(before) - 6):
            if (
                before[i] == "05"
                and before[i + 1] == "00"
                and before[i + 3] == "00"
                and before[i + 4] == "08"
                and before[i + 5] == "00"
                and before[i + 6] == "98"
            ):
                state_token = f"pre98:{before[i+2].upper()}"
                break
        if state_token:
            token_counter[state_token] += 1
            if len(token_examples[state_token]) < 5:
                token_examples[state_token].append(row_text(row))
        entries.append(
            {
                "offset": row["offset"],
                "text": row_text(row),
                "byte_length": row["byte_length"],
                "raw_byte_length": row.get("raw_byte_length"),
                "before_bytes": row.get("before_bytes", ""),
                "dialogue_state_token": state_token,
            }
        )

    summary = []
    for token, count in token_counter.most_common():
        summary.append(
            {
                "dialogue_state_token": token,
                "count": count,
                "sample_texts": token_examples[token],
            }
        )

    return {
        "source_group": "registry_d_fc_script_texts",
        "status": "objective_state_tokens_only",
        "note": (
            "These are objective preamble state tokens recovered from before_bytes. "
            "They are not confirmed speaker names."
        ),
        "summary": summary,
        "records": entries,
    }


def write_readme(entry8: dict, regd: dict) -> str:
    lines = [
        "# Dialogue Metadata",
        "",
        "이 폴더는 **화자 이름 추정**이 아니라, 대사 직전 제어군에서 뽑은 **객관적 state token** 을 담는다.",
        "",
        "현재 원칙:",
        "",
        "- `dialogue_state_token` 은 confirmed speaker ID 가 아니다.",
        "- 같은 token 을 공유하는 줄은 같은 active portrait/state 후보로 묶어 볼 수 있다.",
        "- 번역팀에서 화자 정보가 필요할 때도, 우선은 `candidate / unresolved` 레이어로 다룬다.",
        "",
        "## Files",
        "",
        "- `entry8_dialogue_state_index.json`: Registry A entry 8 script-line state tokens",
        "- `registry_d_dialogue_state_index.json`: Registry D FC-script state tokens",
        "",
        "## Top Entry8 tokens",
        "",
    ]
    for item in entry8["summary"][:10]:
        lines.append(f"- `{item['dialogue_state_token']}`: {item['count']} lines")
    lines.append("")
    lines.append("## Top Registry D tokens")
    lines.append("")
    for item in regd["summary"][:10]:
        lines.append(f"- `{item['dialogue_state_token']}`: {item['count']} lines")
    lines.append("")
    return "\n".join(lines)


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    entry8 = collect_entry8()
    regd = collect_registry_d()
    (OUT_DIR / "entry8_dialogue_state_index.json").write_text(
        json.dumps(entry8, ensure_ascii=False, indent=2) + "\n"
    )
    (OUT_DIR / "registry_d_dialogue_state_index.json").write_text(
        json.dumps(regd, ensure_ascii=False, indent=2) + "\n"
    )
    (OUT_DIR / "README.md").write_text(write_readme(entry8, regd) + "\n")
    print("Wrote dialogue metadata indices")


if __name__ == "__main__":
    main()
