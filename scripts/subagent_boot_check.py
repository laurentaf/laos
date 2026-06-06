#!/usr/bin/env python3
"""
subagent_boot_check.py — Verifica tool readiness antes de despachar um subagente.

Proposta LACOUNCIL 518b82d5 (charter-autonomy) + 4a9f07c3 (external_directory)
+ f9b636fc (SDD scaffold — Missão 0, 6ª dimensão).
Para um subagente nomeado, valida 7 dimensoes:
  1. venv:                LAOS, latade, lacouncil, lan8n, ladesign, laengine, laecon
  2. daemon:              LADESIGN (pnpm install + node_modules)
  3. MCP:                 primarios presentes em .opencode/opencode.jsonc (opcionais lazy)
  4. paths:               projects/<name>/artifacts/<subclass>/ criaavel
  5. env:                 vars requeridas presentes ou com default documentado
  6. external_directory:  (proposta 4a9f07c3) parse do permission frontmatter
                          do subagente + cobertura dos paths do charter
                          + smoke-test em path de alto risco (dotfile caveat)
7. child-repo-skeleton: (proposta f9b636fc) SDD scaffold Missão 0.
Sub-check `skeleton` (always active) valida a
matriz per-file (8 fixos + 1 condicional).
Sub-check `first-real-adr` (gated) valida
ADR-mínimo-1 só após o 1º estágio decisório.
Meta-audit skip: se project_dir/project.yaml
nao existe, gate 7 pula com INFO (nao FAIL).
Escopo restrito: projetos reais sempre têm
project.yaml. Cobre meta-audits, ad-hoc reviews,
e sign-offs de propostas estruturais.
Detalhes em `knowledge/sdd-principles.md` §2.

Exit 0 = PASS; exit 1 = BLOCKED com findings acionaveis por check.

Uso:
  uv run python scripts/subagent_boot_check.py <subagent> --project-name <name>
  uv run python scripts/subagent_boot_check.py data-architect --project-name foo
"""

import argparse
import concurrent.futures
import json
import os
import re
import subprocess
import sys
import time
from pathlib import Path

import yaml

SUBAGENT_CHARTERS = {
    "data-architect": {
        "venv": ["laos", "latade", "lacouncil"],
        "daemon": [],
        "mcp_primary": ["latade"],
        "mcp_optional": ["context7"],
        "output_subclasses": ["data", "pipeline", "dq"],
        "env": ["LATADE_DB_PATH"],
        # Proposta 4a9f07c3: paths in-charter que o subagente precisa acessar
        # sem "Permissão necessária" prompt. Sincronizado com
        # knowledge/opencode-permissions.md §3 (tabela de paths por subagente).
        "external_directory_required_paths": [
            "../latade/**",                  # repo da capability primária
            "E:/projects/**",                # contexto cross-project
            "E:/projects/_commomdata/**",     # grounding data (convenção transversal)
        ],
    },
    "dashboard-designer": {
        "venv": ["laos"],
        "daemon": ["ladesign"],
        "mcp_primary": [],
        "mcp_optional": ["ladesign", "context7", "exa"],
        "output_subclasses": ["design", "deck"],
        "env": [],
        "external_directory_required_paths": [
            "../ladesign/**",                # repo da capability (skills, knowledge)
            "../ladesign/.od/**",            # daemon storage (DOTFILE — dotfile caveat risk)
            "E:/projects/**",                # contexto cross-project
        ],
    },
    "automation-engineer": {
        "venv": ["laos", "lan8n"],
        "daemon": [],
        "mcp_primary": ["lan8n"],
        "mcp_optional": ["n8n-community", "context7"],
        "output_subclasses": ["automation"],
        "env": ["N8N_API_URL"],
        "external_directory_required_paths": [
            "../lan8n/**",                   # repo da capability (templates, specs)
            "../n8n/**",                     # alias do repo (ver AGENTS.md naming note)
            "E:/projects/**",                # contexto cross-project
            "E:/projects/_commomdata/**",     # grounding data
        ],
    },
    "delivery-reviewer": {
        "venv": ["laos", "lacouncil", "latade"],
        "daemon": [],
        "mcp_primary": [],
        "mcp_optional": [],
        "output_subclasses": [],
        "env": [],
        # Read-only; edit: deny no frontmatter. Allowlist cobre a leitura de
        # contexto cross-project para validar artefatos.
        "external_directory_required_paths": [
            "E:/projects/**",
        ],
    },
    "orchestrator": {
        "venv": ["laos", "lacouncil", "latade", "lan8n", "laecon"],
        "daemon": ["ladesign"],
        "mcp_primary": ["lacouncil"],
        "mcp_optional": ["context7", "exa", "github"],
        "output_subclasses": ["_meta"],
        "env": ["GITHUB_TOKEN"],
        # Orchestrator nao tem permission frontmatter (config no JSONC top-level).
        # Check 6 skip — o JSONC ja foi auditado manualmente em opencode.jsonc.
        "external_directory_required_paths": [],
    },
    "capability-architect": {
        "venv": ["laos", "lacouncil", "latade", "lan8n", "laecon"],
        "daemon": ["ladesign"],
        "mcp_primary": ["lacouncil"],
        "mcp_optional": ["context7", "github"],
        "output_subclasses": ["_meta"],
        "env": [],
        "external_directory_required_paths": [
            "E:/projects/**",                # le contexto de qualquer projeto
            "../latade/**",
            "../lan8n/**",
            "../lacouncil/**",
            "../laengine/**",
            "../laecon/**",
            "../ladesign/**",
        ],
    },
    # workflow-decomposer (WDL v1, proposal a4fe9faa, BASIC cold start 2026-06-06).
    # Subagent dispatched BEFORE any specialist dispatch on a project loop.
    # Reuses the lacouncil MCP server (type=reference in opencode.jsonc), so
    # the "mcp_primary" is the lacouncil dependency — but the wall is
    # enforced by the charter, not the MCP config. 7-dim schema per
    # proposal a4fe9faa §"Subagent Charter":
    #   1. venv                — laos + lacouncil (read-only consumer)
    #   2. daemon              — none (no Node daemon; pure Python subagent)
    #   3. MCP primary         — lacouncil (read-only tool surface)
    #   4. paths               — artifacts/wdl/<plan-id>/ (child-repo path;
    #                            created by orchestrator, validated here)
    #   5. env                 — none required (lacouncil MCP carries its
    #                            own env via opencode.jsonc)
    #   6. external_directory  — ../lacouncil/** allow (per charter
    #                            frontmatter; E:/projects/** is `ask`
    #                            not `allow`, so external_directory gate
    #                            does NOT block but does NOT require coverage)
    #   7. child-repo-skeleton — wdl-rollout is a meta-project; sub-check
    #                            `skeleton` runs against the LAOS-mirror at
    #                            projects/_meta/wdl-rollout/. For per-project
    #                            dispatches, the orchestrator's project.yaml
    #                            + artifacts/wdl/<plan-id>/ is the
    #                            operative surface.
    "workflow-decomposer": {
        "venv": ["laos", "lacouncil"],
        "daemon": [],
        "mcp_primary": ["lacouncil"],
        "mcp_optional": [],
        "output_subclasses": ["wdl"],
        "env": [],
        "external_directory_required_paths": [
            "../lacouncil/**",                # WDL's only data source
        ],
    },
}

