#!/usr/bin/env python3

from __future__ import annotations

import argparse
import base64
import json
import mimetypes
import shutil
import subprocess
import sys
import urllib.parse
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
HTML = ROOT / "tools" / "localization_workbench.html"
WORKBENCH_DIR = ROOT / "confirmed_data" / "localization_workbench"
DATASET_PATH = WORKBENCH_DIR / "workbench_dataset.json"
SPEAKERS_PATH = WORKBENCH_DIR / "speaker_aliases.json"
SPEAKER_REGISTRY_PATH = WORKBENCH_DIR / "speaker_registry.json"
PROGRESS_PATH = WORKBENCH_DIR / "progress_state.json"
IMAGE_REPLACEMENTS_PATH = WORKBENCH_DIR / "image_replacements.json"
UPLOADS_ROOT = WORKBENCH_DIR / "uploaded_image_replacements"
IMPORT_REPORT_DIR = WORKBENCH_DIR / "import_reports"
AGENT_INBOX_DIR = WORKBENCH_DIR / "agent_inbox"
IMPORTED_AGENT_RESULTS_DIR = WORKBENCH_DIR / "imported_agent_results"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="로컬라이제이션 workbench 서버")
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=8766)
    return parser.parse_args()


def load_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, payload: Any) -> None:
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


