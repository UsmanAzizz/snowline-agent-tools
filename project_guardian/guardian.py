import os
import re
import sys
import json
import subprocess
import argparse

if sys.stdout.encoding != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8')

exclude_dirs = {'.git', 'node_modules', 'vendor', 'dist', 'build', 'quarantine', '.backup_replace', '.agents', '.history'}
js_py_exts = {'.js', '.jsx', '.ts', '.tsx', '.py'}
MAX_FILE_SIZE = 500 * 1024

target_dir = os.getcwd()

total_fails = 0
total_warns = 0

def print_fail(msg, summary_mode):
    global total_fails
    total_fails += 1
    if not summary_mode:
        print(f"[FAIL] {msg}")

def print_warn(msg, summary_mode):
    global total_warns
    total_warns += 1
    if not summary_mode:
        print(f"[WARN] {msg}")

def print_info(msg, summary_mode):
    if not summary_mode:
        print(f"[INFO] {msg}")

def scan_secrets(summary_mode):
    if not summary_mode: print("\n--- MODULE 1: SECRET SCANNER ---")
    secret_patterns = [
        r'(?i)(password\s*[:=]\s*[\'"].+[\'"])',
        r'(?i)(api_key\s*[:=]\s*[\'"].+[\'"])',
        r'(?i)(secret\s*[:=]\s*[\'"].+[\'"])',
        r'(mongodb\+srv://.+)',
        r'(mysql://.+)',
        r'(Bearer\s+[A-Za-z0-9\-\._~+/]+=*)'
    ]
    compiled_patterns = [re.compile(p) for p in secret_patterns]
    
    for root, dirs, files in os.walk(target_dir):
        dirs[:] = [d for d in dirs if d not in exclude_dirs]
        for file in files:
            if file.startswith('.env'): continue
            filepath = os.path.join(root, file)
            if os.path.getsize(filepath) > MAX_FILE_SIZE: continue
            
            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    for line_num, line in enumerate(f, 1):
                        for pattern in compiled_patterns:
                            if pattern.search(line):
                                rel_path = os.path.relpath(filepath, target_dir)
                                print_fail(f"Potential credential leak in {rel_path} line {line_num}", summary_mode)
            except UnicodeDecodeError:
                pass

def check_env_gitignore(summary_mode):
    if not summary_mode: print("\n--- MODULE 2: ENV & GITIGNORE VERIFIER ---")
    gitignore_path = os.path.join(target_dir, '.gitignore')
    ignored_lines = set()
    if os.path.exists(gitignore_path):
        with open(gitignore_path, 'r', encoding='utf-8') as f:
            ignored_lines = set(line.strip() for line in f if line.strip() and not line.startswith('#'))
    
    env_files = [f for f in os.listdir(target_dir) if f.startswith('.env') and os.path.isfile(os.path.join(target_dir, f))]
    for env_file in env_files:
        if env_file == '.env.example': continue
        if env_file not in ignored_lines and f"/{env_file}" not in ignored_lines and "*.env" not in ignored_lines and ".env*" not in ignored_lines:
            print_fail(f"File {env_file} is missing from .gitignore!", summary_mode)
    
    env_example_path = os.path.join(target_dir, '.env.example')
    example_keys = set()
    if os.path.exists(env_example_path):
        with open(env_example_path, 'r', encoding='utf-8') as f:
            for line in f:
                if '=' in line and not line.startswith('#'):
                    key = line.split('=')[0].strip()
                    example_keys.add(key)
                    
    used_keys = set()
    process_env_pattern = re.compile(r'process\.env\.([A-Za-z0-9_]+)')
    for root, dirs, files in os.walk(target_dir):
        dirs[:] = [d for d in dirs if d not in exclude_dirs]
        for file in files:
            if not any(file.endswith(ext) for ext in js_py_exts): continue
            filepath = os.path.join(root, file)
            if os.path.getsize(filepath) > MAX_FILE_SIZE: continue
            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    for line in f:
                        for m in process_env_pattern.findall(line):
                            used_keys.add(m)
            except: pass
            
    for key in used_keys:
        if key not in example_keys and key != 'NODE_ENV':
            print_warn(f"process.env.{key} is used, but missing from .env.example", summary_mode)

