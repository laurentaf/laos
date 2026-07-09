"""Start FastAPI server and test health endpoint."""
import subprocess
import sys
import time
import urllib.request
import os
import signal

server_dir = os.path.join(os.path.dirname(__file__), "..", "..", "..", "server")
os.chdir(server_dir)

# Start server as subprocess
proc = subprocess.Popen(
    [sys.executable, "-m", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"],
    stdout=subprocess.PIPE,
    stderr=subprocess.PIPE,
)

# Wait for server to start
for i in range(10):
    try:
        resp = urllib.request.urlopen("http://localhost:8000/api/v1/health", timeout=2)
        print(f"SERVER RUNNING on port 8000")
        print(f"Health response: {resp.read().decode()}")
        break
    except Exception:
        time.sleep(1)
else:
    print("Server failed to start")
    proc.terminate()
    out, err = proc.communicate()
    print("STDOUT:", out.decode()[:500])
    print("STDERR:", err.decode()[:500])
    sys.exit(1)

print(f"\nServer PID: {proc.pid}")
print("Test login:")
try:
    import json
    req = urllib.request.Request(
        "http://localhost:8000/api/v1/auth/login",
        data=json.dumps({"username": "admin", "password": "admin"}).encode(),
        headers={"Content-Type": "application/json"},
    )
    resp = urllib.request.urlopen(req)
    print(f"  Login response: {resp.read().decode()[:200]}")
except Exception as e:
    print(f"  Login error: {e}")