class WorkbenchStore:
    def __init__(self) -> None:
        self.last_auto_import_summary = {
            "imported_count": 0,
            "imported_files": [],
            "report_paths": [],
        }
        self.reload()
        self.auto_import_agent_results()

    def reload(self) -> None:
        self.dataset = load_json(DATASET_PATH)
        self.speakers = load_json(SPEAKERS_PATH)
        self.speaker_registry = load_json(SPEAKER_REGISTRY_PATH)
        self.progress = load_json(PROGRESS_PATH)
        self.image_replacements = load_json(IMAGE_REPLACEMENTS_PATH)

    def bundle(self) -> dict[str, Any]:
        dataset = json.loads(json.dumps(self.dataset, ensure_ascii=False))
        image_map = {item["item_id"]: item for item in self.image_replacements}
        for item in dataset["items"]:
            if item["category_id"] == "image_review_units":
                sidecar = image_map.get(item["item_id"])
                if sidecar:
                    for field in ("source_preview_path", "source_download_path", "replacement_path", "comparison_notes", "notes", "progress_status", "status"):
                        if field in sidecar:
                            item[field] = sidecar[field]
        return {
            "dataset": dataset,
            "speakers": self.speakers,
            "speaker_registry": self.speaker_registry,
            "progress": self.progress,
            "image_replacements": self.image_replacements,
            "auto_import_summary": self.last_auto_import_summary,
        }

    def save_item(self, item_id: str, updates: dict[str, Any]) -> dict[str, Any]:
        items = self.dataset["items"]
        for item in items:
            if item["item_id"] == item_id:
                previous_translation = item.get("translation", "")
                current_agent_draft = updates.get("agent_draft", item.get("agent_draft", ""))
                for field in (
                    "translation",
                    "agent_draft",
                    "agent_comment",
                    "manual_locked",
                    "notes",
                    "progress_status",
                    "review_status",
                ):
                    if field in updates:
                        item[field] = updates[field]
                new_translation = item.get("translation", "")
                if (
                    "translation" in updates
                    and new_translation
                    and new_translation != previous_translation
                    and new_translation != current_agent_draft
                    and not updates.get("manual_locked", False)
                ):
                    item["manual_locked"] = True
                write_json(DATASET_PATH, self.dataset)
                self.sync_sources()
                return item
        raise KeyError(item_id)

    def save_speaker(self, token: str, updates: dict[str, Any]) -> dict[str, Any]:
        for item in self.speakers:
            if item["dialogue_state_token"] == token:
                for field in ("speaker_id", "notes", "confirmed", "speaker_name", "speaker_role"):
                    if field in updates:
                        item[field] = updates[field]
                write_json(SPEAKERS_PATH, self.speakers)
                return item
        raise KeyError(token)

    def save_speaker_registry(self, payload: dict[str, Any]) -> dict[str, Any]:
        speaker_id = payload.get("speaker_id", "").strip()
        speaker_name = payload.get("speaker_name", "").strip()
        if not speaker_name:
            raise ValueError("speaker_name is required")
        if not speaker_id:
            speaker_id = f"speaker_{len(self.speaker_registry) + 1:03d}"

        for item in self.speaker_registry:
            if item["speaker_id"] == speaker_id:
                item["speaker_name"] = speaker_name
                item["speaker_role"] = payload.get("speaker_role", "")
                item["notes"] = payload.get("notes", "")
                write_json(SPEAKER_REGISTRY_PATH, self.speaker_registry)
                return item

        new_item = {
            "speaker_id": speaker_id,
            "speaker_name": speaker_name,
            "speaker_role": payload.get("speaker_role", ""),
            "notes": payload.get("notes", ""),
        }
        self.speaker_registry.append(new_item)
        write_json(SPEAKER_REGISTRY_PATH, self.speaker_registry)
        return new_item

    def save_progress(self, updates: dict[str, Any]) -> dict[str, Any]:
        for field in ("current_category_id", "current_item_id", "last_built_rom"):
            if field in updates:
                self.progress[field] = updates[field]
        write_json(PROGRESS_PATH, self.progress)
        return self.progress

    def save_image_item(self, item_id: str, updates: dict[str, Any]) -> dict[str, Any]:
        for item in self.image_replacements:
            if item["item_id"] == item_id:
                for field in ("source_preview_path", "source_download_path", "replacement_path", "comparison_notes", "notes", "progress_status", "status"):
                    if field in updates:
                        item[field] = updates[field]
                write_json(IMAGE_REPLACEMENTS_PATH, self.image_replacements)
                for dataset_item in self.dataset["items"]:
                    if dataset_item["item_id"] == item_id:
                        dataset_item.update(item)
                        break
                write_json(DATASET_PATH, self.dataset)
                return item
        raise KeyError(item_id)

    def upload_image_item(self, item_id: str, filename: str, content_base64: str) -> dict[str, Any]:
        data = base64.b64decode(content_base64)
        item = next((entry for entry in self.image_replacements if entry["item_id"] == item_id), None)
        if not item:
            raise KeyError(item_id)

        dataset_item = next(
            (entry for entry in self.dataset["items"] if entry["item_id"] == item_id),
            None,
        )
        if not dataset_item:
            raise KeyError(item_id)

        safe_dir = UPLOADS_ROOT / item_id.replace(":", "_")
        safe_dir.mkdir(parents=True, exist_ok=True)
        output_path = safe_dir / Path(filename).name
        output_path.write_bytes(data)
        relative = str(output_path.relative_to(ROOT))
        item["replacement_path"] = relative
        item["progress_status"] = "edited"
        write_json(IMAGE_REPLACEMENTS_PATH, self.image_replacements)
        for dataset_item in self.dataset["items"]:
            if dataset_item["item_id"] == item_id:
                dataset_item["replacement_path"] = relative
                dataset_item["progress_status"] = "edited"
                break
        write_json(DATASET_PATH, self.dataset)
        return item

    def sync_sources(self) -> None:
        subprocess.run(
            [sys.executable, "scripts/sync_workbench_to_sources.py"],
            cwd=ROOT,
            text=True,
            capture_output=True,
            check=True,
        )

    def rebuild(self, category_id: str | None) -> dict[str, Any]:
        command = [sys.executable, "scripts/build_localization_review_rom.py"]
        if category_id:
            command.extend(["--category-id", category_id])
        completed = subprocess.run(
            command,
            cwd=ROOT,
            text=True,
            capture_output=True,
            check=True,
        )
        self.progress["last_built_rom"] = "patched_roms/current_review/hnr_localization_review.gba"
        write_json(PROGRESS_PATH, self.progress)
        return {
            "ok": True,
            "rom_path": self.progress["last_built_rom"],
            "stdout": completed.stdout,
        }

    def import_translation_results(self, filename: str, content_base64: str) -> dict[str, Any]:
        data = base64.b64decode(content_base64)
        IMPORT_REPORT_DIR.mkdir(parents=True, exist_ok=True)
        import_path = IMPORT_REPORT_DIR / Path(filename).name
        import_path.write_bytes(data)
        report_path = IMPORT_REPORT_DIR / f"{import_path.stem}_import_report.json"
        command = [
            sys.executable,
            "scripts/import_translation_agent_results.py",
            str(import_path),
            "--report",
            str(report_path),
        ]
        completed = subprocess.run(
            command,
            cwd=ROOT,
            text=True,
            capture_output=True,
            check=True,
        )
        self.reload()
        report = load_json(report_path)
        return {
            "ok": True,
            "import_path": str(import_path.relative_to(ROOT)),
            "report_path": str(report_path.relative_to(ROOT)),
            "summary": report,
            "stdout": completed.stdout,
        }

    def auto_import_agent_results(self) -> dict[str, Any]:
        AGENT_INBOX_DIR.mkdir(parents=True, exist_ok=True)
        IMPORTED_AGENT_RESULTS_DIR.mkdir(parents=True, exist_ok=True)
        IMPORT_REPORT_DIR.mkdir(parents=True, exist_ok=True)

        imported_files: list[str] = []
        report_paths: list[str] = []

        for import_path in sorted(AGENT_INBOX_DIR.glob("*.json")):
            report_path = IMPORT_REPORT_DIR / f"{import_path.stem}_import_report.json"
            command = [
                sys.executable,
                "scripts/import_translation_agent_results.py",
                str(import_path),
                "--report",
                str(report_path),
            ]
            subprocess.run(
                command,
                cwd=ROOT,
                text=True,
                capture_output=True,
                check=True,
            )
            destination = IMPORTED_AGENT_RESULTS_DIR / import_path.name
            if destination.exists():
                destination.unlink()
            shutil.move(str(import_path), str(destination))
            imported_files.append(str(destination.relative_to(ROOT)))
            report_paths.append(str(report_path.relative_to(ROOT)))

        if imported_files:
            self.reload()

        self.last_auto_import_summary = {
            "imported_count": len(imported_files),
            "imported_files": imported_files,
            "report_paths": report_paths,
        }
        return self.last_auto_import_summary


