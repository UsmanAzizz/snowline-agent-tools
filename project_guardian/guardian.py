import os
import re
import sys
import json
import subprocess
import argparse
import hashlib
import time

if sys.stdout.encoding != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8')

exclude_dirs = {'.git', 'node_modules', 'vendor', 'dist', 'build', 'quarantine', '.backup_replace', '.agents', '.history'}
js_py_exts = {'.js', '.jsx', '.ts', '.tsx', '.py'}
MAX_FILE_SIZE = 500 * 1024
target_dir = os.getcwd()

def get_dir_signature():
    mtimes = []
    for root, dirs, files in os.walk(target_dir):
        dirs[:] = [d for d in dirs if d not in exclude_dirs]
        for f in files:
            filepath = os.path.join(root, f)
            try:
                if os.path.getsize(filepath) <= MAX_FILE_SIZE:
                    mtimes.append(str(os.path.getmtime(filepath)))
            except Exception:
                pass
    return hashlib.md5("".join(sorted(mtimes)).encode()).hexdigest()

def scan_secrets():
    fails = []
    secret_patterns = [
        r'(?i)(password\s*[:=]\s*[\'"].+[\'"])',
        r'(?i)(api_key\s*[:=]\s*[\'"].+[\'"])',
        r'(?i)(secret\s*[:=]\s*[\'"].+[\'"])',
        r'(mongodb\+srv://.+)',
        r'(mysql://.+)',
        r'(Bearer\s+[A-Za-z0-9\-\._~+/]+=*)'
    ]
    compiled = [re.compile(p) for p in secret_patterns]
    for root, dirs, files in os.walk(target_dir):
        dirs[:] = [d for d in dirs if d not in exclude_dirs]
        for file in files:
            if file.startswith('.env'): continue
            filepath = os.path.join(root, file)
            if os.path.getsize(filepath) > MAX_FILE_SIZE: continue
            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    for line_num, line in enumerate(f, 1):
                        for pattern in compiled:
                            if pattern.search(line):
                                rel_path = os.path.relpath(filepath, target_dir)
                                fails.append(f"Potential credential leak in {rel_path} line {line_num}")
            except UnicodeDecodeError: pass
    return fails

def check_env_gitignore():
    fails = []
    warns = []
    gitignore_path = os.path.join(target_dir, '.gitignore')
    ignored = set()
    if os.path.exists(gitignore_path):
        with open(gitignore_path, 'r', encoding='utf-8') as f:
            ignored = set(line.strip() for line in f if line.strip() and not line.startswith('#'))
    
    for f in os.listdir(target_dir):
        if f.startswith('.env') and os.path.isfile(os.path.join(target_dir, f)) and f != '.env.example':
            if f not in ignored and f"/{f}" not in ignored and "*.env" not in ignored and ".env*" not in ignored:
                fails.append(f"File {f} is missing from .gitignore!")
    
    env_ex = os.path.join(target_dir, '.env.example')
    ex_keys = set()
    if os.path.exists(env_ex):
        with open(env_ex, 'r', encoding='utf-8') as f:
            for line in f:
                if '=' in line and not line.startswith('#'):
                    ex_keys.add(line.split('=')[0].strip())
                    
    used_keys = set()
    penv_pattern = re.compile(r'process\.env\.([A-Za-z0-9_]+)')
    for root, dirs, files in os.walk(target_dir):
        dirs[:] = [d for d in dirs if d not in exclude_dirs]
        for file in files:
            if not any(file.endswith(ext) for ext in js_py_exts): continue
            filepath = os.path.join(root, file)
            if os.path.getsize(filepath) > MAX_FILE_SIZE: continue
            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    for line in f:
                        for m in penv_pattern.findall(line): used_keys.add(m)
            except: pass
            
    for key in used_keys:
        if key not in ex_keys and key != 'NODE_ENV':
            warns.append(f"process.env.{key} is used, but missing from .env.example")
    return fails, warns

def check_physical_imports():
    warns = []
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
                            if match.startswith('.'):
                                dir_path = os.path.dirname(filepath)
                                target_p = os.path.normpath(os.path.join(dir_path, match))
                                found = False
                                for suffix in ['', '.js', '.jsx', '.ts', '.tsx', '/index.js', '/index.jsx']:
                                    if os.path.exists(target_p + suffix):
                                        found = True
                                        break
                                if not found:
                                    rel = os.path.relpath(filepath, target_dir)
                                    warns.append(f"Relative import '{match}' at {rel}:{line_num} does not exist physically!")
            except: pass
    return warns

def check_dependencies():
    warns = []
    fails = []
    pkg_path = os.path.join(target_dir, 'package.json')
    if not os.path.exists(pkg_path): return warns, fails
        
    try:
        with open(pkg_path, 'r', encoding='utf-8') as f:
            pkg = json.load(f)
    except: return warns, fails
        
    deps = list(pkg.get('dependencies', {}).keys())
    used = set()
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
                                if len(parts) > 1: pkg_name = f"{parts[0]}/{parts[1]}"
                            used.add(pkg_name)
            except: pass
            
    for dep in deps:
        if dep not in used and not dep.startswith('@vite') and not dep.startswith('@babel') and not dep.startswith('react'):
            warns.append(f"Package '{dep}' is installed but appears unused.")
            
    return warns, fails

