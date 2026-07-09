"""Build frontend and start serving it."""
import subprocess
import sys
import os
import time
import threading
from pathlib import Path

web_dir = Path(r"F:\projects\eixo_do_mal\web")
os.chdir(str(web_dir))

# 1. Install dependencies
print("=== Installing npm dependencies ===")
result = subprocess.run(["npm", "install"], capture_output=True, text=True, timeout=120)
if result.returncode != 0:
    print(f"npm install FAILED:\n{result.stdout[-500:]}\n{result.stderr[-500:]}")
    sys.exit(1)
print("npm install OK")

# 2. Update vite proxy to point to port 8080
vite_config = web_dir / "vite.config.ts"
config_text = vite_config.read_text(encoding="utf-8")
if "8000" in config_text and "8080" not in config_text:
    config_text = config_text.replace("'http://localhost:8000'", "'http://localhost:8080'")
    config_text = config_text.replace("'ws://localhost:8000'", "'ws://localhost:8080'")
    vite_config.write_text(config_text, encoding="utf-8")
    print("Vite config updated: proxy → port 8080")

# 3. Build frontend
print("=== Building frontend ===")
result = subprocess.run(["npx.cmd", "vite", "build"], capture_output=True, text=True, timeout=120)
if result.returncode != 0:
    print(f"vite build FAILED:\n{result.stdout[-500:]}\n{result.stderr[-500:]}")
    # Continue with partial build
    print("Continuing with whatever was built...")
else:
    print("vite build OK")

# 4. Start HTTP server for the built files
print("=== Starting static file server on port 5173 ===")
import http.server
import socketserver

class Handler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(web_dir / "dist"), **kwargs)
    def log_message(self, format, *args):
        print(f"[frontend] {args[0]} {args[1]} {args[2]}")

def serve():
    with socketserver.TCPServer(("0.0.0.0", 5173), Handler) as httpd:
        print(f"Frontend serving at http://0.0.0.0:5173")
        httpd.serve_forever()

t = threading.Thread(target=serve, daemon=True)
t.start()

# 5. Test
time.sleep(1)
try:
    import urllib.request
    resp = urllib.request.urlopen("http://localhost:5173", timeout=3)
    print(f"\n=== Frontend OK: {resp.status} ({len(resp.read())} bytes) ===")
except Exception as e:
    print(f"\n=== Frontend check: {e} ===")

print("\n=== READY ===")
print("Backend:  http://localhost:8080")
print("Frontend: http://localhost:5173")
print("Login: admin / admin")
print("(Ctrl+C twice to stop)")

# Keep alive
while True:
    time.sleep(60)
