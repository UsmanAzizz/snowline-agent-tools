import os
import sys
import re
import shutil
import json
from datetime import datetime

if sys.stdout.encoding != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8')


def check_scope_write(write_target):
    """Block if write target is outside allowed scope (security gate, fail-closed)."""
    # Ensure .agents/skills is in sys.path so scope_guardian can be found
    _SKILLS = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))  # -> .agents/skills
    if _SKILLS not in sys.path:
        sys.path.insert(0, _SKILLS)
    from scope_guardian.scripts.scope_check import is_file_in_scope

    lock_file = os.path.join(os.getcwd(), '.agents', 'scope_lock.json')
    if not os.path.exists(lock_file):
        print("[BLOCKED] scope_lock.json not found in .agents/. Create it first to define scope.")
        sys.exit(1)
    try:
        with open(lock_file, 'r', encoding='utf-8') as f:
            scope_data = json.load(f)
    except Exception:
        print("[BLOCKED] Failed to parse scope_lock.json.")
        sys.exit(1)
    allowed_files = scope_data.get('allowed_files', [])
    allowed_patterns = scope_data.get('allowed_patterns', [])
    task = scope_data.get('task', 'Unknown task')
    if not is_file_in_scope(write_target, allowed_files, allowed_patterns):
        print(f"[BLOCKED] Write target is OUT OF SCOPE.")
        print(f"Task: {task}")
        print(f"Target: {write_target}")
        print(f"Allowed: {allowed_files}")
        sys.exit(1)


IGNORE_DIRS = {'.git', 'node_modules', 'vendor', 'dist', 'build', '.history'}
EXTENSIONS = ['.js', '.jsx', '.ts', '.tsx']

def find_file(filename, root_dir):
    matches = []
    # If filename has no extension, we will search for it with common extensions
    has_ext = any(filename.endswith(ext) for ext in EXTENSIONS)
    search_names = [filename] if has_ext else [filename + ext for ext in EXTENSIONS]
    
    for r, dirs, files in os.walk(root_dir):
        dirs[:] = [d for d in dirs if d not in IGNORE_DIRS]
        for f in files:
            if f in search_names:
                matches.append(os.path.join(r, f))
    return matches

def compute_relative_path(source_file, target_file):
    source_dir = os.path.dirname(os.path.abspath(source_file))
    target_abs = os.path.abspath(target_file)
    # Get relative path from source_dir to target_file
    rel_path = os.path.relpath(target_abs, source_dir)
    # Convert Windows backslashes to forward slashes for imports
    rel_path = rel_path.replace('\\', '/')
    # Ensure it starts with ./ or ../
    if not rel_path.startswith('.'):
        rel_path = './' + rel_path
    # Remove extension for JS/TS imports
    for ext in EXTENSIONS:
        if rel_path.endswith(ext):
            rel_path = rel_path[:-len(ext)]
            break
    return rel_path

def fix_import(source_file, broken_import, apply_mode):
    print("🔗 SMART IMPORT FIXER 🔗")
    print("=" * 60)

    # Check scope before writing
    check_scope_write(source_file)

    if not os.path.exists(source_file):
        print(f"[FAIL] Source file not found: {source_file}")
        return
        
    basename = os.path.basename(broken_import)
    print(f"[INFO] Searching for actual location of '{basename}'...")
    
    root_dir = os.getcwd()
    matches = find_file(basename, root_dir)
    
    if not matches:
        print(f"[FAIL] Could not find any file named {basename} in the project.")
        return
        
    # Finding 2B: proximity tiebreaker for multiple matches
    if len(matches) > 1:
        source_dir = os.path.dirname(os.path.abspath(source_file))
        def proximity_score(match):
            match_dir = os.path.dirname(match)
            if match_dir == source_dir:
                return 0
            try:
                rel = os.path.relpath(match_dir, source_dir)
                if rel == '.':
                    return 0
                # Count number of '..' components in relative path
                return rel.count('..') + rel.count(os.sep)
            except:
                return 999
        matches.sort(key=proximity_score)
        if proximity_score(matches[0]) < proximity_score(matches[-1]):
            target_file = matches[0]
            print(f"[INFO] Multiple matches found — using nearest one: {target_file}")
        else:
            print(f"[FAIL] Multiple files found with basename '{basename}':")
            for m in matches:
                print(f"  - {m}")
            print(f"[FAIL] Please provide the full path to the correct file.")
            return
    elif len(matches) == 1:
        target_file = matches[0]

    new_import = compute_relative_path(source_file, target_file)
    print(f"\n[INFO] Broken Import : {broken_import}")
    print(f"[INFO] Correct Import: {new_import}")

    try:
        with open(source_file, 'r', encoding='utf-8') as f:
            content = f.read()

        # Finding 2A: use quote-backreference regex to avoid substring corruption
        escaped = re.escape(broken_import)
        pattern = re.compile(r'([\'"])' + escaped + r'\1')
        if pattern.search(content):
            new_content = pattern.sub(lambda m: m.group(1) + new_import + m.group(1), content)
        elif broken_import in content:
            # Fallback: plain replace only if pattern didn't match (e.g. unusual quote char)
            new_content = content.replace(broken_import, new_import)
        else:
            print(f"[WARN] The import '{broken_import}' was not found in {source_file}.")
            return
        
        if not apply_mode:
            print("\n" + "=" * 60)
            print("[OK] Dry-run complete. Found the correct path.")
            print("\n💡 PROMPT UNTUK AI (Copy-Paste ini):")
            print(f'"Berdasarkan hasil pencarian Smart Import Fixer di atas, jalankan ulang perintah dengan tambahan flag --apply untuk memperbaiki rute secara otomatis."')
        else:
            backup_dir = os.path.join(root_dir, '.backup_replace', datetime.now().strftime("%Y%m%d_%H%M%S"))
            os.makedirs(backup_dir, exist_ok=True)
            backup_path = os.path.join(backup_dir, os.path.basename(source_file) + ".bak")
            shutil.copy2(source_file, backup_path)
            
            with open(source_file, 'w', encoding='utf-8') as f:
                f.write(new_content)
                
            print("\n" + "=" * 60)
            print(f"[OK] Import fixed! Backup saved to {backup_dir}")
            
    except Exception as e:
        print(f"[FAIL] Error processing file: {e}")

def check_role_permission(is_apply=False):
    if is_apply:
        import os, json
        try:
            root_dir = os.getcwd()
            paths = [
                os.path.join(root_dir, '.here_we_are', 'peran.json'),
                os.path.join(root_dir, '.agents', 'chamber', 'peran.json')
            ]
            for p in paths:
                if os.path.exists(p):
                    with open(p, 'r', encoding='utf-8') as f:
                        peran_data = json.load(f)
                    if peran_data.get('peran') == 'QA':
                        print("[BLOCKED] Akses tulis (--apply) ditolak untuk peran QA.")
                        sys.exit(1)
        except Exception:
            pass

def main():
    if len(sys.argv) < 3:
        print("Usage: python fixer.py <source_file> <broken_import_string> [--apply]")
        sys.exit(1)
        
    apply_mode = "--apply" in sys.argv
    check_role_permission(apply_mode)
    source_file = sys.argv[1]
    broken_import = sys.argv[2]
    
    fix_import(source_file, broken_import, apply_mode)

if __name__ == "__main__":
    main()
