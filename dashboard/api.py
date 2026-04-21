#!/usr/bin/env python3
"""GridLib API — download manager. Runs on localhost:9081, nginx proxies /api/ here."""

import json
import os
import queue
import subprocess
import threading
import time
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path
from urllib.parse import urlparse

COLLECTIONS_DIR = Path(
    os.environ.get("GRIDLIB_COLLECTIONS_DIR", "/opt/gridlib/collections")
)
PORT = int(os.environ.get("GRIDLIB_API_PORT", 9081))

DEST_DIRS = {
    "kiwix": Path(os.environ.get("ZIM_DIR", "/srv/kiwix/content")),
    "maps": Path(os.environ.get("MAPS_DIR", "/srv/gridlib/maps")),
}

# In-memory download state  { filename: { status, percent, size_mb, downloaded_mb, error? } }
_downloads: dict = {}
_lock = threading.Lock()
_procs: dict = {}  # filename → subprocess.Popen
_queue: queue.Queue = queue.Queue()  # queued download jobs


# ── Collections ───────────────────────────────────────────────────────────────


def load_collections() -> list[dict]:
    result = []
    for path in sorted(COLLECTIONS_DIR.glob("*.json")):
        try:
            result.append(json.loads(path.read_text()))
        except Exception:
            pass
    return result


def installed_files() -> dict[str, list[str]]:
    found: dict[str, list[str]] = {}
    for kind, dest in DEST_DIRS.items():
        try:
            found[kind] = [f.name for f in dest.iterdir() if f.is_file()]
        except Exception:
            found[kind] = []
    return found


# ── Downloads ─────────────────────────────────────────────────────────────────


def _track_progress(filename: str, total_mb: float, dest: Path) -> None:
    total_bytes = total_mb * 1_000_000
    while True:
        with _lock:
            state = _downloads.get(filename)
        if not state or state["status"] not in ("downloading", "pending"):
            break
        try:
            current = dest.stat().st_size if dest.exists() else 0
            pct = (
                min(round(current / total_bytes * 100, 1), 99) if total_bytes > 0 else 0
            )
            with _lock:
                _downloads[filename]["percent"] = pct
                _downloads[filename]["downloaded_mb"] = round(current / 1_000_000, 1)
        except Exception:
            pass
        time.sleep(1)


def _restart_kiwix() -> None:
    try:
        subprocess.run(["systemctl", "restart", "kiwix-serve.service"], timeout=10)
    except Exception:
        pass


