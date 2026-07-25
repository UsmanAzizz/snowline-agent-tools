import os
import sys
import re
import shutil
from datetime import datetime

if sys.stdout.encoding != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8')

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
        
    target_file = matches[0]
    if len(matches) > 1:
        print(f"[WARN] Multiple files found. Using the first one: {target_file}")
        
    new_import = compute_relative_path(source_file, target_file)
    print(f"\n[INFO] Broken Import : {broken_import}")
    print(f"[INFO] Correct Import: {new_import}")
    
    try:
        with open(source_file, 'r', encoding='utf-8') as f:
            content = f.read()
            
        if broken_import not in content:
            print(f"[WARN] The string '{broken_import}' was not found in {source_file}.")
            return
            
        new_content = content.replace(broken_import, new_import)
        
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

def main():
    if len(sys.argv) < 3:
        print("Usage: python fixer.py <source_file> <broken_import_string> [--apply]")
        sys.exit(1)
        
    source_file = sys.argv[1]
    broken_import = sys.argv[2]
    apply_mode = "--apply" in sys.argv
    
    fix_import(source_file, broken_import, apply_mode)

if __name__ == "__main__":
    main()
