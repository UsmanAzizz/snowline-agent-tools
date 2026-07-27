import sys
if sys.stdout.encoding != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8')
import os
import subprocess

def extract_risk(text):
    if not text: return 1
    risk_val = 1
    for line in text.split('\n'):
        if '[RISK]' in line or 'Risk Label' in line:
            if 'High' in line: risk_val = max(risk_val, 3)
            elif 'Medium' in line: risk_val = max(risk_val, 2)
            elif 'Low' in line: risk_val = max(risk_val, 1)
    return risk_val

def main():
    if len(sys.argv) < 2:
        print("Usage: python snowline_run.py <command> [args...]")
        sys.exit(1)

    command = sys.argv[1]
    project_root = os.getcwd()
    scope_check_path = os.path.join(project_root, '.agents', 'skills', 'scope_guardian', 'scripts', 'scope_check.py')
    
    if not os.path.exists(scope_check_path):
        print(f"[ERROR] scope_check.py tidak ditemukan di {scope_check_path}")
        sys.exit(1)

    if command == "smart_replace":
        if len(sys.argv) < 5:
            print("Usage: python snowline_run.py smart_replace <target_dir_or_file> <search> <replace> [--apply|--apply-validated]")
            sys.exit(1)
            
        target_dir = sys.argv[2]
        search_str = sys.argv[3]
        replace_str = sys.argv[4]
        extra_flags = sys.argv[5:]
        replace_text_path = os.path.join(project_root, '.agents', 'skills', 'smart_replace', 'replace_text.py')

        if not os.path.exists(replace_text_path):
            print(f"[ERROR] replace_text.py tidak ditemukan di {replace_text_path}")
            sys.exit(1)

        # 1. SCOPE CHECK
        scope_cmd = [sys.executable, scope_check_path, target_dir]
        scope_res = subprocess.run(scope_cmd, capture_output=True, text=True, encoding='utf-8')
        
        print(scope_res.stdout)
        if scope_res.stderr: print(scope_res.stderr)
        if scope_res.returncode != 0: sys.exit(1)

        risk1 = extract_risk(scope_res.stdout)

        # 2. SMART REPLACE
        replace_cmd = [sys.executable, replace_text_path, target_dir, search_str, replace_str] + extra_flags
        replace_res = subprocess.run(replace_cmd, capture_output=True, text=True, encoding='utf-8')
        
        print(replace_res.stdout)
        if replace_res.stderr: print(replace_res.stderr)
        if replace_res.returncode != 0: sys.exit(replace_res.returncode)
        
        risk2 = extract_risk(replace_res.stdout)
        max_risk = max(risk1, risk2)

        # 3. INTERACTIVE PROMPT
        if not any(f.startswith("--apply") for f in extra_flags):
            print("\n" + "="*50)
            print("💡 PROMPT UNTUK AI (Orchestrator Guidance):")
            print(f"[INFO] Unified Risk Level (Scope vs Action): {'Low' if max_risk == 1 else 'Medium' if max_risk == 2 else 'High'}")
            if max_risk == 1:
                print("Karena Unified Risk = Low dan validasi syntax berhasil, silakan jalankan perintah yang sama dengan tambahan flag `--apply`.")
            else:
                print("Karena Unified Risk = Medium/High, Anda WAJIB memastikan tidak ada kerusakan logika. Jika aman, jalankan perintah yang sama dengan tambahan flag `--apply-validated`.")

    elif command == "auto_scaffolder":
        if len(sys.argv) < 5:
            print("Usage: python snowline_run.py auto_scaffolder <type> <name> <target_dir> [--apply]")
            sys.exit(1)
            
        file_type = sys.argv[2]
        comp_name = sys.argv[3]
        target_dir = sys.argv[4]
        extra_flags = sys.argv[5:]
        
        scaffolder_path = os.path.join(project_root, '.agents', 'skills', 'auto_scaffolder', 'scaffolder.py')
        if not os.path.exists(scaffolder_path):
            print(f"[ERROR] scaffolder.py tidak ditemukan di {scaffolder_path}")
            sys.exit(1)

        # 1. SCOPE CHECK
        scope_cmd = [sys.executable, scope_check_path, target_dir]
        scope_res = subprocess.run(scope_cmd, capture_output=True, text=True, encoding='utf-8')
        
        print(scope_res.stdout)
        if scope_res.stderr: print(scope_res.stderr)
        if scope_res.returncode != 0: sys.exit(1)
        
        risk1 = extract_risk(scope_res.stdout)

        # 2. AUTO SCAFFOLDER
        scaffolder_cmd = [sys.executable, scaffolder_path, file_type, comp_name, target_dir] + extra_flags
        scaffolder_res = subprocess.run(scaffolder_cmd, capture_output=True, text=True, encoding='utf-8')
        
        print(scaffolder_res.stdout)
        if scaffolder_res.stderr: print(scaffolder_res.stderr)
        if scaffolder_res.returncode != 0: sys.exit(scaffolder_res.returncode)
        
        risk2 = extract_risk(scaffolder_res.stdout)
        max_risk = max(risk1, risk2)

        # 3. INTERACTIVE PROMPT
        if not any(f.startswith("--apply") for f in extra_flags):
            print("\n" + "="*50)
            print("💡 PROMPT UNTUK AI (Orchestrator Guidance):")
            print(f"[INFO] Unified Risk Level (Scope vs Action): {'Low' if max_risk == 1 else 'Medium' if max_risk == 2 else 'High'}")
            if max_risk == 1:
                print("Karena Unified Risk = Low dan validasi syntax berhasil, silakan jalankan perintah yang sama dengan tambahan flag `--apply`.")
            else:
                print("Karena Unified Risk = Medium/High, Anda WAJIB memastikan tidak ada kerusakan logika. Jika aman, jalankan perintah yang sama dengan tambahan flag `--apply-validated`.")

    else:
        print(f"[ERROR] Command '{command}' not supported by snowline_run.")
        sys.exit(1)

if __name__ == "__main__":
    main()
