import os
import sys
import tempfile
import json
import shutil
import subprocess
from pathlib import Path

SKRIP = Path(__file__).parent.parent / "src" / "snowline" / "templates" / "skills" / "smart_replace" / "replace_text.py"

def test_write_log_directions():
    temp_dir = tempfile.mkdtemp(prefix="test_a2_")
    try:
        agents = os.path.join(temp_dir, ".agents")
        os.makedirs(agents)
        scope_data = {
            "task": "perbaiki navbar",
            "allowed_files": ["src/Navbar.jsx"],
            "allowed_patterns": []
        }
        with open(os.path.join(agents, "scope_lock.json"), "w", encoding="utf-8") as f:
            json.dump(scope_data, f)
            
        src_dir = os.path.join(temp_dir, "src")
        os.makedirs(src_dir)
        nav_file = os.path.join(src_dir, "Navbar.jsx")
        app_file = os.path.join(src_dir, "App.jsx")
        with open(nav_file, "w", encoding="utf-8") as f:
            f.write("const Navbar = () => TARGET;\n")
        with open(app_file, "w", encoding="utf-8") as f:
            f.write("const App = () => TARGET;\n")
            
        # Arah c: dry-run tidak menulis ke write_log.jsonl
        res_dry = subprocess.run([
            sys.executable, str(SKRIP), nav_file, "TARGET", "REPLACED"
        ], cwd=temp_dir, capture_output=True, text=True)
        log_file = os.path.join(agents, "write_log.jsonl")
        assert not os.path.exists(log_file), "Arah C gagal: dry-run menulis ke write_log.jsonl"
        
        # Arah a: tulisan di dalam lingkup
        res_in = subprocess.run([
            sys.executable, str(SKRIP), nav_file, "TARGET", "REPLACED", "--apply"
        ], cwd=temp_dir, capture_output=True, text=True)
        assert os.path.exists(log_file), f"write_log.jsonl tidak dibuat:\n{res_in.stdout}\n{res_in.stderr}"
        with open(log_file, "r", encoding="utf-8") as f:
            lines = [json.loads(l) for l in f if l.strip()]
        assert len(lines) == 1, f"Harusnya 1 baris, dapat {len(lines)}"
        assert lines[0]["dalam_lingkup"] is True, "dalam_lingkup harusnya True"
        assert lines[0]["alat"] == "smart_replace"
        assert lines[0]["tugas"] == "perbaiki navbar"
        assert lines[0]["berkas"] == "src/Navbar.jsx"
        
        # Arah b: tulisan di luar lingkup
        res_out = subprocess.run([
            sys.executable, str(SKRIP), app_file, "TARGET", "REPLACED", "--apply"
        ], cwd=temp_dir, capture_output=True, text=True)
        with open(log_file, "r", encoding="utf-8") as f:
            lines = [json.loads(l) for l in f if l.strip()]
        assert len(lines) == 2, f"Harusnya 2 baris, dapat {len(lines)}"
        assert lines[1]["dalam_lingkup"] is False, "dalam_lingkup harusnya False"
        assert lines[1]["alat"] == "smart_replace"
        assert lines[1]["tugas"] == "perbaiki navbar"
        assert lines[1]["berkas"] == "src/App.jsx"
        
    finally:
        shutil.rmtree(temp_dir, ignore_errors=True)

    # --- Arah d: 10 tulisan -> 10 baris, tetap JSONL sah
    temp_d = tempfile.mkdtemp(prefix="test_a2_d_")
    try:
        agents = os.path.join(temp_d, ".agents")
        os.makedirs(agents)
        files = [f"f{i}.py" for i in range(10)]
        with open(os.path.join(agents, "scope_lock.json"), "w", encoding="utf-8") as f:
            json.dump({"task": "bulk test", "allowed_files": files, "allowed_patterns": []}, f)
            
        for i in range(10):
            with open(os.path.join(temp_d, f"f{i}.py"), "w", encoding="utf-8") as f:
                f.write("val = TARGET\n")
                
        res_bulk = subprocess.run([
            sys.executable, str(SKRIP), temp_d, "TARGET", "100", "--apply-validated", "--allow-partial-match"
        ], cwd=temp_d, capture_output=True, text=True)
        
        log_file = os.path.join(agents, "write_log.jsonl")
        assert os.path.exists(log_file)
        with open(log_file, "r", encoding="utf-8") as f:
            lines = [json.loads(l) for l in f if l.strip()]
        assert len(lines) == 10, f"Harusnya 10 baris log, dapat {len(lines)}"
        for l in lines:
            assert "waktu" in l and "alat" in l and "berkas" in l and "dalam_lingkup" in l and "tugas" in l
    finally:
        shutil.rmtree(temp_d, ignore_errors=True)

if __name__ == "__main__":
    test_write_log_directions()
    print("test_write_log passed")