def _run_job(url: str | None, filename: str, kind: str, size_mb: float, extract: dict | None) -> None:
    dest_dir = DEST_DIRS.get(kind, DEST_DIRS["kiwix"])
    dest_dir.mkdir(parents=True, exist_ok=True)
    dest = dest_dir / filename

    with _lock:
        state = _downloads.get(filename)
        if not state or state["status"] == "cancelled":
            return
        state["status"] = "downloading"

    try:
        if extract:
            cmd = ["pmtiles", "extract", extract["source"], str(dest), f"--bbox={extract['bbox']}"]
        else:
            cmd = ["curl", "-L", "--continue-at", "-", "-o", str(dest), url]

        proc = subprocess.Popen(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        with _lock:
            _procs[filename] = proc

        tracker = threading.Thread(
            target=_track_progress, args=(filename, size_mb, dest), daemon=True
        )
        tracker.start()
        proc.wait()

        with _lock:
            _procs.pop(filename, None)
            state = _downloads.get(filename)
            if state and state["status"] not in ("cancelled",):
                if proc.returncode == 0:
                    state["status"] = "complete"
                    state["percent"] = 100
                else:
                    state["status"] = "error"
                    state["error"] = f"{'pmtiles' if extract else 'curl'} exited with code {proc.returncode}"

        if proc.returncode == 0 and kind == "kiwix":
            _restart_kiwix()

    except Exception as e:
        with _lock:
            if filename in _downloads:
                _downloads[filename]["status"] = "error"
                _downloads[filename]["error"] = str(e)


def _queue_worker() -> None:
    while True:
        job = _queue.get()
        try:
            _run_job(**job)
        finally:
            _queue.task_done()


def start_download(url: str | None, filename: str, kind: str, size_mb: float, extract: dict | None = None) -> None:
    with _lock:
        existing = _downloads.get(filename, {}).get("status")
        if existing in ("downloading", "queued"):
            return
        _downloads[filename] = {
            "status": "queued",
            "percent": 0,
            "size_mb": size_mb,
            "downloaded_mb": 0,
            "kind": kind,
        }
    _queue.put({"url": url, "filename": filename, "kind": kind, "size_mb": size_mb, "extract": extract})


def cancel_download(filename: str) -> bool:
    with _lock:
        proc = _procs.get(filename)
        state = _downloads.get(filename)
        if not state:
            return False
        kind = state.get("kind", "kiwix")
        if proc:
            proc.terminate()
        state["status"] = "cancelled"
    # Remove partial file after process is killed
    dest = DEST_DIRS.get(kind, DEST_DIRS["kiwix"]) / filename
    try:
        dest.unlink(missing_ok=True)
    except Exception:
        pass
    return True


def uninstall_file(filename: str, kind: str) -> bool:
    dest = DEST_DIRS.get(kind, DEST_DIRS["kiwix"]) / filename
    try:
        dest.unlink()
    except FileNotFoundError:
        return False
    with _lock:
        _downloads.pop(filename, None)
    if kind == "kiwix":
        _restart_kiwix()
    return True


# ── HTTP handler ──────────────────────────────────────────────────────────────

CORS = {
    "Access-Control-Allow-Origin": "*",
    "Access-Control-Allow-Methods": "GET, POST, DELETE, OPTIONS",
    "Access-Control-Allow-Headers": "Content-Type",
}


class Handler(BaseHTTPRequestHandler):
    def log_message(self, fmt, *args):
        pass

    def _send(self, data: dict | list, status: int = 200) -> None:
        body = json.dumps(data).encode()
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        for k, v in CORS.items():
            self.send_header(k, v)
        self.end_headers()
        self.wfile.write(body)

    def _body(self) -> dict:
        length = int(self.headers.get("Content-Length", 0))
        return json.loads(self.rfile.read(length)) if length else {}

    def do_OPTIONS(self) -> None:
        self.send_response(204)
        for k, v in CORS.items():
            self.send_header(k, v)
        self.end_headers()

    def do_GET(self) -> None:
        path = urlparse(self.path).path.rstrip("/")

        if path == "/collections":
            cols = load_collections()
            installed = installed_files()
            self._send({"collections": cols, "installed": installed})

        elif path == "/downloads":
            with _lock:
                self._send(dict(_downloads))

        else:
            self._send({"error": "not found"}, 404)

    def do_POST(self) -> None:
        path = urlparse(self.path).path.rstrip("/")

        if path == "/download":
            body = self._body()
            url = body.get("url") or None
            filename = body.get("filename", "")
            kind = body.get("kind", "kiwix")
            size_mb = float(body.get("size_mb", 0))
            extract = body.get("extract") or None

            if not filename or (not url and not extract):
                self._send({"error": "filename and either url or extract are required"}, 400)
                return

            start_download(url, filename, kind, size_mb, extract)
            self._send({"status": "started", "filename": filename})

        else:
            self._send({"error": "not found"}, 404)

    def do_DELETE(self) -> None:
        path = urlparse(self.path).path.rstrip("/")
        body = self._body()

        if path == "/download":
            filename = body.get("filename", "")
            if cancel_download(filename):
                self._send({"status": "cancelled", "filename": filename})
            else:
                self._send({"error": "download not found"}, 404)

        elif path == "/file":
            filename = body.get("filename", "")
            kind = body.get("kind", "kiwix")
            if not filename:
                self._send({"error": "filename is required"}, 400)
                return
            if uninstall_file(filename, kind):
                self._send({"status": "uninstalled", "filename": filename})
            else:
                self._send({"error": "file not found"}, 404)

        else:
            self._send({"error": "not found"}, 404)


if __name__ == "__main__":
    for dest in DEST_DIRS.values():
        dest.mkdir(parents=True, exist_ok=True)

    threading.Thread(target=_queue_worker, daemon=True).start()

    server = HTTPServer(("127.0.0.1", PORT), Handler)
    print(f"GridLib API → http://127.0.0.1:{PORT}")
    server.serve_forever()
