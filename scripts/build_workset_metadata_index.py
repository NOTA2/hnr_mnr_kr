#!/usr/bin/env python3

from __future__ import annotations

import json
from datetime import date
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DATA_ROOT = ROOT / "confirmed_data"
WORKSETS_DIR = DATA_ROOT / "translation_worksets"
WORKSPACE_DIR = DATA_ROOT / "translation_workspace"
LAYOUT_INDEX_PATH = DATA_ROOT / "text_layout" / "text_layout_assignment_index.json"
OUT_JSON = WORKSPACE_DIR / "workset_metadata_index.json"
OUT_MD = WORKSPACE_DIR / "workset_metadata_index.md"


def load_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def collect_source_groups(records: list[dict]) -> list[str]:
    return sorted({record["source_group"] for record in records})


def build_entry(layout_index: dict, workset_id: str, path: str, record_count: int, purpose: str) -> dict:
    assignment = layout_index["workset_assignments"].get(workset_id, {})
    kind = assignment.get("kind", "special")
    layout_family = assignment.get("layout_family")
    by_source_group = assignment.get("by_source_group", {})

    if kind == "uniform":
        layout_strategy = f"단일 family `{layout_family}` 기준"
    elif kind == "mixed":
        layout_strategy = "source_group 별 family 를 먼저 적용"
    else:
        layout_strategy = "별도 manifest / 특수 절차 기준"

    if workset_id == "translation_workset_startup_font_showcase":
        translation_status = "폰트/삽입 검증용 준비 완료"
        qa_required = ["고정 슬롯 byte 길이 확인", "첫 화면 4줄 시각 확인"]
        image_overlap_risk = "낮음"
        line_break_policy = "수동 줄바꿈 금지"
        must_preserve = ["append_terminator=false", "고정 byte_length", "뒤 제어코드 위치"]
        recommended_order = 0
        notes = ["모든 레코드는 startup_intro_texts 에서 왔다."]
    elif workset_id == "translation_workset_core_ui":
        translation_status = "바로 번역 시작 가능"
        qa_required = ["메뉴/세이브/지역명 대표 화면 확인", "혼합 family 적용 확인"]
        image_overlap_risk = "중간"
        line_break_policy = "source_group 별 규칙 우선"
        must_preserve = ["save_menu 01 FF 헤더", "location family 보수적 길이 유지"]
        recommended_order = 1
        notes = [
            "이 workset 은 하나의 창 규격으로 보면 안 된다.",
            "반드시 source_group 별 family 를 먼저 적용한다.",
        ]
    elif workset_id == "translation_workset_gameplay_terms":
        translation_status = "바로 번역 시작 가능"
        qa_required = ["용어/설명문 길이 과팽창 방지", "0x0B / 패딩 보존 확인"]
        image_overlap_risk = "낮음"
        line_break_policy = "추가 줄바꿈 지양"
        must_preserve = ["0x0B separator", "전각 공백 패딩", "짧고 명확한 설명문"]
        recommended_order = 2
        notes = [
            "레코드 구조는 대부분 객관적으로 닫혔다.",
            "다만 runtime box family 가 미확정인 곳이 있어 설명문은 계속 짧게 유지하는 편이 안전하다.",
        ]
    elif workset_id == "translation_workset_registry_d_dialogue":
        translation_status = "번역 시작 가능, 페이지 QA 후속 필요"
        qa_required = ["기존 개행 보존", "장문 run page-turn 확인", "화자 state token 참고"]
        image_overlap_risk = "낮음"
        line_break_policy = "기존 개행만 보존, 새 개행은 보수적으로"
        must_preserve = ["FC-delimited 구조", "adjacent control stream", "dialogue_state sidecar 참고"]
        recommended_order = 3
        notes = [
            "FC stop-byte 기준의 record 경계는 확정됐다.",
            "다만 장문 run 의 실제 page-turn 동작은 시각 QA 로 한 번 더 확인해야 한다.",
        ]
    elif workset_id == "translation_workset_intro_full_test":
        translation_status = "테스트/검증 전용"
        qa_required = ["여러 family 혼합 동작 확인", "시작 카드 이후 인트로 흐름 확인"]
        image_overlap_risk = "낮음"
        line_break_policy = "실제 번역 기준이 아니라 검증용"
        must_preserve = ["family 혼합 구조", "source_group 별 규칙"]
        recommended_order = 90
        notes = [
            "여러 family 를 한 파일에서 함께 검증하는 QA 세트다.",
            "이 세트에서 보이는 길이/줄 수를 전역 제한으로 일반화하면 안 된다.",
        ]
    elif workset_id == "translation_workset_intro_full_compact_test":
        translation_status = "테스트/검증 전용"
        qa_required = ["compact 문구 가독성 확인", "pointer 없는 상황 검증"]
        image_overlap_risk = "낮음"
        line_break_policy = "실제 번역 기준이 아니라 검증용"
        must_preserve = ["family 혼합 구조", "source_group 별 규칙"]
        recommended_order = 91
        notes = ["pointer 없는 상황에서 compact 문구로 시각 QA 를 돌리는 검증 세트다."]
    else:
        translation_status = "별도 확인 필요"
        qa_required = ["구조 확인"]
        image_overlap_risk = "미정"
        line_break_policy = "source 규칙 확인 후 결정"
        must_preserve = []
        recommended_order = 99
        notes = assignment.get("notes", [])

    return {
        "workset_id": workset_id,
        "path": path,
        "record_count": record_count,
        "purpose": purpose,
        "kind": kind,
        "layout_strategy": layout_strategy,
        "layout_family": layout_family,
        "by_source_group": by_source_group,
        "translation_status": translation_status,
        "line_break_policy": line_break_policy,
        "must_preserve": must_preserve,
        "qa_required": qa_required,
        "image_overlap_risk": image_overlap_risk,
        "recommended_translation_order": recommended_order,
        "notes": notes,
    }


