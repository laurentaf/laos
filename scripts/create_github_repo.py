#!/usr/bin/env python3
"""Create GitHub repo and push."""
import os, json, subprocess, urllib.request

token = os.environ.get("GITHUB_TOKEN")
if not token:
    print("GITHUB_TOKEN não encontrado no ambiente")
    exit(1)

# Create repo via GitHub API
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
    print(f"Repo created: {result['html_url']}")
except urllib.error.HTTPError as e:
    body = e.read().decode()
    print(f"HTTP {e.code}: {body}")
    if e.code == 422:
        print("Repo may already exist. Proceeding with push...")
    else:
        exit(1)

# Push
subprocess.run([
    "git", "remote", "add", "origin",
    f"https://laurentaf:{token}@github.com/laurentaf/chez-violeta-intelligence.git"
], cwd="F:/projects/chez-violeta-intelligence")

result = subprocess.run([
    "git", "push", "-u", "origin", "master"
], cwd="F:/projects/chez-violeta-intelligence", capture_output=True, text=True)

print(result.stdout)
if result.stderr:
    print("STDERR:", result.stderr[:500])
print(f"Exit: {result.returncode}")
