"""
Snowline CLI - Agent Tools Installer
"""
import os
import shutil
import argparse
import sys
import filecmp
import tempfile, subprocess, json
import hashlib
from datetime import datetime
from pathlib import Path
import sysconfig
if sys.platform == 'win32':
    import winreg

# ============================================================
# Hash Functions for agents.md baseline tracking
# ============================================================

def save_agents_md_hash(file_path: Path):
    """Save SHA256 hash of agents.md to baseline file."""
    baseline_file = file_path.parent / ".agents_md_baseline_hash"
    if file_path.exists():
        hash_val = hashlib.sha256(file_path.read_bytes()).hexdigest()[:16]
        baseline_file.write_text(hash_val)

def load_agents_md_baseline(file_path: Path) -> str:
    """Load saved baseline hash, return empty string if not exists."""
    baseline_file = file_path.parent / ".agents_md_baseline_hash"
    if baseline_file.exists():
        return baseline_file.read_text().strip()
    return ""

def current_agents_md_hash(file_path: Path) -> str:
    """Calculate current SHA256 hash (first 16 chars)."""
    if file_path.exists():
        return hashlib.sha256(file_path.read_bytes()).hexdigest()[:16]
    return ""

# Trigger PATH update on import

# Trigger PATH update on import
import snowline

# Ensure Scripts folder is in PATH for this process (read from registry)
_scripts = sysconfig.get_path('scripts')
if sys.platform == 'win32':
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
    import glob
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


