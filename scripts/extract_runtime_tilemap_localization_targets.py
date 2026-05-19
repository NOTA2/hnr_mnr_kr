#!/usr/bin/env python3
"""Extract focused BG tilemap regions that contain localizable UI text."""

from __future__ import annotations

import json
import struct
from pathlib import Path

from PIL import Image, ImageDraw

from render_runtime_tilemaps import ROOT, screen_entry_offset


CAPTURE_ROOT = ROOT / "confirmed_data" / "image_inventory" / "runtime_user_captures"
VIEW_ROOT = ROOT / "confirmed_data" / "image_inventory" / "runtime_tilemaps"
OUT_DIR = ROOT / "confirmed_data" / "image_inventory" / "runtime_tilemap_targets"


TARGETS = [
    {
        "target_id": "alchemy_notebook_label_bg1",
        "label": "연성수첩 메뉴 라벨",
        "scene": "no_entry8_latest_ss2",
        "frame": "frame_008774",
        "bg": 1,
        "tile_rect": [0, 0, 6, 2],
        "text_seen": "錬成手帳",
        "korean_goal": "연성수첩",
        "notes": "ROM 블록 매칭이 잡히지 않아 런타임 폰트/문자 타일 가능성이 높은 BG tilemap 영역.",
    },
    {
        "target_id": "battle_hud_actor_names_bg1",
        "label": "전투 HUD 에드/알 이름",
        "scene": "no_entry8_ss3",
        "frame": "frame_112458",
        "bg": 1,
        "tile_rect": [0, 14, 16, 4],
        "text_seen": "エド / アル",
        "korean_goal": "에드 / 알",
        "notes": "전투 HUD 좌측 이름/수치 영역. 소형 글자 블록과 함께 검토할 대상.",
    },
    {
        "target_id": "battle_attack_label_bg1",
        "label": "전투 명령 こうげき",
        "scene": "no_entry8_ss3",
        "frame": "frame_112458",
        "bg": 1,
        "tile_rect": [24, 14, 6, 2],
        "text_seen": "こうげき",
        "korean_goal": "공격",
        "notes": "전투 하단 명령 버튼 라벨. 화면에는 텍스트처럼 보이나 BG tilemap상 전용 타일로 배치된다.",
    },
    {
        "target_id": "card_list_controls_bg1",
        "label": "카드 리스트 ID/BACK/NEXT/いいえ",
        "scene": "no_entry8_latest_ss3",
        "frame": "frame_009730",
        "bg": 1,
        "tile_rect": [0, 0, 18, 20],
        "text_seen": "ID / BACK / NEXT / いいえ",
        "korean_goal": "ID / 뒤로 / 다음 / 아니요",
        "notes": "카드 리스트 UI 레이어. same-slot RLE 교체는 아직 압축 크기 초과라 tilemap/확장 전략 후보로 둔다.",
    },
]


def write_json(path: Path, payload) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def read_bg_control(ioreg: bytes, bg: int) -> dict:
    bgcnt = struct.unpack_from("<H", ioreg, 0x8 + bg * 2)[0]
    return {
        "bg": bg,
        "bgcnt": bgcnt,
        "char_base": ((bgcnt >> 2) & 0x3) * 0x4000,
        "screen_base": (bgcnt >> 8) & 0x1F,
        "is_8bpp": bool(bgcnt & 0x80),
        "size": (bgcnt >> 14) & 0x3,
        "scroll_x": struct.unpack_from("<H", ioreg, 0x10 + bg * 4)[0] & 0x1FF,
        "scroll_y": struct.unpack_from("<H", ioreg, 0x12 + bg * 4)[0] & 0x1FF,
    }


def crop_and_scale(path: Path, tile_rect: list[int], out_dir: Path) -> tuple[str, str]:
    image = Image.open(path).convert("RGB")
    x, y, w, h = tile_rect
    crop = image.crop((x * 8, y * 8, (x + w) * 8, (y + h) * 8))
    crop_path = out_dir / "crop.png"
    crop.save(crop_path)
    scaled = crop.resize((crop.width * 4, crop.height * 4), Image.Resampling.NEAREST)
    scaled_path = out_dir / "crop_4x.png"
    scaled.save(scaled_path)
    return str(crop_path.relative_to(ROOT)), str(scaled_path.relative_to(ROOT))


