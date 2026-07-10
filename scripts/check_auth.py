#!/usr/bin/env python3
"""Check what auth methods are available."""
import os

# Check env
for key in sorted(os.environ.keys()):
    if 'GITHUB' in key.upper() or 'GH_' in key.upper() or 'TOKEN' in key.upper() or 'PASSWORD' in key.upper():
        val = os.environ[key]
        masked = val[:8] + '...' if len(val) > 8 else '(empty)'
        print(f"{key}={masked}")

# Check git credential helpers
import subprocess
r = subprocess.run(['git', 'config', '--global', 'credential.helper'], capture_output=True, text=True)
print(f"\nGit credential helper: {r.stdout.strip() or '(none)'} {r.stderr.strip()}")
