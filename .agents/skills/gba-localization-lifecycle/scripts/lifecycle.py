#!/usr/bin/env python3
"""Initialize and validate the repository-local GBA localization lifecycle."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import subprocess
import sys
import tempfile
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Optional


CONTROL_DIR = Path(".gba-localization")
PROJECT_FILE = CONTROL_DIR / "project.json"
STATE_FILE = CONTROL_DIR / "lifecycle.json"
CLAIM_FILE = CONTROL_DIR / "active_claim.json"
PHASES = (
    "bootstrap",
    "rom_analysis",
    "text",
    "font",
    "images",
    "translate",
    "build_qa",
    "release",
)
PHASE_SKILLS = {
    "bootstrap": "gba-localization-bootstrap",
    "rom_analysis": "gba-localization-rom-analysis",
    "text": "gba-localization-text",
    "font": "gba-localization-font",
    "images": "gba-localization-images",
    "translate": "gba-localization-translate",
    "build_qa": "gba-localization-build-qa",
    "release": "gba-localization-release",
}
DEPENDENCIES = {
    "bootstrap": (),
    "rom_analysis": ("bootstrap",),
    "text": ("rom_analysis",),
    "font": ("rom_analysis",),
    "images": ("rom_analysis",),
    "translate": ("text",),
    "build_qa": ("font", "translate"),
    "release": ("images", "build_qa"),
}
STATUSES = {"not_started", "in_progress", "blocked", "ready", "complete"}
FORBIDDEN_TRACKED_SUFFIXES = {
    ".gba",
    ".sav",
    ".sgm",
    ".state",
    ".srm",
}
MACHINE_PATH_MARKERS = (
    str(Path("/", "Users")) + os.sep,
    str(Path("/", "home")) + os.sep,
    str(Path("/", "private", "tmp")) + os.sep,
    "\\Users\\",
)


class LifecycleError(RuntimeError):
    pass


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def parse_utc(value: str) -> datetime:
    try:
        parsed = datetime.fromisoformat(value)
    except ValueError as exc:
        raise LifecycleError(f"invalid UTC timestamp: {value}") from exc
    if parsed.tzinfo is None:
        raise LifecycleError(f"timestamp has no timezone: {value}")
    return parsed.astimezone(timezone.utc)


def load_json(path: Path) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise LifecycleError(f"missing required file: {path}") from exc
    except json.JSONDecodeError as exc:
        raise LifecycleError(f"invalid JSON in {path}: {exc}") from exc
    if not isinstance(value, dict):
        raise LifecycleError(f"expected JSON object: {path}")
    return value


def atomic_write_json(path: Path, value: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = json.dumps(value, ensure_ascii=False, indent=2) + "\n"
    with tempfile.NamedTemporaryFile(
        "w",
        encoding="utf-8",
        dir=path.parent,
        prefix=f".{path.name}.",
        delete=False,
    ) as handle:
        handle.write(payload)
        temp_path = Path(handle.name)
    os.replace(temp_path, path)


def write_new_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    try:
        with path.open("x", encoding="utf-8") as handle:
            handle.write(content)
    except FileExistsError as exc:
        raise LifecycleError(f"refusing to overwrite existing file: {path}") from exc


def ensure_relative(path_text: str, label: str) -> Path:
    path = Path(path_text)
    if path.is_absolute() or ".." in path.parts:
        raise LifecycleError(f"{label} must be a repository-relative path: {path_text}")
    return path


def is_within(path: Path, root: Path) -> bool:
    try:
        path.relative_to(root)
    except ValueError:
        return False
    return True


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def run_git(root: Path, *args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ("git", *args),
        cwd=root,
        text=True,
        capture_output=True,
        check=False,
    )


def active_claim(root: Path) -> Optional[dict[str, Any]]:
    path = root / CLAIM_FILE
    if not path.exists():
        return None
    claim = load_json(path)
    owner = claim.get("owner")
    phase = claim.get("phase")
    expires_at = claim.get("expires_at")
    if not isinstance(owner, str) or not owner:
        raise LifecycleError("active claim has no owner")
    if phase not in PHASES:
        raise LifecycleError("active claim has an invalid phase")
    if not isinstance(expires_at, str):
        raise LifecycleError("active claim has no expiry")
    claim["expired"] = parse_utc(expires_at) <= datetime.now(timezone.utc)
    return claim


def default_manifests(now: str) -> dict[Path, dict[str, Any]]:
    return {
        CONTROL_DIR / "manifests" / "artifacts.json": {
            "schema_version": 1,
            "updated_at": now,
            "items": [],
        },
        CONTROL_DIR / "manifests" / "text_sources.json": {
            "schema_version": 1,
            "updated_at": now,
            "families": [],
        },
        CONTROL_DIR / "manifests" / "font.json": {
            "schema_version": 1,
            "updated_at": now,
            "status": "unknown",
            "code_space": {},
            "glyph_storage": {},
            "renderer": {},
            "atlas": {},
            "runtime_tests": [],
        },
        CONTROL_DIR / "manifests" / "image_targets.json": {
            "schema_version": 1,
            "updated_at": now,
            "inventory_complete": False,
            "targets": [],
        },
        CONTROL_DIR / "manifests" / "translation.json": {
            "schema_version": 1,
            "updated_at": now,
            "source_of_truth": "",
            "apply_priority": [
                "manual_locked_translation",
                "translation",
                "agent_draft",
                "original",
            ],
            "worksets": [],
        },
        CONTROL_DIR / "manifests" / "qa_cases.json": {
            "schema_version": 1,
            "updated_at": now,
            "build_id": "",
            "cases": [],
        },
        CONTROL_DIR / "manifests" / "release.json": {
            "schema_version": 1,
            "updated_at": now,
            "releases": [],
        },
    }


def load_gate_manifest(
    root: Path, filename: str, errors: list[str]
) -> dict[str, Any]:
    path = root / CONTROL_DIR / "manifests" / filename
    try:
        return load_json(path)
    except LifecycleError as exc:
        errors.append(str(exc))
        return {}


def phase_gate_errors(root: Path, phase: str) -> list[str]:
    errors: list[str] = []
    try:
        project = load_json(root / PROJECT_FILE)
    except LifecycleError as exc:
        return [str(exc)]

    if phase == "bootstrap":
        source_rom = project.get("source_rom", {})
        if not isinstance(source_rom, dict):
            return ["bootstrap requires project.source_rom"]
        try:
            source_relative = ensure_relative(
                str(source_rom.get("path", "")), "source ROM"
            )
        except LifecycleError as exc:
            return [str(exc)]
        source_path = (root / source_relative).resolve()
        if not is_within(source_path, root):
            errors.append("bootstrap source ROM resolves outside the repository")
        elif not source_path.is_file():
            errors.append("bootstrap requires the source ROM to exist locally")
        else:
            expected_hash = source_rom.get("sha256", "")
            if not expected_hash:
                errors.append("bootstrap requires a source ROM SHA-256")
            elif sha256_file(source_path) != expected_hash:
                errors.append("bootstrap source ROM SHA-256 mismatch")
        if (root / ".git").exists():
            ignored = run_git(
                root,
                "check-ignore",
                "-q",
                "--no-index",
                source_relative.as_posix(),
            )
            if ignored.returncode != 0:
                errors.append("bootstrap requires the source ROM path to be ignored")
            tracked = run_git(root, "ls-files", "-z")
            forbidden = [
                path
                for path in tracked.stdout.split("\0")
                if Path(path).suffix.lower() in FORBIDDEN_TRACKED_SUFFIXES
            ]
            if forbidden:
                errors.append("bootstrap forbids tracked runtime files")

    elif phase == "rom_analysis":
        manifest = load_gate_manifest(root, "artifacts.json", errors)
        items = manifest.get("items")
        if not isinstance(items, list) or not items:
            errors.append("rom_analysis requires a non-empty artifact inventory")
        elif any(
            not isinstance(item, dict)
            or not item.get("id")
            or not item.get("role")
            or not item.get("confidence")
            for item in items
        ):
            errors.append(
                "every ROM artifact requires id, role, and confidence fields"
            )

    elif phase == "text":
        manifest = load_gate_manifest(root, "text_sources.json", errors)
        families = manifest.get("families")
        if not isinstance(families, list) or not families:
            errors.append("text requires at least one source family")
        elif any(
            not isinstance(family, dict)
            or not family.get("family_id")
            or not family.get("record_type")
            or not family.get("encoding")
            or not isinstance(family.get("apply_capabilities"), list)
            or not family.get("apply_capabilities")
            or not isinstance(family.get("extract_command"), str)
            or not family.get("extract_command")
            for family in families
        ):
            errors.append(
                "every text family requires family_id, record_type, encoding, "
                "apply_capabilities, and extract_command"
            )
        else:
            for family in families:
                capabilities = family.get("apply_capabilities", [])
                if any(
                    capability
                    not in {"protected", "unknown", "extract_only"}
                    for capability in capabilities
                ) and not family.get("apply_command"):
                    errors.append(
                        f"text family {family['family_id']} needs an apply_command"
                    )
                for key in ("extract_command", "apply_command"):
                    command = family.get(key, "")
                    if command and not isinstance(command, str):
                        errors.append(
                            f"text family {family['family_id']} {key} "
                            "must be a string"
                        )
                    elif any(
                        marker in command for marker in MACHINE_PATH_MARKERS
                    ):
                        errors.append(
                            f"text family {family['family_id']} {key} "
                            "contains a machine-local path"
                        )

    elif phase == "font":
        manifest = load_gate_manifest(root, "font.json", errors)
        for key in ("code_space", "glyph_storage", "renderer", "atlas"):
            if not isinstance(manifest.get(key), dict) or not manifest.get(key):
                errors.append(f"font requires non-empty {key} evidence")
        tests = manifest.get("runtime_tests")
        if not isinstance(tests, list) or not tests:
            errors.append("font requires runtime tests")
        elif any(
            not isinstance(test, dict) or test.get("status") != "passed"
            for test in tests
        ):
            errors.append("all font runtime tests must pass")
        if manifest.get("status") not in {"ready", "complete"}:
            errors.append("font manifest status must be ready or complete")

    elif phase == "images":
        manifest = load_gate_manifest(root, "image_targets.json", errors)
        if manifest.get("inventory_complete") is not True:
            errors.append("images requires inventory_complete=true")
        targets = manifest.get("targets")
        if not isinstance(targets, list):
            errors.append("image targets must be an array")
        else:
            required = (
                "target_id",
                "rom_resource_offset_or_id",
                "compression",
                "screen_order_mapping",
                "palette_source",
                "source_1x_path",
                "replacement_path",
                "allowed_edit_rect",
                "apply_command",
                "verification_command",
                "runtime_evidence_path",
            )
            for target in targets:
                if not isinstance(target, dict):
                    errors.append("image targets must be objects")
                    continue
                if target.get("artifact_role") == "final_replacement":
                    missing = [key for key in required if not target.get(key)]
                    if missing:
                        errors.append(
                            f"final image target is missing: {', '.join(missing)}"
                        )
                    for key in (
                        "screen_order_mapping",
                        "palette_source",
                        "source_1x_path",
                        "replacement_path",
                        "runtime_evidence_path",
                    ):
                        value = target.get(key, "")
                        try:
                            relative = ensure_relative(
                                str(value), f"image target {key}"
                            )
                        except LifecycleError as exc:
                            errors.append(str(exc))
                            continue
                        path = (root / relative).resolve()
                        if not is_within(path, root):
                            errors.append(
                                f"image target {key} resolves outside repository"
                            )
                        elif not path.exists():
                            errors.append(f"image target path is missing: {value}")
                    for key in ("apply_command", "verification_command"):
                        command = target.get(key, "")
                        if any(
                            marker in command for marker in MACHINE_PATH_MARKERS
                        ):
                            errors.append(
                                f"image target {key} contains a machine-local path"
                            )

    elif phase == "translate":
        manifest = load_gate_manifest(root, "translation.json", errors)
        source_of_truth = manifest.get("source_of_truth")
        if not source_of_truth:
            errors.append("translate requires a canonical source_of_truth")
        else:
            try:
                relative = ensure_relative(
                    str(source_of_truth), "translation source_of_truth"
                )
            except LifecycleError as exc:
                errors.append(str(exc))
            else:
                source_path = (root / relative).resolve()
                if not is_within(source_path, root):
                    errors.append(
                        "translation source_of_truth resolves outside repository"
                    )
                elif not source_path.exists():
                    errors.append("translation source_of_truth is missing")
        worksets = manifest.get("worksets")
        if not isinstance(worksets, list) or not worksets:
            errors.append("translate requires at least one workset")
        elif any(
            not isinstance(workset, dict)
            or not workset.get("id")
            or workset.get("status") not in {"reviewed", "manual_locked", "excluded"}
            for workset in worksets
        ):
            errors.append(
                "every translation workset requires id and a release-ready status"
            )

    elif phase == "build_qa":
        manifest = load_gate_manifest(root, "qa_cases.json", errors)
        if not manifest.get("build_id"):
            errors.append("build_qa requires a build_id")
        cases = manifest.get("cases")
        if not isinstance(cases, list) or not cases:
            errors.append("build_qa requires at least one QA case")
        elif any(
            not isinstance(case, dict)
            or not case.get("case_id")
            or case.get("status") not in {"passed", "waived"}
            for case in cases
        ):
            errors.append("all build QA cases must be passed or explicitly waived")

    elif phase == "release":
        manifest = load_gate_manifest(root, "release.json", errors)
        releases = manifest.get("releases")
        if not isinstance(releases, list) or not releases:
            errors.append("release requires a release manifest entry")
        else:
            latest = releases[-1]
            required = (
                "version",
                "patch_path",
                "patch_sha256",
                "source_rom_sha256",
                "output_rom_sha256",
            )
            if not isinstance(latest, dict):
                errors.append("latest release entry must be an object")
            else:
                missing = [key for key in required if not latest.get(key)]
                if missing:
                    errors.append(
                        f"latest release entry is missing: {', '.join(missing)}"
                    )
                if latest.get("roundtrip_verified") is not True:
                    errors.append("release patch round-trip is not verified")
                patch_value = latest.get("patch_path", "")
                try:
                    patch_relative = ensure_relative(
                        str(patch_value), "release patch"
                    )
                except LifecycleError as exc:
                    errors.append(str(exc))
                else:
                    patch_path = (root / patch_relative).resolve()
                    if not is_within(patch_path, root):
                        errors.append("release patch resolves outside repository")
                    elif not patch_path.is_file():
                        errors.append("release patch is missing")
                    elif latest.get("patch_sha256") != sha256_file(patch_path):
                        errors.append("release patch SHA-256 mismatch")
                source_config = project.get("source_rom", {})
                source_hash = (
                    source_config.get("sha256")
                    if isinstance(source_config, dict)
                    else None
                )
                if latest.get("source_rom_sha256") != source_hash:
                    errors.append(
                        "release source ROM hash differs from project source hash"
                    )

    return errors


def command_init(args: argparse.Namespace) -> int:
    root = Path(args.root).resolve()
    if not root.is_dir():
        raise LifecycleError(f"repository root does not exist: {root}")
    if (root / CONTROL_DIR).exists():
        raise LifecycleError(
            "control directory already exists; use status/check or integrate it "
            "manually instead of overwriting it"
        )

    source_relative = ensure_relative(args.source_rom, "source ROM")
    source_path = (root / source_relative).resolve()
    if not is_within(source_path, root):
        raise LifecycleError("source ROM resolves outside the repository")

    now = utc_now()
    source_hash = sha256_file(source_path) if source_path.is_file() else ""
    project = {
        "schema_version": 1,
        "project_name": args.name,
        "target_language": args.target_language,
        "repo_root": ".",
        "source_rom": {
            "path": source_relative.as_posix(),
            "sha256": source_hash,
            "tracked": False,
        },
        "paths": {
            "analysis": "analysis",
            "canonical_data": "localization/data",
            "worksets": "localization/worksets",
            "assets": "localization/assets",
            "runtime_evidence": "localization/evidence",
            "release": "releases",
        },
        "commands": {
            "extract_text": "",
            "build_worksets": "",
            "apply_text": "",
            "apply_images": "",
            "build_review_rom": "",
            "audit": "",
            "create_patch": "",
        },
    }
    lifecycle = {
        "schema_version": 1,
        "updated_at": now,
        "phases": {
            phase: {
                "status": "not_started",
                "evidence": [],
                "blockers": [],
                "notes": [],
                "updated_at": now,
            }
            for phase in PHASES
        },
        "history": [],
    }

    atomic_write_json(root / PROJECT_FILE, project)
    atomic_write_json(root / STATE_FILE, lifecycle)
    for relative, manifest in default_manifests(now).items():
        atomic_write_json(root / relative, manifest)

    retrospective_dir = root / CONTROL_DIR / "retrospective"
    write_new_text(
        retrospective_dir / "decisions.md",
        "# Localization Decisions\n\n"
        "Record durable decisions, rejected alternatives, and the evidence that "
        "changed the workflow.\n",
    )
    write_new_text(
        retrospective_dir / "failure_modes.md",
        "# Project Failure Modes\n\n"
        "Record symptom, cause, prevention, and the reusable rule. Do not paste "
        "raw chat logs or copyrighted game content.\n",
    )

    asset = (
        Path(__file__).resolve().parents[1]
        / "assets"
        / "starter-project"
        / "gitignore.fragment"
    )
    write_new_text(
        root / CONTROL_DIR / "gitignore.fragment",
        asset.read_text(encoding="utf-8"),
    )

    print(f"initialized: {root / CONTROL_DIR}")
    if source_hash:
        print(f"source ROM SHA-256: {source_hash}")
    else:
        print(f"source ROM not found yet: {source_relative.as_posix()}")
    print("next skill: $gba-localization-bootstrap")
    return 0


def collect_checks(root: Path) -> tuple[list[str], list[str]]:
    errors: list[str] = []
    warnings: list[str] = []
    project = load_json(root / PROJECT_FILE)
    lifecycle = load_json(root / STATE_FILE)

    if project.get("schema_version") != 1:
        errors.append("unsupported project schema_version")
    source_rom = project.get("source_rom")
    if not isinstance(source_rom, dict):
        errors.append("project.source_rom must be an object")
    else:
        source_text = source_rom.get("path", "")
        try:
            source_relative = ensure_relative(str(source_text), "source ROM")
        except LifecycleError as exc:
            errors.append(str(exc))
        else:
            source_path = (root / source_relative).resolve()
            if not is_within(source_path, root):
                errors.append("source ROM resolves outside the repository")
            if source_rom.get("tracked") is not False:
                errors.append("project.source_rom.tracked must be false")
            expected_hash = source_rom.get("sha256", "")
            if source_path.is_file():
                actual_hash = sha256_file(source_path)
                if not expected_hash:
                    warnings.append("source ROM exists but SHA-256 is empty")
                elif actual_hash != expected_hash:
                    errors.append("source ROM SHA-256 does not match project.json")
            else:
                warnings.append(f"source ROM is absent locally: {source_relative}")

            if (root / ".git").exists():
                ignored = run_git(
                    root,
                    "check-ignore",
                    "-q",
                    "--no-index",
                    source_relative.as_posix(),
                )
                if ignored.returncode != 0:
                    errors.append(
                        f"source ROM path is not ignored: {source_relative.as_posix()}"
                    )

    paths = project.get("paths", {})
    if not isinstance(paths, dict):
        errors.append("project.paths must be an object")
    else:
        for key, value in paths.items():
            try:
                relative = ensure_relative(str(value), f"project.paths.{key}")
            except LifecycleError as exc:
                errors.append(str(exc))
                continue
            if not is_within((root / relative).resolve(), root):
                errors.append(f"project.paths.{key} resolves outside the repository")

    commands = project.get("commands", {})
    if not isinstance(commands, dict):
        errors.append("project.commands must be an object")
    else:
        for key, value in commands.items():
            if not isinstance(value, str):
                errors.append(f"project.commands.{key} must be a string")
            elif any(marker in value for marker in MACHINE_PATH_MARKERS):
                errors.append(
                    f"project.commands.{key} contains a machine-local path"
                )

    phases = lifecycle.get("phases")
    if not isinstance(phases, dict):
        errors.append("lifecycle.phases must be an object")
        phases = {}
    for phase in PHASES:
        record = phases.get(phase)
        if not isinstance(record, dict):
            errors.append(f"missing lifecycle phase: {phase}")
            continue
        status = record.get("status")
        if status not in STATUSES:
            errors.append(f"invalid status for {phase}: {status}")
            continue
        evidence = record.get("evidence", [])
        blockers = record.get("blockers", [])
        if not isinstance(evidence, list) or not all(
            isinstance(item, str) for item in evidence
        ):
            errors.append(f"{phase}.evidence must be a string array")
            evidence = []
        if not isinstance(blockers, list) or not all(
            isinstance(item, str) for item in blockers
        ):
            errors.append(f"{phase}.blockers must be a string array")
            blockers = []
        if status in {"ready", "complete"}:
            if not evidence:
                errors.append(f"{phase} is {status} without evidence")
            for dependency in DEPENDENCIES[phase]:
                dependency_status = phases.get(dependency, {}).get("status")
                if dependency_status not in {"ready", "complete"}:
                    errors.append(
                        f"{phase} is {status} before dependency {dependency} is ready"
                    )
            for gate_error in phase_gate_errors(root, phase):
                errors.append(f"{phase} gate: {gate_error}")
        if status == "blocked" and not blockers:
            errors.append(f"{phase} is blocked without a blocker")
        for evidence_text in evidence:
            try:
                evidence_relative = ensure_relative(
                    evidence_text, f"{phase} evidence"
                )
            except LifecycleError as exc:
                errors.append(str(exc))
                continue
            evidence_path = (root / evidence_relative).resolve()
            if not is_within(evidence_path, root):
                errors.append(f"{phase} evidence resolves outside repository: {evidence_text}")
            elif not evidence_path.exists():
                errors.append(f"missing {phase} evidence: {evidence_text}")

    if (root / ".git").exists():
        tracked = run_git(root, "ls-files", "-z")
        if tracked.returncode != 0:
            warnings.append(f"could not inspect tracked files: {tracked.stderr.strip()}")
        else:
            forbidden = sorted(
                path
                for path in tracked.stdout.split("\0")
                if Path(path).suffix.lower() in FORBIDDEN_TRACKED_SUFFIXES
            )
            if forbidden:
                errors.append(
                    "forbidden runtime files are tracked: " + ", ".join(forbidden)
                )
    else:
        warnings.append("repository has no .git directory")

    try:
        claim = active_claim(root)
    except LifecycleError as exc:
        errors.append(str(exc))
    else:
        if claim and claim["expired"]:
            warnings.append(
                f"expired phase claim remains: {claim['phase']} by {claim['owner']}"
            )

    return errors, warnings


def command_check(args: argparse.Namespace) -> int:
    root = Path(args.root).resolve()
    errors, warnings = collect_checks(root)
    for warning in warnings:
        print(f"WARNING: {warning}")
    for error in errors:
        print(f"ERROR: {error}")
    if errors:
        print(f"check failed: {len(errors)} error(s), {len(warnings)} warning(s)")
        return 1
    print(f"check passed: {len(warnings)} warning(s)")
    return 0


def command_claim(args: argparse.Namespace) -> int:
    root = Path(args.root).resolve()
    lifecycle = load_json(root / STATE_FILE)
    if args.minutes < 1 or args.minutes > 1440:
        raise LifecycleError("claim minutes must be between 1 and 1440")
    if "\n" in args.owner or len(args.owner) > 120:
        raise LifecycleError("claim owner must be a single line under 121 characters")
    phases = lifecycle.get("phases", {})
    missing_dependencies = [
        dependency
        for dependency in DEPENDENCIES[args.phase]
        if phases.get(dependency, {}).get("status") not in {"ready", "complete"}
    ]
    if missing_dependencies:
        raise LifecycleError(
            "cannot claim before dependencies are ready: "
            + ", ".join(missing_dependencies)
        )
    existing = active_claim(root)
    if existing and not existing["expired"]:
        if existing["owner"] != args.owner:
            raise LifecycleError(
                f"{existing['phase']} is already claimed by {existing['owner']} "
                f"until {existing['expires_at']}"
            )
        if existing["phase"] != args.phase:
            raise LifecycleError(
                f"{args.owner} must release the {existing['phase']} claim "
                f"before claiming {args.phase}"
            )

    now = datetime.now(timezone.utc).replace(microsecond=0)
    claim = {
        "schema_version": 1,
        "owner": args.owner,
        "phase": args.phase,
        "acquired_at": now.isoformat(),
        "expires_at": (now + timedelta(minutes=args.minutes)).isoformat(),
    }
    atomic_write_json(root / CLAIM_FILE, claim)
    action = "renewed" if existing and existing["owner"] == args.owner else "acquired"
    print(
        f"claim {action}: {args.phase} by {args.owner} "
        f"until {claim['expires_at']}"
    )
    return 0


def command_release_claim(args: argparse.Namespace) -> int:
    root = Path(args.root).resolve()
    path = root / CLAIM_FILE
    claim = active_claim(root)
    if claim is None:
        print("no active claim")
        return 0
    if claim["owner"] != args.owner:
        raise LifecycleError(
            f"claim belongs to {claim['owner']}; {args.owner} cannot release it"
        )
    path.unlink()
    print(f"claim released: {claim['phase']} by {args.owner}")
    return 0


def next_phases(phases: dict[str, Any]) -> list[str]:
    candidates: list[str] = []
    for phase in PHASES:
        status = phases.get(phase, {}).get("status")
        if status in {"ready", "complete"}:
            continue
        if all(
            phases.get(dependency, {}).get("status") in {"ready", "complete"}
            for dependency in DEPENDENCIES[phase]
        ):
            candidates.append(phase)
    return candidates


def command_status(args: argparse.Namespace) -> int:
    root = Path(args.root).resolve()
    project = load_json(root / PROJECT_FILE)
    lifecycle = load_json(root / STATE_FILE)
    phases = lifecycle.get("phases", {})
    claim = active_claim(root)
    recommended = (
        [claim["phase"]]
        if claim and not claim["expired"]
        else next_phases(phases)
    )
    if args.json:
        print(
            json.dumps(
                {
                    "project_name": project.get("project_name"),
                    "phases": phases,
                    "next_phases": recommended,
                    "active_claim": claim,
                },
                ensure_ascii=False,
                indent=2,
            )
        )
        return 0

    print(f"project: {project.get('project_name', '(unnamed)')}")
    if claim:
        claim_state = "expired" if claim["expired"] else "active"
        print(
            f"claim: {claim_state} {claim['phase']} by {claim['owner']} "
            f"until {claim['expires_at']}"
        )
    else:
        print("claim: none")
    for phase in PHASES:
        record = phases.get(phase, {})
        status = record.get("status", "missing")
        evidence_count = len(record.get("evidence", []))
        blocker_count = len(record.get("blockers", []))
        print(
            f"{phase:12} {status:12} "
            f"evidence={evidence_count} blockers={blocker_count}"
        )
    if recommended:
        print("recommended:")
        for phase in recommended:
            print(f"  ${PHASE_SKILLS[phase]} ({phase})")
    else:
        print("recommended: no open phase")
    return 0


def command_checkpoint(args: argparse.Namespace) -> int:
    root = Path(args.root).resolve()
    state_path = root / STATE_FILE
    lifecycle = load_json(state_path)
    phases = lifecycle.get("phases")
    if not isinstance(phases, dict) or args.phase not in phases:
        raise LifecycleError(f"missing lifecycle phase: {args.phase}")
    claim = active_claim(root)
    if claim and not claim["expired"] and claim["phase"] != args.phase:
        raise LifecycleError(
            f"cannot checkpoint {args.phase} while {claim['phase']} is claimed "
            f"by {claim['owner']}"
        )

    record = phases[args.phase]
    if not isinstance(record, dict):
        raise LifecycleError(f"invalid lifecycle record: {args.phase}")

    evidence = list(record.get("evidence", []))
    for item in args.evidence:
        relative = ensure_relative(item, f"{args.phase} evidence")
        evidence_path = (root / relative).resolve()
        if not is_within(evidence_path, root):
            raise LifecycleError(f"evidence resolves outside repository: {item}")
        if not evidence_path.exists():
            raise LifecycleError(f"evidence does not exist: {item}")
        normalized = relative.as_posix()
        if normalized not in evidence:
            evidence.append(normalized)

    blockers = [] if args.clear_blockers else list(record.get("blockers", []))
    for blocker in args.blocker:
        if blocker not in blockers:
            blockers.append(blocker)

    if args.status in {"ready", "complete"}:
        missing_dependencies = [
            dependency
            for dependency in DEPENDENCIES[args.phase]
            if phases.get(dependency, {}).get("status") not in {"ready", "complete"}
        ]
        if missing_dependencies:
            raise LifecycleError(
                "dependencies are not ready: " + ", ".join(missing_dependencies)
            )
        if not evidence:
            raise LifecycleError("ready/complete status requires evidence")
        missing_evidence = []
        for item in evidence:
            relative = ensure_relative(item, "evidence")
            evidence_path = (root / relative).resolve()
            if not is_within(evidence_path, root) or not evidence_path.exists():
                missing_evidence.append(item)
        if missing_evidence:
            raise LifecycleError(
                "evidence does not exist: " + ", ".join(missing_evidence)
            )
        gate_errors = phase_gate_errors(root, args.phase)
        if gate_errors:
            raise LifecycleError(
                f"{args.phase} gate failed: " + "; ".join(gate_errors)
            )
        blockers = []
    elif args.status == "blocked" and not blockers:
        raise LifecycleError("blocked status requires at least one blocker")

    now = utc_now()
    previous_status = record.get("status", "not_started")
    notes = list(record.get("notes", []))
    if args.note:
        notes.append({"at": now, "text": args.note})
    record.update(
        {
            "status": args.status,
            "evidence": evidence,
            "blockers": blockers,
            "notes": notes,
            "updated_at": now,
        }
    )
    lifecycle.setdefault("history", []).append(
        {
            "at": now,
            "phase": args.phase,
            "from": previous_status,
            "to": args.status,
            "note": args.note,
        }
    )
    lifecycle["updated_at"] = now
    atomic_write_json(state_path, lifecycle)
    print(f"{args.phase}: {previous_status} -> {args.status}")
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Manage a repository-local GBA localization lifecycle."
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    init_parser = subparsers.add_parser("init")
    init_parser.add_argument("--root", default=".")
    init_parser.add_argument("--name", required=True)
    init_parser.add_argument("--target-language", default="ko")
    init_parser.add_argument("--source-rom", default="local_roms/source.gba")
    init_parser.set_defaults(handler=command_init)

    check_parser = subparsers.add_parser("check")
    check_parser.add_argument("--root", default=".")
    check_parser.set_defaults(handler=command_check)

    status_parser = subparsers.add_parser("status")
    status_parser.add_argument("--root", default=".")
    status_parser.add_argument("--json", action="store_true")
    status_parser.set_defaults(handler=command_status)

    checkpoint_parser = subparsers.add_parser("checkpoint")
    checkpoint_parser.add_argument("--root", default=".")
    checkpoint_parser.add_argument("--phase", choices=PHASES, required=True)
    checkpoint_parser.add_argument(
        "--status", choices=sorted(STATUSES), required=True
    )
    checkpoint_parser.add_argument("--evidence", action="append", default=[])
    checkpoint_parser.add_argument("--blocker", action="append", default=[])
    checkpoint_parser.add_argument("--clear-blockers", action="store_true")
    checkpoint_parser.add_argument("--note", default="")
    checkpoint_parser.set_defaults(handler=command_checkpoint)

    claim_parser = subparsers.add_parser("claim")
    claim_parser.add_argument("--root", default=".")
    claim_parser.add_argument("--phase", choices=PHASES, required=True)
    claim_parser.add_argument("--owner", required=True)
    claim_parser.add_argument("--minutes", type=int, default=120)
    claim_parser.set_defaults(handler=command_claim)

    release_parser = subparsers.add_parser("release-claim")
    release_parser.add_argument("--root", default=".")
    release_parser.add_argument("--owner", required=True)
    release_parser.set_defaults(handler=command_release_claim)

    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()
    try:
        return args.handler(args)
    except LifecycleError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
