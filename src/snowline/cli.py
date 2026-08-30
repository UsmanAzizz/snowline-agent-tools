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

# Keadaan lokal: berkas dan folder yang ditulis snowline sendiri waktu bekerja,
# bukan bagian dari templat. Satu daftar dipakai dua tempat -- .gitignore yang
# ditulis `init`, dan pemeriksa berkas usang di `update` dan `status`.
#
# Sebelum ini keduanya punya daftar sendiri-sendiri dan berbeda pendapat:
# .gitignore tahu session_cache.json itu keadaan lokal, pemeriksa usang tidak.
# Akibatnya 27 berkas bawaan snowline dilaporkan [USANG] di proyek nyata, dan
# label itu jadi kebisingan yang orang belajar abaikan.
RUNTIME_STATE_FILES = [
    "write_log.jsonl",
    "scope_lock.json",
    "task_lock.json",
    "session_cache.json",
    "decision_history.json",
    "companion_usage.jsonl",
    "mode_ringan.json",
    "memory.json",
    "chamber/role.json",
    "role.json",
    ".agents_md_baseline_hash",
]

# Folder yang seluruh isinya keadaan lokal.
RUNTIME_STATE_DIRS = [
    "hooks/.history",
    "test_history",
    "__pycache__",
]


PROTECTED_FILES = {
    "memory.json",
    "PROJECT_CONTEXT.md",
    "PROJECT_NOTES.md",
    "CURRENT_STATE.md",
    "scope_lock.json",
    "write_log.jsonl",
    "mode_ringan.json",
    ".gitignore",
}

def is_protected(rel: str) -> bool:
    """Apakah berkas ini terlindungi (perbandingan tidak peka huruf)."""
    norm_lower = rel.replace("\\", "/").strip("/").lower()
    return norm_lower in {f.lower() for f in PROTECTED_FILES}

def get_snowline_version() -> str:
    """Baca versi dinamis dari __init__.__version__."""
    try:
        from snowline import __version__
        return __version__
    except Exception:
        try:
            import snowline
            return getattr(snowline, "__version__", "1.2.0")
        except Exception:
            return "1.2.0"

def get_installed_package_info():
    """Membaca informasi paket yang sedang berjalan via importlib.metadata."""
    import importlib.metadata
    import json

    installed_commit = None
    pkg_unknown_reason = ""
    pkg_unknown_kind = ""
    version = None

    try:
        dist = importlib.metadata.distribution("snowline-agent-tools")
        version = dist.version
        direct_url_content = dist.read_text("direct_url.json")
        if direct_url_content:
            try:
                data = json.loads(direct_url_content)
                vcs_info = data.get("vcs_info", {})
                installed_commit = vcs_info.get("commit_id", "")
                if not installed_commit:
                    dir_info = data.get("dir_info", {})
                    if isinstance(dir_info, dict) and dir_info.get("editable") is True:
                        pkg_unknown_kind = "editable"
                        url_target = data.get("url", "")
                        pkg_unknown_reason = f"dipasang dalam mode editable (menunjuk ke {url_target})"
                    else:
                        pkg_unknown_kind = "wheel"
                        pkg_unknown_reason = "direct_url.json ada tetapi tanpa vcs_info (dipasang dari wheel, bukan dari git)"
            except Exception as e:
                pkg_unknown_kind = "parse_error"
                pkg_unknown_reason = f"Gagal membaca direct_url.json: {e}"
        else:
            pkg_unknown_kind = "no_direct_url"
            pkg_unknown_reason = "direct_url.json tidak ditemukan pada metadata paket terinstal"
    except importlib.metadata.PackageNotFoundError:
        pkg_unknown_kind = "no_dist_info"
        pkg_unknown_reason = "Paket snowline-agent-tools tidak ditemukan di sys.path penafsir yang sedang berjalan"
    except Exception as e:
        pkg_unknown_kind = "no_package_info"
        pkg_unknown_reason = f"Gagal membaca metadata paket: {e}"

    return {
        "commit": installed_commit,
        "version": version,
        "unknown_kind": pkg_unknown_kind,
        "unknown_reason": pkg_unknown_reason,
    }


