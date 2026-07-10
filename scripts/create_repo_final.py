#!/usr/bin/env python3
"""Create GitHub repo using PyGithub or direct API."""
import json
import subprocess
import urllib.request
import urllib.error
import os

# Try to get token from multiple sources
token = os.environ.get("GITHUB_TOKEN")

# If no env token, try git credential manager
if not token:
    try:
        result = subprocess.run(
            ["git", "config", "--global", "credential.helper"],
            capture_output=True, text=True, timeout=5
        )
        helper = result.stdout.strip()
        if helper:
            # Try to use the helper
            pass
    except:
        pass

if token:
    # Create repo via API
    data = json.dumps({
        "name": "chez-violeta-intelligence",
        "description": "Chez Violeta — Operations Intelligence Platform",
        "private": False,
        "auto_init": False
    }).encode()

    req = urllib.request.Request(
        "https://api.github.com/user/repos",
        data=data,
        headers={
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
            "Accept": "application/vnd.github.v3+json"
        },
        method="POST"
    )

    try:
        resp = urllib.request.urlopen(req)
        result = json.loads(resp.read())
        print(f"CREATED: {result['html_url']}")
    except urllib.error.HTTPError as e:
        body = e.read().decode()
        if e.code == 422 and "already exists" in body:
            print("ALREADY_EXISTS")
        else:
            print(f"ERROR {e.code}: {body[:200]}")
            exit(1)
else:
    print("NO_GITHUB_TOKEN - creating via browser form submit")
    
    # Try to use the browser session via a POST to the GitHub form
    # This uses the same endpoint the browser form would submit to
    import http.cookiejar
    
    # We can't get browser cookies from Python, so let's check
    # if there's a way to use the browser
    print("Cannot create repo without GITHUB_TOKEN or browser session access")
    exit(1)
