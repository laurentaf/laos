#!/usr/bin/env python3
"""Try to read GitHub token from various Windows locations."""
import os
import subprocess
import json

# Check Windows Credential Manager via cmdkey
try:
    result = subprocess.run(['cmdkey', '/list'], capture_output=True, text=True, timeout=5)
    for line in result.stdout.split('\n'):
        if 'github' in line.lower():
            print(f"Found GitHub credential target: {line.strip()}")
except Exception as e:
    print(f"cmdkey error: {e}")

# Check if git has stored credentials
try:
    result = subprocess.run(['git', 'credential', 'fill'], 
                          input='protocol=https\nhost=github.com\n\n', 
                          capture_output=True, text=True, timeout=5)
    print(f"Git credential:\n{result.stdout}")
except Exception as e:
    print(f"git credential error: {e}")

# Check common env vars
for var in ['GITHUB_TOKEN', 'GH_TOKEN', 'GIT_TOKEN', 'GIT_CREDENTIALS']:
    val = os.environ.get(var)
    if val:
        masked = val[:10] + '...' if len(val) > 10 else '(short)'
        print(f"{var}={masked}")
    else:
        print(f"{var}=[not set]")

# Check Windows credential manager for git
import ctypes
# GitHub uses git-credential-manager on Windows
print("\nChecking for git-credential-manager...")
for path in [
    r"C:\Program Files\Git\mingw64\bin\git-credential-manager.exe",
    r"C:\Program Files\Git\cmd\git-credential-manager.exe",
]:
    if os.path.exists(path):
        print(f"Found GCM at: {path}")
