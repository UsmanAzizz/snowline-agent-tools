"""
Snowline CLI - Agent Tools Installer
"""
import os
import shutil
import argparse
import sys
from datetime import datetime
from pathlib import Path
import sysconfig
import winreg

# Trigger PATH update on import
import snowline_toolkit

# Ensure Scripts folder is in PATH for this process (read from registry)
_scripts = sysconfig.get_path('scripts')
try:
    key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"Environment", 0, winreg.KEY_READ)
    user_path, _ = winreg.QueryValueEx(key, "Path")
    winreg.CloseKey(key)
    os.environ['PATH'] = user_path + os.pathsep + os.environ.get('PATH', '')
except Exception:
    pass


# ANSI colors for terminal
class Colors:
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    BOLD = '\033[1m'
    DIM = '\033[2m'
    RESET = '\033[0m'

    # ASCII fallback for Windows terminals without Unicode support
    CHECK = '+'
    INFO = 'i'
    WARN = '!'
    ERROR = 'x'


def safe_print(text, end="\n"):
    """Print with UTF-8 encoding, fallback to ASCII on Windows."""
    try:
        print(text, end=end)
    except UnicodeEncodeError:
        # Replace Unicode chars with ASCII fallbacks
        replacements = {
            '✓': '[+]', '✗': '[x]', 'ℹ': '[i]', '⚠': '[!]',
            '•': '-', '→': '->', '...': '...'
        }
        for old, new in replacements.items():
            text = text.replace(old, new)
        print(text)


def print_header(text):
    safe_print(f"\n{Colors.CYAN}{Colors.BOLD}{'=' * 50}{Colors.RESET}")
    safe_print(f"{Colors.CYAN}{Colors.BOLD}  {text}{Colors.RESET}")
    safe_print(f"{Colors.CYAN}{Colors.BOLD}{'=' * 50}{Colors.RESET}\n")


def print_success(text):
    safe_print(f"{Colors.GREEN}{Colors.CHECK} {text}{Colors.RESET}")


def print_info(text):
    safe_print(f"{Colors.CYAN}{Colors.INFO} {text}{Colors.RESET}")


def print_warning(text):
    safe_print(f"{Colors.YELLOW}{Colors.WARN} {text}{Colors.RESET}")


def print_error(text):
    safe_print(f"{Colors.RED}{Colors.ERROR} {text}{Colors.RESET}")


def print_section(text):
    safe_print(f"\n{Colors.BOLD}{text}{Colors.RESET}")


def print_list_item(text, indent=2):
    safe_print(f"{' ' * indent}{Colors.DIM}*{Colors.RESET} {text}")



def _clear_pip_cache():
    """Clear pip build cache."""
    import tempfile, shutil, glob
    patterns = [
        tempfile.gettempdir() + "/pip-req-build-*",
        tempfile.gettempdir() + "/pip-ephem-wheel-cache-*",
    ]
    for p in patterns:
        for d in glob.glob(p):
            try:
                shutil.rmtree(d, ignore_errors=True)
            except:
                pass


