#!/usr/bin/env python3

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
WORKSPACE = REPO_ROOT / "analysis" / "translation_workspace"
INDEX_PATH = WORKSPACE / "index.json"
README_PATH = WORKSPACE / "README.md"


def run(cmd: list[str]) -> None:
    subprocess.run(cmd, cwd=REPO_ROOT, check=True)


def load_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def main() -> int:
    WORKSPACE.mkdir(parents=True, exist_ok=True)
    run([sys.executable, "scripts/build_master_text_workspace.py"])
    run([sys.executable, "scripts/build_entry8_cluster_worksets.py"])

    master_manifest = load_json(WORKSPACE / "all_extracted_texts_manifest.json")
    entry8_manifest = load_json(WORKSPACE / "registry_a_entry8_clusters_manifest.json")

    priority_worksets = [
        {
            "label": "core_ui",
            "file": "analysis/translation_workset_core_ui.json",
            "record_count": len(load_json(REPO_ROOT / "analysis" / "translation_workset_core_ui.json")),
            "notes": "시스템/세이브/지역명/UI 기술명 위주의 첫 번역 진입점",
        },
        {
            "label": "gameplay_terms",
            "file": "analysis/translation_workset_gameplay_terms.json",
            "record_count": len(load_json(REPO_ROOT / "analysis" / "translation_workset_gameplay_terms.json")),
            "notes": "아이템/용어/설명 계열",
        },
        {
            "label": "registry_d_dialogue",
            "file": "analysis/translation_workset_registry_d_dialogue.json",
            "record_count": len(load_json(REPO_ROOT / "analysis" / "translation_workset_registry_d_dialogue.json")),
            "notes": "이벤트/전투 전후 대사 중심",
        },
        {
            "label": "entry8_clusters_manifest",
            "file": "analysis/translation_workspace/registry_a_entry8_clusters_manifest.json",
            "record_count": int(entry8_manifest["cluster_count"]),
            "notes": "대형 스토리/이벤트 뱅크를 72개 cluster로 분할한 인덱스",
        },
        {
            "label": "all_extracted_master",
            "file": "analysis/translation_workspace/all_extracted_texts_master.json",
            "record_count": int(master_manifest["record_count"]),
            "notes": "현재까지 확보된 known extracted text source 전체 기준본",
        },
    ]

    index = {
        "workspace_root": "analysis/translation_workspace",
        "master": master_manifest,
        "entry8_clusters": {
            "cluster_count": int(entry8_manifest["cluster_count"]),
            "manifest": "analysis/translation_workspace/registry_a_entry8_clusters_manifest.json",
            "output_dir": "analysis/translation_workspace/registry_a_entry8_clusters",
            "primary_tags": sorted(entry8_manifest["primary_tag_index"].keys()),
        },
        "priority_worksets": priority_worksets,
        "workflow_note": [
            "폰트 확정 전에는 workset 구조 정리와 번역 준비를 진행한다.",
            "폰트 확정 후에는 core_ui -> gameplay_terms -> registry_d_dialogue -> entry8 clusters 순으로 번역/검수 루프를 시작한다.",
            "실플레이에서 새 일본어가 보이면 그때만 extraction inventory를 다시 연다.",
        ],
    }
    INDEX_PATH.write_text(json.dumps(index, ensure_ascii=False, indent=2), encoding="utf-8")

    readme = """# Translation Workspace

이 폴더는 현재까지 확보한 번역 작업 기준본을 모아 둔 작업 허브다.

## 핵심 파일

- [all_extracted_texts_master.json](/Users/user/test/analysis/translation_workspace/all_extracted_texts_master.json)
- [all_extracted_texts_manifest.json](/Users/user/test/analysis/translation_workspace/all_extracted_texts_manifest.json)
- [registry_a_entry8_clusters_manifest.json](/Users/user/test/analysis/translation_workspace/registry_a_entry8_clusters_manifest.json)
- [index.json](/Users/user/test/analysis/translation_workspace/index.json)

## 권장 시작 순서

1. [translation_workset_core_ui.json](/Users/user/test/analysis/translation_workset_core_ui.json)
2. [translation_workset_gameplay_terms.json](/Users/user/test/analysis/translation_workset_gameplay_terms.json)
3. [translation_workset_registry_d_dialogue.json](/Users/user/test/analysis/translation_workset_registry_d_dialogue.json)
4. [registry_a_entry8_clusters_manifest.json](/Users/user/test/analysis/translation_workspace/registry_a_entry8_clusters_manifest.json)

## 재생성

```bash
python3 scripts/build_translation_workspace.py
```
"""
    README_PATH.write_text(readme, encoding="utf-8")

    print(f"workspace index : {INDEX_PATH}")
    print(f"workspace readme: {README_PATH}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
