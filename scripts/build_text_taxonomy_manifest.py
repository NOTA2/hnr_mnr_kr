#!/usr/bin/env python3

from __future__ import annotations

import json
from collections import Counter
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
WORKSPACE = REPO_ROOT / "confirmed_data" / "translation_workspace"
MASTER_PATH = WORKSPACE / "all_extracted_texts_master.json"
OUTPUT_PATH = WORKSPACE / "text_taxonomy_manifest.json"

SOURCE_CLASSIFICATION = {
    "startup_intro_texts": {
        "content_type": "intro_title_card_text",
        "scope": "objective",
        "notes": "게임 시작 직후 첫 카드의 연대/지명/형제 나이 표기",
    },
    "system_messages": {
        "content_type": "system_message",
        "scope": "objective",
        "notes": "시스템 상태/통신 등 UI 메시지",
    },
    "save_menu_prefixed_texts": {
        "content_type": "save_menu_message",
        "scope": "objective",
        "notes": "세이브/진행 관련 메뉴 문구",
    },
    "location_texts": {
        "content_type": "location_name",
        "scope": "objective",
        "notes": "월드맵/지역명",
    },
    "ui_skill_texts": {
        "content_type": "ui_skill_name_or_description",
        "scope": "objective",
        "notes": "UI 기술명/설명 계열",
    },
    "battle_texts": {
        "content_type": "battle_skill_name_or_description",
        "scope": "objective",
        "notes": "전투 기술명/설명",
    },
    "ability_texts": {
        "content_type": "ability_or_material_description",
        "scope": "objective",
        "notes": "능력/재료 설명 계열",
    },
    "material_texts": {
        "content_type": "material_name_or_description",
        "scope": "objective",
        "notes": "재료명/재료 설명",
    },
    "item_texts": {
        "content_type": "item_or_event_term",
        "scope": "objective",
        "notes": "아이템명과 이벤트 관련 용어가 함께 섞임",
    },
    "registry_a_entry12_texts": {
        "content_type": "gameplay_item_or_event_text",
        "scope": "objective",
        "notes": "게임플레이/아이템/이벤트 관련 소형 뱅크",
    },
    "registry_d_fc_script_texts": {
        "content_type": "dialogue_or_tutorial_script",
        "scope": "objective",
        "notes": "이벤트/튜토리얼 mixed script 대사",
    },
    "registry_a_entry8_prefixed_texts": {
        "content_type": "dialogue_or_event_script",
        "scope": "objective",
        "notes": "대형 스토리/이벤트/메뉴 mixed script",
    },
    "credits_texts": {
        "content_type": "credits_text",
        "scope": "objective",
        "notes": "스태프롤/크레딧",
    },
}


def main() -> int:
    records = json.loads(MASTER_PATH.read_text(encoding="utf-8"))
    counts = Counter()
    unknown_sources = Counter()
    speaker_candidate_count = 0

    for row in records:
        source_group = str(row.get("source_group", ""))
        info = SOURCE_CLASSIFICATION.get(source_group)
        if info:
            counts[info["content_type"]] += 1
        else:
            unknown_sources[source_group] += 1

        # Strictly non-objective if inferred from text alone; keep zero unless explicit field exists.
        if "speaker" in row or "speaker_id" in row:
            speaker_candidate_count += 1

    payload = {
        "master_file": "confirmed_data/translation_workspace/all_extracted_texts_master.json",
        "record_count": len(records),
        "source_classification": SOURCE_CLASSIFICATION,
        "counts_by_content_type": dict(sorted(counts.items())),
        "unknown_source_groups": dict(sorted(unknown_sources.items())),
        "speaker_metadata": {
            "explicit_speaker_fields_found": speaker_candidate_count,
            "speaker_identification_status": "not_available_yet",
            "notes": [
                "현재 추출 JSON에는 speaker / speaker_id 필드가 없다.",
                "따라서 대사의 화자를 비자의적으로 확정하려면 script control 구조에서 화자 메타데이터를 별도로 추적해야 한다.",
                "cluster_primary_tag / cluster_tags 는 작업 보조용 자동 태그이며, 화자 정보로 취급하면 안 된다.",
            ],
        },
    }
    OUTPUT_PATH.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"taxonomy manifest: {OUTPUT_PATH}")
    print(f"records          : {len(records)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