def init(dry=True):
    # Check if already installed - suggest update
    existing_count = 0
    skills_dir = Path.cwd() / ".agents" / "skills"
    if skills_dir.exists():
        existing_count = len([f for f in skills_dir.rglob("*") if f.is_file() and not f.name.endswith(".pyc")])
    
    if existing_count > 0 and not dry:
        print_info(f"Found {existing_count} existing skills")
        print()
        print_warning("Skills already installed!")
        print_info("To update, run: snowline update --apply")
        print_info("To reinstall, run: snowline uninstall --apply first")
        print()
        safe_print(f"{Colors.DIM}Use --apply to install anyway{Colors.RESET}")
        return

    templates = Path(__file__).parent / "templates"
    root = Path.cwd() / ".agents"
    target = root / "skills"

    print_header("Snowline Agent Tools - Installer")

    if not templates.exists():
        print_error("Templates folder not found!")
        print_info(f"Expected at: {templates}")
        return

    # Count files
    skill_files = [f for f in templates.rglob("*") if f.is_file() and not f.name.endswith(".pyc")]

    # Root files (PROJECT_CONTEXT.md is NOT created - it's the historical one from git)
    agents_template = templates / "AGENTS_TEMPLATE.md"
    root_files = {
        "agents.md": agents_template.read_text(encoding="utf-8") if agents_template.exists() else "# Agents Configuration\n",
        "memory.json": """{
  "version": "1.0",
  "context": {},
  "history": []
}
""",
        "PROJECT_NOTES.md": """# Project Notes

## Current Project
> Add project details here

## Goals
- [ ]

## Notes
> Additional notes
"""
    }

    print_info(f"Target directory: {root}")
    print_info(f"Installing: {len(skill_files)} skills, {len(root_files)} configuration files")

    if dry:
        print_section("Preview (Dry Run)")
        safe_print("The following files will be created:")
        safe_print("")

        safe_print(f"{Colors.BOLD}Configuration Files:{Colors.RESET}")
        for name in root_files:
            print_list_item(name)

        safe_print(f"\n{Colors.BOLD}Skills ({len(skill_files)}):{Colors.RESET}")
        skill_categories = {}
        for f in skill_files:
            rel = str(f.relative_to(templates))
            category = rel.split('/')[0] if '/' in rel else 'root'
            if category not in skill_categories:
                skill_categories[category] = []
            skill_categories[category].append(rel)

        for category in sorted(skill_categories.keys()):
            print_list_item(f"{Colors.DIM}{category}{Colors.RESET}")
            for f in skill_categories[category][:3]:
                if len(skill_categories[category]) > 3 and f == skill_categories[category][2]:
                    remaining = len(skill_categories[category]) - 3
                    safe_print(f"{' ' * 6}... and {remaining} more")
                    break
                print_list_item(f.split('/')[-1], indent=6)

        safe_print("")
        safe_print(f"{Colors.DIM}Run with --apply to install{Colors.RESET}")
        return

    # Install
    print_section("Installing...")

    # Create root directory
    root.mkdir(parents=True, exist_ok=True)

    # Create root files
    created_root = []
    skipped_root = []
    for name, content in root_files.items():
        dest = root / name
        if not dest.exists():
            dest.write_text(content, encoding="utf-8")
            created_root.append(name)
        else:
            skipped_root.append(name)

    for name in created_root:
        print_success(f"Created {name}")
    for name in skipped_root:
        print_info(f"Skipped {name} (already exists)")

    # Copy skill templates
    created_skills = []
    skipped_skills = []
    updated_skills = []
    
    # Files that should ALWAYS be updated
    ALWAYS_UPDATE = {'SKILL.md', 'companion.py', '__init__.py'}
    
    for f in skill_files:
        rel = f.relative_to(templates)
        dest = target / rel
        dest.parent.mkdir(parents=True, exist_ok=True)
        
        # Always copy SKILL.md, always copy new files
        if not dest.exists() or f.name in ALWAYS_UPDATE:
            shutil.copy2(f, dest)
            if not dest.exists():
                created_skills.append(str(rel))
            else:
                updated_skills.append(str(rel))
        else:
            skipped_skills.append(str(rel))

    # Progress bar for skills
    total = len(created_skills) + len(skipped_skills)
    for i, skill in enumerate(created_skills, 1):
        safe_print(f"  {Colors.GREEN}{Colors.CHECK}{Colors.RESET} {skill}", end="\r")

    print()
    print_section("Installation Complete!")

    safe_print(f"{Colors.BOLD}Summary:{Colors.RESET}")
    print_success(f"Created {len(created_root)} config files")
    print_success(f"Installed {len(created_skills)} skills, updated {len(updated_skills)}")
    if skipped_root:
        print_info(f"Skipped {len(skipped_root)} existing config files")
    if skipped_skills:
        print_info(f"Skipped {len(skipped_skills)} existing skills")

    print()
    safe_print(f"{Colors.BOLD}Next Steps:{Colors.RESET}")
    print_list_item("Review .agents/agents.md for agent rules")
    print_list_item("Update .agents/PROJECT_NOTES.md with your project info")
    print_list_item("Run 'snowline update' to sync new skills later")

    safe_print(f"\n{Colors.DIM}Location: {root}{Colors.RESET}\n")