VENV_DIRS = {
    "laos": ".", "latade": "../latade", "lacouncil": "../lacouncil",
    "lan8n": "../n8n", "ladesign": "../ladesign", "laengine": "../laengine",
    "laecon": "../laecon",
}
DAEMON_DIRS = {"ladesign": ("../ladesign", "pnpm")}
ENV_DEFAULTS = {
    "LATADE_DB_PATH": ":memory:",
    "N8N_API_URL": "http://localhost:5678/api/v1",
}

# Smoke-test targets (proposta 4a9f07c3 §3): paths de alto risco onde o
# dotfile caveat ou location incomum pode falhar no opencode runtime.
# So rodamos um write/read/delete real para validar acesso do OS.
# Limitacao conhecida (knowledge/opencode-permissions.md §6): o teste
# definitivo do glob semantics acontece em dispatch real, nao aqui.
SMOKE_TEST_TARGETS = {
    "data-architect": "E:/projects/_commomdata/**",
    "dashboard-designer": "../ladesign/.od/**",   # dotfile — caso classico
    "automation-engineer": "E:/projects/_commomdata/**",
}

# ─── SDD scaffold matrix (proposta f9b636fc, 6ª dimensao) ──────────
# Matriz per-file de "conteudo minimo aceito" para o SDD scaffold
# (Missao 0). Proveniencia: `knowledge/sdd-principles.md` §2.
# O gate mecanico valida (a) existencia, (b) tamanho minimo, (c)
# presenca de cabecalhos de secao obrigatorias.
#
# Schema:
#   path:             path relativo ao child repo do projeto
#   min_chars:        tamanho minimo (len(text)) exigido
#   headers:          lista de regex case-insensitive que devem bater
#                     contra o texto (pelo menos um)
#   stub_by_design:   se True, o arquivo e' template canonico e o gate
#                     aceita como esta (sem checar tamanho/headers).
#                     Usado para `_template.md` do ADR e HARNESS.
#   conditional:      lista de `needs:` que disparam a exigencia.
#                     Se vazia, o arquivo e' sempre exigido.
SDD_SKELETON_MATRIX = [
    {
        "path": "spec/constitution.md",
        "min_chars": 400,
        "headers": [r"^##\s+Princ", r"^##\s+Scope", r"^##\s+Non.?goals"],
        "stub_by_design": False,
        "conditional": [],
    },
    {
        "path": "spec/todo.md",
        "min_chars": 100,
        "headers": [r"-\s+\[\s*\]"],   # ≥ 1 task `- [ ]`
        "stub_by_design": False,
        "conditional": [],
    },
    {
        "path": "spec/adr/_template.md",
        "min_chars": 0,
        "headers": [],
        "stub_by_design": True,         # copia literal do LATADE
        "conditional": [],
    },
    {
        "path": "spec/adr/README.md",
        "min_chars": 80,
        "headers": [r"^#\s+ADR", r"(vazio|empty|\bindex\b)"],
        "stub_by_design": False,
        "conditional": [],
    },
    {
        "path": "spec/harness/_template.md",
        "min_chars": 0,
        "headers": [],
        "stub_by_design": True,         # copia literal do LATADE
        "conditional": [],
    },
    {
        "path": "spec/specs/000-bootstrap/spec.md",
        "min_chars": 400,
        "headers": [r"^##\s+Contexto", r"^##\s+Decis", r"^##\s+Crit"],
        "stub_by_design": False,
        "conditional": [],
    },
    {
        "path": "contract.md",
        "min_chars": 250,
        "headers": [r"^##\s+Brief", r"^##\s+Needs?", r"^##\s+Deliverables?",
                    r"^##\s+Capabilities?", r"^##\s+Repo"],
        "stub_by_design": False,
        "conditional": [],
    },
    {
        "path": "README.md",
        "min_chars": 400,
        "headers": [r"^##\s+O\s+que", r"^##\s+Como", r"^##\s+Onde"],
        "stub_by_design": False,
        "conditional": [],
    },
    {
        "path": "spec/design-direction.md",
        "min_chars": 300,
        "headers": [],                   # 1 paragrafo + 2-3 principios macro
                                          # (sem header fixo; gate por chars)
        "stub_by_design": False,
        "conditional": ["dashboard", "design"],
    },
]


