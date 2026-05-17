#!/usr/bin/env python3

from __future__ import annotations

import json
from datetime import date
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DATA_ROOT = ROOT / "confirmed_data"
IMAGE_DIR = DATA_ROOT / "image_inventory"
INVENTORY_PATH = IMAGE_DIR / "image_text_inventory.json"
OUT_JSON = IMAGE_DIR / "image_extraction_pipeline.json"
OUT_MD = IMAGE_DIR / "image_extraction_pipeline.md"
WORKSPACES_DIR = IMAGE_DIR / "workspaces"
LZ77_SCAN_PATH = IMAGE_DIR / "lz77_blocks.json"


def load_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def ensure_workspace_dirs(review_units: list[dict]) -> list[str]:
    created: list[str] = []
    for unit in review_units:
        unit_dir = ROOT / unit["future_workspace"]
        for child in ("candidates", "dumps", "exports", "notes"):
            path = unit_dir / child
            path.mkdir(parents=True, exist_ok=True)
            created.append(str(path.relative_to(ROOT)))
    return created


def build() -> dict:
    inventory = load_json(INVENTORY_PATH)
    review_units = inventory["review_units"]
    created_dirs = ensure_workspace_dirs(review_units)
    lz77_scan_exists = LZ77_SCAN_PATH.exists()
    lz77_block_count = 0
    if lz77_scan_exists:
        lz77_scan = load_json(LZ77_SCAN_PATH)
        lz77_block_count = len(lz77_scan if isinstance(lz77_scan, list) else lz77_scan.get("blocks", []))

    return {
        "version": 1,
        "last_updated": date.today().isoformat(),
        "status": "prepared",
        "pipeline_goal": "이미지에 구워진 텍스트 자산을 review unit 단위로 찾고, 덤프/수정/교체 가능한 작업 폴더를 준비한다.",
        "review_unit_order": [
            {
                "id": unit["id"],
                "review_order": unit["review_order"],
                "workspace": unit["future_workspace"],
                "probe_method": unit["recommended_probe_method"],
            }
            for unit in review_units
        ],
        "pipeline_steps": [
            {
                "step": 1,
                "name": "대표 화면 확보",
                "description": "각 review unit 별로 실제 게임 화면 스크린샷 또는 참고 이미지를 모아, 무엇을 찾아야 하는지 고정한다.",
            },
            {
                "step": 2,
                "name": "후보 자산 탐색",
                "description": "LZ77 scan, 4bpp dump, raw tile dump 를 써서 해당 화면과 닮은 후보 자산을 찾는다.",
            },
            {
                "step": 3,
                "name": "덤프 시각 비교",
                "description": "후보 덤프를 PNG/타일 시트 형태로 모아 실제 화면과 비교하고, 맞는 후보만 남긴다.",
            },
            {
                "step": 4,
                "name": "편집용 산출물 분리",
                "description": "수정 대상이 확인되면 exports 폴더에 편집용 산출물을 만들고, notes 폴더에 포맷/팔레트/압축 여부를 기록한다.",
            },
            {
                "step": 5,
                "name": "교체 전략 결정",
                "description": "원위치 덮어쓰기, 재압축 후 교체, 포인터 재배치 중 어느 방식이 필요한지 결정한다.",
            },
        ],
        "tooling_reference": {
            "scan_lz77": "python3 -m gba_kor_tool scan-lz77 <rom>",
            "dump_4bpp": "python3 -m gba_kor_tool dump-4bpp <rom> <offset> <tile-count> <output>",
            "decompress_lz77": "python3 -m gba_kor_tool decompress-lz77 <rom> <offset> <output>",
        },
        "candidate_scan": {
            "lz77_scan_path": str(LZ77_SCAN_PATH.relative_to(ROOT)),
            "exists": lz77_scan_exists,
            "block_count": lz77_block_count,
            "note": "review unit 후보 탐색의 출발점으로 쓰는 전역 LZ77 스캔 결과다.",
        },
        "workspace_layout": {
            "root": str(WORKSPACES_DIR.relative_to(ROOT)),
            "children": ["candidates", "dumps", "exports", "notes"],
            "created_count": len(created_dirs),
        },
        "first_targets": [
            "01_title_logo_wordmark",
            "02_title_screen_static_menu_wordmarks",
            "03_event_or_cutscene_text_cards",
        ],
        "note": "이 문서는 실제 이미지 교체를 완료했다는 뜻이 아니라, review unit 별 추출/덤프/정리 루프를 바로 시작할 수 있게 scaffold 를 준비한 것이다.",
    }


def render_md(data: dict) -> str:
    lines = [
        "# 이미지 추출 파이프라인 준비",
        "",
        f"- 마지막 갱신: `{data['last_updated']}`",
        f"- 상태: `{data['status']}`",
        f"- 목표: {data['pipeline_goal']}",
        "",
        "## 우선 review unit 순서",
        "",
    ]
    for item in data["review_unit_order"]:
        lines.append(f"- `{item['id']}` (순서={item['review_order']})")
        lines.append(f"  - 작업 폴더: `{item['workspace']}`")
        lines.append(f"  - 탐색 방식: {item['probe_method']}")

    lines.extend(["", "## 작업 단계", ""])
    for step in data["pipeline_steps"]:
        lines.append(f"- `{step['step']}. {step['name']}`: {step['description']}")

    lines.extend(["", "## 도구 참고", ""])
    for key, value in data["tooling_reference"].items():
        lines.append(f"- `{key}`: `{value}`")

    lines.extend(["", "## 후보 스캔 기준", ""])
    lines.append(f"- LZ77 scan 파일: `{data['candidate_scan']['lz77_scan_path']}`")
    lines.append(f"- 존재 여부: `{data['candidate_scan']['exists']}`")
    lines.append(f"- 블록 수: `{data['candidate_scan']['block_count']}`")
    lines.append(f"- 메모: {data['candidate_scan']['note']}")

    lines.extend(["", "## 작업 폴더 구조", ""])
    lines.append(f"- 루트: `{data['workspace_layout']['root']}`")
    lines.append(f"- 하위 폴더: `{', '.join(data['workspace_layout']['children'])}`")
    lines.append(f"- 생성 수: `{data['workspace_layout']['created_count']}`")

    lines.extend(["", "## 첫 목표", ""])
    for item in data["first_targets"]:
        lines.append(f"- `{item}`")

    lines.extend(["", "## 비고", ""])
    lines.append(f"- {data['note']}")
    lines.append("")
    return "\n".join(lines)


def main() -> int:
    IMAGE_DIR.mkdir(parents=True, exist_ok=True)
    WORKSPACES_DIR.mkdir(parents=True, exist_ok=True)
    data = build()
    OUT_JSON.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    OUT_MD.write_text(render_md(data), encoding="utf-8")
    print(f"wrote {OUT_JSON}")
    print(f"wrote {OUT_MD}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
