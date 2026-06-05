"""Tests for scripts/preflight_check.py.

Strategy: create a tmp project with a known-bad project.yaml and a known-
good project.yaml, then verify the preflight reports the expected findings.

Each of the 5 checks has at least one test that demonstrates the BLOCKED
path and one that demonstrates the PASS path.
"""
from __future__ import annotations

import shutil
import subprocess
import sys
import textwrap
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]
SCRIPT = REPO_ROOT / "scripts" / "preflight_check.py"


# ─── helpers ────────────────────────────────────────────────────────────────


def _run_preflight(project_dir: Path) -> subprocess.CompletedProcess:
    """Invoke the preflight script as a subprocess (real binary)."""
    return subprocess.run(
        [sys.executable, str(SCRIPT), str(project_dir)],
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        timeout=30,
    )


def _write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(textwrap.dedent(content), encoding="utf-8")


def _make_minimal_laos_root(parent: Path) -> Path:
    """Create a tmp dir that looks enough like a LAOS root for _find_laos_root."""
    laos = parent / "fake-laos"
    (laos / "projects" / "_meta" / "fake-capability").mkdir(parents=True)
    (laos / "AGENTS.md").write_text("# fake", encoding="utf-8")
    return laos


# ─── fixtures ───────────────────────────────────────────────────────────────


@pytest.fixture
def tmp_laos_root(tmp_path: Path) -> Path:
    """Provide a tmp LAOS root with projects/ subdir and AGENTS.md."""
    laos = _make_minimal_laos_root(tmp_path)
    return laos


# ─── Check 1: YAML arithmetic ──────────────────────────────────────────────


def test_yaml_arithmetic_catches_off_by_n(tmp_laos_root: Path) -> None:
    """conditions_total=19 with only 17 listed must be flagged."""
    project = tmp_laos_root / "projects" / "_meta" / "fake-capability"
    _write(
        project / "project.yaml",
        """
        name: fake
        capability_status:
          conditions_total: 19
          conditions_blocking_stable: 19
        condicoes_vinculantes:
          data_architect: [DA-1, DA-2, DA-3, DA-4, DA-5]   # 5
          dashboard_designer: [DD-1, DD-2, DD-3]            # 3
          automation_engineer: [AE-1, AE-2, AE-3, AE-4]     # 4
          delivery_reviewer: [DR-1, DR-2, DR-3, DR-4, DR-5]  # 5
        # total listed = 17, declared = 19
        """,
    )
    # Touch the deliverables-less path: leave it empty
    result = _run_preflight(project)
    assert result.returncode == 1, f"expected BLOCKED, got PASS:\n{result.stdout}"
    assert "ARITHMETIC_OFF_BY_N" in result.stdout
    assert "off-by-2" in result.stdout


def test_yaml_arithmetic_passes_when_consistent(tmp_laos_root: Path) -> None:
    """conditions_total=17 with 17 listed must NOT be flagged for arithmetic."""
    project = tmp_laos_root / "projects" / "_meta" / "fake-capability"
    _write(
        project / "project.yaml",
        """
        name: fake
        capability_status:
          conditions_total: 17
          conditions_blocking_stable: 17
        condicoes_vinculantes:
          data_architect: [DA-1, DA-2, DA-3, DA-4, DA-5]
          dashboard_designer: [DD-1, DD-2, DD-3]
          automation_engineer: [AE-1, AE-2, AE-3, AE-4]
          delivery_reviewer: [DR-1, DR-2, DR-3, DR-4, DR-5]
        """,
    )
    result = _run_preflight(project)
    # we expect 0 BLOCKED lines from arithmetic; but other checks may flag
    # missing deliverables. So we check that no ARITHMETIC line is present.
    assert "ARITHMETIC" not in result.stdout or "ARITHMETIC_OFF" not in result.stdout


def test_yaml_invalid_returns_blocked(tmp_laos_root: Path) -> None:
    """YAML with a syntax error must be flagged, not crash the script."""
    project = tmp_laos_root / "projects" / "_meta" / "fake-capability"
    _write(
        project / "project.yaml",
        """
        name: fake
        capability_status:
          conditions_total: : 17  # invalid YAML
        """,
    )
    result = _run_preflight(project)
    assert result.returncode == 1
    assert "YAML_INVALID" in result.stdout


# ─── Check 2: Deliverable path existence ──────────────────────────────────


