#!/usr/bin/env python3
"""Curate actual graphics/tilemap localization targets from extracted assets."""

from __future__ import annotations

import json
import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT / ".vendor") not in sys.path:
    sys.path.insert(0, str(ROOT / ".vendor"))

from PIL import Image, ImageDraw


OUT_DIR = ROOT / "confirmed_data" / "image_inventory" / "localization_targets"
WORKBENCH_IMAGES = ROOT / "confirmed_data" / "localization_workbench" / "image_replacements.json"
SCREEN_ORDER_MANIFEST = ROOT / "confirmed_data" / "image_inventory" / "runtime_rle_screen_order" / "screen_order_manifest.json"


def read_json(path: Path, default):
    if not path.exists():
        return default
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, payload) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def copy_asset(rel_path: str, target_name: str) -> str:
    src = ROOT / rel_path
    if not src.exists():
        return rel_path
    dst = OUT_DIR / "assets" / target_name
    dst.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(src, dst)
    return str(dst.relative_to(ROOT))


def workbench_item_by_id() -> dict[str, dict]:
    return {item["item_id"]: item for item in read_json(WORKBENCH_IMAGES, [])}


def screen_order_by_key() -> dict[tuple[str, str, int, int], dict]:
    out = {}
    for item in read_json(SCREEN_ORDER_MANIFEST, []):
        out[(item["scene"], item["frame"], int(item["bg"]), int(item["offset"]))] = item
    return out


def target(
    *,
    target_id: str,
    label: str,
    kind: str,
    status: str,
    source_path: str,
    edit_path: str = "",
    tile_map_path: str = "",
    rom_offset: int | None = None,
    item_id: str = "",
    text_seen: str = "",
    korean_goal: str = "",
    notes: str = "",
    apply_ready: bool = False,
) -> dict:
    asset_source = copy_asset(source_path, f"{target_id}__source.png") if source_path else ""
    asset_edit = copy_asset(edit_path, f"{target_id}__edit.png") if edit_path else ""
    return {
        "target_id": target_id,
        "label": label,
        "kind": kind,
        "status": status,
        "apply_ready": apply_ready,
        "rom_offset": rom_offset,
        "rom_offset_hex": f"0x{rom_offset:08X}" if rom_offset is not None else "",
        "workbench_item_id": item_id,
        "source_path": source_path,
        "edit_path": edit_path,
        "tile_map_path": tile_map_path,
        "asset_source_path": asset_source,
        "asset_edit_path": asset_edit,
        "text_seen": text_seen,
        "korean_goal": korean_goal,
        "notes": notes,
    }


