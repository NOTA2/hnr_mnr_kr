#!/usr/bin/env python3
"""Build broad nearby graphic candidate sheets around confirmed UI images."""

from __future__ import annotations

import json
import math
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT / ".vendor") not in sys.path:
    sys.path.insert(0, str(ROOT / ".vendor"))

from PIL import Image, ImageDraw, ImageFont


IMAGE_INVENTORY = ROOT / "confirmed_data" / "image_inventory"
OUT_DIR = IMAGE_INVENTORY / "runtime_tile_matches" / "expanded_nearby_image_candidates"
SCREEN_ORDER_MANIFEST = IMAGE_INVENTORY / "runtime_rle_screen_order" / "screen_order_manifest.json"
GLOBAL_REPORT = IMAGE_INVENTORY / "global_tile_extraction" / "notes" / "global_tile_extraction_report.json"


LZ77_WINDOWS = [
    {
        "name": "field_menu_lz77_broad",
        "title": "field/menu LZ77 broad neighborhood",
        "lo": 0x00500000,
        "hi": 0x00560000,
        "note": "0x005323AC/0x0053257C 주변을 넓게 확장한 LZ77 후보",
    },
]


def load_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, payload) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def font(size: int = 12):
    for name in ("Arial Unicode.ttf", "Arial.ttf"):
        try:
            return ImageFont.truetype(name, size)
        except OSError:
            pass
    return ImageFont.load_default()


FONT = font(12)
SMALL_FONT = font(10)


def open_rgb(path: str) -> Image.Image:
    image = Image.open(ROOT / path)
    if image.mode not in ("RGB", "RGBA"):
        image = image.convert("RGB")
    elif image.mode == "RGBA":
        bg = Image.new("RGB", image.size, (20, 22, 26))
        bg.paste(image, mask=image.split()[3])
        image = bg
    return image


def fit_image(image: Image.Image, max_w: int, max_h: int) -> Image.Image:
    if image.width <= 0 or image.height <= 0:
        return image
    scale = min(max_w / image.width, max_h / image.height)
    scale = min(scale, 4.0)
    new_size = (max(1, int(image.width * scale)), max(1, int(image.height * scale)))
    return image.resize(new_size, Image.Resampling.NEAREST)


def draw_wrapped(draw: ImageDraw.ImageDraw, pos: tuple[int, int], text: str, *, width: int, fill: tuple[int, int, int], font_obj) -> int:
    x, y = pos
    line = ""
    lines: list[str] = []
    for token in text.replace("/", "/ ").split():
        trial = token if not line else f"{line} {token}"
        if draw.textlength(trial, font=font_obj) <= width:
            line = trial
        else:
            if line:
                lines.append(line)
            line = token
    if line:
        lines.append(line)
    for row in lines[:4]:
        draw.text((x, y), row, fill=fill, font=font_obj)
        y += 14
    return y


def make_contact_sheet(
    items: list[dict],
    *,
    out_path: Path,
    title: str,
    image_key: str,
    columns: int,
    cell_w: int,
    cell_h: int,
    thumb_h: int,
) -> str:
    if not items:
        raise ValueError(f"no items for {title}")
    rows = math.ceil(len(items) / columns)
    header_h = 34
    sheet = Image.new("RGB", (columns * cell_w, header_h + rows * cell_h), (13, 15, 19))
    draw = ImageDraw.Draw(sheet)
    draw.text((10, 10), title, fill=(232, 238, 245), font=FONT)

    for index, item in enumerate(items):
        col = index % columns
        row = index // columns
        x = col * cell_w
        y = header_h + row * cell_h
        draw.rectangle((x, y, x + cell_w - 1, y + cell_h - 1), outline=(41, 47, 56))
        image = open_rgb(item[image_key])
        thumb = fit_image(image, cell_w - 16, thumb_h)
        sheet.paste(thumb, (x + 8, y + 8))
        label_y = y + 12 + thumb_h
        label = item.get("label") or item.get("title") or ""
        meta = f"{item.get('source_kind', '')} {item.get('offset_hex', '')}".strip()
        if item.get("scene"):
            meta += f" {item.get('scene')} bg{item.get('bg')}"
        if item.get("replacement_target"):
            meta += " apply"
        draw.text((x + 8, label_y), meta, fill=(154, 193, 255), font=SMALL_FONT)
        draw_wrapped(
            draw,
            (x + 8, label_y + 14),
            label,
            width=cell_w - 16,
            fill=(221, 226, 232),
            font_obj=SMALL_FONT,
        )
    out_path.parent.mkdir(parents=True, exist_ok=True)
    sheet.save(out_path)
    return str(out_path.relative_to(ROOT))


