import os
import shutil
import argparse
import filecmp
import sys
from datetime import datetime
from pathlib import Path
import sysconfig

def show_path():
    """Show where snowline is installed and how to add to PATH."""
    scripts_path = sysconfig.get_path('scripts')
    python_path = sys.executable
    print("[INFO] Python:", python_path)
    print("[INFO] Scripts:", scripts_path)
    print()
    print("[ADD TO PATH]")
    print("  setx PATH \"%PATH%;" + scripts_path + "\" /M")
    print()
    print("[OR ADD ALIAS]")
    print("  Set-Alias -Name snowline -Value \"" + python_path + " -m snowline_toolkit.cli\"")
    print("  Or: py -m snowline_toolkit.cli")
    print()
    print("[PATH ISSUE? Run as admin or use:]")
    print("  py -m snowline_toolkit.cli")
    print("  Or add to PATH manually:")
    cmd = "[Environment]::SetEnvironmentVariable(\"Path\", (Get-Content Env:PATH) + \";scripts" + scripts_path + "\", \"User\")"
    print("  " + cmd)

def create_alias(scope="user"):
    """Create persistent PowerShell alias."""
    python_exe = sys.executable
    cmd = python_exe + " -m snowline_toolkit.cli"

    profile_path = os.path.expanduser("~/Documents/WindowsPowerShell/Microsoft.PowerShell_profile.ps1")
    os.makedirs(os.path.dirname(profile_path), exist_ok=True)

    alias_line = "\nfunction snowline { " + cmd + " $args }\n"

    # Check if already exists
    if os.path.exists(profile_path):
        with open(profile_path, 'r', encoding='utf-8') as f:
            content = f.read()
        if 'function snowline' in content or 'alias snowline' in content:
            print("[INFO] Alias already exists in", profile_path)
            return

    with open(profile_path, 'a', encoding='utf-8') as f:
        f.write("\n# Snowline Agent Tools\n" + alias_line)

    print("[SUCCESS] Alias created in", profile_path)
    print("[NOTE] Reload profile: . $" + profile_path)
    print("[OR] Restart terminal")

def is_symlink_or_junction(path):
    if not os.path.exists(path):
        return False
    if os.path.islink(path):
        return True
    if hasattr(os.path, 'isjunction') and os.path.isjunction(path):
        return True
    import stat
    try:
        attrs = os.stat(path, follow_symlinks=False).st_file_attributes
        return bool(attrs & stat.FILE_ATTRIBUTE_REPARSE_POINT)
    except AttributeError:
        pass
    return False

def check_and_update_path(dry_run=False):
    if os.name != 'nt':
        return

    scripts_path = sysconfig.get_path('scripts')
    try:
        import winreg
        key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, "Environment", 0, winreg.KEY_READ | winreg.KEY_WRITE)
        current_path, _ = winreg.QueryValueEx(key, "Path")
        normalized_target = os.path.normpath(scripts_path).lower()
        normalized_paths = [os.path.normpath(p.strip()).lower() for p in current_path.split(';') if p.strip()]

        if normalized_target not in normalized_paths:
            if dry_run:
                print("[DRY-RUN] Would add to PATH:", scripts_path)
            else:
                print("[INFO]", scripts_path, "not in User PATH")
        winreg.CloseKey(key)
    except Exception:
        pass

def check_and_scaffold_agents_md(dry_run=False):
    cwd = Path(os.getcwd())
    agents_md = cwd / ".agents" / "AGENTS.md"
    template = Path(__file__).parent / "templates" / "AGENTS_TEMPLATE.md"

    if not template.exists():
        return

    if not agents_md.exists() or agents_md.stat().st_size < 100:
        if dry_run:
            print("[DRY-RUN] Would scaffold", agents_md)
        else:
            agents_md.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(template, agents_md)
            print("[INFO] Scaffolded", agents_md.relative_to(cwd))

