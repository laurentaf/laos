"""P4: verifier framework — catches broken artifacts, green when complete."""

from __future__ import annotations

import json
from pathlib import Path

from laos.verify import engine


def _write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def _project_yaml(tmp_path: Path) -> dict:
    return {
        "project_name": "vproj",
        "deliverables": [
            {
                "name": "good-sql",
                "label": "Modelo dimensional",
                "stage": 1,
                "artifacts": ["artifacts/data/schema-gold.sql"],
            },
            {
                "name": "broken-json",
                "label": "Config de pipeline",
                "stage": 2,
                "artifacts": ["artifacts/automation/config.json"],
            },
        ],
    }


def _make_project(tmp_path: Path) -> Path:
    """Create LAOS-style layout: <root>/projects/vproj/project.yaml."""
    import yaml

    proj = tmp_path / "projects" / "vproj"
    proj.mkdir(parents=True, exist_ok=True)
    (proj / "project.yaml").write_text(
        yaml.safe_dump(_project_yaml(tmp_path)), encoding="utf-8",
    )
    return proj


def test_verifier_passes_complete_project(tmp_path):
    proj = _make_project(tmp_path)
    _write(proj / "artifacts/data/schema-gold.sql",
           "CREATE TABLE gold.sales AS SELECT * FROM silver.sales;")
    _write(proj / "artifacts/automation/config.json",
           json.dumps({"nodes": ["a", "b"], "schedule": "daily"}))

    results, all_ok = engine.verify_project(tmp_path, "vproj")
    assert all_ok is True
    by_name = {r.deliverable: r for r in results}
    assert by_name["good-sql"].ok
    assert by_name["broken-json"].ok


def test_verifier_catches_broken_artifact(tmp_path):
    """NEGATIVE test: broken JSON must FAIL — proves the check has teeth."""
    proj = _make_project(tmp_path)
    _write(proj / "artifacts/data/schema-gold.sql",
           "CREATE TABLE gold.sales AS SELECT * FROM silver.sales;")
    # broken JSON on purpose
    _write(proj / "artifacts/automation/config.json",
           '{"nodes": [unclosed]')

    results, all_ok = engine.verify_project(tmp_path, "vproj")
    assert all_ok is False
    by_name = {r.deliverable: r for r in results}
    assert by_name["good-sql"].ok
    broken = by_name["broken-json"]
    assert broken.exists is True        # file present
    assert broken.imports is False      # but does not parse -> CAUGHT
    assert broken.ok is False


def test_verifier_catches_missing_artifact(tmp_path):
    """Deliverable declares artifact that doesn't exist -> FAIL."""
    proj = _make_project(tmp_path)
    # only one artifact present; the other is missing
    _write(proj / "artifacts/data/schema-gold.sql",
           "CREATE TABLE gold.sales AS SELECT * FROM silver.sales;")

    results, all_ok = engine.verify_project(tmp_path, "vproj")
    assert all_ok is False
    by_name = {r.deliverable: r for r in results}
    assert by_name["broken-json"].exists is False
    assert by_name["broken-json"].ok is False


def test_verifier_ready_to_ship_flag(tmp_path):
    import duckdb

    from laos.db import schema as schema_mod

    proj = _make_project(tmp_path)
    _write(proj / "artifacts/data/schema-gold.sql",
           "CREATE TABLE gold.sales AS SELECT * FROM silver.sales;")
    _write(proj / "artifacts/automation/config.json",
           json.dumps({"nodes": ["a", "b"]}))

    con = duckdb.connect(":memory:")
    schema_mod.apply_schema(con)
    # patch engine's schema.connect to use our in-memory con
    import laos.verify.engine as eng

    original = eng.schema.connect
    eng.schema.connect = lambda: con
    try:
        results, all_ok = engine.verify_project(tmp_path, "vproj")
        assert all_ok
        row = con.execute(
            "SELECT ready_to_ship FROM projects WHERE project_id='vproj'"
        ).fetchone()
        assert row[0] is True
    finally:
        eng.schema.connect = original