def fetch_remote_package_info(repo_url="https://github.com/UsmanAzizz/snowline-agent-tools.git", timeout=15):
    """Membaca commit HEAD dan commit tag rilis terbaru dari remote git repo."""
    remote_head = None
    latest_tag_commit = None
    latest_tag_name = None

    try:
        res = subprocess.run(
            ["git", "ls-remote", "--tags", "--heads", repo_url],
            capture_output=True, text=True, timeout=timeout
        )
        if res.returncode == 0 and res.stdout:
            tags_map = {}
            peeled_map = {}
            for line in res.stdout.splitlines():
                parts = line.strip().split()
                if len(parts) >= 2:
                    sha, ref = parts[0], parts[1]
                    if ref == "refs/heads/main" or ref == "HEAD":
                        remote_head = sha
                    elif ref.startswith("refs/tags/"):
                        tag_ref = ref[len("refs/tags/"):]
                        if tag_ref.endswith("^{}"):
                            peeled_map[tag_ref[:-3]] = sha
                        else:
                            tags_map[tag_ref] = sha

            def parse_ver(t):
                import re
                m = re.findall(r'\d+', t)
                return tuple(int(x) for x in m) if m else (0,)

            valid_tags = [t for t in tags_map.keys() if "alpha" not in t.lower() and "beta" not in t.lower()] or list(tags_map.keys())
            if valid_tags:
                valid_tags.sort(key=parse_ver)
                latest_tag_name = valid_tags[-1]
                latest_tag_commit = peeled_map.get(latest_tag_name, tags_map[latest_tag_name])
    except Exception:
        pass

    return {
        "head_commit": remote_head,
        "latest_tag_commit": latest_tag_commit,
        "latest_tag_name": latest_tag_name,
    }


def evaluate_package_freshness(installed_commit, remote_head_commit, latest_tag_commit, tag_name=None):
    """
    Evaluasi status kemutakhiran paket.
    Return dict:
      - status: 'latest' | 'behind' | 'unknown'
      - reason: str (keterangan pembanding atau penyebab unknown)
      - matched_target: 'tag' | 'head' | 'both' | None
    """
    if not installed_commit:
        return {
            "status": "unknown",
            "reason": "commit terpasang tidak diketahui",
            "matched_target": None,
        }

    if not remote_head_commit and not latest_tag_commit:
        return {
            "status": "unknown",
            "reason": "remote commit tidak terbaca",
            "matched_target": None,
        }

    matches_tag = bool(latest_tag_commit and installed_commit == latest_tag_commit)
    matches_head = bool(remote_head_commit and installed_commit == remote_head_commit)

    if matches_tag and matches_head:
        return {
            "status": "latest",
            "reason": f"sesuai dengan tag rilis terbaru ({tag_name or 'tag'}) dan remote HEAD ({remote_head_commit[:8]})",
            "matched_target": "both",
        }
    elif matches_tag:
        return {
            "status": "latest",
            "reason": f"sesuai dengan tag rilis terbaru ({tag_name or 'tag'} - {latest_tag_commit[:8]})",
            "matched_target": "tag",
        }
    elif matches_head:
        return {
            "status": "latest",
            "reason": f"sesuai dengan remote HEAD ({remote_head_commit[:8]})",
            "matched_target": "head",
        }
    else:
        target_descs = []
        if tag_name and latest_tag_commit:
            target_descs.append(f"tag {tag_name} ({latest_tag_commit[:8]})")
        elif latest_tag_commit:
            target_descs.append(f"tag rilis ({latest_tag_commit[:8]})")
        if remote_head_commit:
            target_descs.append(f"HEAD ({remote_head_commit[:8]})")
        pembanding = " dan ".join(target_descs) if target_descs else "remote"
        return {
            "status": "behind",
            "reason": f"tertinggal dari {pembanding}",
            "matched_target": None,
        }

