import os
import json
import subprocess
import sys
import tempfile
import shutil

def run_case(enforcer, target_file, cwd):
    repo_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    skills_dir = os.path.join(repo_root, ".agents", "skills").replace("\\", "/")
    
    cmd = []
    if enforcer == "scope_check":
        cmd = [sys.executable, "-c", f"import sys; sys.path.insert(0, '{skills_dir}'); from scope_guardian.scripts.scope_check import check_scope; check_scope(r'{target_file}')"]
    elif enforcer == "replace_text":
        cmd = [sys.executable, "-c", f"import sys; sys.path.insert(0, '{skills_dir}'); from smart_replace.replace_text import check_scope; check_scope([(r'{target_file}', '', '')])"]
    elif enforcer == "context_mapper":
        cmd = [sys.executable, "-c", f"import sys; sys.path.insert(0, '{skills_dir}'); from context_mapper.context_mapper import check_scope_write; check_scope_write(r'{target_file}')"]
    elif enforcer == "auto_scaffolder":
        cmd = [sys.executable, "-c", f"import sys; sys.path.insert(0, '{skills_dir}'); from auto_scaffolder.scaffolder import check_scope_write; check_scope_write(r'{target_file}')"]
    elif enforcer == "import_fixer":
        cmd = [sys.executable, "-c", f"import sys; sys.path.insert(0, '{skills_dir}'); from import_fixer.fixer import check_scope_write; check_scope_write(r'{target_file}')"]
        
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=5, cwd=cwd)
        if result.returncode == 0:
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

cases = [
    (1, "tanpa lock", "src/test.py", None),
    (2, "di allowed_files", "src/test.py", {"allowed_files": ["src/test.py"], "task": "test"}),
    (3, "di luar allowed", "src/other.py", {"allowed_files": ["src/test.py"], "task": "test"}),
    (4, "berkas di .agents/", ".agents/knowledge/DEPENDENCY_MAP.md", {"allowed_files": [], "task": "test"}),
    (5, "jalur absolut Windows", "C:\\fake\\path\\src\\test.py", {"allowed_files": ["src/test.py"], "task": "test"}),
    (6, "JSON rusak", "src/test.py", "{ bad json")
]

enforcers = ["scope_check", "replace_text", "context_mapper", "auto_scaffolder", "import_fixer"]

print("| kasus | " + " | ".join(enforcers) + " |")
print("|-------|" + "|".join(["-"*len(e) for e in enforcers]) + "|")

with tempfile.TemporaryDirectory() as tmpdir:
    agents_dir = os.path.join(tmpdir, ".agents")
    os.makedirs(agents_dir)
    lock_path = os.path.join(agents_dir, "scope_lock.json")
    
    for case_num, case_desc, target, lock_content in cases:
        if os.path.exists(lock_path):
            os.remove(lock_path)
            
        if lock_content is not None:
            with open(lock_path, "w", encoding="utf-8") as f:
                if isinstance(lock_content, str):
                    f.write(lock_content)
                else:
                    json.dump(lock_content, f)
            
        results = []
        for enf in enforcers:
            res = run_case(enf, target, tmpdir)
            results.append(res)
        
        print(f"| {case_num} {case_desc} | " + " | ".join(results) + " |")