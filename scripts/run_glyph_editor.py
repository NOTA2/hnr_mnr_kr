#!/usr/bin/env python3

from __future__ import annotations

import argparse
import json
import subprocess
import urllib.parse
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[1]
EDITOR_HTML = REPO_ROOT / "tools" / "glyph_editor.html"
ACTIVE_MANIFEST = (REPO_ROOT / "analysis" / "startup_intro_active_workbench" / "prepared_manifest.json").resolve()
ACTIVE_OUTPUT_DIR = (REPO_ROOT / "patched_roms" / "startup_intro_active").resolve()
SOURCE_ROM = (REPO_ROOT / "Hagane no Renkinjutsushi - Meisou no Rondo (Japan).gba").resolve()


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="12x12 PGM glyph editor server")
    parser.add_argument(
        "--manifest",
        default="analysis/startup_intro_active_workbench/prepared_manifest.json",
        help="prepared_manifest.json path",
    )
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=8765)
    return parser.parse_args()


def parse_pgm(path: Path) -> tuple[list[int], int, int]:
    data = path.read_bytes()
    if not data.startswith(b"P5"):
        raise ValueError(f"unsupported pgm format: {path}")

    index = 2

    def next_token() -> bytes:
        nonlocal index
        while index < len(data):
            byte = data[index]
            if byte == 0x23:
                while index < len(data) and data[index] not in (0x0A, 0x0D):
                    index += 1
            elif chr(byte).isspace():
                index += 1
            else:
                break
        start = index
        while index < len(data) and not chr(data[index]).isspace():
            index += 1
        return data[start:index]

    width = int(next_token())
    height = int(next_token())
    max_value = int(next_token())
    while index < len(data) and chr(data[index]).isspace():
        index += 1
    payload = list(data[index:index + width * height])
    if max_value != 255 or len(payload) != width * height:
        raise ValueError(f"unexpected pgm payload: {path}")
    return payload, width, height


def write_pgm(path: Path, pixels: list[int], width: int, height: int) -> None:
    payload = bytes(pixels)
    header = f"P5\n{width} {height}\n255\n".encode("ascii")
    path.write_bytes(header + payload)


class GlyphStore:
    def __init__(self, manifest_path: Path) -> None:
        self.manifest_path = manifest_path.resolve()
        self.can_rebuild_startup_intro = self.manifest_path == ACTIVE_MANIFEST
        payload = json.loads(manifest_path.read_text(encoding="utf-8"))
        if not isinstance(payload, list):
            raise ValueError("manifest must be a JSON array")
        self.entries: list[dict[str, Any]] = []
        for index, item in enumerate(payload):
            if not isinstance(item, dict):
                continue
            pgm_value = item.get("pgm")
            if not isinstance(pgm_value, str):
                continue
            pgm_path = Path(pgm_value)
            if not pgm_path.is_absolute():
                pgm_path = (manifest_path.parent / pgm_path).resolve()
            pixels, width, height = parse_pgm(pgm_path)
            self.entries.append(
                {
                    "index": index,
                    "code": item.get("code"),
                    "char": item.get("char"),
                    "pgm_path": pgm_path,
                    "width": width,
                    "height": height,
                    "pixels": pixels,
                }
            )

    def list_entries(self) -> list[dict[str, Any]]:
        result = []
        for entry in self.entries:
            result.append(
                {
                    "index": entry["index"],
                    "code": entry["code"],
                    "char": entry["char"],
                    "width": entry["width"],
                    "height": entry["height"],
                    "pgm_path": str(entry["pgm_path"]),
                }
            )
        return result

    def rebuild_startup_intro(self) -> dict[str, Any]:
        if not self.can_rebuild_startup_intro:
            raise ValueError("rebuild is only enabled for the active startup intro workbench")
        command = [
            "zsh",
            "scripts/build_startup_intro_test.sh",
            str(SOURCE_ROM),
            str(ACTIVE_OUTPUT_DIR),
        ]
        completed = subprocess.run(
            command,
            cwd=REPO_ROOT,
            text=True,
            capture_output=True,
            check=True,
        )
        return {
            "ok": True,
            "rom_path": str(ACTIVE_OUTPUT_DIR / "hnr_startup_intro_test.gba"),
            "stdout": completed.stdout,
        }

    def get_entry(self, index: int) -> dict[str, Any]:
        return self.entries[index]

    def update_entry(self, index: int, pixels: list[int]) -> dict[str, Any]:
        entry = self.entries[index]
        width = int(entry["width"])
        height = int(entry["height"])
        if len(pixels) != width * height:
            raise ValueError("pixel count mismatch")
        normalized = [34 if int(value) else 0 for value in pixels]
        write_pgm(Path(entry["pgm_path"]), normalized, width, height)
        entry["pixels"] = normalized
        return {
            "index": entry["index"],
            "code": entry["code"],
            "char": entry["char"],
            "width": width,
            "height": height,
            "pixels": normalized,
            "pgm_path": str(entry["pgm_path"]),
        }