def hdr(s):
    print(f"\n=== {s} ===")


def ok(s):
    print(f"  [OK]  {s}")


def fail(s):
    print(f"  [FAIL] {s}")


def warn(s):
    print(f"  [WARN] {s}")


def check_venv(cap, root):
    venv = (root / VENV_DIRS[cap] / ".venv").resolve()
    py = venv / ("Scripts/python.exe" if os.name == "nt" else "bin/python")
    if not venv.exists():
        fail(f"{cap}: venv ausente em {venv}")
        fail(f"  Fix: cd {VENV_DIRS[cap]} && uv sync")
        return False
    if not py.exists():
        fail(f"{cap}: python ausente em {py}")
        return False
    # Drift detection: compare venv mtime against the LOCKFILE (not pyproject).
    # pyproject.toml can be touched for non-dep reasons (formatting, comments);
    # the lockfile is the source of truth for installed deps.
    pyp = (root / VENV_DIRS[cap] / "pyproject.toml").resolve()
    lock = (root / VENV_DIRS[cap] / "uv.lock").resolve()
    ref = lock if lock.exists() else pyp
    if ref is not None and ref.exists() and ref.stat().st_mtime > venv.stat().st_mtime:
        fail(f"{cap}: lockfile mais novo que .venv (drift)")
        fail(f"  Fix: cd {VENV_DIRS[cap]} && uv sync")
        return False
    ok(f"{cap}: venv OK")
    return True


def check_daemon(cap, root):
    if cap not in DAEMON_DIRS:
        return True
    d, pm = DAEMON_DIRS[cap]
    p = (root / d).resolve()
    if not p.exists():
        fail(f"{cap}: daemon dir ausente em {p}")
        return False
    if not (p / "node_modules").exists():
        fail(f"{cap}: node_modules ausente")
        fail(f"  Fix: cd {d} && {pm} install")
        return False
    ok(f"{cap}: daemon OK")
    return True


def check_mcp(mcps, root):
    # Backwards-compat shim: callers from older dispatches may still pass
    # a single list. Treat the list as primary, no optionals. New callers
    # should use check_mcp_primary_optional.
    return check_mcp_primary_optional(mcps, [], root)


# ─── Check 3b: smoke-test *.health() via stdio JSON-RPC ─────────
# Proposta LACOUNCIL f82d6261 (4/4 SIM, supermaioria). Restricoes do
# Conselho (nao negociaveis):
#   1. Invocacao paralela via concurrent.futures.ThreadPoolExecutor.
#   2. Timeout 2-3s por invocao, com fail-fast.
#   3. MCPs opcionais (context7, exa, github): WARN (nao bloqueia).
#      Primarios (latade, ladesign, lan8n, lacouncil): BLOCK se health() falhar.
# Sem dependencias novas; usa apenas stdlib (subprocess, json, concurrent.futures, time).

MCP_HEALTH_TIMEOUT_S = 2.5  # fail-fast por invocacao
MCP_STDIO_PROTOCOL_VERSION = "2024-11-05"


def _strip_jsonc_comments(text):
    """Remove `// line` and `/* block */` comments from a JSONC string,
    preserving string contents. Sufficient for opencode.jsonc.
    """
    out, i, n, in_string, escape = [], 0, len(text), False, False
    while i < n:
        c = text[i]
        if in_string:
            out.append(c)
            if escape:
                escape = False
            elif c == "\\":
                escape = True
            elif c == '"':
                in_string = False
            i += 1
            continue
        if c == '"':
            in_string = True
            out.append(c)
            i += 1
            continue
        if c == "/" and i + 1 < n and text[i + 1] == "/":
            i += 2
            while i < n and text[i] != "\n":
                i += 1
            continue
        if c == "/" and i + 1 < n and text[i + 1] == "*":
            i += 2
            while i < n - 1 and not (text[i] == "*" and text[i + 1] == "/"):
                i += 1
            i += 2
            continue
        out.append(c)
        i += 1
    return "".join(out)


def _parse_mcp_configs(cfg_path):
    """Parse opencode.jsonc and return {mcp_name: cfg_block} for every
    entry under 'mcp'. Returns {} if file missing or invalid.
    """
    if not cfg_path.exists():
        return {}
    try:
        raw = cfg_path.read_text(encoding="utf-8")
        data = json.loads(_strip_jsonc_comments(raw))
        return data.get("mcp", {}) or {}
    except (json.JSONDecodeError, OSError) as e:
        fail(f"opencode.jsonc parse error: {e}")
        return {}


