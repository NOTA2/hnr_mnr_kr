#!/usr/bin/env python3

from __future__ import annotations

import subprocess
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
SOURCE_PATH = REPO_ROOT / "confirmed_data" / "extracted_texts" / "registry_d_fc_script_texts.json"
OUTPUT_PATH = REPO_ROOT / "confirmed_data" / "translation_worksets" / "translation_workset_registry_d_dialogue.json"


def main() -> int:
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    subprocess.run(
        [
            sys.executable,
            "-m",
            "gba_kor_tool",
            "build-translation-set",
            str(OUTPUT_PATH),
            str(SOURCE_PATH),
        ],
        cwd=REPO_ROOT,
        check=True,
    )
    print(f"registry_d workset: {OUTPUT_PATH}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
