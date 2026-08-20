import sys
import os
import re

if sys.stdout.encoding != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8')

def check_plan(filepath):
    if not os.path.exists(filepath):
        print(f"[ERROR] Plan file not found: {filepath}")
        sys.exit(1)
        
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.readlines()
        
    unfinished_tasks = []
    
    # Regex to find unchecked markdown checkboxes, e.g. "- [ ] Task" or "* [ ] Task"
    # It allows for leading whitespace.
    unchecked_pattern = re.compile(r'^\s*[-*]\s*\[\s*\]\s+(.*)')
    
    for i, line in enumerate(content):
        match = unchecked_pattern.match(line)
        if match:
            unfinished_tasks.append((i+1, match.group(1).strip()))
            
    if unfinished_tasks:
        print("[BLOCKED] Plan Tracker Guard: Transisi ke status DONE DITOLAK!")
        print("Ditemukan kotak centang yang belum diselesaikan (unfinished tasks):")
        for line_num, task in unfinished_tasks:
            print(f"  - Baris {line_num}: {task}")
        print("\nSelesaikan atau centang ([x]) semua tugas sebelum menutup plan ini.")
        sys.exit(1)
        
    print("[OK] Semua tugas di plan sudah dicentang. Lanjutkan eksekusi.")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python tracker_guard.py <path_to_plan.md>")
        sys.exit(1)
        
    check_plan(sys.argv[1])
