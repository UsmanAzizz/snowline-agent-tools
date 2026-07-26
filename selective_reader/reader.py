import os
import sys
import re
import json
import hashlib

if sys.stdout.encoding != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8')

MAX_FILE_SIZE = 500 * 1024 # 500 KB

def parse_js(content):
    toc = []
    class_pattern = re.compile(r'^\s*(?:export\s+)?(?:default\s+)?class\s+([A-Za-z0-9_]+)', re.MULTILINE)
    func_pattern = re.compile(r'^\s*(?:export\s+)?(?:default\s+)?(?:async\s+)?function\s+([A-Za-z0-9_]+)', re.MULTILINE)
    arrow_pattern = re.compile(r'^\s*(?:export\s+)?const\s+([A-Za-z0-9_]+)\s*=\s*(?:async\s+)?(?:\([^)]*\)|[A-Za-z0-9_]+)\s*=>', re.MULTILINE)
    
    for match in class_pattern.finditer(content):
        line = content.count('\n', 0, match.start()) + 1
        toc.append((line, f"Class: {match.group(1)}"))
        
    for match in func_pattern.finditer(content):
        line = content.count('\n', 0, match.start()) + 1
        toc.append((line, f"Function: {match.group(1)}"))
        
    for match in arrow_pattern.finditer(content):
        line = content.count('\n', 0, match.start()) + 1
        toc.append((line, f"Arrow Function: {match.group(1)}"))
        
    toc.sort(key=lambda x: x[0])
    return toc

def get_project_root(start_path):
    current = os.path.abspath(start_path)
    while True:
        if os.path.exists(os.path.join(current, 'package.json')) or os.path.exists(os.path.join(current, '.git')):
            return current
        parent = os.path.dirname(current)
        if parent == current:
            return os.path.abspath(start_path)
        current = parent

def load_cache(cache_file):
    if os.path.exists(cache_file):
        try:
            with open(cache_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception:
            pass
    return {}

def save_cache(cache_file, data):
    try:
        os.makedirs(os.path.dirname(cache_file), exist_ok=True)
        with open(cache_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2)
    except Exception:
        pass

def main():
    if len(sys.argv) < 2:
        print("[FAIL] Usage: python reader.py <absolute_path_to_file>")
        sys.exit(1)
        
    filepath = sys.argv[1]
    if not os.path.exists(filepath):
        print(f"[FAIL] File not found: {filepath}")
        sys.exit(1)
        
    if os.path.getsize(filepath) > MAX_FILE_SIZE:
        print(f"[FAIL] File too large (>500KB): {filepath}")
        sys.exit(1)
        
    project_root = get_project_root(filepath)
    cache_file = os.path.join(project_root, '.agents', 'session_cache.json')
    cache_data = load_cache(cache_file)
    
    file_mtime = str(os.path.getmtime(filepath))
    cache_key = f"reader_{hashlib.md5(filepath.encode()).hexdigest()}"
    
    if cache_key in cache_data:
        cached_entry = cache_data[cache_key]
        if cached_entry.get('mtime') == file_mtime and cached_entry.get('file') == filepath:
            print(f"[INFO] Menggunakan hasil cache dari session_cache.json (file belum berubah)")
            print(f"📄 TABLE OF CONTENTS: {os.path.basename(filepath)}")
            print("-" * 50)
            if not cached_entry['toc']:
                print("[INFO] No primary class or function declarations found.")
            else:
                for line, desc in cached_entry['toc']:
                    print(f"Line {line:<5}: {desc}")
            print("-" * 50)
            print("\n💡 PROMPT UNTUK AI (Copy-Paste ini):")
            print(f'"Berdasarkan TOC di atas, tolong gunakan tool view_file untuk membaca hanya baris yang relevan dari fungsi yang bermasalah di file {os.path.basename(filepath)}."')
            sys.exit(0)
            
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
    except Exception as e:
        print(f"[FAIL] Failed to read file: {e}")
        sys.exit(1)
        
    print(f"📄 TABLE OF CONTENTS: {os.path.basename(filepath)}")
    print("-" * 50)
    
    toc = parse_js(content)
    if not toc:
        print("[INFO] No primary class or function declarations found.")
    else:
        for line, desc in toc:
            print(f"Line {line:<5}: {desc}")
            
    cache_data[cache_key] = {
        'file': filepath,
        'mtime': file_mtime,
        'toc': toc
    }
    save_cache(cache_file, cache_data)
            
    print("-" * 50)
    print("\n💡 PROMPT UNTUK AI (Copy-Paste ini):")
    print(f'"Berdasarkan TOC di atas, tolong gunakan tool view_file untuk membaca hanya baris yang relevan dari fungsi yang bermasalah di file {os.path.basename(filepath)}."')

if __name__ == '__main__':
    main()
