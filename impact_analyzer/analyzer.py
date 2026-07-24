import os
import sys
import re

if sys.stdout.encoding.lower() != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8')

def find_usages(project_root, target_name):
    """Scan all files to find which ones mention target_name"""
    usages = set()
    exclude_dirs = {'.git', 'node_modules', 'dist', 'build', '.agents', 'vendor', '.history'}
    
    pattern = re.compile(r'\b' + re.escape(target_name) + r'\b')
    
    for root, dirs, files in os.walk(project_root):
        dirs[:] = [d for d in dirs if d not in exclude_dirs]
        for file in files:
            if not file.endswith(('.js', '.jsx', '.ts', '.tsx', '.py', '.php')):
                continue
            
            filepath = os.path.join(root, file)
            try:
                with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
                    if pattern.search(content):
                        usages.add(filepath)
            except Exception:
                pass
    return usages

def main():
    if len(sys.argv) < 3:
        print("Usage: python analyzer.py <target_file_path> <project_root_dir>")
        sys.exit(1)
        
    target_path = sys.argv[1]
    project_root = sys.argv[2]
    
    if not os.path.exists(target_path):
        print(f"[ERROR] Target file not found: {target_path}")
        sys.exit(1)
        
    target_filename = os.path.basename(target_path)
    target_base, _ = os.path.splitext(target_filename)
    
    if target_base.lower() == 'index':
        # If it's an index file, the import is usually the folder name
        target_base = os.path.basename(os.path.dirname(target_path))
        
    print(f"🔍 Analyzing Impact for: {target_base}")
    print(f"📂 Project Root: {project_root}")
    print("-" * 50)
    
    # Level 1
    print("\n[Level 1] Direct Dependents (Files importing this):")
    level_1 = find_usages(project_root, target_base)
    level_1.discard(target_path) # Remove self
    
    if not level_1:
        print("  ✅ No dependents found. Safe to modify/delete.")
        sys.exit(0)
        
    for f in level_1:
        print(f"  - {os.path.relpath(f, project_root)}")
        
    # Level 2
    print("\n[Level 2] Indirect Dependents (Files importing Level 1):")
    level_2 = set()
    for l1_file in level_1:
        l1_base, _ = os.path.splitext(os.path.basename(l1_file))
        if l1_base.lower() == 'index':
            l1_base = os.path.basename(os.path.dirname(l1_file))
            
        usages = find_usages(project_root, l1_base)
        usages.discard(l1_file)
        usages.discard(target_path)
        level_2.update(usages)
        
    level_2 = level_2 - level_1
    if not level_2:
        print("  ✅ No Level 2 dependents found.")
    else:
        for f in level_2:
            print(f"  - {os.path.relpath(f, project_root)}")
            
    print("\n" + "=" * 50)
    print("💡 PROMPT UNTUK AI (Copy-Paste ini):")
    print(f"Saya ingin memodifikasi `{target_filename}`. Berdasarkan analisis dampak, ada {len(level_1)} file yang langsung bergantung padanya. Tolong buatkan rencana modifikasi yang aman agar file-file dependent tersebut tidak error.")

if __name__ == '__main__':
    main()
