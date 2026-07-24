import os
import re
import sys

if sys.stdout.encoding != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8')

if len(sys.argv) < 2:
    print("Usage: python sweeper.py <target_directory>")
    sys.exit(1)
target = sys.argv[1]

residue_files = []
todo_count = 0
comment_blocks = []

# Directories that are standard and not residues
ignore_dirs = {'node_modules', '.git', 'build', 'dist', 'uploads', 'public', '.vscode', '.history', 'quarantine', '.native_browser', '.exambro_android', '.plan', '.skills'}

for root, dirs, files in os.walk(target):
    dirs[:] = [d for d in dirs if d not in ignore_dirs]
    
    # Check for residue directories
    for d in dirs:
        if d.lower() in ['aa', 'arsip', 'temp', 'backup', 'old', 'scratch']:
            residue_files.append(os.path.join(root, d) + " [Suspected Backup/Temp Folder]")
            
    # Check for residue files
    for f in files:
        f_lower = f.lower()
        if f_lower.endswith(('.bak', '.old', '.log', '.db', '.sqlite', '.tmp')) or 'copy' in f_lower:
            # Exempt known necessary files
            if f_lower not in ['database.db'] and not f_lower.endswith('.test.js'):
                residue_files.append(os.path.join(root, f) + " [Suspected Leftover File]")
        
        # In this specific project, let's also flag the 'database.db' in root since it's a MySQL project
        if f == 'database.db' and root == target:
            residue_files.append(os.path.join(root, f) + " [Local SQLite DB in MySQL project]")
            
        # Scan code files for TODOs and large commented blocks
        if f_lower.endswith(('.js', '.jsx', '.php', '.html')):
            path = os.path.join(root, f)
            try:
                with open(path, 'r', encoding='utf-8') as file:
                    content = file.read()
                    todos = re.findall(r'(?i)\b(TODO|FIXME)\b', content)
                    todo_count += len(todos)
                    
                    # Check for large blocks of commented-out code (>= 7 consecutive lines)
                    lines = content.split('\n')
                    consecutive_comments = 0
                    for i, line in enumerate(lines):
                        if line.strip().startswith('//'):
                            consecutive_comments += 1
                        else:
                            if consecutive_comments >= 7:
                                comment_blocks.append(f"{path} (Lines {i-consecutive_comments+1}-{i}): {consecutive_comments} consecutive commented lines")
                            consecutive_comments = 0
            except Exception:
                pass

print(f"--- 🕵️ PYTHON RESIDUE SCANNER REPORT ---")
print(f"\n📂 Suspect Files/Folders ({len(residue_files)}):")
for r in residue_files:
    print(" -", r)

print(f"\n📝 TODO/FIXME tags found: {todo_count}")

print(f"\n🗑️ Large Commented Code Blocks ({len(comment_blocks)}):")
for c in comment_blocks[:15]: # Show top 15
    print(" -", c)
if len(comment_blocks) > 15:
    print(f"   ...and {len(comment_blocks)-15} more.")