def build_targets() -> list[dict]:
    images = workbench_item_by_id()
    screen_order = screen_order_by_key()
    targets: list[dict] = []

    def image_item_target(item_id: str, target_id: str, label: str, text_seen: str, korean_goal: str, notes: str) -> None:
        item = images.get(item_id, {})
        source = item.get("source_preview_path", "")
        targets.append(
            target(
                target_id=target_id,
                label=label,
                kind="rom_image_block",
                status="registered_in_gui",
                source_path=source,
                edit_path=item.get("source_download_path", source),
                rom_offset=int(item.get("candidate_gallery", [{}])[0].get("offset") or 0) or None,
                item_id=item_id,
                text_seen=text_seen,
                korean_goal=korean_goal,
                notes=notes,
                apply_ready=item.get("replacement_target") is not False,
            )
        )

    image_item_target(
        "image:field_alchemy_label_005323AC",
        "field_obj_alchemy_label",
        "필드 OBJ 라벨 錬成",
        "錬成",
        "연성",
        "사용자 ss1 OBJ 레이어에서 실제 표시 확인. LZ77 이미지 블록 후보로 GUI에 등록되어 있다.",
    )
    image_item_target(
        "image:field_label_0053257C",
        "field_obj_item_label",
        "필드 OBJ 라벨 アイテム",
        "アイテム",
        "아이템",
        "사용자 ss2 OBJ 레이어에서 실제 표시 확인. 기존 판독 アセやし는 픽셀 폰트의 アイテム 오독으로 정정했다.",
    )
    image_item_target(
        "image:field_status_label_00532764",
        "field_menu_status_label",
        "필드/메뉴 라벨 ステータス",
        "ステータス",
        "상태",
        "주변 LZ77 스캔으로 얻은 메뉴 라벨 후보. 실제 화면 추가 확인 시 우선 검증 대상.",
    )
    image_item_target(
        "image:field_save_label_0053293C",
        "field_menu_save_label",
        "필드/메뉴 라벨 セーブ",
        "セーブ",
        "저장",
        "주변 LZ77 스캔으로 얻은 메뉴 라벨 후보. 실제 화면 추가 확인 시 우선 검증 대상.",
    )

    battle_command_targets = [
        (
            "image:raw4bpp:003ABF5C",
            "battle_bottom_attack_command",
            "전투 하단 커맨드 こうげき",
            "こうげき",
            "공격",
        ),
        (
            "image:raw4bpp:003AC0DC",
            "battle_bottom_notebook_command",
            "전투 하단 커맨드 てちょう",
            "てちょう",
            "수첩",
        ),
        (
            "image:raw4bpp:003AC25C",
            "battle_bottom_alchemy_command",
            "전투 하단 커맨드 れんせい",
            "れんせい",
            "연성",
        ),
        (
            "image:raw4bpp:003AC3DC",
            "battle_bottom_item_command",
            "전투 하단 커맨드 アイテム",
            "アイテム",
            "아이템",
        ),
        (
            "image:raw4bpp:003AC55C",
            "battle_bottom_special_command",
            "전투 하단 커맨드 ひっさつ",
            "ひっさつ",
            "필살기",
        ),
    ]
    for item_id, target_id, label, text_seen, korean_goal in battle_command_targets:
        image_item_target(
            item_id,
            target_id,
            label,
            text_seen,
            korean_goal,
            "전투 하단 버튼은 BG1 타일맵이 같은 VRAM 슬롯을 가리키고, 원본 픽셀은 ROM raw 4bpp 0x180바이트 블록에서 복사된다. GUI 업로드 시 같은 오프셋에 직접 적용한다.",
        )

    image_item_target(
        "image:rle_screen_order_focus:current_review_ss6:frame_000006:bg1:003A3540:book_right_tabs",
        "card_book_right_category_tabs",
        "카드 책자 오른쪽 탭 金属/石/自然/無機",
        "金属 / 石 / 自然 / 無機",
        "금속 / 돌 / 자연 / 무기",
        "ss6~ss9 책자 오른쪽 세로 탭 4개. RLE 0x003A3540 전체 카드 리스트 블록에서 오른쪽 탭 영역만 분리한 GUI 직접 교체 항목.",
    )

    image_item_target(
        "image:rle:007E9404",
        "title_new_game",
        "타이틀 はじめから",
        "はじめから",
        "처음부터",
        "타이틀 RLE 블록을 32열 화면형 레이아웃으로 재추출한 4배 편집 PNG. GUI 업로드 시 same-slot RLE 적용 대상.",
    )
    image_item_target(
        "image:rle:007E95E0",
        "title_continue",
        "타이틀 つづきから",
        "つづきから",
        "이어하기",
        "타이틀 RLE 블록을 32열 화면형 레이아웃으로 재추출한 4배 편집 PNG. GUI 업로드 시 same-slot RLE 적용 대상.",
    )
    image_item_target(
        "image:rle:007E97A4",
        "title_link",
        "타이틀 通信",
        "通信",
        "통신",
        "타이틀 RLE 블록을 32열 화면형 레이아웃으로 재추출한 4배 편집 PNG. GUI 업로드 시 same-slot RLE 적용 대상.",
    )

    screen_targets = [
        (
            ("current_review_ss2", "frame_000002", 0, 0x003ABB9C),
            "battle_confirm_ok_yes_no_popup",
            "전투 확인 팝업 OK?/はい/いいえ",
            "OK? / はい / いいえ",
            "OK? / 예 / 아니요",
            "사용자가 제공한 current_review ss2에서 확인. 화면순 RLE 편집 PNG와 tile_map이 정상 생성되어 GUI 직접 교체 대상으로 등록한다.",
            True,
        ),
        (
            ("no_entry8_latest_ss1", "frame_007084", 0, 0x003AF23C),
            "battle_popup_alchemy_commands",
            "전투 팝업 錬成/つかう/すてる/もどる",
            "錬成 / つかう / すてる / もどる",
            "연성 / 사용 / 버리기 / 돌아가기",
            "화면순 RLE 편집 및 적용 no-op 테스트 통과.",
            True,
        ),
        (
            ("no_entry8_latest_ss1", "frame_007084", 1, 0x003A206C),
            "battle_card_alchemy_panel",
            "전투 카드 패널 2枚",
            "2枚",
            "2장",
            "화면순 RLE 편집 및 적용 no-op 테스트 통과. CARD/ALCHEMY는 영어 워드마크라 번역 대상에서 제외하고, 일본어 `枚`만 실제 한글화 대상으로 본다.",
            True,
        ),
        (
            ("no_entry8_latest_ss3", "frame_009730", 1, 0x003A3540),
            "card_list_frame_controls",
            "카드 리스트 いいえ UI",
            "いいえ",
            "아니요",
            "화면순 추출 및 no-op 적용 확인 완료. ID/BACK/NEXT는 영어 워드마크라 번역 대상에서 제외하고, 일본어 `いいえ`만 실제 한글화 대상으로 본다.",
            True,
        ),
        (
            ("no_entry8_latest_ss3", "frame_009730", 1, 0x003A5E50),
            "card_list_iie_variant_003A5E50",
            "카드 리스트 いいえ UI 변형 1",
            "いいえ",
            "아니요",
            "주변 RLE 확장 추출에서 확인한 카드 리스트 UI 변형. 영어 ID/BACK/NEXT는 제외하고 일본어 `いいえ`만 실제 한글화 대상으로 본다.",
            True,
        ),
        (
            ("no_entry8_latest_ss3", "frame_009730", 1, 0x003A6E24),
            "card_list_iie_variant_003A6E24",
            "카드 리스트 いいえ UI 변형 2",
            "いいえ",
            "아니요",
            "주변 RLE 확장 추출에서 확인한 카드 리스트 UI 변형. 영어 ID/BACK/NEXT는 제외하고 일본어 `いいえ`만 실제 한글화 대상으로 본다.",
            True,
        ),
        (
            ("no_entry8_latest_ss3", "frame_009730", 1, 0x003A7C3C),
            "card_list_iie_variant_003A7C3C",
            "카드 리스트 いいえ UI 변형 3",
            "いいえ",
            "아니요",
            "주변 RLE 확장 추출에서 확인한 카드 리스트 UI 변형. 영어 ID/BACK/NEXT는 제외하고 일본어 `いいえ`만 실제 한글화 대상으로 본다.",
            True,
        ),
        (
            ("no_entry8_latest_ss3", "frame_009730", 1, 0x003A8894),
            "card_list_iie_variant_003A8894",
            "카드 리스트 いいえ UI 변형 4",
            "いいえ",
            "아니요",
            "주변 RLE 확장 추출에서 확인한 카드 리스트 UI 변형. 영어 ID/BACK/NEXT는 제외하고 일본어 `いいえ`만 실제 한글화 대상으로 본다.",
            True,
        ),
        (
            ("no_entry8_latest_ss3", "frame_009730", 1, 0x003A9624),
            "card_list_iie_variant_003A9624",
            "카드 리스트 いいえ UI 변형 5",
            "いいえ",
            "아니요",
            "주변 RLE 확장 추출에서 확인한 카드 리스트 UI 변형. 영어 ID/BACK/NEXT는 제외하고 일본어 `いいえ`만 실제 한글화 대상으로 본다.",
            True,
        ),
        (
            ("no_entry8_latest_ss3", "frame_009730", 1, 0x003AA4C0),
            "card_list_iie_variant_003AA4C0",
            "카드 리스트 いいえ UI 변형 6",
            "いいえ",
            "아니요",
            "주변 RLE 확장 추출에서 확인한 카드 리스트 UI 변형. 영어 ID/BACK/NEXT는 제외하고 일본어 `いいえ`만 실제 한글화 대상으로 본다.",
            True,
        ),
        (
            ("timeline_with_rle", "frame_001200", 0, 0x007E0000),
            "title_logo_copyright",
            "타이틀 로고/부제",
            "鋼の錬金術師 / 迷走の輪舞曲",
            "강철의 연금술사 / 미주의 윤무곡 또는 확정 제목",
            "화면순 RLE 편집 및 적용 no-op 테스트 통과. 저작권/영문 표기는 제외하고 일본어 로고/부제만 실제 한글화 대상으로 본다.",
            True,
        ),
    ]
    for key, target_id, label, text_seen, korean_goal, notes, apply_ready in screen_targets:
        item = screen_order.get(key, {})
        if not item:
            continue
        if not item.get("replacement_target"):
            continue
        targets.append(
            target(
                target_id=target_id,
                label=label,
                kind="runtime_rle_screen_order",
                status="registered_in_gui",
                source_path=item.get("source_download_path") or item.get("editable_preview_path", ""),
                edit_path=item.get("source_download_path", ""),
                tile_map_path=item.get("tile_map_path", ""),
                rom_offset=key[3],
                item_id=(
                    f"image:rle_screen_order:{key[0]}:{key[1]}:bg{key[2]}:{key[3]:08X}"
                ),
                text_seen=text_seen,
                korean_goal=korean_goal,
                notes=notes,
                apply_ready=True,
            )
        )

    return targets


