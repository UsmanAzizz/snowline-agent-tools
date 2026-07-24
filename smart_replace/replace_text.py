import os
import sys
import argparse
import subprocess
import re
from datetime import datetime
import shutil

RG_PATH = "rg"
DEFAULT_EXCLUDES = ['node_modules', '.git', '.history', 'vendor', 'dist', 'build', 'quarantine']

def get_args():
    parser = argparse.ArgumentParser(description="Safe Text Replacer with Ripgrep and Python")
    parser.add_argument("target_dir", help="Target directory (absolute path)")
    parser.add_argument("search_string", help="String or pattern to search for")
    parser.add_argument("replace_string", help="String to replace with")
    
    parser.add_argument("--ext", help="Comma-separated extensions to include (e.g. .js,.jsx)", default="")
    parser.add_argument("--regex", action="store_true", help="Treat search_string as a regular expression")
    parser.add_argument("--whole-word", action="store_true", help="Match whole words only (default true if not --regex)", default=None)
    parser.add_argument("--apply", action="store_true", help="Actually modify the files. If omitted, performs a DRY RUN.")
    parser.add_argument("--exclude", help="Comma-separated additional folders to exclude", default="")
    
    return parser.parse_args()

def run_rg(target_dir, search_string, ext, is_regex, whole_word, extra_excludes):
    if not os.path.exists(RG_PATH):
        print(f"[ERROR] ripgrep not found at {RG_PATH}. Please install or check path.")
        sys.exit(1)
        
    cmd = [RG_PATH, '-l', '--hidden'] # -l prints only file paths with matches
    
    # Excludes
    excludes = DEFAULT_EXCLUDES.copy()
    if extra_excludes:
        excludes.extend([x.strip() for x in extra_excludes.split(',')])
        
    for ex in excludes:
        cmd.extend(['-g', f'!{ex}/**'])
        
    # Extensions
    if ext:
        exts = [e.strip() if e.strip().startswith('.') else f".{e.strip()}" for e in ext.split(',')]
        for e in exts:
            cmd.extend(['-g', f'*{e}'])
            
    # Whole word
    if whole_word:
        cmd.append('-w')
        
    # Fixed string vs regex
    if not is_regex:
        cmd.append('-F')
        
    cmd.append(search_string)
    cmd.append(target_dir)
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, check=False)
        if result.returncode == 0:
            return [line for line in result.stdout.splitlines() if line.strip()]
        elif result.returncode == 1:
            return [] # No matches found
        else:
            print(f"[ERROR] rg failed: {result.stderr}")
            sys.exit(1)
    except Exception as e:
        print(f"[ERROR] Failed to run rg: {e}")
        sys.exit(1)

def backup_file(filepath, target_dir):
    rel_path = os.path.relpath(filepath, target_dir)
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    backup_dir_root = os.path.join(target_dir, '.backup_replace', timestamp)
    
    backup_filepath = os.path.join(backup_dir_root, rel_path)
    os.makedirs(os.path.dirname(backup_filepath), exist_ok=True)
    
    shutil.copy2(filepath, backup_filepath)
    return backup_filepath

def main():
    args = get_args()
    
    if shutil.which(RG_PATH) is None:
        print("Error: ripgrep (rg) tidak ditemukan di system PATH Anda.")
        print("Silakan install ripgrep terlebih dahulu dari https://github.com/BurntSushi/ripgrep")
        print("Atau sesuaikan variabel RG_PATH di dalam script ini jika rg terinstall di lokasi lain.")
        sys.exit(1)
    
    if args.whole_word is None:
        args.whole_word = not args.regex
        
    print(f"\n{'='*50}")
    print(f" SMART REPLACE UTILITY")
    print(f" Mode: {'EXECUTE (--apply)' if args.apply else 'PREVIEW (Dry Run)'}")
    print(f" Target: {args.target_dir}")
    print(f" Search: '{args.search_string}'")
    print(f" Replace: '{args.replace_string}'")
    print(f"{'='*50}\n")
    
    # 1. Find files using RG
    matched_files = run_rg(args.target_dir, args.search_string, args.ext, args.regex, args.whole_word, args.exclude)
    
    if not matched_files:
        print("No matching files found. Exiting.")
        sys.exit(0)
        
    print(f"Found {len(matched_files)} files containing matches. Processing...\n")
    
    # 2. Compile python regex for local replacement
    if args.regex:
        pattern_str = args.search_string
    else:
        pattern_str = re.escape(args.search_string)
        
    if args.whole_word:
        pattern_str = rf"\b{pattern_str}\b"
        
    pattern = re.compile(pattern_str)
    
    total_occurrences = 0
    files_changed = 0
    
    for filepath in matched_files:
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                lines = f.readlines()
        except UnicodeDecodeError:
            print(f"[SKIPPED] Cannot read {filepath} (non-utf8)")
            continue
            
        new_lines = []
        file_occurrences = 0
        changed = False
        
        preview_buffer = []
        
        for i, line in enumerate(lines):
            new_line, subs = pattern.subn(args.replace_string, line)
            new_lines.append(new_line)
            
            if subs > 0:
                changed = True
                file_occurrences += subs
                preview_buffer.append(f"  Line {i+1}: - {line.strip()}")
                preview_buffer.append(f"          + {new_line.strip()}")
                
        if changed:
            files_changed += 1
            total_occurrences += file_occurrences
            print(f"\n[FILE] {os.path.relpath(filepath, args.target_dir)}")
            print('\n'.join(preview_buffer))
            
            if args.apply:
                backup_path = backup_file(filepath, args.target_dir)
                with open(filepath, 'w', encoding='utf-8') as f:
                    f.writelines(new_lines)
                print(f"  [OK] Updated. Backup: {os.path.relpath(backup_path, args.target_dir)}")
                
    print(f"\n{'='*50}")
    print(f" SUMMARY")
    print(f" Files modified: {files_changed} out of {len(matched_files)} matched files")
    print(f" Total replacements: {total_occurrences}")
    if not args.apply:
        print(f" *** THIS WAS A DRY RUN. NO FILES WERE MODIFIED. ***")
        print(f" Run with --apply to execute changes.")
    print(f"{'='*50}\n")

if __name__ == '__main__':
    main()