def make_handler(store: GlyphStore):
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
                body = EDITOR_HTML.read_bytes()
                self.send_response(HTTPStatus.OK)
                self.send_header("Content-Type", "text/html; charset=utf-8")
                self.send_header("Content-Length", str(len(body)))
                self.end_headers()
                self.wfile.write(body)
                return
            if parsed.path == "/manifest":
                self._json(
                    {
                        "entries": store.list_entries(),
                        "manifest": str(store.manifest_path),
                        "can_rebuild_startup_intro": store.can_rebuild_startup_intro,
                        "active_output_dir": str(ACTIVE_OUTPUT_DIR),
                    }
                )
                return
            if parsed.path == "/glyph":
                query = urllib.parse.parse_qs(parsed.query)
                index = int(query.get("index", ["0"])[0])
                entry = store.get_entry(index)
                self._json(
                    {
                        "index": entry["index"],
                        "code": entry["code"],
                        "char": entry["char"],
                        "width": entry["width"],
                        "height": entry["height"],
                        "pixels": entry["pixels"],
                        "pgm_path": str(entry["pgm_path"]),
                    }
                )
                return
            self.send_error(HTTPStatus.NOT_FOUND, "not found")

        def do_POST(self) -> None:
            parsed = urllib.parse.urlparse(self.path)
            if parsed.path != "/glyph":
                if parsed.path == "/rebuild":
                    try:
                        result = store.rebuild_startup_intro()
                    except subprocess.CalledProcessError as exc:
                        self.send_error(HTTPStatus.INTERNAL_SERVER_ERROR, exc.stderr or str(exc))
                        return
                    except Exception as exc:
                        self.send_error(HTTPStatus.BAD_REQUEST, str(exc))
                        return
                    self._json(result)
                    return
                self.send_error(HTTPStatus.NOT_FOUND, "not found")
                return
            query = urllib.parse.parse_qs(parsed.query)
            index = int(query.get("index", ["0"])[0])
            length = int(self.headers.get("Content-Length", "0"))
            payload = json.loads(self.rfile.read(length).decode("utf-8"))
            pixels = payload.get("pixels")
            if not isinstance(pixels, list):
                self.send_error(HTTPStatus.BAD_REQUEST, "pixels must be a list")
                return
            try:
                result = store.update_entry(index, pixels)
            except Exception as exc:
                self.send_error(HTTPStatus.BAD_REQUEST, str(exc))
                return
            self._json(result)

        def log_message(self, format: str, *args: Any) -> None:
            return

    return Handler


def main() -> int:
    args = parse_args()
    manifest_path = Path(args.manifest)
    if not manifest_path.is_absolute():
        manifest_path = (REPO_ROOT / manifest_path).resolve()
    store = GlyphStore(manifest_path)
    server = ThreadingHTTPServer((args.host, args.port), make_handler(store))
    print(f"glyph editor: http://{args.host}:{args.port}")
    print(f"manifest    : {manifest_path}")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