def run_npm_audit():
    fails = []
    try:
        result = subprocess.run('npm audit --json', shell=True, capture_output=True, text=True, check=False, timeout=15)
        try:
            audit_data = json.loads(result.stdout)
            vulns = audit_data.get('metadata', {}).get('vulnerabilities', {})
            high = vulns.get('high', 0)
            critical = vulns.get('critical', 0)
            if high > 0 or critical > 0:
                fails.append(f"npm audit detected {high} HIGH and {critical} CRITICAL vulnerabilities!")
        except: pass
    except: pass
    return fails

def get_npm_audit_signature():
    pkg_lock = os.path.join(target_dir, 'package-lock.json')
    mtime = os.path.getmtime(pkg_lock) if os.path.exists(pkg_lock) else 0
    return f"{mtime}_{time.time() // 86400}"

def print_section(title, fails, warns, summary_mode):
    if not summary_mode:
        print(f"\n--- {title} ---")
        for f in fails: print(f"[FAIL] {f}")
        for w in warns: print(f"[WARN] {w}")

def main():
    parser = argparse.ArgumentParser(description="Project Guardian")
    parser.add_argument("--summary", action="store_true", help="Only show final score")
    args = parser.parse_args()
    
    global target_dir
    target_dir = os.path.abspath(os.getcwd())
    cache_file = os.path.join(target_dir, '.agents', 'session_cache.json')
    dir_sig = get_dir_signature()
    cache_key = f"guardian_{hashlib.md5(target_dir.encode()).hexdigest()}"
    audit_sig = get_npm_audit_signature()
    
    cache_data = {}
    if os.path.exists(cache_file):
        try:
            with open(cache_file, 'r', encoding='utf-8') as f: cache_data = json.load(f)
        except: pass
        
    cached_data = cache_data.get(cache_key, {})
    
    if cached_data.get('signature') == dir_sig:
        print("[INFO] Menggunakan hasil cache untuk scanning file (tidak ada file berubah)")
        sec_fails = cached_data.get('sec_fails', [])
        env_fails, env_warns = cached_data.get('env_fails', []), cached_data.get('env_warns', [])
        imp_warns = cached_data.get('imp_warns', [])
        dep_warns, dep_fails = cached_data.get('dep_warns', []), cached_data.get('dep_fails', [])
    else:
        sec_fails = scan_secrets()
        env_fails, env_warns = check_env_gitignore()
        imp_warns = check_physical_imports()
        dep_warns, dep_fails = check_dependencies()
        cached_data.update({
            'signature': dir_sig,
            'sec_fails': sec_fails, 'env_fails': env_fails, 'env_warns': env_warns,
            'imp_warns': imp_warns, 'dep_warns': dep_warns, 'dep_fails': dep_fails
        })
        
    if cached_data.get('audit_signature') == audit_sig:
        print("[INFO] Menggunakan hasil cache untuk npm audit (< 24 jam dan package-lock sama)")
        audit_fails = cached_data.get('audit_fails', [])
    else:
        if not args.summary: print("\nRunning npm audit (this may take a while)...")
        audit_fails = run_npm_audit()
        cached_data.update({
            'audit_signature': audit_sig,
            'audit_fails': audit_fails
        })
        
    cache_data[cache_key] = cached_data
    try:
        os.makedirs(os.path.dirname(cache_file), exist_ok=True)
        with open(cache_file, 'w', encoding='utf-8') as f: json.dump(cache_data, f, indent=2)
    except: pass
    
    if not args.summary: print("🛡️ PROJECT GUARDIAN AUDITOR 🛡️")
    
    print_section("MODULE 1: SECRET SCANNER", sec_fails, [], args.summary)
    print_section("MODULE 2: ENV & GITIGNORE VERIFIER", env_fails, env_warns, args.summary)
    print_section("MODULE 3: PHYSICAL IMPORT CHECKER", [], imp_warns, args.summary)
    
    all_dep_fails = dep_fails + audit_fails
    print_section("MODULE 4: DEPENDENCIES & UNUSED PACKAGES", all_dep_fails, dep_warns, args.summary)
    
    total_fails = len(sec_fails) + len(env_fails) + len(all_dep_fails)
    total_warns = len(env_warns) + len(imp_warns) + len(dep_warns)
    
    if args.summary:
        print(f"🛡️ RINGKASAN GUARDIAN: 🔴 {total_fails} FAIL | 🟡 {total_warns} WARN | 🟢 Sektor lainnya Aman.")
    else:
        print("\n" + "=" * 60)
        print(f"🛡️ RINGKASAN: 🔴 {total_fails} FAIL | 🟡 {total_warns} WARN | 🟢 Sektor lainnya Aman.")
        print("\n💡 PROMPT UNTUK AI (Copy-Paste ini):")
        print('"Tolong perbaiki semua temuan [FAIL] di atas (khususnya .gitignore dan env). Untuk [WARN], abaikan jika itu adalah dummy data atau file test."')

if __name__ == '__main__':
    main()
