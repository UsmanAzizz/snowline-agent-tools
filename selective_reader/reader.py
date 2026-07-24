import os
import sys
import re

MAX_FILE_SIZE = 500 * 1024 # 500 KB

def parse_js(content):
    # Heuristics for JS/TS functions and classes
    toc = []
    # Match class Name {
    class_pattern = re.compile(r'^\s*(?:export\s+)?(?:default\s+)?class\s+([A-Za-z0-9_]+)', re.MULTILINE)
    # Match function name(
    func_pattern = re.compile(r'^\s*(?:export\s+)?(?:default\s+)?(?:async\s+)?function\s+([A-Za-z0-9_]+)', re.MULTILINE)
    # Match const name = (args) =>
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

def main():
    if len(sys.argv) < 2:
        print("[FAIL] Penggunaan: python reader.py <absolute_path_to_file>")
        sys.exit(1)
        
    filepath = sys.argv[1]
    if not os.path.exists(filepath):
        print(f"[FAIL] File tidak ditemukan: {filepath}")
        sys.exit(1)
        
    if os.path.getsize(filepath) > MAX_FILE_SIZE:
        print(f"[FAIL] File terlalu besar (>500KB): {filepath}")
        sys.exit(1)
        
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
    except Exception as e:
        print(f"[FAIL] Gagal membaca file: {e}")
        sys.exit(1)
        
    print(f"📄 TABLE OF CONTENTS: {os.path.basename(filepath)}")
    print("-" * 50)
    
    toc = parse_js(content)
    if not toc:
        print("[INFO] Tidak ditemukan deklarasi class atau fungsi utama.")
    else:
        for line, desc in toc:
            print(f"Baris {line:<5}: {desc}")
            
    print("-" * 50)
    print("\n💡 PROMPT UNTUK AI (Copy-Paste ini):")
    print(f'"Berdasarkan TOC di atas, tolong gunakan tool view_file untuk membaca hanya baris yang relevan dari fungsi yang bermasalah di file {os.path.basename(filepath)}."')

if __name__ == '__main__':
    main()