def init_snowline(dry_run=False):
    current_dir = Path(__file__).parent
    templates_dir = current_dir / "templates"

    if not templates_dir.exists():
        print("[FAIL] Templates not found at", templates_dir)
        return

    target_dir = Path(os.getcwd()) / ".agents" / "skills"

    print("[Snowline Agent Tools - Initialization]")
    if dry_run:
        print("[DRY-RUN mode. No changes.")
        print("Run with --apply to apply.\n")
    else:
        print("[INFO] Initializing .agents/skills...\n")

    if not dry_run:
        target_dir.mkdir(parents=True, exist_ok=True)

    file_count = 0
    dir_count = 0

    for root, dirs, files in os.walk(templates_dir):
        rel_path = Path(root).relative_to(templates_dir)
        target_root = target_dir / rel_path

        for d in dirs:
            if d == "__pycache__":
                continue
            target_d = target_root / d
            if not dry_run:
                target_d.mkdir(parents=True, exist_ok=True)
            dir_count += 1

        for f in files:
            if f.endswith(".pyc") or f == ".DS_Store":
                continue
            src_file = Path(root) / f
            dest_file = target_root / f
            if not dry_run:
                shutil.copy2(src_file, dest_file)
            file_count += 1

    if dry_run:
        print("\n[DRY-RUN] Would create", dir_count, "dirs,", file_count, "files")
    else:
        print("\n[OK]", file_count, "files,", dir_count, "dirs")

    check_and_scaffold_agents_md(dry_run)

def update_snowline(dry_run=False):
    target_dir = Path(os.getcwd()) / ".agents" / "skills"
    if not target_dir.exists():
        print("[FAIL] .agents/skills not found. Run 'init' first.")
        return

    if is_symlink_or_junction(str(target_dir)):
        print("[INFO] Using symlink. Run 'git pull' in source folder.")
        return

    current_dir = Path(__file__).parent
    templates_dir = current_dir / "templates"

    if dry_run:
        print("[DRY-RUN mode. No changes.\n")

    diff_files = []
    new_files = []

    for root, dirs, files in os.walk(templates_dir):
        rel_path = Path(root).relative_to(templates_dir)
        target_root = target_dir / rel_path

        for f in files:
            if f.endswith(".pyc") or f == ".DS_Store":
                continue
            src_file = Path(root) / f
            dest_file = target_root / f

            if not dest_file.exists():
                new_files.append((src_file, dest_file))
            elif not filecmp.cmp(src_file, dest_file, shallow=False):
                diff_files.append((src_file, dest_file))

    if not diff_files and not new_files:
        print("[OK] All up to date.")
        return

    if dry_run:
        print("[DRY-RUN] Found", len(new_files), "new,", len(diff_files), "modified")
        return

    backup_dir = Path(os.getcwd()) / ".backup_replace" / datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_dir.mkdir(parents=True, exist_ok=True)

    print("[INFO] Backup in", backup_dir)

    for _, dest in diff_files:
        rel_path = dest.relative_to(os.getcwd())
        backup_path = backup_dir / rel_path
        backup_path.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(dest, backup_path)

    for src, dest in new_files + diff_files:
        dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src, dest)

    print("[OK] Updated")

def uninstall_snowline(dry_run=False):
    target_dir = Path(os.getcwd()) / ".agents" / "skills"

    if dry_run:
        print("[DRY-RUN mode. No changes.\n")

    to_delete = []
    if target_dir.exists():
        to_delete.append(target_dir)

    if not to_delete:
        print("[OK] Nothing to uninstall.")
        return

    print("[Will delete]", len(to_delete), "items")

    if dry_run:
        return

    import shutil as sh
    for d in to_delete:
        if is_symlink_or_junction(str(d)):
            try:
                import _winapi
                _winapi.RemoveDirectory(str(d))
            except:
                os.rmdir(d)
        else:
            sh.rmtree(d)
        print("[OK] Deleted", d.relative_to(os.getcwd()))

def main():
    parser = argparse.ArgumentParser(description="Snowline Agent Tools")
    subparsers = parser.add_subparsers(dest='command')

    init_parser = subparsers.add_parser('init')
    init_parser.add_argument('--apply', action='store_true')

    update_parser = subparsers.add_parser('update')
    update_parser.add_argument('--apply', action='store_true')

    uninstall_parser = subparsers.add_parser('uninstall')
    uninstall_parser.add_argument('--apply', action='store_true')

    alias_parser = subparsers.add_parser('alias')

    path_parser = subparsers.add_parser('path')

    args = parser.parse_args()

    if args.command is None or args.command == 'init':
        dry_run = not getattr(args, 'apply', False)
        init_snowline(dry_run)
    elif args.command == 'update':
        dry_run = not getattr(args, 'apply', False)
        update_snowline(dry_run)
    elif args.command == 'uninstall':
        dry_run = not getattr(args, 'apply', False)
        uninstall_snowline(dry_run)
    elif args.command == 'alias':
        create_alias()
    elif args.command == 'path':
        show_path()

if __name__ == '__main__':
    main()