def build() -> dict:
    layout_index = load_json(LAYOUT_INDEX_PATH)
    entries: list[dict] = []

    workset_specs = [
        (
            "translation_workset_startup_font_showcase",
            WORKSETS_DIR / "translation_workset_startup_font_showcase.json",
            "폰트/삽입 검증용 시작 화면 4줄",
        ),
        (
            "translation_workset_core_ui",
            WORKSETS_DIR / "translation_workset_core_ui.json",
            "시스템/세이브/지역명/UI 기술명 등 첫 실제 번역 진입 세트",
        ),
        (
            "translation_workset_gameplay_terms",
            WORKSETS_DIR / "translation_workset_gameplay_terms.json",
            "아이템/전투/능력/재료/설명 계열 용어 세트",
        ),
        (
            "translation_workset_registry_d_dialogue",
            WORKSETS_DIR / "translation_workset_registry_d_dialogue.json",
            "튜토리얼/이벤트/전투 전후 대사 세트",
        ),
        (
            "translation_workset_intro_full_test",
            WORKSETS_DIR / "translation_workset_intro_full_test.json",
            "인트로 확장 QA 세트",
        ),
        (
            "translation_workset_intro_full_compact_test",
            WORKSETS_DIR / "translation_workset_intro_full_compact_test.json",
            "인트로 compact QA 세트",
        ),
    ]

    for workset_id, path, purpose in workset_specs:
        records = load_json(path)
        entry = build_entry(layout_index, workset_id, str(path.relative_to(ROOT)), len(records), purpose)
        entry["source_groups"] = collect_source_groups(records)
        entries.append(entry)

    entry8_manifest = load_json(WORKSPACE_DIR / "registry_a_entry8_clusters_manifest.json")
    entries.append(
        {
            "workset_id": "registry_a_entry8_clusters_manifest",
            "path": "confirmed_data/translation_workspace/registry_a_entry8_clusters_manifest.json",
            "record_count": int(entry8_manifest["cluster_count"]),
            "purpose": "대형 스토리/이벤트 뱅크를 cluster 단위로 나눈 인덱스",
            "kind": "cluster_manifest",
            "layout_strategy": "cluster 단위로 나눈 뒤 entry8 single-line 규칙을 적용",
            "layout_family": "entry8_prefixed_01ff_script_line",
            "by_source_group": {"registry_a_entry8_prefixed_texts": "entry8_prefixed_01ff_script_line"},
            "translation_status": "번역 시작 가능, cluster 단위 운영 권장",
            "line_break_policy": "수동 줄바꿈 금지",
            "must_preserve": ["01 FF 헤더", "char_count", "제어코드 인접 구조", "dialogue_state sidecar 참고"],
            "qa_required": ["chain-heavy cluster 우선 점검", "후반 cluster 의 page-flow 확인"],
            "image_overlap_risk": "낮음",
            "recommended_translation_order": 4,
            "source_groups": ["registry_a_entry8_prefixed_texts"],
            "notes": [
                "cluster 를 한 번에 다 번역하지 말고 primary_tag / runtime focus 순서로 나누는 편이 안전하다."
            ],
        }
    )

    entries.sort(key=lambda item: item["recommended_translation_order"])

    return {
        "version": 1,
        "last_updated": date.today().isoformat(),
        "summary": {
            "entry_count": len(entries),
            "usage": "번역팀이 실제 번역 시작 전에 workset 별 제약과 QA 범위를 빠르게 확인하는 인덱스",
        },
        "entries": entries,
        "reading_order": [
            "1. translation_workset_startup_font_showcase 로 폰트/삽입 경로를 확인한다.",
            "2. translation_workset_core_ui 와 gameplay_terms 로 실번역을 시작한다.",
            "3. Registry D dialogue 와 entry8 cluster 는 대사 sidecar 와 runtime 주의사항을 함께 본다.",
        ],
    }


