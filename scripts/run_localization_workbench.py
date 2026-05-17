#!/usr/bin/env python3

from __future__ import annotations

import argparse
import base64
import json
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
PROGRESS_PATH = WORKBENCH_DIR / "progress_state.json"
IMAGE_REPLACEMENTS_PATH = WORKBENCH_DIR / "image_replacements.json"
UPLOADS_ROOT = WORKBENCH_DIR / "uploaded_image_replacements"


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
        self.reload()

    def reload(self) -> None:
        self.dataset = load_json(DATASET_PATH)
        self.speakers = load_json(SPEAKERS_PATH)
        self.progress = load_json(PROGRESS_PATH)
        self.image_replacements = load_json(IMAGE_REPLACEMENTS_PATH)

    def bundle(self) -> dict[str, Any]:
        dataset = json.loads(json.dumps(self.dataset, ensure_ascii=False))
        image_map = {item["item_id"]: item for item in self.image_replacements}
        for item in dataset["items"]:
            if item["category_id"] == "image_review_units":
                sidecar = image_map.get(item["item_id"])
                if sidecar:
                    for field in ("replacement_path", "notes", "progress_status", "status"):
                        if field in sidecar:
                            item[field] = sidecar[field]
        return {
            "dataset": dataset,
            "speakers": self.speakers,
            "progress": self.progress,
            "image_replacements": self.image_replacements,
        }

    def save_item(self, item_id: str, updates: dict[str, Any]) -> dict[str, Any]:
        items = self.dataset["items"]
        for item in items:
            if item["item_id"] == item_id:
                for field in (
                    "translation",
                    "agent_draft",
                    "agent_comment",
                    "manual_locked",
                    "notes",
                    "progress_status",
                    "review_status",
                    "speaker_alias",
                    "speaker_confirmed",
                ):
                    if field in updates:
                        item[field] = updates[field]
                write_json(DATASET_PATH, self.dataset)
                return item
        raise KeyError(item_id)

    def save_speaker(self, token: str, updates: dict[str, Any]) -> dict[str, Any]:
        for item in self.speakers:
            if item["dialogue_state_token"] == token:
                for field in ("speaker_name", "speaker_role", "notes", "confirmed"):
                    if field in updates:
                        item[field] = updates[field]
                write_json(SPEAKERS_PATH, self.speakers)
                return item
        raise KeyError(token)

    def save_progress(self, updates: dict[str, Any]) -> dict[str, Any]:
        for field in ("current_category_id", "current_item_id", "current_review_scope", "last_built_rom"):
            if field in updates:
                self.progress[field] = updates[field]
        write_json(PROGRESS_PATH, self.progress)
        return self.progress

    def save_image_item(self, item_id: str, updates: dict[str, Any]) -> dict[str, Any]:
        for item in self.image_replacements:
            if item["item_id"] == item_id:
                for field in ("replacement_path", "notes", "progress_status", "status"):
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
        if category_id:
            self.progress["current_review_scope"] = category_id
        write_json(PROGRESS_PATH, self.progress)
        return {
            "ok": True,
            "rom_path": self.progress["last_built_rom"],
            "stdout": completed.stdout,
        }


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