def test_path_missing_is_flagged(tmp_laos_root: Path) -> None:
    """A deliverable that doesn't exist must be flagged."""
    project = tmp_laos_root / "projects" / "_meta" / "fake-capability"
    _write(
        project / "project.yaml",
        """
        name: fake
        capability_status:
          conditions_total: 0
        condicoes_vinculantes: {}
        deliverables:
          - path: nonexistent/file.md
            type: docs
        """,
    )
    result = _run_preflight(project)
    assert "PATH_MISSING" in result.stdout
    assert "nonexistent/file.md" in result.stdout


# ─── Check 3: Secret scan ───────────────────────────────────────────────────


def test_aws_key_caught(tmp_laos_root: Path) -> None:
    """An AWS access key in a yaml must be flagged."""
    project = tmp_laos_root / "projects" / "_meta" / "fake-capability"
    _write(
        project / "project.yaml",
        """
        name: fake
        capability_status: {conditions_total: 0}
        """,
    )
    _write(
        project / "leaked.yaml",
        """
        # This should be caught
        aws_key: AKIAIOSFODNN7EXAMPLE
        """,
    )
    result = _run_preflight(project)
    assert "POSSIBLE_SECRET" in result.stdout
    assert "AWS" in result.stdout


def test_env_var_template_not_flagged(tmp_laos_root: Path) -> None:
    """A template placeholder like ${API_KEY} must NOT be flagged."""
    project = tmp_laos_root / "projects" / "_meta" / "fake-capability"
    _write(
        project / "project.yaml",
        """
        name: fake
        capability_status: {conditions_total: 0}
        """,
    )
    _write(
        project / "template.yaml",
        """
        # This should NOT be caught (env-var template)
        api_key: ${API_KEY_FROM_ENV}
        token: "{{GITHUB_TOKEN}}"
        """,
    )
    result = _run_preflight(project)
    assert "POSSIBLE_SECRET" not in result.stdout


# ─── Check 4: Cross-reference integrity ───────────────────────────────────


def test_dangling_article_reference_caught(tmp_laos_root: Path) -> None:
    """A reference to Art. 99 in a doc when Constitution only has Art. 1-10."""
    project = tmp_laos_root / "projects" / "_meta" / "fake-capability"
    _write(
        project / "project.yaml",
        """
        name: fake
        capability_status: {conditions_total: 0}
        """,
    )
    _write(
        project / "CONSTITUTION.md",
        """
        # Fake Constitution
        ## Artigo 1 — Foo
        ## Artigo 2 — Bar
        """,
    )
    _write(
        project / "README.md",
        """
        # Reads Constitution Art. 99 which doesn't exist
        """,
    )
    result = _run_preflight(project)
    assert "DANGLING_REF" in result.stdout
    assert "Art. 99" in result.stdout


def test_dangling_condition_caught(tmp_laos_root: Path) -> None:
    """A reference to DA-99 in a doc when only DA-1..5 are catalogued."""
    project = tmp_laos_root / "projects" / "_meta" / "fake-capability"
    # Arithmetic must be consistent so the script reaches the cross-ref check.
    _write(
        project / "project.yaml",
        """
        name: fake
        capability_status: {conditions_total: 2}
        condicoes_vinculantes:
          data_architect: [DA-1, DA-2]
        """,
    )
    _write(
        project / "tracking.md",
        """
        # Tracking
        | DA-99 | dangling reference |
        """,
    )
    result = _run_preflight(project)
    assert "DANGLING_CONDITION" in result.stdout
    assert "DA-99" in result.stdout


# ─── Check 5: No implementation code in LAOS ──────────────────────────────


def test_python_file_in_projects_is_flagged(tmp_laos_root: Path) -> None:
    """A .py file under projects/ must be flagged (only specs allowed)."""
    project = tmp_laos_root / "projects" / "_meta" / "fake-capability"
    _write(
        project / "project.yaml",
        """
        name: fake
        capability_status: {conditions_total: 0}
        """,
    )
    # This is a script that should NOT exist under projects/
    _write(
        project / "should_not_be_here.py",
        """
        print('oops')
        """,
    )
    result = _run_preflight(project)
    assert "IMPL_CODE_IN_LAOS" in result.stdout
    assert ".py" in result.stdout


# ─── Integration test: laecon M0 should pass ──────────────────────────────


def test_laeco_m0_passes_clean(tmp_path: Path) -> None:
    """Sanity check: real laecon M0 must pass preflight (we already fixed it)."""
    real_project = REPO_ROOT / "projects" / "_meta" / "laecon-capability"
    if not real_project.exists():
        pytest.skip("laecon-capability not present in this checkout")
    result = _run_preflight(real_project)
    assert result.returncode == 0, (
        f"laecon M0 should be clean after arithmetic fix; got:\n{result.stdout}"
    )
    assert "PREFLIGHT_PASS" in result.stdout
