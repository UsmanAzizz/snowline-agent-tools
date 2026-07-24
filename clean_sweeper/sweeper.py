import os
import re
import sys

if sys.stdout.encoding != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8')

MAX_FILE_SIZE = 500 * 1024 # 500 KB
ignore_dirs = {'node_modules', '.git', 'build', 'dist', 'uploads', 'public', '.vscode', '.history', 'quarantine', '.native_browser', '.exambro_android', '.plan', '.skills', '.backup_replace', '.agents'}

def sweep(target):
    residue_files = []
    todo_count = 0
    comment_blocks = []
    scanned_files = 0
    
    for root, dirs, files in os.walk(target):
        dirs[:] = [d for d in dirs if d not in ignore_dirs]
        
        # Check for residue directories
        for d in dirs:
            if d.lower() in ['aa', 'arsip', 'temp', 'backup', 'old', 'scratch']:
                residue_files.append(os.path.join(root, d) + " [Suspected Backup/Temp Folder]")
                
        # Check for residue files
        for f in files:
            filepath = os.path.join(root, f)
            if os.path.getsize(filepath) > MAX_FILE_SIZE:
                continue
                
            scanned_files += 1
            f_lower = f.lower()
            if f_lower.endswith(('.bak', '.old', '.log', '.db', '.sqlite', '.tmp')) or 'copy' in f_lower:
                if f_lower not in ['database.db'] and not f_lower.endswith('.test.js'):
                    residue_files.append(filepath + " [Suspected Leftover File]")
            
            if f == 'database.db' and root == target:
                residue_files.append(filepath + " [Local SQLite DB in MySQL project]")
                
            if f_lower.endswith(('.js', '.jsx', '.php', '.html', '.py')):
                try:
                    with open(filepath, 'r', encoding='utf-8') as file:
                        content = file.read()
                        todos = re.findall(r'(?i)\b(TODO|FIXME)\b', content)
                        todo_count += len(todos)
                        
                        lines = content.split('\n')
                        consecutive_comments = 0
                        for i, line in enumerate(lines):
                            if line.strip().startswith(('//', '#')):
                                consecutive_comments += 1
                            else:
                                if consecutive_comments >= 7:
                                    comment_blocks.append(f"{filepath} (Lines {i-consecutive_comments+1}-{i}): {consecutive_comments} consecutive commented lines")
                                consecutive_comments = 0
                except Exception:
                    pass
                    
    return residue_files, todo_count, comment_blocks, scanned_files

def main():
    if len(sys.argv) < 2:
        print("[FAIL] Usage: python sweeper.py <target_directory>")
        sys.exit(1)
    
    target = sys.argv[1]
    residue_files, todo_count, comment_blocks, scanned_files = sweep(target)
    
    print("🧹 CLEAN SWEEPER REPORT")
    print("=" * 50)
    
    total_issues = 0
    if residue_files:
        for r in residue_files:
            rel = os.path.relpath(r.split(" [")[0], target)
            print(f"[FAIL] {rel} " + r[r.index('['):])
            total_issues += 1
            
    if todo_count > 0:
        print(f"[WARN] Ditemukan {todo_count} tag TODO/FIXME di dalam kode.")
        total_issues += 1
        
    if comment_blocks:
        for c in comment_blocks:
            path_part, desc = c.split(" (", 1)
            rel = os.path.relpath(path_part, target)
            print(f"[WARN] {rel} ({desc}")
            total_issues += 1
            
    print("\n" + "=" * 50)
    
    if total_issues == 0:
        print(f"[OK] Proyek bersih! {scanned_files} file dipindai tanpa ada temuan residu.")
    else:
        print(f"[OK] Selesai memindai {scanned_files} file.")
        print("\n💡 PROMPT UNTUK AI (Copy-Paste ini):")
        print('"Berdasarkan laporan Clean Sweeper di atas, tolong periksa temuan [FAIL] dan hapus file yatim piatu tersebut. Untuk temuan [WARN], periksa apakah komentar raksasa itu bisa dihapus."')

if __name__ == "__main__":
    main()