def make_handler(store: WorkbenchStore):
    class Handler(BaseHTTPRequestHandler):
        def _json(self, payload: Any, status: int = 200) -> None:
            body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
            self.send_response(status)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)

        def do_GET(self) -> None:
            parsed = urllib.parse.urlparse(self.path)
            if parsed.path in ("/", "/index.html"):
                body = HTML.read_bytes()
                self.send_response(HTTPStatus.OK)
                self.send_header("Content-Type", "text/html; charset=utf-8")
                self.send_header("Content-Length", str(len(body)))
                self.end_headers()
                self.wfile.write(body)
                return
            if parsed.path == "/bundle":
                store.reload()
                self._json(store.bundle())
                return
            if parsed.path == "/workspace-file":
                params = urllib.parse.parse_qs(parsed.query)
                raw_path = params.get("path", [""])[0]
                if not raw_path:
                    self.send_error(HTTPStatus.BAD_REQUEST, "missing path")
                    return
                file_path = (ROOT / raw_path).resolve()
                if not file_path.is_file() or ROOT not in file_path.parents:
                    self.send_error(HTTPStatus.NOT_FOUND, "file not found")
                    return
                body = file_path.read_bytes()
                content_type, _ = mimetypes.guess_type(file_path.name)
                self.send_response(HTTPStatus.OK)
                self.send_header("Content-Type", content_type or "application/octet-stream")
                self.send_header("Content-Length", str(len(body)))
                self.end_headers()
                self.wfile.write(body)
                return
            self.send_error(HTTPStatus.NOT_FOUND, "not found")

        def do_POST(self) -> None:
            parsed = urllib.parse.urlparse(self.path)
            length = int(self.headers.get("Content-Length", "0"))
            payload = json.loads(self.rfile.read(length).decode("utf-8")) if length else {}
            try:
                if parsed.path == "/item":
                    result = store.save_item(payload["item_id"], payload)
                    self._json(result)
                    return
                if parsed.path == "/speaker":
                    result = store.save_speaker(payload["dialogue_state_token"], payload)
                    self._json(result)
                    return
                if parsed.path == "/speaker-registry":
                    result = store.save_speaker_registry(payload)
                    self._json(result)
                    return
                if parsed.path == "/progress":
                    result = store.save_progress(payload)
                    self._json(result)
                    return
                if parsed.path == "/image-item":
                    result = store.save_image_item(payload["item_id"], payload)
                    self._json(result)
                    return
                if parsed.path == "/image-upload":
                    result = store.upload_image_item(
                        payload["item_id"],
                        payload["filename"],
                        payload["content_base64"],
                    )
                    self._json(result)
                    return
                if parsed.path == "/rebuild":
                    result = store.rebuild(payload.get("category_id"))
                    self._json(result)
                    return
                if parsed.path == "/import-translation-results":
                    result = store.import_translation_results(
                        payload["filename"],
                        payload["content_base64"],
                    )
                    self._json(result)
                    return
            except subprocess.CalledProcessError as exc:
                self.send_error(HTTPStatus.INTERNAL_SERVER_ERROR, exc.stderr or str(exc))
                return
            except Exception as exc:
                self.send_error(HTTPStatus.BAD_REQUEST, str(exc))
                return

            self.send_error(HTTPStatus.NOT_FOUND, "not found")

        def log_message(self, format: str, *args: Any) -> None:
            return

    return Handler


def main() -> int:
    args = parse_args()
    store = WorkbenchStore()
    server = ThreadingHTTPServer((args.host, args.port), make_handler(store))
    print(f"localization workbench: http://{args.host}:{args.port}")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
