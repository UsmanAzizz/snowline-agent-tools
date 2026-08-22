import os
import subprocess
import tempfile
import sys
import json

def get_root_dir():
    return os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))

def run_cmd(cmd):
    p = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True, text=True)
    out, err = p.communicate()
    return p.returncode, out, err

def test_encoding_tools():
    root = get_root_dir()
    test_tmp = os.path.join(root, 'tests', 'tmp')
    os.makedirs(test_tmp, exist_ok=True)
    with tempfile.TemporaryDirectory(dir=test_tmp) as tmpdir:
        # Create a JS file with non-ASCII characters
        js_file = os.path.join(tmpdir, "test_non_ascii.js")
        non_ascii_content = "import { dummy } from './dummy';\n// Komentar bahasa indonesia dengan karakter non-ASCII: á é í ó úñ ☺ ☻ 💡\nfunction handlePinSubmit() {\n  const x = 'ini ada data non ascii: ã';\n}\n"
        with open(js_file, 'w', encoding='utf-8') as f:
            f.write(non_ascii_content)
        
        # Test 1: code_finder.py
        code_finder = os.path.join(root, "src", "snowline", "templates", "skills", "smart_search", "code_finder.py")
        rc, out, err = run_cmd(f"{sys.executable} {code_finder} {tmpdir} handlePinSubmit")
        assert "1 kecocokan di 1 file" in out or "1 file" in out, f"code_finder failed to read non-ASCII file. Output: {out}"
        
        # Test 2: splicer.py
        splicer = os.path.join(root, "src", "snowline", "templates", "skills", "surgical_splicer", "splicer.py")
        rc, out, err = run_cmd(f"{sys.executable} {splicer} {js_file} handlePinSubmit")
        assert rc == 0, f"splicer.py crashed on non-ASCII file. Err: {err}"
        assert "function handlePinSubmit" in out, f"splicer.py failed to extract function from non-ASCII file. Output: {out}"
        
        # Test 3: loop_detector.py
        loop_detector = os.path.join(root, "src", "snowline", "templates", "hooks", "loop_detector.py")
        history_file = os.path.join(tmpdir, "history.json")
        history_data = [{"args": "test non ascii áéí"}]
        with open(history_file, 'w', encoding='utf-8') as f:
            json.dump(history_data, f)
            
        os.environ["SNOWLINE_HISTORY"] = history_file
        try:
            rc, out, err = run_cmd(f"echo {{}} | {sys.executable} {loop_detector} \"test non ascii áéí\"")
            assert rc == 0, f"loop_detector.py crashed on non-ASCII file. Err: {err}"
        finally:
            if "SNOWLINE_HISTORY" in os.environ:
                del os.environ["SNOWLINE_HISTORY"]
