import os
import shutil
import argparse
import filecmp
import sys
from datetime import datetime
from pathlib import Path
import sysconfig

# Progress bar
def progress(current, total, bar=30):
    pct = int(current / total * bar)
    return f"[{'#' * pct}{'-' * (bar - pct)}] {current}/{total}"

def show_path():
    scripts = sysconfig.get_path('scripts')
    python_exe = sys.executable
    print()
    print("  Python:", python_exe)
    print("  Scripts:", scripts)
    print()
    print("  Add to PATH:")
    print("    setx PATH \"%PATH%;" + scripts + "\" /M")
    print()
    print("  Or use directly:")
    print("    py -m snowline_toolkit")
    print("    python -m snowline_toolkit")
    print()

def init(dry=True):
    templates = Path(__file__).parent / "templates"
    target = Path.cwd() / ".agents" / "skills"

    print("[Init] .agents/skills")

    if not templates.exists():
        print("[Error] Templates not found")
        return

    if dry:
        print("[Dry run] Run with --apply to execute")

    files = list(templates.rglob("*"))
    files = [f for f in files if f.is_file() and not f.name.endswith(".pyc")]
    total = len(files)

    print(f"[{total} files]")

    if dry:
        return

    target.mkdir(parents=True, exist_ok=True)
    copied = 0
    for f in files:
        rel = f.relative_to(templates)
        dest = target / rel
        dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(f, dest)
        copied += 1
        print(f"  {progress(copied, total, 20)] {rel}", end="\r")

    print()
    print("[OK] Done. {copied} files")

def update():
    target = Path.cwd() / ".agents" / "skills"
    if not target.exists():
        print("[Error] Run 'init' first")
        return

    templates = Path(__file__).parent / "templates"
    print("[Update] .agents/skills")

    # Find new/modified
    new_files = []
    mod_files = []
    for f in templates.rglob("*"):
        if not f.is_file() or f.name.endswith(".pyc"):
            continue
        rel = f.relative_to(templates)
        dest = target / rel
        if not dest.exists():
            new_files.append((f, dest))
        elif not filecmp.cmp(f, dest):
            mod_files.append((f, dest))

    total = len(new_files) + len(mod_files)
    if total == 0:
        print("[OK] Up to date")
        return

    print(f"[{len(new_files)} new, {len(mod_files)} modified]")

    # Backup
    backup = Path.cwd() / f".backup/{datetime.now().strftime('%H%M%S')}"
    backup.mkdir(parents=True, exist_ok=True)
    print(f"[Backup] {backup.name}")

    for _, dest in mod_files:
        rel = dest.relative_to()
        bak = backup / rel
        bak.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(dest, bak)

    # Copy new/modified
    for src, dest in new_files + mod_files:
        dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src, dest)

    print(f"[OK] Done. {total} files updated")

def uninstall():
    target = Path.cwd() / ".agents" / "skills"
    print("[Uninstall] .agents/skills")
    if not target.exists():
        print("[OK] Nothing to do")
        return
    shutil.rmtree(target)
    print("[OK] Removed .agents/skills")

def main():
    parser = argparse.ArgumentParser(description="Snowline Tools")
    sub = parser.add_subparsers(dest="cmd")
    sub.add_parser("init", help="Initialize .agents/skills")
    sub.add_parser("update", help="Update .agents/skills")
    sub.add_parser("uninstall", help="Remove .agents/skills")
    sub.add_parser("path", help="Show paths")

    args = parser.parse_args()

    if args.cmd == "init":
        init(dry=False)
    elif args.cmd == "update":
        update()
    elif args.cmd == "uninstall":
        uninstall()
    elif args.cmd == "path":
        show_path()
    else:
        init(dry=False)  # Default action

if __name__ == "__main__":
    main()