def is_runtime_state(rel: str) -> bool:
    """Apakah jalur relatif di dalam .agents/ ini keadaan lokal, bukan templat."""
    norm = rel.replace(chr(92), "/")
    if norm in RUNTIME_STATE_FILES:
        return True
    return any(norm == d or norm.startswith(d + "/") for d in RUNTIME_STATE_DIRS)


def build_agents_gitignore() -> str:
    """Isi .agents/.gitignore, dibangun dari daftar yang sama."""
    baris = ["# Snowline Agent Tools - keadaan lokal, jangan di-commit"]
    baris += RUNTIME_STATE_FILES
    baris += [d + "/" for d in RUNTIME_STATE_DIRS if d != "__pycache__"]
    baris += ["*.pyc", "__pycache__/"]
    return chr(10).join(baris) + chr(10)


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
import snowline


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
        ".gitignore": build_agents_gitignore(),
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
    ALWAYS_UPDATE = {'SKILL.md', '__init__.py', '__main__.py'}
    
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
    print_list_item("Pasang gerbang keamanan git: snowline install-hooks --apply")
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
        if is_protected(rel):
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
        rel_norm = rel.replace("\\", "/")
        rel_lower = rel_norm.lower()
        if is_protected(rel) or is_runtime_state(rel) or rel_lower.startswith("chamber") or rel_lower.startswith("knowledge") or rel_lower.startswith("rules") or rel_lower == "agents.md": continue
        if not (templates / rel).exists():
            obsolete_files.append((f, rel))

    total_current = len([f for f in target.rglob("*") if f.is_file()])

    print_info(f"Current skills: {total_current}")

    # Check package status via importlib.metadata & remote tags/HEAD
    pkg_info = get_installed_package_info()
    installed_commit = pkg_info.get("commit")
    remote_info = fetch_remote_package_info()
    freshness = evaluate_package_freshness(
        installed_commit=installed_commit,
        remote_head_commit=remote_info.get("head_commit"),
        latest_tag_commit=remote_info.get("latest_tag_commit"),
        tag_name=remote_info.get("latest_tag_name")
    )
    pkg_behind = (freshness["status"] == "behind")

    if not new_files and not modified_files and not agents_md_modified and not pkg_behind and not obsolete_files:
        print_success("All skills are up to date!")
        return

    if pkg_behind and not new_files and not modified_files and not agents_md_modified and not obsolete_files:
        print_warning(f"Package version tertinggal! ({freshness['reason']})")
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
    pkg_info = get_installed_package_info()
    installed_commit = pkg_info.get("commit")
    pkg_unknown_kind = pkg_info.get("unknown_kind")
    pkg_unknown_reason = pkg_info.get("unknown_reason")

    remote_info = fetch_remote_package_info()
    remote_commit = remote_info.get("head_commit")
    freshness = evaluate_package_freshness(
        installed_commit=installed_commit,
        remote_head_commit=remote_commit,
        latest_tag_commit=remote_info.get("latest_tag_commit"),
        tag_name=remote_info.get("latest_tag_name")
    )

    pkg_latest = (freshness["status"] == "latest")
    pkg_behind = (freshness["status"] == "behind")
    pkg_unknown = (freshness["status"] == "unknown" and (not installed_commit or pkg_unknown_kind))
    pkg_reason = freshness["reason"]

    # ---- Layer 2: .agents files ----
    new_files_count = 0
    modified_files_count = 0
    agents_md_modified = False

    target = Path.cwd() / ".agents"
    if target.exists():
        templates = Path(__file__).parent / "templates"
        agents_template = templates / "AGENTS_TEMPLATE.md"
        agents_dest = target.parent / "agents.md"
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
            if is_protected(rel):
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
        rel_norm = rel.replace("\\", "/")
        rel_lower = rel_norm.lower()
        if is_protected(rel) or is_runtime_state(rel) or rel_lower.startswith("chamber") or rel_lower.startswith("knowledge") or rel_lower.startswith("rules") or rel_lower == "agents.md": continue
        if not (templates / rel).exists():
            obsolete_files.append((f, rel))

    total_current = len([f for f in target.rglob("*") if f.is_file()]) if target.exists() else 0
    agents_sinkron = (new_files_count == 0 and modified_files_count == 0 and not agents_md_modified and len(obsolete_files) == 0)
    agents_tersedia = (new_files_count > 0 or modified_files_count > 0 or agents_md_modified or len(obsolete_files) > 0)

    # ---- Output ----
    print_header("Snowline Status")

    # Layer 1: Package
    if pkg_unknown:
        print_error("Tidak dapat menentukan versi package terinstal")
        print_info(f"Penyebab: {pkg_unknown_reason}")
        if pkg_unknown_kind not in ("wheel", "editable"):
            print_info("Coba: pip install --force-reinstall git+https://github.com/UsmanAzizz/snowline-agent-tools.git")
    elif pkg_latest:
        safe_print(f"  Paket         : commit {installed_commit[:8]} ({pkg_reason})      -> terbaru")
    elif pkg_behind:
        safe_print(f"  Paket         : commit {installed_commit[:8]} ({pkg_reason})      -> tertinggal")
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

    role_file = target / "role.json"
    if not dry:
        target.mkdir(parents=True, exist_ok=True)
        if force or not role_file.exists():
            role_file.write_text('{"peran": null}\n', encoding="utf-8")
            print_list_item("dipasang: .agents/chamber/role.json")
        else:
            print_info("role.json sudah ada (tidak ditimpa)")
            
        # Ensure role.json is in .agents/.gitignore
        agents_gi = Path.cwd() / ".agents" / ".gitignore"
        if agents_gi.exists():
            gi_content = agents_gi.read_text(encoding="utf-8")
            to_append = []
            if "chamber/role.json" not in gi_content and "role.json" not in gi_content:
                to_append.append("chamber/role.json")
                to_append.append("role.json")
            if to_append:
                agents_gi.write_text(gi_content.rstrip() + "\n" + "\n".join(to_append) + "\n", encoding="utf-8")
        else:
            agents_dir = Path.cwd() / ".agents"
            agents_dir.mkdir(parents=True, exist_ok=True)
            agents_gi.write_text("write_log.jsonl\nscope_lock.json\nsession_cache.json\nmode_ringan.json\nchamber/role.json\nrole.json\n*.pyc\n__pycache__/\n", encoding="utf-8")
    else:
        print_list_item("akan dipasang: .agents/chamber/role.json")

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
    import re
    from datetime import datetime

    templates = Path(__file__).parent / "test_templates"
    src_test = templates / "SNOWLINE_TEST.md"
    src_report = templates / "TEST_REPORT.md"

    for f in (src_test, src_report):
        if not f.exists():
            print(f"[BLOCKED] Templat tidak ditemukan: {f}")
            print("Pemasangan snowline tampaknya tidak lengkap.")
            return

    history_root = Path.cwd() / ".agents" / "test_history"
    history_root.mkdir(parents=True, exist_ok=True)

    today_str = datetime.now().strftime("%Y-%m-%d")
    pattern = re.compile(rf"^{re.escape(today_str)}_(\d+)$")
    existing_nums = []
    for entry in history_root.iterdir():
        if entry.is_dir():
            m = pattern.match(entry.name)
            if m:
                existing_nums.append((int(m.group(1)), entry))

    reused = False
    if existing_nums:
        existing_nums.sort(key=lambda x: x[0])
        latest_num, latest_dir = existing_nums[-1]
        latest_report = latest_dir / "TEST_REPORT.md"

        is_empty = False
        if not latest_report.exists():
            is_empty = True
        else:
            try:
                if latest_report.read_bytes() == src_report.read_bytes():
                    is_empty = True
            except Exception:
                pass

        if is_empty:
            target_dir = latest_dir
            reused = True
        else:
            target_dir = history_root / f"{today_str}_{latest_num + 1}"
    else:
        target_dir = history_root / f"{today_str}_1"

    target_dir.mkdir(parents=True, exist_ok=True)
    snowline_test_path = target_dir / "SNOWLINE_TEST.md"
    test_report_path = target_dir / "TEST_REPORT.md"

    abs_report_path = str(test_report_path.resolve())
    test_content = src_test.read_bytes()
    if b"{{JALUR_LAPORAN}}" in test_content:
        test_content = test_content.replace(b"{{JALUR_LAPORAN}}", abs_report_path.encode("utf-8"))

    with open(snowline_test_path, "wb") as f:
        f.write(test_content)

    with open(test_report_path, "wb") as f:
        f.write(src_report.read_bytes())

    try:
        rel_dir = target_dir.relative_to(Path.cwd()).as_posix()
    except Exception:
        rel_dir = str(target_dir)

    if reused:
        print(f"[SUCCESS] Folder {rel_dir}/ dipakai ulang\n          (laporannya belum terisi).")
    else:
        print(f"[SUCCESS] Uji baru disiapkan di {rel_dir}/\n          Tempel isi SNOWLINE_TEST.md di folder itu ke sesi agen.")