def render_md(data: dict) -> str:
    lines = [
        "# Workset 메타데이터 인덱스",
        "",
        f"- 마지막 갱신: `{data['last_updated']}`",
        f"- 항목 수: `{data['summary']['entry_count']}`",
        f"- 용도: {data['summary']['usage']}",
        "",
        "## 권장 읽기 순서",
        "",
    ]
    for item in data["reading_order"]:
        lines.append(f"- {item}")

    lines.extend(["", "## Workset별 요약", ""])
    for entry in data["entries"]:
        lines.append(f"### `{entry['workset_id']}`")
        lines.append("")
        lines.append(f"- 경로: `{entry['path']}`")
        lines.append(f"- 레코드 수: `{entry['record_count']}`")
        lines.append(f"- 목적: {entry['purpose']}")
        lines.append(f"- 상태: {entry['translation_status']}")
        lines.append(f"- layout 전략: {entry['layout_strategy']}")
        lines.append(f"- 줄바꿈 규칙: {entry['line_break_policy']}")
        lines.append(f"- source_group: `{', '.join(entry['source_groups'])}`")
        lines.append(f"- 이미지 겹침 위험: {entry['image_overlap_risk']}")
        lines.append(f"- 필수 보존 요소: {', '.join(entry['must_preserve']) if entry['must_preserve'] else '없음'}")
        lines.append(f"- QA 필요 항목: {', '.join(entry['qa_required'])}")
        if entry["by_source_group"]:
            lines.append("- source_group별 family:")
            for source_group, family in entry["by_source_group"].items():
                lines.append(f"  - `{source_group}` -> `{family}`")
        if entry["notes"]:
            lines.append("- 참고:")
            for note in entry["notes"]:
                lines.append(f"  - {note}")
        lines.append("")

    return "\n".join(lines)


def main() -> int:
    WORKSPACE_DIR.mkdir(parents=True, exist_ok=True)
    data = build()
    OUT_JSON.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    OUT_MD.write_text(render_md(data), encoding="utf-8")
    print(f"wrote {OUT_JSON}")
    print(f"wrote {OUT_MD}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
