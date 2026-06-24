#!/usr/bin/env python3
"""Non-destructive integrity checks for the GUI localization workflow."""

from __future__ import annotations

import argparse
import importlib.util
import json
import sys
from pathlib import Path
from typing import Any


sys.dont_write_bytecode = True

ROOT = Path(__file__).resolve().parents[2]


def root_path(relative: str) -> Path:
    return ROOT / relative


def root_relative(path: Path) -> str:
    return path.relative_to(ROOT).as_posix()


def load_json(path: Path) -> Any:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


class Audit:
    def __init__(self) -> None:
        self.errors: list[str] = []
        self.warnings: list[str] = []
        self.summary: dict[str, Any] = {}

    def require_path(self, relative: str, label: str) -> None:
        path = root_path(relative)
        if not path.exists():
            self.errors.append(f"missing {label}: {relative}")

    def warn_path(self, relative: str, label: str) -> None:
        path = root_path(relative)
        if not path.exists():
            self.warnings.append(f"missing optional {label}: {relative}")

    def require_json(self, relative: str, label: str) -> Any | None:
        path = root_path(relative)
        if not path.exists():
            self.errors.append(f"missing {label}: {relative}")
            return None
        try:
            return load_json(path)
        except Exception as exc:  # pragma: no cover - diagnostic path
            self.errors.append(f"invalid JSON in {relative}: {exc}")
            return None

    def compile_python(self, relative: str) -> None:
        path = root_path(relative)
        if not path.exists():
            self.errors.append(f"missing Python script: {relative}")
            return
        try:
            compile(path.read_text(encoding="utf-8"), str(path), "exec")
        except SyntaxError as exc:
            self.errors.append(f"syntax error in {relative}: {exc}")


def audit_required_paths(audit: Audit) -> None:
    required_paths = [
        ("tools/localization_workbench.html", "localization workbench HTML"),
        ("tools/glyph_editor.html", "glyph editor HTML"),
        ("confirmed_data/localization_workbench/workbench_dataset.json", "GUI dataset"),
        ("confirmed_data/localization_workbench/image_replacements.json", "image replacement state"),
        ("confirmed_data/localization_workbench/progress_state.json", "GUI progress state"),
        ("confirmed_data/localization_workbench/uploaded_image_replacements", "uploaded image replacements"),
        ("analysis/generated_workbenches/current_review/prepared.tbl", "current review prepared table"),
        ("patched_roms/current_review/current_review_font_ready.gba", "font-ready review ROM"),
        ("patched_roms/current_review/hnr_localization_review.gba", "current review ROM"),
        ("Hagane no Renkinjutsushi - Meisou no Rondo (Japan).gba", "source ROM"),
    ]
    for relative, label in required_paths:
        audit.require_path(relative, label)

    optional_local_paths = [
        ("patched_roms/current_review/current_review_text_fast_translated.gba", "latest fast text output ROM"),
        ("local_roms/english_patched/Fullmetal Alchemist Stray Rondo (English Patched v0.02).gba", "English HUD reference ROM"),
    ]
    for relative, label in optional_local_paths:
        audit.warn_path(relative, label)

    release_paths = [
        "releases/hnr_mnr_ko_v0.1.0/hnr_mnr_ko_v0.1.0.bps",
        "releases/hnr_mnr_ko_v0.1.0.zip",
        "releases/hnr_mnr_ko_v0.1.0/README_ko.md",
        "releases/hnr_mnr_ko_v0.1.0/NOTICE.txt",
        "releases/hnr_mnr_ko_v0.1.0/checksums.sha256",
        "releases/hnr_mnr_ko_v0.1.0/LICENSES/Galmuri_OFL_1.1.txt",
    ]
    for relative in release_paths:
        audit.warn_path(relative, "existing release artifact")


def audit_scripts(audit: Audit) -> None:
    critical_python = [
        "scripts/audit/audit_gui_workflow_integrity.py",
        "scripts/audit_gui_workflow_integrity.py",
        "scripts/run_localization_workbench.py",
        "scripts/build_localization_review_rom.py",
        "scripts/build_localization_workbench_dataset.py",
        "scripts/rebuild_localization_workbench_all_in_one.py",
        "scripts/sync_workbench_to_sources.py",
        "scripts/import_translation_agent_results.py",
        "scripts/apply_image_replacements.py",
        "scripts/create_bps_patch.py",
        "scripts/extract_battle_hud_name_table.py",
        "scripts/apply_english_battle_hud_font.py",
        "scripts/apply_common_hud_korean_slot_patch.py",
        "scripts/apply_battle_hud_name_font.py",
        "scripts/run_glyph_editor.py",
    ]
    for relative in critical_python:
        audit.compile_python(relative)

    critical_shell = [
        "scripts/build_translated_rom_with_active_atlas.sh",
        "scripts/rebuild_active_workbenches_from_atlas.sh",
    ]
    for relative in critical_shell:
        audit.require_path(relative, "workflow shell script")


