"""
Snowline CLI - Clean init
"""
import shutil
import sys

def init():
    from pathlib import Path
    templates = Path(__file__).parent / "templates"
    target = Path.cwd() / ".agents" / "skills"

    files = [f for f in templates.rglob("*") if f.is_file() and not f.name.endswith(".pyc")]
    print(f"[{len(files)} files")

    for f in files:
        dest = target / f.relative_to(templates)
        dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(f, dest)

    print("[OK]" if files else "[Skip]")