def draw_contact(targets: list[dict]) -> str:
    thumbs: list[Image.Image] = []
    for index, item in enumerate(targets, start=1):
        image = Image.open(ROOT / item["crop_4x_path"]).convert("RGB")
        image.thumbnail((260, 120), Image.Resampling.NEAREST)
        canvas = Image.new("RGB", (280, 190), (16, 16, 18))
        canvas.paste(image, ((280 - image.width) // 2, 0))
        draw = ImageDraw.Draw(canvas)
        draw.text(
            (6, 126),
            f"{index:02d} {item['target_id']}\n{item['text_seen']}\n{item['korean_goal']}",
            fill=(240, 240, 240),
        )
        thumbs.append(canvas)
    cols = 2
    rows = (len(thumbs) + cols - 1) // cols
    sheet = Image.new("RGB", (cols * 280, rows * 190), (8, 8, 10))
    for index, thumb in enumerate(thumbs):
        sheet.paste(thumb, ((index % cols) * 280, (index // cols) * 190))
    path = OUT_DIR / "runtime_tilemap_targets_contact_sheet.png"
    sheet.save(path)
    return str(path.relative_to(ROOT))


def extract_target(config: dict) -> dict:
    scene = config["scene"]
    frame = config["frame"]
    bg = int(config["bg"])
    out_dir = OUT_DIR / config["target_id"]
    out_dir.mkdir(parents=True, exist_ok=True)
    ioreg = (CAPTURE_ROOT / scene / f"{frame}_ioreg_04000000.bin").read_bytes()
    control = read_bg_control(ioreg, bg)
    x, y, w, h = [int(value) for value in config["tile_rect"]]
    entries = []
    for screen_y in range(y, y + h):
        map_y = ((control["scroll_y"] // 8) + screen_y) % 32
        for screen_x in range(x, x + w):
            map_x = ((control["scroll_x"] // 8) + screen_x) % 32
            entry_addr = screen_entry_offset(control["screen_base"], map_x, map_y, control["size"])
            vram = (CAPTURE_ROOT / scene / f"{frame}_vram_06000000.bin").read_bytes()
            entry = struct.unpack_from("<H", vram, entry_addr)[0]
            entries.append(
                {
                    "screen_tile_x": screen_x,
                    "screen_tile_y": screen_y,
                    "map_tile_x": map_x,
                    "map_tile_y": map_y,
                    "screen_entry_addr": entry_addr,
                    "screen_entry": entry,
                    "tile_index": entry & 0x3FF,
                    "hflip": bool(entry & 0x400),
                    "vflip": bool(entry & 0x800),
                    "palette_bank": (entry >> 12) & 0xF,
                }
            )
    view_path = VIEW_ROOT / scene / frame / f"bg{bg}_viewport.png"
    crop_path, crop_4x_path = crop_and_scale(view_path, [x, y, w, h], out_dir)
    payload = {
        **config,
        "bg_control": control,
        "viewport_path": str(view_path.relative_to(ROOT)),
        "crop_path": crop_path,
        "crop_4x_path": crop_4x_path,
        "tile_entries": entries,
        "unique_tile_indexes": sorted({entry["tile_index"] for entry in entries}),
        "unique_palette_banks": sorted({entry["palette_bank"] for entry in entries}),
    }
    (out_dir / "tilemap_target.json").write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return payload


def write_markdown(items: list[dict], contact_sheet: str) -> None:
    lines = [
        "# Runtime Tilemap Localization Targets",
        "",
        "런타임 BG tilemap에서 실제 한글화 대상 텍스트가 보이는 영역만 잘라낸 목록입니다.",
        "",
        f"- contact sheet: `{contact_sheet}`",
        f"- total targets: `{len(items)}`",
        "",
        "| id | scene | bg | tile rect | seen | goal | unique tiles |",
        "| --- | --- | ---: | --- | --- | --- | ---: |",
    ]
    for item in items:
        lines.append(
            "| `{target_id}` | `{scene}` | `{bg}` | `{rect}` | {seen} | {goal} | `{tiles}` |".format(
                target_id=item["target_id"],
                scene=item["scene"],
                bg=item["bg"],
                rect=item["tile_rect"],
                seen=item["text_seen"],
                goal=item["korean_goal"],
                tiles=len(item["unique_tile_indexes"]),
            )
        )
    lines.extend(["", "## Notes", ""])
    lines.extend(f"- `{item['target_id']}`: {item['notes']}" for item in items)
    (OUT_DIR / "runtime_tilemap_targets.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    items = [extract_target(config) for config in TARGETS]
    contact_sheet = draw_contact(items)
    write_json(OUT_DIR / "runtime_tilemap_targets.json", items)
    write_markdown(items, contact_sheet)
    print(f"targets: {len(items)}")
    print(f"contact: {ROOT / contact_sheet}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
