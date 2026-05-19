#!/usr/bin/env python3

from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import sys
from datetime import datetime
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
WORKBENCH_DIR = ROOT / "confirmed_data" / "localization_workbench"
DATASET_PATH = WORKBENCH_DIR / "workbench_dataset.json"
BACKUP_ROOT = ROOT / "confirmed_data" / "localization_workbench_backups"

BACKUP_TARGETS = [
    ROOT / "confirmed_data" / "localization_workbench",
    ROOT / "confirmed_data" / "translation_worksets",
    ROOT / "confirmed_data" / "translation_workspace" / "registry_a_entry8_clusters",
    ROOT / "confirmed_data" / "extracted_texts",
    ROOT / "confirmed_data" / "font_assets" / "translation_normalization_profile.json",
]

CRITICAL_FIELDS = [
    "translation",
    "agent_draft",
    "agent_comment",
    "manual_locked",
    "progress_status",
    "review_status",
]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Safely sync GUI workbench edits back to source JSON, rebuild the "
            "localization workbench dataset, and restore from backup if existing "
            "translation/review state unexpectedly changes."
        )
    )
    parser.add_argument(
        "--no-restore-on-failure",
        action="store_true",
        help="leave changed files in place if validation fails instead of restoring the backup",
    )
    parser.add_argument(
        "--allow-removed-items",
        action="store_true",
        help="do not fail if existing text item ids disappear after rebuild",
    )
    parser.add_argument(
        "--allow-critical-field-drift",
        action="store_true",
        help="do not fail when translation/agent/review fields differ after rebuild",
    )
    return parser.parse_args()


def rel(path: Path) -> Path:
    return path.relative_to(ROOT)


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def copy_target_to_backup(source: Path, backup_dir: Path) -> None:
    if not source.exists():
        return
    destination = backup_dir / rel(source)
    destination.parent.mkdir(parents=True, exist_ok=True)
    if source.is_dir():
        shutil.copytree(source, destination)
    else:
        shutil.copy2(source, destination)


def create_backup() -> Path:
    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_dir = BACKUP_ROOT / f"workbench_rebuild_{stamp}"
    backup_dir.mkdir(parents=True, exist_ok=False)
    for target in BACKUP_TARGETS:
        copy_target_to_backup(target, backup_dir)
    return backup_dir


def restore_backup(backup_dir: Path) -> None:
    for target in reversed(BACKUP_TARGETS):
        backup_target = backup_dir / rel(target)
        if not backup_target.exists():
            continue
        if target.exists():
            if target.is_dir():
                shutil.rmtree(target)
            else:
                target.unlink()
        target.parent.mkdir(parents=True, exist_ok=True)
        if backup_target.is_dir():
            shutil.copytree(backup_target, target)
        else:
            shutil.copy2(backup_target, target)


def run_step(command: list[str]) -> subprocess.CompletedProcess[str]:
    print(f"$ {' '.join(command)}", flush=True)
    completed = subprocess.run(
        command,
        cwd=ROOT,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
    )
    print(completed.stdout, end="")
    if completed.returncode != 0:
        raise subprocess.CalledProcessError(completed.returncode, command, output=completed.stdout)
    return completed


def item_snapshot(dataset: dict[str, Any]) -> dict[str, dict[str, Any]]:
    snapshot: dict[str, dict[str, Any]] = {}
    for item in dataset.get("items", []):
        item_id = item.get("item_id")
        if not item_id or item.get("category_id") == "image_review_units":
            continue
        snapshot[item_id] = {field: item.get(field) for field in CRITICAL_FIELDS}
    return snapshot


def validate_rebuild(before: dict[str, dict[str, Any]], after: dict[str, dict[str, Any]], args: argparse.Namespace) -> dict[str, Any]:
    removed = sorted(set(before) - set(after))
    field_drifts: list[dict[str, Any]] = []
    if not args.allow_critical_field_drift:
        for item_id in sorted(set(before) & set(after)):
            for field in CRITICAL_FIELDS:
                before_value = before[item_id].get(field)
                after_value = after[item_id].get(field)
                if before_value != after_value:
                    field_drifts.append(
                        {
                            "item_id": item_id,
                            "field": field,
                            "before": before_value,
                            "after": after_value,
                        }
                    )
                    break

    failures: list[str] = []
    if removed and not args.allow_removed_items:
        failures.append(f"existing text items disappeared: {len(removed)}")
    if field_drifts:
        failures.append(f"critical item fields changed: {len(field_drifts)}")

    return {
        "ok": not failures,
        "failures": failures,
        "before_count": len(before),
        "after_count": len(after),
        "new_count": len(set(after) - set(before)),
        "removed_count": len(removed),
        "removed_examples": removed[:50],
        "critical_field_drift_count": len(field_drifts),
        "critical_field_drift_examples": field_drifts[:50],
    }


def main() -> int:
    args = parse_args()
    if not DATASET_PATH.exists():
        raise SystemExit(f"missing dataset: {DATASET_PATH}")

    before_dataset = load_json(DATASET_PATH)
    before_snapshot = item_snapshot(before_dataset)
    backup_dir = create_backup()
    print(f"backup: {backup_dir}")

    report_path = backup_dir / "all_in_one_report.json"
    report: dict[str, Any] = {
        "backup_dir": str(backup_dir),
        "steps": [],
    }

    try:
        for command in (
            [sys.executable, "scripts/sync_workbench_to_sources.py"],
            [sys.executable, "scripts/build_localization_workbench_dataset.py"],
        ):
            completed = run_step(command)
            report["steps"].append(
                {
                    "command": command,
                    "returncode": completed.returncode,
                    "output": completed.stdout,
                }
            )

        after_dataset = load_json(DATASET_PATH)
        after_snapshot = item_snapshot(after_dataset)
        validation = validate_rebuild(before_snapshot, after_snapshot, args)
        report["validation"] = validation
        write_json(report_path, report)

        if not validation["ok"]:
            print("validation failed:")
            for failure in validation["failures"]:
                print(f"- {failure}")
            print(f"report: {report_path}")
            if args.no_restore_on_failure:
                print("left changed files in place because --no-restore-on-failure was set")
            else:
                restore_backup(backup_dir)
                print(f"restored backup: {backup_dir}")
            return 2

        print("validation ok")
        print(f"text items before/after: {validation['before_count']} -> {validation['after_count']}")
        print(f"new text items: {validation['new_count']}")
        print(f"report: {report_path}")
        return 0
    except Exception as exc:
        report["exception"] = repr(exc)
        write_json(report_path, report)
        print(f"failed: {exc}", file=sys.stderr)
        print(f"report: {report_path}", file=sys.stderr)
        if not args.no_restore_on_failure:
            restore_backup(backup_dir)
            print(f"restored backup: {backup_dir}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