def check_physical_imports(summary_mode):
    if not summary_mode: print("\n--- MODULE 3: PHYSICAL IMPORT CHECKER ---")
    import_pattern = re.compile(r'(?:import\s+.*?from\s+|require\()[\'"]([^\'"]+)[\'"]')
    for root, dirs, files in os.walk(target_dir):
        dirs[:] = [d for d in dirs if d not in exclude_dirs]
        for file in files:
            if not any(file.endswith(ext) for ext in js_py_exts): continue
            filepath = os.path.join(root, file)
            if os.path.getsize(filepath) > MAX_FILE_SIZE: continue
            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    for line_num, line in enumerate(f, 1):
                        for match in import_pattern.findall(line):
                            import_path = match
                            if import_path.startswith('.'):
                                dir_path = os.path.dirname(filepath)
                                target_p = os.path.normpath(os.path.join(dir_path, import_path))
                                found = False
                                for suffix in ['', '.js', '.jsx', '.ts', '.tsx', '/index.js', '/index.jsx']:
                                    if os.path.exists(target_p + suffix):
                                        found = True
                                        break
                                if not found:
                                    rel_source = os.path.relpath(filepath, target_dir)
                                    print_warn(f"Relative import '{import_path}' at {rel_source}:{line_num} does not exist physically!", summary_mode)
            except: pass

def check_dependencies(summary_mode):
    if not summary_mode: print("\n--- MODULE 4: DEPENDENCIES & UNUSED PACKAGES ---")
    package_json_path = os.path.join(target_dir, 'package.json')
    if not os.path.exists(package_json_path):
        return
        
    try:
        with open(package_json_path, 'r', encoding='utf-8') as f:
            pkg = json.load(f)
    except: return
        
    deps = list(pkg.get('dependencies', {}).keys())
    used_deps = set()
    import_pattern = re.compile(r'(?:import\s+.*?from\s+|require\()[\'"]([^\'"]+)[\'"]')
    
    for root, dirs, files in os.walk(target_dir):
        dirs[:] = [d for d in dirs if d not in exclude_dirs]
        for file in files:
            if not any(file.endswith(ext) for ext in js_py_exts): continue
            filepath = os.path.join(root, file)
            if os.path.getsize(filepath) > MAX_FILE_SIZE: continue
            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    for line in f:
                        for match in import_pattern.findall(line):
                            pkg_name = match.split('/')[0]
                            if pkg_name.startswith('@'):
                                parts = match.split('/')
                                if len(parts) > 1:
                                    pkg_name = f"{parts[0]}/{parts[1]}"
                            used_deps.add(pkg_name)
            except: pass
            
    for dep in deps:
        if dep not in used_deps and not dep.startswith('@vite') and not dep.startswith('@babel') and not dep.startswith('react'):
            print_warn(f"Package '{dep}' is installed but appears unused.", summary_mode)

    if not summary_mode: print("\nRunning npm audit (this may take a while)...")
    try:
        result = subprocess.run('npm audit --json', shell=True, capture_output=True, text=True, check=False, timeout=15)
        try:
            audit_data = json.loads(result.stdout)
            vulns = audit_data.get('metadata', {}).get('vulnerabilities', {})
            high = vulns.get('high', 0)
            critical = vulns.get('critical', 0)
            if high > 0 or critical > 0:
                print_fail(f"npm audit detected {high} HIGH and {critical} CRITICAL vulnerabilities!", summary_mode)
        except: pass
    except: pass

def main():
    parser = argparse.ArgumentParser(description="Project Guardian")
    parser.add_argument("--summary", action="store_true", help="Only show final score")
    args = parser.parse_args()

    if not args.summary:
        print("🛡️ PROJECT GUARDIAN AUDITOR 🛡️")
        
    scan_secrets(args.summary)
    check_env_gitignore(args.summary)
    check_physical_imports(args.summary)
    check_dependencies(args.summary)
    
    if args.summary:
        print(f"🛡️ RINGKASAN GUARDIAN: 🔴 {total_fails} FAIL | 🟡 {total_warns} WARN | 🟢 Sektor lainnya Aman.")
    else:
        print("\n" + "=" * 60)
        print(f"🛡️ RINGKASAN: 🔴 {total_fails} FAIL | 🟡 {total_warns} WARN | 🟢 Sektor lainnya Aman.")
        print("\n💡 PROMPT UNTUK AI (Copy-Paste ini):")
        print('"Tolong perbaiki semua temuan [FAIL] di atas (khususnya .gitignore dan env). Untuk [WARN], abaikan jika itu adalah dummy data atau file test."')

if __name__ == '__main__':
    main()