def _resolve_mcp_env(env_block, root):
    """Build a resolved env dict for an MCP subprocess.
    - {env:NAME}             -> os.environ[NAME] (empty if missing)
    - {workspaceFolder}      -> str(root) (LAOS repo root)
    - other string values    -> kept as-is
    """
    merged = os.environ.copy()
    if not isinstance(env_block, dict):
        return merged
    for k, v in env_block.items():
        if not isinstance(v, str):
            merged[k] = v
            continue
        if v.startswith("{env:") and v.endswith("}"):
            merged[k] = os.environ.get(v[5:-1], "")
        elif "{workspaceFolder}" in v:
            merged[k] = v.replace("{workspaceFolder}", str(root))
        else:
            merged[k] = v
    return merged


def _mcp_frame(req):
    """Frame a JSON-RPC request for MCP stdio transport. FastMCP's stdio
    server reads line-delimited JSON (`async for line in stdin` then
    JSONRPCMessage.model_validate_json(line) — see mcp/server/stdio.py:63-65).
    No Content-Length headers; one JSON object per newline.
    """
    return json.dumps(req) + "\n"


def _parse_mcp_framed_messages(out_bytes):
    """Parse newline-delimited JSON-RPC messages from stdout bytes.
    FastMCP's stdio transport writes one JSON object per line; we split
    on newlines and json.loads each non-empty line. Order preserved.
    """
    msgs = []
    text = out_bytes.decode("utf-8", errors="replace")
    for line in text.splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            msgs.append(json.loads(line))
        except json.JSONDecodeError:
            pass
    return msgs


def _smoke_test_mcp(name, cfg_block, root, timeout=MCP_HEALTH_TIMEOUT_S):
    """Spawn the MCP server (local stdio transport) and call its `health`
    tool via JSON-RPC. Returns (ok, info, elapsed_s).
    Falls back to `tools/list` if `health` tool not found (e.g. ladesign).
    Catches "config-OK but server broken at runtime" (proposal f82d6261).
    """
    command = cfg_block.get("command") if isinstance(cfg_block, dict) else None
    if not command or not isinstance(command, list):
        return (False, "no `command` array in opencode.jsonc", 0.0)
    env_block = cfg_block.get("env", {}) or {}
    full_env = _resolve_mcp_env(env_block, root)
    t0 = time.monotonic()
    try:
        kwargs = dict(
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            env=full_env,
            cwd=str(root),
        )
        if os.name == "nt":
            kwargs["creationflags"] = 0x08000000  # CREATE_NO_WINDOW
        proc = subprocess.Popen(command, **kwargs)
    except (OSError, ValueError) as e:
        return (False, f"spawn failed: {type(e).__name__}: {e}", time.monotonic() - t0)

    init_req = _mcp_frame({
        "jsonrpc": "2.0", "id": 1, "method": "initialize",
        "params": {
            "protocolVersion": MCP_STDIO_PROTOCOL_VERSION,
            "capabilities": {},
            "clientInfo": {"name": "laos-boot-check", "version": "1.0"},
        },
    })
    health_req = _mcp_frame({
        "jsonrpc": "2.0", "id": 2, "method": "tools/call",
        "params": {"name": "health", "arguments": {}},
    })
    list_req = _mcp_frame({
        "jsonrpc": "2.0", "id": 3, "method": "tools/list", "params": {},
    })
    try:
        proc.stdin.write((init_req + health_req + list_req).encode("utf-8"))
        proc.stdin.flush()
    except (BrokenPipeError, OSError) as e:
        try: proc.kill()
        except Exception: pass
        return (False, f"server died on input: {e}", time.monotonic() - t0)

    try:
        out_bytes, err_bytes = proc.communicate(timeout=timeout)
    except subprocess.TimeoutExpired:
        try: proc.kill()
        except Exception: pass
        try: out_bytes, err_bytes = proc.communicate()
        except Exception: out_bytes, err_bytes = b"", b""
        return (False, f"timeout after {timeout}s; stderr={err_bytes[:200]!r}", time.monotonic() - t0)
    finally:
        if proc.poll() is None:
            try: proc.kill()
            except Exception: pass

    elapsed = time.monotonic() - t0
    out = out_bytes.decode("utf-8", errors="replace")
    err = err_bytes.decode("utf-8", errors="replace")
    msgs = _parse_mcp_framed_messages(out.encode("utf-8", errors="replace"))
    health_resp = next((m for m in msgs if m.get("id") == 2), None)
    list_resp = next((m for m in msgs if m.get("id") == 3), None)

    # Path 1: health() succeeded
    if health_resp and "result" in health_resp:
        result = health_resp["result"]
        if result.get("isError"):
            return (False, f"health() returned isError: {str(result)[:200]}", elapsed)
        content = result.get("content", [])
        if content and isinstance(content, list):
            text = content[0].get("text", "") if isinstance(content[0], dict) else ""
            return (True, f"health() OK: {text[:120]}", elapsed)
        return (True, f"health() OK: {str(result)[:120]}", elapsed)

    # Path 2: health() tool not found -> fall back to tools/list
    if health_resp and "error" in health_resp:
        err_msg = (health_resp["error"].get("message") or "").lower()
        if "tool" in err_msg and "not found" in err_msg:
            if list_resp and "result" in list_resp:
                tools = list_resp["result"].get("tools", []) or []
                names = [t.get("name", "?") for t in tools[:5] if isinstance(t, dict)]
                return (True, f"health() not exposed; tools/list OK ({len(tools)} tools: {names})", elapsed)
            return (False, f"health() not exposed AND tools/list failed: {str(list_resp)[:200]}", elapsed)
        return (False, f"health() error: {str(health_resp['error'])[:200]}", elapsed)

    # Path 3: no health() response at all (id mismatch) — accept tools/list as fallback
    if list_resp and "result" in list_resp:
        tools = list_resp["result"].get("tools", []) or []
        return (True, f"tools/list OK ({len(tools)} tools; no health() response id=2)", elapsed)

    return (False, f"no usable response ({len(msgs)} msgs); stderr={err[:200]!r}", elapsed)


