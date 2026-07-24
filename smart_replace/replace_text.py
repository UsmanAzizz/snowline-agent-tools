import os
import sys
import argparse
import re
import shutil
from datetime import datetime

DEFAULT_EXCLUDES = {'.git', 'node_modules', '.history', 'vendor', 'dist', 'build', 'quarantine', '.backup_replace', '.agents'}
MAX_FILE_SIZE = 500 * 1024 # 500 KB

def get_args():
    parser = argparse.ArgumentParser(description="Smart Replace (Pure Python Edition)")
    parser.add_argument("target_dir", help="Target directory (absolute path)")
    parser.add_argument("search_string", help="String or pattern to search for")
    parser.add_argument("replace_string", help="String to replace with")
    parser.add_argument("--ext", help="Comma-separated extensions to include (e.g. .js,.jsx)", default="")
    parser.add_argument("--regex", action="store_true", help="Treat search_string as a regular expression")
    parser.add_argument("--whole-word", action="store_true", help="Match whole words only")
    parser.add_argument("--apply", action="store_true", help="Actually modify the files")
    return parser.parse_args()

def backup_file(filepath, backup_dir):
    rel_path = os.path.relpath(filepath, os.getcwd())
    backup_path = os.path.join(backup_dir, rel_path)
    os.makedirs(os.path.dirname(backup_path), exist_ok=True)
    shutil.copy2(filepath, backup_path)
    return backup_path

def main():
    args = get_args()
    
    if not os.path.exists(args.target_dir):
        print(f"[FAIL] Target directory not found: {args.target_dir}")
        sys.exit(1)
        
    exts = [e.strip() for e in args.ext.split(',')] if args.ext else []
    
    pattern_str = args.search_string
    if not args.regex:
        pattern_str = re.escape(pattern_str)
    if args.whole_word:
        pattern_str = r'\b' + pattern_str + r'\b'
        
    try:
        regex = re.compile(pattern_str)
    except re.error as e:
        print(f"[FAIL] Invalid regex: {e}")
        sys.exit(1)
        
    backup_dir = None
    if args.apply:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_dir = os.path.join(args.target_dir, '.backup_replace', timestamp)

    match_count = 0
    file_count = 0
    scanned_files = 0
    
    for root, dirs, files in os.walk(args.target_dir):
        dirs[:] = [d for d in dirs if d not in DEFAULT_EXCLUDES]
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
                
                rel_path = os.path.relpath(filepath, args.target_dir)
                print(f"[WARN] Found {count} matches in {rel_path}")
                
                if args.apply:
                    backup_file(filepath, backup_dir)
                    with open(filepath, 'w', encoding='utf-8') as f:
                        f.write(new_content)

    print(f"\n[OK] Scan selesai ({scanned_files} file dipindai). Menemukan {match_count} kecocokan di {file_count} file.")
    if not args.apply:
        print("\n💡 PROMPT UNTUK AI (Copy-Paste ini):")
        print('"Berdasarkan hasil dry-run di atas, tolong jalankan ulang perintah tersebut dengan menambahkan flag --apply untuk menerapkan perubahannya secara aman."')
    else:
        print(f"\n[INFO] Perubahan telah diterapkan ke {file_count} file. Backup tersimpan di: {backup_dir}")

if __name__ == "__main__":
    main()
