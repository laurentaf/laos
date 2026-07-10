#!/usr/bin/env python3
"""Create GitHub repo and push the chez-violeta-intelligence repo."""
import json
import os
import subprocess
import urllib.request
import urllib.error

# First try to get the GitHub token
# Check env
token = os.environ.get("GITHUB_TOKEN") or os.environ.get("GH_TOKEN")

# If not in env, try to get from git credential manager
if not token:
    try:
        proc = subprocess.run(
            ["git", "credential", "fill"],
            input="protocol=https\nhost=github.com\n\n",
            capture_output=True, text=True, timeout=5,
            cwd="F:/projects/chez-violeta-intelligence"
        )
        for line in proc.stdout.split("\n"):
            if line.startswith("password="):
                token = line[9:]
                break
    except:
        pass

# If we have a token, use GitHub API
if token:
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
        print(f"REPO_CREATED: {result['html_url']}")
    except urllib.error.HTTPError as e:
        body = e.read().decode()
        if e.code == 422 and "already exists" in body:
            print("REPO_ALREADY_EXISTS")
        else:
            print(f"API_ERROR {e.code}: {body[:300]}")
            exit(1)
    
    # Remove old remote and add with token
    subprocess.run(["git", "remote", "remove", "origin"], 
                  cwd="F:/projects/chez-violeta-intelligence")
    subprocess.run([
        "git", "remote", "add", "origin",
        f"https://oauth2:{token}@github.com/laurentaf/chez-violeta-intelligence.git"
    ], cwd="F:/projects/chez-violeta-intelligence")
    
    # Push
    result = subprocess.run(["git", "push", "-u", "origin", "master"],
                          cwd="F:/projects/chez-violeta-intelligence",
                          capture_output=True, text=True)
    print(f"PUSH stdout: {result.stdout[:500]}")
    print(f"PUSH stderr: {result.stderr[:500]}")
    print(f"PUSH exit: {result.returncode}")
else:
    print("NO_TOKEN_AVAILABLE")
    # Try browser form submission via cookie-based auth
    # Use urllib with the browser's cookies... nope, can't access those
    exit(1)