def build_contact_sheet(targets: list[dict]) -> str:
    thumbs: list[Image.Image] = []
    for index, item in enumerate(targets, start=1):
        path = ROOT / (item.get("asset_source_path") or item.get("source_path", ""))
        if not path.exists():
            continue
        image = Image.open(path).convert("RGB")
        image.thumbnail((260, 150), Image.Resampling.NEAREST)
        canvas = Image.new("RGB", (280, 215), (16, 16, 18))
        canvas.paste(image, ((280 - image.width) // 2, 0))
        draw = ImageDraw.Draw(canvas)
        apply = "apply" if item["apply_ready"] else item["status"]
        label = item["label"][:26]
        text = f"{index:02d} {item['target_id']}\n{label}\n{item['rom_offset_hex']} {apply}"
        draw.text((6, 156), text, fill=(240, 240, 240))
        thumbs.append(canvas)
    cols = 3
    rows = (len(thumbs) + cols - 1) // cols
    sheet = Image.new("RGB", (cols * 280, rows * 215), (8, 8, 10))
    for index, thumb in enumerate(thumbs):
        sheet.paste(thumb, ((index % cols) * 280, (index // cols) * 215))
    out = OUT_DIR / "actual_localization_targets_contact_sheet.png"
    out.parent.mkdir(parents=True, exist_ok=True)
    sheet.save(out)
    return str(out.relative_to(ROOT))


def write_markdown(targets: list[dict], contact_sheet: str) -> None:
    lines = [
        "# Actual Localization Tilemap/Image Targets",
        "",
        "실제 화면에서 일본어 UI가 보이는 그래픽/타일맵 후보만 추린 목록입니다. 영어 워드마크는 번역 대상에서 제외합니다.",
        "",
        f"- contact sheet: `{contact_sheet}`",
        f"- total targets: `{len(targets)}`",
        "",
        "| id | label | status | offset | seen | goal |",
        "| --- | --- | --- | --- | --- | --- |",
    ]
    for item in targets:
        lines.append(
            "| `{target_id}` | {label} | `{status}` | `{offset}` | {seen} | {goal} |".format(
                target_id=item["target_id"],
                label=item["label"],
                status=item["status"],
                offset=item["rom_offset_hex"] or "-",
                seen=item["text_seen"],
                goal=item["korean_goal"],
            )
        )
    lines.extend(["", "## Notes", ""])
    for item in targets:
        lines.append(f"- `{item['target_id']}`: {item['notes']}")
    (OUT_DIR / "actual_localization_targets.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    targets = build_targets()
    contact_sheet = build_contact_sheet(targets)
    write_json(OUT_DIR / "actual_localization_targets.json", targets)
    write_markdown(targets, contact_sheet)
    print(f"targets: {len(targets)}")
    print(f"contact: {ROOT / contact_sheet}")
    print(f"manifest: {OUT_DIR / 'actual_localization_targets.json'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