def check_mcp_primary_optional(mcp_primary, mcp_optional, root):
    """Check 3 (proposta f82d6261): textual config check + parallel
    smoke-test of *.health() via stdio JSON-RPC. Primary MCPs BLOCK;
    optional MCPs WARN. Remote MCPs (type=remote) skip smoke-test.
    Returns True if dispatch is safe (no primary failures).
    """
    if not mcp_primary and not mcp_optional:
        ok("(sem MCPs - subagent read-only)")
        return True
    cfg = root / ".opencode" / "opencode.jsonc"
    if not cfg.exists():
        fail(f"opencode.jsonc ausente em {cfg}")
        return False

    # Phase 1: textual config check (light, must pass before smoke)
    raw = cfg.read_text(encoding="utf-8")
    all_mcps = list(mcp_primary) + list(mcp_optional)
    missing = [m for m in all_mcps if f'"{m}":' not in raw]
    if missing:
        fail(f"MCPs ausentes em opencode.jsonc: {missing}")
        fail(f"  Fix: adicionar mcp.{missing[0]} ao orchestrator config")
        return False

    # Phase 2: parse full config and identify local stdio MCPs to smoke-test
    configs = _parse_mcp_configs(cfg)
    if not configs:
        fail("opencode.jsonc parse falhou; smoke-test pulado")
        return False

    findings = 0
    targets = []
    for name in all_mcps:
        cfg_block = configs.get(name)
        if cfg_block is None:
            fail(f"{name}: bloco no opencode.jsonc nao encontrado apos parse")
            findings += 1
            continue
        if not cfg_block.get("enabled", True):
            warn(f"{name}: disabled em opencode.jsonc (skip smoke-test)")
            continue
        if cfg_block.get("type") == "remote":
            # Remote MCPs (context7, exa, github) usam URL, nao stdio:
            # nao podem ser stdio-probed do boot check. Config check ja' passou.
            ok(f"{name}: remote MCP (stdio smoke-test NAO aplicavel)")
            continue
        targets.append((name, cfg_block, name in mcp_primary))

    if not targets:
        ok("(todos os MCPs aplicaveis sao remote/disabled; smoke-test pulado)")
        return findings == 0

    # Phase 3: parallel stdio smoke-test (ThreadPoolExecutor, fail-fast 2.5s)
    t0 = time.monotonic()
    with concurrent.futures.ThreadPoolExecutor(max_workers=len(targets)) as ex:
        future_to_meta = {
            ex.submit(_smoke_test_mcp, name, cfg_block, root): (name, is_primary)
            for name, cfg_block, is_primary in targets
        }
        for fut in concurrent.futures.as_completed(future_to_meta):
            name, is_primary = future_to_meta[fut]
            try:
                ok_flag, info, elapsed = fut.result()
            except Exception as e:
                ok_flag, info, elapsed = False, f"exception: {type(e).__name__}: {e}", 0.0
            tag = "PRIMARY" if is_primary else "OPTIONAL"
            if ok_flag:
                ok(f"{name}.health()  {tag}  PASS  ({elapsed:.2f}s)  -- {info}")
            else:
                if is_primary:
                    fail(f"{name}.health()  {tag}  BLOCK  ({elapsed:.2f}s)  -- {info}")
                    findings += 1
                else:
                    warn(f"{name}.health()  {tag}  WARN  ({elapsed:.2f}s)  -- {info}")
    total = time.monotonic() - t0
    if findings == 0:
        ok(f"smoke-test completo em {total:.2f}s (paralelo, max_workers={len(targets)})")
    return findings == 0


def check_paths(root, project, subclasses):
    if not subclasses:
        ok("(subagent read-only ou sem subclasses)")
        return True
    if not project:
        fail("--project-name e obrigatorio para subagents que escrevem em artifacts/")
        return False
    base = root / "projects" / project / "artifacts"
    base.mkdir(parents=True, exist_ok=True)
    for s in subclasses:
        (base / s).mkdir(parents=True, exist_ok=True)
    ok(f"paths artifacts/{{{'/'.join(subclasses)}}} OK sob {base}")
    return True


def check_env(env):
    if not env:
        ok("(sem env vars requeridas)")
        return True
    miss = [v for v in env if v not in os.environ and v not in ENV_DEFAULTS]
    if miss:
        fail(f"env vars ausentes sem default: {miss}")
        fail(f"  Fix: setar via OS env ou .env (nunca commitar)")
        return False
    ok(f"env vars {env} OK")
    return True


