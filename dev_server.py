"""Local development server — serves public/ and /api/compute."""
import json, sys, os
from http.server import HTTPServer, SimpleHTTPRequestHandler
from pathlib import Path

ROOT = Path(__file__).parent
sys.path.insert(0, str(ROOT))

from api.compute import _validate, _compute


class DevHandler(SimpleHTTPRequestHandler):
    def __init__(self, *a, **kw):
        super().__init__(*a, directory=str(ROOT / "public"), **kw)

    def do_GET(self):
        # /exp06/*.py → public/exp06/ (already in public/, handled by super)
        # /experiments/*.py → legacy local dev support
        if self.path.startswith("/experiments/"):
            file_path = ROOT / self.path.lstrip("/")
            if file_path.exists():
                content = file_path.read_bytes()
                self.send_response(200)
                self.send_header("Content-Type", "text/plain; charset=utf-8")
                self.send_header("Content-Length", str(len(content)))
                self.end_headers()
                self.wfile.write(content)
                return
        super().do_GET()

    def do_POST(self):
        if self.path == "/api/compute":
            length = int(self.headers.get("Content-Length", 0))
            body   = json.loads(self.rfile.read(length)) if length else {}
            try:
                result = _compute(_validate(body))
            except Exception as e:
                result = {"success": False, "error": str(e)}
            payload = json.dumps(result).encode()
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(payload)))
            self.send_header("Access-Control-Allow-Origin", "*")
            self.end_headers()
            self.wfile.write(payload)
        else:
            self.send_response(404)
            self.end_headers()

    def do_OPTIONS(self):
        self.send_response(204)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()

    def log_message(self, fmt, *args):
        print(f"  {args[0]}  {args[1]}", flush=True)


if __name__ == "__main__":
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 8080
    print(f"Dev server → http://localhost:{port}")
    HTTPServer(("", port), DevHandler).serve_forever()
