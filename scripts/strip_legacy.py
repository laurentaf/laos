#!/usr/bin/env python3
"""Strip legacy/governance from the laos-v2 repo (product-only).

Removes: preflight_check test (WDL/laecon legacy), _meta projects,
governance meta-projects, legacy scripts. Keeps delivery projects.

Run from F:\projects\laos-v2.
"""

from __future__ import annotations

import pathlib
import shutil

NEW = pathlib.Path(r"F:\projects\laos-v2")
LOG = NEW / ".laos" / "strip.log"

# governance/meta projects to remove (product = delivery projects only)
META_PROJECTS = [
    "_example", "_meta", "capability-architect", "charter-autonomy",
    "charter-autonomy-test", "wdl-rollout", "smoke-test",
    "readme-improvement", "laos-brand", "lacareerops-refactor",
    "lacareerops-selfeval", "previsao-concursos",
]

# legacy scripts to remove (git/one-shot/governance)
LEGACY_SCRIPTS = [
    "preflight_check.py", "subagent_boot_check.py", "toolchain_inventory.py",
    "sign_wdl.py", "migrate_lacouncil_wdl_signatures.py", "pre-commit.hook.py",
    "post-merge.hook.py", "delivery-hook.py", "run_hidden.py", "run-hidden.py",
    "load_env.py", "list_capabilities.py", "bootstrap_project.py",
    "archive_legacy.py", "split_map.py", "build_v2.py", "jsonc_check.py",
    "go_models.py", "go_direct.py", "nota10_validate.py",
    "smoke_llm.py", "litellm_probe.py", "litellm_langfuse_check.py",
    "litellm_env_check.py", "litellm_debug.py", "langfuse_traces.py",
    "langfuse_scores.py", "langfuse_cost.py", "langfuse_full.py",
    "langfuse_db_check.py", "langfuse_keys.py", "langfuse_auth_debug.py",
    "langfuse_score_post.py", "cost_debug.py", "check_auth.py",
    "console_probe.py", "console_llm_test.py", "force_restart.py",
    "limpeza_run.py", "limpeza_stage.py", "limpeza_phase.py",
    "limpeza_phase4.py", "limpeza_full.py", "limpeza_reset.py",
    "limpeza_inspect.py", "limpeza_inspect2.py", "limpeza_verify.py",
    "limpeza_final.py", "limpeza_browser.py", "limpeza_facts.py",
    "limpeza_handoff.py", "free_lock.py", "kill_lock.py",
    "server_check.py", "server_probe.py", "board_probe2.py",
    "verify_score.py", "seed_board.py", "shortcut_check.py",
    "shortcut_boot_test.py", "make_shortcut.py", "launch_panel.py",
    "infra_helper.py", "server.py", "split_map.py",
]


def main() -> int:
    LOG.parent.mkdir(parents=True, exist_ok=True)
    with LOG.open("a", encoding="utf-8") as f:
        # projects
        for name in META_PROJECTS:
            p = NEW / "projects" / name
            if p.exists():
                shutil.rmtree(p)
                f.write(f"removed project: {name}\n")
        # preflight test (legacy)
        t = NEW / "tests" / "test_preflight_check.py"
        if t.exists():
            t.unlink()
            f.write("removed test_preflight_check.py (legacy WDL/laecon)\n")
        # scripts
        for s in LEGACY_SCRIPTS:
            p = NEW / "scripts" / s
            if p.exists():
                p.unlink()
                f.write(f"removed script: {s}\n")
        # knowledge: strip governance entries (keep observability-guide + padroes)
        keep_knowledge = {
            "observability-guide.md", "padroes-entrega.md", "glossario-negocio.md",
            "stack-decisions.md", "discover-before-build.md",
        }
        kdir = NEW / "knowledge"
        if kdir.exists():
            for kf in kdir.glob("*.md"):
                if kf.name not in keep_knowledge:
                    kf.unlink()
                    f.write(f"removed knowledge: {kf.name}\n")
    print("STRIP_OK (see .laos/strip.log)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
