import os
import json
import subprocess
import sys

def run_case(enforcer, case_num, target_file):
    # Determine how to call the enforcer
    cmd = []
    if enforcer == "scope_check":
        cmd = [sys.executable, "-c", f"import sys; sys.path.insert(0, '.agents/skills'); from scope_guardian.scripts.scope_check import check_scope; check_scope(r'{target_file}')"]
    elif enforcer == "replace_text":
        cmd = [sys.executable, "-c", f"import sys; sys.path.insert(0, '.agents/skills'); from smart_replace.replace_text import check_scope; check_scope([(r'{target_file}', '', '')])"]
    elif enforcer == "context_mapper":
        cmd = [sys.executable, "-c", f"import sys; sys.path.insert(0, '.agents/skills'); from context_mapper.context_mapper import check_scope_write; check_scope_write(r'{target_file}')"]
    elif enforcer == "auto_scaffolder":
        cmd = [sys.executable, "-c", f"import sys; sys.path.insert(0, '.agents/skills'); from auto_scaffolder.scaffolder import check_scope_write; check_scope_write(r'{target_file}')"]
    elif enforcer == "import_fixer":
        cmd = [sys.executable, "-c", f"import sys; sys.path.insert(0, '.agents/skills'); from import_fixer.fixer import check_scope_write; check_scope_write(r'{target_file}')"]
        
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=5)
        if result.returncode == 0:
            # If it prints [ALLOWED], it's PASS/ALLOW. Some might return 0 without printing [ALLOWED] (like check_scope returns True)
            if "[BLOCKED]" in result.stdout or "[BLOCKED]" in result.stderr:
                return "BLOCK"
            return "ALLOW"
        else:
            if "[BLOCKED]" in result.stdout or "[BLOCKED]" in result.stderr:
                return "BLOCK"
            if "Exception" in result.stderr or "Traceback" in result.stderr:
                return "ERROR"
            return "BLOCK (exit 1)"
    except Exception as e:
        return f"ERR: {e}"

def setup_lock(content):
    os.makedirs(".agents", exist_ok=True)
    with open(".agents/scope_lock.json", "w", encoding="utf-8") as f:
        f.write(content)

def remove_lock():
    if os.path.exists(".agents/scope_lock.json"):
        os.remove(".agents/scope_lock.json")

cases = [
    (1, "tanpa lock", "src/test.py", None),
    (2, "di allowed_files", "src/test.py", json.dumps({"allowed_files": ["src/test.py"], "task": "test"})),
    (3, "di luar allowed", "src/other.py", json.dumps({"allowed_files": ["src/test.py"], "task": "test"})),
    (4, "berkas di .agents/", ".agents/knowledge/DEPENDENCY_MAP.md", json.dumps({"allowed_files": [], "task": "test"})),
    (5, "jalur absolut Windows", "C:\\fake\\path\\src\\test.py", json.dumps({"allowed_files": ["src/test.py"], "task": "test"})),
    (6, "JSON rusak", "src/test.py", "{ bad json")
]

enforcers = ["scope_check", "replace_text", "context_mapper", "auto_scaffolder", "import_fixer"]

print("| kasus | " + " | ".join(enforcers) + " |")
print("|-------|" + "|".join(["-"*len(e) for e in enforcers]) + "|")

for case_num, case_desc, target, lock_content in cases:
    if lock_content is None:
        remove_lock()
    else:
        setup_lock(lock_content)
        
    results = []
    for enf in enforcers:
        res = run_case(enf, case_num, target)
        results.append(res)
    
    print(f"| {case_num} {case_desc} | " + " | ".join(results) + " |")

# Cleanup
remove_lock()