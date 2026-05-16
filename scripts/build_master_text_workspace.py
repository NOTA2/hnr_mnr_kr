#!/usr/bin/env python3

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
ANALYSIS = REPO_ROOT / "analysis"
WORKSPACE = ANALYSIS / "translation_workspace"
OUTPUT_JSON = WORKSPACE / "all_extracted_texts_master.json"
OUTPUT_MANIFEST = WORKSPACE / "all_extracted_texts_manifest.json"

SOURCES = [
    "system_messages.json",
    "item_texts.json",
    "location_texts.json",
    "battle_texts.json",
    "ability_texts.json",
    "material_texts.json",
    "ui_skill_texts.json",
    "save_menu_prefixed_texts.json",
    "registry_d_fc_script_texts.json",
    "registry_a_entry8_prefixed_texts.json",
    "registry_a_entry12_texts.json",
    "credits_texts.json",
]


def main() -> int:
    WORKSPACE.mkdir(parents=True, exist_ok=True)
    cmd = [sys.executable, "-m", "gba_kor_tool", "build-translation-set", str(OUTPUT_JSON)]
    cmd.extend(str(ANALYSIS / name) for name in SOURCES)
    subprocess.run(cmd, cwd=REPO_ROOT, check=True)

    merged = json.loads(OUTPUT_JSON.read_text(encoding="utf-8"))
    manifest_sources = []
    for index, name in enumerate(SOURCES):
        path = ANALYSIS / name
        records = json.loads(path.read_text(encoding="utf-8"))
        manifest_sources.append(
            {
                "source_order": index,
                "file": f"analysis/{name}",
                "record_count": len(records),
            }
        )

    manifest = {
        "output": "analysis/translation_workspace/all_extracted_texts_master.json",
        "record_count": len(merged),
        "source_count": len(SOURCES),
        "sources": manifest_sources,
        "coverage_note": "현재까지 확보한 known extracted text sources를 통합한 작업 기준본이다. 실플레이 기반 누락 회수와 이미지 텍스트는 별도다.",
    }
    OUTPUT_MANIFEST.write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"master json : {OUTPUT_JSON}")
    print(f"manifest    : {OUTPUT_MANIFEST}")
    print(f"records     : {len(merged)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