# ─── Check 6: external_directory (proposta 4a9f07c3) ──────────────

def parse_frontmatter_external_directory(agent_path):
    """Parse .opencode/agent/<name>.md YAML frontmatter and return the
    permission.external_directory block as a dict {pattern: action}.
    Returns {} if the file is missing, has no frontmatter, or the block
    is absent. The capability-architect implementing item 5 of the
    proposal is responsible for adding the frontmatter block; this
    function only reads it.
    """
    if not agent_path.exists():
        return {}
    text = agent_path.read_text(encoding="utf-8")
    if not text.startswith("---"):
        return {}
    end = text.find("\n---", 3)
    if end < 0:
        return {}
    fm_text = text[3:end].strip()
    try:
        data = yaml.safe_load(fm_text)
    except yaml.YAMLError:
        return {}
    if not isinstance(data, dict):
        return {}
    perm = data.get("permission", {})
    if not isinstance(perm, dict):
        return {}
    ext = perm.get("external_directory", {})
    if isinstance(ext, str):
        # Shorthand form: "ask" or "allow" applies to every path.
        return {"*": ext}
    if isinstance(ext, dict):
        return ext
    return {}


def glob_pattern_covers(required, pattern):
    """Heuristic: does `pattern` (an allowlist entry like '../latade/**')
    cover `required` (a charter path like '../latade/foo/bar')?
    Conservative: false negatives are OK (we'll flag a gap), false
    positives are NOT (would let a path slip through that shouldn't).
    Supports the common glob forms used in opencode permission: '**',
    '*', and prefix-based matching.
    """
    if pattern == "*":
        return True
    p = pattern.rstrip("/").rstrip("\\")
    r = required.rstrip("/").rstrip("\\")
    if p.endswith("/**"):
        prefix = p[:-3]
        return r == prefix or r.startswith(prefix + "/") or r.startswith(prefix + "\\")
    if p.endswith("/*"):
        prefix = p[:-2]
        return r.startswith(prefix + "/") or r.startswith(prefix + "\\")
    if "**" in p:
        # Translate ** to .* for regex match; conservative.
        regex = "^" + re.escape(p).replace(r"\*\*", ".*").replace(r"\*", "[^/\\\\]*") + "$"
        return bool(re.match(regex, r))
    return p == r


def check_external_directory(subagent, root):
    """Check 6 (proposta 4a9f07c3): parse the subagente's permission
    frontmatter and verify its external_directory allowlist covers every
    path declared in the charter. Returns False on any gap.

    Failure modes covered:
      - Frontmatter ausente ou sem bloco permission.external_directory
      - Allowlist presente mas incompleta (path do charter nao coberto)
      - Smoke-test em path de alto risco (dotfile caveat) bloqueado pelo OS
    """
    charter = SUBAGENT_CHARTERS.get(subagent, {})
    required = charter.get("external_directory_required_paths", [])
    if not required:
        ok("(charter nao declara external_directory_required_paths; check 6 skip)")
        return True
    agent_path = root / ".opencode" / "agent" / f"{subagent}.md"
    allowlist = parse_frontmatter_external_directory(agent_path)
    if not allowlist:
        fail(f"{subagent}: frontmatter sem permission.external_directory")
        fail(f"  Agent file: {agent_path}")
        fail(f"  Charter declara paths que exigem allowlist: {required}")
        fail(f"  Fix (proposta 4a9f07c3 item 5 — orchestrator): adicionar")
        fail(f"       bloco 'external_directory' no permission frontmatter de")
        fail(f"       .opencode/agent/{subagent}.md cobrindo os paths acima.")
        fail(f"  Documentacao canonica: knowledge/opencode-permissions.md")
        # Run smoke-test even on gap (informational)
        smoke_test_external_directory(subagent, required, root)
        return False
    # Coverage check
    missing = []
    for req in required:
        if not any(glob_pattern_covers(req, pat) for pat, action in allowlist.items()
                   if action == "allow"):
            missing.append(req)
    if missing:
        fail(f"{subagent}: external_directory allowlist nao cobre paths do charter")
        fail(f"  Allowlist atual: {sorted(allowlist.keys())}")
        fail(f"  Paths faltando: {missing}")
        fail(f"  Fix: adicionar entries faltantes ao permission.external_directory")
        return False
    ok(f"{subagent}: external_directory allowlist cobre {len(required)}/{len(required)} path(s) do charter")
    # Smoke-test for high-risk paths
    if not smoke_test_external_directory(subagent, required, root):
        return False
    return True