def init(dry=True, force=False):
    # Check if already installed
    existing_count = 0
    skills_dir = Path.cwd() / ".agents" / "skills"
    if skills_dir.exists():
        existing_count = len([f for f in skills_dir.rglob("*") if f.is_file() and not f.name.endswith(".pyc")])

    if existing_count > 0 and not force:
        print_info(f"Found {existing_count} existing skills")
        print()
        print_warning("Skills sudah terpasang. Tidak ada yang diubah.")
        print_info("Untuk memasang ulang: snowline reinstall --apply")
        return

    templates = Path(__file__).parent / "templates"
    root = Path.cwd() / ".agents"
    target = root

    print_header("Snowline Agent Tools - Installer")

    if not templates.exists():
        print_error("Templates folder not found!")
        print_info(f"Expected at: {templates}")
        return

    # Count files
    skill_files = [
        f for f in templates.rglob("*")
        if f.is_file()
        and not f.name.endswith(".pyc")
        and f.name != "AGENTS_TEMPLATE.md"  # Handled separately via agents_template variable
    ]

    # Root files (PROJECT_CONTEXT.md is NOT created - it's the historical one from git)
    agents_template = templates / "AGENTS_TEMPLATE.md"
    root_files = {
        ".gitignore": """write_log.jsonl
scope_lock.json
session_cache.json
mode_ringan.json
*.pyc
__pycache__/
""",
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

    # Save baseline hash for agents.md (so we know if user edited it)
    agents_dest = root / "agents.md"
    if agents_dest.exists():
        save_agents_md_hash(agents_dest)

    # Copy skill templates
    created_skills = []
    skipped_skills = []
    updated_skills = []
    
    # Files that should ALWAYS be updated
    ALWAYS_UPDATE = {'SKILL.md', 'companion_cli.py', '__init__.py', '__main__.py'}
    
    for f in skill_files:
        rel = f.relative_to(templates)
        dest = target / rel
        dest.parent.mkdir(parents=True, exist_ok=True)
        
        # Always copy SKILL.md, always copy new files
        if force or not dest.exists() or f.name in ALWAYS_UPDATE:
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
    target = root

    print_header("Snowline Update")

    if not target.exists():
        print_error("No skills found!")
        print_info("Run 'snowline init --apply' first")
        return

    templates = Path(__file__).parent / "templates"

    # Check for agents.md update (root file, not in skills/)
    agents_template = templates / "AGENTS_TEMPLATE.md"
    agents_dest = target.parent / "agents.md"
    agents_md_modified = False
    if agents_template.exists() and agents_dest.exists():
        if not filecmp.cmp(agents_template, agents_dest, shallow=False):
            agents_md_modified = True

    # Protected files (will NOT be auto-updated)
    PROTECTED = {
        "memory.json",
        "PROJECT_CONTEXT.md",
        "PROJECT_NOTES.md",
        "CURRENT_STATE.md",
        "scope_lock.json",
        "write_log.jsonl",
        "mode_ringan.json",
        ".gitignore",
        # NOTE: agents.md NOT protected - follows timestamp logic like other files
    }

    skill_files = [
        f for f in templates.rglob("*")
        if f.is_file()
        and not f.name.endswith(".pyc")
        and f.name != "AGENTS_TEMPLATE.md"  # Handled separately via agents_template variable
    ]

    new_files = []
    modified_files = []

    for f in skill_files:
        rel = str(f.relative_to(templates))
        if rel in PROTECTED:
            continue
        dest = target / rel
        if not dest.exists():
            new_files.append((f, rel))
        elif not filecmp.cmp(f, dest, shallow=False):
            modified_files.append((f, rel))

    obsolete_files = []
    for f in target.rglob("*"):
        if not f.is_file() or f.name.endswith(".pyc"): continue
        rel = str(f.relative_to(target))
        if rel in PROTECTED or rel.startswith("chamber") or rel.startswith("knowledge") or rel.startswith("rules") or rel == "agents.md" or rel == ".agents_md_baseline_hash": continue
        if not (templates / rel).exists():
            obsolete_files.append((f, rel))

    total_current = len([f for f in target.rglob("*") if f.is_file()])

    print_info(f"Current skills: {total_current}")

    # Check package commit (mirrors status() logic for consistency)
    import glob
    import json as _json

    remote_commit = None
    try:
        result = subprocess.run(
            ['git', 'ls-remote', 'https://github.com/UsmanAzizz/snowline-agent-tools.git', 'HEAD'],
            capture_output=True, text=True, timeout=15
        )
        if result.returncode == 0 and result.stdout:
            remote_commit = result.stdout.split()[0]
    except Exception as e:
        pass  # Silently fail - not critical

    installed_commit = None
    package_info = None
    try:
        result = subprocess.run(
            ['pip', 'show', 'snowline-agent-tools'],
            capture_output=True, text=True
        )
        if result.returncode == 0:
            for line in result.stdout.split('\n'):
                if line.startswith('Location:'):
                    package_info = line.split(':', 1)[1].strip()
    except Exception as e:
        pass  # Silently fail - not critical

    if package_info and remote_commit:
        dist_info_pattern = os.path.join(package_info, 'snowline_agent_tools-*.dist-info')
        matches = glob.glob(dist_info_pattern)
        if matches:
            direct_url_path = os.path.join(matches[0], 'direct_url.json')
            if os.path.exists(direct_url_path):
                try:
                    with open(direct_url_path, 'r', encoding='utf-8') as f:
                        data = _json.load(f)
                    installed_commit = data.get('vcs_info', {}).get('commit_id', '')
                except Exception as e:
                    pass  # Silently fail - not critical

    pkg_behind = (installed_commit and remote_commit and installed_commit != remote_commit)

    if not new_files and not modified_files and not agents_md_modified and not pkg_behind and not obsolete_files:
        print_success("All skills are up to date!")
        return

    if pkg_behind and not new_files and not modified_files and not agents_md_modified and not obsolete_files:
        print_warning("Package version tertinggal!")
        print_info("Skill files sudah sinkron. Jalankan 'snowline reinstall --latest' untuk update package.")
        return

    print_info(f"Available: {len(new_files)} new, {len(modified_files)} modified, {len(obsolete_files)} obsolete")

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
        
        # Warning for agents.md
        for _, rel in obsolete_files[:10]:
            print_list_item(f"[USANG] {rel}")
        if len(obsolete_files) > 10:
            print_info(f"... and {len(obsolete_files) - 10} more obsolete files")


        if obsolete_files:
            print_info("Catatan: Berkas [USANG] tidak akan dihapus otomatis.")
            print_info("Gunakan perintah manual untuk menghapusnya, misal: rm .agents/nama_berkas")

        if agents_md_modified:
            print()
            print_warning("[WARN] agents.md akan diperbarui!")
            print_warning("Jika Anda sudah edit manual, backup dulu sebelum lanjut.")
            print_warning("Contoh: copy .agents/agents.md ke .agents/agents.md.bak")
        
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

    # Update agents.md if template is newer
    if agents_md_modified:
        agents_dest = target.parent / "agents.md"
        baseline_hash = load_agents_md_baseline(agents_dest)
        current_hash = current_agents_md_hash(agents_dest)

        if baseline_hash and current_hash != baseline_hash:
            # User edited - auto-backup first
            backup_dir = target.parent.parent / ".backup_replace"
            backup_dir.mkdir(parents=True, exist_ok=True)
            ts = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_file = backup_dir / f"agents_md_{ts}.md"
            shutil.copy2(agents_dest, backup_file)
            print_info(f"[AUTO-BACKUP] {backup_file.name}")

        # Overwrite with template
        shutil.copy2(agents_template, agents_dest)
        if (target.parent / "chamber").exists():
            _ensure_chamber_pointer(agents_dest)
        save_agents_md_hash(agents_dest)
        print_info(f"Updated: agents.md")

    print()
    print_success(f"Updated: {created} new, {updated} modified")


def uninstall(apply=False, confirm_msg=None):
    _clear_pip_cache()
    root = Path.cwd() / ".agents"
    skills_dir = root / "skills"
    templates = Path(__file__).parent / "templates"

    print_header("Snowline Uninstall")

    if not skills_dir.exists():
        print_info("No skills found to remove")
        return

    # Build set of known template file relative paths
    known_paths = set()
    for f in templates.rglob("*"):
        if f.is_file() and f.name != "AGENTS_TEMPLATE.md":
            known_paths.add(str(f.relative_to(templates)))

    skill_files = [f for f in skills_dir.rglob("*") if f.is_file() and not f.name.endswith(".pyc")]

    # Separate into template-owned vs user-created
    to_remove = []
    to_preserve = []
    for f in skill_files:
        rel = str(f.relative_to(skills_dir))
        if rel in known_paths:
            to_remove.append(f)
        else:
            to_preserve.append(f)

    skill_count = len(to_remove)
    preserve_count = len(to_preserve)

    if not apply:
        print_warning(f"Will remove {skill_count} installed skill files from {skills_dir}")
        if to_preserve:
            print_info(f"Will preserve {preserve_count} user-created files:")
            for f in to_preserve:
                print_list_item(str(f.relative_to(skills_dir)))
        print_info("Configuration files will be kept")
        print()
        default_cmd = "snowline uninstall --apply to confirm"
        cmd = confirm_msg if confirm_msg else default_cmd
        safe_print(f"Run {Colors.BOLD}{cmd}{Colors.RESET}")
        return

    removed = 0
    for f in to_remove:
        try:
            f.unlink()
            removed += 1
        except Exception as e:
            safe_print(f"  {Colors.RED}x{Colors.RESET} {f.relative_to(skills_dir)}: {e}")

    for d in sorted(skills_dir.rglob("*"), reverse=True):
        if d.is_dir() and not list(d.iterdir()):
            try:
                d.rmdir()
            except Exception:
                pass

    print()
    print_success(f"Removed {removed} installed skill files")
    if to_preserve:
        print_info(f"Preserved {preserve_count} user-created files")


def reinstall(apply=False, latest=False):
    if latest:
        print_info("Mengambil versi terbaru dari GitHub...")
        if not apply:
            print_warning("Ini akan mendownload package dan melakukan reinstall.")
            safe_print("Run snowline reinstall --apply --latest to execute")
            return

        package_url = "git+https://github.com/UsmanAzizz/snowline-agent-tools.git"
        import platform
        if platform.system().lower() == "windows":
            print_info("Mendelegasikan ke CMD terpisah (Windows)...")
            cmd_str = f'start cmd.exe /c "ping 127.0.0.1 -n 2 > nul & echo Sedang mengunduh... & {sys.executable} -m pip install --force-reinstall --no-cache-dir {package_url} && {sys.executable} -m snowline.cli reinstall --apply && echo. && echo Reinstall berhasil! & pause"'
            os.system(cmd_str)
            sys.exit(0)
        else:
            res = subprocess.run([sys.executable, '-m', 'pip', 'install', '--force-reinstall', '--no-cache-dir', package_url])
            if res.returncode == 0:
                print_success("Package terupdate!")
                uninstall(apply=True)
                init(dry=False, force=True)
                print_success("Reinstall selesai!")
            else:
                print_error("Gagal mendownload package. Instalasi lokal tidak disentuh.")
    else:
        print_info("Memulihkan dari paket lokal.")
        if not apply:
            print_info("Untuk sekaligus mengambil versi terbaru dari GitHub: snowline reinstall --apply --latest")
        uninstall(apply=apply, confirm_msg="snowline reinstall --apply to confirm")
        if apply:
            init(dry=False, force=True)


def status():
    """Check package (GitHub) and project (.agents) layers."""

    # ---- Layer 1: Package (GitHub) ----
    installed_commit = None
    package_info = None

    try:
        result = subprocess.run(
            ['pip', 'show', 'snowline-agent-tools'],
            capture_output=True,
            text=True
        )
        if result.returncode == 0:
            for line in result.stdout.split('\n'):
                if line.startswith('Location:'):
                    package_info = line.split(':', 1)[1].strip()
    except Exception as e:
        print_warning(f"Gagal memeriksa paket: {e}")

    pkg_unknown_reason = ""
    pkg_unknown_kind = ""
    if package_info:
        import glob
        dist_info_pattern = os.path.join(package_info, 'snowline_agent_tools-*.dist-info')
        matches = glob.glob(dist_info_pattern)
        if matches:
            direct_url_path = os.path.join(matches[0], 'direct_url.json')
            if os.path.exists(direct_url_path):
                try:
                    with open(direct_url_path, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                    vcs_info = data.get('vcs_info', {})
                    installed_commit = vcs_info.get('commit_id', '')
                    if not installed_commit:
                        pkg_unknown_kind = "wheel"
                        pkg_unknown_reason = "direct_url.json ada tetapi tanpa vcs_info (dipasang dari wheel, bukan dari git)"
                except Exception as e:
                    pkg_unknown_kind = "parse_error"
                    pkg_unknown_reason = f"Gagal membaca direct_url.json: {e}"
            else:
                pkg_unknown_kind = "no_direct_url"
                pkg_unknown_reason = f"direct_url.json tidak ada di {matches[0]}"
        else:
            pkg_unknown_kind = "no_dist_info"
            pkg_unknown_reason = f"dist-info tidak ditemukan di {package_info}"
    else:
        pkg_unknown_kind = "no_package_info"
        pkg_unknown_reason = "Informasi lokasi package tidak ditemukan"


    remote_commit = None
    try:
        result = subprocess.run(
            ['git', 'ls-remote', 'https://github.com/UsmanAzizz/snowline-agent-tools.git', 'HEAD'],
            capture_output=True,
            text=True,
            timeout=15
        )
        if result.returncode == 0 and result.stdout:
            remote_commit = result.stdout.split()[0]
    except Exception:
        pass

    pkg_latest = (installed_commit and remote_commit and installed_commit == remote_commit)
    pkg_behind = (installed_commit and remote_commit and installed_commit != remote_commit)
    pkg_unknown = (not installed_commit)

    # ---- Layer 2: .agents files ----
    new_files_count = 0
    modified_files_count = 0
    agents_md_modified = False

    target = Path.cwd() / ".agents"
    if target.exists():
        templates = Path(__file__).parent / "templates"
        agents_template = templates / "AGENTS_TEMPLATE.md"
        agents_dest = target.parent / "agents.md"
        PROTECTED = {
            "memory.json", "PROJECT_CONTEXT.md", "PROJECT_NOTES.md",
            "CURRENT_STATE.md", "scope_lock.json",
        "write_log.jsonl",
        "mode_ringan.json",
        ".gitignore",
        }
        skill_files = [
            f for f in templates.rglob("*")
            if f.is_file()
            and not f.name.endswith(".pyc")
            and f.name != "AGENTS_TEMPLATE.md"
        ]
        if agents_template.exists() and agents_dest.exists():
            if not filecmp.cmp(agents_template, agents_dest, shallow=False):
                agents_md_modified = True
        for f in skill_files:
            rel = str(f.relative_to(templates))
            if rel in PROTECTED:
                continue
            dest = target / rel
            if not dest.exists():
                new_files_count += 1
            elif not filecmp.cmp(f, dest, shallow=False):
                modified_files_count += 1

    obsolete_files = []
    for f in target.rglob("*"):
        if not f.is_file() or f.name.endswith(".pyc"): continue
        rel = str(f.relative_to(target))
        if rel in PROTECTED or rel.startswith("chamber") or rel.startswith("knowledge") or rel.startswith("rules") or rel == "agents.md" or rel == ".agents_md_baseline_hash": continue
        if not (templates / rel).exists():
            obsolete_files.append((f, rel))

    total_current = len([f for f in target.rglob("*") if f.is_file()]) if target.exists() else 0
    agents_sinkron = (new_files_count == 0 and modified_files_count == 0 and not agents_md_modified)
    agents_tersedia = (new_files_count > 0 or modified_files_count > 0 or agents_md_modified)

    # ---- Output ----
    print_header("Snowline Status")

    # Layer 1: Package
    if pkg_unknown:
        print_error("Tidak dapat menentukan versi package terinstal")
        print_info(f"Penyebab: {pkg_unknown_reason}")
        if pkg_unknown_kind != "wheel":
            print_info("Coba: pip install --force-reinstall git+https://github.com/UsmanAzizz/snowline-agent-tools.git")
    elif pkg_latest:
        safe_print(f"  Paket         : commit {installed_commit[:8]}  (GitHub: {remote_commit[:8]})      -> terbaru")
    elif pkg_behind:
        safe_print(f"  Paket         : commit {installed_commit[:8]}  (GitHub: {remote_commit[:8]})      -> tertinggal")
        print_info("  -> snowline status (lalu pilih y)")
    else:
        safe_print(f"  Paket         : commit {installed_commit[:8] if installed_commit else '?'}  (GitHub: {remote_commit[:8] if remote_commit else '?'})")

    # Layer 2: .agents files
    safe_print(f"  File .agents/ : {total_current} file ({new_files_count} baru, {modified_files_count} diperbarui)     -> {'sinkron' if agents_sinkron else 'tersedia'}")

    if agents_tersedia:
        for _, rel in obsolete_files[:10]:
            print_list_item(f"[USANG] {rel}")
        if len(obsolete_files) > 10:
            print_info(f"... and {len(obsolete_files) - 10} more obsolete files")


        if obsolete_files:
            print_info("Catatan: Berkas [USANG] tidak akan dihapus otomatis.")
            print_info("Gunakan perintah manual untuk menghapusnya, misal: rm .agents/nama_berkas")

        if agents_md_modified:
            safe_print(f"                 -> {1 + modified_files_count} perubahan (termasuk agents.md)")
        safe_print(f"                 -> snowline update --apply")

    # Summary
    print()
    if pkg_latest and agents_sinkron:
        print_success("Semua sektor sudah terbaru.")
    elif pkg_unknown:
        pass  # Already printed above
    elif pkg_behind and agents_tersedia:
        print_warning("Package DAN file project tersedia update.")
    elif pkg_behind:
        print_warning("Ada versi package terbaru.")
    elif agents_tersedia:
        print_info("Ada file project yang tersedia update.")

    # Interactive prompt (only if GitHub is behind)
    if pkg_behind:
        print()
        safe_print(f"Apakah Anda ingin melakukan instalasi ulang dan update sekarang? [y/N]: ", end="")
        try:
            choice = input().strip().lower()
        except KeyboardInterrupt:
            choice = 'n'
            print()

        if choice == 'y':
            package_url = "git+https://github.com/UsmanAzizz/snowline-agent-tools.git"
            import platform

            if platform.system().lower() == "windows":
                print_info("Mendelegasikan proses update ke jendela terpisah...")
                cmd_str = f'start cmd.exe /c "ping 127.0.0.1 -n 2 > nul & echo Sedang mengunduh dan menerapkan versi terbaru... & {sys.executable} -m pip install --force-reinstall --no-cache-dir {package_url} && {sys.executable} -m snowline.cli update --apply && echo. && echo Update berhasil diterapkan! & pause"'
                os.system(cmd_str)
                safe_print(f"{Colors.DIM}Sesi perintah ini diakhiri untuk membuka akses modulasi file.{Colors.RESET}")
                sys.exit(0)
            else:
                print_section("Memulai proses update...")
                import subprocess as _subproc
                res = _subproc.run([sys.executable, '-m', 'pip', 'install', '--force-reinstall', '--no-cache-dir', package_url])
                if res.returncode == 0:
                    print_section("Menerapkan update pada tools lokal (snowline update)...")
                    _subproc.run([sys.executable, '-m', 'snowline.cli', 'update', '--apply'])
                    print_success("Update selesai!")
                else:
                    print_error("Update gagal (pip install gagal).")
        else:
            print_info("Update dibatalkan. Anda dapat mengupdate manual dengan perintah:")
            safe_print(f"  {Colors.BOLD}pip install --force-reinstall --no-cache-dir git+https://github.com/UsmanAzizz/snowline-agent-tools.git{Colors.RESET}")
            safe_print(f"  {Colors.BOLD}snowline update --apply{Colors.RESET}")




def _ensure_chamber_pointer(agents_md_path):
    """Appends chamber pointer to agents.md if not present."""
    if not agents_md_path.exists():
        return
    content = agents_md_path.read_text(encoding="utf-8")
    if "CHAMBER_RULES.md" not in content:
        pointer = "\n## Protokol Chamber\n- Ada protokol kerja di `.agents/chamber/`\n- Baca `CHAMBER_RULES.md` sebelum melapor\n- Laporan ditulis lewat: `snowline add-entry --from-file <berkas>`\n"
        agents_md_path.write_text(content + pointer, encoding="utf-8")

def init_chamber(dry=True, force=False):
    """Pasang chamber — protokol kerja PM/TL/QA. Opsional, terpisah dari init."""
    templates = Path(__file__).parent / "chamber_templates"
    target = Path.cwd() / ".agents" / "chamber"

    print_header("Snowline Chamber - Installer")

    if not templates.exists():
        print_error("Folder chamber_templates tidak ditemukan!")
        print_info(f"Dicari di: {templates}")
        return

    berkas = sorted(f for f in templates.glob("*.md") if f.is_file())
    if not berkas:
        print_error("Tidak ada templat chamber untuk dipasang.")
        return

    sudah_ada = [f.name for f in berkas if (target / f.name).exists()]
    if sudah_ada and not force:
        print_warning(f"Chamber sudah terpasang ({len(sudah_ada)} berkas).")
        print_info("Tidak ada yang diubah. Gunakan --force untuk menimpa.")
        print_info("Catatan: --force menimpa connector.md dan STATE.md juga.")
        return

    if dry:
        print_info("DRY RUN - tidak ada berkas yang ditulis.")
        print()

    for f in berkas:
        print_list_item(f"{'akan dipasang' if dry else 'dipasang'}: .agents/chamber/{f.name}")
        if not dry:
            target.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(f, target / f.name)

    print()
    if dry:
        print_info("Jalankan ulang dengan --apply untuk benar-benar memasang.")
        return

    _ensure_chamber_pointer(Path.cwd() / ".agents" / "agents.md")
    print_success(f"Chamber terpasang di {target}")
    print()
    safe_print(f"{Colors.BOLD}Langkah berikutnya:{Colors.RESET}")
    print_list_item("Baca .agents/chamber/CHAMBER_RULES.md")
    print_list_item("Tempel ONBOARDING_TL.md ke sesi agen pertama")
    print_list_item("Tempel ONBOARDING_QA.md ke sesi agen KEDUA yang terpisah")
    print_list_item("Sesudah itu, sinyal cukup satu kata: ''")
    print()
    safe_print(f"{Colors.DIM}TL dan QA harus sesi berbeda. Kalau satu sesi memegang"
               f" keduanya,{Colors.RESET}")
    safe_print(f"{Colors.DIM}ia sedang memeriksa pekerjaannya sendiri.{Colors.RESET}\n")


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
    safe_print(f"{Colors.DIM}Alternative: Use 'python -m snowline.cli'{Colors.RESET}\n")



def init_test(force=False):
    import os
    test_report_path = "TEST_REPORT.md"
    snowline_test_path = "SNOWLINE_TEST.md"

    if os.path.exists(test_report_path) and not force:
        with open(test_report_path, "r", encoding="utf-8") as f:
            if len(f.read().strip()) > 0:
                print(f"[BLOCKED] {test_report_path} sudah ada isinya. Gunakan --force untuk menimpa.")
                return

    snowline_test_content = """# Panduan Pengujian Snowline

Kamu diminta memakai paket alat agen ini untuk mengerjakan pekerjaan sungguhan
di proyek tempat kamu berada sekarang, lalu melaporkan apa yang terjadi.

Ini bukan tinjauan dan bukan penilaian. Jangan menulis apakah snowline bagus,
berguna, atau menjanjikan. Tulis apa yang kamu jalankan dan apa yang keluar.

## Aturan

1. **Dilarang memperbaiki.** Jangan menambal kode, mengubah konfigurasi, atau
   mengakali perintah supaya jalan. Kalau macet, catat macetnya lalu lanjut ke
   tugas berikutnya.
2. **Dilarang meringkas keluaran.** Tempel mentah. Tidak boleh ada
   "*(dan 46 berkas lainnya)*" atau "*keluarannya panjang*". Kalau memang
   panjang, tempel 15 baris pertama dan 5 baris terakhir, dan katakan berapa
   baris yang dipotong.
3. **Tidak ada klaim tanpa keluaran.** Kalimat "berhasil", "jalan", atau
   "sesuai harapan" hanya boleh muncul tepat di bawah keluaran yang
   menunjukkannya.
4. **Dilarang membaca sumber snowline.** Jangan membuka repositori snowline-agent-tools, jangan membaca site-packages/snowline/. Kamu menguji dari luar. Kalau tebakan pertamamu salah, cara kedua salah, dan petunjuk layarnya tidak membantu — itu temuan. Kalau jawabannya tidak ada di --help atau docstring biasa, dan kamu baru bisa menemukannya setelah membaca file Python sumbernya, itu juga temuan: alatnya butuh dokumentasi yang lebih baik.
5. **Catat tebakan.** Kalau kamu mencari sesuatu dan tidak ada, atau kamu harus menebak maksud argumennya, catat tebakan itu.
6. **Kerjakan berurutan.** M1 sampai M9, jangan dilompati. Kalau satu hal gagal keras sampai kamu tidak bisa jalan sama sekali, baru tinggalkan.
7. **Pakai alat dari proyek ini saja.** Semua skrip yang kamu jalankan harus berasal dari `.agents/` proyek tempat kamu sekarang. Jangan memanggil skrip dari proyek lain di mesin ini, walaupun jalurnya kamu tahu.
"""

    test_report_content = """# Laporan Pengujian Snowline

Laporan ini bukan penilaian. Jangan menulis apakah snowline bagus atau tidak.

## 0. Lingkungan

- OS: 
- Python: 
- Terpasang di sistem / dari sumber: 
- Versi persis: 
- Perintah yang membuktikan versinya:

## 1. Masuk tanpa dituntun

## 2. Companion

## 3. Satu suntingan sungguhan

## 4. Batas tulis

## 5. Chamber: pasang dan baca

## 6. Chamber: gerbang entri, dua arah

## 7. Satu agen, dua sesi

## 8. Subagen QA

## 9. Alat yang tidak kamu sentuh

## 10. Keputusan yang tidak bisa kamu periksa

## 11. Ke mana waktunya habis
"""

    with open(snowline_test_path, "w", encoding="utf-8", newline="") as f:
        f.write(snowline_test_content)
    
    with open(test_report_path, "w", encoding="utf-8", newline="") as f:
        f.write(test_report_content)

    print("[SUCCESS] SNOWLINE_TEST.md dan TEST_REPORT.md telah disiapkan.")

def main():
    parser = argparse.ArgumentParser(
        prog="snowline",
        description="Snowline Agent Tools - Portable tools for AI coding assistants"
    )
    subparsers = parser.add_subparsers(dest="command", help="Commands")

    p_init = subparsers.add_parser("init", help="Initialize .agents folder with skills")
    p_init.add_argument("target", nargs="?", help="Optional target to init (e.g. 'test')")
    p_init.add_argument("--apply", action="store_true", help="Apply installation")
    p_init.add_argument("--force", action="store_true", help="Force overwrite existing skills")

    p_update = subparsers.add_parser("update", help="Check for skill updates")
    p_update.add_argument("--apply", action="store_true", help="Apply updates")
    p_uninstall = subparsers.add_parser("uninstall", help="Remove installed skills")
    p_uninstall.add_argument("--apply", action="store_true", help="Apply uninstall")
    p_reinstall = subparsers.add_parser("reinstall", help="Reinstall skills (uninstall then init)")
    p_reinstall.add_argument("--apply", action="store_true", help="Apply reinstall")
    p_reinstall.add_argument("--latest", action="store_true", help="Also download latest package from GitHub")
    p_chamber = subparsers.add_parser("init_chamber", help="Install chamber protocol (PM/TL/QA) into .agents/chamber")
    p_chamber.add_argument("--apply", action="store_true", help="Apply installation")
    p_chamber.add_argument("--force", action="store_true", help="Overwrite existing chamber files")
    
    subparsers.add_parser("context", help="Tampilkan irisan tugas dan entri terakhir connector")
    
    p_add = subparsers.add_parser("add-entry", help="Tambahkan entri baru ke connector")
    p_add.add_argument("--from-file", help="Berkas masukan untuk entri")
    p_add.add_argument("--stdin", action="store_true", help="Gunakan standar input untuk masukan")
    p_add.add_argument("--force", action="store_true", help="Paksa tulis meskipun tidak lolos check-entry")

    p_check = subparsers.add_parser("check-entry", help="Periksa kelengkapan entri connector")
    p_check.add_argument("file", help="Berkas entri markdown")
    
    p_close = subparsers.add_parser("close-entry", help="Pindahkan satu entri dari connector ke history/<topik>")
    p_close.add_argument("topik", help="Nama topik, misal 'caching', 'encoding'")
    
    p_audit = subparsers.add_parser("audit", help="Ringkas catatan tulisan dari write_log.jsonl")
    p_audit.add_argument("--sejak", help="Filter catatan sejak tanggal/waktu tertentu")
    p_audit.add_argument("--hanya-luar-lingkup", action="store_true", help="Hanya tampilkan berkas di luar lingkup")

    p_test_clone = subparsers.add_parser("test-clone", help="Jalankan tes di klon repositori bersih")
    p_test_clone.add_argument("--cmd", help="Perintah khusus untuk menjalankan tes", default=None)
    p_setup_path = subparsers.add_parser("setup-path", help="Setup PATH and profiles")
    subparsers.add_parser("path", help="Show installation paths")
    subparsers.add_parser("status", help="Check package + project layers for updates")

    args = parser.parse_args()

    if args.command == "init":
        if args.target == "test":
            init_test(force=args.force)
        else:
            init(dry=not args.apply, force=args.force)
    elif args.command == "update":
        update(apply=args.apply)
    elif args.command == "uninstall":
        uninstall(apply=args.apply)
    elif args.command == "reinstall":
        reinstall(apply=args.apply, latest=args.latest)
    elif args.command == "init_chamber":
        init_chamber(dry=not args.apply, force=args.force)
    elif args.command == "context":
        try:
            from snowline.core_context import show_context
            show_context()
        except ImportError:
            sys.path.insert(0, os.path.dirname(__file__))
            from core_context import show_context
            show_context()
    elif args.command == "add-entry":
        from .core_add_entry import add_entry
        sys.exit(add_entry(from_file=args.from_file, use_stdin=args.stdin, force=args.force))
    elif args.command == "check-entry":
        try:
            from snowline.core_entry_checker import check_entry
            with open(args.file, 'r', encoding='utf-8') as f:
                content = f.read()
            if check_entry(content):
                sys.exit(0)
            else:
                sys.exit(1)
        except Exception as e:
            safe_print(f"{Colors.RED}Gagal memeriksa entri: {e}{Colors.RESET}")
            sys.exit(1)

    elif args.command == "close-entry":
        try:
            from snowline.core_close_entry import close_entry_command
            close_entry_command(args.topik)
        except Exception as e:
            safe_print(f"{Colors.RED}Gagal menutup entri: {e}{Colors.RESET}")
            sys.exit(1)
            
    elif args.command == "audit":
        try:
            from snowline.core_audit import run_audit
        except ImportError:
            sys.path.insert(0, os.path.dirname(__file__))
            from core_audit import run_audit
        sys.exit(run_audit(sejak=args.sejak, hanya_luar_lingkup=args.hanya_luar_lingkup))
    elif args.command == "test-clone":
        try:
            from snowline.core_test_clone import run_test_clone
        except ImportError:
            sys.path.insert(0, os.path.dirname(__file__))
            from core_test_clone import run_test_clone
        run_test_clone(args.cmd)
    elif args.command == "setup-path":
        from snowline import setup_path
        setup_path()
    elif args.command == "path":
        show_path()
    elif args.command == "status":
        status()
    else:
        print_header("Snowline Agent Tools")
        safe_print(f"{Colors.BOLD}Version:{Colors.RESET} 1.1.3")
        safe_print("")
        safe_print(f"{Colors.BOLD}Commands:{Colors.RESET}")
        print_list_item("init --apply  - Install skills to .agents folder")
        print_list_item("init_chamber  - Install chamber protocol (PM/TL/QA), optional")
        print_list_item("update        - Check for new/modified skills")
        print_list_item("status        - Check package + project layers")
        print_list_item("path          - Show installation paths")
        print_list_item("uninstall     - Remove installed skills")
        print_list_item("reinstall     - Reinstall skills (uninstall then init)")
        safe_print("")
        safe_print(f"{Colors.DIM}Run 'snowline <command> --help' for more info{Colors.RESET}\n")


if __name__ == "__main__":
    main()
