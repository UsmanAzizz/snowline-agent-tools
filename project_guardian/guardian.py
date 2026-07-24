import os
import re
import sys
import json
import subprocess

if sys.stdout.encoding != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8')

print("🛡️ PROJECT GUARDIAN AUDITOR 🛡️\n")

target_dir = os.getcwd()

# Shared globals
exclude_dirs = {'.git', 'node_modules', 'vendor', 'dist', 'build', 'quarantine', '.backup_replace', '.agents', '.history'}
js_py_exts = {'.js', '.jsx', '.ts', '.tsx', '.py'}

def print_fail(msg):
    print(f"[FAIL] {msg}")

def print_warn(msg):
    print(f"[WARN] {msg}")

def print_info(msg):
    print(f"[INFO] {msg}")

# --- MODULE 1: SECRET SCANNER ---
def scan_secrets():
    print("--- MODUL 1: SECRET SCANNER ---")
    secret_patterns = [
        r'(?i)(password\s*[:=]\s*[\'"].+[\'"])',
        r'(?i)(api_key\s*[:=]\s*[\'"].+[\'"])',
        r'(?i)(secret\s*[:=]\s*[\'"].+[\'"])',
        r'(mongodb\+srv://.+)',
        r'(mysql://.+)',
        r'(Bearer\s+[A-Za-z0-9\-\._~+/]+=*)'
    ]
    compiled_patterns = [re.compile(p) for p in secret_patterns]
    found = False

    for root, dirs, files in os.walk(target_dir):
        dirs[:] = [d for d in dirs if d not in exclude_dirs]
        for file in files:
            if file.startswith('.env'): continue
            
            filepath = os.path.join(root, file)
            # Skip massive files
            if os.path.getsize(filepath) > 1024 * 500: continue
            
            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    for line_num, line in enumerate(f, 1):
                        for pattern in compiled_patterns:
                            if pattern.search(line):
                                rel_path = os.path.relpath(filepath, target_dir)
                                print_fail(f"Potensi credential bocor di {rel_path} baris {line_num}")
                                found = True
            except UnicodeDecodeError:
                pass
    if not found:
        print("[OK] Tidak ada hardcoded credential ditemukan.")

# --- MODULE 2: ENV & GITIGNORE ---
def check_env_gitignore():
    print("\n--- MODUL 2: ENV & GITIGNORE VERIFIER ---")
    
    # Check .env files in gitignore
    gitignore_path = os.path.join(target_dir, '.gitignore')
    ignored_lines = set()
    if os.path.exists(gitignore_path):
        with open(gitignore_path, 'r', encoding='utf-8') as f:
            ignored_lines = set(line.strip() for line in f if line.strip() and not line.startswith('#'))
    
    env_files = [f for f in os.listdir(target_dir) if f.startswith('.env') and os.path.isfile(os.path.join(target_dir, f))]
    
    for env_file in env_files:
        if env_file == '.env.example': continue
        if env_file not in ignored_lines and f"/{env_file}" not in ignored_lines and "*.env" not in ignored_lines and ".env*" not in ignored_lines:
            print_fail(f"File {env_file} tidak ada di .gitignore!")
    
    # Parity check .env.example vs process.env
    env_example_path = os.path.join(target_dir, '.env.example')
    example_keys = set()
    if os.path.exists(env_example_path):
        with open(env_example_path, 'r', encoding='utf-8') as f:
            for line in f:
                if '=' in line and not line.startswith('#'):
                    key = line.split('=')[0].strip()
                    example_keys.add(key)
                    
    # Find all process.env.X
    used_keys = set()
    process_env_pattern = re.compile(r'process\.env\.([A-Za-z0-9_]+)')
    for root, dirs, files in os.walk(target_dir):
        dirs[:] = [d for d in dirs if d not in exclude_dirs]
        for file in files:
            if not any(file.endswith(ext) for ext in js_py_exts): continue
            filepath = os.path.join(root, file)
            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    for line in f:
                        matches = process_env_pattern.findall(line)
                        for m in matches:
                            used_keys.add(m)
            except: pass
            
    for key in used_keys:
        if key not in example_keys and key != 'NODE_ENV':
            print_warn(f"Variabel process.env.{key} dipakai, tapi tidak didokumentasikan di .env.example")