def smoke_test_external_directory(subagent, required_paths, root):
    """Real write/read/delete probe at a representative in-charter path.
    Targets paths flagged as high-risk (dotfile caveat or unusual
    location) per the dashboard-designer's vote on 4a9f07c3.
    Validates OS-level filesystem access. The definitive test of
    opencode glob semantics happens in real dispatch (proposal
    acceptance criteria #6/#7); this catches config-time failures
    and OS-level blocks (ACL, path-not-exists).
    """
    target = SMOKE_TEST_TARGETS.get(subagent)
    if not target or target not in required_paths:
        ok("(sem smoke-test alvo para este subagente; allowlist textual confere)")
        return True
    # Translate glob pattern to a real probe path.
    # '../<cap>/.od/**'  -> '../<cap>/.od/__permission_probe__'
    # 'E:/projects/_commomdata/**' -> 'E:/projects/_commomdata/__permission_probe__'
    real = target.replace("**", "__permission_probe__").rstrip("/").rstrip("\\")
    if real.startswith("../") or real.startswith("..\\"):
        probe_dir = (root / real).resolve()
    elif re.match(r"^[A-Za-z]:", real):
        probe_dir = Path(real)
    else:
        probe_dir = (root / real).resolve()
    try:
        probe_dir.mkdir(parents=True, exist_ok=True)
        probe_file = probe_dir / "probe.txt"
        probe_file.write_text("LAOS boot-check smoke-test " + subagent, encoding="utf-8")
        content = probe_file.read_text(encoding="utf-8")
        assert "LAOS" in content
        probe_file.unlink()
        # Try to clean up the probe dir; tolerate non-empty.
        try:
            probe_dir.rmdir()
        except OSError:
            pass
        ok(f"smoke-test em {probe_dir} OK (write/read/delete)")
        return True
    except Exception as e:
        fail(f"smoke-test em {probe_dir} bloqueado: {type(e).__name__}: {e}")
        fail(f"  Causas provaveis: ACL do Windows, parent path nao acessivel,")
        fail(f"  ou dotfile caveat do glob opencode (definitive test: dispatch real).")
        return False


# ─── Check 7: child-repo-skeleton (proposta f9b636fc) ────────────

def _project_yaml_needs(project_dir):
    """Read `project.yaml` from the child repo (if exists) and return
    the `needs:` list. Returns [] if the file is missing, malformed,
    or has no `needs:` field. Used to gate the conditional file
    `spec/design-direction.md` (only required when `dashboard` or
    `design` is in needs).
    """
    p = project_dir / "project.yaml"
    if not p.exists():
        # try the LAOS project path (project.yaml mirror at LAOS root)
        # — passed in by caller via project_dir being the child repo
        return []
    try:
        data = yaml.safe_load(p.read_text(encoding="utf-8"))
    except (yaml.YAMLError, OSError):
        return []
    if not isinstance(data, dict):
        return []
    needs = data.get("needs", [])
    if not isinstance(needs, list):
        return []
    return [str(n).strip() for n in needs]


def _resolve_child_repo(root, project_name):
    """Locate the child repo for a project. The LAOS mirror is at
    `projects/<name>/` (contains `project.yaml`); the child repo is
    the URL stored in `project.yaml` `repo:`. We do not clone here —
    the SDD scaffold is checked against the LAOS mirror first, and
    falls back to the child repo path if the mirror doesn't carry
    the spec/ tree (e.g. when the orchestrator created the child
    repo with `github.create_repository` and pushed the scaffold
    there). For MVP, we check BOTH paths and accept the first one
    that has the file.
    """
    candidates = []
    if project_name:
        candidates.append(root / "projects" / project_name)
        # TODO (future): also check the child repo URL from project.yaml
        # once `github.*` MCP exposes `get_repository_local_path`.
    return candidates


def _sdd_check_one(file_path, spec):
    """Validate a single file of the SDD matrix. Returns (ok, msg).
    ok=True  -> no failure
    ok=False -> failure with actionable message
    """
    if not file_path.exists():
        return False, (
            f"{spec['path']}: arquivo ausente. "
            f"Fix: criar a partir de `registry/spec-templates/` "
            f"(proposta f9b636fc Missao 0)."
        )
    if spec["stub_by_design"]:
        # Templates canonicos (copia literal do LATADE): gate aceita
        # o arquivo como esta', sem checar tamanho ou headers.
        return True, f"{spec['path']}: stub-by-design OK (template canonico)"
    try:
        text = file_path.read_text(encoding="utf-8")
    except OSError as e:
        return False, f"{spec['path']}: erro de leitura: {e}"
    if len(text) < spec["min_chars"]:
        return False, (
            f"{spec['path']}: {len(text)} chars; precisa >= {spec['min_chars']}."
        )
    if spec["headers"]:
        for pattern in spec["headers"]:
            if not re.search(pattern, text, re.MULTILINE | re.IGNORECASE):
                return False, (
                    f"{spec['path']}: header obrigatorio nao encontrado "
                    f"(regex: {pattern!r}). Fix: adicionar a secao."
                )
    return True, f"{spec['path']}: OK ({len(text)} chars, headers batem)"


