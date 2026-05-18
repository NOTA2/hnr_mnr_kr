#!/usr/bin/env python3

from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from gba_kor_tool.translation_normalization import PROFILE_PATH, build_default_profile

EXTRACTED_ROOT = ROOT / "confirmed_data" / "extracted_texts"


def load_texts() -> list[str]:
    texts: list[str] = []
    for path in sorted(EXTRACTED_ROOT.glob("*.json")):
        payload = json.loads(path.read_text(encoding="utf-8"))
        if not isinstance(payload, list):
            continue
        for record in payload:
            if isinstance(record, dict):
                text = record.get("text")
                if isinstance(text, str) and text:
                    texts.append(text)
    return texts


def main() -> int:
    texts = load_texts()
    profile = build_default_profile(texts)
    PROFILE_PATH.write_text(json.dumps(profile, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"written : {PROFILE_PATH}")
    print(f"texts   : {len(texts)}")
    print(f"chars   : {len(profile['safe_chars'])}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
