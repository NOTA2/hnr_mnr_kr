#!/usr/bin/env python3

from __future__ import annotations

import json
from datetime import date
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DATA_ROOT = ROOT / "confirmed_data"
TEXT_LAYOUT = DATA_ROOT / "text_layout"
WORKSPACE = DATA_ROOT / "translation_workspace"
IMAGE = DATA_ROOT / "image_inventory"

SUBPROFILE_PATH = TEXT_LAYOUT / "runtime_dialogue_subprofiles.json"
PAGEFLOW_PATH = TEXT_LAYOUT / "runtime_pageflow_focus.json"
AUDIT_PATH = WORKSPACE / "extraction_audit_status.json"
IMAGE_PATH = IMAGE / "image_text_inventory.json"

OUT_JSON = WORKSPACE / "runtime_resolution_gates.json"
OUT_MD = WORKSPACE / "runtime_resolution_gates.md"


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def build() -> dict:
    sub = load_json(SUBPROFILE_PATH)
    page = load_json(PAGEFLOW_PATH)
    audit = load_json(AUDIT_PATH)
    image = load_json(IMAGE_PATH)

    return {
        "version": 1,
        "last_updated": date.today().isoformat(),
        "structural_closure": {
            "status": audit["structural_extraction_status"],
            "known_source_count": audit["known_source_count"],
            "known_record_count": audit["known_record_count"],
        },
        "machine_closable_runtime_scope": {
            "status": "nearly_closed_except_visual_confirmation",
            "entry8_focus_cluster_count": page["entry8_focus"]["focus_cluster_count"],
            "entry8_chain_heavy_clusters": sub["entry8"]["profile_counts"]["chain_heavy_singleline"],
            "registry_d_long_multiline_focus_count": page["registry_d_focus"]["long_multiline_focus_count"],
            "notes": [
                "남은 runtime 범위는 더 이상 source 전체가 아니라, 한정된 focus 집합으로 줄었다.",
                "Entry8 은 외부 script 로 이어질 가능성이 높은 chain-heavy 짧은 줄 cluster 로 좁혀졌다.",
                "Registry D 는 소수의 장문 multiline 계층과 page-turn 동작으로 좁혀졌다.",
            ],
        },
        "image_inventory_scope": {
            "status": image["status"],
            "review_unit_count": len(image["review_units"]),
            "highest_priority_units": [unit["id"] for unit in sorted(image["review_units"], key=lambda x: x["review_order"])[:4]],
        },
        "human_verification_blockers": [
            {
                "id": "live_playthrough_text_audit",
                "reason": "실제 플레이 흐름으로 훑어봐야만 아직 방문하지 않은 runtime 분기에서 일본어 문자열이 더 남아 있는지 확인할 수 있다.",
            },
            {
                "id": "visual_page_turn_confirmation",
                "reason": "entry8 연쇄 표시와 Registry D 장문 multiline 사례의 대사창/page-flow 동작은 실제 화면 확인이 있어야만 완전히 닫을 수 있다.",
            },
            {
                "id": "baked_image_text_asset_review",
                "reason": "실제 이미지에 구워진 텍스트는 asset 단위 검토와 이후 추출/교체 작업이 아직 필요하다.",
            },
        ],
        "operational_reading": [
            "기계적으로 닫을 수 있는 구조적 추출은 현재 알려진 source 기준 사실상 마감됐다.",
            "이제 남은 일의 대부분은 미발견 텍스트 뱅크 탐색이 아니라, 사람 눈으로 확인해야 하는 runtime 동작과 이미지 검토다.",
        ],
    }


def render_md(data: dict) -> str:
    lines = [
        "# runtime 마감 관문",
        "",
        f"- 마지막 갱신: `{data['last_updated']}`",
        "",
        "## 구조적 마감 상태",
        "",
        f"- 상태: `{data['structural_closure']['status']}`",
        f"- 확인된 source 수: `{data['structural_closure']['known_source_count']}`",
        f"- 확인된 record 수: `{data['structural_closure']['known_record_count']}`",
        "",
        "## 기계적으로 거의 닫힌 runtime 범위",
        "",
        f"- 상태: `{data['machine_closable_runtime_scope']['status']}`",
        f"- entry8 focus cluster 수: `{data['machine_closable_runtime_scope']['entry8_focus_cluster_count']}`",
        f"- entry8 chain-heavy cluster 수: `{data['machine_closable_runtime_scope']['entry8_chain_heavy_clusters']}`",
        f"- Registry D 장문 multiline focus 수: `{data['machine_closable_runtime_scope']['registry_d_long_multiline_focus_count']}`",
        "",
        "## 이미지 검토 범위",
        "",
        f"- 상태: `{data['image_inventory_scope']['status']}`",
        f"- 검토 단위 수: `{data['image_inventory_scope']['review_unit_count']}`",
    ]
    for unit in data["image_inventory_scope"]["highest_priority_units"]:
        lines.append(f"- 우선 검토 단위: `{unit}`")
    lines.extend(["", "## 사람 확인이 필요한 항목", ""])
    for item in data["human_verification_blockers"]:
        lines.append(f"- `{item['id']}`: {item['reason']}")
    lines.extend(["", "## 현재 해석", ""])
    for note in data["operational_reading"]:
        lines.append(f"- {note}")
    lines.append("")
    return "\n".join(lines)


def main() -> int:
    data = build()
    OUT_JSON.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    OUT_MD.write_text(render_md(data), encoding="utf-8")
    print(f"wrote {OUT_JSON}")
    print(f"wrote {OUT_MD}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