def check_child_repo_skeleton(subagent, root, project_name):
    """Check 7 (proposta f9b636fc): SDD scaffold (Missao 0).

    Two sub-checks:
      (a) `skeleton`         - always active. Walks SDD_SKELETON_MATRIX
                               and validates existence + size + headers
                               for every applicable file. FAIL on any
                               gap with actionable message.
      (b) `first-real-adr`   - GATED. Active only when at least one
                               decision-producing stage has completed.
                               Operational signal: ADR count in
                               `spec/adr/` (excluding `_template.md` and
                               `README.md`) > 0. If the project has at
                               least one real ADR, then require that the
                               spec/_template and README are present and
                               that the ADRs follow NNN-<slug>.md
                               numbering starting at 001.

    TODO: quando `project.yaml` ganhar campo explicito `current_stage`,
          usar esse campo para gatear (b) em vez do ADR-count fallback.
          Por ora, o signal e' robusto: se ja' existe um ADR real, o
          decisorio 1 ja' passou.
    """
    if not project_name:
        # Sub-check (a) nao pode rodar sem project-name; skip com INFO.
        ok("(sub-check `skeleton` skip: --project-name nao fornecido)")
        ok("(sub-check `first-real-adr` skip: --project-name nao fornecido)")
        return True
    candidates = _resolve_child_repo(root, project_name)
    if not candidates:
        ok("(sub-check `skeleton` skip: nenhum path candidato para o child repo)")
        return True
    project_dir = candidates[0]
    # Meta-audit skip: se nao ha' project.yaml no project_dir, nao e' um
    # audit de projeto (e' meta-audit, ad-hoc review, etc.). Gate 7 nao
    # se aplica; sai com INFO. Cobre o caso chicken-and-egg onde o proprio
    # sign-off da proposta que adiciona a gate e' despachado (ex.: BASIC
    # sign-off G4 da proposta f9b636fc, ou auditorias da propria LAOS).
    if not (project_dir / "project.yaml").exists():
        ok(f"(sub-check `skeleton` skip: {project_dir.name}/project.yaml "
           f"ausente - nao e' audit de projeto; meta-audit ou ad-hoc review)")
        ok("(sub-check `first-real-adr` skip: idem)")
        return True
    # Read needs to gate the conditional `spec/design-direction.md`
    needs = _project_yaml_needs(project_dir)
    # ---- Sub-check (a): `skeleton` ----
    skeleton_failures = 0
    for spec in SDD_SKELETON_MATRIX:
        if spec["conditional"]:
            if not any(n in spec["conditional"] for n in needs):
                # Conditional nao disparada; gate nao reclama.
                continue
        file_path = project_dir / spec["path"]
        passed, msg = _sdd_check_one(file_path, spec)
        if passed:
            ok(msg)
        else:
            fail(f"sub-check `skeleton`: {msg}")
            skeleton_failures += 1
    # ---- Sub-check (b): `first-real-adr` (gated) ----
    adr_dir = project_dir / "spec" / "adr"
    real_adrs = []
    if adr_dir.exists():
        real_adrs = [
            p for p in sorted(adr_dir.glob("*.md"))
            if p.name not in ("_template.md", "README.md")
        ]
    if not real_adrs:
        # Gate desligado: nenhum ADR real ainda, 1o decisorio nao chegou.
        # INFO-only, nao FAIL.
        ok(f"sub-check `first-real-adr`: INFO — nenhum ADR real em "
           f"spec/adr/ (gate desligado ate o 1o estagio decisorio)")
    else:
        # Gate ligado: 1o decisorio ja' passou. Validar numeracao
        # basica (>= 001, sem gaps no prefixo numerico).
        bad_names = []
        for p in real_adrs:
            m = re.match(r"^(\d{3,})-", p.name)
            if not m:
                bad_names.append(p.name)
        if bad_names:
            fail(f"sub-check `first-real-adr`: ADRs com numeracao invalida "
                 f"(esperado NNN-<slug>.md a partir de 001): {bad_names}")
            skeleton_failures += 1
        else:
            ok(f"sub-check `first-real-adr`: {len(real_adrs)} ADR(s) real(is) "
               f"encontrado(s); numeracao OK")
    if skeleton_failures:
        return False
    return True


# ─── main ────────────────────────────────────────────────────────

def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("subagent")
    ap.add_argument("--project-root", default=".")
    ap.add_argument("--project-name", default=None)
    args = ap.parse_args()

    c = SUBAGENT_CHARTERS.get(args.subagent)
    if not c:
        print(f"ERRO: subagente '{args.subagent}' desconhecido. Conhecidos: {list(SUBAGENT_CHARTERS)}", file=sys.stderr)
        return 1
    root = Path(args.project_root).resolve()
    print(f"Boot check: {args.subagent} @ {root}")
    findings = 0

    hdr("1. venv")
    for cap in c["venv"]:
        if not check_venv(cap, root):
            findings += 1

    hdr("2. daemon")
    for cap in c["daemon"]:
        if not check_daemon(cap, root):
            findings += 1
    if not c["daemon"]:
        ok("(sem daemon requerido)")

    hdr("3. MCP primario (smoke-test *.health() — proposta f82d6261)")
    if not check_mcp_primary_optional(c["mcp_primary"], c.get("mcp_optional", []), root):
        findings += 1

    hdr("4. paths")
    if not check_paths(root, args.project_name, c["output_subclasses"]):
        findings += 1

    hdr("5. env")
    if not check_env(c["env"]):
        findings += 1

    hdr("6. external_directory (proposta 4a9f07c3)")
    if not check_external_directory(args.subagent, root):
        findings += 1

    hdr("7. child-repo-skeleton (proposta f9b636fc — Missao 0)")
    if not check_child_repo_skeleton(args.subagent, root, args.project_name):
        findings += 1

    print()
    if findings:
        print(f"BLOCKED: {findings} check(s) com falha.")
        print(f"Proximo passo: corrija os findings e rode novamente antes de despachar {args.subagent}.")
        return 1
    print(f"PASS: {args.subagent} pronto para dispatch. Brief curto, sem re-statuir charter.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
