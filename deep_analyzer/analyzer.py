import os
import sys
import json

if sys.stdout.encoding != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8')

def analyze_project(target_dir):
    print("\n🔬 DEEP ANALYZER: Project Profiler 🔬")
    print("=" * 60)
    
    # 1. Tech Stack Detection
    stack = []
    if os.path.exists(os.path.join(target_dir, 'package.json')):
        stack.append("Node.js")
    if os.path.exists(os.path.join(target_dir, 'requirements.txt')) or os.path.exists(os.path.join(target_dir, 'Pipfile')):
        stack.append("Python")
    if os.path.exists(os.path.join(target_dir, 'vite.config.js')) or os.path.exists(os.path.join(target_dir, 'vite.config.ts')):
        stack.append("Vite (React/Vue)")
    if os.path.exists(os.path.join(target_dir, 'next.config.js')):
        stack.append("Next.js")
    if os.path.exists(os.path.join(target_dir, 'composer.json')):
        stack.append("PHP/Laravel")
        
    stack_str = ", ".join(stack) if stack else "Unknown (Vanilla/Other)"
    print(f"[{'OK' if stack else 'WARN'}] Tech Stack Detected: {stack_str}")
    
    # 2. Package.json Parsing (Commands & Deps)
    pkg_path = os.path.join(target_dir, 'package.json')
    if os.path.exists(pkg_path):
        try:
            with open(pkg_path, 'r', encoding='utf-8') as f:
                pkg = json.load(f)
                
            scripts = pkg.get('scripts', {})
            if scripts:
                print("\n[INFO] Available npm/yarn Commands:")
                for name, cmd in scripts.items():
                    print(f"  - npm run {name:<12} : {cmd}")
            else:
                print("\n[WARN] No scripts found in package.json")
                
            deps = pkg.get('dependencies', {})
            dev_deps = pkg.get('devDependencies', {})
            print(f"\n[INFO] Core Dependencies: {len(deps)} runtime, {len(dev_deps)} dev")
            # Print top 5 dependencies just for context
            top_deps = list(deps.keys())[:5]
            if top_deps:
                print(f"  - Key libraries: {', '.join(top_deps)}...")
                
        except Exception as e:
            print(f"[FAIL] Could not parse package.json: {e}")
            
    # 3. Quick Directory Stats
    print("\n[INFO] Directory Statistics:")
    ignore_dirs = {'.git', 'node_modules', 'vendor', 'dist', 'build', '.history'}
    file_counts = {'.js': 0, '.jsx': 0, '.ts': 0, '.tsx': 0, '.py': 0, '.php': 0, '.html': 0, '.css': 0}
    total_files = 0
    total_size = 0
    
    for root, dirs, files in os.walk(target_dir):
        dirs[:] = [d for d in dirs if d not in ignore_dirs]
        for file in files:
            total_files += 1
            filepath = os.path.join(root, file)
            try:
                total_size += os.path.getsize(filepath)
            except: pass
            
            ext = os.path.splitext(file)[1].lower()
            if ext in file_counts:
                file_counts[ext] += 1
                
    mb_size = total_size / (1024 * 1024)
    print(f"  - Total Scanned Files: {total_files} ({mb_size:.2f} MB)")
    
    active_exts = {k: v for k, v in file_counts.items() if v > 0}
    ext_str = ", ".join([f"{k} ({v})" for k, v in active_exts.items()])
    if ext_str:
        print(f"  - Source Files: {ext_str}")

def main():
    target = sys.argv[1] if len(sys.argv) > 1 else os.getcwd()
    
    if not os.path.isdir(target):
        print(f"[FAIL] Target is not a directory: {target}")
        sys.exit(1)
        
    analyze_project(target)
    
    print("\n" + "=" * 60)
    print("[OK] Analisis proyek selesai dengan cepat tanpa membebani token.")
    print("\n💡 PROMPT UNTUK AI (Copy-Paste ini):")
    print('"Berdasarkan hasil Deep Analyzer di atas, gunakan perintah npm/test yang tersedia jika Anda perlu memvalidasi bug, atau gunakan alat lain untuk menyelidiki file spesifik."')

if __name__ == "__main__":
    main()