def main():
    parser = argparse.ArgumentParser(
        prog="snowline",
        description="Snowline Agent Tools - Portable tools for AI coding assistants"
    )
    parser.add_argument("--version", "-v", action="version", version=get_snowline_version(), help="Show program's version number and exit")
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

    p_rot = subparsers.add_parser("rotate", help="Pindahkan riwayat entri connector ke history/<topik> secara aman")
    p_rot.add_argument("topik", help="Nama topik arsip rotasi")
    p_rot.add_argument("--apply", action="store_true", help="Terapkan rotasi secara permanen")
    
    p_audit = subparsers.add_parser("audit", help="Ringkas catatan tulisan dari write_log.jsonl")
    p_audit.add_argument("--sejak", help="Filter catatan sejak tanggal/waktu tertentu")
    p_audit.add_argument("--hanya-luar-lingkup", action="store_true", help="Hanya tampilkan berkas di luar lingkup")

    p_role = subparsers.add_parser("role", help="Tampilkan atau ubah peran di .agents/chamber/role.json")
    p_role.add_argument("nama_peran", nargs="?", help="Nama peran baru (misal: QA, TL, PM)")
    p_role.add_argument("--apply", action="store_true", help="Terapkan perubahan peran secara permanen")

    p_ih = subparsers.add_parser("install-hooks", help="Pasang Project Guardian pre-commit hook")
    p_ih.add_argument("--apply", action="store_true", help="Terapkan pemasangan hook")
    p_ih.add_argument("--force", action="store_true", help="Timpa hook pre-commit yang sudah ada (simpan cadangan .bak)")

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
    elif args.command == "role":
        try:
            from snowline.core_role import role_command
        except ImportError:
            sys.path.insert(0, os.path.dirname(__file__))
            from core_role import role_command
        role_command(args.nama_peran, apply=args.apply)

    elif args.command == "rotate":
        try:
            from snowline.core_rotate import rotate_command
        except ImportError:
            sys.path.insert(0, os.path.dirname(__file__))
            from core_rotate import rotate_command
        rotate_command(args.topik, apply=args.apply)
            
    elif args.command == "audit":
        try:
            from snowline.core_audit import run_audit
        except ImportError:
            sys.path.insert(0, os.path.dirname(__file__))
            from core_audit import run_audit
        sys.exit(run_audit(sejak=args.sejak, hanya_luar_lingkup=args.hanya_luar_lingkup))
    elif args.command == "install-hooks":
        try:
            from snowline.install_hooks import install_hook
        except ImportError:
            sys.path.insert(0, os.path.dirname(__file__))
            from install_hooks import install_hook
        success = install_hook(force=args.force, dry=not args.apply)
        if not success:
            sys.exit(1)
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
        safe_print(f"{Colors.BOLD}Version:{Colors.RESET} {get_snowline_version()}")
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