def update(apply=False):
    _clear_pip_cache()
    root = Path.cwd() / ".agents"
    target = root / "skills"

    print_header("Snowline Update")

    if not target.exists():
        print_error("No skills found!")
        print_info("Run 'snowline init --apply' first")
        return

    templates = Path(__file__).parent / "templates"
    
    # Protected files
    PROTECTED = {
        "memory.json",
        "PROJECT_CONTEXT.md",
        "PROJECT_NOTES.md",
        "CURRENT_STATE.md",
        "scope_lock.json",
        "agents.md",
    }

    skill_files = [f for f in templates.rglob("*") if f.is_file() and not f.name.endswith(".pyc")]

    new_files = []
    modified_files = []
    
    for f in skill_files:
        rel = str(f.relative_to(templates))
        if rel in PROTECTED:
            continue
        dest = target / rel
        if not dest.exists():
            new_files.append((f, rel))
        elif f.stat().st_mtime > dest.stat().st_mtime:
            modified_files.append((f, rel))

    total_current = len([f for f in target.rglob("*") if f.is_file()])
    
    print_info(f"Current skills: {total_current}")
    
    if not new_files and not modified_files:
        print_success("All skills are up to date!")
        return

    print_info(f"Available: {len(new_files)} new, {len(modified_files)} modified")

    if not apply:
        print_section("Changes to be applied:")
        
        for _, rel in new_files[:10]:
            print_list_item(f"[NEW] {rel}")
        if len(new_files) > 10:
            print_info(f"... and {len(new_files) - 10} more new files")
        
        for _, rel in modified_files[:10]:
            print_list_item(f"[UPDATE] {rel}")
        if len(modified_files) > 10:
            print_info(f"... and {len(modified_files) - 10} more modified files")
        
        print()
        safe_print(f"Run {Colors.BOLD}snowline update --apply{Colors.RESET} to apply changes")
        return

    print_section("Applying updates...")
    
    created = 0
    updated = 0
    
    for src, rel in new_files:
        dest = target / rel
        dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src, dest)
        safe_print(f"  {Colors.GREEN}+{Colors.RESET} {rel}")
        created += 1

    for src, rel in modified_files:
        dest = target / rel
        shutil.copy2(src, dest)
        safe_print(f"  {Colors.YELLOW}~{Colors.RESET} {rel}")
        updated += 1

    print()
    print_success(f"Updated: {created} new, {updated} modified")


def uninstall(apply=False):
    _clear_pip_cache()
    root = Path.cwd() / ".agents"
    skills_dir = root / "skills"

    print_header("Snowline Uninstall")

    if not skills_dir.exists():
        print_info("No skills found to remove")
        return

    skill_files = [f for f in skills_dir.rglob("*") if f.is_file() and not f.name.endswith(".pyc")]
    skill_count = len(skill_files)

    if not apply:
        print_warning(f"Will remove {skill_count} skill files from {skills_dir}")
        print_info("Configuration files will be kept")
        print()
        safe_print(f"Run {Colors.BOLD}snowline uninstall --apply{Colors.RESET} to confirm")
        return

    removed = 0
    for f in skill_files:
        try:
            f.unlink()
            removed += 1
        except Exception as e:
            safe_print(f"  {Colors.RED}x{Colors.RESET} {f.relative_to(skills_dir)}: {e}")

    for d in sorted(skills_dir.rglob("*"), reverse=True):
        if d.is_dir() and not list(d.iterdir()):
            d.rmdir()

    print()
    print_success(f"Removed {removed} skill files")


def show_path():
    scripts = sysconfig.get_path('scripts')
    python_exe = sys.executable

    print_header("Snowline - Path Information")
    safe_print(f"{Colors.BOLD}Python:{Colors.RESET} {python_exe}")
    safe_print(f"{Colors.BOLD}Scripts:{Colors.RESET} {scripts}")
    safe_print("")
    safe_print(f"{Colors.BOLD}To use 'snowline' command directly:{Colors.RESET}")
    safe_print(f"  Add to PATH: {scripts}")
    safe_print("")
    safe_print(f"{Colors.DIM}Alternative: Use 'python -m snowline_toolkit.cli'{Colors.RESET}\n")


def main():
    parser = argparse.ArgumentParser(
        prog="snowline",
        description="Snowline Agent Tools - Portable tools for AI coding assistants"
    )
    subparsers = parser.add_subparsers(dest="command", help="Commands")

    p_init = subparsers.add_parser("init", help="Initialize .agents folder with skills")
    p_init.add_argument("--apply", action="store_true", help="Apply installation")

    p_update = subparsers.add_parser("update", help="Check for skill updates")
    p_update.add_argument("--apply", action="store_true", help="Apply updates")
    p_uninstall = subparsers.add_parser("uninstall", help="Remove installed skills")
    p_uninstall.add_argument("--apply", action="store_true", help="Apply uninstall")
    subparsers.add_parser("path", help="Show installation paths")

    args = parser.parse_args()

    if args.command == "init":
        init(dry=not args.apply)
    elif args.command == "update":
        update(apply=args.apply)
    elif args.command == "uninstall":
        uninstall(apply=args.apply)
    elif args.command == "path":
        show_path()
    else:
        print_header("Snowline Agent Tools")
        safe_print(f"{Colors.BOLD}Version:{Colors.RESET} 1.0.5")
        safe_print("")
        safe_print(f"{Colors.BOLD}Commands:{Colors.RESET}")
        print_list_item("init --apply  - Install skills to .agents folder")
        print_list_item("update        - Check for new/modified skills")
        print_list_item("path          - Show installation paths")
        print_list_item("uninstall     - Remove installed skills")
        safe_print("")
        safe_print(f"{Colors.DIM}Run 'snowline <command> --help' for more info{Colors.RESET}\n")


if __name__ == "__main__":
    main()
