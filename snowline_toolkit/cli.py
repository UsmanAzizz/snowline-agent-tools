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
    new_files = [(f, target / f.relative_to(templates)) for f in templates.rglob("*") if f.is_file() and not f.name.endswith(".pyc")]
    print("[Update] .agents/skills")
    print(f"[{len(new_files)} files]")

def main():
    parser = argparse.ArgumentParser(prog="snowline")
    subparsers = parser.add_subparsers(dest="command", help="Commands")

    p_init = subparsers.add_parser("init", help="Initialize .agents/skills")
    p_init.add_argument("--apply", action="store_true", help="Apply changes")

    p_update = subparsers.add_parser("update", help="Update skills")
    p_uninstall = subparsers.add_parser("uninstall", help="Remove .agents/skills")
    p_path = subparsers.add_parser("path", help="Show paths")

    args = parser.parse_args()

    if args.command == "init":
        init(dry=not args.apply)
    elif args.command == "update":
        update()
    elif args.command == "uninstall":
        target = Path.cwd() / ".agents" / "skills"
        if target.exists():
            shutil.rmtree(target)
            print("[OK] Removed .agents/skills")
        else:
            print("[Skip] Not found")
    elif args.command == "path":
        show_path()
    else:
        print("[Snowline] Ready. Run 'snowline init --help'")

if __name__ == "__main__":
    main()