def audit_gitignore(audit: Audit) -> None:
    gitignore_path = root_path(".gitignore")
    if not gitignore_path.exists():
        audit.errors.append("missing .gitignore")
        return
    text = gitignore_path.read_text(encoding="utf-8")
    required_patterns = ["*.gba", "*.sav", "*.sgm", "*.state", "*.srm", "*.ips", "*.ups", "*.bps", "!releases/**/*.bps"]
    missing = [pattern for pattern in required_patterns if pattern not in text]
    if missing:
        audit.errors.append(f".gitignore missing ROM/save/patch patterns: {', '.join(missing)}")


def audit_workbench_data(audit: Audit) -> None:
    dataset = audit.require_json("confirmed_data/localization_workbench/workbench_dataset.json", "GUI dataset")
    image_replacements = audit.require_json("confirmed_data/localization_workbench/image_replacements.json", "image replacement state")
    progress = audit.require_json("confirmed_data/localization_workbench/progress_state.json", "GUI progress state")

    if not isinstance(dataset, dict):
        audit.errors.append("workbench_dataset.json is not an object")
        return
    items = dataset.get("items")
    categories = dataset.get("categories")
    if not isinstance(items, list) or not items:
        audit.errors.append("workbench_dataset.json has no non-empty items list")
        return
    if not isinstance(categories, list) or not categories:
        audit.errors.append("workbench_dataset.json has no non-empty categories list")

    item_ids = {str(item.get("item_id")) for item in items if item.get("item_id")}
    image_item_count = sum(1 for item in items if str(item.get("item_id", "")).startswith("image:") or "image" in str(item.get("category_id", "")))

    if not isinstance(image_replacements, list):
        audit.errors.append("image_replacements.json is not a list")
        return

    missing_dataset_items = [
        str(item.get("item_id"))
        for item in image_replacements
        if item.get("item_id") and str(item.get("item_id")) not in item_ids
    ]
    if missing_dataset_items:
        audit.errors.append(
            "image replacements missing from workbench dataset: "
            + ", ".join(missing_dataset_items[:10])
        )

    missing_paths: list[str] = []
    edited_count = 0
    for item in image_replacements:
        item_id = str(item.get("item_id", "<unknown>"))
        status = item.get("progress_status")
        replacement_path = str(item.get("replacement_path") or "").strip()
        if status == "edited":
            edited_count += 1
        for field in ("source_download_path", "source_preview_path"):
            value = str(item.get(field) or "").strip()
            if value and not root_path(value).exists():
                missing_paths.append(f"{item_id} {field}: {value}")
        if replacement_path and not root_path(replacement_path).exists():
            missing_paths.append(f"{item_id} replacement_path: {replacement_path}")
        if status == "edited" and not replacement_path:
            missing_paths.append(f"{item_id} edited item has empty replacement_path")

    if missing_paths:
        audit.errors.append("missing image workflow paths: " + "; ".join(missing_paths[:10]))

    if isinstance(progress, dict):
        last_built_rom = str(progress.get("last_built_rom") or "").strip()
        if last_built_rom and not root_path(last_built_rom).exists():
            audit.errors.append(f"progress_state last_built_rom does not exist: {last_built_rom}")
    else:
        audit.errors.append("progress_state.json is not an object")

    audit.summary.update(
        {
            "workbench_items": len(items),
            "workbench_categories": len(categories) if isinstance(categories, list) else 0,
            "workbench_image_items": image_item_count,
            "image_replacement_items": len(image_replacements),
            "edited_image_replacements": edited_count,
        }
    )


def audit_patch_roundtrip(audit: Audit) -> None:
    script_path = root_path("scripts/create_bps_patch.py")
    if not script_path.exists():
        audit.errors.append("missing BPS patch script")
        return
    spec = importlib.util.spec_from_file_location("create_bps_patch_audit", script_path)
    if spec is None or spec.loader is None:
        audit.errors.append("could not load BPS patch script")
        return
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    source = bytes(range(64))
    target = source[:8] + b"KOR" + source[11:] + b"!"
    patch = module.create_patch(source, target, b"audit")
    verified = module.apply_patch(source, patch)
    if verified != target:
        audit.errors.append("BPS patch roundtrip failed")
    else:
        audit.summary["bps_roundtrip_bytes"] = len(patch)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--json", action="store_true", help="Print machine-readable summary.")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    audit = Audit()
    audit_required_paths(audit)
    audit_scripts(audit)
    audit_gitignore(audit)
    audit_workbench_data(audit)
    audit_patch_roundtrip(audit)

    result = {
        "ok": not audit.errors,
        "summary": audit.summary,
        "warnings": audit.warnings,
        "errors": audit.errors,
    }
    if args.json:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        status = "ok" if result["ok"] else "failed"
        print(f"gui workflow integrity: {status}")
        for key, value in audit.summary.items():
            print(f"- {key}: {value}")
        for warning in audit.warnings:
            print(f"warning: {warning}")
        for error in audit.errors:
            print(f"error: {error}")
    return 0 if result["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