def best_screen_order_by_offset(items: list[dict]) -> list[dict]:
    def rank(item: dict) -> tuple[int, int, int, float]:
        scene = str(item.get("scene", ""))
        scene_rank = 2 if scene.startswith("no_entry8_latest") else 1 if scene.startswith("current_review") else 0
        return (
            1 if item.get("replacement_target") else 0,
            scene_rank,
            int(item.get("matched_tile_count") or 0),
            float(item.get("score") or 0),
        )

    best: dict[int, dict] = {}
    for item in items:
        offset = int(item["offset"])
        item = {
            **item,
            "source_kind": "screen-order-rle",
            "image_path": item["editable_preview_path"],
        }
        if offset not in best or rank(item) > rank(best[offset]):
            best[offset] = item
    return sorted(best.values(), key=lambda item: int(item["offset"]))


def load_screen_order_items() -> list[dict]:
    items = load_json(SCREEN_ORDER_MANIFEST)
    for item in items:
        item["source_kind"] = "screen-order-rle"
        item["image_path"] = item["editable_preview_path"]
    return items


def load_lz77_window_items() -> dict[str, list[dict]]:
    report = load_json(GLOBAL_REPORT)
    output: dict[str, list[dict]] = {}
    for window in LZ77_WINDOWS:
        chosen = []
        for block in report.get("lz77", []):
            offset = int(block["offset"])
            if not (window["lo"] <= offset <= window["hi"]):
                continue
            chosen.append(
                {
                    "source_kind": "lz77-nearby",
                    "offset": offset,
                    "offset_hex": f"0x{offset:08X}",
                    "label": f"{window['note']} / size=0x{int(block['decompressed_size']):X}",
                    "preview_path": block["preview_path"],
                    "raw_path": block.get("raw_path", ""),
                    "decompressed_size": block.get("decompressed_size"),
                    "compressed_size": block.get("compressed_size"),
                    "replacement_target": False,
                }
            )
        output[window["name"]] = sorted(chosen, key=lambda item: item["offset"])
    return output


def write_markdown(summary: dict) -> str:
    lines = [
        "# Expanded Nearby Image Candidates",
        "",
        "확인된 일본어 UI 이미지 주변을 더 넓게 펼친 검토용 시트입니다.",
        "",
        "## Outputs",
        "",
    ]
    for key, value in summary["outputs"].items():
        lines.append(f"- `{key}`: `{value}`")
    lines.extend(
        [
            "",
            "## Notes",
            "",
            "- `screen_order_*`는 런타임 BG tilemap을 적용한 화면순 RLE 후보라 타일 밀림이 가장 적다.",
            "- `lz77_*`는 ROM 주변 블록을 넓게 본 원본 후보라, 실제 적용 전 화면/팔레트/타일맵 검증이 필요하다.",
            "- 영어만 보이는 워드마크는 한글화 대상에서 제외하고, 일본어가 보이는 후보만 다음 단계로 승격한다.",
            "",
        ]
    )
    md_path = OUT_DIR / "expanded_nearby_image_candidates.md"
    md_path.write_text("\n".join(lines), encoding="utf-8")
    return str(md_path.relative_to(ROOT))


def main() -> int:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    screen_order = load_screen_order_items()
    screen_order_unique = best_screen_order_by_offset(screen_order)
    lz77_windows = load_lz77_window_items()

    outputs = {
        "screen_order_all": make_contact_sheet(
            screen_order,
            out_path=OUT_DIR / "screen_order_all_contact_sheet.png",
            title=f"Runtime screen-order RLE candidates ({len(screen_order)})",
            image_key="image_path",
            columns=4,
            cell_w=300,
            cell_h=260,
            thumb_h=180,
        ),
        "screen_order_unique": make_contact_sheet(
            screen_order_unique,
            out_path=OUT_DIR / "screen_order_unique_contact_sheet.png",
            title=f"Unique screen-order RLE candidates ({len(screen_order_unique)})",
            image_key="image_path",
            columns=4,
            cell_w=300,
            cell_h=260,
            thumb_h=180,
        ),
    }

    lz77_payload = {}
    for name, items in lz77_windows.items():
        if not items:
            continue
        outputs[name] = make_contact_sheet(
            items,
            out_path=OUT_DIR / f"{name}_contact_sheet.png",
            title=f"{name} ({len(items)})",
            image_key="preview_path",
            columns=5,
            cell_w=260,
            cell_h=156,
            thumb_h=82,
        )
        lz77_payload[name] = items

    summary = {
        "screen_order_count": len(screen_order),
        "screen_order_unique_count": len(screen_order_unique),
        "screen_order_items": screen_order,
        "screen_order_unique_items": screen_order_unique,
        "lz77_windows": lz77_payload,
        "outputs": outputs,
    }
    outputs["markdown"] = write_markdown(summary)
    write_json(OUT_DIR / "expanded_nearby_image_candidates.json", summary)
    print(f"screen-order all: {len(screen_order)}")
    print(f"screen-order unique: {len(screen_order_unique)}")
    for name, items in lz77_windows.items():
        print(f"{name}: {len(items)}")
    print(f"out: {OUT_DIR}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
