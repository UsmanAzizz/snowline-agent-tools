import os
import shutil
import argparse
import filecmp
import sys
from datetime import datetime
from pathlib import Path
import sysconfig

def show_path():
    scripts = sysconfig.get_path('scripts')
    python_exe = sys.executable
    print()
    print("  Scripts:", scripts)
    print("  Run 'snowline path' for full info")

def init(dry=True):
    templates = Path(__file__).parent / "templates"
    target = Path.cwd() / ".agents" / "skills"

    if not templates.exists():
        print("[Error] Templates not found")
        return

    files = [f for f in templates.rglob("*") if f.is_file() and not f.name.endswith(".pyc")]
    print("[Init] .agents/skills")
    print(f"[{len(files)} files")

    if dry:
        print("[Dry] Run with --apply")
        return

    copied = 0
    for f in files:
        rel = f.relative_to(templates)
        dest = target / rel
        dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(f, dest)
        copied += 1
        print(f"  {copied}/{len(files)} {rel}", end="\r")

    print()
    print(f"[OK] {copied} files")

def update():
    target = Path.cwd() / ".agents" / "skills"
    if not target.exists():
        print("[Error] Run 'init' first")
        return

    templates = Path(__file__).parent / "templates"
    new_files = [(f, target / f.relative_to(templates)] for f in templates.rglob("*") if f.is_file() and not f.name.endswith(".pyc")]
    print("[Update] .agents/skills")
    print(f"[{len(new_files)} files")

def main():
    print("[Snowline] Ready")
