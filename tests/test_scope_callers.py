import os
import sys
import tempfile
import json
import shutil
import subprocess
from pathlib import Path

SKILLS = Path(__file__).parent.parent / "src" / "snowline" / "templates" / "skills"

def test_all_5_callers_after_unification():
    temp_dir = tempfile.mkdtemp(prefix="test_a5_")
    try:
        agents = os.path.join(temp_dir, ".agents")
        os.makedirs(agents)
        scope_data = {
            "task": "unification test",
            "allowed_files": ["src/MyComp.jsx", "src/fix.js", "src/code.py"],
            "allowed_patterns": ["*.md", ".agents/knowledge/*"]
        }
        with open(os.path.join(agents, "scope_lock.json"), "w", encoding="utf-8") as f:
            json.dump(scope_data, f)
            
        src_dir = os.path.join(temp_dir, "src")
        os.makedirs(src_dir)

        # 1. Caller: scope_check.py (Canonical)
        res1 = subprocess.run([
            sys.executable, str(SKILLS / "scope_guardian" / "scripts" / "scope_check.py"),
            os.path.join(src_dir, "MyComp.jsx")
        ], cwd=temp_dir, capture_output=True, text=True)
        assert res1.returncode == 0
        assert "[ALLOWED]" in res1.stdout

        # 2. Caller: replace_text.py
        py_file = os.path.join(src_dir, "code.py")
        with open(py_file, "w", encoding="utf-8") as f:
            f.write("val = OLD_VAL\n")
        res2 = subprocess.run([
            sys.executable, str(SKILLS / "smart_replace" / "replace_text.py"),
            py_file, "OLD_VAL", "NEW_VAL", "--apply"
        ], cwd=temp_dir, capture_output=True, text=True)
        assert res2.returncode == 0
        assert "[SUCCESS]" in res2.stdout

        # 3. Caller: scaffolder.py
        res3 = subprocess.run([
            sys.executable, str(SKILLS / "auto_scaffolder" / "scaffolder.py"),
            "react", "MyComp", src_dir, "--apply"
        ], cwd=temp_dir, capture_output=True, text=True)
        assert res3.returncode == 0
        assert os.path.exists(os.path.join(src_dir, "MyComp.jsx"))

        # 4. Caller: fixer.py
        fix_file = os.path.join(src_dir, "fix.js")
        with open(fix_file, "w", encoding="utf-8") as f:
            f.write("import target from './target';\n")
        with open(os.path.join(src_dir, "target.js"), "w", encoding="utf-8") as f:
            f.write("export default 1;\n")
        res4 = subprocess.run([
            sys.executable, str(SKILLS / "import_fixer" / "fixer.py"),
            fix_file, "./target", "--apply"
        ], cwd=temp_dir, capture_output=True, text=True)
        assert res4.returncode == 0

        # 5. Caller: context_mapper.py
        res5 = subprocess.run([
            sys.executable, str(SKILLS / "context_mapper" / "context_mapper.py"),
            "--apply"
        ], cwd=temp_dir, capture_output=True, text=True)
        assert res5.returncode == 0

    finally:
        shutil.rmtree(temp_dir, ignore_errors=True)

if __name__ == "__main__":
    test_all_5_callers_after_unification()
    print("test_scope_callers passed")
