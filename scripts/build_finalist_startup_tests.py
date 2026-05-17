#!/usr/bin/env python3

from __future__ import annotations

import json
import shutil
import subprocess
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
CANDIDATES = REPO_ROOT / "confirmed_data" / "font_assets" / "finalist_font_candidates.json"
SHOWCASE_TRANSLATIONS = (
    REPO_ROOT / "confirmed_data" / "translation_worksets" / "translation_workset_startup_font_showcase.json"
)
COLLECTED_OUTPUT_DIR = REPO_ROOT / "patched_roms" / "font_compare" / "finalists"


def main() -> int:
    candidates = json.loads(CANDIDATES.read_text(encoding="utf-8"))
    COLLECTED_OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
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
        built_rom = REPO_ROOT / "patched_roms" / "font_compare" / slug / f"hnr_startup_intro_{slug}.gba"
        collected_rom = COLLECTED_OUTPUT_DIR / built_rom.name
        if built_rom.exists():
            shutil.copy2(built_rom, collected_rom)
            print(f"collected -> {collected_rom}")
        built += 1
    print(f"built={built} skipped={skipped}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
