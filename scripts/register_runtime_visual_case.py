#!/usr/bin/env python3

from __future__ import annotations

import argparse
import json
import shutil
from datetime import datetime
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
AUDIT_JSON = ROOT / "confirmed_data" / "image_inventory" / "runtime_visual_asset_audit.json"
AUDIT_MD = ROOT / "confirmed_data" / "image_inventory" / "runtime_visual_asset_audit.md"
SCREENSHOT_DIR = ROOT / "confirmed_data" / "image_inventory" / "runtime_screenshots"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="실플레이 미번역 이미지/타일 스크린샷 케이스를 등록합니다.")
    parser.add_argument("screenshot", type=Path)
    parser.add_argument("--case-id", required=True)
    parser.add_argument("--visible-text", default="")
    parser.add_argument("--context", default="")
    parser.add_argument(
        "--source-type",
        choices=["unknown", "rendered_text_string", "font_or_glyph_sheet", "tilemap_composed_ui", "baked_image_text"],
        default="unknown",
    )
    parser.add_argument("--notes", default="")
    return parser.parse_args()


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, payload: dict) -> None:
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def render_md(data: dict) -> str:
    lines = [
        "# Runtime Visual Asset Audit",
        "",
        f"- 상태: `{data['status']}`",
        f"- 마지막 갱신: `{data['last_updated']}`",
        "",
        "정적 LZ77/raw contact sheet 에서는 한글화 대상 이미지 라벨이 거의 보이지 않았지만, 실제 플레이에서는 번역해야 할 이미지/타일 텍스트가 다수 보일 수 있다. 따라서 이미지 감사를 닫지 않고 **실플레이 스크린샷 기반 역추적**으로 진행한다.",
        "",
        "## 왜 정적 추출만으로 부족한가",
        "",
    ]
    for note in data.get("current_reading", []):
        lines.append(f"- {note}")
    lines.extend(["", "## 현재 확인된 케이스", ""])
    for case in data.get("known_cases", []):
        lines.append(
            f"- `{case['case_id']}`: `{case.get('source_type', 'unknown')}` / "
            f"`{case.get('status', '')}` / {case.get('visible_context', '')}"
        )
    lines.extend(["", "## 열린 케이스", ""])
    for case in data.get("open_cases", []):
        lines.append(
            f"- `{case['case_id']}`: `{case.get('source_type', 'unknown')}` / "
            f"{case.get('visible_text', '')} / screenshot=`{case.get('screenshot', '')}`"
        )
        if case.get("context"):
            lines.append(f"  - context: {case['context']}")
        if case.get("notes"):
            lines.append(f"  - notes: {case['notes']}")
    lines.extend(
        [
            "",
            "## 앞으로의 처리 순서",
            "",
            "1. 미번역 이미지/타일이 보이는 플레이 스크린샷을 케이스로 등록한다.",
            "2. 보이는 문구가 일반 문자열, 폰트/글리프, 타일맵 UI, 구운 이미지 중 무엇인지 분류한다.",
            "3. 영문판 동일 화면 또는 동일 ROM 블록과 비교한다.",
            "4. 실제 교체가 필요한 경우에만 GUI 이미지 작업 항목으로 승격한다.",
            "",
        ]
    )
    return "\n".join(lines)


def main() -> int:
    args = parse_args()
    if not args.screenshot.exists():
        raise SystemExit(f"screenshot not found: {args.screenshot}")

    data = load_json(AUDIT_JSON)
    SCREENSHOT_DIR.mkdir(parents=True, exist_ok=True)
    suffix = args.screenshot.suffix or ".png"
    copied = SCREENSHOT_DIR / f"{args.case_id}{suffix}"
    shutil.copy2(args.screenshot, copied)

    case = {
        "case_id": args.case_id,
        "status": "open",
        "registered_at": datetime.now().isoformat(timespec="seconds"),
        "screenshot": str(copied.relative_to(ROOT)),
        "visible_text": args.visible_text,
        "context": args.context,
        "source_type": args.source_type,
        "notes": args.notes,
    }
    data["last_updated"] = datetime.now().date().isoformat()
    data.setdefault("open_cases", [])
    data["open_cases"] = [item for item in data["open_cases"] if item.get("case_id") != args.case_id]
    data["open_cases"].append(case)
    write_json(AUDIT_JSON, data)
    AUDIT_MD.write_text(render_md(data), encoding="utf-8")
    print(f"registered: {case['case_id']}")
    print(f"screenshot: {case['screenshot']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