# --- MODULE 3: PHYSICAL IMPORT CHECKER ---
def check_physical_imports():
    print("\n--- MODUL 3: PHYSICAL IMPORT CHECKER ---")
    import_pattern = re.compile(r'(?:import\s+.*?from\s+|require\()[\'"]([^\'"]+)[\'"]')
    
    warn_count = 0
    info_count = 0
    for root, dirs, files in os.walk(target_dir):
        dirs[:] = [d for d in dirs if d not in exclude_dirs]
        for file in files:
            if not any(file.endswith(ext) for ext in js_py_exts): continue
            filepath = os.path.join(root, file)
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
                                    print_warn(f"Import relative '{import_path}' di {rel_source}:{line_num} tidak ditemukan fisik!")
                                    warn_count += 1
                            elif import_path.startswith('@/') or import_path.startswith('~'):
                                info_count += 1
            except: pass
    if warn_count == 0:
        print("[OK] Semua relative import valid.")
    print(f"[INFO] {info_count} import path dengan alias tidak diverifikasi secara fisik.")

# --- MODULE 4: DEPENDENCY & UNUSED PACKAGES ---
def check_dependencies():
    print("\n--- MODUL 4: DEPENDENCIES & UNUSED PACKAGES ---")
    package_json_path = os.path.join(target_dir, 'package.json')
    if not os.path.exists(package_json_path):
        print("[INFO] Tidak ditemukan package.json. Melewati modul dependency.")
        return
        
    try:
        with open(package_json_path, 'r', encoding='utf-8') as f:
            pkg = json.load(f)
    except:
        print_fail("Gagal membaca package.json")
        return
        
    deps = list(pkg.get('dependencies', {}).keys())
    
    used_deps = set()
    import_pattern = re.compile(r'(?:import\s+.*?from\s+|require\()[\'"]([^\'"]+)[\'"]')
    
    for root, dirs, files in os.walk(target_dir):
        dirs[:] = [d for d in dirs if d not in exclude_dirs]
        for file in files:
            if not any(file.endswith(ext) for ext in js_py_exts): continue
            filepath = os.path.join(root, file)
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
            
    unused_count = 0
    for dep in deps:
        if dep not in used_deps and not dep.startswith('@vite') and not dep.startswith('@babel') and not dep.startswith('react'):
            print_warn(f"Package '{dep}' terinstal tapi mungkin tidak pernah di-import (Unused Package).")
            unused_count += 1
    if unused_count == 0:
        print("[OK] Semua dependencies tampak digunakan.")

    print("\nMenjalankan npm audit (mungkin memakan waktu)...")
    try:
        # Run npm audit using shell=True for windows compatibility
        result = subprocess.run('npm audit --json', shell=True, capture_output=True, text=True, check=False, timeout=15)
        try:
            audit_data = json.loads(result.stdout)
            vulns = audit_data.get('metadata', {}).get('vulnerabilities', {})
            high = vulns.get('high', 0)
            critical = vulns.get('critical', 0)
            if high > 0 or critical > 0:
                print_fail(f"npm audit mendeteksi {high} HIGH dan {critical} CRITICAL vulnerabilities!")
            else:
                print("[OK] Tidak ada vulnerability tingkat High/Critical.")
        except:
            print_warn("Gagal mem-parsing output JSON dari npm audit.")
    except Exception as e:
        print_warn(f"Gagal mengeksekusi npm audit: {e}")

if __name__ == '__main__':
    scan_secrets()
    check_env_gitignore()
    check_physical_imports()
    check_dependencies()
    print("\n🛡️ AUDIT SELESAI 🛡️")
