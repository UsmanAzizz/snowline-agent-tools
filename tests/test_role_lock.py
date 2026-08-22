import os
import sys
import tempfile
import subprocess
import json

def test_role_lock_encodings():
    """
    Tests that role.json works with utf-8, utf-8-sig (BOM), and utf-16 encodings.
    """
    script = """import sys, json, os
from smart_replace.replace_text import check_task_state
# We will mock os.getcwd() to point to our temp dir
old_getcwd = os.getcwd
os.getcwd = lambda: sys.argv[1]
try:
    check_task_state(is_apply=True)
    print("PASS_NOT_BLOCKED")
except SystemExit:
    print("BLOCKED")
"""

    with tempfile.TemporaryDirectory() as tmpdir:
        here_we_are = os.path.join(tmpdir, '.here_we_are')
        os.makedirs(here_we_are)
        peran_file = os.path.join(here_we_are, 'role.json')
        
        script_file = os.path.join(tmpdir, 'test_script.py')
        with open(script_file, 'w', encoding='utf-8') as f:
            f.write(script)
            
        env = os.environ.copy()
        # Need to make sure smart_replace is importable
        tools_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src", "snowline", "templates", "skills"))
        env["PYTHONPATH"] = tools_dir

        encodings = ['utf-8', 'utf-8-sig', 'utf-16']
        for enc in encodings:
            with open(peran_file, 'w', encoding=enc) as f:
                json.dump({"role": "QA"}, f)
                
            r = subprocess.run([sys.executable, script_file, tmpdir], env=env, capture_output=True, text=True)
            assert "BLOCKED" in r.stdout or "BLOCKED" in r.stderr, f"Failed to block QA role with encoding {enc}. Output: {r.stdout} {r.stderr}"
            
        # Also test that it doesn't block if role is not QA
        for enc in encodings:
            with open(peran_file, 'w', encoding=enc) as f:
                json.dump({"role": "TL"}, f)
                
            r = subprocess.run([sys.executable, script_file, tmpdir], env=env, capture_output=True, text=True)
            assert "PASS_NOT_BLOCKED" in r.stdout, f"Blocked unexpectedly with role TL and encoding {enc}. Output: {r.stdout} {r.stderr}"

if __name__ == '__main__':
    test_role_lock_encodings()
    print("All role lock encoding tests passed.")
