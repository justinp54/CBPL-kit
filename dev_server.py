"""Local development server — serves public/ on localhost:8080."""
import sys
from http.server import HTTPServer, SimpleHTTPRequestHandler
from pathlib import Path

ROOT = Path(__file__).parent


class DevHandler(SimpleHTTPRequestHandler):
    def __init__(self, *a, **kw):
        super().__init__(*a, directory=str(ROOT / "public"), **kw)

    def log_message(self, fmt, *args):
        print(f"  {args[0]}  {args[1]}", flush=True)


if __name__ == "__main__":
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 8080
    print(f"Dev server → http://localhost:{port}")
    HTTPServer(("", port), DevHandler).serve_forever()
