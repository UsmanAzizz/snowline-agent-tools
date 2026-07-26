import os
import sys
import argparse
import re
import shutil
import json
from datetime import datetime

# Force UTF-8 encoding for Windows terminal
if sys.stdout.encoding.lower() != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8')

DEFAULT_EXCLUDES = {'.git', 'node_modules', '.history', 'vendor', 'dist', 'build', 'quarantine', '.backup_replace', '.agents'}
MAX_FILE_SIZE = 500 * 1024 # 500 KB

def check_task_state():
    state_file = os.path.join(os.getcwd(), '.agents', 'task_state.json')
    if not os.path.exists(state_file):
        return
        
    try:
        with open(state_file, 'r', encoding='utf-8') as f:
            state = json.load(f)
    except Exception:
        return
        
    if state.get('phase') == 'pseudocode_pending':
        print("[BLOCKED] Pseudocode untuk task ini belum disetujui user.")
        print(f"Task: {state.get('task', 'Unknown')}")
        print("Minta user approve pseudocode dulu sebelum --apply bisa dijalankan.")
        sys.exit(1)

def find_project_root(start_path):
    current = os.path.abspath(start_path)
    while True:
        if os.path.exists(os.path.join(current, 'package.json')) or os.path.exists(os.path.join(current, '.git')):
            return current
        parent = os.path.dirname(current)
        if parent == current:
            return os.path.abspath(start_path)
        current = parent

def get_args():
    parser = argparse.ArgumentParser(description="Smart Replace (Pure Python Edition)")
    parser.add_argument("target_dir", help="Target directory or file (absolute path)")
    parser.add_argument("search_string", help="String or pattern to search for")
    parser.add_argument("replace_string", nargs="?", default="", help="String to replace with (or empty if using --replacement-file)")
    parser.add_argument("--search-file", help="Path to file containing search text", default=None)
    parser.add_argument("--replacement-file", help="Path to file containing replacement text", default=None)
    parser.add_argument("--ext", help="Comma-separated extensions to include (e.g. .js,.jsx)", default="")
    parser.add_argument("--regex", action="store_true", help="Treat search_string as a regular expression")
    parser.add_argument("--fuzzy", action="store_true", help="Allow flexible whitespace/newlines matching (opt-in)")
    parser.add_argument("--whole-word", action="store_true", help="Match whole words only")
    parser.add_argument("--apply", action="store_true", help="Actually modify the files (Low risk only)")
    parser.add_argument("--apply-validated", action="store_true", help="Actually modify the files (Bypass Medium/High risk block)")
    return parser.parse_args()

def backup_file(filepath, backup_dir):
    rel_path = os.path.relpath(filepath, os.getcwd())
    backup_path = os.path.join(backup_dir, rel_path)
    os.makedirs(os.path.dirname(backup_path), exist_ok=True)
    shutil.copy2(filepath, backup_path)
    return backup_path

def main():
    args = get_args()

    if args.search_file:
        try:
            with open(args.search_file, 'r', encoding='utf-8') as f:
                args.search_string = f.read()
        except Exception as e:
            print(f"[ERROR] Could not read search file: {e}")
            sys.exit(1)

    if args.replacement_file:
        try:
            with open(args.replacement_file, 'r', encoding='utf-8') as f:
                args.replace_string = f.read()
        except Exception as e:
            print(f"[ERROR] Could not read replacement file: {e}")
            sys.exit(1)
    
    if not os.path.exists(args.target_dir):
        print(f"[FAIL] Target not found: {args.target_dir}")
        sys.exit(1)
        
    exts = [e.strip() for e in args.ext.split(',')] if args.ext else []
    
    pattern_str = args.search_string
    if args.fuzzy:
        # Fuzzy mode: escape exact strings but allow any whitespace between words
        words = pattern_str.split()
        escaped_words = [re.escape(w) for w in words]
        pattern_str = r'\s+'.join(escaped_words)
    elif not args.regex:
        pattern_str = re.escape(pattern_str)
        
    if args.whole_word:
        pattern_str = r'\b' + pattern_str + r'\b'
        
    try:
        regex = re.compile(pattern_str)
    except re.error as e:
        print(f"[FAIL] Invalid regex: {e}")
        sys.exit(1)
        
    backup_dir = None
    if args.apply or args.apply_validated:
        check_task_state()
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        project_root = find_project_root(args.target_dir)
        backup_dir = os.path.join(project_root, '.backup_replace', timestamp)

    match_count = 0
    file_count = 0
    scanned_files = 0
    pending_writes = []
    
    # Check if target is a file or directory
    if os.path.isfile(args.target_dir):
        files_to_scan = [(os.path.dirname(args.target_dir), [os.path.basename(args.target_dir)])]
    else:
        files_to_scan = []
        for root, dirs, files in os.walk(args.target_dir):
            dirs[:] = [d for d in dirs if d not in DEFAULT_EXCLUDES]
            files_to_scan.append((root, files))
    
    for root, files in files_to_scan:
        for file in files:
            if exts and not any(file.endswith(e) for e in exts):
                continue
            
            filepath = os.path.join(root, file)
            if os.path.getsize(filepath) > MAX_FILE_SIZE:
                continue
                
            scanned_files += 1
            
            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    content = f.read()
            except UnicodeDecodeError:
                continue
                
            if regex.search(content):
                file_count += 1
                new_content, count = regex.subn(args.replace_string, content)
                match_count += count
                
                rel_path = os.path.relpath(filepath, args.target_dir if os.path.isdir(args.target_dir) else os.path.dirname(args.target_dir))
                print(f"[WARN] Found {count} matches in {rel_path}")
                pending_writes.append((filepath, new_content))

    print(f"\\n[OK] Scan selesai ({scanned_files} file dipindai). Menemukan {match_count} kecocokan di {file_count} file.")
    
    # Calculate risk
    is_logic = False
    is_widespread = file_count > 3
    risk_level = "Low"
    
    if args.replace_string:
        logic_keywords = ['if', 'for', 'while', 'function', 'class', 'import', 'export', 'return']
        if any(kw in args.replace_string for kw in logic_keywords):
            is_logic = True
            
    if is_widespread and is_logic:
        risk_level = "High"
    elif is_widespread or is_logic:
        risk_level = "Medium"
        
    print(f"[RISK] {risk_level} (Widespread: {is_widespread}, Logic: {is_logic})")
    
    if not pending_writes:
        return
        
    if not (args.apply or args.apply_validated):
        print("\\n[DRY RUN] Ini hanya simulasi. Gunakan --apply untuk mengeksekusi.")
        if risk_level in ["Medium", "High"]:
            print(f"[BLOCKED] Karena risiko {risk_level}, Anda HARUS menggunakan --apply-validated setelah memastikan aman.")
        sys.exit(0)
        
    if risk_level in ["Medium", "High"] and not args.apply_validated:
        print(f"\\n[BLOCKED] Risiko modifikasi adalah {risk_level}.")
        print("Anda HARUS memvalidasi ulang (misal: cek linter/syntax) sebelum mengeksekusi.")
        print("Gunakan --apply-validated jika Anda sudah 100% yakin.")
        sys.exit(1)
        
    for filepath, new_content in pending_writes:
        backup_path = backup_file(filepath, backup_dir)
        with open(filepath, 'w', encoding='utf-8', newline='\\n') as f:
            f.write(new_content)
            
    print(f"\\n[SUCCESS] Berhasil memodifikasi {file_count} file. Backup tersimpan di {backup_dir}")

if __name__ == '__main__':
    main()
