#!/usr/bin/env python3

from __future__ import annotations

import argparse
import json
import math
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from gba_kor_tool.cli import decompress_lz77

ROM = ROOT / "Hagane no Renkinjutsushi - Meisou no Rondo (Japan).gba"
LZ77_BLOCKS = ROOT / "confirmed_data" / "image_inventory" / "lz77_blocks.json"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="review unit 후보용 LZ77/4bpp 덤프를 준비합니다.")
    parser.add_argument(
        "review_unit",
        nargs="+",
        choices=[
            "title_logo_wordmark",
            "title_screen_static_menu_wordmarks",
            "event_or_cutscene_text_cards",
            "ui_panel_label_art",
            "ui_icon_badge_wordmarks",
            "battle_result_or_reward_banners",
            "all_text_units",
        ],
    )
    parser.add_argument("--limit", type=int, default=12, help="unit 하나당 최대 후보 수")
    return parser.parse_args()


def load_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, payload) -> None:
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def render_raw_4bpp(raw_path: Path, output_path: Path, *, columns: int = 32) -> dict[str, int]:
    data = raw_path.read_bytes()
    if len(data) % 32 != 0:
        raise ValueError(f"raw 4bpp size is not tile-aligned: {raw_path}")
    tile_count = len(data) // 32
    rows = math.ceil(tile_count / columns)
    width = columns * 8
    height = rows * 8
    image = bytearray(width * height)

    for tile_index in range(tile_count):
        tile_x = (tile_index % columns) * 8
        tile_y = (tile_index // columns) * 8
        tile = data[tile_index * 32 : (tile_index + 1) * 32]
        for row in range(8):
            row_data = tile[row * 4 : row * 4 + 4]
            for pair_index, byte in enumerate(row_data):
                lo = byte & 0x0F
                hi = (byte >> 4) & 0x0F
                image[(tile_y + row) * width + tile_x + pair_index * 2] = lo * 17
                image[(tile_y + row) * width + tile_x + pair_index * 2 + 1] = hi * 17

    output_path.write_bytes(
        f"P5\n{width} {height}\n255\n".encode("ascii") + bytes(image)
    )
    return {"tile_count": tile_count, "width": width, "height": height, "columns": columns, "rows": rows}


def candidate_blocks(*, min_size: int, max_size: int | None, limit: int) -> list[dict]:
    blocks = load_json(LZ77_BLOCKS)
    candidates = [
        block
        for block in blocks
        if block["decompressed_size"] >= min_size
        and (max_size is None or block["decompressed_size"] <= max_size)
        and block["decompressed_size"] % 32 == 0
    ]
    candidates.sort(key=lambda block: (block["decompressed_size"], block["compressed_size"]), reverse=True)
    return candidates[:limit]


UNIT_CONFIG = {
    "title_logo_wordmark": {
        "workspace": "01_title_logo_wordmark",
        "report_stem": "title_logo_candidate_report",
        "title": "타이틀 로고 후보 덤프",
        "min_size": 0x8000,
        "max_size": None,
    },
    "title_screen_static_menu_wordmarks": {
        "workspace": "02_title_screen_static_menu_wordmarks",
        "report_stem": "title_screen_menu_candidate_report",
        "title": "타이틀 메뉴 워드마크 후보 덤프",
        "min_size": 0x2000,
        "max_size": 0x8000,
    },
    "event_or_cutscene_text_cards": {
        "workspace": "03_event_or_cutscene_text_cards",
        "report_stem": "event_or_cutscene_card_candidate_report",
        "title": "이벤트/컷신 카드 후보 덤프",
        "min_size": 0x4000,
        "max_size": None,
    },
    "ui_panel_label_art": {
        "workspace": "06_ui_panel_label_art",
        "report_stem": "ui_panel_label_candidate_report",
        "title": "UI 패널 라벨 후보 덤프",
        "min_size": 0x1000,
        "max_size": 0x6000,
    },
    "ui_icon_badge_wordmarks": {
        "workspace": "07_ui_icon_badge_wordmarks",
        "report_stem": "ui_icon_badge_candidate_report",
        "title": "UI 아이콘/배지 워드마크 후보 덤프",
        "min_size": 0x0400,
        "max_size": 0x2000,
    },
    "battle_result_or_reward_banners": {
        "workspace": "08_battle_result_or_reward_banners",
        "report_stem": "battle_banner_candidate_report",
        "title": "전투 결과/보상 배너 후보 덤프",
        "min_size": 0x1000,
        "max_size": 0x8000,
    },
}


def build_candidates_for_unit(unit_id: str, limit: int) -> int:
    cfg = UNIT_CONFIG[unit_id]
    workspace = ROOT / "confirmed_data" / "image_inventory" / "workspaces" / cfg["workspace"]
    dumps_dir = workspace / "dumps"
    exports_dir = workspace / "exports"
    notes_dir = workspace / "notes"
    for path in (dumps_dir, exports_dir, notes_dir):
        path.mkdir(parents=True, exist_ok=True)

    rom_bytes = ROM.read_bytes()
    report = {"review_unit": unit_id, "candidates": []}
    for index, block in enumerate(
        candidate_blocks(min_size=cfg["min_size"], max_size=cfg["max_size"], limit=limit),
        start=1,
    ):
        stem = f"{index:02d}_off_{block['offset']:08X}"
        raw_path = dumps_dir / f"{stem}.bin"
        pgm_path = exports_dir / f"{stem}.pgm"
        payload, _ = decompress_lz77(rom_bytes, block["offset"], max_output_size=4 * 1024 * 1024)
        raw_path.write_bytes(payload)
        render_info = render_raw_4bpp(raw_path, pgm_path)
        report["candidates"].append(
            {
                **block,
                "raw_path": str(raw_path.relative_to(ROOT)),
                "preview_path": str(pgm_path.relative_to(ROOT)),
                **render_info,
            }
        )

    report_path = notes_dir / f"{cfg['report_stem']}.json"
    write_json(report_path, report)
    md_path = notes_dir / f"{cfg['report_stem']}.md"
    lines = [
        f"# {cfg['title']}",
        "",
        f"- 후보 수: `{len(report['candidates'])}`",
        f"- review_unit: `{unit_id}`",
        "",
    ]
    for item in report["candidates"]:
        lines.extend(
            [
                f"## 0x{item['offset']:08X}",
                "",
                f"- 압축 크기: `{item['compressed_size']}`",
                f"- 복원 크기: `{item['decompressed_size']}`",
                f"- raw: `{item['raw_path']}`",
                f"- preview: `{item['preview_path']}`",
                f"- 타일 수: `{item['tile_count']}` / 크기: `{item['width']}x{item['height']}`",
                "",
            ]
        )
    md_path.write_text("\n".join(lines), encoding="utf-8")
    print(f"report: {report_path}")
    print(f"markdown: {md_path}")
    return 0


def main() -> int:
    args = parse_args()
    units = list(args.review_unit)
    if "all_text_units" in units:
        units = [unit for unit in UNIT_CONFIG]
    for unit_id in units:
        build_candidates_for_unit(unit_id, args.limit)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
