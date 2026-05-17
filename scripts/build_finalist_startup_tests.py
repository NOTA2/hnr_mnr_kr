#!/usr/bin/env python3

from __future__ import annotations

import json
import subprocess
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
CANDIDATES = REPO_ROOT / "confirmed_data" / "font_assets" / "finalist_font_candidates.json"
SHOWCASE_TRANSLATIONS = (
    REPO_ROOT / "confirmed_data" / "translation_worksets" / "translation_workset_startup_font_showcase.json"
)


def main() -> int:
    candidates = json.loads(CANDIDATES.read_text(encoding="utf-8"))
    built = 0
    skipped = 0
    for candidate in candidates:
        source_png = REPO_ROOT / candidate["source_png"]
        slug = candidate["slug"]
        columns = str(candidate.get("columns", 64))
        if not source_png.exists():
            print(f"skip  : {slug} (missing {source_png})")
            skipped += 1
            continue
        command = [
            "zsh",
            "scripts/build_startup_intro_from_atlas.sh",
            str(source_png),
            slug,
            columns,
            str(SHOWCASE_TRANSLATIONS.relative_to(REPO_ROOT)),
        ]
        subprocess.run(command, cwd=REPO_ROOT, check=True)
        built += 1
    print(f"built={built} skipped={skipped}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
