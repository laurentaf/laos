"""Debug: check _resolve_child_repo resolution."""
import sys, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).parents[2]))  # add Laos root
from scripts.subagent_boot_check import _resolve_child_repo

root = pathlib.Path("F:/projects/Laos")
project_name = "eixo-do-mal"
result = _resolve_child_repo(root, project_name)
print(f"Root: {root}")
print(f"Project: {project_name}")
print(f"Candidates ({len(result)}):")
for c in result:
    print(f"  {c} (exists={c.exists()}, is_dir={c.is_dir()})")
    if c.exists():
        for item in c.iterdir():
            print(f"    - {item.name} {'DIR' if item.is_dir() else 'FILE'}")
